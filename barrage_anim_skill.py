from azurlane import anim, barrage, load_lua
import os
import sys
import traceback

load_lua.server = 'en-US'

skill_data_srcs = load_lua.load_sharecfg('skill_data_template', key_type=int)
skill_display_srcs = load_lua.load_sharecfg('skill_data_display', key_type=int)
ship_data_srcs = load_lua.load_sharecfg('ship_data_template', key_type=int)
ship_stats_srcs = load_lua.load_sharecfg('ship_data_statistics', key_type=int)

world_size = (75, 50)
# pixels per in-game unit
ppu = 10

# compute skill -> ship
skill_to_ship_names_map = {}

color_count_override = {
    12800 : 128,
    12810 : 64,
}

def redo_condition(skill_src, weapon_ids):
    #if skill_src['id'] == 13020: return True
    return False

for ship_id, ship_data_src in ship_data_srcs.items():
    if not ship_data_src['buff_list_display']: continue
    for skill_id in ship_data_src['buff_list_display'].values():
        if skill_id not in skill_to_ship_names_map:
            skill_to_ship_names_map[skill_id] = set()
        if 'name' in ship_data_src:
            direct_name = ship_data_src['name']
            skill_to_ship_names_map[skill_id].add(direct_name)
        stats_name = ship_stats_srcs[ship_id]['name']
        skill_to_ship_names_map[skill_id].add(stats_name)
        
seen_weapon_sets = {}
skill_to_ship_names_map[40000] = set(["Bunny (Meowfficer)"])
skill_to_ship_names_map[40001] = set(["Bunny (Meowfficer)"])
skill_display_srcs[40000] = {
    'name' : 'Bite Their Fingers I',
    'id' : 40000,
}
skill_display_srcs[40001] = {
    'name' : 'Bite Their Fingers II',
    'id' : 40001,
}

def find_names(skill_id):
    rounded_skill_id = (skill_id // 10) * 10
    candidate_skill_ids = [x for x in range(skill_id, rounded_skill_id-1, -1)]
    name = None
    for candidate_skill_id in candidate_skill_ids:
        if candidate_skill_id in skill_display_srcs:
            name = skill_display_srcs[candidate_skill_id]['name']
            break
        elif candidate_skill_id in skill_data_srcs:
            name = skill_data_srcs[candidate_skill_id]['name']
            break
    ships = None
    for candidate_skill_id in candidate_skill_ids:
        if candidate_skill_id in skill_to_ship_names_map:
            ships = skill_to_ship_names_map[candidate_skill_id]
            break
    return name, ships

for skill_src in load_lua.skill_iter():
    skill_id = skill_src['id']
    #if skill_id < 100000: continue
    #if skill_id not in [13440]: continue

    last_index = 0
    while last_index + 1 in skill_src:
        last_index += 1
    if last_index == 0:
        last_level = skill_src
    else:
        last_level = skill_src[last_index]
    if 'effect_list' not in last_level: continue
    last_effects = last_level['effect_list']

    weapon_ids = []
    for idx, effect in last_effects.items():
        if effect['type'] != 'BattleSkillFire': continue
        weapon_id = effect['arg_list']['weapon_id']
        if 'delay' in effect['arg_list']:
            weapon_id = (weapon_id, effect['arg_list']['delay'])
        weapon_ids.append(weapon_id)
            
    if len(weapon_ids) == 0: continue
    name, ships = find_names(skill_id)
    if not name and not ships:
        print('No skill name or ship found for skill ID', skill_id)
        continue

    if not name:
        name = '(unknown skill name)'
    
    weapon_set = tuple(weapon_ids)
    if weapon_set in seen_weapon_sets:
        print('ships', ships, ':', name, 'skill_id', skill_id, ': weapon_ids', weapon_ids, '-> skill_id', seen_weapon_sets[weapon_set])
        continue
    else:
        seen_weapon_sets[weapon_set] = skill_id
        print('ships', ships, ':', name, 'skill_id', skill_id, ': weapon_ids', weapon_ids)
    
    filename_out = 'skill_anim_out/bullet_pattern_skill_%d.gif' % skill_id
    
    color_count = 32
    if skill_id in color_count_override:
        color_count = color_count_override[skill_id]
    animator = anim.GifAnimator(color_count=color_count)
    #animator = anim.Img2WebPAnimator()
    
    if not os.path.exists(filename_out) or redo_condition(skill_src, weapon_ids):
        try:
            barrage.create_barrage_anim(animator, weapon_ids, world_size)
        except Exception as e:
            print('Error:', e)
            #print(traceback.print_exc())
            #print(sys.exc_info(), traceback.print_exc())
        animator.write_animation(filename_out)
    

