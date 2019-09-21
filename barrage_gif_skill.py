import barrage_gif
import load_lua
import sys

skill_data_srcs = load_lua.load_sharecfg('skill_data_template', key_type=int)

range_limit = 80
max_duration = 5.0
pad_duration = 0.25

world_size = (75, 40)
# pixels per in-game unit
ppu = 10

for skill_id, skill_data_src in skill_data_srcs.items():
    try:
        skill_src = load_lua.load_skill(skill_id)
    except FileNotFoundError:
        #print('No skill file for skill_id', skill_id)
        continue
    last_index = 0
    while last_index + 1 in skill_src:
        last_index += 1
    if last_index == 0: continue
    last_level = skill_src[last_index]
    if 'effect_list' not in last_level: continue
    last_effects = last_level['effect_list']

    weapon_ids = []
    for idx, effect in last_effects.items():
        if effect['type'] != 'BattleSkillFire': continue
        weapon_ids.append(effect['arg_list']['weapon_id'])
    if len(weapon_ids) == 0: continue
    print(skill_data_src['name'], skill_id, ':', weapon_ids)
    filename_out = 'skill_gif_out/bullet_pattern_skill_%d.gif' % skill_id
    try:
        barrage_gif.create_barrage_gif(filename_out, weapon_ids, world_size, ppu,
                                       range_limit = range_limit, max_duration = max_duration, pad_duration = pad_duration)
    except:
        print("Unexpected error:", sys.exc_info())
    

