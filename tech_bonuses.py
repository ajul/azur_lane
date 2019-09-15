import csv
import re

hull_strings = {
    'Destroyer' : 'DD',
    'Light Cruiser' : 'CL',
    'Heavy Cruiser, Monitor, Super Cruiser' : 'CA/BM/CB',
    'Battlecruiser, Battleship, Aviation Battleship' : 'BC/BB/BBV',
    'Light Aircraft Carrier, Aircraft Carrier' : 'CV/CVL',
    'Light Aircraft Carrier' : 'CV/CVL',
    'Repair Ship' : 'AR',
    'Submarine, Submarine Carrier' : 'SS/SSV',
}

hull_string_indexes = [x for x in hull_strings.values()]
hull_string_indexes.remove('CV/CVL')

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

main_nations = ['Eagle Union', 'Royal Navy', 'Sakura Empire', 'Ironblood']

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

def read_bonuses(bonus_index):
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

            if nation == 'Metalblood': nation = 'Ironblood'

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
    result += '! style="min-width:75px;" | Bonus\n'
    result += '! style="width:100%;" | Ships\n'

    bonus_types = sorted(set(bonus for hulls, bonus in bonuses.keys() if hulls == bonus_hulls_string), key = lambda x: (bonus_indices.index(x[3:]), x))
        
    for bonus in bonus_types:
        result += '|-\n'
        result += '| ' + bonus[:3] + '{{' + bonus[3:] + '}}'
        if bonus[3:] == 'ASW' and bonus_hulls_string == 'CV/CVL':
            result += '<br/>(CVL only)'
        elif bonus[3:] == 'Evasion' and bonus_hulls_string == 'BC/BB/BBV':
            result += '<br/>(BC only)'
        result += ' || '
        key = (bonus_hulls_string, bonus)
        ship_lists = []
        for main_nation in main_nations:
            ship_list = ', '.join('[[' + name + ']]' for name, nation in sorted(bonuses[key]) if nation == main_nation)
            if ship_list:
                ship_lists.append((main_nation, ship_list))
        ship_list = ', '.join('[[' + name + ']]' for name, nation in sorted(bonuses[key]) if nation not in main_nations)
        if ship_list:
            ship_lists.append(('Other', ship_list))
            
        result += '<br/>'.join("'''" + nation + ":''' " + ship_list for nation, ship_list in ship_lists)
        result += '\n'
    result += '|}\n'
    return result

def create_tabber(bonuses):
    result = ''
    result += '<div style="width:1300px;"><tabber>\n'
    result += '|-|'.join(create_table(bonuses, bonus_hulls_string) for bonus_hulls_string in hull_string_indexes)
    result += '</tabber></div>\n'
    return result

result = ''
result += '==== Collection stat bonuses ====\n'
result += create_tabber(collect_bonuses)

result += '==== Level 120 stat bonuses ====\n'
result += create_tabber(lv120_bonuses)

#result += 'Special thanks to [[User:Dimbreath|Dimbreath]] for gathering/providing all of the data on Tech Point values, '
#result += 'original data can be found [https://docs.google.com/spreadsheets/d/1SOAqHc1zgE3SdSEZesrmKd0hDkhZL4Zg96heJMLbSOM/edit#gid=0 here]\n'

print(result)

def recsv(bonuses):
    result = ''
    for (hulls, bonus), value in bonuses.items():
        for ship, nation in value:
            result += '%s,%s,%s,%s\n' % (hulls, bonus, ship, nation)
    return result

with open('collection_bonuses.csv', mode = 'w') as f:
    f.write(recsv(collect_bonuses))
    
with open('lv120_bonuses.csv', mode = 'w') as f:
    f.write(recsv(lv120_bonuses))
