import os
os.chdir('..')

import sys
sys.path.append(".")

if os.path.exists('pywikibot.lwp'):
    os.remove('pywikibot.lwp') #pepega

import pywikibot

import azurlane.load_lua
import azurlane.weapon
import azurlane.wiki

equip_stats_srcs = azurlane.load_lua.load_sharecfg('equip_data_statistics')

site = pywikibot.Site('azurlane')  # The site we want to run our bot on
site.login()
category = pywikibot.Category(site, 'Submarine Torpedo')

for page in category.articles():
    equip_wikis = page.text.split('|-|')
    edit_message = 'Bot: set armor modifiers:'
    edited = False

    for equip_wiki_index, equip_wiki in enumerate(equip_wikis):
        equip_id = int(azurlane.wiki.get_template_value(equip_wiki, 'BaseID'))
        equip = equip_stats_srcs[equip_id]
        weapon_id = equip['weapon_id'][1]
        weapon = azurlane.weapon.WeaponStats(weapon_id)
        prev_armor_type = ['CoefMax', 'Coef', 'PatternSpread', 'Spread']
        for armor_type_index, armor_type in enumerate(['ArmorModL', 'ArmorModM', 'ArmorModH']):
            old_value = azurlane.wiki.get_template_value(equip_wiki, armor_type)
            new_value = str(int(round(weapon.armor_modifiers[armor_type_index] * 100)))
            if old_value != new_value:
                equip_wiki = azurlane.wiki.set_template_value(equip_wiki, armor_type, new_value, prev_armor_type)
                edited = True
            prev_armor_type = armor_type
        if edited:
            edit_message += str([int(round(x * 100)) for x in weapon.armor_modifiers])
            equip_wikis[equip_wiki_index] = equip_wiki
        
    page.text = '|-|'.join(equip_wikis)
    if edited:
        print(page.title(), edit_message)
        #print(page.text)
        page.save(edit_message)
    else:
        print(page.title(), 'skipped')
    
