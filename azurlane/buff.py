from azurlane import load_lua

def describe_buff(buff_id, bullet_damage = None):
    try:
        buff = load_lua.load_buff(buff_id)
    except FileNotFoundError:
        return 'Missing buff file'
    
    basic_descriptions = []
    
    if buff['time'] > 0:
        basic_descriptions.append('duration %0.1fs' % buff['time'])
    
    if buff['stack'] == 1:
        basic_descriptions.append('does not stack')
    else:
        basic_descriptions.append('stacks up to %d times' % buff['stack'])
        
    
    effect_descriptions = []
    for effect in buff['effect_list'].values():
        arg_list = effect['arg_list']
        if effect['type'] == 'BattleBuffAddAttr':
            number = arg_list['number']
            attr = arg_list['attr']
            effect_desc = '%+0.3f %s' % (number, attr)
        elif effect['type'] == 'BattleBuffDOT':
            dot_type = 'burn' if arg_list['dotType'] == 1 else 'flood'
            base_damage = arg_list['number']
            proportion_of_alpha = arg_list['k']
            tick_time = arg_list['time']
            tick_count = int(buff['time'] / arg_list['time'])
            attr = arg_list['attr']
            
            effect_desc = dot_type + ' for '
            damage_descs = []
            if proportion_of_alpha != 0.0:
                s = '%0.1f%% of alpha damage' % (proportion_of_alpha * 100.0)
                if bullet_damage is not None:
                    s += ' (= %0.2f)' % (bullet_damage * proportion_of_alpha)
                s += ' scaled with ' + attr
                damage_descs.append(s)
            if base_damage != 0.0:
                damage_descs.append('%0.1f damage' % base_damage)
            effect_desc += ' + '.join(damage_descs)
            effect_desc += ' every %0.1fs (%d times)' % (tick_time, tick_count)
        elif effect['type'] == 'BattleBuffFixVelocity':
            speed_effects = []
            if arg_list['add'] != 0.0:
                speed_effects.append('%+0.1f' % arg_list['add'])
            if arg_list['mul'] != 0.0:
                speed_effects.append('%+0.1f%%' % (arg_list['mul'] / 100.0))
            effect_desc = ', '.join(speed_effects) + ' movement speed'
        elif effect['type'] == 'BattleBuffAddBuff':
            effect_desc = 'conditional : (%s)' % describe_buff(arg_list['buff_id'])
        else:
            effect_desc = 'unknown effect type ' + effect['type']
        effect_descriptions.append(effect_desc)
    
    return ', '.join(basic_descriptions) + ' : ' + ', '.join(effect_descriptions)
