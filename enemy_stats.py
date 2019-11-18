import load_lua
import re

chapter_srcs = load_lua.load_sharecfg('chapter_template')
expedition_data_srcs = load_lua.load_sharecfg('expedition_data_template')
enemy_data_srcs = load_lua.load_sharecfg('enemy_data_statistics')

for chapter_id, chapter_src in chapter_srcs.items():
    if chapter_id == 'all': continue
    is_hard_mode = chapter_src['type'] > 1
    # filter to main story
    m = re.match('\d+–\d', chapter_src['chapter_name'])
    if not m: continue
    expedition_ids = set()
    for t in chapter_src['expedition_id_weight_list'].values():
        expedition_ids.add(t[1])
    for key in ['ambush_expedition_list',
                'guarder_expedition_list',
                'elite_expedition_list',
                'ai_expedition_list',
                'patrolai_expedition_list',
                'submarine_expedition_list',
                'boss_expedition_id']:
        for expedition_id in chapter_src[key]:
            if expedition_id > 1: expedition_ids.add(expedition_id)
        
    print(chapter_id, chapter_src['chapter_name'], is_hard_mode, expedition_ids)
