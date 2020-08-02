from azurlane import load_lua
import os

story_prefix = 'shengyongqu'

ship_skin_srcs = load_lua.load_sharecfg('ship_skin_template', key_type=int)

tabs = {}

for chapter, story in load_lua.load_stories(story_prefix):
    tab_text = '%s=\n' % chapter
    for line in story['scripts'].values():
        if 'actor' in line:
            actor = ship_skin_srcs[line['actor']]['name']
        elif 'actorName' in line:
            actor = line['actorName']
        else:
            actor = 'Narrator'
        if 'say' in line and line['say']:
            line_text = "'''%s:''' %s<br/>\n" % (actor, line['say'])
            tab_text += line_text
        else:
            for sequence_item in line['sequence'].values():
                if sequence_item[1]:
                    line_text = "'''%s:''' %s<br/>\n" % (actor, sequence_item[1])
                    tab_text += line_text
    tabs[tuple(int(x) for x in chapter.split('-'))] = tab_text

result = '<tabber>\n' + '|-|'.join(v for k, v in sorted(tabs.items())) + '</tabber>\n'
print(result)
