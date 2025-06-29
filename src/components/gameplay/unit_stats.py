"""
Unit Stats Component

Handles unit attributes, combat stats, and equipment effects for the tactical RPG system.
Integrates with the equipment system to provide weapon-based attack ranges and effects.
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
import random

from core.ecs.component import BaseComponent

class UnitType(Enum):
    """Unit types from the original apex-tactics.py system"""
    HEROMANCER = "heromancer"
    UBERMENSCH = "ubermensch"
    SOUL_LINKED = "soul_linked"
    REALM_WALKER = "realm_walker"
    WARGI = "wargi"
    MAGI = "magi"

@dataclass
class UnitStatsComponent(BaseComponent):
    """
    Component defining unit stats, attributes, and combat capabilities.
    
    Implements the same 9-attribute system as apex-tactics.py with equipment integration.
    """
    
    def __init__(self, name: str, unit_type: UnitType, x: int = 0, y: int = 0,
                 wisdom: int = None, wonder: int = None, worthy: int = None, 
                 faith: int = None, finesse: int = None, fortitude: int = None, 
                 speed: int = None, spirit: int = None, strength: int = None):
        super().__init__()
        
        self.name = name
        self.unit_type = unit_type
        self.x, self.y = x, y
        
        # Core attributes (5-15 base + type bonuses)
        self.wisdom = wisdom or random.randint(5, 15)
        self.wonder = wonder or random.randint(5, 15)
        self.worthy = worthy or random.randint(5, 15)
        self.faith = faith or random.randint(5, 15)
        self.finesse = finesse or random.randint(5, 15)
        self.fortitude = fortitude or random.randint(5, 15)
        self.speed = speed or random.randint(5, 15)
        self.spirit = spirit or random.randint(5, 15)
        self.strength = strength or random.randint(5, 15)
        
        # Apply type bonuses
        self._apply_type_bonuses()
        
        # Derived stats
        self.max_hp = self.hp = (self.strength + self.fortitude + self.faith + self.worthy) * 5
        self.max_mp = self.mp = (self.wisdom + self.wonder + self.spirit + self.finesse) * 3
        self.max_ap = self.ap = self.speed
        self.move_points = self.speed // 2 + 2
        self.current_move_points = self.move_points
        self.alive = True
        
        # Combat attributes - base values
        self.base_attack_range = 1
        self.base_attack_effect_area = 0
        
        # Equipment slots
        self.equipped_weapon = None
        self.equipped_armor = None
        self.equipped_accessory = None
        
        # Action options
        self.action_options = ["Move", "Attack", "Spirit", "Magic", "Inventory"]
    
    def _apply_type_bonuses(self):
        """Apply type-specific attribute bonuses (3-8 bonus to 3 attributes)"""
        type_bonus_map = {
            UnitType.HEROMANCER: ['speed', 'strength', 'finesse'],
            UnitType.UBERMENSCH: ['speed', 'strength', 'fortitude'],
            UnitType.SOUL_LINKED: ['faith', 'fortitude', 'worthy'],
            UnitType.REALM_WALKER: ['spirit', 'faith', 'worthy'],
            UnitType.WARGI: ['wisdom', 'wonder', 'spirit'],
            UnitType.MAGI: ['wisdom', 'wonder', 'finesse']
        }
        
        bonus_attributes = type_bonus_map.get(self.unit_type, [])
        for attribute in bonus_attributes:
            bonus = random.randint(3, 8)
            current_value = getattr(self, attribute)
            setattr(self, attribute, current_value + bonus)
    
    def equip_weapon(self, weapon_data: Dict[str, Any]) -> bool:
        """
        Equip a weapon and update combat stats.
        
        Args:
            weapon_data: Weapon data from asset system
            
        Returns:
            True if weapon was equipped successfully
        """
        if weapon_data.get('type') != 'Weapons':
            return False
        
        self.equipped_weapon = weapon_data
        print(f"{self.name} equipped {weapon_data['name']}")
        return True
    
    def equip_armor(self, armor_data: Dict[str, Any]) -> bool:
        """
        Equip armor and update defensive stats.
        
        Args:
            armor_data: Armor data from asset system
            
        Returns:
            True if armor was equipped successfully
        """
        if armor_data.get('type') != 'Armor':
            return False
        
        self.equipped_armor = armor_data
        print(f"{self.name} equipped {armor_data['name']}")
        return True
    
    def equip_accessory(self, accessory_data: Dict[str, Any]) -> bool:
        """
        Equip an accessory and update stats.
        
        Args:
            accessory_data: Accessory data from asset system
            
        Returns:
            True if accessory was equipped successfully
        """
        if accessory_data.get('type') != 'Accessories':
            return False
        
        self.equipped_accessory = accessory_data
        print(f"{self.name} equipped {accessory_data['name']}")
        return True
    
    @property
    def attack_range(self) -> int:
        """Get current attack range including weapon bonuses"""
        base_range = self.base_attack_range
        
        # Add weapon range bonus
        if self.equipped_weapon and 'stats' in self.equipped_weapon:
            weapon_range = self.equipped_weapon['stats'].get('attack_range', 0)
            return max(base_range, weapon_range)  # Use higher value
        
        return base_range
    
    @property
    def attack_effect_area(self) -> int:
        """Get current attack effect area including weapon bonuses"""
        base_area = self.base_attack_effect_area
        
        # Add weapon area bonus
        if self.equipped_weapon and 'stats' in self.equipped_weapon:
            weapon_area = self.equipped_weapon['stats'].get('effect_area', 0)
            return max(base_area, weapon_area)  # Use higher value
        
        return base_area
    
    @property
    def physical_attack(self) -> int:
        """Calculate physical attack including weapon bonuses"""
        base_attack = self.strength + self.finesse + random.randint(1, 6)
        
        # Add weapon attack bonus
        if self.equipped_weapon and 'stats' in self.equipped_weapon:
            weapon_attack = self.equipped_weapon['stats'].get('physical_attack', 0)
            base_attack += weapon_attack
        
        return base_attack
    
    @property
    def magical_attack(self) -> int:
        """Calculate magical attack including weapon bonuses"""
        base_attack = self.wonder + self.spirit + random.randint(1, 6)
        
        # Add weapon magical attack bonus
        if self.equipped_weapon and 'stats' in self.equipped_weapon:
            weapon_attack = self.equipped_weapon['stats'].get('magical_attack', 0)
            base_attack += weapon_attack
        
        return base_attack
    
    @property
    def spiritual_attack(self) -> int:
        """Calculate spiritual attack"""
        return self.faith + self.worthy + random.randint(1, 6)
    
    @property
    def physical_defense(self) -> int:
        """Calculate physical defense including armor bonuses"""
        base_defense = self.fortitude + self.strength // 2
        
        # Add armor defense bonus
        if self.equipped_armor and 'stats' in self.equipped_armor:
            armor_defense = self.equipped_armor['stats'].get('physical_defense', 0)
            base_defense += armor_defense
        
        return base_defense
    
    @property
    def magical_defense(self) -> int:
        """Calculate magical defense including armor bonuses"""
        base_defense = self.spirit + self.wisdom // 2
        
        # Add armor magical defense bonus
        if self.equipped_armor and 'stats' in self.equipped_armor:
            armor_defense = self.equipped_armor['stats'].get('magical_defense', 0)
            base_defense += armor_defense
        
        return base_defense
    
    @property
    def spiritual_defense(self) -> int:
        """Calculate spiritual defense"""
        return self.worthy + self.faith // 2
    
    def get_equipment_summary(self) -> Dict[str, str]:
        """Get summary of equipped items"""
        return {
            'weapon': self.equipped_weapon['name'] if self.equipped_weapon else 'None',
            'armor': self.equipped_armor['name'] if self.equipped_armor else 'None',
            'accessory': self.equipped_accessory['name'] if self.equipped_accessory else 'None'
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize component to dictionary"""
        base_dict = super().to_dict()
        base_dict.update({
            'name': self.name,
            'unit_type': self.unit_type.value,
            'position': (self.x, self.y),
            'attributes': {
                'wisdom': self.wisdom,
                'wonder': self.wonder,
                'worthy': self.worthy,
                'faith': self.faith,
                'finesse': self.finesse,
                'fortitude': self.fortitude,
                'speed': self.speed,
                'spirit': self.spirit,
                'strength': self.strength
            },
            'stats': {
                'hp': self.hp,
                'max_hp': self.max_hp,
                'mp': self.mp,
                'max_mp': self.max_mp,
                'ap': self.ap,
                'max_ap': self.max_ap,
                'move_points': self.move_points,
                'current_move_points': self.current_move_points,
                'alive': self.alive
            },
            'combat': {
                'attack_range': self.attack_range,
                'attack_effect_area': self.attack_effect_area,
                'physical_attack': self.physical_attack,
                'magical_attack': self.magical_attack,
                'spiritual_attack': self.spiritual_attack,
                'physical_defense': self.physical_defense,
                'magical_defense': self.magical_defense,
                'spiritual_defense': self.spiritual_defense
            },
            'equipment': {
                'weapon': self.equipped_weapon,
                'armor': self.equipped_armor,
                'accessory': self.equipped_accessory
            }
        })
        return base_dict
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UnitStatsComponent':
        """Deserialize component from dictionary"""
        unit_type = UnitType(data['unit_type'])
        position = data.get('position', (0, 0))
        attrs = data.get('attributes', {})
        
        component = cls(
            name=data['name'],
            unit_type=unit_type,
            x=position[0],
            y=position[1],
            **attrs
        )
        
        # Restore base component data
        component.entity_id = data.get('entity_id')
        component.created_at = data.get('created_at', component.created_at)
        component.component_id = data.get('component_id', component.component_id)
        
        # Restore stats
        if 'stats' in data:
            stats = data['stats']
            component.hp = stats.get('hp', component.hp)
            component.max_hp = stats.get('max_hp', component.max_hp)
            component.mp = stats.get('mp', component.mp)
            component.max_mp = stats.get('max_mp', component.max_mp)
            component.ap = stats.get('ap', component.ap)
            component.max_ap = stats.get('max_ap', component.max_ap)
            component.move_points = stats.get('move_points', component.move_points)
            component.current_move_points = stats.get('current_move_points', component.current_move_points)
            component.alive = stats.get('alive', component.alive)
        
        # Restore equipment
        if 'equipment' in data:
            equipment = data['equipment']
            component.equipped_weapon = equipment.get('weapon')
            component.equipped_armor = equipment.get('armor')
            component.equipped_accessory = equipment.get('accessory')
        
        return component
    
    def __str__(self) -> str:
        return f"{self.name} ({self.unit_type.value.title()}) [Range: {self.attack_range}, Area: {self.attack_effect_area}]"
    
    def __repr__(self) -> str:
        return f"UnitStatsComponent({self.name}, {self.unit_type.value})"