import numpy
from PIL import Image, ImageDraw

rare_xp = [
0,
100,
300,
600,
1000,
1500,
2100,
2900,
4000,
5500,
7500,
10100,
13500,
17900,
23500,
30500,
39100,
49600,
62300,
77500,
95500,
116600,
141200,
169700,
202500,
240000,
282600,
330900,
385500,
447000,
]

elite_xp = [
0,
100,
300,
600,
1000,
1600,
2500,
3800,
5600,
8000,
11200,
15400,
20800,
27600,
36000,
46300,
58800,
73800,
91600,
112500,
136900,
165200,
197800,
235100,
277700,
326200,
381200,
443300,
513300,
592000,
]

ssr_xp = [
0,
100,
300,
700,
1400,
2500,
4100,
6400,
9600,
13900,
19500,
26600,
35500,
46500,
59900,
76000,
95100,
117600,
143900,
174400,
209500,
249600,
295300,
347200,
405900,
472000,
546100,
629000,
721500,
824400,
]

divisor = 1000
bar_height = 20
text_offset_x = -12
text_offset_y = 5

image_height = bar_height * 4
image_width = 900000 // divisor

def int_ceiling_divide(n, d):
    return (n - 1) // d + 1

def draw_bar(draw, idx, xp, even_color, odd_color):
    left = 0
    top = idx * bar_height
    bottom = top + bar_height
    odd = False
    for lv in [5, 10, 15, 20, 25, 30]:
        right = int_ceiling_divide(xp[lv - 1], divisor)
        color = odd_color if odd else even_color
        draw.rectangle([left, top, right, bottom], fill=color)
        if (right - left) >= 10:
            draw.text((right + text_offset_x, top + text_offset_y),
                      '%2d' % lv, fill = (0, 0, 0, 255), align = 'right')
        left = right
        odd = not odd

def draw_scale(draw, idx):
    left = 0
    top = idx * bar_height
    bottom = top + bar_height
    odd = False
    for xp in range(50000, 900001, 50000):
        right = int_ceiling_divide(xp, divisor)
        color = (255, 255, 255, 255) if odd else (0, 0, 0, 255)
        draw.rectangle([left, top, right, bottom], fill=color)
        if odd:
            draw.text((right + text_offset_x - 12, top + text_offset_y),
                      '%2dk' % (xp / 1000), fill = (0, 0, 0, 255), align = 'right')
        left = right
        odd = not odd

img = Image.new('RGBA', (image_width, image_height), color = (0, 0, 0, 0))
draw = ImageDraw.Draw(img)

draw_bar(draw, 0, rare_xp, (127, 127, 255, 255), (191, 191, 255, 255))
draw_bar(draw, 1, elite_xp, (255, 127, 255, 255), (255, 191, 255, 255))
draw_bar(draw, 2, ssr_xp, (255, 191, 63, 255), (255, 223, 159, 255))

draw_scale(draw, 3)

img.save('meowfficer_xp.png')
