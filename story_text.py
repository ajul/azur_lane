from azurlane import load_lua
import re
import os

stories = {}

story_dir = os.path.join(load_lua.src_dir, load_lua.server, 'gamecfg', 'story')
ship_skin_srcs = load_lua.load_sharecfg('ship_skin_template', key_type=int)
memory_srcs = load_lua.load_sharecfg('memory_template', key_type=int)
memory_group_srcs = load_lua.load_sharecfg('memory_group', key_type=int)

memory_titles = {}
memory_ids = {}

memory_group_titles = {}

for memory_group in memory_group_srcs.values():
    title = memory_group['title']
    for memory_id in memory_group['memories'].values():
        memory_group_titles[memory_id] = title

for memory in memory_srcs.values():
    chapter_id = memory['story']
    title = memory['title']
    memory_titles[chapter_id] = title
    if memory['id'] in memory_group_titles:
        #print(chapter_id)
        memory_group_titles[chapter_id] = memory_group_titles[memory['id']]

for filename in os.listdir(story_dir):
    m = re.match('(.*[^\d])([\d-]*)\.lua$', filename)
    if not m:
        print('Skipping', filename)
        continue
    story_prefix = m.group(1)
    if re.match('index', story_prefix):
        print('Skipping', filename)
        continue
    chapter_number = m.group(2)
    chapter_key = tuple(int(x or 0) for x in chapter_number.split('-'))
    
    path = os.path.join(story_dir, filename)
    story_data = load_lua.load_file(path)

    chapter_id = story_data['id']
    if chapter_id in memory_titles:
        chapter_name = '%s: %s' % (chapter_number, memory_titles[chapter_id])
    else:
        chapter_name = 'Chapter %s' % chapter_number

    if chapter_id in memory_group_titles:
        story_name = memory_group_titles[chapter_id]
    else:
        story_name = story_prefix

    chapter_lines = []
    for line in story_data['scripts'].values():
        if 'actor' in line and line['actor'] > 0:
            if line['actor'] in ship_skin_srcs:
                actor = ship_skin_srcs[line['actor']]['name']
            else:
                actor = 'Unknown actor %d' % line['actor']
                #print(actor)
        elif 'actorName' in line:
            actor = line['actorName']
        else:
            actor = 'Narrator'
        if 'say' in line and line['say']:
            chapter_lines.append((actor, line['say']))
        elif 'sequence' in line:
            for sequence_item in line['sequence'].values():
                if sequence_item[1]:
                    chapter_lines.append((actor, sequence_item[1]))
        if 'options' in line:
            for option_index, value in line['options'].items():
                if len(line['options']) > 1:
                    actor = "'''Option %d:'''" % option_index
                else:
                    actor = "'''Commander:'''"
                chapter_lines.append((actor, value['content']))
    chapter_text = 'Chapter %s=<table style="border:none;">' % chapter_name

    def font_rescale_to_span(m):
        input_size = float(m.group(1))
        #print(input_size)
        output_size = input_size / 30.0
        return '<span style="font-size:%0.2fem;">' % output_size
    
    for actor, line in chapter_lines:
        line = re.sub('\r?\n', '<br/>', line)
        line = re.sub('<size=(\d+)>', font_rescale_to_span, line)
        line = re.sub('</size>', '</span>', line)
        chapter_text += '<tr><td style="font-weight:bold; vertical-align:top; padding-right:1em;">%s</td><td>%s</td></tr>\n' % (actor, line)
    chapter_text += '</table>'

    if story_name not in stories: stories[story_name] = {}
    stories[story_name][chapter_key] = chapter_text

for story_key, chapters in stories.items():
    if len(chapters) > 1:
        out_text = '<tabber>\n' + '|-|'.join(v for k, v in sorted(chapters.items())) + '</tabber>\n'
    else:
        out_text = ''.join(v for v in sorted(chapters.values()))
    out_file_name = story_key
    out_file_name = re.sub(' ', '_', out_file_name)
    out_file_name = re.sub('\W', '', out_file_name)
    with open('story_out/%s.txt' % out_file_name, 'w', encoding='utf-8') as out_file:
        out_file.write(out_text)

        
