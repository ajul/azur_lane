from azurlane import load_lua

chapter_srcs = load_lua.load_sharecfg('world_chapter_random', key_type=int)
target_srcs = load_lua.load_sharecfg('world_target_data', key_type=int)
item_srcs = load_lua.load_sharecfg('item_data_statistics', key_type=int)
world_item_srcs = load_lua.load_sharecfg('world_item_data_template', key_type=int)
#world_expedition_srcs = load_lua.load_sharecfg('world_chapter_template', key_type=int)

def get_item(item_id):
    return item_srcs.get(item_id, world_item_srcs.get(item_id, {}))

result = '{| class="wikitable sortable"\n'
result += '! ID !! Name !! Corruption !! Star objectives !! Rewards\n'

total_rewards = {}

for chapter_id, chapter_data in chapter_srcs.items():
    if chapter_id > 10 and chapter_id < 200:
        print(chapter_id)
        chapter_name = chapter_data['name']
        corruption = str(chapter_data['hazard_level'])
        ap_cost = str(chapter_data['enter_cost'])
        if ap_cost == '0': continue

        """
        if len(chapter_data['sairen_chapter']) > 0:
            siren_chapter_id = chapter_data['sairen_chapter'][1]
            siren_chapter_data = chapter_srcs[siren_chapter_id]
            siren_corruption = siren_chapter_data['hazard_level']
            siren_ap_cost = siren_chapter_data['enter_cost']
            corruption += '<br/>Siren: %d' % siren_corruption
            #ap_cost += '<br/>Siren: %d' % siren_ap_cost
        """

        """
        if len(chapter_data['complete_chapter']) > 0:
            complete_chapter_id = chapter_data['complete_chapter'][1]
            complete_chapter_data = chapter_srcs[complete_chapter_id]
            complete_corruption = str(complete_chapter_data['hazard_level'])
            complete_ap_cost = str(complete_chapter_data['enter_cost'])
            corruption += '<br/>Safe: %s' % complete_corruption
            ap_cost += '<br/>Safe: %s' % complete_ap_cost
        """

        targets = []
        for target_id in chapter_data['normal_target'].values():
            target_data = target_srcs[target_id]
            targets.append(target_data['target_desc'])
        for target_id in chapter_data['cryptic_target'].values():
            target_data = target_srcs[target_id]
            targets.append(target_data['target_desc'])

        rewards = []
        for reward_data in chapter_data['target_drop_show'].values():
            item_type = reward_data[2][1]
            item_id = reward_data[2][2]
            quantity = reward_data[2][3]
            if item_type == 2:
                item_data = item_srcs[item_id]
            elif item_type == 12:
                item_data = world_item_srcs[item_id]
            item_name = item_data['name']
            rewards.append((item_name, quantity))
            total_rewards[item_name] = total_rewards.get(item_name, 0) + quantity

        result += '|-\n'
        result += '| %d || %s || %s \n' % (chapter_id, chapter_name, corruption)
        result += '| \n'
        for target in targets:
            result += '# %s\n' % target
        result += '| \n'
        for item_name, quantity in rewards:
            result += '# %s × %d\n' % (item_name.rstrip(), quantity)

result += '|}\n'

with open('op_zone_info.txt', 'w', encoding='utf-8') as out_file:
    out_file.write(result)

for key in sorted(total_rewards.keys()):
    print('* %s × %d' % (key, total_rewards[key]))
