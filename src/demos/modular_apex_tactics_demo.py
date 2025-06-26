#!/usr/bin/env uv run
"""
Modular Apex Tactics Demo

Complete replacement of apex-tactics.py using the ECS architecture.
Demonstrates the same functionality with improved modularity and performance.

Run with: uv run src/demos/modular_apex_tactics_demo.py
"""

import sys
import os
import time
import random
import importlib.util
import math
from typing import List, Dict, Optional

# Add project root to path for imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    from ursina import *
    URSINA_AVAILABLE = True
except ImportError:
    URSINA_AVAILABLE = False
    print("Ursina not available - demo cannot run")
    print("Install with: uv add ursina")
    
    # Create fallback classes and objects for when Ursina is not available
    class MockColor:
        def __init__(self):
            self.red = "red"
            self.orange = "orange"
            self.cyan = "cyan"
            self.magenta = "magenta"
            self.green = "green"
            self.blue = "blue"
            self.white = "white"
            self.gray = "gray"
            self.dark_gray = "dark_gray"
            self.yellow = "yellow"
            self.light_gray = "light_gray"
        
        def rgba(self, r, g, b, a):
            return f"rgba({r},{g},{b},{a})"
    
    class MockVec3:
        def __init__(self, x=0, y=0, z=0):
            self.x, self.y, self.z = x, y, z
    
    class MockEntity:
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)
    
    class MockApp:
        def run(self): pass
        def quit(self): pass
    
    # Mock global objects
    color = MockColor()
    Vec3 = MockVec3
    UrsinaEntity = MockEntity  # Don't name it Entity to avoid conflict with ECS Entity
    camera = MockVec3()
    mouse = type('obj', (object,), {'velocity': MockVec3()})()
    held_keys = {}
    time = type('obj', (object,), {'dt': 0.016})()
    application = MockApp()
    
    # Mock functions
    def Ursina(): return MockApp()
    def DirectionalLight(**kwargs): pass
    def AmbientLight(**kwargs): pass
    def Sky(): pass
    def Text(*args, **kwargs): return MockEntity()
    def Button(**kwargs): return MockEntity()
    def WindowPanel(**kwargs): return MockEntity()
    def destroy(obj): pass
    
    # Create Entity alias for Ursina visual entities
    Entity = MockEntity

# Import ECS framework
from core.ecs.world import World
from core.ecs.entity import Entity as ECSEntity
from core.math.vector import Vector3, Vector2Int
from core.math.grid import TacticalGrid

# Import components
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

# Import CameraController from apex-tactics.py (preserved)
try:
    # Try to import from apex-tactics.py
    apex_tactics_path = '/home/junior/src/apex-tactics'
    if apex_tactics_path not in sys.path:
        sys.path.insert(0, apex_tactics_path)
    
    # Import the apex-tactics file as a module
    import importlib.util
    spec = importlib.util.spec_from_file_location("apex_tactics", 
                                                 os.path.join(apex_tactics_path, "apex-tactics.py"))
    if spec and spec.loader:
        apex_tactics_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(apex_tactics_module)
        ApexCameraController = apex_tactics_module.CameraController
        print("✓ Imported CameraController from apex-tactics.py")
    else:
        raise ImportError("Could not load apex-tactics.py")
        
except (ImportError, Exception) as e:
    print(f"⚠️  Could not import from apex-tactics.py: {e}")
    print("Using fallback camera controller")
    
    # Fallback: create a simple camera controller
    class ApexCameraController:
        def __init__(self, grid_width=8, grid_height=8):
            self.grid_center = Vec3(grid_width/2 - 0.5, 0, grid_height/2 - 0.5)
            self.camera_target = Vec3(self.grid_center.x, self.grid_center.y, self.grid_center.z)
            self.camera_distance = 8
            self.camera_angle_x = 30
            self.camera_angle_y = 0
            self.camera_mode = 0
            self.move_speed = 0.5
            self.rotation_speed = 50
        
        def update_camera(self):
            if self.camera_mode == 0:
                rad_y = math.radians(self.camera_angle_y)
                rad_x = math.radians(self.camera_angle_x)
                
                x = self.camera_target.x + self.camera_distance * math.cos(rad_x) * math.sin(rad_y)
                y = self.camera_target.y + self.camera_distance * math.sin(rad_x)
                z = self.camera_target.z + self.camera_distance * math.cos(rad_x) * math.cos(rad_y)
                
                camera.position = (x, y, z)
                camera.look_at(self.camera_target)
        
        def handle_input(self, key):
            if self.camera_mode == 0:
                if key == 'scroll up':
                    self.camera_distance = max(3, self.camera_distance - 0.5)
                elif key == 'scroll down':
                    self.camera_distance = min(15, self.camera_distance + 0.5)
        
        def handle_mouse_input(self):
            if self.camera_mode == 0 and held_keys['left mouse']:
                self.camera_angle_y += mouse.velocity.x * 50
                self.camera_angle_x = max(-80, min(80, self.camera_angle_x - mouse.velocity.y * 50))

class GridTileEntity(Entity):
    """Visual representation of grid tiles"""
    def __init__(self, x, y, **kwargs):
        super().__init__(
            model='cube',
            color=color.gray,
            scale=(0.9, 0.1, 0.9),
            position=(x, 0, y),
            **kwargs
        )
        self.grid_x = x
        self.grid_y = y
        self.default_color = color.gray
        self.highlighted = False
        
    def highlight(self, highlight_color=None):
        if highlight_color is None:
            highlight_color = color.orange
        self.color = highlight_color
        self.highlighted = True
        
    def clear_highlight(self):
        self.color = self.default_color
        self.highlighted = False

class UnitEntityVisual(Entity):
    """Visual representation of game units"""
    def __init__(self, game_entity: ECSEntity, **kwargs):
        # Get unit info
        unit_type_comp = game_entity.get_component(UnitTypeComponent)
        color_map = {
            UnitType.HEROMANCER: color.red,
            UnitType.UBERMENSCH: color.orange,
            UnitType.SOUL_LINKED: color.cyan,
            UnitType.REALM_WALKER: color.magenta,
            UnitType.WARGI: color.green,
            UnitType.MAGI: color.blue
        }
        unit_color = color_map.get(unit_type_comp.unit_type if unit_type_comp else UnitType.HEROMANCER, color.white)
        
        # Get position
        x, z = 0, 0
        try:
            from core.ecs.component import Transform
            transform = game_entity.get_component(Transform)
            if transform:
                x, z = transform.position.x, transform.position.z
        except:
            # Fallback position lookup
            pass
        
        super().__init__(
            model='cube',
            color=unit_color,
            scale=(0.8, 1.5, 0.8),
            position=(x, 0.8, z),
            **kwargs
        )
        
        self.game_entity = game_entity
        self.selected = False
        
        # Add unit name text
        self.name_text = Text(
            f"Unit_{game_entity.id[:6]}",
            position=(0, 1.2, 0),
            scale=3,
            color=color.white,
            parent=self,
            billboard=True
        )
        
    def update_from_entity(self):
        """Update visual from game entity state"""
        try:
            from core.ecs.component import Transform
            transform = self.game_entity.get_component(Transform)
            if transform:
                self.position = (transform.position.x, 0.8, transform.position.z)
        except:
            pass
        
        # Update selection visual
        if self.selected:
            self.scale = (1.0, 1.8, 1.0)
        else:
            self.scale = (0.8, 1.5, 0.8)

class ModularApexTacticsDemo:
    """
    Complete tactical RPG demo using ECS architecture.
    
    Replaces apex-tactics.py functionality with modular, component-based design.
    """
    
    def __init__(self):
        if not URSINA_AVAILABLE:
            print("Ursina is required for this demo")
            return
        
        # Initialize Ursina
        self.app = Ursina()
        
        # ECS World
        self.world = World()
        
        # Game systems
        self.battle_manager = BattleManager(self.world)
        self.combat_system = CombatSystem()
        
        # Camera system (preserved from apex-tactics.py)
        self.camera_controller = ApexCameraController(8, 8)
        
        # Grid system
        self.tactical_grid = TacticalGrid(8, 8, cell_size=1.0)
        
        # Game state
        self.game_entities: List[ECSEntity] = []
        self.visual_entities: List[UnitEntityVisual] = []
        self.grid_tiles: List[List[GridTileEntity]] = []
        self.selected_entity: Optional[ECSEntity] = None
        self.current_turn = 0
        
        # UI state
        self.info_panel = None
        
        # Setup demo
        self._setup_scene()
        self._create_grid_visual()
        self._create_demo_units()
        self._create_ui()
        # Input will be setup when run() is called
        
        print("=== Modular Apex Tactics Demo ===")
        print("ECS-based tactical RPG replacing apex-tactics.py")
        print()
        print("Controls:")
        print("  WASD - Move camera")
        print("  Mouse - Look around (hold left button)")
        print("  Left click - Select unit")
        print("  Right click - Move unit") 
        print("  1/2/3 - Camera modes")
        print("  Space - End turn")
        print("  Tab - Show entity info")
        print("  ESC - Exit")
        print()
        
        # Show initial statistics
        self._show_ecs_statistics()
    
    def _setup_scene(self):
        """Setup basic Ursina scene"""
        # Set window properties
        window.title = "Modular Apex Tactics - ECS Demo"
        window.borderless = False
        window.fullscreen = False
        window.exit_button.visible = False
        
        # Basic lighting
        DirectionalLight(y=2, z=-1, rotation=(45, -45, 0))
        AmbientLight(color=color.rgba(100, 100, 100, 100))
        
        # Ground plane
        Entity(
            model='plane',
            texture='white_cube',
            color=color.dark_gray,
            scale=(20, 1, 20),
            position=(4, -0.1, 4)
        )
        
        # Sky
        Sky()
    
    def _create_grid_visual(self):
        """Create visual grid representation"""
        self.grid_tiles = []
        for x in range(8):
            row = []
            for y in range(8):
                tile = GridTileEntity(x, y)
                tile.on_click = lambda t=tile: self._handle_tile_click(t)
                row.append(tile)
            self.grid_tiles.append(row)
    
    def _create_demo_units(self):
        """Create demo units using ECS"""
        print("Creating demo units with ECS architecture...")
        
        # Create units using the converter
        self.game_entities = UnitConverter.create_demo_army(self.world, 6)
        
        # Create visual representations
        for game_entity in self.game_entities:
            visual_entity = UnitEntityVisual(game_entity)
            visual_entity.on_click = lambda ge=game_entity: self._handle_unit_click(ge)
            self.visual_entities.append(visual_entity)
        
        print(f"Created {len(self.game_entities)} ECS entities")
        
        # Show unit information
        for i, entity in enumerate(self.game_entities):
            unit_type_comp = entity.get_component(UnitTypeComponent)
            attributes_comp = entity.get_component(AttributeStats)
            if unit_type_comp and attributes_comp:
                print(f"  {i+1}. {unit_type_comp.unit_type.value.title()} - HP: {attributes_comp.current_hp}")
    
    def _create_ui(self):
        """Create demo UI"""
        try:
            from ursina.prefabs.window_panel import WindowPanel
            
            self.info_panel = WindowPanel(
                title='Modular Apex Tactics - ECS Demo',
                content=(
                    Text('ECS Architecture Demo', color=color.white, scale=1.2),
                    Text(''),
                    Text('Select a unit to see ECS components', color=color.light_gray),
                    Text(''),
                    Text('Features:', color=color.yellow),
                    Text('• Component-based entities'),
                    Text('• Modular system architecture'),
                    Text('• Performance optimized'),
                    Text('• Event-driven design'),
                    Text(''),
                    Text('Press Tab for ECS statistics', color=color.cyan),
                ),
                popup=False
            )
            
            # Position panel
            self.info_panel.x = 0.7
            self.info_panel.y = 0.2
            self.info_panel.scale = 0.8
            
        except ImportError:
            print("WindowPanel not available - running without UI")
    
    def _handle_tile_click(self, tile: GridTileEntity):
        """Handle clicking on grid tile"""
        print(f"Clicked tile ({tile.grid_x}, {tile.grid_y})")
        
        # Clear previous highlights
        self._clear_tile_highlights()
        
        # Highlight clicked tile
        tile.highlight(color.yellow)
        
        # If we have a selected unit, try to move it
        if self.selected_entity:
            self._attempt_move_unit(self.selected_entity, tile.grid_x, tile.grid_y)
    
    def _handle_unit_click(self, game_entity: ECSEntity):
        """Handle clicking on unit"""
        print(f"Selected entity: {game_entity.id}")
        
        # Clear previous selection
        if self.selected_entity:
            old_visual = self._get_visual_for_entity(self.selected_entity)
            if old_visual:
                old_visual.selected = False
        
        # Select new entity
        self.selected_entity = game_entity
        visual_entity = self._get_visual_for_entity(game_entity)
        if visual_entity:
            visual_entity.selected = True
        
        # Update UI
        self._update_info_panel()
        
        # Show movement range
        self._show_movement_range(game_entity)
    
    def _attempt_move_unit(self, game_entity: ECSEntity, target_x: int, target_y: int):
        """Attempt to move unit to target position"""
        # Get current position
        current_pos = self._get_entity_position(game_entity)
        if not current_pos:
            return
        
        # Calculate distance
        distance = abs(target_x - current_pos[0]) + abs(target_y - current_pos[1])
        
        # Check movement component
        tactical_movement = game_entity.get_component(TacticalMovementComponent)
        if not tactical_movement:
            print("Unit has no movement component")
            return
        
        if not tactical_movement.can_move(distance):
            print(f"Unit cannot move {distance} tiles (MP: {tactical_movement.current_movement_points})")
            return
        
        # Move unit
        try:
            from core.ecs.component import Transform
            transform = game_entity.get_component(Transform)
            if transform:
                transform.position = Vector3(target_x, 0, target_y)
                tactical_movement.consume_movement(distance)
                print(f"Moved unit to ({target_x}, {target_y})")
                self._update_info_panel()
        except ImportError:
            print("Transform component not available")
    
    def _show_movement_range(self, game_entity: ECSEntity):
        """Show movement range for selected unit"""
        self._clear_tile_highlights()
        
        tactical_movement = game_entity.get_component(TacticalMovementComponent)
        if not tactical_movement:
            return
        
        current_pos = self._get_entity_position(game_entity)
        if not current_pos:
            return
        
        movement_range = tactical_movement.get_remaining_movement()
        
        # Highlight tiles in movement range
        for x in range(8):
            for y in range(8):
                distance = abs(x - current_pos[0]) + abs(y - current_pos[1])
                if distance <= movement_range and distance > 0:
                    self.grid_tiles[x][y].highlight(color.green)
        
        # Highlight current position
        self.grid_tiles[current_pos[0]][current_pos[1]].highlight(color.cyan)
    
    def _get_entity_position(self, game_entity: ECSEntity) -> Optional[tuple]:
        """Get entity grid position"""
        try:
            from core.ecs.component import Transform
            transform = game_entity.get_component(Transform)
            if transform:
                return (int(transform.position.x), int(transform.position.z))
        except ImportError:
            pass
        return None
    
    def _get_visual_for_entity(self, game_entity: ECSEntity) -> Optional[UnitEntityVisual]:
        """Get visual entity for game entity"""
        for visual in self.visual_entities:
            if visual.game_entity == game_entity:
                return visual
        return None
    
    def _clear_tile_highlights(self):
        """Clear all tile highlights"""
        for row in self.grid_tiles:
            for tile in row:
                tile.clear_highlight()
    
    def _update_info_panel(self):
        """Update info panel with selected entity data"""
        if not self.info_panel or not self.selected_entity:
            return
        
        entity = self.selected_entity
        
        # Get components
        unit_type_comp = entity.get_component(UnitTypeComponent)
        attributes_comp = entity.get_component(AttributeStats)
        tactical_movement_comp = entity.get_component(TacticalMovementComponent)
        
        # Build content
        content = [
            Text(f'Entity: {entity.id[:8]}...', color=color.white, scale=1.2),
            Text(''),
        ]
        
        if unit_type_comp:
            content.extend([
                Text(f'Type: {unit_type_comp.unit_type.value.title()}', color=color.yellow),
                Text(f'Bonuses: {", ".join(unit_type_comp.get_primary_attributes())}'),
                Text(''),
            ])
        
        if attributes_comp:
            content.extend([
                Text('Attributes:', color=color.cyan),
                Text(f'HP: {attributes_comp.current_hp}/{attributes_comp.max_hp}'),
                Text(f'MP: {attributes_comp.current_mp}/{attributes_comp.max_mp}'),
                Text(f'STR: {attributes_comp.strength} | FOR: {attributes_comp.fortitude}'),
                Text(f'WIS: {attributes_comp.wisdom} | SPD: {attributes_comp.speed}'),
                Text(''),
            ])
        
        if tactical_movement_comp:
            content.extend([
                Text('Movement:', color=color.orange),
                Text(f'MP: {tactical_movement_comp.current_movement_points}/{tactical_movement_comp.max_movement_points}'),
                Text(f'AP: {tactical_movement_comp.current_action_points}/{tactical_movement_comp.max_action_points}'),
                Text(''),
            ])
        
        content.extend([
            Text('Components:', color=color.light_gray),
            Text(f'{len(entity.get_component_types())} components'),
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
        for entity in self.game_entities:
            tactical_movement = entity.get_component(TacticalMovementComponent)
            if tactical_movement:
                tactical_movement.refresh_for_new_turn()
        
        # Update UI
        self._update_info_panel()
        self._clear_tile_highlights()
    
    def _show_ecs_statistics(self):
        """Show ECS system statistics"""
        print("\n=== ECS Statistics ===")
        
        # Entity manager stats
        entity_stats = self.world.entity_manager.get_statistics()
        print(f"Entities: {entity_stats['active_entities']}")
        print(f"Components: {entity_stats['component_counts']}")
        
        # Conversion stats
        conversion_stats = UnitConverter.get_conversion_statistics(self.game_entities)
        print(f"Unit Types: {conversion_stats['unit_types']}")
        
        # Performance info
        total_entities = len(self.game_entities)
        print(f"Visual Entities: {len(self.visual_entities)}")
        print(f"Grid Tiles: {len(self.grid_tiles) * len(self.grid_tiles[0]) if self.grid_tiles else 0}")
        
        # Component breakdown per entity
        if self.game_entities:
            sample_entity = self.game_entities[0]
            print(f"Sample Entity Components: {[c.__name__ for c in sample_entity.get_component_types()]}")
        
        print("==================\n")
    
    def _exit_demo(self):
        """Exit the demo"""
        print("Exiting Modular Apex Tactics Demo")
        self._show_ecs_statistics()
        application.quit()
    
    def run(self):
        """Start the demo"""
        try:
            # Set initial camera
            self.camera_controller.update_camera()
            
            # Register global input and update functions for Ursina
            self._register_global_functions()
            
            # Run Ursina app
            self.app.run()
            
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
        """Handle input events"""
        # Camera controls
        self.camera_controller.handle_input(key)
        
        # Demo controls
        if key == 'escape':
            self._exit_demo()
        elif key == 'space':
            self._end_turn()
        elif key == 'tab':
            self._show_ecs_statistics()
        elif key == '1':
            self.camera_controller.camera_mode = 0
            print("Camera: Orbit mode")
        elif key == '2':
            self.camera_controller.camera_mode = 1
            print("Camera: Free mode")
        elif key == '3':
            self.camera_controller.camera_mode = 2
            print("Camera: Top-down mode")
    
    def _handle_update(self):
        """Handle update events"""
        # Update camera
        self.camera_controller.update_camera()
        self.camera_controller.handle_mouse_input()
        
        # WASD camera movement (like phase4_visual_demo.py)
        camera_speed = 5
        camera_move = Vec3(0, 0, 0)
        if held_keys['w']:
            camera_move += camera.forward * time.dt * camera_speed
        if held_keys['s']:
            camera_move += camera.back * time.dt * camera_speed
        if held_keys['a']:
            camera_move += camera.left * time.dt * camera_speed
        if held_keys['d']:
            camera_move += camera.right * time.dt * camera_speed
        
        camera.position += camera_move
        
        # Update visual entities from game entities
        for visual_entity in self.visual_entities:
            visual_entity.update_from_entity()

def main():
    """Main demo function"""
    if not URSINA_AVAILABLE:
        print("Cannot run demo without Ursina. Install with:")
        print("uv add ursina")
        return
    
    try:
        demo = ModularApexTacticsDemo()
        demo.run()
    except Exception as e:
        print(f"Failed to start demo: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()