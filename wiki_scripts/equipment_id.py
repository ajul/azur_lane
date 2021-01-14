import sys
import os
sys.path.append("..")
if os.path.exists('pywikibot.lwp'):
    os.remove('pywikibot.lwp') #pepega

import pywikibot
import azurlane.load_lua
import azurlane.weapon
os.chdir('..')

equip_stats_srcs = load_lua.load_sharecfg('equip_data_statistics')

equip_stats_srcs_base_only = { k : v for k, v in equip_stats_srcs.items() if 'base' not in v }

import re

site = pywikibot.Site('azurlane')  # The site we want to run our bot on
site.login()
category = pywikibot.Category(site, 'Equipment')

equip_wiki_keys = [
    'Name',
    'ENName',
    'Image',
    'Stars',
    'BaseID',
    'Type',
]

for page in category.articles():
    equip_wikis = page.text.split('|-|')

    edit_message = 'Bot: set BaseIDs:'
    edited = False
    
    for equip_wiki_index, equip_wiki in enumerate(equip_wikis):
        # try to determine internal ID
       
        equip_wiki_data = {}
        for equip_wiki_key in equip_wiki_keys:
            pattern = r'%s\s*=(.*)' % equip_wiki_key
            match = re.search(pattern, equip_wiki)
            if match:
                value = match.group(1).strip()
                equip_wiki_data[equip_wiki_key] = value
            else:
                equip_wiki_data[equip_wiki_key] = ''

        if not (equip_wiki_data['Name'] or equip_wiki_data['ENName'] or equip_wiki_data['Image']):
            continue

        if equip_wiki_data['BaseID']:
            print(equip_wiki_data['Name'], 'already has BaseID, skipping')
            continue

        candidates = []
        for equip_id, equip_stats in equip_stats_srcs_base_only.items():
            match_name = equip_wiki_data['Name'] != '' and (equip_wiki_data['Name'] == equip_stats['name'])
            match_en_name = equip_wiki_data['ENName'] != '' and (equip_wiki_data['ENName'] == equip_stats['name'])
            match_rarity = equip_wiki_data['Stars'] != '' and (int(equip_wiki_data['Stars']) == equip_stats['rarity'])
            match_image = equip_wiki_data['Image'] != '' and (
                equip_wiki_data['Image'] == equip_stats['icon'] + '.png' or
                equip_wiki_data['Image'] == equip_stats['icon'])
            matches = (match_rarity, match_en_name, match_name, match_image)
            if match_rarity and (match_image or match_name or match_en_name):
                candidates.append((matches, equip_id))
        candidates.sort()
        if len(candidates) == 1:
            pass
            # print(page.title(), ":", equip_wiki_data['Name'], candidates[0][1])
        else:
            pass
            #print(page.title(), ":", equip_wiki_data['Name'], candidates)
        _, equip_id = candidates[-1]
        pattern = 'BaseID = .*'
        match = re.search(pattern, equip_wiki)
        if match:
            # replace blank
            equip_wiki = re.sub(pattern, 'BaseID = %d' % equip_id, equip_wiki)
            equip_wikis[equip_wiki_index] = equip_wiki
        else:
            # insert new line
            pattern = 'Image\s*=.*'
            match = re.search(pattern, equip_wiki)
            insert_text = '\n  | BaseID = %d' % equip_id
            equip_wiki = equip_wiki[:match.end(0)] + insert_text + equip_wiki[match.end(0):]
            equip_wikis[equip_wiki_index] = equip_wiki
        edit_message += ' %d' % equip_id
        edited = True
        #if equip_wiki_data['Type'] != common.equipment_types[equip_stats_srcs_base_only[equip_id]['type']]:
        #    print(page.title(), equip_wiki_data['Type'], common.equipment_types[equip_stats_srcs_base_only[equip_id]['type']])
    
    page.text = '|-|'.join(equip_wikis)

    if edited:
        page.save(edit_message)
