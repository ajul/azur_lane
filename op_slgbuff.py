from azurlane import load_lua

buff_srcs = load_lua.load_sharecfg('world_SLGbuff_data', key_type=int)

result = ''

for buff_id, buff_data in buff_srcs.items():
    result += '|-\n'
    result += '| %s || %s\n' % (buff_data['name'], buff_data['desc'])

print(result)
