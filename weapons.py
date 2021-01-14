import azurlane.load_lua
import azurlane.weapon
import copy

bullet_srcs = azurlane.load_lua.load_sharecfg('bullet_template')
weapon_srcs = azurlane.load_lua.load_sharecfg('weapon_property')
equip_srcs = azurlane.load_lua.load_sharecfg('equip_data_statistics')

enhance_levels = {}
data = {}

for equip_id, equip_src in equip_srcs.items():
    if equip_src['type'] in [7, 8, 9]: continue
    if 'name' not in equip_src:
        print('equip', equip_id, 'missing name')
        continue
    equip_name = equip_src['name']
    equip_tech = equip_src['tech']
    
    if 'base' not in equip_src:
        enhance_levels[equip_id] = 0
        level = 0
    else:
        enhance_levels[equip_src['base']] += 1
        level = enhance_levels[equip_src['base']]
    if level not in [10, 13]: continue
    equip_name += ' +%d' % level

    if 'weapon_id' not in equip_src or len(equip_src['weapon_id']) == 0: continue
    weapon_id = equip_src['weapon_id'][1]
    try:
        weapon_stats = azurlane.weapon.WeaponStats(weapon_id)
        data[equip_name] = weapon_stats
    except Exception as e:
        pass

for k, v in data.items():
    print(k, v.damage, v.shells, v.salvos, v.rof, v.dps())

    
