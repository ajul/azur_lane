import azurlane.load_lua
import azurlane.buff
import azurlane.skill
import copy

aircraft_srcs = azurlane.load_lua.load_sharecfg('aircraft_template')
barrage_srcs = azurlane.load_lua.load_sharecfg('barrage_template')
bullet_srcs = azurlane.load_lua.load_sharecfg('bullet_template')
weapon_srcs = azurlane.load_lua.load_sharecfg('weapon_property')
skill_data_srcs = azurlane.load_lua.load_sharecfg('skill_data_template')
skill_display_srcs = azurlane.load_lua.load_sharecfg('skill_data_display')

seen_weapon_sets = {}
for skill_id, skill_display_src in skill_display_srcs.items():
    last_effects = azurlane.skill.get_last_effects(skill_id)

    if last_effects is None:
        continue

    weapon_ids = []
    for idx, effect in last_effects.items():
        if effect['type'] != 'BattleSkillFire': continue
        weapon_ids.append(effect['arg_list']['weapon_id'])
    if len(weapon_ids) == 0: continue
    ship_names = []
    rounded_skill_id = (skill_id // 10) * 10
    if skill_id in azurlane.skill.skill_to_ship_names_map:
        ship_names = azurlane.skill.skill_to_ship_names_map[skill_id]
    elif rounded_skill_id in azurlane.skill.skill_to_ship_names_map:
        ship_names = azurlane.skill.skill_to_ship_names_map[rounded_skill_id]

    # (damage, bullet_id) -> num_bullets

    bullets = {}
    barrage_ids = []
    aircraft_ids = set()
    aircraft_weapon_ids = set()

    weapon_strings = []

    def add_weapon(weapon_id):
        if weapon_id not in weapon_srcs:
            print('Skill', skill_id, ship_names, 'missing weapon', weapon_id)
            return
        weapon_src = weapon_srcs[weapon_id]
        weapon_strings.append('%d (type %d)' % (weapon_id, weapon_src['type']))
        barrage_index = 1
        while barrage_index in weapon_src['barrage_ID'] and barrage_index in weapon_src['bullet_ID']:
            barrage_id = weapon_src['barrage_ID'][barrage_index]
            barrage_ids.append(barrage_id)
            barrage_src = barrage_srcs[barrage_id]
            bullet_id = weapon_src['bullet_ID'][barrage_index]
            num_bullets = (barrage_src['primal_repeat'] + 1) * (barrage_src['senior_repeat'] + 1)
            if bullet_id in bullet_srcs:
                damage = weapon_src['damage'] * weapon_src['corrected'] / 100.0
                bullet_key = (damage, bullet_id)
                if bullet_key not in bullets:
                    bullets[bullet_key] = 0

                bullets[bullet_key] += num_bullets
            elif bullet_id in aircraft_srcs:
                 aircraft_src = aircraft_srcs[bullet_id]
                 aircraft_ids.add(bullet_id)
                 for weapon_id in aircraft_src['weapon_ID'].values():
                     aircraft_weapon_ids.add(weapon_id)
                     for i in range(num_bullets):
                         add_weapon(weapon_id)
            else:
                print('Skill', skill_id, ship_names, 'missing bullet/aircaft', bullet_id)
            barrage_index += 1

    for weapon_id in weapon_ids:
        add_weapon(weapon_id)

    first_line = 'Skill %d %s: ships %s: weapon_ids %s, barrage_ids %s' % (
        skill_id, skill_display_src['name'], sorted(ship_names), ', '.join(weapon_strings), barrage_ids)
    if len(aircraft_ids) > 0:
        first_line += ', aircraft_ids %s, aircraft weapon_ids %s' % (aircraft_ids, aircraft_weapon_ids)
    print(first_line)
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
        if 'tracker' in bullet_src['acceleration']:
            s += '\n        tracking range %d' % bullet_src['acceleration']['tracker']['range']
        if 'range' in bullet_src['hit_type']:
            s += '\n        splash range %d' % bullet_src['hit_type']['range']
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
            buff_desc = azurlane.buff.describe_buff(buff_id, damage)
            s += '\n        %0.2f%% buff %d (lv %d): %s' % (buff_chance, buff_id, buff_level, buff_desc)
            buff_index += 1
        print(s)
        
