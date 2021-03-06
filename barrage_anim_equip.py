from azurlane import anim, barrage, load_lua
import sys
import webp

equip_srcs = load_lua.load_sharecfg('equip_data_statistics', key_type=int)
weapon_srcs = load_lua.load_sharecfg('weapon_property', key_type=int)
barrage_srcs = load_lua.load_sharecfg('barrage_template', key_type=int)
bullet_srcs = load_lua.load_sharecfg('bullet_template', key_type=int)

world_size = (75, 30)
# pixels per in-game unit
ppu = 10

# (bullet_id, barrage_id) -> equip_id
seen_patterns = {}

equip_barrage_image_map = {}

dry_run = True

def get_equip_sub_srcs(equip_src):
    weapon_src = weapon_srcs[equip_src['weapon_id'][1]]
    barrage_src = barrage_srcs[weapon_src['barrage_ID'][1]]
    bullet_src = bullet_srcs[weapon_src['bullet_ID'][1]]
    return weapon_src, barrage_src, bullet_src

for equip_id, equip_src in equip_srcs.items():
    if equip_id < 1000:
        # These are default weapons.
        continue
    if equip_id % 20 != 0:
        # Base level only.
        continue
    if 'name' not in equip_src: continue
    if 'type' not in equip_src: continue
    if equip_src['type'] in [1, 2]:
        # DD, CL
        duration = 1
    elif equip_src['type'] in [3, 11]:
        # CA, CB
        duration = 2
    elif equip_src['type'] in [5, 13]:
        # torpedo, sub torpedo
        duration = None
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
    
    pattern = (barrage_src['id'], bullet_src['id'])
    base_log = '%s (equip_id %d): barrage_id %d, bullet_id %d' % (
        equip_src['name'],
        equip_id,
        pattern[0],
        pattern[1])
    if pattern in seen_patterns:
        print('%-100s => equip_id %d' % (
            base_log,
            seen_patterns[pattern]))
        equip_barrage_image_map[equip_id] = seen_patterns[pattern]
    else:
        print(base_log)
        seen_patterns[pattern] = equip_id
        equip_barrage_image_map[equip_id] = equip_id
        if not dry_run:
            filename_out = 'weapon_anim_out/bullet_pattern_equip_%d.gif' % equip_src['id']
            animator = anim.GifAnimator()
            barrage.create_barrage_anim(animator, [weapon_src['id']], world_size, ppu = ppu)
            animator.write_animation(filename_out)

result_string = 'equip_barrage_image_map = {\n'

for k in sorted(equip_barrage_image_map.keys()):
    result_string += '  %s : %s,\n' % (repr(k), repr(equip_barrage_image_map[k]))

result_string += '}\n'

with open('equip_barrage_image_map.py', 'w', encoding='utf-8') as outfile:
    outfile.write(result_string)
