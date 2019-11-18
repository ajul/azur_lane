import anim
import barrage_anim
import load_lua
import os
import sys
import traceback

skill_data_srcs = load_lua.load_sharecfg('skill_data_template', key_type=int)
skill_display_srcs = load_lua.load_sharecfg('skill_data_display', key_type=int)
ship_data_srcs = load_lua.load_sharecfg('ship_data_template', key_type=int)
ship_stats_srcs = load_lua.load_sharecfg('ship_data_statistics', key_type=int)

range_limit = 80
max_duration = 10.0
pad_duration = 0.5

world_size = (75, 50)
# pixels per in-game unit
ppu = 20

# compute skill -> ship
skill_to_ship_names_map = {}

for ship_id, ship_data_src in ship_data_srcs.items():
    for skill_id in ship_data_src['buff_list_display'].values():
        if skill_id not in skill_to_ship_names_map:
            skill_to_ship_names_map[skill_id] = set()
        direct_name = ship_data_src['name']
        skill_to_ship_names_map[skill_id].add(direct_name)
        stats_name = ship_stats_srcs[ship_id]['name']
        skill_to_ship_names_map[skill_id].add(stats_name)
        
seen_weapon_sets = {}
for skill_id, skill_display_src in skill_display_srcs.items():
    #if skill_id < 100000: continue
    #if skill_id not in [29212]: continue
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
    ship_names = []
    rounded_skill_id = (skill_id // 10) * 10
    if skill_id in skill_to_ship_names_map:
        ship_names = skill_to_ship_names_map[skill_id]
    elif rounded_skill_id in skill_to_ship_names_map:
        ship_names = skill_to_ship_names_map[rounded_skill_id]
    
    weapon_set = tuple(weapon_ids)
    if weapon_set in seen_weapon_sets:
        print('ships', ship_names, ':', skill_display_src['name'], 'skill_id', skill_id, ': weapon_ids', weapon_ids, '-> skill_id', seen_weapon_sets[weapon_set])
        continue
    else:
        seen_weapon_sets[weapon_set] = skill_id
        print('ships', ship_names, ':', skill_display_src['name'], 'skill_id', skill_id, ': weapon_ids', weapon_ids)
    
    filename_out = 'skill_anim_out/barrage_skill_%d.webm' % skill_id
    animator = anim.Vp9Animator(fps = 60)
    if not os.path.exists(filename_out):
        try:
            barrage_anim.create_barrage_gif(filename_out, animator, weapon_ids, world_size, ppu,
                                           range_limit = range_limit, max_duration = max_duration, min_pad_duration = pad_duration)
        except:
            print(traceback.print_exc())
            #print(sys.exc_info(), traceback.print_exc())
    
