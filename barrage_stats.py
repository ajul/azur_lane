from azurlane import load_lua, skill
import common
import copy

barrage_srcs = load_lua.load_sharecfg('barrage_template')
bullet_srcs = load_lua.load_sharecfg('bullet_template')
weapon_srcs = load_lua.load_sharecfg('weapon_property')
skill_data_srcs = load_lua.load_sharecfg('skill_data_template')
skill_display_srcs = load_lua.load_sharecfg('skill_data_display')

seen_weapon_sets = {}
for skill_id, skill_display_src in skill_display_srcs.items():
    last_effects = skill.get_last_effects(skill_id)

    if last_effects is None:
        continue

    weapon_ids = []
    for idx, effect in last_effects.items():
        if effect['type'] != 'BattleSkillFire': continue
        weapon_ids.append(effect['arg_list']['weapon_id'])
    if len(weapon_ids) == 0: continue
    ship_names = []
    rounded_skill_id = (skill_id // 10) * 10
    if skill_id in skill.skill_to_ship_names_map:
        ship_names = skill.skill_to_ship_names_map[skill_id]
    elif rounded_skill_id in skill.skill_to_ship_names_map:
        ship_names = skill.skill_to_ship_names_map[rounded_skill_id]

    # (damage, bullet_id) -> num_bullets

    bullets = {}
    barrage_ids = []

    for weapon_id in weapon_ids:
        if weapon_id not in weapon_srcs:
            print('Skill', skill_id, ship_names, 'missing weapon', weapon_id)
            continue
        weapon_src = weapon_srcs[weapon_id]
        barrage_index = 1
        while barrage_index in weapon_src['barrage_ID']:
            barrage_id = weapon_src['barrage_ID'][barrage_index]
            barrage_ids.append(barrage_id)
            barrage_src = barrage_srcs[barrage_id]
            bullet_id = weapon_src['bullet_ID'][barrage_index]
            if bullet_id not in bullet_srcs:
                print('Skill', skill_id, ship_names, 'missing bullet', bullet_id)
                barrage_index += 1
                continue

            damage = weapon_src['damage'] * weapon_src['corrected'] / 100.0
            bullet_key = (damage, bullet_id)
            if bullet_key not in bullets:
                bullets[bullet_key] = 0

            num_bullets = (barrage_src['primal_repeat'] + 1) * (barrage_src['senior_repeat'] + 1)
            bullets[bullet_key] += num_bullets
            barrage_index += 1

    print('Skill %d %s: ships %s: weapon_ids %s, barrage_ids %s' % (
        skill_id, skill_display_src['name'], ship_names, weapon_ids, barrage_ids))
    for (damage, bullet_id), num_bullets in bullets.items():
        bullet_src = bullet_srcs[bullet_id]
        bullet_type = bullet_src['type']
        armor_modifiers = (bullet_src['damage_type'][1],
                           bullet_src['damage_type'][2],
                           bullet_src['damage_type'][3])

            
        net_damage = tuple(damage * num_bullets * x for x in armor_modifiers)
        s = '    bullet %d (type %d) : base damage %0.2f x %d : net damage %0.2f / %0.2f / %0.2f' % (
            bullet_id, bullet_type,
            damage, num_bullets,
            net_damage[0], net_damage[1], net_damage[2])
        if bullet_src['pierce_count'] > 0:
            s += '\n        pierce %d' % bullet_src['pierce_count']
        buff_index = 1
        while buff_index in bullet_src['attach_buff']:
            buff = bullet_src['attach_buff'][buff_index]
            if 'rant' in buff:
                buff_chance = buff['rant'] / 100.0
            else:
                buff_chance = 100.0
            buff_id = buff['buff_id']
            if 'level' in buff:
                buff_level = buff['level']
            else:
                buff_level = 0
            s += '\n        %0.2f%% buff %d (lv %d)' % (buff_chance, buff_id, buff_level)
            buff_index += 1
        print(s)
        
