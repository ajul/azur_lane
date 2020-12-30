from azurlane import load_lua

equip_data_srcs = load_lua.load_sharecfg('equip_data_statistics')
item_data_srcs = load_lua.load_sharecfg('item_data_statistics')
upgrade_srcs = load_lua.load_sharecfg('equip_upgrade_data')

result = '{| class = "wikitable sortable"\n'
result += '! Output !! Upgrade from !! Coins !! Materials\n'

for upgrade_data in upgrade_srcs.values():
    output_id = upgrade_data['target_id']
    output = equip_data_srcs[output_id]
    output_name = output['name']
    source_id = upgrade_data['upgrade_from']
    source = equip_data_srcs[source_id]
    source_name = source['name']
    coins = upgrade_data['coin_consume']

    result += '|-\n'
    result += '| %s || %s || %d \n' % (output_name, source_name, coins)
    result += '| \n'
    for material_data in upgrade_data['material_consume'].values():
        material_id = material_data[1]
        material_name = item_data_srcs[material_id]['name']
        quantity = material_data[2]
        result += '* %s × %d\n' % (material_name, quantity)

result += '|}'

with open('crafting.txt', 'w', encoding='utf-8') as out_file:
    out_file.write(result)
