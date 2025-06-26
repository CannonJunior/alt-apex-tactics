#!/usr/bin/env uv run
"""
Apex ECS Demo v1 - Minimal Starting Point

This is an exact copy of apex-tactics.py to start with.
We'll gradually replace components with ECS while preserving input functionality.
"""

from ursina import *
from enum import Enum
import random
import math

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
        self.hp = max(0, self.hp - damage)
        if self.hp <= 0:
            self.alive = False
            print(f"{self.name} has been defeated!")

class TacticalGrid:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.units = {}  # Dictionary mapping (x, y) to Unit objects
        
    def place_unit(self, unit, x, y):
        if self.is_valid_position(x, y) and (x, y) not in self.units:
            # Remove unit from old position if it exists
            old_pos = None
            for pos, u in self.units.items():
                if u == unit:
                    old_pos = pos
                    break
            if old_pos:
                del self.units[old_pos]
            
            # Place unit at new position
            self.units[(x, y)] = unit
            unit.x, unit.y = x, y
            return True
        return False
        
    def move_unit(self, unit, new_x, new_y):
        if (unit.x, unit.y) in self.units and self.units[(unit.x, unit.y)] == unit:
            distance = abs(new_x - unit.x) + abs(new_y - unit.y)
            if distance <= unit.current_move_points and self.is_valid_position(new_x, new_y) and (new_x, new_y) not in self.units:
                # Move the unit
                del self.units[(unit.x, unit.y)]
                self.units[(new_x, new_y)] = unit
                unit.x, unit.y = new_x, new_y
                unit.current_move_points -= distance
                return True
        return False
        
    def is_valid_position(self, x, y):
        return 0 <= x < self.width and 0 <= y < self.height
        
    def get_unit_at(self, x, y):
        return self.units.get((x, y))

class CameraController:
    def __init__(self, grid_width=8, grid_height=8):
        self.grid_center = Vec3(grid_width/2 - 0.5, 0, grid_height/2 - 0.5)
        self.camera_target = Vec3(self.grid_center.x, self.grid_center.y, self.grid_center.z)
        self.camera_distance = 8
        self.camera_angle_x = 30
        self.camera_angle_y = 0
        self.camera_mode = 0  # 0: orbit, 1: free, 2: top-down
        self.move_speed = 0.5
        self.rotation_speed = 50
        
    def update_camera(self):
        if self.camera_mode == 0:  # Orbit mode
            rad_y = math.radians(self.camera_angle_y)
            rad_x = math.radians(self.camera_angle_x)
            
            x = self.camera_target.x + self.camera_distance * math.cos(rad_x) * math.sin(rad_y)
            y = self.camera_target.y + self.camera_distance * math.sin(rad_x)
            z = self.camera_target.z + self.camera_distance * math.cos(rad_x) * math.cos(rad_y)
            
            camera.position = (x, y, z)
            camera.look_at(self.camera_target)
        
        elif self.camera_mode == 1:  # Free camera mode
            pass  # Handled by input functions
        
        elif self.camera_mode == 2:  # Top-down mode
            camera.position = (self.camera_target.x, 12, self.camera_target.z)
            camera.rotation = (90, 0, 0)
    
    def handle_input(self, key):
        # Camera mode switching
        if key == '1':
            self.camera_mode = 0
            print("Orbit Camera Mode")
            control_panel.update_camera_mode(0)
        elif key == '2':
            self.camera_mode = 1
            print("Free Camera Mode")
            control_panel.update_camera_mode(1)
        elif key == '3':
            self.camera_mode = 2
            print("Top-down Camera Mode")
            control_panel.update_camera_mode(2)
        
        # Orbit camera controls
        elif self.camera_mode == 0:
            if key == 'scroll up':
                self.camera_distance = max(3, self.camera_distance - 0.5)
            elif key == 'scroll down':
                self.camera_distance = min(15, self.camera_distance + 0.5)
        
        # Free camera controls
        elif self.camera_mode == 1:
            if key == 'w':
                camera.position += camera.forward * self.move_speed
            elif key == 's':
                camera.position -= camera.forward * self.move_speed
            elif key == 'a':
                camera.position -= camera.right * self.move_speed
            elif key == 'd':
                camera.position += camera.right * self.move_speed
            elif key == 'q':
                camera.position += camera.up * self.move_speed
            elif key == 'e':
                camera.position -= camera.up * self.move_speed
        
        # Top-down camera movement
        elif self.camera_mode == 2:
            if key == 'w':
                self.camera_target.z -= self.move_speed
            elif key == 's':
                self.camera_target.z += self.move_speed
            elif key == 'a':
                self.camera_target.x -= self.move_speed
            elif key == 'd':
                self.camera_target.x += self.move_speed
    
    def handle_mouse_input(self):
        if self.camera_mode == 0:  # Orbit mode
            if held_keys['left mouse']:
                self.camera_angle_y += mouse.velocity.x * 50
                self.camera_angle_x = max(-80, min(80, self.camera_angle_x - mouse.velocity.y * 50))
            
            # Keyboard rotation
            rotation_speed = self.rotation_speed * time.dt
            if held_keys['left arrow']:
                self.camera_angle_y -= rotation_speed
            elif held_keys['right arrow']:
                self.camera_angle_y += rotation_speed
            elif held_keys['up arrow']:
                self.camera_angle_x = max(-80, self.camera_angle_x - rotation_speed)
            elif held_keys['down arrow']:
                self.camera_angle_x = min(80, self.camera_angle_x + rotation_speed)
        
        elif self.camera_mode == 1:  # Free camera mode
            if held_keys['left mouse']:
                camera.rotation_y += mouse.velocity.x * 40
                camera.rotation_x -= mouse.velocity.y * 40
                camera.rotation_x = max(-90, min(90, camera.rotation_x))

# Simple Control Panel for basic game info
class ControlPanel:
    def __init__(self):
        # Create a simple window panel for unit info
        self.panel = WindowPanel(
            title='Apex ECS Demo v1 - Input Preserved',
            content=(
                Text('Camera Mode: Orbit', color=color.white),
                Text(''),
                Text('CONTROLS:', color=color.yellow),
                Text('1/2/3 - Camera Modes'),
                Text('WASD - Camera Movement'),
                Text('Mouse - Camera Rotation'),
                Text('Scroll - Zoom (Orbit Mode)'),
                Text(''),
                Text('STATUS: Input system working', color=color.green),
            ),
            popup=False
        )
        
        # Position the panel
        self.panel.x = 0.6
        self.panel.y = 0.3
        self.panel.scale = 0.8
        
        # Store references to update later
        self.camera_mode_text = self.panel.content[0]
        
    def update_camera_mode(self, mode):
        mode_names = ["Orbit", "Free", "Top-down"]
        self.camera_mode_text.text = f'Camera Mode: {mode_names[mode]}'
        self.panel.layout()

# Minimal game initialization
print("=" * 50)
print("APEX ECS DEMO V1 - MINIMAL STARTING POINT")
print("=" * 50)
print("Starting from exact copy of apex-tactics.py")
print("All input functionality should be preserved")
print()
print("Controls:")
print("  1/2/3 - Switch camera modes")
print("  WASD - Move camera")
print("  Mouse drag - Rotate camera")
print("  Mouse scroll - Zoom (orbit mode)")
print("=" * 50)

# Initialize components
control_panel = ControlPanel()
camera_controller = CameraController(8, 8)

def input(key):
    # For now, just delegate everything to camera controller
    # This preserves the exact input behavior from apex-tactics.py
    camera_controller.handle_input(key)

def update():
    # Update camera exactly as in apex-tactics.py
    camera_controller.handle_mouse_input()
    camera_controller.update_camera()

# Set initial camera position
camera_controller.update_camera()

# Add lighting
DirectionalLight(y=10, z=5)

print("Demo initialized - testing input preservation...")
app.run()