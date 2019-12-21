import load_lua
import common
import copy
import re

chapter_srcs = load_lua.load_sharecfg('chapter_template')
expedition_data_srcs = load_lua.load_sharecfg('expedition_data_template')
enemy_data_srcs = load_lua.load_sharecfg('enemy_data_statistics')
aircraft_srcs = load_lua.load_sharecfg('aircraft_template')

# chapter -> primary -> [secondaries]
datas = {}
air_datas = {}

def process_spawn(chapter, expedition, dungeon, spawn):
    enemy_id = spawn['monsterTemplateID']
    
    enemy = enemy_data_srcs[enemy_id]
    if 'base' in enemy:
        base = copy.deepcopy(enemy_data_srcs[enemy['base']])
        base.update(enemy)
        enemy = base

    is_hard_mode = chapter['type'] > 1
    level = expedition['level']
    boss_stage = ''
    stage_name = chapter['chapter_name'].replace('–', '-')
    if 'bossData' in spawn:
        boss_stage = stage_name

    m = re.search('(.*?)-?(\d*)$', stage_name)
    display_chapter = m.group(1)
    stage = m.group(2)

    chapter_key = (is_hard_mode, display_chapter)
    primary_key = (boss_stage, enemy['icon_type'] > 0, enemy['name'], enemy_id)

    enemy_data = {
        'level' : level,
        'stage_name' : stage_name,
        'name' : enemy['name'],
        'icon_type' : enemy['icon_type'],
        'is_boss' : 'bossData' in spawn,
    }
    for stat in ['type', 'armor_type']:
        enemy_data[stat] = enemy[stat]
    for stat in ['durability', 'dodge', 'hit', 'luck', 'speed']:
        enemy_data[stat] = int(round(enemy[stat] + (level - 1) * enemy[stat + '_growth'] / 1000.0))

    if chapter_key not in datas:
        datas[chapter_key] = {}

    if primary_key not in datas[chapter_key]:
        datas[chapter_key][primary_key] = []

    datas[chapter_key][primary_key].append(enemy_data)

def process_air(chapter, expedition, dungeon, air):
    aircraft_id = air['templateID']
    aircraft = aircraft_srcs[aircraft_id]

    level = expedition['level']
    is_hard_mode = chapter['type'] > 1
    stage_name = chapter['chapter_name'].replace('–', '-')
    m = re.search('(.*?)-?(\d*)$', stage_name)
    display_chapter = m.group(1)
    chapter_key = (is_hard_mode, display_chapter)
    primary_key = (aircraft['type'], aircraft_id,)

    aircraft_data = {
        'level' : level,
        'stage_name' : stage_name,
        'hp' : int(round(aircraft['max_hp'] + (level - 1) * aircraft['hp_growth'] / 1000.0)),
        'hit' : int(round(aircraft['accuracy'] + (level - 1) * aircraft['ACC_growth'] / 1000.0)),
        'power' : int(round(aircraft['attack_power'] + (level - 1) * aircraft['AP_growth'] / 1000.0)),
    }

    for stat in ['type', 'crash_DMG', 'speed']:
        aircraft_data[stat] = aircraft[stat]

    aircraft_data['net_crash'] = aircraft_data['crash_DMG'] * (1.0 + aircraft_data['power'] / 100.0)

    if chapter_key not in air_datas:
        air_datas[chapter_key] = {}

    if primary_key not in air_datas[chapter_key]:
        air_datas[chapter_key][primary_key] = []

    air_datas[chapter_key][primary_key].append(aircraft_data)

for chapter_id, chapter in chapter_srcs.items():
    if chapter_id == 'all': continue
    # filter to main story
    m = re.match('\d+–\d', chapter['chapter_name'])
    if not m: continue

    expedition_ids = set()
    dungeon_ids = set()
    for t in chapter['expedition_id_weight_list'].values():
        expedition_id = t[1]
        expedition_ids.add(expedition_id)
    for key in ['ambush_expedition_list',
                'guarder_expedition_list',
                'elite_expedition_list',
                'ai_expedition_list',
                'patrolai_expedition_list',
                'submarine_expedition_list',
                'boss_expedition_id']:
        for expedition_id in chapter[key].values():
            if expedition_id > 1:
                expedition_ids.add(expedition_id)

    for expedition_id in expedition_ids:
        expedition = expedition_data_srcs[expedition_id]
        dungeon_id = expedition['dungeon_id']
        dungeon = load_lua.load_dungeon(dungeon_id)
        for stage in dungeon['stages'].values():
            for wave in stage['waves'].values():
                if 'spawn' in wave:
                    for spawn_id, spawn in wave['spawn'].items():
                        if not isinstance(spawn_id, int):
                            print('Malformed spawn in dungeon', dungeon_id)
                            continue
                        process_spawn(chapter, expedition, dungeon, spawn)
                if 'reinforcement' in wave:
                    for spawn in wave['reinforcement'].values():
                        process_spawn(chapter, expedition, dungeon, spawn)
                if 'airFighter' in wave:
                    for air in wave['airFighter'].values():
                        process_air(chapter, expedition, dungeon, air)

def range_string(enemy_datas, key):
    min_value = min(enemy_data[key] for enemy_data in enemy_datas)
    max_value = max(enemy_data[key] for enemy_data in enemy_datas)
    if min_value == max_value:
        return '%d' % min_value
    else:
        return 'data-sort-value="%d" | %d - %d' % (max_value, min_value, max_value)

for chapter_key in sorted(datas):
    chapter_name = chapter_key[1]
    if chapter_key[0]:
        chapter_name = chapter_name + ' (Hard)'
    chapter_datas = datas[chapter_key]
    result = '{|class = "wikitable sortable" style="text-align: center;"\n'
    result += '! Name !! Level !! Type !! Armor !! HP !! Acc !! Eva !! Speed !! Lck\n'
    for primary_key in sorted(chapter_datas):
        enemy_datas = chapter_datas[primary_key]
        if enemy_datas[0]['is_boss']:
            enemy_name = 'data-sort-value="~~%s %s" style="text-align: left;" | %s (%s boss)' % (
                enemy_datas[0]['stage_name'], enemy_datas[0]['name'], enemy_datas[0]['name'], enemy_datas[0]['stage_name'])
        elif enemy_datas[0]['icon_type'] > 0:
            enemy_name = 'data-sort-value="~%s" style="text-align: left;" | %s' % (enemy_datas[0]['name'], enemy_datas[0]['name'])
        else:
            enemy_name = 'style="text-align: left;" | %s' % enemy_datas[0]['name']
        
        row_data = [
            enemy_name,
            range_string(enemy_datas, 'level'),
            common.ship_types[enemy_datas[0]['type']],
            common.armor_types[enemy_datas[0]['armor_type']],
            ]
        for stat in ['durability', 'hit', 'dodge', 'speed', 'luck']:
            row_data.append(range_string(enemy_datas, stat))
        result += '|-\n| ' + ' || '.join(row_data) + '\n'
    result += '|}\n'
    with open('enemy_stats_out/Chapter %s.txt' % chapter_name, 'w') as outfile:
        outfile.write(result)

for chapter_key in sorted(air_datas):
    chapter_name = chapter_key[1]
    if chapter_key[0]:
        chapter_name = chapter_name + ' (Hard)'
    chapter_datas = air_datas[chapter_key]
    result = '{|class = "wikitable sortable" style="text-align: center;"\n'
    result += '! Type !! Level !! HP !! Crash !! Acc !! Speed\n'
    for primary_key in sorted(chapter_datas):
        air_data = chapter_datas[primary_key]
        row_data = [
            common.aircraft_types[air_data[0]['type']],
            range_string(air_data, 'level'),
            range_string(air_data, 'hp'),
            range_string(air_data, 'net_crash'),
            range_string(air_data, 'hit'),
            range_string(air_data, 'speed'),
        ]
        result += '|-\n| ' + ' || '.join(row_data) + '\n'
    result += '|}\n'
    with open('enemy_stats_out/Chapter %s air.txt' % chapter_name, 'w') as outfile:
        outfile.write(result)
