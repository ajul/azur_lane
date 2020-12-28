from azurlane import load_lua

expedition_data_srcs = load_lua.load_sharecfg('expedition_data_template')
enemy_data_srcs = load_lua.load_sharecfg('enemy_data_statistics')

op_boss_level = 128
growth_mult = (op_boss_level - 1) / 1000.0

for expedition_data in expedition_data_srcs.values():
    if "Defense Module" not in expedition_data['name']: continue
    dungeon_id = expedition_data['dungeon_id']
    dungeon_data = load_lua.load_dungeon(dungeon_id)
    waves = dungeon_data['stages'][1]['waves']
    for wave in waves.values():
        for spawn in wave.get('spawn', {}).values():
            if 'bossData' in spawn:
                boss_id = spawn['monsterTemplateID']
                boss = enemy_data_srcs[boss_id]
                hit = int(round(boss['hit'] + boss['hit_growth'] * growth_mult))
                dodge = int(round(boss['dodge'] + boss['dodge_growth'] * growth_mult))
                print(expedition_data['name'], boss_id, hit, dodge)
