import numpy
from PIL import Image, ImageDraw

# Total XP is a bit over 4 million.

xp_en = numpy.concatenate((
    numpy.arange(0, 4000, 100),
    numpy.arange(4000, 8000, 200),
    numpy.arange(8000, 10700, 300),
    [10700],
    numpy.arange(12100, 16060, 440),
    [16060],
    numpy.arange(17250, 22425, 575),
    [22425],
    numpy.arange(24000, 26400, 1200),
    numpy.arange(26400, 31200, 2400),
    [31200],
    numpy.arange(36000, 48000, 6000),
    [48000, 72000, 158400],
    numpy.arange(70000, 78000, 2000),
    [78000],
    numpy.arange(85000, 145000, 12000),
    numpy.arange(145000, 235000, 18000),
    numpy.arange(235000, 319000, 21000),
    [319000],
    )).astype('int')

xp_cn = numpy.concatenate((
    numpy.arange(0, 4000, 100),
    numpy.arange(4000, 8000, 200),
    numpy.arange(8000, 11000, 300),
    numpy.arange(11000, 15000, 400),
    numpy.arange(15000, 20000, 500),
    [20000, 21000,
     22000, 24000, 26000,
     30000, 35000,
     40000, 60000, 132000],
    numpy.arange(70000, 78000, 2000),
    [78000],
    numpy.arange(85000, 145000, 12000),
    numpy.arange(145000, 235000, 18000),
    numpy.arange(235000, 319000, 21000),
    [319000],
    )).astype('int')

# level, color
areas = [
    (70, (191, 191, 191)),
    (80, (127, 127, 255)),
    (90, (191, 127, 255)),
    (99, (255, 127, 255)),
    (100, (255, 63, 255)),
    (105, (255, 255, 127)),
    (110, (255, 223, 127)),
    (115, (255, 191, 127)),
    (120, (255, 159, 127)),
]

xp = xp_cn

divisor = 5000

image_height = 20
image_width = (numpy.sum(xp) - 1) // divisor + 1

img = Image.new('RGB', (image_width, image_height), color = (0, 0, 0))
draw = ImageDraw.Draw(img)

prev_column = 0
for level, color in areas:
    column = numpy.sum(xp[:level])
    left = (prev_column - 1) // divisor + 1
    right = (column - 1) // divisor + 1
    draw.rectangle([left, 0, right, image_height], fill=color)
    draw.text((right - 20, image_height // 2 - 5), '%3d' % level, fill = (0, 0, 0), align = 'right')
    prev_column = column

img.save('xp.png')
