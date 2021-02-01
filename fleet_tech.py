import azurlane.common
import azurlane.ship

goal = 'level'

ship_type_groups = [
    ('DD',),
    ('CL',),
    ('CA', 'BM', 'CB'),
    ('BC', 'BB', 'BBV'),
    ('CVL', 'CV'),
    ('AR',),
    ('AE',),
    ('SS', 'SSV'),
]

# ship_type_group -> (benefit_ship_types, value, shiptypes) -> nationality_id -> ship names
data = [{} for x in ship_type_groups]

for ship_group in azurlane.ship.ship_group_iter():
    if ship_group.fleet_tech_src is None: continue

    attribute_key = 'add_' + goal + '_attr'
    amount_key = 'add_' + goal + '_value'
    shiptype_key = 'add_' + goal + '_shiptype'
    attribute_id = ship_group.fleet_tech_src[attribute_key]
    amount = ship_group.fleet_tech_src[amount_key]
    benefit_ship_types = tuple(azurlane.common.ship_types[x] for x in ship_group.fleet_tech_src[shiptype_key].values())

    for ship_type_group_id, ship_types in enumerate(ship_type_groups):
        if ship_group.ship_type in ship_types: break

    ship_type_group_data = data[ship_type_group_id]
    if len(benefit_ship_types) == len(ship_types):
        benefit_ship_types = ()
    key = (attribute_id, benefit_ship_types, amount)
    if key not in ship_type_group_data: ship_type_group_data[key] = [[] for x in range(5)]
    nationality_index = ship_group.src['nationality']
    if nationality_index > 4: nationality_index = 0
    ship_type_group_data[key][nationality_index].append(ship_group.name)

tabs = []

for ship_type_group_id, ship_types in enumerate(ship_type_groups):
    tab = '/'.join(ship_types) + '=\n'
    tab += '{|class = "azltable"\n'
    tab += '! style="min-width:75px;" | Bonus\n'
    tab += '! style="width:100%;" | Ships\n'
    ship_type_group_data = data[ship_type_group_id]
    for key in sorted(ship_type_group_data.keys()):
        attribute_id, benefit_ship_types, amount = key
        
        tab += '|-\n'
        tab += '| +%d {{%s}}' % (amount, azurlane.common.attributes[attribute_id])
        if benefit_ship_types: tab += '<br/>(' + '/'.join(benefit_ship_types) + ' only)'
        tab += ' || '

        ship_lines = []

        ship_lists = ship_type_group_data[key]
        for nationality_index, nationality in [(1, 'Eagle Union'),
                                               (2, 'Royal Navy'),
                                               (3, 'Sakura Empire'),
                                               (4, 'Iron Blood'),
                                               (0, 'Other')]:
            ship_list = azurlane.ship.sorted_ship_name_list(ship_lists[nationality_index])
            if ship_list:
                ship_lines.append("'''%s:''' " % nationality + ', '.join('[[%s]]' % name for name in ship_list))

        tab += '<br/>'.join(ship_lines) + '\n'
    tab += '|}\n'
    tabs.append(tab)

result = '<tabber>\n' + '|-|\n'.join(tabs) + '</tabber>\n'
print(result)
            
