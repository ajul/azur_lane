import load_lua
import math
import subprocess
import copy
import hashlib
import struct
from PIL import Image, ImageDraw

weapon_srcs = load_lua.load_sharecfg('weapon_property')
barrage_srcs = load_lua.load_sharecfg('barrage_template')
bullet_srcs = load_lua.load_sharecfg('bullet_template')

bullet_models = {
    'BulletUSA' : ('bullet-04-y', 4, 1), # normal
    'BulletUK' : ('bullet_UK', 6, 2), # normal
    'BulletJP' : ('bulletjp', 5, 1.25), # HE
    'Bullet1' : ('kuasheAP', 6, 2), # AP
    'kuashe' : ('bullet_UK', 8, 3), # big normal
    'kuasheHE' : ('kuasheHE', 8, 4), # big HE
    'kuasheAP' : ('kuasheAP', 8, 4), # big AP
    'kuasheSAP' : ('kuasheAP', 8, 4), # big SAP
    'Torpedo01' : ('Torpedo01', 2, 1), 
    
    'kuashetuowei' : ('bullet_UK', 8, 3),
    'BulletGER' : ('bulletGER', 3, 3),
    'chuantoudan' : ('path_00269', 6, 0.5),
    'Bomberbomb500' : ('Bomberbomb150lb', 4, 2),
    'xingxingzidan01' : ('AL_Star01', 2, 2),
    'xingxingzidan02' : ('AL_Star02', 2, 2),
    'Bulletelc' : ('bulletUSA', 6, 2), # eldridge until i get the proper image
    'Torpedo_Vampire' : ('Torpedo_Vampire', 2, 1), 
    'shizijia_faxi' : ('AL_Trail00', 3, 3),
    'Bullet1_faxi' : ('AL_Trail01_1', 4, 4),
    'Bullet2_faxi' : ('AL_Trail01_1', 4, 4),
    'Bullet3_faxi' : ('AL_Trail01_1', 4, 4),
    'hwxgz_1' : ('hwxgz_1', 3, 3),
    'hwxgz_2' : ('hwxgz_2', 4, 2),
    'hwxqb_1' : ('hwxqb_1', 3, 3),
    'hwxqb_2' : ('hwxqb_2', 4, 2),
    'bullet1' : ('bullet1', 6, 2), # other AP
    'bullet2' : ('bullet2', 6, 2), # other HE
    'Al_Flower01' : ('Al_Flower01', 3, 3),
}

tints = {
    'Bullet1_faxi' : (1.0, 0.5, 0.5),
    'Bullet2_faxi' : (0.5, 0.5, 1.0),
    'kuasheSAP' : (1.0, 0.5, 0.5),
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
    result = model.resize((new_res_x, new_res_z), Image.LANCZOS)
    if model_name in tints:
        tint = tints[model_name]
        for y in range(result.size[1]):
            for x in range(result.size[0]):
                color = result.getpixel((x, y))
                new_color = tuple(int(round(c * t)) for c, t in zip(color, tint[:3])) + color[3:]
                result.putpixel((x, y), new_color)
    return result

def put_on_background(image):
    bg = Image.new('RGBA', image.size, color = (34, 34, 34, 255))
    return Image.alpha_composite(bg, image)

def hash_ints(*t):
    hasher = hashlib.md5()
    hasher.update(struct.pack('<' + 'L' * len(t), *t))
    return struct.unpack('<H', hasher.digest()[0:2])[0] / 2**16
    
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
    
    def ground_angle(self):
        vertical = self.z
        horizontal = self.x
        return math.atan2(vertical, horizontal)
    
    def ground_angle_degrees(self):
        return math.degrees(self.ground_angle())
        
    def draw_angle_degrees(self):
        vertical = self.y + self.z / camera_slope
        horizontal = self.x
        return math.degrees(math.atan2(vertical, horizontal))
    
    def normalized(self):
        return self / self.magnitude()
        
    def ground_cross(self):
        return Vector(-self.z, 0.0, self.x)
    
    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y, self.z + other.z)
    
    def __sub__(self, other):
        return Vector(self.x - other.x, self.y - other.y, self.z - other.z)
        
    def __mul__(self, other):
        return Vector(self.x * other, self.y * other, self.z * other)

    def __truediv__(self, other):
        return Vector(self.x / other, self.y / other, self.z / other)
    
    def __str__(self):
        return '(%f, %f, %f)' % (self.x, self.y, self.z)

class Bullet():
    def __init__(self, model, delay, position0, velocity0, gravity, accelerations, distance):
        self.model = model
        self.delay = delay
        self.position0 = position0
        self.velocity0 = velocity0
        self.gravity = gravity
        self.accelerations = []
        for k in sorted(accelerations.keys()):
            raw_acceleration = accelerations[k]
            acceleration = copy.deepcopy(raw_acceleration)
            if 'flip' in raw_acceleration and raw_acceleration['flip'] and self.velocity0.ground_angle_degrees() >= 0.0:
                acceleration['v'] *= -1.0
            self.accelerations.append(acceleration)
                
        self.distance = distance
        
        if gravity != 0:
            lifetime = distance / self.velocity0.ground_magnitude() / velocity_factor
            self.velocity0.y = -0.5 * gravity  * acceleration_factor * lifetime
        
        self.reset()
    
    def reset(self):
        self.fired = self.delay == 0.0
        self.alive = True
        
        self.position = self.position0.copy()
        self.velocity = self.velocity0.copy()
        self.acceleration_index = 0
        self.acceleration_sign = 1
        self.previous_draw_angle = None
        self.update_model_rotation()

    def update_model_rotation(self):
        draw_angle = self.velocity.draw_angle_degrees()
        if draw_angle != self.previous_draw_angle:
            self.model_rotated = self.model.rotate(draw_angle, Image.BICUBIC, True)
        self.previous_draw_angle = draw_angle
        
    def update(self, t, dt):
        if t >= self.delay: 
            self.fired = True
            dt = min(dt, t - self.delay)
        else:
            return
        self.position += self.velocity * dt * velocity_factor
        if (self.position - self.position0).ground_magnitude_squared() > self.distance * self.distance:
            self.alive = False
            return
        
        if len(self.accelerations) > 0:
            while self.acceleration_index + 1 < len(self.accelerations):
                next_acceleration = self.accelerations[self.acceleration_index + 1]
                if t - self.delay >= next_acceleration['t']:
                    self.acceleration_index += 1
                else:
                    break

            current_acceleration = self.accelerations[self.acceleration_index]
            if 'u' in current_acceleration:
                acceleration_u = current_acceleration['u'] * dt * acceleration_factor * self.acceleration_sign
                if acceleration_u < 0 and acceleration_u * acceleration_u >= self.velocity.ground_magnitude_squared():
                    acceleration_u = -1.0 * acceleration_u
                    self.acceleration_sign *= -1.0
                self.velocity += self.velocity.normalized() * acceleration_u
            if 'v' in current_acceleration:
                self.velocity += self.velocity.ground_cross().normalized() * current_acceleration['v'] * dt * acceleration_factor

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
    def __init__(self, barrage_src, bullet_src, extra_delay, start_pos, target_pos, ppu, range_limit, hash_index):
        if barrage_src['trans_ID'] >= 0:
            raise NotImplementedError('trans_ID not implemented.')
    
        model = get_model(bullet_src, ppu)
        
        random_offset_x = 0
        if 'randomOffsetX' in bullet_src['extra_param']:
            random_offset_x = bullet_src['extra_param']['randomOffsetX']
            
        random_offset_z = 0
        if 'randomOffsetZ' in bullet_src['extra_param']:
            random_offset_z = bullet_src['extra_param']['randomOffsetZ']
        
        speed = bullet_src['velocity']
        accelerations = bullet_src['acceleration']

        parallel = barrage_src['primal_repeat'] + 1
        serial = barrage_src['senior_repeat'] + 1
        
        first_delay = barrage_src['first_delay'] + extra_delay
        all_delay = barrage_src['delay']
        serial_delay = barrage_src['senior_delay']
        parallel_delay = barrage_src['delta_delay']
        
        if 'random_angle' in barrage_src and barrage_src['random_angle']:
            has_random_angle = True
        else:
            has_random_angle = False
        offset_angle = math.radians(barrage_src['angle'])
        delta_angle = math.radians(barrage_src['delta_angle'])
        
        offset_x = barrage_src['offset_x']
        delta_offset_x = barrage_src['delta_offset_x']
        
        offset_z = barrage_src['offset_z']
        delta_offset_z = barrage_src['delta_offset_z'] 
        
        offset_prioritise = barrage_src['offset_prioritise']
        if offset_prioritise: print('offset_prioritise', offset_angle, offset_z)
        
        self.bullets = []
    
        bullet_idx = 0
        for serial_idx in range(serial):
            for parallel_idx in range(parallel):
                base_hash_tuple = (hash_index, barrage_src['id'], serial_idx, parallel_idx)
                # Compute distance/target location.
                hash_target_x = (hash_ints(*base_hash_tuple, 0) - 0.5) * random_offset_x
                hash_target_z = (hash_ints(*base_hash_tuple, 1) - 0.5) * random_offset_z
                random_target_pos = target_pos + Vector(hash_target_x, 0, hash_target_z)
                aim_vector = random_target_pos - start_pos
                aim_angle = aim_vector.ground_angle()
                
                distance = bullet_src['range'] # + offset?
                if range_limit is not None:
                    distance = min(distance, range_limit)
                
                if 'gravity' in bullet_src['extra_param']:
                    gravity = bullet_src['extra_param']['gravity']
                else:
                    gravity = 0.0
                if gravity != 0.0:
                    distance = aim_vector.magnitude()
            
                delay = first_delay + serial_delay * serial_idx + parallel_delay * parallel_idx + all_delay * bullet_idx
                x0 = start_pos.x + offset_x + delta_offset_x * parallel_idx
                z0 = start_pos.z + offset_z + delta_offset_z * parallel_idx
                angle = offset_angle + delta_angle * parallel_idx
                if has_random_angle:
                    h = hash_ints(*base_hash_tuple, 2)
                    angle *= (h - 0.5)
                angle += aim_angle
                v0 = Vector.from_angle(angle) * speed
                
                self.bullets.append(Bullet(model, delay, Vector(x0, 0, z0), v0, gravity, accelerations, distance))
                bullet_idx += 1
        
        self.random_count = 0
        if has_random_angle or random_offset_x != 0 or random_offset_z != 0:
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

# weapon_id elements may be a 2-tuple where the second element is an extra delay.
def create_barrage_anim(filename_out, animator, weapon_ids, world_size, ppu, min_duration = 0.0, max_duration = 30.0, range_limit = None, min_pad_duration = 0.0, time_stretch = 1):
    image_res = (ppu * world_size[0], ppu * world_size[1] // camera_slope)
    start_pos = Vector(5, 0.0, world_size[1] / 2)
    target_pos = Vector(world_size[0] - 15, 0.0, world_size[1] / 2)
    
    frame_filenames = []
    frame_index = 0
    
    def draw_iteration(frame_index, hash_index):
        draw_barrages = []
        
        random_count = 0
    
        for weapon_id in weapon_ids:
            extra_delay = 0
            if isinstance(weapon_id, tuple):
                extra_delay = weapon_id[1]
                weapon_id = weapon_id[0]
            weapon_src = weapon_srcs[weapon_id]
            if 'base' in weapon_src:
                base_weapon_src = copy.deepcopy(weapon_srcs[weapon_src['base']])
                base_weapon_src.update(weapon_src)
                weapon_src = base_weapon_src
            
            barrage_index = 1
            while barrage_index in weapon_src['barrage_ID']:
                barrage_src = barrage_srcs[weapon_src['barrage_ID'][barrage_index]]
                bullet_src = bullet_srcs[weapon_src['bullet_ID'][barrage_index]]
                barrage = Barrage(barrage_src, bullet_src, extra_delay, start_pos, target_pos, ppu, range_limit, hash_index = hash_index)
                if barrage.random_count > 0:
                    if random_count == 0: random_count = barrage.random_count
                    else: random_count = min(random_count, barrage.random_count)
                    
                draw_barrages.append(barrage)
                barrage_index += 1
    
        t = 0.0
        dt = 1.0 / animator.fps / time_stretch
        
        iteration_frame_index = 0
    
        while any(draw_barrage.alive() for draw_barrage in draw_barrages) and t < max_duration:
            t = iteration_frame_index / animator.fps / time_stretch
            frame = Image.new('RGBA', image_res)
            for draw_barrage in draw_barrages:
                frame = draw_barrage.draw(frame, ppu)
            frame = put_on_background(frame)
            animator.write_frame(frame, frame_index)
            
            for draw_barrage in draw_barrages:
                draw_barrage.update(t, dt)
            
            frame_index += 1
            iteration_frame_index += 1
        
        pad_duration = max(min_pad_duration, min_duration - t)
        
        if pad_duration > 0:
            num_pad_frames = math.ceil(pad_duration * animator.fps)
            for i in range(num_pad_frames):
                frame_filename = 'temp/frame_%02d.gif' % frame_index
                frame = Image.new('RGB', image_res, color = (34, 34, 34, 255))
                animator.write_frame(frame, frame_index)
            
                frame_index += 1
                iteration_frame_index += 1
            
        return frame_index, random_count
    
    frame_index, random_count = draw_iteration(frame_index, 0)
    
    if random_count > 0:
        repeat_count = max(1, 5 - random_count)
        for repeat_idx in range(repeat_count):
            frame_index, _ = draw_iteration(frame_index, repeat_idx + 1)
    
    animator.write_animation(filename_out)
