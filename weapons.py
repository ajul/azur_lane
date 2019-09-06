import lupa
from lupa import LuaRuntime
import os

src_dir = '../AzurLane_ClientSource/Src/EN'
bullet_path = os.path.join(src_dir, 'sharecfg/bullet_template.lua')
weapon_path = os.path.join(src_dir, 'sharecfg/weapon_property.lua')
equip_path = os.path.join(src_dir, 'sharecfg/equip_data_statistics.lua')

lua = LuaRuntime(unpack_returned_tuples=True)

def convert_to_python_dict(lua_table):
    result = {}
    for k, v in lua_table.items():
        try:
            pv = convert_to_python_dict(v)
        except AttributeError:
            pv = v
        result[k] = pv
    return result
         
with open(bullet_path, encoding='utf-8') as f:
    lua.execute(f.read())
    g = lua.globals()
    bullets = convert_to_python_dict(g.pg.bullet_template)

with open(weapon_path, encoding='utf-8') as f:
    lua.execute(f.read())
    g = lua.globals()
    weapons = convert_to_python_dict(g.pg.weapon_property)

with open(equip_path, encoding='utf-8') as f:
    lua.execute(f.read())
    g = lua.globals()
    equips = convert_to_python_dict(g.pg.equip_data_statistics)

for equip in equips.values():
    if 'name' in equip and 'BB' in equip['label'].values():
        print(equip['name'])
        weapon = weapons[equip['weapon_id'][1]]
        bullet = bullets[weapon['bullet_ID'][1]]
        print(bullet['velocity'])
        print(bullet['hit_type'])
        print(bullet['extra_param'])
        print()

