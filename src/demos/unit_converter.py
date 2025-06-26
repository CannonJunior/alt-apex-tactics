"""
Unit Converter

Converts apex-tactics.py Unit objects to ECS entities with appropriate components.
Provides seamless migration from monolithic to modular architecture.
"""

import random
from typing import Optional
from enum import Enum

# Import ECS framework
from core.ecs.entity import Entity
from core.ecs.world import World
from core.math.vector import Vector3

# Import components
from components.stats.attributes import AttributeStats
from components.combat.attack import AttackComponent
from components.combat.defense import DefenseComponent
from components.movement.movement import MovementComponent
from components.gameplay.unit_type import UnitTypeComponent, UnitType
from components.gameplay.tactical_movement import TacticalMovementComponent

# Apex-tactics Unit class definition (for conversion)
class ApexUnit:
    """
    Simplified representation of apex-tactics.py Unit class for conversion.
    This would normally be imported from the original file.
    """
    def __init__(self, name, unit_type, x, y, **attributes):
        self.name = name
        self.type = unit_type
        self.x, self.y = x, y
        
        # Randomize attributes (matching apex-tactics.py logic)
        self._randomize_attributes(**attributes)
        
        # Derived stats (matching apex-tactics.py calculations)
        self.max_hp = self.hp = (self.strength + self.fortitude + self.faith + self.worthy) * 5
        self.max_mp = self.mp = (self.wisdom + self.wonder + self.spirit + self.finesse) * 3
        self.max_ap = self.ap = self.speed
        self.move_points = self.speed // 2 + 2
        self.current_move_points = self.move_points
        self.alive = True
        
        # Combat attributes
        self.attack_range = 1
        self.attack_effect_area = 0
        self.equipped_weapon = None
        self.action_options = ["Move", "Attack", "Spirit", "Magic", "Inventory"]
    
    def _randomize_attributes(self, **provided_attributes):
        """Randomize attributes with type bonuses (matching apex-tactics.py)"""
        # Base random values (5-15)
        base_attrs = {
            'wisdom': provided_attributes.get('wisdom') or random.randint(5, 15),
            'wonder': provided_attributes.get('wonder') or random.randint(5, 15),
            'worthy': provided_attributes.get('worthy') or random.randint(5, 15),
            'faith': provided_attributes.get('faith') or random.randint(5, 15),
            'finesse': provided_attributes.get('finesse') or random.randint(5, 15),
            'fortitude': provided_attributes.get('fortitude') or random.randint(5, 15),
            'speed': provided_attributes.get('speed') or random.randint(5, 15),
            'spirit': provided_attributes.get('spirit') or random.randint(5, 15),
            'strength': provided_attributes.get('strength') or random.randint(5, 15)
        }
        
        # Type-specific bonuses (+3-8)
        type_bonuses = {
            UnitType.HEROMANCER: ['speed', 'strength', 'finesse'],
            UnitType.UBERMENSCH: ['speed', 'strength', 'fortitude'],
            UnitType.SOUL_LINKED: ['faith', 'fortitude', 'worthy'],
            UnitType.REALM_WALKER: ['spirit', 'faith', 'worthy'],
            UnitType.WARGI: ['wisdom', 'wonder', 'spirit'],
            UnitType.MAGI: ['wisdom', 'wonder', 'finesse']
        }
        
        for attr in type_bonuses[self.type]:
            base_attrs[attr] += random.randint(3, 8)
        
        # Assign to self
        for attr, value in base_attrs.items():
            setattr(self, attr, value)
    
    @property
    def physical_defense(self):
        return (self.speed + self.strength + self.fortitude) // 3
    
    @property
    def magical_defense(self):
        return (self.wisdom + self.wonder + self.finesse) // 3
    
    @property
    def spiritual_defense(self):
        return (self.spirit + self.faith + self.worthy) // 3
    
    @property
    def physical_attack(self):
        return (self.speed + self.strength + self.finesse) // 2
    
    @property
    def magical_attack(self):
        return (self.wisdom + self.wonder + self.spirit) // 2
    
    @property
    def spiritual_attack(self):
        return (self.faith + self.fortitude + self.worthy) // 2

class UnitConverter:
    """
    Converts apex-tactics.py Unit objects to ECS entities.
    
    Provides faithful conversion of all unit data while enabling
    the new modular architecture.
    """
    
    @staticmethod
    def create_apex_unit(name: str, unit_type: UnitType, x: int, y: int, **attributes) -> ApexUnit:
        """
        Create an apex-tactics style unit for conversion.
        
        Args:
            name: Unit name
            unit_type: UnitType enum value
            x, y: Grid position
            **attributes: Override specific attributes
            
        Returns:
            ApexUnit instance
        """
        return ApexUnit(name, unit_type, x, y, **attributes)
    
    @staticmethod
    def apex_unit_to_entity(apex_unit: ApexUnit, world: World, 
                          entity_id: Optional[str] = None) -> Entity:
        """
        Convert apex-tactics Unit to ECS entity.
        
        Args:
            apex_unit: Unit from apex-tactics.py to convert
            world: ECS world to create entity in
            entity_id: Optional specific entity ID
            
        Returns:
            Fully configured ECS entity
        """
        # Create entity
        if entity_id:
            entity = Entity(entity_id)
            world.entity_manager._register_entity(entity)
        else:
            entity = world.entity_manager.create_entity()
        
        # Add unit type component
        unit_type_component = UnitTypeComponent(apex_unit.type)
        entity.add_component(unit_type_component)
        
        # Add attribute stats (enhanced with unit data)
        attributes_component = UnitConverter._create_attributes_component(apex_unit)
        entity.add_component(attributes_component)
        
        # Add position using Transform component
        from core.ecs.component import Transform
        transform = Transform(Vector3(apex_unit.x, 0, apex_unit.y))
        entity.add_component(transform)
        
        # Add combat components
        attack_component = AttackComponent(
            attack_range=apex_unit.attack_range,
            area_effect_radius=apex_unit.attack_effect_area
        )
        entity.add_component(attack_component)
        
        defense_component = DefenseComponent()
        entity.add_component(defense_component)
        
        # Add movement components
        movement_component = MovementComponent(
            movement_range=apex_unit.move_points
        )
        entity.add_component(movement_component)
        
        tactical_movement = TacticalMovementComponent(
            movement_points=apex_unit.move_points,
            movement_range=apex_unit.move_points,
            action_points=apex_unit.max_ap
        )
        # Set current movement points to match apex unit
        tactical_movement.current_movement_points = apex_unit.current_move_points
        entity.add_component(tactical_movement)
        
        return entity
    
    @staticmethod
    def _create_attributes_component(apex_unit: ApexUnit) -> AttributeStats:
        """
        Create AttributeStats component from apex unit data.
        
        Args:
            apex_unit: Source unit data
            
        Returns:
            Configured AttributeStats component
        """
        attributes = AttributeStats(
            strength=apex_unit.strength,
            fortitude=apex_unit.fortitude,
            finesse=apex_unit.finesse,
            wisdom=apex_unit.wisdom,
            wonder=apex_unit.wonder,
            worthy=apex_unit.worthy,
            faith=apex_unit.faith,
            spirit=apex_unit.spirit,
            speed=apex_unit.speed
        )
        
        # Set current HP/MP to match apex unit
        attributes._current_hp = apex_unit.hp
        attributes._current_mp = apex_unit.mp
        
        return attributes
    
    @staticmethod
    def entity_to_apex_unit(entity: Entity) -> Optional[ApexUnit]:
        """
        Convert ECS entity back to apex-tactics Unit (for compatibility).
        
        Args:
            entity: ECS entity to convert
            
        Returns:
            ApexUnit instance or None if conversion fails
        """
        # Get required components
        unit_type_comp = entity.get_component(UnitTypeComponent)
        attributes_comp = entity.get_component(AttributeStats)
        
        if not unit_type_comp or not attributes_comp:
            return None
        
        # Get position
        position = (0, 0)
        from core.ecs.component import Transform
        transform = entity.get_component(Transform)
        if transform:
            position = (int(transform.position.x), int(transform.position.z))
        
        # Create apex unit with extracted data
        apex_unit = ApexUnit(
            name=f"Entity_{entity.id[:8]}",
            unit_type=unit_type_comp.unit_type,
            x=position[0],
            y=position[1],
            strength=attributes_comp.strength,
            fortitude=attributes_comp.fortitude,
            finesse=attributes_comp.finesse,
            wisdom=attributes_comp.wisdom,
            wonder=attributes_comp.wonder,
            worthy=attributes_comp.worthy,
            faith=attributes_comp.faith,
            spirit=attributes_comp.spirit,
            speed=attributes_comp.speed
        )
        
        # Override derived stats to match component
        apex_unit.hp = attributes_comp.current_hp
        apex_unit.mp = attributes_comp.current_mp
        
        return apex_unit
    
    @staticmethod
    def create_demo_army(world: World, army_size: int = 6) -> list:
        """
        Create a demo army for testing.
        
        Args:
            world: ECS world
            army_size: Number of units to create
            
        Returns:
            List of created entities
        """
        demo_units = [
            ("Alexios", UnitType.HEROMANCER, 1, 1),
            ("Kassandra", UnitType.UBERMENSCH, 2, 1),
            ("Barnabas", UnitType.WARGI, 3, 1),
            ("Deimos", UnitType.SOUL_LINKED, 5, 7),
            ("Chrysis", UnitType.MAGI, 6, 7),
            ("Stentor", UnitType.REALM_WALKER, 7, 7),
        ]
        
        entities = []
        for i in range(min(army_size, len(demo_units))):
            name, unit_type, x, y = demo_units[i]
            apex_unit = UnitConverter.create_apex_unit(name, unit_type, x, y)
            entity = UnitConverter.apex_unit_to_entity(apex_unit, world)
            entities.append(entity)
        
        return entities
    
    @staticmethod
    def get_conversion_statistics(entities: list) -> dict:
        """
        Get statistics about converted entities.
        
        Args:
            entities: List of converted entities
            
        Returns:
            Dictionary with conversion statistics
        """
        stats = {
            'total_entities': len(entities),
            'unit_types': {},
            'average_attributes': {},
            'component_counts': {}
        }
        
        if not entities:
            return stats
        
        # Count unit types
        for entity in entities:
            unit_type_comp = entity.get_component(UnitTypeComponent)
            if unit_type_comp:
                type_name = unit_type_comp.unit_type.value
                stats['unit_types'][type_name] = stats['unit_types'].get(type_name, 0) + 1
        
        # Count components
        for entity in entities:
            for component_type in entity.get_component_types():
                type_name = component_type.__name__
                stats['component_counts'][type_name] = stats['component_counts'].get(type_name, 0) + 1
        
        return stats