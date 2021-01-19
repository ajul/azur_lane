import azurlane.common
import azurlane.load_lua
import math

reload_divisor = 150.32
fixed_cooldown = 0.3

bullet_srcs = azurlane.load_lua.load_sharecfg('bullet_template')
barrage_srcs = azurlane.load_lua.load_sharecfg('barrage_template')
weapon_srcs = azurlane.load_lua.load_sharecfg('weapon_property')
equip_stats_srcs = azurlane.load_lua.load_sharecfg('equip_data_statistics')

class Weapon():
    def __init__(self, weapon_id):
        self.weapon = weapon_srcs[weapon_id]
        self.bullet = bullet_srcs[self.weapon['bullet_ID'][1]]
        self.barrage = barrage_srcs[self.weapon['barrage_ID'][1]]
        self.rof = self.weapon['reload_max'] / reload_divisor
        self.shells = self.barrage['primal_repeat'] + 1
        self.salvoes = self.barrage['senior_repeat'] + 1
        self.total_shells = self.shells * self.salvoes
        self.volley_time = (self.total_shells - 1) * self.barrage['delay'] + (self.salvoes - 1) * self.barrage['senior_delay']
        self.armor_modifiers = [x for x in self.bullet['damage_type'].values()]
        
    def dps(self, reload = 100.0):
        reload_mult = math.sqrt(200.0 / (100.0 + reload))
        base_dps = self.weapon['damage'] * 0.01 * self.weapon['corrected'] * self.total_shells / (self.volley_time + reload_mult * self.rof + fixed_cooldown)
        armor_dps = [base_dps * x for x in self.armor_modifiers]
        return base_dps, armor_dps
    
class Equip():
    def __init__(self, equip_id):
        self.equip_stats = equip_stats_srcs[equip_id]
        self.weapon = None
        self.max_weapon = None
        if len(self.equip_stats['weapon_id']) == 1:
            weapon_id = self.equip_stats['weapon_id'][1]
            if weapon_id in weapon_srcs:
                self.weapon = Weapon(weapon_id)
            max_weapon_id = weapon_id
            while max_weapon_id+1 in weapon_srcs and weapon_srcs[max_weapon_id+1]['base'] == weapon_id: max_weapon_id += 1
            self.max_weapon = Weapon(max_weapon_id)
            self.max_level = max_weapon_id - weapon_id
        self.ammo_type = None
        if len(self.equip_stats['ammo_icon']) == 1:
            self.ammo_type = self.equip_stats['ammo_icon'][1]
    
    def to_wiki(self):
        result = '{{Equipment\n'
        result += '<!-- Equipment Information -->\n'
        result += '  | Name=\n'
        result += '  | Image=%s\n' % self.equip_stats['icon']
        result += '  | BaseID=%d\n' % self.equip_stats['id']
        result += '  | Type=%s\n' % azurlane.common.equipment_types[self.equip_stats['type']]
        result += '  | Stars=%d\n' % self.equip_stats['rarity']
        result += '  | Nationality=%s\n' % azurlane.common.nationalities[self.equip_stats['nationality']]
        result += '  | Tech=T%d\n' % self.equip_stats['tech']
        result += '  | BulletPattern=%d\n' % self.equip_stats['id']

        result += '<!-- Alternative Names -->\n'
        result += '  | AltNames=1\n'
        result += '  | CNName=\n'
        result += '  | JPName=\n'
        result += '  | KRName=\n'
        result += '  | ENName=%s\n' % self.equip_stats['name']

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

        if self.weapon:
            result += '<!-- Weapon Stats -->\n'
            result += '  | Damage=%d\n' % self.weapon.weapon['damage']
            result += '  | DamageMax=%d\n' % self.max_weapon.weapon['damage']
            result += '  | RoF=%0.2f\n' % self.weapon.rof
            result += '  | RoFMax=%0.2f\n' % self.max_weapon.rof
            result += '  | Spread=\n'
            result += '  | Angle=\n'
            result += '  | WepRange=\n'
            result += '  | FiringRange=%d\n' % self.weapon.weapon['range']
            result += '  | ProjRange=%d\n' % self.weapon.bullet['range']
            result += '  | Shells=%d\n' % self.weapon.shells
            result += '  | Salvoes=%d\n' % self.weapon.salvoes
            result += '  | Characteristic=%s\n' % self.equip_stats['speciality']
            result += '  | VolleyTime=%0.2f\n' % self.weapon.volley_time
            result += '  | Coef=%d\n' % self.weapon.weapon['corrected']
            result += '  | CoefMax=%d\n' % self.max_weapon.weapon['corrected']
            result += '  | ArmorModL=%d\n' % (int(round(self.weapon.armor_modifiers[0] * 100)))
            result += '  | ArmorModM=%d\n' % (int(round(self.weapon.armor_modifiers[1] * 100)))
            result += '  | ArmorModH=%d\n' % (int(round(self.weapon.armor_modifiers[2] * 100)))
        
        if self.ammo_type:
            result += '  | Ammo=%s\n' % azurlane.common.ammo_types[self.ammo_type]

        result += '  | AAGun1=\n'
        result += '  | AAGun2=\n'
        result += '  | Bombs1=\n'
        result += '  | Bombs2=\n'

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
    
