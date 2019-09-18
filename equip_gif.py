import load_lua
import math
import subprocess
from PIL import Image, ImageDraw

bullet_srcs = load_lua.load_sharecfg('bullet_template')
weapon_srcs = load_lua.load_sharecfg('weapon_property')
barrage_srcs = load_lua.load_sharecfg('barrage_template')
equip_srcs = load_lua.load_sharecfg('equip_data_statistics', key_type=int)

bullet_models = {
    'BulletUSA' : ('bullet-04-y', 4, 1), # normal
    'BulletUK' : ('bullet_UK', 6, 2), # normal
    'BulletJP' : ('bulletjp', 6, 2), # HE
    'Bullet1' : ('kuasheAP', 6, 2), # AP
    'kuashe' : ('bullet_UK', 8, 4), # big normal
    'kuasheHE' : ('kuasheHE', 8, 4), # big HE
    'kuasheAP' : ('kuasheAP', 8, 4), # big AP
    'kuasheSAP' : ('bulletUSA', 8, 4), # big SAP (not sure on model)
}

# default units: seconds, radians, game units

fps = 50 # some browsers don't like more than 50; 30 is the highest integer factor of common frame rates
time_stretch = 1

velocity_scale = 6

# pixels per in-game unit
ppu = 10
world_size = (75, 30)
start_pos = (5, world_size[1] // 2)
camera_slope = 2
image_res = (ppu * world_size[0], ppu * world_size[1] // camera_slope)

# gif stuff
color_count = 16
lossy = 20 # default 20

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
    #print(model_name)
    filename, length, width = bullet_models[model_name]
    model = Image.open('bullet_models/%s.png' % filename)
    new_res_x = round(ppu * length)
    new_res_z = round(ppu * width)
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

def get_equip_sub_srcs(equip_src):
    weapon_src = weapon_srcs[equip_src['weapon_id'][1]]
    bullet_src = bullet_srcs[weapon_src['bullet_ID'][1]]
    barrage_src = barrage_srcs[weapon_src['barrage_ID'][1]]
    return weapon_src, bullet_src, barrage_src

def create_equip_gif(equip_src, duration):
    weapon_src, bullet_src, barrage_src = get_equip_sub_srcs(equip_src)

    barrage = Barrage(barrage_src, bullet_src)

    frame_filenames = []

    frame_count = duration * fps * time_stretch
    
    for frame_index in range(frame_count):
        t = frame_index / fps / time_stretch
        frame = Image.new('RGBA', image_res)
        frame = barrage.draw(frame, t)
        frame = put_on_black_background(frame)
        frame_filename = 'weapon_gif_out/frame_%02d.gif' % frame_index
        frame.convert('RGB').save(frame_filename)
        frame_filenames.append(frame_filename)

    filename_out = 'weapon_gif_out/bullet_pattern_equip_%d.gif' % equip_src['id']

    gifsicle_cmd = ['./gifsicle.exe',
                    '--output=%s' % filename_out,
                    '--loopcount=0',
                    '--colors=%d' % color_count,
                    '--lossy=%d' % lossy,
                    '--delay=%d' % round(100 / fps),
                    '-O1'] + frame_filenames

    subprocess.run(gifsicle_cmd)

# (bullet_id, barrage_id) -> equip_id
seen_patterns = {}

for equip_id, equip_src in equip_srcs.items():
    if equip_id < 1000:
        # These are default weapons.
        continue
    if 'name' not in equip_src: continue
    if 'type' not in equip_src: continue
    if equip_src['type'] in [1, 2]:
        # DD, CL
        duration = 1
    elif equip_src['type'] in [3, 11]:
        # CA, CB
        duration = 2
    else:
        continue
    # label-less equips may not be proper equips
    if len(equip_src['label']) == 0:
        continue
    try:
        weapon_src, bullet_src, barrage_src = get_equip_sub_srcs(equip_src)
    except KeyError:
        print(equip_src['name'], ':', 'missing pattern data')
        continue
    pattern = (bullet_src['id'], barrage_src['id'])
    base_log = '%s (equip_id %d): bullet_id %d, barrage_id %d' % (
        equip_src['name'],
        equip_id,
        pattern[0],
        pattern[1])
    if pattern in seen_patterns:
        print('%-100s => equip_id %d' % (
            base_log,
            seen_patterns[pattern]))
    else:
        print(base_log)
        seen_patterns[pattern] = equip_id
        create_equip_gif(equip_src, duration)

# weapon 11000, bullet 999 (BulletUSA), barrage 1000 = 76mm
# weapon 11200, bullet 1000 (BulletUK), barrage 1001 = gearing T1
# weapon 11240, bullet 1006 (BulletJP), barrage 1001 = gearing T3
# weapon 12100 = cleveland T1
# weapon 31000, bullet 1200 (BulletUK), barrage 1001 = akizuki
# weapon 41100, bullet 1303 (Bullet1), barrage 1001 = Z-46
# weapon 42200, bullet 1304 (Bullet1), barrage 1001 = tabasco
# weapon 43000, bullet 1401 (kuasheAP), barrage 1206 = hipper
# weapon 90140 = 136.8mm T3
# bullet 1510 = Mk7 406 mm
# create_weapon_gif(12100)
