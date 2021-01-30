import azurlane.common
import azurlane.load_lua
import math

reload_divisor = 150.32
fixed_cooldown = 0.3

aircraft_srcs = azurlane.load_lua.load_sharecfg('aircraft_template')
bullet_srcs = azurlane.load_lua.load_sharecfg('bullet_template')
barrage_srcs = azurlane.load_lua.load_sharecfg('barrage_template')
weapon_srcs = azurlane.load_lua.load_sharecfg('weapon_property')
equip_stats_srcs = azurlane.load_lua.load_sharecfg('equip_data_statistics')
equip_stats_srcs_cn = azurlane.load_lua.load_sharecfg('equip_data_statistics', server='zh-CN')
equip_stats_srcs_kr = azurlane.load_lua.load_sharecfg('equip_data_statistics', server='ko-KR')
equip_stats_srcs_jp = azurlane.load_lua.load_sharecfg('equip_data_statistics', server='ja-JP')

equip_attribute_translations = {
    'air' : 'Aviation',
    'antiaircraft' : 'AA',
    'antisub' : 'ASW',
    'cannon' : 'Firepower',
    'dodge' : 'Evasion',
    'durability' : 'Health', 
    'hit' : 'Acc',
    'luck' : 'Luck',
    'oxy_max' : 'Oxygen',
    'reload' : 'RoF',
    'speed' : 'Spd',
    'torpedo' : 'Torpedo',
}

equip_attribute_max_translations = {
    'air' : 'AvMax',
    'cannon' : 'FPMax',
    'torpedo' : 'TorpMax',
}

for k, v in equip_attribute_translations.items():
    if k not in equip_attribute_max_translations:
        equip_attribute_max_translations[k] = v + 'Max'

def find_max_id(srcs, base_id):
    max_id = base_id
    while max_id+1 in srcs and 'base' in srcs[max_id+1] and srcs[max_id+1]['base'] == base_id: max_id += 1
    return max_id

class Weapon():
    def __init__(self, weapon_id):
        self.src = weapon_srcs[weapon_id]
        self.bullet = None
        self.armor_modifiers = None
        if len(self.src['bullet_ID']) > 0:
            bullet_id = self.src['bullet_ID'][1]
            if bullet_id in bullet_srcs:
                self.bullet = bullet_srcs[bullet_id]
                self.armor_modifiers = [x for x in self.bullet['damage_type'].values()]
        self.barrage = barrage_srcs[self.src['barrage_ID'][1]]
        self.rof = self.src['reload_max'] / reload_divisor
        self.shells = self.barrage['primal_repeat'] + 1
        self.salvoes = self.barrage['senior_repeat'] + 1
        self.total_shells = self.shells * self.salvoes
        self.volley_time = (self.total_shells - 1) * self.barrage['delay'] + (self.salvoes - 1) * self.barrage['senior_delay']
        if self.barrage['random_angle']:
            self.spread = self.barrage['angle']
        else:
            self.spread = self.barrage['delta_angle'] * self.barrage['primal_repeat']
        
    def dps(self, reload = 100.0):
        reload_mult = math.sqrt(200.0 / (100.0 + reload))
        base_dps = self.src['damage'] * 0.01 * self.src['corrected'] * self.total_shells / (self.volley_time + reload_mult * self.rof + fixed_cooldown)
        armor_dps = [base_dps * x for x in self.armor_modifiers]
        return base_dps, armor_dps

class Aircraft():
    def __init__(self, aircraft_id):
        self.src = aircraft_srcs[aircraft_id]
        self.guns = []
        self.bombs = []
        for weapon_id in self.src['weapon_ID'].values():
            weapon = Weapon(weapon_id)
            if weapon.src['type'] == 4:
                self.guns.append(weapon)
            else:
                self.bombs.append(weapon)
        
    
class Equip():
    def __init__(self, equip_id):
        self.src = equip_stats_srcs[equip_id]
        self.max_src = equip_stats_srcs[find_max_id(equip_stats_srcs, equip_id)]
        self.max_level = self.max_src['id'] - self.src['id']
        self.weapon = None
        self.max_weapon = None
        self.aircraft = None
        self.max_aircraft = None
        self.fighter = None
        self.max_fighter = None
        if len(self.src['weapon_id']) >= 1:
            weapon_id = self.src['weapon_id'][1]
            if weapon_id in weapon_srcs:
                self.weapon = Weapon(weapon_id)
                self.max_weapon = Weapon(find_max_id(weapon_srcs, weapon_id))
            elif weapon_id in aircraft_srcs:
                self.aircraft = Aircraft(weapon_id)
                self.max_aircraft = Aircraft(find_max_id(aircraft_srcs, weapon_id))
                if len(self.src['weapon_id']) >= 2:
                    fighter_id = self.src['weapon_id'][2]
                    self.fighter = Aircraft(fighter_id)
                    self.max_fighter = Aircraft(find_max_id(aircraft_srcs, fighter_id))
            else:
                print('Could not find weapon ID ' + str(weapon_id))
                
        self.ammo_type = None
        if len(self.src['ammo_icon']) == 1:
            self.ammo_type = self.src['ammo_icon'][1]
        self.attributes = []
        for attribute_index in range(1, 4):
            k = 'attribute_%d' % attribute_index
            if k not in self.src: break
            attribute = self.src[k]
            value = int(self.src['value_%d' % attribute_index])
            self.attributes.append((attribute, value))
        
        if equip_id in equip_stats_srcs_cn:
            self.name_cn = equip_stats_srcs_cn[equip_id]['name']
        else:
            self.name_cn = None
        if equip_id in equip_stats_srcs_kr:
            self.name_kr = equip_stats_srcs_kr[equip_id]['name']
        else:
            self.name_kr = None
        if equip_id in equip_stats_srcs_jp:
            self.name_jp = equip_stats_srcs_jp[equip_id]['name']
        else:
            self.name_jp = None
    
    def get_level(self, level):
        return Equip(self.src['id'] + level)
    
    def wiki_value(self, wiki_key):
        if wiki_key == 'ENName':
            return self.src['name']
        elif wiki_key == 'CNName':
            return self.name_cn
        elif wiki_key == 'JPName':
            return self.name_jp
        elif wiki_key == 'KRName':
            return self.name_kr
        else:
            raise NotImplementedError('wiki_value not implemented for', wiki_key)
    
    def to_wiki(self):
        result = '{{Equipment\n'
        result += '<!-- Equipment Information -->\n'
        # result += '  | Name=\n'
        result += '  | Image=%s\n' % self.src['icon']
        result += '  | BaseID=%d\n' % self.src['id']
        result += '  | Type=%s\n' % azurlane.common.equipment_types[self.src['type']]
        result += '  | Stars=%d\n' % self.src['rarity']
        result += '  | Nationality=%s\n' % azurlane.common.nationalities[self.src['nationality']]
        result += '  | Tech=T%d\n' % self.src['tech']
        result += '  | BulletPattern=%d\n' % self.src['id']

        result += '<!-- Alternative Names -->\n'
        result += '  | AltNames=1\n'
        result += '  | CNName=\n'
        result += '  | JPName=\n'
        result += '  | KRName=\n'
        result += '  | ENName=%s\n' % self.src['name']

        """
        result += '<!-- Equipment Stats -->\n'
        result += '  | Health=\n'
        result += '  | HealthMax=\n'
        result += '  | Torpedo=\n'
        result += '  | TorpMax=\n'
        result += '  | Firepower=\n'
        result += '  | FPMax=\n'
        result += '  | Aviation=\n'
        result += '  | AvMax=\n'
        result += '  | Evasion=\n'
        result += '  | EvasionMax=\n'
        result += '  | ASW=\n'
        result += '  | ASWMax=\n'
        result += '  | Oxygen=\n'
        result += '  | OxygenMax=\n'
        result += '  | AA=\n'
        result += '  | AAMax=\n'

        result += '  | Acc=\n'
        result += '  | AccMax=\n'
        result += '  | Spd=\n'
        result += '  | SpdMax=\n'
        result += '  | Luck=\n'
        result += '  | LuckMax=\n'
        """

        if self.weapon:
            result += '<!-- Weapon Stats -->\n'
            result += '  | Damage=%d\n' % self.weapon.src['damage']
            result += '  | DamageMax=%d\n' % self.max_weapon.src['damage']
            result += '  | RoF=%0.2f\n' % self.weapon.rof
            result += '  | RoFMax=%0.2f\n' % self.max_weapon.rof
            result += '  | Spread=\n'
            result += '  | Angle=\n'
            result += '  | WepRange=\n'
            result += '  | FiringRange=%d\n' % self.weapon.src['range']
            if self.weapon.bullet:
                result += '  | ProjRange=%d\n' % self.weapon.bullet['range']
            result += '  | Shells=%d\n' % self.weapon.shells
            result += '  | Salvoes=%d\n' % self.weapon.salvoes
            result += '  | Characteristic=%s\n' % self.src['speciality']
            result += '  | VolleyTime=%0.2f\n' % self.weapon.volley_time
            result += '  | Coef=%d\n' % self.weapon.src['corrected']
            result += '  | CoefMax=%d\n' % self.max_weapon.src['corrected']
            if self.weapon.bullet:
                result += '  | ArmorModL=%d\n' % (int(round(self.weapon.armor_modifiers[0] * 100)))
                result += '  | ArmorModM=%d\n' % (int(round(self.weapon.armor_modifiers[1] * 100)))
                result += '  | ArmorModH=%d\n' % (int(round(self.weapon.armor_modifiers[2] * 100)))
        
        if self.ammo_type:
            result += '  | Ammo=%s\n' % azurlane.common.ammo_types[self.ammo_type]

        if self.aircraft:
            for i, gun in enumerate(self.aircraft.guns):
                result += '  | AAGun%d=%s\n' % (i+1, gun.src['name'])
            for i, bomb in enumerate(self.aircraft.bombs):
                result += '  | Bombs%d=%s\n' % (i+1, bomb.src['name'])

        result += '<!-- Equipment Usability -->\n'
        result += '  | DD=\n'
        result += '  | DDNote=\n'
        result += '  | CL=\n'
        result += '  | CLNote=\n'
        result += '  | CA=\n'
        result += '  | CANote=\n'
        result += '  | CB=\n'
        result += '  | CBNote=\n'
        result += '  | BB=\n'
        result += '  | BBNote=\n'
        result += '  | BC=\n'
        result += '  | BCNote=\n'
        result += '  | BM=\n'
        result += '  | BMNote=\n'
        result += '  | BBV=\n'
        result += '  | BBVNote=\n'
        result += '  | CV=\n'
        result += '  | CVNote=\n'
        result += '  | CVL=\n'
        result += '  | CVLNote=\n'
        result += '  | AR=\n'
        result += '  | ARNote=\n'
        result += '  | SS=\n'
        result += '  | SSNote=\n'
        result += '  | SSV=\n'
        result += '  | SSVNote=\n'

        result += '<!-- Obtainability and Notes -->\n'
        result += '  | DropLocation=\n'
        result += '  | Notes=\n'
        result += '}}\n'
        return result
    
