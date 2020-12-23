from azurlane import load_lua
from azurlane.math import Vector, camera_slope
from PIL import Image, ImageDraw
import copy
import random
import math

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
    'bullet1' : ('bullet_UK', 6, 2), # Suruga normal
    'bullet2' : ('kuasheAP', 6, 2), # Suruga AP
    'Al_Flower01' : ('Al_Flower01', 3, 3),
    'zimudan' : ('zimudan', 3, 3),
    
    'BomberbombBlack' : ('BomberbombBlack', 4, 1.5), # Hermes
    'BomberbombWhite' : ('BomberbombWhite', 4, 1.5), # Hermes
    'BomberbombKnife' : ('BomberbombKnife', 4, 1.5), # Hermes
    
    'bingzhui' : ('hwxqb_1', 3, 3), # placeholder for Sovetskaya Rossiya
    'bingzhuibig' : ('hwxqb_1', 5, 5), # placeholder for Sovetskaya Rossiya
    
    'mofazidan02' : ('hwxgz_3', 3, 3),
}

tints = {
    'Bullet1_faxi' : (1.0, 0.5, 0.5),
    'Bullet2_faxi' : (0.5, 0.5, 1.0),
    'kuasheSAP' : (1.0, 0.5, 0.5),
}

velocity_factor = 6
acceleration_factor = 900

background_color = (34, 34, 34, 255)

def get_model(bullet_src, ppu):
    model_name = bullet_src['modle_ID']
    #print(model_name)
    
    if model_name == '':
        return Image.new('RGBA', (2, 2), (0, 0, 0, 0))

    filename, length, width = bullet_models[model_name]
    model = Image.open('bullet_models/%s.png' % filename)
    out_res_x = round(ppu * length)
    out_res_z = round(ppu * width)
    result = model.resize((out_res_x, out_res_z), Image.LANCZOS)
    if model_name in tints:
        tint = tints[model_name]
        for y in range(result.size[1]):
            for x in range(result.size[0]):
                color = result.getpixel((x, y))
                new_color = tuple(int(round(c * t)) for c, t in zip(color, tint[:3])) + color[3:]
                result.putpixel((x, y), new_color)
    return result

def put_on_background(image):
    bg = Image.new('RGBA', image.size, color = background_color)
    return Image.alpha_composite(bg, image)

class Bullet():
    def __init__(self, weapon_set, weapon_src, bullet_src, delay, position0, velocity0, max_range, target_pos):
        self.weapon_set = weapon_set
        self.weapon_src = weapon_src
        self.bullet_src = bullet_src
        self.model = get_model(self.bullet_src, self.weapon_set.render_ppu)
        self.delay = delay
        self.position0 = position0
        self.velocity0 = velocity0
        self.max_range = max_range
        self.target_pos = target_pos
        self.accelerations = []
        for k in sorted(bullet_src['acceleration'].keys()):
            if k == 'tracker':
                print('Tracking not currently represented, disabling.')
                continue
            raw_acceleration = bullet_src['acceleration'][k]
            acceleration = copy.deepcopy(raw_acceleration)
            if 'flip' in raw_acceleration and raw_acceleration['flip'] and self.velocity0.ground_angle_degrees() >= 0.0:
                acceleration['v'] *= -1.0
            if 'u' in acceleration: acceleration['u'] *= acceleration_factor
            if 'v' in acceleration: acceleration['v'] *= acceleration_factor
            self.accelerations.append(acceleration)
        
        self.is_bomb = bullet_src['extra_param'].get('airdrop', False)
        self.gravity = bullet_src['extra_param'].get('gravity', 0.0) * acceleration_factor
        # Arching shot.
        if self.gravity < 0.0 and self.position0.y == 0.0:
            lifetime = (self.target_pos - self.position0).ground_magnitude() / self.velocity0.ground_magnitude()
            self.velocity0.y = -0.5 * self.gravity * lifetime
    
        self.alive = True
        if bullet_src['type'] == 9:
            raise RuntimeError('Smokescreen not supported.')
            self.alive = False
        self.fired = self.delay == 0.0
        
        self.position = self.position0.copy()
        self.velocity = self.velocity0.copy()
        self.acceleration_index = 0
        self.acceleration_sign = 1
        self.previous_draw_angle_degrees = None
        self.update_model_rotation()
        self.shrapnel = []
        
        self.entered_bounds = False

    def update_model_rotation(self):
        draw_angle_degrees = self.velocity.draw_angle_degrees()
        if self.is_bomb:
            draw_angle_degrees += 180.0
        if draw_angle_degrees != self.previous_draw_angle_degrees:
            self.model_rotated = self.model.rotate(draw_angle_degrees, Image.BICUBIC, True)
        self.previous_draw_angle_degrees = draw_angle_degrees
        
    def update(self, t, dt):
        if t < self.delay: return
        
        for pattern in self.shrapnel:
            pattern.update(t, dt)
        
        if not self.alive: return
        
        self.fired = True
        
        # TODO: not sure on exact order of shrapnel operations within frame
        if 'lastTime' in self.bullet_src['extra_param']:
            if t - self.delay >= self.bullet_src['extra_param']['lastTime']:
                self.die(t)
                return
        
        dt = min(dt, t - self.delay)
        self.position += self.velocity * dt
        if self.gravity < 0.0:
            if (self.position.y < 0.0 and self.velocity.y < 0.0) or ('shrapnel' in self.bullet_src['extra_param'] and self.velocity.y < 0.0):
                self.die(t)
                return
        else:
            if (self.position - self.position0).ground_magnitude_squared() > self.max_range * self.max_range:
                self.die(t)
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
                acceleration_u = current_acceleration['u'] * dt * self.acceleration_sign
                if acceleration_u < 0 and acceleration_u * acceleration_u >= self.velocity.ground_magnitude_squared():
                    acceleration_u = -1.0 * acceleration_u
                    self.acceleration_sign *= -1.0
                self.velocity += self.velocity.normalized() * acceleration_u
            if 'v' in current_acceleration:
                self.velocity += self.velocity.ground_cross().normalized() * current_acceleration['v'] * dt
        else:
            in_bounds = self.weapon_set.in_bounds(self.position)
            if self.entered_bounds and not in_bounds:
                self.die(t)
            elif not self.entered_bounds and in_bounds:
                self.in_bounds = True

        self.velocity.y += self.gravity * dt
        
        self.update_model_rotation()
    
    def die(self, t):
        self.alive = False
        if 'shrapnel' in self.bullet_src['extra_param']:
            shrapnel_src = self.bullet_src['extra_param']['shrapnel']
            shrapnel_index = 1
            while shrapnel_index in shrapnel_src:
                bullet_id = shrapnel_src[shrapnel_index]['bullet_ID']
                barrage_id = shrapnel_src[shrapnel_index]['barrage_ID']
                bullet_src = bullet_srcs[bullet_id]
                barrage_src = barrage_srcs[barrage_id]
                self.shrapnel.append(Pattern(self.weapon_set, self.weapon_src, barrage_src, bullet_src, t, self))
                shrapnel_index += 1
    
    def any_alive(self):
        return self.alive or any(pattern.alive() for pattern in self.shrapnel)

    def draw(self, frame):
        if not self.fired: return frame
        
        if self.alive:
            model_res_x, model_res_z = self.model_rotated.size
            x_corner_px = int(round(self.position.x * self.weapon_set.render_ppu - model_res_x / 2))
            # flip z
            z_corner_px = int(round(frame.size[1] - (self.position.z / camera_slope + self.position.y) * self.weapon_set.render_ppu - model_res_z / 2))
            overlay = Image.new('RGBA', frame.size)
            overlay.paste(self.model_rotated, (x_corner_px, z_corner_px))
            return Image.alpha_composite(frame, overlay)
        else:
            for pattern in self.shrapnel:
                frame = pattern.draw(frame)
            return frame

class Pattern():
    def __init__(self, weapon_set, weapon_src, barrage_src, bullet_src, extra_delay, parent_bullet = None):
        self.weapon_set = weapon_set
        self.barrage_src = barrage_src
        self.bullet_src = bullet_src
        self.extra_delay = extra_delay
        self.parent_bullet = parent_bullet
        
        self.bullets = []
    
        if barrage_src['trans_ID'] >= 0:
            raise NotImplementedError('trans_ID not implemented.')
        
        random_offset_x = bullet_src['extra_param'].get('randomOffsetX', 0)
        random_offset_z = bullet_src['extra_param'].get('randomOffsetZ', 0)

        parallel = barrage_src['primal_repeat'] + 1
        serial = barrage_src['senior_repeat'] + 1
        
        first_delay = barrage_src['first_delay'] + extra_delay
        all_delay = barrage_src['delay']
        serial_delay = barrage_src['senior_delay']
        parallel_delay = 0 # barrage_src['delta_delay'] # doesn't actually do anything?
        
        has_random_angle = barrage_src.get('random_angle', False)
        offset_angle = math.radians(barrage_src['angle'])
        delta_angle = math.radians(barrage_src['delta_angle'])
        
        offset_x = barrage_src['offset_x']
        delta_offset_x = barrage_src['delta_offset_x']
        
        offset_z = barrage_src['offset_z']
        delta_offset_z = barrage_src['delta_offset_z']
        
        offset_prioritise = barrage_src['offset_prioritise']
        if offset_prioritise: print('offset_prioritise', offset_angle, offset_z)
        
        bullet_idx = 0
        for serial_idx in range(serial):
            for parallel_idx in range(parallel):
                # not always applied?
                if bullet_src['extra_param'].get('gravity', 0.0) != 0.0:
                    random_offset = Vector(self.weapon_set.random_centered(random_offset_x),
                                           0.0,
                                           self.weapon_set.random_centered(random_offset_z))
                else:
                    random_offset = Vector(0.0, 0.0, 0.0)
                
                max_range = bullet_src['range'] + self.weapon_set.random_centered(bullet_src['range_offset'], count = False)
                delay = first_delay + serial_delay * serial_idx + parallel_delay * parallel_idx + all_delay * bullet_idx
                self.weapon_set.delays.append(delay)
                
                speed = bullet_src['velocity'] + self.weapon_set.random_centered(bullet_src['extra_param'].get('velocity_offset', 0.0)) * 2.0
                
                if self.parent_bullet:
                    print(self.parent_bullet.position)
                    position0 = self.parent_bullet.position.copy()
                    random_target_pos = self.weapon_set.target_pos + random_offset
                    angle0 = offset_angle + delta_angle * parallel_idx
                    if has_random_angle:
                        angle0 = self.weapon_set.random_centered(angle0)
                else:
                    if bullet_src['extra_param'].get('airdrop', False):
                        if weapon_src['aim_type'] == 1:
                            random_target_pos = self.weapon_set.target_pos + random_offset
                        else:
                            random_target_pos = self.weapon_set.start_pos + random_offset
                        
                        position0 = random_target_pos.copy()
                    else:
                        position0 = self.weapon_set.start_pos.copy()
                        random_target_pos = self.weapon_set.target_pos + random_offset
                    position0.x += offset_x + delta_offset_x * parallel_idx
                    position0.z += offset_z + delta_offset_z * parallel_idx
                    
                    position0 += Vector(bullet_src['extra_param'].get('offsetX', 0.0),
                                        bullet_src['extra_param'].get('offsetY', 0.0),
                                        bullet_src['extra_param'].get('offsetZ', 0.0))
                    
                    if weapon_src['type'] == 19: # unaimed BB barrages?
                        random_target_pos = Vector(self.weapon_set.target_pos.x,
                                                   position0.y,
                                                   position0.z) + random_offset
                        
                    #print(barrage_src['id'], position0)
                    aim_vector = random_target_pos - position0
                    aim_angle = aim_vector.ground_angle()
                    
                    angle0 = offset_angle + delta_angle * parallel_idx
                    if has_random_angle:
                        angle0 = self.weapon_set.random_centered(angle0)
                    
                    if weapon_src['aim_type'] == 1:
                        angle0 += aim_angle
                    
                velocity0 = Vector.from_angle(angle0) * speed * velocity_factor
                #print(barrage_src['id'], velocity0)
                #print(barrage_src['id'], bullet_src['id'], position0)
                
                bullet = Bullet(self.weapon_set, weapon_src, bullet_src, delay, position0, velocity0, max_range, random_target_pos)
                self.bullets.append(bullet)
                bullet_idx += 1
    
    def update(self, t, dt):
        for bullet in self.bullets:
            bullet.update(t, dt)

    def draw(self, frame):
        for bullet in self.bullets:
            frame = bullet.draw(frame)
        return frame
    
    def alive(self):
        return any(bullet.any_alive() for bullet in self.bullets)

# Not resettable.
class WeaponSet():
    def __init__(self, weapon_ids, world_size, border_size, output_ppu, supersample, start_pos, target_pos, seed):
        self.world_size = world_size
        self.border_size = border_size
        self.output_ppu = output_ppu
        self.render_ppu = output_ppu * supersample
        self.supersample = supersample
        self.start_pos = start_pos
        self.target_pos = target_pos
        self.rng = random.Random(str(seed))
        self.rng_count = 0
        self.t = 0.0
        
        self.patterns = []
        self.delays = []
        
        for weapon_id in weapon_ids:
            extra_delay = 0
            if isinstance(weapon_id, tuple):
                extra_delay = weapon_id[1]
                weapon_id = weapon_id[0]
            weapon_src = weapon_srcs[weapon_id]
            
            barrage_index = 1
            while barrage_index in weapon_src['barrage_ID']:
                barrage_src = barrage_srcs[weapon_src['barrage_ID'][barrage_index]]
                bullet_src = bullet_srcs[weapon_src['bullet_ID'][barrage_index]]
                pattern = Pattern(self, weapon_src, barrage_src, bullet_src, extra_delay)
                self.patterns.append(pattern)
                barrage_index += 1
    
    def random(self, max_value = 1.0, count = True):
        if max_value == 0.0: return 0.0
        if count: self.rng_count += 1
        return self.rng.random(0.0, max_value)
    
    def random_centered(self, width = 1.0, count = True):
        if width == 0.0: return 0.0
        if count: self.rng_count += 1
        return self.rng.uniform(-0.5 * width, 0.5 * width)
    
    def in_bounds(self, v):
        return (v.x >= -self.border_size and 
                v.x < self.world_size[0] + self.border_size and
                v.z >= -self.border_size and 
                v.z < self.world_size[1] + self.border_size)
    
    def draw(self, animator, pad_duration = None):
        render_res = (self.render_ppu * self.world_size[0], self.render_ppu * self.world_size[1] // camera_slope)
        output_res = (self.output_ppu * self.world_size[0], self.output_ppu * self.world_size[1] // camera_slope)
        dt = 1.0 / animator.fps
        
        while any(pattern.alive() for pattern in self.patterns):
            self.t += dt
            frame = Image.new('RGBA', render_res, color = background_color)
            for pattern in self.patterns:
                frame = pattern.draw(frame)
                pattern.update(self.t, dt)
            frame = frame.resize(output_res, Image.BOX)
            animator.write_frame(frame)
            
        if pad_duration is not None:
            # Compute max delay.
            self.delays.sort()
            max_delta = 0.0
            for i in range(len(self.delays) - 1):
                max_delta = max(max_delta, self.delays[i+1] - self.delays[i])
            
            num_pad_frames = math.ceil((pad_duration + max_delta) * animator.fps)
            for i in range(num_pad_frames):
                frame = Image.new('RGBA', output_res, color = background_color)
                animator.write_frame(frame)

# weapon_id elements may be a 2-tuple where the second element is an extra delay.
# Animations with random elements will be repeated as long as they are not estimated to exceed max_repeat_duration (not including pads).
def create_barrage_anim(animator, weapon_ids, world_size, ppu = 10, supersample = 2, max_repeat_duration = 6.0, pad_duration = 0.5):
    start_pos = Vector(5, 0.0, world_size[1] / 2)
    target_pos = Vector(world_size[0] - 25, 0.0, world_size[1] / 2)
    border_size = 5
    seed = [weapon_ids, 0]
    
    weapon_set = WeaponSet(weapon_ids, world_size, border_size, ppu, supersample, start_pos, target_pos, seed)
    weapon_set.draw(animator, pad_duration)
    
    if weapon_set.rng_count > 0:
        last_iteration_time = weapon_set.t
        total_time = weapon_set.t
        while total_time + last_iteration_time <= max_repeat_duration:
            seed[1] += 1
            weapon_set = WeaponSet(weapon_ids, world_size, border_size, ppu, supersample, start_pos, target_pos, seed)
            weapon_set.draw(animator, pad_duration)
            last_iteration_time = weapon_set.t
            total_time += last_iteration_time
    