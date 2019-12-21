import lupa
from lupa import LuaRuntime
import os
import re

src_dir = '../AzurLaneScripts/EN'
lua = LuaRuntime(unpack_returned_tuples=True)

# If key_type is not None, top-level keys will be filtered to that type and sorted.
def convert_to_python_dict(lua_table, key_type = None):
    result = {}
    if key_type is None:
        keys = list(lua_table.keys())
    else:
        keys = sorted(k for k in lua_table.keys() if (key_type is None or isinstance(k, key_type)))
    for k in keys:
        v = lua_table[k]
        try:
            pv = convert_to_python_dict(v)
        except AttributeError:
            pv = v
        result[k] = pv
    return result

def load_sharecfg(table_name, key_type = None):
    path = os.path.join(src_dir, 'sharecfg', table_name + '.lua')
    with open(path, encoding='utf-8') as f:
        lua.execute(f.read())
        g = lua.globals()
        
        return convert_to_python_dict(g.pg[table_name], key_type)

def load_skill(skill_id):
    path = os.path.join(src_dir, 'gamecfg', 'skill', 'skill_%d.lua' % skill_id)
    with open(path, encoding='utf-8') as f:
        return convert_to_python_dict(lua.execute(f.read()))

def load_buff(buff_id):
    path = os.path.join(src_dir, 'gamecfg', 'buff', 'buff_%d.lua' % buff_id)
    with open(path, encoding='utf-8') as f:
        return convert_to_python_dict(lua.execute(f.read()))

def load_dungeon(dungeon_id):
    path = os.path.join(src_dir, 'gamecfg', 'dungeon', '%d.lua' % dungeon_id)
    with open(path, encoding='utf-8') as f:
        raw = f.read()
        processed = re.sub('Vector3\((.*?)\)', '{\g<1>}', raw)
        return convert_to_python_dict(lua.execute(processed))