import load_lua
import math
import subprocess
import copy
from PIL import Image, ImageDraw

weapon_srcs = load_lua.load_sharecfg('weapon_property')
barrage_srcs = load_lua.load_sharecfg('barrage_template')
bullet_srcs = load_lua.load_sharecfg('bullet_template')

bullet_models = {
    'BulletUSA' : ('bullet-04-y', 4, 1), # normal
    'BulletUK' : ('bullet_UK', 6, 2), # normal
    'BulletJP' : ('bulletjp', 6, 2), # HE
    'Bullet1' : ('kuasheAP', 6, 2), # AP
    'kuashe' : ('bullet_UK', 8, 3), # big normal
    'kuasheHE' : ('kuasheHE', 8, 4), # big HE
    'kuasheAP' : ('kuasheAP', 8, 4), # big AP
    'kuasheSAP' : ('bulletUSA', 8, 4), # big SAP (not sure on model)
    'Torpedo01' : ('Torpedo01', 2, 1), 
    
    'kuashetuowei' : ('bullet_UK', 8, 4),
    'BulletGER' : ('bulletGER', 3, 3),
    'chuantoudan' : ('path_00269', 4, 0.5),
    'Bomberbomb500' : ('Bomberbomb150lb', 4, 2),
    'xingxingzidan01' : ('AL_Star01', 3, 3),
}

velocity_factor = 6
acceleration_factor = 150

camera_slope = 2

def get_model(bullet_src, ppu):
    model_name = bullet_src['modle_ID']
    #print(model_name)
    filename, length, width = bullet_models[model_name]
    model = Image.open('bullet_models/%s.png' % filename)
    new_res_x = round(ppu * length)
    new_res_z = round(ppu * width)
    return model.resize((new_res_x, new_res_z), Image.LANCZOS)

def put_on_background(image):
    bg = Image.new('RGBA', image.size, color = (34, 34, 34, 255))
    return Image.alpha_composite(bg, image)
    
class Vector():
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
        
    @staticmethod
    def from_angle(angle):
        return Vector(math.cos(angle), 0.0, math.sin(angle))
        
    def copy(self):
        return Vector(self.x, self.y, self.z)
    
    def magnitude(self):
        return math.sqrt(self.magnitude_squared())
    
    def magnitude_squared(self):
        return self.x * self.x + self.y * self.y + self.z * self.z
    
    def ground_magnitude(self):
        return math.sqrt(self.ground_magnitude_squared())
    
    def ground_magnitude_squared(self):
        return self.x * self.x + self.z * self.z
        
    def draw_angle_degrees(self):
        vertical = self.y + self.z / camera_slope
        horizontal = self.x
        return math.degrees(math.atan2(vertical, horizontal))
    
    def normalized(self):
        return self / self.magnitude()
        
    def ground_cross(self):
        return Vector(self.z, 0, -self.x)
    
    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y, self.z + other.z)
    
    def __sub__(self, other):
        return Vector(self.x - other.x, self.y - other.y, self.z - other.z)
        
    def __mul__(self, other):
        return Vector(self.x * other, self.y * other, self.z * other)

    def __truediv__(self, other):
        return Vector(self.x / other, self.y / other, self.z / other)

class Bullet():
    def __init__(self, model, delay, position0, velocity0, gravity, accelerations, max_range):
        self.model = model
        self.delay = delay
        self.position0 = position0
        self.velocity0 = velocity0
        self.gravity = gravity
        self.accelerations = [accelerations[k] for k in sorted(accelerations.keys())]
        self.max_range = max_range
        
        if gravity != 0:
            lifetime = max_range / self.velocity0.ground_magnitude() / velocity_factor
            self.velocity0.y = -0.5 * gravity  * acceleration_factor * lifetime
        
        self.reset()
    
    def reset(self):
        self.fired = self.delay == 0.0
        self.alive = True
        
        self.position = self.position0.copy()
        self.velocity = self.velocity0.copy()
        self.acceleration_index = 0
        self.previous_angle = None
        self.update_model_rotation()

    def update_model_rotation(self):
        angle = self.velocity.draw_angle_degrees()
        if angle != self.previous_angle:
            self.model_rotated = self.model.rotate(angle, Image.BICUBIC, True)
        self.previous_angle = angle
        
    def update(self, t, dt):
        if t >= self.delay: 
            self.fired = True
        else:
            return
        self.position += self.velocity * dt * velocity_factor
        if (self.position - self.position0).ground_magnitude_squared() > self.max_range * self.max_range:
            self.alive = False
            return
        while self.acceleration_index + 1 < len(self.accelerations):
            next_acceleration = self.accelerations[self.acceleration_index + 1]
            if t >= next_acceleration['t']:
                self.acceleration_index += 1
            else:
                current_acceleration = self.accelerations[self.acceleration_index]
                if 'u' in current_acceleration:
                    self.velocity += self.velocity.normalized() * current_acceleration['u'] * dt * acceleration_factor
                if 'v' in current_acceleration:
                    self.velocity += self.velocity.ground_cross().normalized() * current_acceleration['v'] * dt * acceleration_factor
                break
        self.velocity.y += self.gravity * dt * acceleration_factor
        
        self.update_model_rotation()

    def draw(self, frame, ppu):
        if not self.fired: return frame
        if not self.alive: return frame
        model_res_x, model_res_z = self.model_rotated.size
        x_corner_px = int(round(self.position.x * ppu - model_res_x / 2))
        # flip z
        z_corner_px = int(round(frame.size[1] - (self.position.z / camera_slope + self.position.y) * ppu - model_res_z / 2))
        overlay = Image.new('RGBA', frame.size)
        overlay.paste(self.model_rotated, (x_corner_px, z_corner_px))
        return Image.alpha_composite(frame, overlay)

class Barrage():
    def __init__(self, barrage_src, bullet_src, start_pos, ppu, range_limit, hash_index):
        if barrage_src['trans_ID'] >= 0:
            raise NotImplementedError('trans_ID not implemented.')
    
        model = get_model(bullet_src, ppu)
        
        max_range = bullet_src['range'] # + offset?
        if range_limit is not None:
            max_range = min(max_range, range_limit)
        speed = bullet_src['velocity']
        if 'gravity' in bullet_src['extra_param']:
            gravity = bullet_src['extra_param']['gravity']
        else:
            gravity = 0.0
        accelerations = bullet_src['acceleration']

        parallel = barrage_src['primal_repeat'] + 1
        serial = barrage_src['senior_repeat'] + 1
        
        delay_offset = barrage_src['delay'] # or first_delay?
        serial_delay = barrage_src['senior_delay']
        delta_delay = barrage_src['delta_delay']
        
        random_angle = math.radians(barrage_src['random_angle']) # TODO
        offset_angle = math.radians(barrage_src['angle'])
        delta_angle = math.radians(barrage_src['delta_angle'])
        
        offset_x = barrage_src['offset_x']
        delta_offset_x = barrage_src['delta_offset_x']
        
        offset_z = barrage_src['offset_z']
        delta_offset_z = barrage_src['delta_offset_z'] 
        
        self.bullets = []
    
        for serial_idx in range(serial):
            for parallel_idx in range(parallel):
                delay = delay_offset + serial_delay * serial_idx + delay_offset * parallel_idx
                x0 = start_pos[0] + offset_x + delta_offset_x * parallel_idx
                z0 = start_pos[1] + offset_z + delta_offset_z * parallel_idx
                angle = offset_angle + delta_angle * parallel_idx
                if random_angle:
                    h = (hash((hash_index, barrage_src['id'], serial_idx, parallel_idx)) % 0x80000000) / 0x80000000
                    angle *= (h - 0.5)
                v0 = Vector.from_angle(angle) * speed
                self.bullets.append(Bullet(model, delay, Vector(x0, 0, z0), v0, gravity, accelerations, max_range))
        
        self.random_count = 0
        if random_angle:
            self.random_count = parallel * serial
            
    def reset(self):
        for bullet in self.bullets:
            bullet.reset() 

    def update(self, t, dt):
        for bullet in self.bullets:
            bullet.update(t, dt)

    def draw(self, frame, ppu):
        for bullet in self.bullets:
            frame = bullet.draw(frame, ppu)
        return frame
    
    def alive(self):
        return any(bullet.alive for bullet in self.bullets)

def create_barrage_gif(filename_out, weapon_ids, world_size, ppu, min_duration = 0.0, max_duration = 60.0, range_limit = None, pad_duration = 0.0, fps = 50, time_stretch = 1, color_count = 16, lossy = 20):
    image_res = (ppu * world_size[0], ppu * world_size[1] // camera_slope)
    start_pos = (5, world_size[1] // 2)
    
    frame_filenames = []
    frame_index = 0
    
    def draw_iteration(frame_index, hash_index):
        draw_barrages = []
        
        random_count = 0
    
        for weapon_id in weapon_ids:
            weapon_src = weapon_srcs[weapon_id]
            if 'base' in weapon_src:
                base_weapon_src = copy.deepcopy(weapon_srcs[weapon_src['base']])
                base_weapon_src.update(weapon_src)
                weapon_src = base_weapon_src
            
            barrage_index = 1
            while barrage_index in weapon_src['barrage_ID']:
                barrage_src = barrage_srcs[weapon_src['barrage_ID'][barrage_index]]
                bullet_src = bullet_srcs[weapon_src['bullet_ID'][barrage_index]]
                barrage = Barrage(barrage_src, bullet_src, start_pos, ppu, range_limit, hash_index = hash_index)
                if barrage.random_count > 0:
                    if random_count == 0: random_count = barrage.random_count
                    else: random_count = min(random_count, barrage.random_count)
                    
                draw_barrages.append(barrage)
                barrage_index += 1
    
        t = 0.0
        dt = 1.0 / fps / time_stretch
        
        iteration_frame_index = 0
    
        while t < min_duration or (any(draw_barrage.alive() for draw_barrage in draw_barrages) and t < max_duration):
            t = iteration_frame_index / fps / time_stretch
            frame = Image.new('RGBA', image_res)
            for draw_barrage in draw_barrages:
                frame = draw_barrage.draw(frame, ppu)
            frame = put_on_background(frame)
            frame_filename = 'temp/frame_%02d.gif' % frame_index
            frame.convert('RGB').save(frame_filename)
            frame_filenames.append(frame_filename)
            
            for draw_barrage in draw_barrages:
                draw_barrage.update(t, dt)
            
            frame_index += 1
            iteration_frame_index += 1
    
        pad_frames = round(pad_duration / dt)
        for i in range(pad_frames):
            frame_filename = 'temp/frame_%02d.gif' % frame_index
            Image.new('RGB', image_res).save(frame_filename)
            frame_filenames.append(frame_filename)
            frame_index += 1
            iteration_frame_index += 1
            
        return frame_index, random_count
    
    frame_index, random_count = draw_iteration(frame_index, 0)
    
    if random_count > 0:
        repeat_count = max(1, 5 - random_count)
        for repeat_idx in range(repeat_count):
            draw_iteration(frame_index, repeat_idx + 1)

    gifsicle_cmd = ['./gifsicle.exe',
                    '--output=%s' % filename_out,
                    '--loopcount=0',
                    '--colors=%d' % color_count,
                    '--lossy=%d' % lossy,
                    '--delay=%d' % round(100 / fps),
                    '-O1'] + frame_filenames

    subprocess.run(gifsicle_cmd)

