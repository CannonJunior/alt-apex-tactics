"""
Legacy Unit Wrapper

Provides backwards compatibility for the old Unit class API while using modern ECS components.
Extracted from apex-tactics.py to maintain clean separation.
"""

from typing import Optional

from components.stats.attributes import AttributeStats
from components.gameplay.unit_type import UnitType
from components.movement.movement import MovementComponent
from components.combat.attack import AttackComponent
from components.combat.defense import DefenseComponent
from components.combat.damage import AttackType
from game.factories.unit_factory import create_unit_entity


class Unit:
    """
    Legacy Unit class wrapper around ECS entities for backwards compatibility.
    
    This maintains the exact same API as the original Unit class in apex-tactics.py
    while using the modern ECS component system underneath.
    """
    
    def __init__(self, name: str, unit_type: UnitType, x: int, y: int, 
                 wisdom: Optional[int] = None, wonder: Optional[int] = None, 
                 worthy: Optional[int] = None, faith: Optional[int] = None, 
                 finesse: Optional[int] = None, fortitude: Optional[int] = None, 
                 speed: Optional[int] = None, spirit: Optional[int] = None, 
                 strength: Optional[int] = None):
        """
        Create a legacy unit wrapper around an ECS entity.
        
        Args match exactly those from the original Unit class in apex-tactics.py
        """
        # Create ECS entity using modular factory
        self.entity = create_unit_entity(
            name, unit_type, x, y, wisdom, wonder, worthy, faith, 
            finesse, fortitude, speed, spirit, strength
        )
        
        # Store basic properties
        self.name = name
        self.type = unit_type
        self.x, self.y = x, y
        
        # Get components for quick access
        self.stats = self.entity.get_component(AttributeStats)
        self.movement = self.entity.get_component(MovementComponent)
        self.attack_comp = self.entity.get_component(AttackComponent)
        self.defense_comp = self.entity.get_component(DefenseComponent)
        
        # Legacy compatibility properties
        self.alive = True
        self.action_options = ["Move", "Attack", "Spirit", "Magic", "Inventory"]
    
    # Attribute property accessors (exactly as in original)
    @property
    def strength(self):
        return self.stats.strength
    
    @property
    def fortitude(self):
        return self.stats.fortitude
    
    @property
    def finesse(self):
        return self.stats.finesse
    
    @property
    def wisdom(self):
        return self.stats.wisdom
    
    @property
    def wonder(self):
        return self.stats.wonder
    
    @property
    def worthy(self):
        return self.stats.worthy
    
    @property
    def faith(self):
        return self.stats.faith
    
    @property
    def spirit(self):
        return self.stats.spirit
    
    @property
    def speed(self):
        return self.stats.speed
    
    # Health and resource properties
    @property
    def max_hp(self):
        return self.stats.max_hp
    
    @property
    def hp(self):
        return self.stats.current_hp
    
    @hp.setter
    def hp(self, value):
        self.stats.current_hp = value
    
    @property
    def max_mp(self):
        return self.stats.max_mp
    
    @property
    def mp(self):
        return self.stats.current_mp
    
    @property
    def max_ap(self):
        return self.stats.derived_stats.get('ap', self.speed)
    
    @property
    def ap(self):
        return self.stats.derived_stats.get('current_ap', self.speed)
    
    @ap.setter
    def ap(self, value):
        # Store AP in derived cache - this is a bit of a hack for legacy compatibility
        self.stats.derived_stats['current_ap'] = value
    
    # Movement properties
    @property
    def move_points(self):
        return self.movement.movement_range
    
    @property
    def current_move_points(self):
        return self.movement.remaining_movement
    
    @current_move_points.setter
    def current_move_points(self, value):
        self.movement.remaining_movement = value
    
    # Combat properties
    @property
    def attack_range(self):
        return self.attack_comp.attack_range
    
    @property
    def attack_effect_area(self):
        return int(self.attack_comp.area_effect_radius)
    
    @property
    def physical_defense(self):
        return self.defense_comp.get_defense_value(AttackType.PHYSICAL)
    
    @property
    def magical_defense(self):
        return self.defense_comp.get_defense_value(AttackType.MAGICAL)
    
    @property
    def spiritual_defense(self):
        return self.defense_comp.get_defense_value(AttackType.SPIRITUAL)
    
    @property
    def physical_attack(self):
        return self.stats.derived_stats.get('physical_attack', (self.speed + self.strength + self.finesse) // 2)
    
    @property
    def magical_attack(self):
        return self.stats.derived_stats.get('magical_attack', (self.wisdom + self.wonder + self.spirit) // 2)
    
    @property
    def spiritual_attack(self):
        return self.stats.derived_stats.get('spiritual_attack', (self.faith + self.fortitude + self.worthy) // 2)
    
    # Combat methods
    def take_damage(self, damage: int, damage_type: AttackType = AttackType.PHYSICAL):
        """
        Apply damage to the unit.
        
        Args:
            damage: Amount of damage to apply
            damage_type: Type of damage (physical, magical, spiritual)
        """
        current_hp = self.hp
        defense = self.defense_comp.get_defense_value(damage_type)
        actual_damage = max(1, damage - defense)
        new_hp = max(0, current_hp - actual_damage)
        self.hp = new_hp
        self.alive = new_hp > 0
    
    def can_move_to(self, x: int, y: int, grid) -> bool:
        """
        Check if unit can move to specified position.
        
        Args:
            x, y: Target grid coordinates
            grid: Grid object to check validity
            
        Returns:
            True if move is valid
        """
        distance = abs(x - self.x) + abs(y - self.y)
        return distance <= self.current_move_points and grid.is_valid(x, y)