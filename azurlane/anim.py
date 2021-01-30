import subprocess
from PIL import Image, ImageDraw

startupinfo = subprocess.STARTUPINFO()
startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
startupinfo.wShowWindow = 7 # SW_SHOWMINNOACTIVE

class Animator():
    def reset(self):
        self.frame_filenames = []
        self.frame_index = 0

    def write_frame(self, frame):
        frame_filename = self.temp_pattern % self.frame_index
        self.frame_index += 1
        frame.convert('RGB').save(frame_filename)
        self.frame_filenames.append(frame_filename)

class GifAnimator(Animator):
    temp_pattern = 'temp/frame_%04d.gif'
    def __init__(self, fps = 50, color_count = 16, lossy = 20):
        self.fps = fps
        self.color_count = color_count
        self.lossy = lossy
        self.reset()
    
    def write_animation(self, filename_out):
        gifsicle_cmd = ['./gifsicle.exe',
                    '--output=%s' % filename_out,
                    '--loopcount=0',
                    '--colors=%d' % self.color_count,
                    '--lossy=%d' % self.lossy,
                    '--delay=%d' % round(100 / self.fps),
                    '-O1'] + self.frame_filenames
                    
        proc = subprocess.Popen(gifsicle_cmd, startupinfo = startupinfo)
        proc.wait()

try:
    import webp

    class WebPAnimator(Animator):
        def reset(self):
            self.frames = []
        
        def __init__(self, fps = 60, lossless=1, quality=100, preset=webp.WebPPreset.DEFAULT):
            self.fps = fps
            self.quality = quality
            self.preset = preset
            self.reset()
        
        def write_frame(self, frame):
            self.frames.append(frame)
        
        def write_animation(self, filename_out):
            if not self.frames: return
            webp.save_images(self.frames, filename_out, fps=self.fps, quality=self.quality, preset=self.preset)
except:
    print('Warning: webp not supported')
    
class Img2WebPAnimator(Animator):
    temp_pattern = 'temp/frame_%04d.png'
    def __init__(self, fps = 60, quality = 20):
        self.fps = fps
        self.quality = quality
        self.reset()
    
    def write_animation(self, filename_out):
        cmd = ['./img2webp.exe',
                    '-o', filename_out,
                    '-min_size',
                    '-mixed',
                    '-d', str(int(round(1000 / self.fps))),
                    '-q', str(self.quality),
                    '-m', '6',
        ] + self.frame_filenames
                    
        proc = subprocess.Popen(cmd, startupinfo = startupinfo)
        proc.wait()

class Vp8Animator(Animator):
    temp_pattern = 'temp/frame_%04d.bmp'
    
    def __init__(self, fps = 60, crf = 10):
        self.fps = fps
        self.crf = crf
        self.reset()
    
    def write_frame(self, frame):
        frame_filename = self.temp_pattern % frame_index
        self.frame_index += 1
        frame.convert('RGB').save(frame_filename)
        self.frame_filenames.append(frame_filename)
    
    def write_animation(self, filename_out):
        ffmpeg_cmd = [
            'ffmpeg', 
            '-y',
            '-r', str(self.fps),
            '-i', self.temp_pattern,
            '-vframes', str(len(self.frame_filenames)),
            '-c:v', 'libvpx',
            '-b:v', '1M',
            '-crf', str(self.crf),
            '-pix_fmt', 'yuv420p',
            filename_out,
        ]
        #print(ffmpeg_cmd)
        subprocess.Popen(ffmpeg_cmd, startupinfo = startupinfo).wait()        

class Vp9Animator(Animator):
    temp_pattern = 'temp/frame_%04d.bmp'
    
    def __init__(self, fps = 60, crf = 30):
        self.fps = fps
        self.crf = crf
        self.reset()
    
    def write_animation(self, filename_out):
        ffmpeg_cmd = [
            'ffmpeg', 
            '-y',
            '-r', str(self.fps),
            '-i', self.temp_pattern,
            '-vframes', str(len(self.frame_filenames)),
            '-c:v', 'libvpx-vp9',
            '-b:v', '0',
            '-crf', str(self.crf),
            '-pix_fmt', 'yuv420p',
            filename_out,
        ]
        #print(ffmpeg_cmd)
        subprocess.Popen(ffmpeg_cmd, startupinfo = startupinfo).wait()
