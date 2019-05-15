import csv
import re

bonus_index = -1

hull_symbols = {
    'Destroyer' : 'DD',
    'Light Cruiser' : 'CL',
    'Heavy Cruiser' : 'CA',
    'Monitor' : 'BM',
    'Super Cruiser' : 'CB',
    
    'Battlecruiser' : 'BC',
    'Battleship' : 'BB',
    'Aviation Battleship' : 'BBV',
    
    'Aircraft Carrier' : 'CV',
    'Light Aircraft Carrier' : 'CVL',

    'Repair Ship' : 'AR',
    
    'Submarine' : 'SS',
    'Submarine Carrier' : 'SSV',
}

hull_symbol_indices = {hull : i for i, hull in enumerate(hull_symbols.values())}

bonus_indices = [
    'Health',
    'Firepower',
    'AA',
    'ASW',
    'Torpedo',
    'Airpower',
    'Reload',
    'Accuracy',
    'Evasion',
]

def hull_symbols_tuple(hulls):
    return tuple(sorted(hull_symbols[hull] for hull in hulls.split(', ')))

def sort_key(key):
    hulls, bonus = key
    amount, stat = bonus.split(' ', maxsplit=1)
    return (tuple(hull_symbol_indices[hull] for hull in hulls), bonus_indices.index(stat), amount)

bonuses = {}

main_nations = ['Eagle Union', 'Royal Navy', 'Sakura Empire', 'Metalblood']

explicit_name_replacements = {
    'Neptune' : 'HMS Neptune',
    'Ōshio' : 'Ooshio',
    'Leberecht Maass' : 'Z1',
    'Georg Thiele' : 'Z2',
    'Hans Lüdemann' : 'Z18',
    'Hermann Künne' : 'Z19',
    'Karl Galster' : 'Z20',
    'Wilhelm Heidkamp' : 'Z21',
    'McCall' : 'McCall',
    'St.Louis' : 'St. Louis',
    "Jun'yō" : 'Junyou',
    'Saint-Louis' : 'Saint Louis',
}

stat_replacements = [
    ('HP', 'Health'),
    ('Hit', 'Accuracy'),
    ('Air Power', 'Airpower'),
    ('Anti-Air', 'AA'),
    ]

with open('tech_bonuses.csv', encoding='utf-8') as csvfile:
    reader = csv.reader(csvfile)
    header = None
    bonus_hull = None
    nation = None
    for row in reader:
        if header is None:
            header = row
            continue

        prefix, name = row[4].split(maxsplit = 1)

        bonus_hulls = row[3] or bonus_hulls
        bonus_hulls_tuple = hull_symbols_tuple(bonus_hulls)

        nation = row[2] or nation

        if name in explicit_name_replacements:
            name = explicit_name_replacements[name]
        else:
            name = name.replace('É', 'E')
            name = name.replace('é', 'e')
            name = name.replace('ō', 'ou')
            name = name.replace('ū', 'uu')
            name = re.sub(r'^I(\d+)$', r'I-\g<1>', name)
            if ' of ' not in name and ' der ' not in name:
                name = name.title()

        bonus = row[bonus_index]
        for old, new in stat_replacements:
            bonus = bonus.replace(old, new)
        key = (bonus_hulls_tuple, bonus)
        
        if key not in bonuses:
            bonuses[key] = []
        bonuses[key].append((name, nation))

result = ''
for key in sorted(bonuses.keys(), key = sort_key):
    hulls, bonus = key
    result += '|-\n'
    result += '| ' + '<br/>'.join('{{' + hull + '}}' + hull for hull in hulls)
    result += ' || ' + bonus[:3] + '{{' + bonus[3:] + '}}'
    for main_nation in main_nations:
        result += ' || ' + ', '.join('[[' + name + ']]' for name, nation in sorted(bonuses[key]) if nation == main_nation)
    result += ' || ' + ', '.join('[[' + name + ']]' for name, nation in sorted(bonuses[key]) if nation not in main_nations)
    result += '\n'

print(result)
