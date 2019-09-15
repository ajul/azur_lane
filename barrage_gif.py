import load_lua
import math
from PIL import Image, ImageDraw

bullet_srcs = load_lua.load_sharecfg('bullet_template')
weapon_srcs = load_lua.load_sharecfg('weapon_property')
barrage_srcs = load_lua.load_sharecfg('barrage_template')

bullet_name_map = {
    'BulletUK' : 'bullet_UK',
}

# default units: seconds, radians, game units

fps = 30
duration = 2.0
# pixels per in-game unit
ppu = 20
world_size = (60, 20)
image_res = tuple(ppu * x for x in world_size)

class Bullet():
    def __init__(self, model, size_x, size_z, delay, x0, z0, angle, v0, max_range):
        model_res = (size_x * ppu, size_y * ppu)
        self.model = model.resize(model_res, Image.LANCZOS)
        self.delay = delay
        self.x0 = x0
        self.z0 = z0
        self.angle = angle
        self.v0 = v0
        self.max_range = max_range

    def position(self, t):
        elapsed = t - self.delay
        if elapsed < 0.0: return None
        distance = elapsed * v0
        if distance > max_range: return None

        x = self.x0 + distance * math.cos(self.angle)
        z = self.z0 + distance * math.sin(self.angle)
        return x, z

    def draw(self, frame, t):
        pass

class Barrage():
    def __init__(self, barrage_src, bullet_src):
        model_name = bullet_src['modle_ID']
        model = Image.open('bullet_models/%s.png' % bullet_name_map[model_name])
        size_x = bullet_src['cld_box'][1]
        size_z = bullet_src['cld_box'][2]
        
        max_range = bullet_src['range'] # + offset?
        v0 = bullet_src['velocity'] * 3.0

        parallel = barrage_src['primal_repeat'] + 1
        serial = barrage_src['senior_repeat'] + 1
        serial_delay = barrage_src['senior_delay']
        
        random_angle = math.radians(barrage_src['random_angle'])
        #angle_deg = math.radians(barrage_src['angle'])
        delta_angle = math.radians(barrage_src['delta_angle'])
        delta_offset_z = barrage_src['delta_offset_z'] 
        
        self.bullets = []

        delay = 0
    
        for serial_idx in range(serial):
            x0 = 0
            if random_angle:
                # TODO: better random representation
                delta_angle_deg = angle_deg / parallel
            if parallel == 0:
                angle = 0
            else:
                angle = -0.5 * (parallel - 1) * delta_angle
            z0 = -0.5 * (parallel - 1) * delta_offset_z
            for parallel_idx in range(parallel):
                self.bullets.append(Bullet(model, size_x, size_z, delay, x0, z0, angle, v0, max_range))
                angle += delta_angle
                z0 += delta_offset_z
            delay += serial_delay

    def draw(self, frame, t):
        for bullet in bullets:
            bullet.draw(frame, t)
        

def create_weapon_gif(weapon_id):
    weapon_src = weapon_srcs[weapon_id]
    bullet_src = bullet_srcs[weapon_src['bullet_ID'][1]]
    barrage_src = barrage_srcs[weapon_src['barrage_ID'][1]]

    barrage = Barrage(barrage_src, bullet_src)
    
    for frame_index in range(duration * fps):
        t = frame_index / fps
        frame = Image.new('RGBA', image_res)
        

create_weapon_gif(31000)
