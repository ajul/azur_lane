import lupa
from lupa import LuaRuntime
import os

src_dir = '../AzurLaneSource/EN'
expedition_path = os.path.join(src_dir, 'sharecfg/expedition_data_template.lua')

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
         
with open(expedition_path, encoding='utf-8') as f:
    lua.execute(f.read())
    g = lua.globals()
    expeditions = convert_to_python_dict(g.pg.expedition_data_template)

for id in sorted(id for id in expeditions.keys() if isinstance(id, int)):
    expedition = expeditions[id]
    if 'exp_commander' not in expedition: continue
    base = expedition['exp_commander']
    ratio = expedition['exp_commander_ratio']
    if expedition['id'] < 101000: continue
    #if expedition['id'] % 1000 != 0: continue
    if 'Flagship' in expedition['name']:
        print(expedition['name'], expedition['id'])
        print(base, ratio)
        print()
