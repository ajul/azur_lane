import azurlane.load_lua
import common
import copy

bullet_srcs = azurlane.load_lua.load_sharecfg('bullet_template')
weapon_srcs = azurlane.load_lua.load_sharecfg('weapon_property')
equip_srcs = azurlane.load_lua.load_sharecfg('equip_data_statistics')

seen_strings = set()

for equip_id, equip_src in equip_srcs.items():
    if equip_src['type'] in [7, 8, 9]: continue
    if 'name' not in equip_src:
        print('equip', equip_id, 'missing name')
        continue
    equip_name = equip_src['name']
    equip_tech = equip_src['tech']
    if 'weapon_id' not in equip_src or len(equip_src['weapon_id']) == 0: continue
    weapon_id = equip_src['weapon_id'][1]
    weapon = weapon_srcs[weapon_id]
    print(equip_name, weapon['angle'])
    continue
    for bullet_id in weapon['bullet_ID'].values():
        if bullet_id not in bullet_srcs:
            #print(equip_name, 'missing bullet ID:', bullet_id)
            continue
        bullet = bullet_srcs[bullet_id]
        random_x = 0
        if 'randomOffsetX' in bullet['extra_param']:
            random_x = bullet['extra_param']['randomOffsetX']
        random_z = 0
        if 'randomOffsetZ' in bullet['extra_param']:
            random_z = bullet['extra_param']['randomOffsetZ']
        splash = 0
        if 'range' in bullet['hit_type']:
            splash = bullet['hit_type']['range']
        if random_x or random_z:
            s = '%s T%d: %d x %d -> %d' % (equip_name, equip_tech, random_x, random_z, splash)
            if s not in seen_strings:
                seen_strings.add(s)
                print(s)
