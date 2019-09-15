import lupa
from lupa import LuaRuntime
import os

src_dir = '../AzurLaneSource/EN'
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

def load_sharecfg(table_name):
    path = os.path.join(src_dir, 'sharecfg', table_name + '.lua')
    with open(path, encoding='utf-8') as f:
        lua.execute(f.read())
        g = lua.globals()
        return convert_to_python_dict(g.pg[table_name])
