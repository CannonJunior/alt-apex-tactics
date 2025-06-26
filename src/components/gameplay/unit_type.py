"""
Unit Type Component

Handles unit type definitions and type-specific bonuses for the tactical RPG system.
Based on the unit types from apex-tactics.py.
"""

from typing import Dict, Any
from dataclasses import dataclass
from enum import Enum

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
class UnitTypeComponent(BaseComponent):
    """
    Component defining unit type and associated bonuses.
    
    Implements the same type system as apex-tactics.py with bonuses
    applied to the 9-attribute system.
    """
    
    def __init__(self, unit_type: UnitType):
        super().__init__()
        self.unit_type = unit_type
        self.type_bonuses = self._get_type_bonuses(unit_type)
    
    def _get_type_bonuses(self, unit_type: UnitType) -> Dict[str, int]:
        """
        Get attribute bonuses for unit type.
        
        Matches the type_bonuses system from apex-tactics.py Unit class.
        Each type gets bonuses to 3 specific attributes.
        """
        type_bonus_map = {
            UnitType.HEROMANCER: ['speed', 'strength', 'finesse'],
            UnitType.UBERMENSCH: ['speed', 'strength', 'fortitude'],
            UnitType.SOUL_LINKED: ['faith', 'fortitude', 'worthy'],
            UnitType.REALM_WALKER: ['spirit', 'faith', 'worthy'],
            UnitType.WARGI: ['wisdom', 'wonder', 'spirit'],
            UnitType.MAGI: ['wisdom', 'wonder', 'finesse']
        }
        
        bonuses = {}
        bonus_attributes = type_bonus_map.get(unit_type, [])
        
        # Apply bonus range from apex-tactics.py (3-8 bonus)
        import random
        for attribute in bonus_attributes:
            bonuses[attribute] = random.randint(3, 8)
        
        return bonuses
    
    def get_bonus_for_attribute(self, attribute: str) -> int:
        """
        Get type bonus for specific attribute.
        
        Args:
            attribute: Name of attribute to get bonus for
            
        Returns:
            Bonus value (0 if no bonus for this attribute)
        """
        return self.type_bonuses.get(attribute, 0)
    
    def get_all_bonuses(self) -> Dict[str, int]:
        """Get all type bonuses as dictionary"""
        return self.type_bonuses.copy()
    
    def get_type_description(self) -> str:
        """Get human-readable description of unit type"""
        descriptions = {
            UnitType.HEROMANCER: "Balanced fighter with speed and strength focus",
            UnitType.UBERMENSCH: "Physical powerhouse with speed and fortitude",
            UnitType.SOUL_LINKED: "Spiritual defender with faith and worthy",
            UnitType.REALM_WALKER: "Spiritual warrior with faith and spirit",
            UnitType.WARGI: "Magical specialist with wisdom and wonder",
            UnitType.MAGI: "Pure magic user with wisdom and finesse"
        }
        return descriptions.get(self.unit_type, "Unknown unit type")
    
    def get_primary_attributes(self) -> list:
        """Get list of primary attributes for this unit type"""
        return list(self.type_bonuses.keys())
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize component to dictionary"""
        base_dict = super().to_dict()
        base_dict.update({
            'unit_type': self.unit_type.value,
            'type_bonuses': self.type_bonuses,
            'description': self.get_type_description(),
            'primary_attributes': self.get_primary_attributes()
        })
        return base_dict
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UnitTypeComponent':
        """Deserialize component from dictionary"""
        unit_type = UnitType(data['unit_type'])
        component = cls(unit_type)
        
        # Restore base component data
        component.entity_id = data.get('entity_id')
        component.created_at = data.get('created_at', component.created_at)
        component.component_id = data.get('component_id', component.component_id)
        
        # Override type bonuses if provided (for consistency in saves)
        if 'type_bonuses' in data:
            component.type_bonuses = data['type_bonuses']
        
        return component
    
    def __str__(self) -> str:
        bonus_summary = ", ".join([f"{attr}+{bonus}" for attr, bonus in self.type_bonuses.items()])
        return f"{self.unit_type.value.title()} ({bonus_summary})"
    
    def __repr__(self) -> str:
        return f"UnitTypeComponent({self.unit_type.value}, bonuses={self.type_bonuses})"