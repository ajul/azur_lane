import load_lua

meow_data_srcs = load_lua.load_sharecfg('commander_data_template', key_type=int)
meow_skill_srcs = load_lua.load_sharecfg('commander_skill_template', key_type=int)
meow_skill_effect_srcs = load_lua.load_sharecfg('commander_skill_effect_template', key_type=int)

for meow in meow_data_srcs.values():
    skill = meow_skill_srcs[meow['skill_id'] + 2]
    descs = [desc[2] for desc in skill['desc'].values()]
    for effect_id, desc in zip(skill['effect_tactic'].values(), descs):
        effect = meow_skill_effect_srcs[effect_id]
        if effect['effect_type'] == 'battle_buff':
            buff_id = effect['args'][1]
            buff = load_lua.load_buff(buff_id)
            effect1 = buff['effect_list'][1]
            if effect1['type'] == 'BattleBuffCastSkill':
                skill_id = effect1['arg_list']['skill_id']
                skill = load_lua.load_skill(skill_id)
                buff_id = skill['effect_list'][1]['arg_list']['buff_id']
                buff = load_lua.load_buff(buff_id)
                print(meow['name'], desc, buff_id)
                for effect in buff['effect_list'].values():
                    print('  ', effect['type'], effect['arg_list'])
                print()
