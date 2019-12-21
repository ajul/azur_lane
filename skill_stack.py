import load_lua

skill_data_srcs = load_lua.load_sharecfg('skill_data_template', key_type=int)

# buff_id -> skills
stack_groups = {}

for skill_data in skill_data_srcs.values():
    name = skill_data['name']
    skill_id = skill_data['id']
    try:
        skill = load_lua.load_skill(skill_id)
    except:
        print('No file for skill %s (%d)' %( name, skill_id))
        continue
    for effect in skill['effect_list'].values():
        if effect['type'] == 'BattleSkillAddBuff':
            buff_id = effect['arg_list']['buff_id']
            if buff_id not in stack_groups:
                stack_groups[buff_id] = set()
            stack_groups[buff_id].add(name)

result = '{| class = "wikitable"\n'
for names in sorted(stack_groups.values()):
    if len(names) <= 1: continue
    result += '| ' + '<br/>'.join(sorted(names)) + '\n'
result += '|}'
print(result)
