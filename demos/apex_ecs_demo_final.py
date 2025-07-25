#!/usr/bin/env uv run
"""
Apex ECS Demo Final - Complete ECS Replacement

This is the final demo that completely replaces apex-tactics.py with ECS
while preserving ALL input functionality exactly.
"""

import sys
import os

# Add src to path for ECS imports
script_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(script_dir, 'src')
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from ursina import *
from enum import Enum
import random
import math

# Import ECS components
from core.ecs.world import World
from core.ecs.entity import Entity as ECSEntity
from core.math.vector import Vector3
from components.stats.attributes import AttributeStats
from components.combat.attack import AttackComponent
from components.combat.defense import DefenseComponent  
from components.movement.movement import MovementComponent
from components.gameplay.unit_type import UnitTypeComponent, UnitType
from components.gameplay.tactical_movement import TacticalMovementComponent

app = Ursina()

# Create a simple ground plane for better visibility
ground = Entity(model='plane', texture='white_cube', color=color.dark_gray, scale=(20, 1, 20), position=(4, -0.1, 4))

# ECS World
ecs_world = World()

class Transform:
    """Simple transform component for position"""
    def __init__(self, position=None):
        self.position = position or Vector3(0, 0, 0)

class ECSUnit:
    """
    Complete ECS-based unit replacement with visual representation
    """
    def __init__(self, name, unit_type, x, y, wisdom=None, wonder=None, worthy=None, faith=None, finesse=None, fortitude=None, speed=None, spirit=None, strength=None):
        # Create ECS entity
        self.entity = ecs_world.entity_manager.create_entity()
        self.name = name
        self.x, self.y = x, y
        
        # Add Transform component
        transform = Transform(Vector3(x, 0, y))
        self.entity.add_component(transform)
        
        # Add UnitType component
        unit_type_comp = UnitTypeComponent(unit_type)
        self.entity.add_component(unit_type_comp)
        
        # Create attributes with randomization
        attributes = self._create_attributes(unit_type, wisdom, wonder, worthy, faith, finesse, fortitude, speed, spirit, strength)
        self.entity.add_component(attributes)
        
        # Add tactical movement component
        movement_points = attributes.speed // 2 + 2
        tactical_movement = TacticalMovementComponent(
            movement_points=movement_points,
            movement_range=movement_points,
            action_points=attributes.speed
        )
        self.entity.add_component(tactical_movement)
        
        # Add combat components
        attack_comp = AttackComponent(
            attack_range=1,
            area_effect_radius=0.0
        )
        self.entity.add_component(attack_comp)
        
        defense_comp = DefenseComponent()
        self.entity.add_component(defense_comp)
        
        # Add basic movement component
        movement_comp = MovementComponent()
        self.entity.add_component(movement_comp)
        
        # Create visual representation
        self._create_visual_entity()
        
        # Cache frequently accessed values for compatibility
        self._cache_properties()
        
    def _create_visual_entity(self):
        """Create Ursina visual entity for this unit"""
        # Color based on unit type
        unit_type_comp = self.entity.get_component(UnitTypeComponent)
        color_map = {
            UnitType.HEROMANCER: color.red,
            UnitType.UBERMENSCH: color.orange,
            UnitType.SOUL_LINKED: color.cyan,
            UnitType.REALM_WALKER: color.magenta,
            UnitType.WARGI: color.green,
            UnitType.MAGI: color.blue
        }
        unit_color = color_map.get(unit_type_comp.unit_type, color.white)
        
        # Create visual entity
        self.visual_entity = Entity(
            model='cube',
            color=unit_color,
            scale=(0.8, 1.5, 0.8),
            position=(self.x, 0.8, self.y)
        )
        
        # Add name label
        self.name_text = Text(
            self.name,
            position=(0, 1.2, 0),
            scale=3,
            color=color.white,
            parent=self.visual_entity,
            billboard=True
        )
        
    def _create_attributes(self, unit_type, wisdom, wonder, worthy, faith, finesse, fortitude, speed, spirit, strength):
        """Create attributes component with randomization logic from original"""
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
        
        for attr in type_bonuses[unit_type]:
            base_attrs[attr] += random.randint(3, 8)
        
        # Create AttributeStats component
        return AttributeStats(
            wisdom=base_attrs['wisdom'],
            wonder=base_attrs['wonder'],
            worthy=base_attrs['worthy'],
            faith=base_attrs['faith'],
            finesse=base_attrs['finesse'],
            fortitude=base_attrs['fortitude'],
            speed=base_attrs['speed'],
            spirit=base_attrs['spirit'],
            strength=base_attrs['strength']
        )
    
    def _cache_properties(self):
        """Cache properties for API compatibility with original Unit class"""
        attributes = self.entity.get_component(AttributeStats)
        tactical_movement = self.entity.get_component(TacticalMovementComponent)
        unit_type_comp = self.entity.get_component(UnitTypeComponent)
        
        if attributes:
            self.max_hp = self.hp = attributes.max_hp
            self.max_mp = self.mp = attributes.max_mp
            self.max_ap = self.ap = attributes.speed
            self.wisdom = attributes.wisdom
            self.wonder = attributes.wonder
            self.worthy = attributes.worthy
            self.faith = attributes.faith
            self.finesse = attributes.finesse
            self.fortitude = attributes.fortitude
            self.speed = attributes.speed
            self.spirit = attributes.spirit
            self.strength = attributes.strength
        
        if tactical_movement:
            self.move_points = tactical_movement.max_movement_points
            self.current_move_points = tactical_movement.current_movement_points
        
        if unit_type_comp:
            self.type = unit_type_comp.unit_type
        
        self.alive = True
        self.attack_range = 1
        self.attack_effect_area = 0
        self.equipped_weapon = None
        self.action_options = ["Move", "Attack", "Spirit", "Magic", "Inventory"]
    
    def update_visual_position(self):
        """Update visual entity position from ECS transform"""
        transform = self.entity.get_component(Transform)
        if transform and self.visual_entity:
            self.visual_entity.position = (transform.position.x, 0.8, transform.position.z)
    
    # Properties for API compatibility - exact same as original
    @property
    def physical_defense(self):
        attributes = self.entity.get_component(AttributeStats)
        if attributes:
            return (attributes.speed + attributes.strength + attributes.fortitude) // 3
        return 0
        
    @property
    def magical_defense(self):
        attributes = self.entity.get_component(AttributeStats)
        if attributes:
            return (attributes.wisdom + attributes.wonder + attributes.finesse) // 3
        return 0
        
    @property
    def spiritual_defense(self):
        attributes = self.entity.get_component(AttributeStats)
        if attributes:
            return (attributes.spirit + attributes.faith + attributes.worthy) // 3
        return 0
        
    @property
    def physical_attack(self):
        attributes = self.entity.get_component(AttributeStats)
        if attributes:
            return (attributes.speed + attributes.strength + attributes.finesse) // 2
        return 0
        
    @property
    def magical_attack(self):
        attributes = self.entity.get_component(AttributeStats)
        if attributes:
            return (attributes.wisdom + attributes.wonder + attributes.spirit) // 2
        return 0
        
    @property
    def spiritual_attack(self):
        attributes = self.entity.get_component(AttributeStats)
        if attributes:
            return (attributes.faith + attributes.fortitude + attributes.worthy) // 2
        return 0
        
    def take_damage(self, damage, damage_type="physical"):
        attributes = self.entity.get_component(AttributeStats)
        if attributes:
            attributes.current_hp = max(0, attributes.current_hp - damage)
            self.hp = attributes.current_hp  # Update cache
            if attributes.current_hp <= 0:
                self.alive = False
                print(f"{self.name} has been defeated!")
                if self.visual_entity:
                    destroy(self.visual_entity)

class ECSGrid:
    """ECS-based tactical grid with visual tiles"""
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.units = {}  # Dictionary mapping (x, y) to ECSUnit objects
        self.tiles = []  # Visual grid tiles
        
        # Create visual grid
        self._create_visual_grid()
        
    def _create_visual_grid(self):
        """Create visual grid tiles"""
        for x in range(self.width):
            row = []
            for y in range(self.height):
                tile = Entity(
                    model='cube',
                    color=color.gray,
                    scale=(0.9, 0.1, 0.9),
                    position=(x, 0, y)
                )
                row.append(tile)
            self.tiles.append(row)
        
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
            
            # Update ECS transform
            transform = unit.entity.get_component(Transform)
            if transform:
                transform.position = Vector3(x, 0, y)
            
            # Update visual position
            unit.update_visual_position()
            
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
                
                # Update ECS transform
                transform = unit.entity.get_component(Transform)
                if transform:
                    transform.position = Vector3(new_x, 0, new_y)
                
                # Update tactical movement component
                tactical_movement = unit.entity.get_component(TacticalMovementComponent)
                if tactical_movement:
                    tactical_movement.consume_movement(distance)
                
                # Update visual position
                unit.update_visual_position()
                
                return True
        return False
        
    def is_valid_position(self, x, y):
        return 0 <= x < self.width and 0 <= y < self.height
        
    def get_unit_at(self, x, y):
        return self.units.get((x, y))

# CRITICAL: CameraController remains EXACTLY the same to preserve input
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

# Enhanced Control Panel showing ECS information
class ControlPanel:
    def __init__(self):
        # Create comprehensive control panel
        self.panel = WindowPanel(
            title='Apex ECS Demo Final - Complete ECS Replacement',
            content=(
                Text('Camera Mode: Orbit', color=color.white),
                Text(''),
                Text('CONTROLS:', color=color.yellow),
                Text('1/2/3 - Camera Modes'),
                Text('WASD - Camera Movement'),
                Text('Mouse - Camera Rotation'),
                Text('Scroll - Zoom (Orbit Mode)'),
                Text(''),
                Text('ARCHITECTURE:', color=color.cyan),
                Text('✓ Input System: Preserved'),
                Text('✓ Units: ECS Components'),
                Text('✓ Grid: ECS-based'),
                Text('✓ Visuals: ECS-driven'),
                Text(''),
                Text('STATUS: Full ECS Demo', color=color.green),
            ),
            popup=False
        )
        
        # Position the panel
        self.panel.x = 0.65
        self.panel.y = 0.35
        self.panel.scale = 0.75
        
        # Store references to update later
        self.camera_mode_text = self.panel.content[0]
        
    def update_camera_mode(self, mode):
        mode_names = ["Orbit", "Free", "Top-down"]
        self.camera_mode_text.text = f'Camera Mode: {mode_names[mode]}'
        self.panel.layout()

# Create demonstration units and setup
def create_full_demo_army():
    """Create a full army demonstration with ECS units on grid"""
    grid = ECSGrid(8, 8)
    units = []
    
    unit_types = list(UnitType)
    names = ["Hero", "Uber", "Soul", "Realm", "War", "Mage", "Alpha", "Beta"]
    
    for i, name in enumerate(names):
        unit_type = unit_types[i % len(unit_types)]
        x, y = (i % 4) * 2, (i // 4) * 3
        
        # Ensure position is valid
        if grid.is_valid_position(x, y):
            unit = ECSUnit(name, unit_type, x, y)
            if grid.place_unit(unit, x, y):
                units.append(unit)
                print(f"Created ECS unit: {name} ({unit_type.value}) at ({x}, {y})")
                print(f"  Stats: HP={unit.hp}, MP={unit.mp}, Speed={unit.speed}")
    
    return grid, units

# Game initialization
print("=" * 60)
print("APEX ECS DEMO FINAL - COMPLETE ECS REPLACEMENT")
print("=" * 60)
print("Full replacement of apex-tactics.py with ECS architecture")
print("ALL input functionality preserved exactly")
print()
print("Features:")
print("  ✓ ECS-based units with visual representation")
print("  ✓ Component composition architecture")
print("  ✓ Visual grid with positioning")
print("  ✓ Preserved camera controller and input system")
print()
print("Controls:")
print("  1/2/3 - Switch camera modes")
print("  WASD - Move camera")
print("  Mouse drag - Rotate camera")
print("  Mouse scroll - Zoom (orbit mode)")
print("=" * 60)

# Initialize all systems
control_panel = ControlPanel()
camera_controller = CameraController(8, 8)

# Create the full demonstration
demo_grid, demo_units = create_full_demo_army()
print(f"\nCreated {len(demo_units)} ECS units on tactical grid")

# Show comprehensive ECS statistics
entity_count = len(ecs_world.entity_manager._entities)
print(f"ECS World: {entity_count} entities")

# Show component statistics for first unit
if demo_units:
    sample_unit = demo_units[0]
    components = [type(comp).__name__ for comp in sample_unit.entity._components.values()]
    print(f"Sample unit components: {components}")

# CRITICAL: Input functions remain EXACTLY the same to preserve ALL functionality
def input(key):
    # This must remain exactly as in apex-tactics.py to preserve input behavior
    camera_controller.handle_input(key)

def update():
    # This must remain exactly as in apex-tactics.py to preserve camera behavior
    camera_controller.handle_mouse_input()
    camera_controller.update_camera()

# Set initial camera position
camera_controller.update_camera()

# Add lighting
DirectionalLight(y=10, z=5)

print("\nFinal demo initialized successfully!")
print("Input system preserved, ECS architecture complete.")
print("=" * 60)

app.run()