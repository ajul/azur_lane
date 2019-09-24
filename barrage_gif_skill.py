import barrage_gif
import load_lua
import sys
import traceback

skill_data_srcs = load_lua.load_sharecfg('skill_data_template', key_type=int)
ship_data_srcs = load_lua.load_sharecfg('ship_data_template', key_type=int)

range_limit = 80
max_duration = 10.0
pad_duration = 0.5

world_size = (75, 50)
# pixels per in-game unit
ppu = 10

# compute skill -> ship
skill_to_ship_names_map = {}

for ship_id, ship_data_src in ship_data_srcs.items():
    for skill_id in ship_data_src['buff_list_display'].values():
        if skill_id not in skill_to_ship_names_map:
            skill_to_ship_names_map[skill_id] = []
        if ship_data_src['name'] not in skill_to_ship_names_map[skill_id]:
            skill_to_ship_names_map[skill_id].append(ship_data_src['name'])
        

for skill_id, skill_data_src in skill_data_srcs.items():
    #if skill_id not in [10350, 29062, 29092]: continue
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
    ship_name = ''
    if skill_id in skill_to_ship_names_map:
        ship_names = skill_to_ship_names_map[skill_id]
    print('ships', ship_names, ':', skill_data_src['name'], 'skill_id', skill_id, ': weapon_ids', weapon_ids)
    filename_out = 'skill_gif_out/bullet_pattern_skill_%d.gif' % skill_id
    try:
        barrage_gif.create_barrage_gif(filename_out, weapon_ids, world_size, ppu,
                                       range_limit = range_limit, max_duration = max_duration, pad_duration = pad_duration,
                                       color_count = 32)
    except:
        print(sys.exc_info(), traceback.print_exc())
    

