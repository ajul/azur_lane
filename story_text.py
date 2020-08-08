from azurlane import load_lua
import re
import os

stories = {}

story_dir = os.path.join(load_lua.src_dir, load_lua.server, 'gamecfg', 'story')
ship_skin_srcs = load_lua.load_sharecfg('ship_skin_template', key_type=int)

for filename in os.listdir(story_dir):
    m = re.match('(.*[^\d])([\d-]*)\.lua$', filename)
    if not m:
        print('Skipping', filename)
        continue
    story_key = m.group(1)
    chapter_name = m.group(2)
    if re.match('index', story_key):
        print('Skipping', filename)
        continue
    chapter_key = tuple(int(x or 0) for x in chapter_name.split('-'))

    path = os.path.join(story_dir, filename)
    story_data = load_lua.load_file(path)

    chapter_text = '%s=\n' % chapter_name
    for line in story_data['scripts'].values():
        if 'actor' in line and line['actor'] > 0:
            if line['actor'] in ship_skin_srcs:
                actor = ship_skin_srcs[line['actor']]['name']
            else:
                actor = 'Unknown actor %d' % line['actor']
                print(actor)
        elif 'actorName' in line:
            actor = line['actorName']
        else:
            actor = 'Narrator'
        if 'say' in line and line['say']:
            line_text = "'''%s:''' %s<br/>\n" % (actor, line['say'])
            chapter_text += line_text
        elif 'sequence' in line:
            for sequence_item in line['sequence'].values():
                if sequence_item[1]:
                    line_text = "'''%s:''' %s<br/>\n" % (actor, sequence_item[1])
                    chapter_text += line_text

    if story_key not in stories: stories[story_key] = {}
    stories[story_key][chapter_key] = chapter_text

for story_key, chapters in stories.items():
    if len(chapters) > 1:
        out_text = '<tabber>\n' + '|-|'.join(v for k, v in sorted(chapters.items())) + '</tabber>\n'
    else:
        out_text = ''.join(v for v in sorted(chapters.values()))
    with open('story_out/%s.txt' % story_key, 'w', encoding='utf-8') as out_file:
        out_file.write(out_text)

        
