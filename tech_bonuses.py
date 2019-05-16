import csv
import re

bonus_index = -2

hull_strings = {
    'Destroyer' : 'DD',
    'Light Cruiser' : 'CL',
    'Heavy Cruiser, Monitor, Super Cruiser' : 'CA/BM/CB',
    'Battlecruiser, Battleship, Aviation Battleship' : 'BB/BC/BBV',
    'Light Aircraft Carrier, Aircraft Carrier' : 'CV/CVL',
    'Light Aircraft Carrier' : 'CVL',
    'Repair Ship' : 'AR',
    'Submarine, Submarine Carrier' : 'SS/SSV',
}

hull_string_indexes = [x for x in hull_strings.values()]

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

def get_bonus_hulls_string(hulls):
    return hull_strings[hulls]

def sort_key(key):
    bonus_hulls_string, bonus = key
    amount, stat = bonus.split(' ', maxsplit=1)
    return (hull_string_indexes.index(bonus_hulls_string), bonus_indices.index(stat), amount)

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

def read_bonuses(index):
    bonuses = {}
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
            bonus_hulls_string = get_bonus_hulls_string(bonus_hulls)

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
            key = (bonus_hulls_string, bonus)
            
            if key not in bonuses:
                bonuses[key] = []
            bonuses[key].append((name, nation))
    return bonuses

collect_bonuses = read_bonuses(-2)
lv120_bonuses = read_bonuses(-1)

#########################################
# Output.
#########################################

def create_table(bonuses, bonus_hulls_string):
    result = ''
    result += bonus_hulls_string + '=\n'
    result += '{|class = "wikitable"\n'
    result += '! Bonus\n'
    for nation in main_nations + ['Other']:
        result += '! style="width:20%;min-width:100px;" | ' + nation + '\n'

    bonus_types = sorted(set(bonus for hulls, bonus in bonuses.keys() if hulls == bonus_hulls_string), key = lambda x: (bonus_indices.index(x[3:]), x))
        
    for bonus in bonus_types:
        result += '|-\n'
        result += '| ' + bonus[:2] + '&nbsp;{{' + bonus[3:] + '}} '
        key = (bonus_hulls_string, bonus)
        for main_nation in main_nations:
            result += ' || ' + ', '.join('[[' + name + ']]' for name, nation in sorted(bonuses[key]) if nation == main_nation)
            
        result += ' || ' + ', '.join('[[' + name + ']]' for name, nation in sorted(bonuses[key]) if nation not in main_nations)
        result += '\n'
    result += '|}\n'
    return result

def create_tabber(bonuses):
    result = ''
    result += '<tabber>\n'
    result += '|-|'.join(create_table(bonuses, bonus_hulls_string) for bonus_hulls_string in hull_string_indexes)
    result += '</tabber>\n'
    return result

result = ''
result += '==== Collection stat bonuses ====\n'
result += create_tabber(collect_bonuses)

result += '==== Level 120 stat bonuses ====\n'
result += create_tabber(lv120_bonuses)

result += 'Special thanks to [[User:Dimbreath|Dimbreath]] for gathering/providing all of the data on Tech Point values, '
result += 'original data can be found [https://docs.google.com/spreadsheets/d/1SOAqHc1zgE3SdSEZesrmKd0hDkhZL4Zg96heJMLbSOM/edit#gid=0 here]\n'

print(result)
