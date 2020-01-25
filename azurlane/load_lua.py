import lupa
from lupa import LuaRuntime
import os
import re
import copy

server = 'EN'
src_dir = '../AzurLaneScripts'
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

def load_sharecfg(table_name, key_type = int, apply_base = True):
    path = os.path.join(src_dir, server, 'sharecfg', table_name + '.lua')
    with open(path, encoding='utf-8') as f:
        lua.execute(f.read())
        g = lua.globals()

        base_result = convert_to_python_dict(g.pg[table_name], key_type)

        if apply_base:
            result = {}
            for k, v in base_result.items():
                if 'base' in v:
                    adjusted_v = copy.deepcopy(base_result[v['base']])
                    adjusted_v.update(v)
                    result[k] = adjusted_v
                else:
                    result[k] = v
            return result
        else:
            return base_result

def load_skill(skill_id):
    path = os.path.join(src_dir, server, 'gamecfg', 'skill', 'skill_%d.lua' % skill_id)
    with open(path, encoding='utf-8') as f:
        return convert_to_python_dict(lua.execute(f.read()))

def load_buff(buff_id):
    path = os.path.join(src_dir, server, 'gamecfg', 'buff', 'buff_%d.lua' % buff_id)
    with open(path, encoding='utf-8') as f:
        return convert_to_python_dict(lua.execute(f.read()))

def load_dungeon(dungeon_id):
    path = os.path.join(src_dir, server, 'gamecfg', 'dungeon', '%d.lua' % dungeon_id)
    with open(path, encoding='utf-8') as f:
        raw = f.read()
        processed = re.sub('Vector3\((.*?)\)', '{\g<1>}', raw)
        return convert_to_python_dict(lua.execute(processed))
