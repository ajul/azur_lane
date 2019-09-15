import numpy
import matplotlib.pyplot as plt

figsize = (16, 9)
dpi = 120

max_num_planes = 24

def aa_damage(num_planes):
    if num_planes >= 20:
        return [0.05] * num_planes
    else:
        result = []
        leftover_damage = 1 - 0.05 * num_planes
        for i in range(num_planes):
            extra_damage = leftover_damage * (0.3 + 0.2 * i / num_planes)
            result.append(0.05 + extra_damage)
            leftover_damage -= extra_damage
        return result

data = []
x = [i+1 for i in range(max_num_planes)]

for i in range(max_num_planes):
    data.append(aa_damage(i+1))

fig = plt.figure(figsize=figsize)
ax = plt.subplot(111)



previous_sum = numpy.zeros((max_num_planes,))
for i in range(max_num_planes):
    current_damage = numpy.array([data[j][i] for j in range(i, max_num_planes)])
    current_sum = current_damage + previous_sum
    gray_level = 1.0 - 0.15 * (i % 5)
    if i < 5:
        color = (gray_level, 0.25, 0.25)
    elif i < 10:
        color = (0.25, 0.25, gray_level)
    elif i < 15:
        color = (0.25, gray_level, 0.25)
    elif i < 20:
        color = (gray_level, 0.25, gray_level)
    else:
        color = (0.25, gray_level, gray_level)
    plt.bar(x[i:], current_damage, 0.75, bottom = previous_sum, color = color)
    previous_sum = current_sum[1:]

ax.set_axisbelow(True)
ax.grid(True, axis='y')
ax.set_title('Mean AA damage (each block is 1 aircraft)')
ax.set_xlabel('Number of aircraft')
ax.set_ylabel('Mean damage multiplier')
ax.set_xlim(left = 0, right = max_num_planes + 1)
ax.set_ylim(bottom = 0, top = max_num_planes * 0.05)
ax.set_xticks(numpy.arange(1, max_num_planes+1, 1))
ax.set_yticks(numpy.arange(0, (max_num_planes + 0.5) * 0.05, 0.05))

plt.savefig('mean_aa_damage_plot.png', dpi = dpi, bbox_inches = "tight") 
