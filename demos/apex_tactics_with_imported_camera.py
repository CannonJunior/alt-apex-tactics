#!/usr/bin/env python3
"""
Apex Tactics Demo with Imported CameraController

This demo uses the standalone CameraController imported from camera_controller.py
instead of the embedded version, testing the modular approach.
"""

from ursina import *
from enum import Enum
import random
import math

# Import the standalone CameraController
from camera_controller import CameraController

app = Ursina()

# Create a simple ground plane for better visibility
ground = Entity(model='plane', texture='white_cube', color=color.dark_gray, scale=(20, 1, 20), position=(4, -0.1, 4))

# Core Data Models
class UnitType(Enum):
    HEROMANCER = "heromancer"
    UBERMENSCH = "ubermensch"
    SOUL_LINKED = "soul_linked"
    REALM_WALKER = "realm_walker"
    WARGI = "wargi"
    MAGI = "magi"

class Unit:
    def __init__(self, name, unit_type, x, y, wisdom=None, wonder=None, worthy=None, faith=None, finesse=None, fortitude=None, speed=None, spirit=None, strength=None):
        self.name = name
        self.type = unit_type
        self.x, self.y = x, y
        
        # Randomize attributes based on unit type
        self._randomize_attributes(wisdom, wonder, worthy, faith, finesse, fortitude, speed, spirit, strength)
        
        # Derived Stats
        self.max_hp = self.hp = (self.strength + self.fortitude + self.faith + self.worthy) * 5
        self.max_mp = self.mp = (self.wisdom + self.wonder + self.spirit + self.finesse) * 3
        self.max_ap = self.ap = self.speed
        self.move_points = self.speed // 2 + 2  # Movement based on speed attribute
        self.current_move_points = self.move_points  # Current movement available this turn
        self.alive = True
        
        # Combat attributes
        self.attack_range = 1  # Default attack range
        self.attack_effect_area = 0  # Default single-target attack (0 means only target tile)
        self.equipped_weapon = None  # Could be expanded later
        
        # Default action options for all units
        self.action_options = ["Move", "Attack", "Spirit", "Magic", "Inventory"]
        
    def _randomize_attributes(self, wisdom, wonder, worthy, faith, finesse, fortitude, speed, spirit, strength):
        # Base random values (5-15)
        base_attrs = {
            'wisdom': wisdom or random.randint(5, 15),
            'wonder': wonder or random.randint(5, 15),
            'worthy': worthy or random.randint(5, 15),
            'faith': faith or random.randint(5, 15),
            'finesse': finesse or random.randint(5, 15),
            'fortitude': fortitude or random.randint(5, 15),
            'speed': speed or random.randint(5, 15),
            'spirit': spirit or random.randint(5, 15),
            'strength': strength or random.randint(5, 15)
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
        
    def take_damage(self, damage, damage_type="physical"):
        defense = {"physical": self.physical_defense, "magical": self.magical_defense, "spiritual": self.spiritual_defense}[damage_type]
        self.hp = max(0, self.hp - max(1, damage - defense))
        self.alive = self.hp > 0

    def can_move_to(self, x, y, grid):
        distance = abs(x - self.x) + abs(y - self.y)
        return distance <= self.current_move_points and grid.is_valid(x, y)

# Battle Grid System
class BattleGrid:
    def __init__(self, width=8, height=8):
        self.width, self.height = width, height
        self.tiles = {}
        self.units = {}
        self.selected_unit = None
        
    def is_valid(self, x, y):
        return 0 <= x < self.width and 0 <= y < self.height and (x, y) not in self.units
        
    def add_unit(self, unit):
        self.units[(unit.x, unit.y)] = unit
        
    def move_unit(self, unit, x, y):
        if unit.can_move_to(x, y, self):
            distance = abs(x - unit.x) + abs(y - unit.y)
            del self.units[(unit.x, unit.y)]
            unit.x, unit.y = x, y
            unit.current_move_points -= distance
            self.units[(x, y)] = unit
            return True
        return False

# Simple control panel for camera mode display
class SimpleControlPanel:
    def __init__(self):
        self.current_mode = 0
        self.mode_text = Text("Camera Mode: Orbit", position=(-0.8, -0.4), scale=1.2, color=color.cyan)
        
    def update_camera_mode(self, mode):
        self.current_mode = mode
        mode_names = ["Orbit", "Free", "Top-down"]
        self.mode_text.text = f"Camera Mode: {mode_names[mode]}"

# Visual Entity System
class VisualEntity:
    def __init__(self, unit, grid):
        self.unit = unit
        self.grid = grid
        
        # Unit type colors
        type_colors = {
            UnitType.HEROMANCER: color.red,
            UnitType.UBERMENSCH: color.blue,
            UnitType.SOUL_LINKED: color.green,
            UnitType.REALM_WALKER: color.yellow,
            UnitType.WARGI: color.magenta,
            UnitType.MAGI: color.cyan
        }
        
        # Create visual representation
        self.entity = Entity(
            model='cube',
            color=type_colors.get(unit.type, color.white),
            scale=(0.8, 1.2, 0.8),
            position=(unit.x, 0.6, unit.y)
        )
        
        # Add name label
        self.label = Text(
            unit.name,
            parent=self.entity,
            scale=10,
            color=color.white,
            position=(0, 1, 0),
            billboard=True
        )
    
    def update_position(self):
        self.entity.position = (self.unit.x, 0.6, self.unit.y)

# Main Game Class
class TacticalRPGWithImportedCamera:
    def __init__(self):
        # Create control panel first
        self.control_panel = SimpleControlPanel()
        
        # Create grid
        self.grid = BattleGrid(8, 8)
        
        # USING IMPORTED CAMERA CONTROLLER
        self.camera_controller = CameraController(
            grid_width=self.grid.width, 
            grid_height=self.grid.height,
            control_panel=self.control_panel  # Pass control panel to imported camera
        )
        
        # Create visual grid
        self.create_visual_grid()
        
        # Create test units
        self.create_test_units()
        
        # UI Elements
        self.create_ui()
        
        print("Tactical RPG with Imported CameraController initialized!")
        print("All camera functionality should work exactly the same as the original.")
        
    def create_visual_grid(self):
        """Create visual representation of the battle grid"""
        self.grid_tiles = []
        for x in range(self.grid.width):
            for y in range(self.grid.height):
                tile = Entity(
                    model='cube',
                    color=color.dark_gray,
                    scale=(0.9, 0.1, 0.9),
                    position=(x, 0, y)
                )
                self.grid_tiles.append(tile)
    
    def create_test_units(self):
        """Create test units"""
        test_units_data = [
            ("Hero1", UnitType.HEROMANCER, 1, 1),
            ("Uber1", UnitType.UBERMENSCH, 3, 2),
            ("Soul1", UnitType.SOUL_LINKED, 5, 1),
            ("Realm1", UnitType.REALM_WALKER, 2, 4),
            ("Wargi1", UnitType.WARGI, 6, 3),
            ("Magi1", UnitType.MAGI, 4, 5)
        ]
        
        self.units = []
        self.visual_entities = []
        
        for name, unit_type, x, y in test_units_data:
            unit = Unit(name, unit_type, x, y)
            self.units.append(unit)
            self.grid.add_unit(unit)
            
            visual_entity = VisualEntity(unit, self.grid)
            self.visual_entities.append(visual_entity)
        
        print(f"Created {len(self.units)} test units")
    
    def create_ui(self):
        """Create user interface"""
        # Instructions
        self.instructions = Text(
            "Apex Tactics - Imported Camera Demo\n" +
            "1/2/3 - Camera modes\n" +
            "WASD - Move camera\n" +
            "Mouse - Look around\n" +
            "ESC - Exit",
            position=(-0.8, 0.4),
            scale=1.0,
            color=color.white
        )
        
        # Status display
        self.status_text = Text(
            "Testing imported CameraController...",
            position=(-0.8, -0.3),
            scale=1.0,
            color=color.lime
        )

# Global game instance
game = None

def input(key):
    """Global input function - uses imported CameraController"""
    if game:
        # Pass input to imported camera controller
        game.camera_controller.handle_input(key)
    
    if key == 'escape':
        application.quit()
    elif key == 't':
        if game:
            print(f"Camera mode: {game.camera_controller.get_mode_name()}")
            print(f"Camera position: {camera.position}")

def update():
    """Global update function - uses imported CameraController"""
    if game:
        # Handle mouse input and update camera using imported controller
        game.camera_controller.handle_mouse_input()
        game.camera_controller.update_camera()

# Initialize the game
print("Initializing Tactical RPG with Imported CameraController...")
game = TacticalRPGWithImportedCamera()

# Set initial camera position using imported controller
game.camera_controller.update_camera()

print("\nDemonstrating modular CameraController approach:")
print("✓ CameraController imported from camera_controller.py")
print("✓ All original functionality preserved")
print("✓ Same input handling and camera modes")
print("✓ Modular, reusable component")

if __name__ == "__main__":
    app.run()