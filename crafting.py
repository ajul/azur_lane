from azurlane import load_lua
from equipment_page_map import equipment_page_map
import urllib.parse

equip_data_srcs = load_lua.load_sharecfg('equip_data_statistics')
item_data_srcs = load_lua.load_sharecfg('item_data_statistics')
upgrade_srcs = load_lua.load_sharecfg('equip_upgrade_data')

def get_links(equipment_id):
    if equipment_id in equipment_page_map:
        tab = equipment_page_map[equipment_id]
    else:
        tab = equip_data_srcs[equipment_id]['name']
        print('Missing page for equipment id', equipment_id, tab)
    return tab.split('#')[0], tab

def quote_link(link):
    return link.replace('"', '&quot;')

seen_outputs = set()
items_using_material = {}

result = '{| class = "wikitable sortable"\n'
result += '! rowspan = "2" | Upgrade from !! colspan = "3" | Materials !! rowspan = "2" | {{Coin}} !! rowspan = "2" | Upgrade to\n'
result += '|-\n'
result += '! 1 !! 2 !! 3 \n'

for upgrade_data in upgrade_srcs.values():
    output_id = upgrade_data['target_id']
    output = equip_data_srcs[output_id]
    source_id = upgrade_data['upgrade_from']
    source = equip_data_srcs[source_id]
    coins = upgrade_data['coin_consume']

    source_page, source_tab = get_links(source_id)
    output_page, output_tab = get_links(output_id)

    result += '|-\n'
    result += '| {{EquipmentBox|%d|%s|%s|%s|No|64}} \n' % (source['rarity'], source_page, source_tab, source['icon'])
    
    for material_data in upgrade_data['material_consume'].values():
        material_id = material_data[1]
        material = item_data_srcs[material_id]
        quantity = material_data[2]
        result += '| {{EquipmentBox|%d|%s|#%s|%s|No|64|%d}}\n' % (material['rarity']+1, material['name'], material['name'], material['name'], quantity)

        material_key = (material['rarity'], material_id)
        
        if material_key not in items_using_material:
            items_using_material[material_key] = []
        items_using_material[material_key].append((output['name'], quantity, output_id))
    result += '| %d \n' % (coins)
    result += '| {{EquipmentBox|%d|%s|%s|%s|No|64}} %s' % (output['rarity'], output_page, output_tab, output['icon'], output_page)

    if output_id not in seen_outputs:
        result += ' {{anchor|%s}} ' % quote_link(output_page)
        seen_outputs.add(output_id)
    result += '\n'

result += '|}\n'

with open('crafting.txt', 'w', encoding='utf-8') as out_file:
    out_file.write(result)

result = '{| class = "wikitable sortable"\n'
result += '! Material !! Used for \n'

for material_rarity, material_id in sorted(items_using_material):
    material = item_data_srcs[material_id]
    result += '|-\n'
    result += '| style="vertical-align:top" | {{anchor|%s}} {{EquipmentBox|%d|%s|#%s|%s|No|64}}\n' % (material['name'], material_rarity+1, material['name'], material['name'], material['name'])
    result += '| \n'
    for output_name, quantity, output_id in items_using_material[(material_rarity, material_id)]:
        output = equip_data_srcs[output_id]
        output_page, output_tab = get_links(output_id)
        result += '{{EquipmentBox|%d|%s|#%s|%s|No|64|%d}}\n' % (output['rarity'], output_page, output_page, output['icon'], quantity)

result += '|}\n'

with open('crafting_inverse.txt', 'w', encoding='utf-8') as out_file:
    out_file.write(result)
