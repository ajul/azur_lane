import load_lua
import math
from PIL import Image, ImageDraw

bullet_srcs = load_lua.load_sharecfg('bullet_template')
weapon_srcs = load_lua.load_sharecfg('weapon_property')
barrage_srcs = load_lua.load_sharecfg('barrage_template')

bullet_name_map = {
    'Bullet1' : 'bullet-04-y',
    'BulletUK' : 'bullet_UK',
    'kuasheAP' : 'kuasheAP',
}

# default units: seconds, radians, game units

fps = 30
duration = 1
velocity_scale = 3.0 # 
time_stretch = 2
# pixels per in-game unit
ppu = 10
world_size = (60, 40)
start_pos = (0, 20)
image_res = tuple(ppu * x for x in world_size)

def get_model(bullet_src):
    model_name = bullet_src['modle_ID']
    return Image.open('bullet_models/%s.png' % bullet_name_map[model_name])

def put_on_black_background(image):
    black = Image.new('RGBA', image.size, color = (0, 0, 0, 255))
    return Image.alpha_composite(black, image)

class Bullet():
    def __init__(self, model, size_x, size_z, delay, x0, z0, angle, v0, max_range):
        model_res = (size_x * ppu, size_z * ppu)
        model_resized = model.resize(model_res, Image.LANCZOS)
        self.model = model_resized.rotate(-math.degrees(angle), Image.BICUBIC, True)
        self.delay = delay
        self.x0 = x0
        self.z0 = z0
        self.angle = angle
        self.v0 = v0
        self.max_range = max_range

    def position(self, t):
        elapsed = t - self.delay
        if elapsed < 0.0: return None, None
        distance = elapsed * self.v0
        if distance > self.max_range: return None, None

        x = self.x0 + distance * math.cos(self.angle)
        z = self.z0 + distance * math.sin(self.angle)
        return x, z

    def draw(self, frame, t):
        x, z = self.position(t)
        if x is None: return frame
        model_res_x, model_res_z = self.model.size
        x_corner_px = int(round(x * ppu - model_res_x / 2))
        z_corner_px = int(round(z * ppu - model_res_z / 2))
        overlay = Image.new('RGBA', frame.size)
        overlay.paste(self.model, (x_corner_px, z_corner_px))
        return Image.alpha_composite(frame, overlay)

class Barrage():
    def __init__(self, barrage_src, bullet_src):
        model = get_model(bullet_src)
        
        size_x = bullet_src['cld_box'][1]
        size_z = bullet_src['cld_box'][2]
        
        max_range = bullet_src['range'] # + offset?
        v0 = bullet_src['velocity'] * velocity_scale

        parallel = barrage_src['primal_repeat'] + 1
        serial = barrage_src['senior_repeat'] + 1
        serial_delay = barrage_src['senior_delay']
        
        random_angle = math.radians(barrage_src['random_angle'])
        angle = math.radians(barrage_src['angle'])
        delta_angle = math.radians(barrage_src['delta_angle'])
        delta_offset_z = barrage_src['delta_offset_z'] 
        
        self.bullets = []

        delay = 0
    
        for serial_idx in range(serial):
            x0 = start_pos[0]
            if parallel == 0:
                angle = 0
            else:
                angle = -0.5 * (parallel - 1) * delta_angle
            z0 = -0.5 * (parallel - 1) * delta_offset_z + start_pos[1]
            for parallel_idx in range(parallel):
                self.bullets.append(Bullet(model, size_x, size_z, delay, x0, z0, angle, v0, max_range))
                angle += delta_angle
                z0 += delta_offset_z
            delay += serial_delay

    def draw(self, frame, t):
        for bullet in self.bullets:
            frame = bullet.draw(frame, t)
        return frame
        

def create_weapon_gif(weapon_id):
    weapon_src = weapon_srcs[weapon_id]
    bullet_src = bullet_srcs[weapon_src['bullet_ID'][1]]
    barrage_src = barrage_srcs[weapon_src['barrage_ID'][1]]

    """
    model = get_model(bullet_src)
    palette_model = model.convert('RGB').quantize()
    palette_model.save('test_model.gif')
    palette = palette_model.palette
    """

    barrage = Barrage(barrage_src, bullet_src)

    frames = []
    
    for frame_index in range(duration * fps * time_stretch):
        t = frame_index / fps / time_stretch
        frame = Image.new('RGBA', image_res)
        frame = barrage.draw(frame, t)
        frame = put_on_black_background(frame)
        frames.append(frame)

    frames[0].save('test_barrage.gif',
                   save_all=True, append_images=frames[1:],
                   duration=1000 // fps, loop=0)

# 22000
# 31000 = 100mm
# weapon 90100 = 136.8mm
# bullet 1510 = Mk7 406 mm
create_weapon_gif(31000)
