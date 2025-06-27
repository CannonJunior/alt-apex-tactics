#!/usr/bin/env uv run
"""
Enhanced ECS Demo

This demo merges the unit selection and panels from run_modular_demo.py
with the complete ECS architecture from apex_ecs_demo_final.py.
All input functionality is preserved exactly.
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

# Import systems
from systems.combat_system import CombatSystem
from game.battle.battle_manager import BattleManager

# Import demo utilities
from demos.unit_converter import UnitConverter

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
        
        # Add selection state
        self.visual_entity.selected = False
        self.visual_entity.game_entity = self.entity  # Link back to ECS entity
        
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
        
        if tactical_movement:
            self.move_points = tactical_movement.max_movement_points
            self.current_move_points = tactical_movement.current_movement_points
        
        if unit_type_comp:
            self.type = unit_type_comp.unit_type
        
        self.alive = True
        self.attack_range = 1
        self.attack_effect_area = 0
    
    def update_visual_position(self):
        """Update visual entity position from ECS transform"""
        transform = self.entity.get_component(Transform)
        if transform and self.visual_entity:
            self.visual_entity.position = (transform.position.x, 0.8, transform.position.z)
            self.x, self.y = transform.position.x, transform.position.z
    
    def set_selected(self, selected: bool):
        """Update selection visual state"""
        if self.visual_entity:
            self.visual_entity.selected = selected
            if selected:
                self.visual_entity.scale = (1.0, 1.8, 1.0)
                self.visual_entity.color = color.white
            else:
                self.visual_entity.scale = (0.8, 1.5, 0.8)
                # Restore original color based on unit type
                unit_type_comp = self.entity.get_component(UnitTypeComponent)
                color_map = {
                    UnitType.HEROMANCER: color.red,
                    UnitType.UBERMENSCH: color.orange,
                    UnitType.SOUL_LINKED: color.cyan,
                    UnitType.REALM_WALKER: color.magenta,
                    UnitType.WARGI: color.green,
                    UnitType.MAGI: color.blue
                }
                self.visual_entity.color = color_map.get(unit_type_comp.unit_type, color.white)

class ECSGrid:
    """ECS-based tactical grid with visual tiles and enhanced selection"""
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.units = {}  # Dictionary mapping (x, y) to ECSUnit objects
        self.tiles = []  # Visual grid tiles
        
        # Create visual grid
        self._create_visual_grid()
        
    def _create_visual_grid(self):
        """Create visual grid tiles with click handlers"""
        for x in range(self.width):
            row = []
            for y in range(self.height):
                tile = Entity(
                    model='cube',
                    color=color.gray,
                    scale=(0.9, 0.1, 0.9),
                    position=(x, 0, y)
                )
                # Add tile properties for selection system
                tile.grid_x = x
                tile.grid_y = y
                tile.default_color = color.gray
                tile.highlighted = False
                
                # No click handler needed - using mouse world coordinates instead
                
                row.append(tile)
            self.tiles.append(row)
    
    # Removed: Old tile click handler - now using mouse world coordinates
    
    def highlight_tile(self, x, y, highlight_color=color.orange):
        """Highlight a specific tile"""
        if 0 <= x < self.width and 0 <= y < self.height:
            tile = self.tiles[x][y]
            tile.color = highlight_color
            tile.highlighted = True
    
    def clear_tile_highlight(self, x, y):
        """Clear highlight from a specific tile"""
        if 0 <= x < self.width and 0 <= y < self.height:
            tile = self.tiles[x][y]
            tile.color = tile.default_color
            tile.highlighted = False
    
    def clear_all_highlights(self):
        """Clear all tile highlights"""
        for x in range(self.width):
            for y in range(self.height):
                self.clear_tile_highlight(x, y)
    
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
            tactical_movement = unit.entity.get_component(TacticalMovementComponent)
            
            if tactical_movement and tactical_movement.can_move(distance) and self.is_valid_position(new_x, new_y) and (new_x, new_y) not in self.units:
                # Move the unit
                del self.units[(unit.x, unit.y)]
                self.units[(new_x, new_y)] = unit
                unit.x, unit.y = new_x, new_y
                
                # Update ECS transform
                transform = unit.entity.get_component(Transform)
                if transform:
                    transform.position = Vector3(new_x, 0, new_y)
                
                # Update tactical movement component
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

class EnhancedECSDemo:
    """
    Enhanced ECS demo with unit selection and panels from run_modular_demo.py
    combined with complete ECS architecture from apex_ecs_demo_final.py
    """
    
    def __init__(self):
        # ECS World
        self.world = World()
        
        # Game systems
        self.battle_manager = BattleManager(self.world)
        self.combat_system = CombatSystem()
        
        # Camera system (preserved from apex_ecs_demo_final.py)
        self.camera_controller = CameraController(8, 8)
        
        # Grid system
        self.grid = ECSGrid(8, 8)
        
        # Game state
        self.units = []  # ECSUnit objects
        self.selected_unit = None  # Currently selected ECSUnit
        self.current_turn = 0
        
        # Path planning state (from apex-tactics.py)
        self.current_mode = None  # "move", "attack", etc.
        self.current_path = []  # List of path positions
        self.path_cursor = None  # Current cursor position in path planning
        
        # UI state
        self.info_panel = None
        self.action_modal = None
        self.movement_modal = None
        
        # Mouse interaction state (from phase4_visual_demo.py)
        self._last_hover_tile = None
        
        # Setup demo
        self._setup_scene()
        self._create_demo_units()
        self._create_ui()
        
        print("=== Enhanced ECS Demo ===")
        print("Complete ECS architecture with enhanced selection and panels")
        print()
        print("Controls:")
        print("  WASD - Move camera (or path planning in move mode)")
        print("  Mouse - Look around (hold right button) + hover highlighting")
        print("  Left click - Click tile to select unit or interact")
        print("  Enter - Confirm movement (in move mode)")
        print("  1/2/3 - Camera modes")
        print("  Space - End turn")
        print("  Tab - Show entity info")
        print("  ESC - Exit")
        print()
        print("Action System:")
        print("  • Mouse hover highlights tiles")
        print("  • Click tile with unit to see action options")
        print("  • Select 'Move' to enter path planning mode")
        print("  • Use WASD to plan movement, Enter to confirm")
        print("  • Select 'Attack' to target enemies")
        print("  • Click empty tile to deselect unit")
        print()
        
    def _setup_scene(self):
        """Setup basic Ursina scene"""
        window.title = "Enhanced ECS Demo - Selection & Panels"
        window.borderless = False
        window.fullscreen = False
        window.exit_button.visible = False
        
        # Basic lighting
        DirectionalLight(y=2, z=-1, rotation=(45, -45, 0))
        AmbientLight(color=color.rgba(100, 100, 100, 100))
        
        # Sky
        Sky()
    
    def _create_demo_units(self):
        """Create demonstration units with ECS"""
        print("Creating enhanced demo units...")
        
        unit_types = list(UnitType)
        names = ["Hero", "Uber", "Soul", "Realm", "War", "Mage", "Alpha", "Beta"]
        positions = [(0, 0), (2, 0), (4, 0), (6, 0), (0, 2), (2, 2), (4, 2), (6, 2)]
        
        for i, name in enumerate(names):
            if i < len(positions):
                unit_type = unit_types[i % len(unit_types)]
                x, y = positions[i]
                
                # Create ECS unit
                unit = ECSUnit(name, unit_type, x, y)
                
                # Do NOT add click handler to visual entity - clicks should go through tiles only
                
                # Place on grid
                if self.grid.place_unit(unit, x, y):
                    self.units.append(unit)
                    print(f"Created ECS unit: {name} ({unit_type.value}) at ({x}, {y})")
        
        print(f"Created {len(self.units)} enhanced ECS units")
    
    # Removed: Units should not have direct click handlers
    # All clicks should go through tiles, which then check for units
    
    def _create_ui(self):
        """Create enhanced UI with selection panels"""
        try:
            from ursina.prefabs.window_panel import WindowPanel
            
            self.info_panel = WindowPanel(
                title='Enhanced ECS Demo - Selection & Panels',
                content=(
                    Text('Enhanced ECS Architecture', color=color.white, scale=1.2),
                    Text(''),
                    Text('Mouse hover + click tiles to select units and see ECS components', color=color.light_gray),
                    Text(''),
                    Text('Enhanced Features:', color=color.yellow),
                    Text('• Mouse world coordinate tile selection'),
                    Text('• Real-time hover highlighting'),
                    Text('• Information panels with live data'),
                    Text('• Movement range visualization'),
                    Text('• Component inspection'),
                    Text('• Grid interaction'),
                    Text(''),
                    Text('Controls: Hover & click tiles, Press Tab for stats', color=color.cyan),
                ),
                popup=False
            )
            
            # Position panel
            self.info_panel.x = 0.65
            self.info_panel.y = 0.35
            self.info_panel.scale = 0.75
            
        except ImportError:
            print("WindowPanel not available - running without UI")
    
    # Removed: _handle_unit_click - Units should not be clicked directly
    # All interaction should go through tile clicks
    
    # Removed: Old _handle_tile_click - now using direct mouse coordinate conversion
    
    def _attempt_move_unit(self, unit: ECSUnit, target_x: int, target_y: int):
        """Attempt to move unit to target position - from run_modular_demo.py"""
        # Calculate distance
        distance = abs(target_x - unit.x) + abs(target_y - unit.y)
        
        # Check movement component
        tactical_movement = unit.entity.get_component(TacticalMovementComponent)
        if not tactical_movement:
            print("Unit has no movement component")
            return
        
        if not tactical_movement.can_move(distance):
            print(f"Unit cannot move {distance} tiles (MP: {tactical_movement.current_movement_points})")
            return
        
        # Move unit on grid
        if self.grid.move_unit(unit, target_x, target_y):
            print(f"Moved {unit.name} to ({target_x}, {target_y})")
            self._update_info_panel()
            self._show_movement_range(unit)  # Update movement range display
    
    def _show_movement_range(self, unit: ECSUnit):
        """Show movement range for selected unit - from run_modular_demo.py"""
        self.grid.clear_all_highlights()
        
        tactical_movement = unit.entity.get_component(TacticalMovementComponent)
        if not tactical_movement:
            return
        
        movement_range = tactical_movement.get_remaining_movement()
        
        # Highlight tiles in movement range
        for x in range(8):
            for y in range(8):
                distance = abs(x - unit.x) + abs(y - unit.y)
                if distance <= movement_range and distance > 0:
                    self.grid.highlight_tile(x, y, color.green)
        
        # Highlight current position
        self.grid.highlight_tile(unit.x, unit.y, color.cyan)
    
    def _update_info_panel(self):
        """Update info panel with selected unit data - enhanced from run_modular_demo.py"""
        if not self.info_panel or not self.selected_unit:
            return
        
        unit = self.selected_unit
        entity = unit.entity
        
        # Get components
        unit_type_comp = entity.get_component(UnitTypeComponent)
        attributes_comp = entity.get_component(AttributeStats)
        tactical_movement_comp = entity.get_component(TacticalMovementComponent)
        attack_comp = entity.get_component(AttackComponent)
        
        # Build enhanced content
        content = [
            Text(f'{unit.name} - {unit_type_comp.unit_type.value.title() if unit_type_comp else "Unknown"}', 
                 color=color.white, scale=1.3),
            Text(f'Entity ID: {entity.id[:8]}...', color=color.light_gray),
            Text(''),
        ]
        
        if unit_type_comp:
            content.extend([
                Text('Unit Type:', color=color.yellow),
                Text(f'  Type: {unit_type_comp.unit_type.value.title()}'),
                Text(f'  Bonuses: {", ".join(unit_type_comp.get_primary_attributes())}'),
                Text(''),
            ])
        
        if attributes_comp:
            content.extend([
                Text('Attributes:', color=color.cyan),
                Text(f'  HP: {attributes_comp.current_hp}/{attributes_comp.max_hp}'),
                Text(f'  MP: {attributes_comp.current_mp}/{attributes_comp.max_mp}'),
                Text(f'  STR: {attributes_comp.strength} | FOR: {attributes_comp.fortitude}'),
                Text(f'  WIS: {attributes_comp.wisdom} | SPD: {attributes_comp.speed}'),
                Text(f'  FIN: {attributes_comp.finesse} | SPI: {attributes_comp.spirit}'),
                Text(''),
            ])
        
        if tactical_movement_comp:
            content.extend([
                Text('Movement:', color=color.orange),
                Text(f'  Movement: {tactical_movement_comp.current_movement_points}/{tactical_movement_comp.max_movement_points}'),
                Text(f'  Actions: {tactical_movement_comp.current_action_points}/{tactical_movement_comp.max_action_points}'),
                Text(f'  Range: {tactical_movement_comp.get_remaining_movement()}'),
                Text(''),
            ])
        
        if attack_comp:
            content.extend([
                Text('Combat:', color=color.red),
                Text(f'  Attack Range: {attack_comp.attack_range}'),
                Text(f'  Area Effect: {attack_comp.area_effect_radius}'),
                Text(''),
            ])
        
        content.extend([
            Text('ECS Info:', color=color.light_gray),
            Text(f'  Components: {len(entity._components)}'),
            Text(f'  Position: ({unit.x}, {unit.y})'),
            Text(''),
            Text('Component breakdown per entity:', color=color.light_gray),
            Text(f'  {[type(comp).__name__ for comp in entity._components.values()]}'),
        ])
        
        # Update panel
        for child in self.info_panel.content:
            destroy(child)
        self.info_panel.content = content
        self.info_panel.layout()
    
    def _end_turn(self):
        """End current turn and refresh units"""
        self.current_turn += 1
        print(f"Turn {self.current_turn} - Refreshing all units")
        
        # Refresh all units
        for unit in self.units:
            tactical_movement = unit.entity.get_component(TacticalMovementComponent)
            if tactical_movement:
                tactical_movement.refresh_for_new_turn()
        
        # Update UI
        self._update_info_panel()
        self.grid.clear_all_highlights()
    
    def _show_ecs_statistics(self):
        """Show ECS system statistics"""
        print("\n=== Enhanced ECS Statistics ===")
        
        # Entity manager stats
        entity_stats = self.world.entity_manager.get_statistics()
        print(f"Entities: {entity_stats['active_entities']}")
        print(f"Components: {entity_stats['component_counts']}")
        
        # Unit stats
        print(f"ECS Units: {len(self.units)}")
        if self.selected_unit:
            print(f"Selected: {self.selected_unit.name}")
        
        # Performance info
        print(f"Grid Size: {self.grid.width}x{self.grid.height}")
        print(f"Turn: {self.current_turn}")
        
        # Component breakdown
        if self.units:
            sample_unit = self.units[0]
            components = [type(comp).__name__ for comp in sample_unit.entity._components.values()]
            print(f"Sample Unit Components: {components}")
        
        print("===========================\n")
    
    def _exit_demo(self):
        """Exit the demo"""
        print("Exiting Enhanced ECS Demo")
        self._show_ecs_statistics()
        application.quit()
    
    # === FUNCTIONS FROM APEX-TACTICS.PY ===
    
    def handle_tile_click(self, x, y):
        """Handle tile click from apex-tactics.py"""
        # Handle attack targeting if in attack mode
        if self.current_mode == "attack" and self.selected_unit:
            self.handle_attack_target_selection(x, y)
            return
            
        # Clear any existing highlights
        self.clear_highlights()
        
        # Check if there's a unit on the clicked tile
        clicked_unit = self.grid.get_unit_at(x, y)
        if clicked_unit:
            # Select the clicked unit and show action modal
            self.selected_unit = clicked_unit
            self.current_path = []  # Reset path when selecting new unit
            self.path_cursor = (clicked_unit.x, clicked_unit.y)  # Start cursor at unit position
            self.current_mode = None  # Reset mode
            self.highlight_selected_unit()
            self.highlight_movement_range()
            self._update_info_panel()
            
            # Show action modal for the selected unit
            self.show_action_modal(clicked_unit)
        else:
            # Clicked on an empty tile - clear selection
            self.selected_unit = None
            self.current_path = []
            self.path_cursor = None
            self.current_mode = None
            self._update_info_panel()
    
    def get_tile_at(self, x, y):
        """Get tile entity at grid position from apex-tactics.py"""
        if 0 <= x < self.grid.width and 0 <= y < self.grid.height:
            return self.grid.tiles[x][y]
        return None
    
    def show_action_modal(self, unit):
        """Show modal with available actions for the selected unit from apex-tactics.py"""
        if not unit:
            return
            
        # Create action buttons dynamically based on unit's action options
        action_buttons = []
        
        def create_action_callback(action_name):
            def action_callback():
                self.handle_action_selection(action_name, unit)
                if self.action_modal:
                    self.action_modal.enabled = False
                    destroy(self.action_modal)
                    self.action_modal = None
            return action_callback
        
        # Create buttons for each action option (use default action options)
        action_options = ["Move", "Attack", "Spirit", "Magic", "Inventory"]
        for action in action_options:
            btn = Button(text=action, color=color.azure)
            btn.on_click = create_action_callback(action)
            action_buttons.append(btn)
        
        # Add cancel button
        cancel_btn = Button(text='Cancel', color=color.red)
        def cancel_action():
            if self.action_modal:
                self.action_modal.enabled = False
                destroy(self.action_modal)
                self.action_modal = None
                
        cancel_btn.on_click = cancel_action
        action_buttons.append(cancel_btn)
        
        # Create content tuple
        content = [Text(f'Select action for {unit.name}:')] + action_buttons
        
        try:
            from ursina.prefabs.window_panel import WindowPanel
            
            # Create modal window
            self.action_modal = WindowPanel(
                title='Unit Actions',
                content=tuple(content),
                popup=True
            )
            
            # Center the window panel
            self.action_modal.y = self.action_modal.panel.scale_y / 2 * self.action_modal.scale_y
            self.action_modal.layout()
        except ImportError:
            print(f"Action selected for {unit.name}: [Modal not available]")
    
    def handle_path_movement(self, direction):
        """Handle path movement and confirmation from apex-tactics.py"""
        if not self.selected_unit or not self.path_cursor:
            return
            
        if direction == 'enter':
            # Show confirmation modal for movement
            self.show_movement_confirmation()
            return
            
        # Calculate new cursor position based on direction
        x, y = self.path_cursor
        if direction == 'w':  # Forward/Up
            new_pos = (x, y - 1)
        elif direction == 's':  # Backward/Down
            new_pos = (x, y + 1)
        elif direction == 'a':  # Right (swapped)
            new_pos = (x + 1, y)
        elif direction == 'd':  # Left (swapped)
            new_pos = (x - 1, y)
        else:
            return
            
        # Check if new position is valid (within movement range)
        if self.is_valid_move_destination(new_pos[0], new_pos[1]):
            # Calculate the distance from unit's starting position to the new position
            total_distance = abs(new_pos[0] - self.selected_unit.x) + abs(new_pos[1] - self.selected_unit.y)
            
            # Get movement component to check movement points
            tactical_movement = self.selected_unit.entity.get_component(TacticalMovementComponent)
            if tactical_movement:
                current_movement = tactical_movement.current_movement_points
            else:
                current_movement = self.selected_unit.current_move_points if hasattr(self.selected_unit, 'current_move_points') else 3
            
            # Don't allow path to exceed movement points
            if total_distance > current_movement:
                return
            
            # Update path cursor
            self.path_cursor = new_pos
            
            # Update current path
            if new_pos not in self.current_path:
                # Add to path if not already in it
                self.current_path.append(new_pos)
            else:
                # If position is already in path, truncate path to that point
                path_index = self.current_path.index(new_pos)
                self.current_path = self.current_path[:path_index + 1]
            
            # Update highlights
            self.update_path_highlights()
    
    def show_movement_confirmation(self):
        """Show modal to confirm unit movement from apex-tactics.py"""
        if not self.path_cursor or not self.selected_unit:
            return
            
        # Create confirmation buttons
        confirm_btn = Button(text='Confirm Move', color=color.green)
        cancel_btn = Button(text='Cancel', color=color.red)
        
        # Set up button callbacks
        def confirm_move():
            self.execute_movement()
            if self.movement_modal:
                self.movement_modal.enabled = False
                destroy(self.movement_modal)
                self.movement_modal = None
                
        def cancel_move():
            if self.movement_modal:
                self.movement_modal.enabled = False
                destroy(self.movement_modal)
                self.movement_modal = None
        
        confirm_btn.on_click = confirm_move
        cancel_btn.on_click = cancel_move
        
        try:
            from ursina.prefabs.window_panel import WindowPanel
            
            # Create modal window
            self.movement_modal = WindowPanel(
                title='Confirm Movement',
                content=(
                    Text(f'Move {self.selected_unit.name} to position ({self.path_cursor[0]}, {self.path_cursor[1]})?'),
                    Text(f'This will use {self.calculate_path_cost()} movement points.'),
                    confirm_btn,
                    cancel_btn
                ),
                popup=True
            )
            
            # Center the window panel
            self.movement_modal.y = self.movement_modal.panel.scale_y / 2 * self.movement_modal.scale_y
            self.movement_modal.layout()
        except ImportError:
            print(f"Movement confirmation for {self.selected_unit.name} to {self.path_cursor}: [Modal not available]")
    
    # === HELPER FUNCTIONS FROM APEX-TACTICS.PY ===
    
    def clear_highlights(self):
        """Clear all tile highlights"""
        self.grid.clear_all_highlights()
        # Clear unit selection highlights
        for unit in self.units:
            if hasattr(unit, 'set_selected'):
                unit.set_selected(False)
    
    def highlight_selected_unit(self):
        """Highlight the selected unit"""
        if self.selected_unit:
            self.selected_unit.set_selected(True)
    
    def highlight_movement_range(self):
        """Highlight all tiles the selected unit can move to"""
        if not self.selected_unit:
            return
            
        for x in range(self.grid.width):
            for y in range(self.grid.height):
                distance = abs(x - self.selected_unit.x) + abs(y - self.selected_unit.y)
                
                # Get movement points from ECS component
                tactical_movement = self.selected_unit.entity.get_component(TacticalMovementComponent)
                if tactical_movement:
                    max_movement = tactical_movement.current_movement_points
                else:
                    max_movement = getattr(self.selected_unit, 'current_move_points', 3)
                
                if distance <= max_movement and self.grid.is_valid_position(x, y):
                    if distance == 0:
                        # Current position - different color
                        self.grid.highlight_tile(x, y, color.white)
                    else:
                        # Valid movement range
                        self.grid.highlight_tile(x, y, color.green)
    
    def is_valid_move_destination(self, x, y):
        """Check if a position is within the unit's movement range"""
        if not self.selected_unit:
            return False
            
        # Calculate total distance from unit's starting position
        total_distance = abs(x - self.selected_unit.x) + abs(y - self.selected_unit.y)
        
        # Get movement points from ECS component
        tactical_movement = self.selected_unit.entity.get_component(TacticalMovementComponent)
        if tactical_movement:
            max_movement = tactical_movement.current_movement_points
        else:
            max_movement = getattr(self.selected_unit, 'current_move_points', 3)
        
        # Check if within movement points and valid grid position
        return (total_distance <= max_movement and 
                0 <= x < self.grid.width and 
                0 <= y < self.grid.height and
                self.grid.get_unit_at(x, y) is None)
    
    def update_path_highlights(self):
        """Update tile highlights to show movement range and current path"""
        # Clear existing highlights
        self.clear_highlights()
        
        if not self.selected_unit:
            return
            
        # Highlight selected unit
        self.highlight_selected_unit()
        
        # Highlight all valid movement tiles in green
        self.highlight_movement_range()
        
        # Highlight current path in blue (override green)
        for pos in self.current_path:
            self.grid.highlight_tile(pos[0], pos[1], color.blue)
        
        # Highlight cursor position in yellow
        if self.path_cursor:
            self.grid.highlight_tile(self.path_cursor[0], self.path_cursor[1], color.yellow)
    
    def calculate_path_cost(self):
        """Calculate the movement cost of the current path"""
        if not self.path_cursor or not self.selected_unit:
            return 0
        return abs(self.path_cursor[0] - self.selected_unit.x) + abs(self.path_cursor[1] - self.selected_unit.y)
    
    def execute_movement(self):
        """Execute the planned movement"""
        if not self.path_cursor or not self.selected_unit:
            return
            
        # Move unit to cursor position
        if self.grid.move_unit(self.selected_unit, self.path_cursor[0], self.path_cursor[1]):
            # Clear selection and path
            self.selected_unit = None
            self.current_path = []
            self.path_cursor = None
            self.clear_highlights()
            self._update_info_panel()
            print(f"Unit moved successfully. Press END TURN when ready.")
    
    def handle_action_selection(self, action_name, unit):
        """Handle the selected action for a unit"""
        print(f"{unit.name} selected action: {action_name}")
        
        if action_name == "Move":
            # Enter movement mode - user can now use WASD to plan movement
            self.current_mode = "move"
            print("Movement mode activated. Use WASD to plan movement, Enter to confirm.")
        elif action_name == "Attack":
            # Enter attack mode
            self.current_mode = "attack"
            self.handle_attack(unit)
        elif action_name == "Spirit":
            print(f"{unit.name} uses spirit action!")
        elif action_name == "Magic":
            print(f"{unit.name} uses magic action!")
        elif action_name == "Inventory":
            print(f"{unit.name} opens inventory!")
    
    def handle_attack_target_selection(self, x, y):
        """Handle attack target selection"""
        target_unit = self.grid.get_unit_at(x, y)
        if target_unit and target_unit != self.selected_unit:
            print(f"{self.selected_unit.name} attacks {target_unit.name}!")
            # Reset mode after attack
            self.current_mode = None
            self.clear_highlights()
        else:
            print("Invalid target for attack")
    
    def handle_attack(self, unit):
        """Handle attack action setup"""
        print(f"{unit.name} is ready to attack. Click on a target unit.")
        # Highlight potential targets
        for x in range(self.grid.width):
            for y in range(self.grid.height):
                target_unit = self.grid.get_unit_at(x, y)
                if target_unit and target_unit != unit:
                    # Highlight potential targets in red
                    self.grid.highlight_tile(x, y, color.red)
    
    def run(self):
        """Start the demo"""
        try:
            # Set initial camera
            self.camera_controller.update_camera()
            
            # Register global input and update functions for Ursina
            self._register_global_functions()
            
            # Run Ursina app
            app.run()
            
        except Exception as e:
            print(f"Demo error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            print("Demo finished")
    
    def _register_global_functions(self):
        """Register global functions that Ursina expects"""
        demo = self
        
        # Create global input function (must be named 'input' in global scope)
        def global_input(key):
            demo._handle_input(key)
        
        # Create global update function  
        def global_update():
            demo._handle_update()
        
        # Register with the main module's globals (where Ursina will look)
        import __main__
        __main__.input = global_input
        __main__.update = global_update
    
    def _handle_input(self, key):
        """Handle input events - EXACT preservation from apex_ecs_demo_final.py with path movement"""
        # Path movement controls (when in move mode)
        if self.current_mode == "move" and self.selected_unit:
            if key in ['w', 'a', 's', 'd', 'enter']:
                self.handle_path_movement(key)
                return  # Don't process camera controls when in move mode
        
        # Camera controls - preserved exactly
        self.camera_controller.handle_input(key)
        
        # Demo controls
        if key == 'escape':
            self._exit_demo()
        elif key == 'space':
            self._end_turn()
        elif key == 'tab':
            self._show_ecs_statistics()
    
    def _handle_update(self):
        """Handle update events - EXACT preservation from apex_ecs_demo_final.py"""
        # Update camera
        self.camera_controller.update_camera()
        self.camera_controller.handle_mouse_input()
        
        # WASD camera movement
        camera_speed = 5
        camera_move = Vec3(0, 0, 0)
        if held_keys['w'] and self.camera_controller.camera_mode != 1:
            camera_move += camera.forward * time.dt * camera_speed
        if held_keys['s'] and self.camera_controller.camera_mode != 1:
            camera_move += camera.back * time.dt * camera_speed
        if held_keys['a'] and self.camera_controller.camera_mode != 1:
            camera_move += camera.left * time.dt * camera_speed
        if held_keys['d'] and self.camera_controller.camera_mode != 1:
            camera_move += camera.right * time.dt * camera_speed
        
        # Only apply movement if not in free camera mode
        if self.camera_controller.camera_mode != 1:
            camera.position += camera_move
        
        # Handle mouse tile interaction (from phase4_visual_demo.py)
        self._handle_mouse_interaction()
    
    def _handle_mouse_interaction(self):
        """Handle mouse interaction with tiles (from phase4_visual_demo.py)"""
        # Handle mouse clicks
        if mouse.left:
            self._handle_mouse_click()
        
        # Handle mouse hover for tile highlighting
        self._handle_mouse_hover()
    
    def _handle_mouse_click(self):
        """Handle mouse click events (from phase4_visual_demo.py)"""
        # Get mouse position in world (from phase4_visual_demo.py)
        if mouse.hovered_entity and hasattr(mouse.hovered_entity, 'on_click'):
            return  # Let entity handle its own click
        
        # Handle tile clicks using world coordinates
        mouse_pos = mouse.world_point
        if mouse_pos:
            # Convert world coordinates to grid coordinates
            grid_x = int(round(mouse_pos.x))
            grid_y = int(round(mouse_pos.z))
            
            # Ensure coordinates are within grid bounds
            if 0 <= grid_x < self.grid.width and 0 <= grid_y < self.grid.height:
                print(f"Mouse clicked at world: {mouse_pos}, grid: ({grid_x}, {grid_y})")
                self.handle_tile_click(grid_x, grid_y)
    
    def _handle_mouse_hover(self):
        """Handle mouse hover for tile highlighting (from phase4_visual_demo.py)"""
        # Get mouse position in world
        mouse_pos = mouse.world_point
        if mouse_pos:
            # Convert world coordinates to grid coordinates
            grid_x = int(round(mouse_pos.x))
            grid_y = int(round(mouse_pos.z))
            
            # Ensure coordinates are within grid bounds
            if 0 <= grid_x < self.grid.width and 0 <= grid_y < self.grid.height:
                # Clear previous hover highlight
                if hasattr(self, '_last_hover_tile'):
                    last_x, last_y = self._last_hover_tile
                    if (last_x, last_y) != (grid_x, grid_y):
                        # Only clear if not currently selected or in path
                        if not self._is_tile_highlighted(last_x, last_y):
                            self.grid.clear_tile_highlight(last_x, last_y)
                
                # Highlight current tile if not already highlighted
                if not self._is_tile_highlighted(grid_x, grid_y):
                    self.grid.highlight_tile(grid_x, grid_y, color.light_gray)
                
                # Store current hover position
                self._last_hover_tile = (grid_x, grid_y)
    
    def _is_tile_highlighted(self, x, y):
        """Check if a tile is already highlighted (from phase4_visual_demo.py)"""
        if 0 <= x < self.grid.width and 0 <= y < self.grid.height:
            tile = self.grid.tiles[x][y]
            return hasattr(tile, 'highlighted') and tile.highlighted
        return False

# Control Panel for enhanced demo
class ControlPanel:
    def __init__(self):
        self.last_camera_mode = None
    
    def update_camera_mode(self, mode):
        self.last_camera_mode = mode
        mode_names = ["Orbit", "Free", "Top-down"]
        print(f"Camera mode: {mode_names[mode]}")

# Initialize demo
print("=" * 60)
print("ENHANCED ECS DEMO")
print("=" * 60)
print("Unit selection and panels from run_modular_demo.py")
print("Complete ECS architecture from apex_ecs_demo_final.py") 
print("ALL input functionality preserved")
print("=" * 60)

# Create control panel and demo
control_panel = ControlPanel()
enhanced_demo = EnhancedECSDemo()

# Add lighting
DirectionalLight(y=10, z=5)

# Run demo
enhanced_demo.run()