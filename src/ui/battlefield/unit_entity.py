from ursina import *
from core.models.unit_types import UnitType

class UnitEntity(Entity):
    def __init__(self, unit):
        colors = {
            UnitType.HEROMANCER: color.orange, 
            UnitType.UBERMENSCH: color.red, 
            UnitType.SOUL_LINKED: color.light_gray,
            UnitType.REALM_WALKER: color.rgb32(128, 0, 128),
            UnitType.WARGI: color.blue, 
            UnitType.MAGI: color.cyan
        }
        super().__init__(
            parent=scene,
            model='cube',
            color=colors[unit.type],
            scale=(0.8, 2.0, 0.8),
            position=(unit.x, 1.0, unit.y)
        )
        self.unit = unit
        self.original_color = colors[unit.type]
        
    def highlight_selected(self):
        self.color = color.white
        
    def unhighlight(self):
        self.color = self.original_color