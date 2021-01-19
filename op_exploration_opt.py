from azurlane import load_lua

chapter_srcs = load_lua.load_sharecfg('world_chapter_random', key_type=int)
target_srcs = load_lua.load_sharecfg('world_target_data', key_type=int)
item_srcs = load_lua.load_sharecfg('item_data_statistics', key_type=int)
world_item_srcs = load_lua.load_sharecfg('world_item_data_template', key_type=int)

desired_item = 'Cube'

class CorruptionData():
    def __init__(self, cost, production):
        self.cost = cost
        self.production = production

all_corruption_data = {
    1 : CorruptionData(5, {
        'Gain control' : 1,
        'record' : 0.5,
        'resource node' : 2,
        'victor' : 2,
        'Merchant' : 0.01,
        }),
    2 : CorruptionData(10, {
        'Gain control' : 1,
        'record' : 0.5,
        'resource node' : 2,
        'victor' : 2,
        'Merchant' : 0.01,
        }),
    3 : CorruptionData(15, {
        'anomalous' : 0.4,
        'record' : 0.5,
        'Gain control' : 1,
        'Meowfficer' : 0.4,
        'resource node' : 3,
        'victor' : 2,
        'Merchant' : 0.01,
        'Scanning' : 0.025,
        }),
    4 : CorruptionData(20, {
        'anomalous' : 0.25,
        'Gain control' : 1,
        'record' : 0.5,
        'Meowfficer' : 0.5,
        'resource node' : 5,
        'victor' : 3,
        'Merchant' : 0.025,
        'Scanning' : 0.025,
        }),
    5 : CorruptionData(30, {
        'anomalous' : 0.25,
        'Gain control' : 1,
        'record' : 0.5,
        'Meowfficer' : 1.0,
        'resource node' : 7,
        'victor' : 3,
        'Merchant' : 0.025,
        'Scanning' : 0.025,
        }),
    6 : CorruptionData(40, {
        'anomalous' : 0.25,
        'Gain control' : 1,
        'record' : 0.5,
        'Meowfficer' : 1.0,
        'resource node' : 7,
        'victor' : 3,
        'Merchant' : 0.025,
        'Scanning' : 0.025,
        }),
}

records = [
    44, 84,
    24, 92,
    93, 131,
    21, 31,
    43, 112,
    22, 134,
    81, 132,
    23, 62,
    83, 122]

rows = []

for chapter_id, chapter_data in chapter_srcs.items():
    if chapter_id > 10 and chapter_id < 200:
        chapter_name = chapter_data['name']
        corruption = chapter_data['hazard_level']
        ap_cost = str(chapter_data['enter_cost'])
        if ap_cost == '0': continue
        if corruption > 6: continue
        if 'Depths' in chapter_name: continue

        corruption_data = all_corruption_data[corruption]

        targets = []
        for target_id in chapter_data['normal_target'].values():
            target_data = target_srcs[target_id]
            targets.append(target_data)
        for target_id in chapter_data['cryptic_target'].values():
            target_data = target_srcs[target_id]
            targets.append(target_data)

        star_costs = []
        for target in targets:
            for product, product_quantity in corruption_data.production.items():
                if product in target['target_desc']:
                    target_quantity = target['condition'][1][2]
                    star_costs.append((corruption_data.cost * target_quantity / product_quantity, product))
                    break

        star_costs.sort()

        total_quantity = 0
        
        for reward_data in chapter_data['target_drop_show'].values():
            stars = reward_data[1]
            if stars > len(star_costs): continue
            
            item_type = reward_data[2][1]
            item_id = reward_data[2][2]
            item_quantity = reward_data[2][3]
            if item_type == 2:
                item_data = item_srcs[item_id]
            elif item_type == 12:
                item_data = world_item_srcs[item_id]
            item_name = item_data['name']
            if desired_item in item_name:
                cost, product = star_costs[stars-1]
                total_quantity += item_quantity
                unit_cost = cost / total_quantity  
                rows.append((chapter_id, chapter_name, stars, corruption, total_quantity, unit_cost, product))
                
result = '{| class = "wikitable sortable"\n'
result += '! ID !! Zone !! Star level !! Corruption !! Qty !! Est. unit cost !! Target type\n'
for row in rows:
    result += '|-\n'
    result += '| %d || %s || %d || %d || %d || %d || %s \n' % row

result += '|}\n'

print(result)
