import azurlane.load_lua
import math

reload_divisor = 150.32
fixed_cooldown = 0.3

bullet_srcs = azurlane.load_lua.load_sharecfg('bullet_template')
barrage_srcs = azurlane.load_lua.load_sharecfg('barrage_template')
weapon_srcs = azurlane.load_lua.load_sharecfg('weapon_property')

class WeaponStats():
    def __init__(self, weapon_id):
        self.weapon = weapon_srcs[weapon_id]
        self.bullet = bullet_srcs[self.weapon['bullet_ID'][1]]
        self.barrage = barrage_srcs[self.weapon['barrage_ID'][1]]
        self.damage = self.weapon['damage']
        self.coef = self.weapon['corrected']
        self.rof = self.weapon['reload_max'] / reload_divisor
        self.shells = self.barrage['primal_repeat'] + 1
        self.salvos = self.barrage['senior_repeat'] + 1
        self.total_shells = self.shells * self.salvos
        self.volley_time = (self.total_shells - 1) * self.barrage['delay'] + (self.salvos - 1) * self.barrage['senior_delay']
        self.proj_range = self.bullet['range']
        self.firing_range = self.weapon['range']
        self.armor_modifiers = [x for x in self.bullet['damage_type'].values()]
        
    def dps(self, reload = 100.0):
        reload_mult = math.sqrt(200.0 / (100.0 + reload))
        base_dps = self.damage * 0.01 * self.coef * self.total_shells / (self.volley_time + reload_mult * self.rof + fixed_cooldown)
        armor_dps = [base_dps * x for x in self.armor_modifiers]
        return base_dps, armor_dps
        
    
