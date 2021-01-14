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
ship_lb_srcs = load_lua.load_sharecfg('ship_data_breakout')
retro_srcs = load_lua.load_sharecfg('transform_data_template')

retro_ship_ids = set()

for retro_data in retro_srcs.values():
    if len(retro_data['ship_id']) > 0:
        retro_ship_ids.add(retro_data['ship_id'][1][2])

display_id_by_group = {}
for display_id, group_data in ship_group_srcs.items():
    display_id_by_group[group_data['group_type']] = display_id

base_max = {}
base_kai = {}

for ship_id, ship in ship_stats_srcs.items():
    base_target_dict = base_kai if ship_id in retro_ship_ids else base_max
    base = list(ship['base_list'][x] for x in [1, 2, 3])
    if ship_id in ship_data_srcs and ship_id in ship_lb_srcs:
        ship_data = ship_data_srcs[ship_id]
        if 2 in ship_data['hide_buff_list'].values():
            base[0] = 3
        elif 1 in ship_data['hide_buff_list'].values():
            base[0] = 2
        group = ship_data['group_type']
        display_id = display_id_by_group[group]
        #print(display_id, ship['name'])
        base_target_dict[display_id] = (ship_id, base)
    else:
        pass
        #print('No data for ship', ship_id, ship['name'])

"""
for display_id, (ship_id, base) in base_max.items():
    print(display_id, ship_stats_srcs[ship_id]['name'], base)
"""

import re

prompt_per_ship = False

site = pywikibot.Site('azurlane')  # The site we want to run our bot on
site.login()
ship_category = pywikibot.Category(site, 'Ships')
for page in ship_category.articles():
    match = re.search(r'ID\s*=\s*((Collab|Plan)?\d+)', page.text)
    if not match:
        print('Page', page.title(), 'does not have parseable ID')
        continue
    display_id_string = match.group(1)
    display_id_string = display_id_string.replace('Collab', '10')
    display_id_string = display_id_string.replace('Plan', '20')
    display_id = int(display_id_string)
    if display_id not in base_max:
        print('No base data for', page.title(), display_id)
        continue
    ship_id, ship_base_max = base_max[display_id]
    ship_base_kai = None
    if display_id in base_kai:
        _, ship_base_kai = base_kai[display_id]
    
    edited = False
    for equipment_index in [1, 2, 3]:
        pattern = u'Eq%dBaseMax = (\d+)' % equipment_index
        match = re.search(pattern, page.text)
        if match:
            old_value = int(match.group(1))
            new_value = ship_base_max[equipment_index-1]
            if new_value != old_value:
                replacement = u'Eq%dBaseMax = %d' % (equipment_index, new_value)
                page.text = re.sub(pattern, replacement, page.text, count=1)
                edited = True
        else:
            print('Page', page.title(), 'does not contain', pattern)
        if ship_base_kai:
            pattern = u'Eq%dBaseKai = (\d+)' % equipment_index
            match = re.search(pattern, page.text)
    if not edited: continue
    print(page.title(), display_id, ship_base_max, ship_base_kai)
    edit_note = 'Bot: Fix some equipment base values. Base values are now %s.' % ship_base_max
    if prompt_per_ship:
        print(page.text)
        wat_do = input('Enter one of the following: "" to continue, "k" to skip, "x" to stop:')
        if wat_do == "":
            page.save(edit_note)
            pass
        elif wat_do == "k":
            continue
        else:
            break
    else:
        page.save(edit_note)
        pass


