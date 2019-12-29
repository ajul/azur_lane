import load_lua
import common

skill_data_srcs = load_lua.load_sharecfg('skill_data_template')
skill_display_srcs = load_lua.load_sharecfg('skill_data_display')
ship_data_srcs = load_lua.load_sharecfg('ship_data_template')
ship_stats_srcs = load_lua.load_sharecfg('ship_data_statistics')

# compute skill -> ship
skill_to_ship_names_map = {}

for ship_id, ship_data_src in ship_data_srcs.items():
    for skill_id in ship_data_src['buff_list_display'].values():
        if skill_id not in skill_to_ship_names_map:
            skill_to_ship_names_map[skill_id] = set()
        direct_name = ship_data_src['name']
        if direct_name:
            skill_to_ship_names_map[skill_id].add(direct_name)
        stats_name = ship_stats_srcs[ship_id]['name']
        if stats_name:
            skill_to_ship_names_map[skill_id].add(stats_name)

def get_last_effects(skill_id):
    try:
        skill_src = load_lua.load_skill(skill_id)
    except FileNotFoundError:
        return None
    last_index = 0
    while last_index + 1 in skill_src:
        last_index += 1
    if last_index == 0:
        return None
    last_level = skill_src[last_index]
    if 'effect_list' not in last_level:
        return None
    return last_level['effect_list']
