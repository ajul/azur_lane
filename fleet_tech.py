import load_lua

fleet_tech_ship_src = load_lua.load_sharecfg('fleet_tech_ship_template', key_type=int)
ship_data_src = load_lua.load_sharecfg('ship_data_statistics', key_type=int)

attributes = {
    1 : 'Health',
    2 : 'Firepower',
    3 : 'Torpedo',
    4 : 'AA',
    5 : 'Aviation',
    6 : 'Reload',
    8 : 'Accuracy',
    9 : 'Evasion',
    12 : 'ASW',
}

ship_types = {
    1 : 'DD',
    2 : 'CL',
    3 : 'CA',
    4 : 'BC',
    5 : 'BB',
    6 : 'CVL',
    7 : 'CV',
    8 : 'SS',
    10 : 'BBV',
    12 : 'AR',
    13 : 'BM',
}

ship_type_groups = [
    ['DD'],
    ['CL'],
    ['CA', 'BM', 'CB'],
    ['BC', 'BB', 'BBV'],
    ['CV', 'CVL'],
    ['AR'],
    ['SS', 'SSV'],
]

nationalities = {
    1 : 'Eagle Union',
    2 : 'Royal Navy',
    3 : 'Sakura Empire',
    4 : 'Ironblood',
    5 : 'Eastern Radiance',
    6 : 'Sardegna Empire',
    7 : 'North Union',
    8 : 'Iris Libre',
    9 : 'Vichya Dominion',
}

class Ship():
    def __init__(self, fleet_tech_ship):
        self.points_collect = fleet_tech_ship['pt_get']
        self.points_lb = fleet_tech_ship['pt_upgrage']
        self.points_120 = fleet_tech_ship['pt_level']

        self.bonus_type_collect = attributes[fleet_tech_ship['add_get_attr']]
        self.bonus_amount_collect = fleet_tech_ship['add_get_value']
        self.bonus_type_120 = attributes[fleet_tech_ship['add_level_attr']]
        self.bonus_amount_120 = fleet_tech_ship['add_level_value']

        ship_data = ship_data_src[fleet_tech_ship['id'] * 10 + 1]
        self.name = ship_data['name']
        self.ship_type = ship_types[ship_data['type']]
        self.nationality = nationalities[ship_data['nationality']]

ships = []

for fleet_tech_ship_id, fleet_tech_ship in fleet_tech_ship_src.items():
    try:
        ships.append(Ship(fleet_tech_ship))
    except:
        print('Missing data for', fleet_tech_ship['id'])

for nationality in nationalities.values():
    total = 0
    for ship in ships:
        if ship.nationality == nationality:
            total += ship.points_collect + ship.points_lb + ship.points_120
    print(nationality, total)
