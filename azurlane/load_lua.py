import lupa
from lupa import LuaRuntime
import os
import re
import copy

default_server = 'en-US'
src_dir = '../AzurLaneData'
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

def load_file(path):
    with open(path, encoding='utf-8') as f:
        s = f.read()
        s = re.sub('Vector3\((.*?)\)', '{\g<1>}', s)
        s = re.sub('AspectMode\.[A-Za-z]+', '"\g<0>"', s)
        return convert_to_python_dict(lua.execute(s))

def load_sharecfg(table_name, key_type = int, apply_base = True, server = None):
    if server is None: server = default_server
    path = os.path.join(src_dir, server, 'sharecfg', table_name.lower() + '.lua')
    with open(path, encoding='utf-8') as f:
        lua_input = f.read()
        # something went strange with the decompile here
        if table_name in ['weapon_property', 'expedition_data_template']:
            lua_input = re.sub('function \\(\\)', '', lua_input)
            lua_input = re.sub('end\\(\\)', '', lua_input)
            lua_input = re.sub('uv0', 'pg', lua_input)
        lua.execute(lua_input)
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

def load_skill(skill_id, server = None):
    if server is None: server = default_server
    path = os.path.join(src_dir, server, 'gamecfg', 'skill', 'skill_%d.lua' % skill_id)
    return load_file(path)

def load_buff(buff_id, server = None):
    if server is None: server = default_server
    path = os.path.join(src_dir, server, 'gamecfg', 'buff', 'buff_%d.lua' % buff_id)
    return load_file(path)

def load_dungeon(dungeon_id, server = None):
    if server is None: server = default_server
    path = os.path.join(src_dir, server, 'gamecfg', 'dungeon', '%d.lua' % dungeon_id)
    return load_file(path)

def load_stories(story_prefix, server = None):
    if server is None: server = default_server
    story_dir = os.path.join(src_dir, server, 'gamecfg', 'story')
    for filename in os.listdir(story_dir):
        if filename.find(story_prefix) == 0:
            path = os.path.join(story_dir, filename)
            suffix = filename[len(story_prefix):-len('.lua')]
            yield suffix, load_file(path)

def skill_iter(server = None):
    if server is None: server = default_server
    skill_dir = os.path.join(src_dir, server, 'gamecfg', 'skill')
    for filename in os.listdir(skill_dir):
        path = os.path.join(skill_dir, filename)
        try:
            yield load_file(path)
        except:
            print('Failed to load', filename)

def dungeon_iter(server = None):
    if server is None: server = default_server
    dungeon_dir = os.path.join(src_dir, server, 'gamecfg', 'dungeon')
    for filename in os.listdir(dungeon_dir):
        path = os.path.join(dungeon_dir, filename)
        yield load_file(path)