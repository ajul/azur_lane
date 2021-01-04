import sys
import os
sys.path.append("..")
if os.path.exists('pywikibot.lwp'):
    os.remove('pywikibot.lwp') #pepega

import pywikibot
from azurlane import load_lua
os.chdir('..')

ship_data_srcs = load_lua.load_sharecfg('ship_data_template')
ship_stats_srcs = load_lua.load_sharecfg('ship_data_statistics')
ship_group_srcs = load_lua.load_sharecfg('ship_data_group')

display_id_by_group = {}
for display_id, group_data in ship_group_srcs.items():
    display_id_by_group[group_data['group_type']] = display_id

base_max = {}
base_kai = {}

for ship_id, ship in ship_stats_srcs.items():
    base_target_dict = base_kai if 'Retrofit' in ship['name'] else base_max
    base = tuple(ship['base_list'][x] for x in [1, 2, 3])
    if ship_id in ship_data_srcs:
        group = ship_data_srcs[ship_id]['group_type']
        display_id = display_id_by_group[group]
        #print(display_id, ship['name'])
        base_target_dict[display_id] = (ship_id, base)
    else:
        pass
        #print('No data for ship', ship_id, ship['name'])
"""
for display_id, (ship_id, base) in base_kai.items():
    print(display_id, ship_stats_srcs[ship_id]['name'], base)
"""

import re

prompt_per_ship = True

site = pywikibot.Site('azurlane')  # The site we want to run our bot on
site.login()
ship_category = pywikibot.Category(site, 'Ships')
for page in ship_category.articles():
    if re.search(r'Eq\dBase', page.text):
        print('Page', page.title(), 'already has base data')
        continue
    match = re.search(r'ID\s*=\s*((Collab)|(Plan)?\d+)', page.text)
    if not match:
        print('Page', page.title(), 'does not have parseable ID')
        continue
    display_id_string = match.group(1)
    display_id_string = display_id_string.replace('Collab', '10')
    display_id_string = display_id_string.replace('Plan', '20')
    display_id = int(display_id_string)
    if display_id not in base_max:
        print('No base data for', page.title())
        continue
    ship_id, ship_base_max = base_max[display_id]
    ship_base_kai = None
    if display_id in base_kai:
        _, ship_base_kai = base_kai[display_id]
    for equipment_index in [1, 2, 3]:
        pattern = u'Eq%dType.*' % equipment_index
        match = re.search(pattern, page.text)
        if match:
            insert_index = match.end(0)
            insert_text = '\n | Eq%dBaseMax = %d' % (equipment_index, ship_base_max[equipment_index-1])
            if ship_base_kai:
                insert_text += '\n | Eq%dBaseKai = %d' % (equipment_index, ship_base_kai[equipment_index-1])
            page.text = page.text[:insert_index] + insert_text + page.text[insert_index:]
        else:
            print('Page', page.title(), 'does not have parseable equipment', equipment_index)
    print(page.title(), ship_base_max, ship_base_kai)
    if prompt_per_ship:
        print(page.text)
        wat_do = input('Enter one of the following: "" to continue, "k" to skip, "x" to stop:')
        if wat_do == "":
            page.save('Bot: Add equipment base data.')
        elif wat_do == "k":
            continue
        else:
            break
    else:
        page.save('Bot: Add equipment base data.')


