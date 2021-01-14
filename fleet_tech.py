from azurlane import common, load_lua

fleet_tech_ship_src = load_lua.load_sharecfg('fleet_tech_ship_template', key_type=int)
ship_data_src = load_lua.load_sharecfg('ship_data_statistics', key_type=int)

ship_type_groups = [
    ['DD'],
    ['CL'],
    ['CA', 'BM', 'CB'],
    ['BB', 'BC', 'BBV'],
    ['CV', 'CVL'],
    ['AR'],
    ['AE'],
    ['SS', 'SSV'],
]

ship_type_group_map = {}

for ship_type_group in ship_type_groups:
    for ship_type in ship_type_group:
        ship_type_group_map[ship_type] = ship_type_group[0]

class Ship():
    def __init__(self, fleet_tech_ship, ship_data):
        self.points_collect = fleet_tech_ship['pt_get']
        self.points_lb = fleet_tech_ship['pt_upgrage']
        self.points_120 = fleet_tech_ship['pt_level']

        self.bonus_type_collect = common.attributes[fleet_tech_ship['add_get_attr']]
        self.bonus_amount_collect = fleet_tech_ship['add_get_value']
        self.bonus_type_120 = common.attributes[fleet_tech_ship['add_level_attr']]
        self.bonus_amount_120 = fleet_tech_ship['add_level_value']

        self.name = ship_data['name']
        self.ship_type = common.ship_types[ship_data['type']]
        self.ship_type_group = ship_type_group_map[self.ship_type]
        self.nationality = common.nationalities[ship_data['nationality']]

ships = []

for fleet_tech_ship_id, fleet_tech_ship in fleet_tech_ship_src.items():
    ship_data_id = fleet_tech_ship['id'] * 10 + 1
    if ship_data_id in ship_data_src:
        ship_data = ship_data_src[ship_data_id]
        ships.append(Ship(fleet_tech_ship, ship_data))
    else:
        print('Missing ship_data_id', ship_data_id)

stat_values = {
    'DD' : {
        'Firepower' : 11,
        'Torpedo' : 15,
        'Reload' : 18,
        'Accuracy' : 19,
        'Evasion' : 28,
        'Health' : 5,
        'AA' : 10,
        'ASW' : 5,
    },
    'CL' : {
        'Firepower' : 18,
        'Torpedo' : 13,
        'Reload' : 20,
        'Accuracy' : 29,
        'Evasion' : 42,
        'Health' : 3,
        'AA' : 7,
        'ASW' : 5,
    },
    'CA' : {
        'Firepower' : 18,
        'Torpedo' : 13,
        'Reload' : 20,
        'Accuracy' : 43,
        'Evasion' : 52,
        'Health' : 2.5,
        'AA' : 9,
    },
    'BB' : {
        'Firepower' : 20,
        'Reload' : 22,
        'Accuracy' : 50,
        'Evasion' : 15,  # ?
        'Health' : 1.5,
        'AA' : 9,
    },
    'CV' : {
        'Aviation' : 16,
        'Reload' : 24,
        'Accuracy' : 100,
        'Health' : 2,
        'AA' : 7.5,
        'ASW' : 5,
    },
    'AE' : {
        'Firepower' : 18,
        'Torpedo' : 13,
        'Reload' : 20,
        'Accuracy' : 29,
        'Evasion' : 42,
        'Health' : 3,
        'AA' : 7,
        'ASW' : 5,
    },
}

faction_technology = {
    'Ironblood' : (
        ('DD', 'Health', 10),
        ('DD', 'Firepower', 4),
        ('CL', 'Health', 10),
        ('CL', 'Firepower', 1),
        ('CA', 'Health', 5),
        ('CA', 'Firepower', 1),
        ('BB', 'Health', 20),
    ),
    'Sakura Empire' : (
        ('DD', 'Torpedo', 7),
        ('CL', 'Torpedo', 13),
        ('CA', 'Torpedo', 13),
        ('BB', 'Firepower', 10),
        ('CV', 'Aviation', 7),
    ),
    'Royal Navy' : (
        ('DD', 'Evasion', 7),
        ('CL', 'Firepower', 7),
        ('CA', 'Firepower', 7),
        ('BB', 'Firepower', 4),
        ('CV', 'Aviation', 5),
        ('CV', 'Reload', 7),
    ),
    'Eagle Union' : (
        ('DD', 'AA', 10),
        ('DD', 'Reload', 7),
        ('CL', 'Firepower', 7),
        ('CL', 'Reload', 7),
        ('CA', 'Firepower', 7),
        ('CA', 'Reload', 7),
        ('BB', 'AA', 10),
        ('BB', 'Accuracy', 10),
        ('CV', 'Aviation', 7),
        ('CV', 'Reload', 7),
    ),
}

"""
for nationality, bonuses in faction_technology.items():
    total = 0
    for ship_type_group, stat, amount in bonuses:
        total += amount * stat_values[ship_type_group][stat]
    print(nationality, total)
"""

faction_point_values = {
    'Ironblood' : 0.16,
    'Sakura Empire' : 0.28,
    'Royal Navy' : 0.32,
    'Eagle Union' : 0.6,
}

"""
for nationality in common.nationalities.values():
    total = 0
    for ship in ships:
        if ship.nationality == nationality:
            total += ship.points_collect + ship.points_lb + ship.points_120
    print(nationality, total)
"""

rows = []

for ship in ships:
    if ship.ship_type_group in ['AR', 'SS']: continue
    value = stat_values[ship.ship_type_group][ship.bonus_type_120] * ship.bonus_amount_120
    if ship.nationality in faction_point_values:
        value += faction_point_values[ship.nationality] * ship.points_120

    bonus_string = '+%d %s' % (ship.bonus_amount_120, ship.bonus_type_120)

    rows.append([ship.name, ship.ship_type_group, ship.nationality, value, bonus_string])

import csv

with open('ship_tech_values.csv', 'w', newline='') as outfile:
    writer = csv.writer(outfile)
    writer.writerow(['Name', 'Group', 'Nationality', 'Value', 'Lv 120 Bonus'])
    for row in rows:
        writer.writerow(row)
