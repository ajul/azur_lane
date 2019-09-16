import load_lua
import math
from PIL import Image, ImageDraw

bullet_srcs = load_lua.load_sharecfg('bullet_template')
weapon_srcs = load_lua.load_sharecfg('weapon_property')
barrage_srcs = load_lua.load_sharecfg('barrage_template')

bullet_models = {
    'BulletUSA' : ('bullet-04-y', 5), # normal
    'BulletUK' : ('bullet_UK', 6), # normal
    'BulletJP' : ('bulletjp', 6), # HE
    'Bullet1' : ('kuasheAP', 6), # AP
    'kuashe' : ('bullet_UK', 8), # big normal
    'kuasheHE' : ('kuasheHE', 8), # big HE
    'kuasheAP' : ('kuasheAP', 8), # big AP
}

# default units: seconds, radians, game units

fps = 30 # some browsers don't like more than 50; 30 is the highest integer factor of common frame rates
duration = 1
velocity_scale = 6
time_stretch = 1
# pixels per in-game unit
ppu = 10
world_size = (80, 40)
start_pos = (10, world_size[1] // 2)
camera_slope = 2
image_res = (ppu * world_size[0], ppu * world_size[1] // camera_slope)

serial_patterns = [
    [],
    [0],
    [0, 1],
    [0, 1, 2],
    [0, 2, 1, 3],
    [0, 4, 3, 2, 4],
]

def get_model(bullet_src):
    model_name = bullet_src['modle_ID']
    print(model_name)
    filename, length = bullet_models[model_name]
    model = Image.open('bullet_models/%s.png' % filename)
    new_res_x = round(ppu * length)
    scale = length * ppu / model.size[0]
    new_res_z = round(scale * model.size[1])
    return model.resize((new_res_x, new_res_z), Image.LANCZOS)

def put_on_black_background(image):
    black = Image.new('RGBA', image.size, color = (0, 0, 0, 255))
    return Image.alpha_composite(black, image)

class Bullet():
    def __init__(self, model, delay, x0, z0, angle, v0, max_range):
        self.model = model.rotate(-math.degrees(math.atan(math.tan(angle) / camera_slope)), Image.BICUBIC, True)
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
        z_corner_px = int(round(z * ppu / camera_slope - model_res_z / 2))
        overlay = Image.new('RGBA', frame.size)
        overlay.paste(self.model, (x_corner_px, z_corner_px))
        return Image.alpha_composite(frame, overlay)

class Barrage():
    def __init__(self, barrage_src, bullet_src):
        model = get_model(bullet_src)
        
        max_range = bullet_src['range'] # + offset?
        v0 = bullet_src['velocity'] * velocity_scale

        parallel = barrage_src['primal_repeat'] + 1
        serial = barrage_src['senior_repeat'] + 1
        serial_delay = barrage_src['senior_delay']
        
        random_angle = math.radians(barrage_src['random_angle'])
        serial_angle = math.radians(barrage_src['angle'])
        delta_angle = math.radians(barrage_src['delta_angle'])
        delta_offset_z = barrage_src['delta_offset_z'] 
        
        self.bullets = []

        delay = 0

        if random_angle and serial > 1:
            #serial_delta_angle = serial_angle / serial
            serial_delta_angle = 0 #TODO: better random representation
        else:
            serial_delta_angle = 0
    
        for serial_idx in range(serial):
            x0 = start_pos[0]
            serial_angle_idx = serial_patterns[serial][serial_idx]
            angle = (serial_angle_idx - (serial - 1) * 0.5) * serial_delta_angle
            if parallel > 1:
                angle += -0.5 * (parallel - 1) * delta_angle
            z0 = -0.5 * (parallel - 1) * delta_offset_z + start_pos[1]
            for parallel_idx in range(parallel):
                self.bullets.append(Bullet(model, delay, x0, z0, angle, v0, max_range))
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

# weapon 11000, bullet 999 (BulletUSA), barrage 1000 = 76mm
# weapon 11200, bullet 1000 (BulletUK), barrage 1001 = gearing T1
# weapon 11240, bullet 1006 (BulletJP), barrage 1001 = gearing T3
# weapon 31000, bullet 1200 (BulletUK), barrage 1001 = akizuki
# weapon 41100, bullet 1303 (Bullet1), barrage 1001 = Z-46
# weapon 42200, bullet 1304 (Bullet1), barrage 1001 = tabasco
# weapon 43000, bullet 1401 (kuasheAP), barrage 1206 = hipper
# weapon 90140 = 136.8mm T3
# bullet 1510 = Mk7 406 mm
create_weapon_gif(22260)
