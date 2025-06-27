"""
Unit Visual Renderer

Handles 3D visual representation of units in the tactical game.
Extracted from apex-tactics.py for better modularity.
"""

from typing import Dict, Any

try:
    from ursina import Entity, color, scene
    URSINA_AVAILABLE = True
except ImportError:
    URSINA_AVAILABLE = False

from components.gameplay.unit_type import UnitType


class UnitEntity(Entity):
    """
    3D visual representation of a unit.
    
    Creates a colored cube entity that represents a unit on the battlefield,
    with highlighting capabilities for selection feedback.
    """
    
    # Unit type to color mapping
    UNIT_COLORS = {
        UnitType.HEROMANCER: 'orange',
        UnitType.UBERMENSCH: 'red',
        UnitType.SOUL_LINKED: 'light_gray',
        UnitType.REALM_WALKER: (128, 0, 128),  # Purple
        UnitType.WARGI: 'blue',
        UnitType.MAGI: 'cyan'
    }
    
    def __init__(self, unit: Any):
        """
        Initialize unit visual entity.
        
        Args:
            unit: Unit object with type, position, and other properties
        """
        if not URSINA_AVAILABLE:
            raise ImportError("Ursina is required for UnitEntity")
        
        # Get color for unit type
        unit_color = self._get_unit_color(unit.type)
        
        super().__init__(
            parent=scene,
            model='cube',
            color=unit_color,
            scale=(0.8, 2.0, 0.8),
            position=(unit.x + 0.5, 1.0, unit.y + 0.5)  # Center units on grid tiles
        )
        
        self.unit = unit
        self.original_color = unit_color
    
    def _get_unit_color(self, unit_type: UnitType):
        """
        Get color for unit type.
        
        Args:
            unit_type: UnitType enum value
            
        Returns:
            Color object for the unit type
        """
        color_value = self.UNIT_COLORS.get(unit_type, 'white')
        
        if isinstance(color_value, tuple):
            # RGB tuple - convert to color
            return color.rgb32(*color_value)
        else:
            # Color name - get from color module
            return getattr(color, color_value, color.white)
    
    def highlight_selected(self):
        """Highlight unit as selected."""
        self.color = color.white
    
    def unhighlight(self):
        """Remove selection highlighting."""
        self.color = self.original_color
    
    def update_position(self, x: int, y: int):
        """
        Update unit position.
        
        Args:
            x, y: New grid coordinates
        """
        self.position = (x + 0.5, 1.0, y + 0.5)
        if hasattr(self.unit, 'x') and hasattr(self.unit, 'y'):
            self.unit.x, self.unit.y = x, y
    
    def set_health_indicator(self, health_percentage: float):
        """
        Update visual health indicator.
        
        Args:
            health_percentage: Health as percentage (0.0 to 1.0)
        """
        if health_percentage > 0.7:
            # Healthy - keep original color
            self.color = self.original_color
        elif health_percentage > 0.3:
            # Wounded - slightly red tint
            self.color = color.orange
        else:
            # Critical - red tint
            self.color = color.dark_red
    
    def cleanup(self):
        """Clean up visual entity."""
        if hasattr(self, 'enabled'):
            self.enabled = False