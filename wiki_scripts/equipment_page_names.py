import sys
import os
sys.path.append("..")
if os.path.exists('pywikibot.lwp'):
    os.remove('pywikibot.lwp') #pepega

import pywikibot
from azurlane import common, load_lua, wiki
os.chdir('..')

site = pywikibot.Site('azurlane')  # The site we want to run our bot on
site.login()
category = pywikibot.Category(site, 'Equipment')

result = wiki.map_page_titles(category.articles(), 'BaseID', int)

with open('wiki_scripts/equipment_page_map.py', 'w', encoding='utf-8') as outfile:
    outfile.write('equipment_page_map = ' + str(result))
