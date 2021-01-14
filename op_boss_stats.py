from azurlane import load_lua

expedition_data_srcs = load_lua.load_sharecfg('expedition_data_template')
enemy_data_srcs = load_lua.load_sharecfg('enemy_data_statistics')

op_boss_level = 128
growth_mult = (op_boss_level - 1) / 1000.0

def get_stat(boss, stat):
    return int(round(boss[stat] + boss[stat + '_growth'] * growth_mult))

filter_strings = [
    "Defense Module",
    "Arbiter",
    ]

for expedition_data in expedition_data_srcs.values():
    if not any((s in expedition_data['name']) for s in filter_strings): continue
    dungeon_id = expedition_data['dungeon_id']
    dungeon_data = load_lua.load_dungeon(dungeon_id)
    waves = dungeon_data['stages'][1]['waves']
    for wave in waves.values():
        for spawn in wave.get('spawn', {}).values():
            if 'bossData' in spawn:
                boss_id = spawn['monsterTemplateID']
                if boss_id not in enemy_data_srcs:
                    print('Missing boss id', boss_id, 'for', expedition_data['name'])
                    continue
                boss = enemy_data_srcs[boss_id]
                s = '%s (%d)' % (expedition_data['name'], boss_id)
                for stat in ('hit', 'dodge', 'luck', 'antiaircraft'):
                    s += ' %s: %d' % (stat, get_stat(boss, stat))
                print(s)
