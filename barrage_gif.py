import load_lua
import math
import subprocess
from PIL import Image, ImageDraw

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
velocity_scale = 6

camera_slope = 2

def get_model(bullet_src, ppu):
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

    def draw(self, frame, t, ppu):
        x, z = self.position(t)
        if x is None: return frame
        model_res_x, model_res_z = self.model.size
        x_corner_px = int(round(x * ppu - model_res_x / 2))
        z_corner_px = int(round(z * ppu / camera_slope - model_res_z / 2))
        overlay = Image.new('RGBA', frame.size)
        overlay.paste(self.model, (x_corner_px, z_corner_px))
        return Image.alpha_composite(frame, overlay)

class Barrage():
    def __init__(self, barrage_src, bullet_src, start_pos, ppu):
        model = get_model(bullet_src, ppu)
        
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
            #serial_angle_idx = serial_patterns[serial][serial_idx]
            #angle = (serial_angle_idx - (serial - 1) * 0.5) * serial_delta_angle
            angle = 0
            if parallel > 1:
                angle += -0.5 * (parallel - 1) * delta_angle
            z0 = -0.5 * (parallel - 1) * delta_offset_z + start_pos[1]
            for parallel_idx in range(parallel):
                self.bullets.append(Bullet(model, delay, x0, z0, angle, v0, max_range))
                angle += delta_angle
                z0 += delta_offset_z
            delay += serial_delay

    def draw(self, frame, t, ppu):
        for bullet in self.bullets:
            frame = bullet.draw(frame, t, ppu)
        return frame

def create_equip_gif(filename_out, bullet_src, barrage_src, duration,  world_size, ppu, fps = 50, time_stretch = 1, color_count = 16, lossy = 20):
    image_res = (ppu * world_size[0], ppu * world_size[1] // camera_slope)
    start_pos = (5, world_size[1] // 2)

    barrage = Barrage(barrage_src, bullet_src, start_pos, ppu)

    frame_filenames = []

    frame_count = duration * fps * time_stretch
    
    for frame_index in range(frame_count):
        t = frame_index / fps / time_stretch
        frame = Image.new('RGBA', image_res)
        frame = barrage.draw(frame, t, ppu)
        frame = put_on_black_background(frame)
        frame_filename = 'weapon_gif_out/frame_%02d.gif' % frame_index
        frame.convert('RGB').save(frame_filename)
        frame_filenames.append(frame_filename)

    gifsicle_cmd = ['./gifsicle.exe',
                    '--output=%s' % filename_out,
                    '--loopcount=0',
                    '--colors=%d' % color_count,
                    '--lossy=%d' % lossy,
                    '--delay=%d' % round(100 / fps),
                    '-O1'] + frame_filenames

    subprocess.run(gifsicle_cmd)

