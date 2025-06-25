#!/usr/bin/env python3
"""
Phase 4 Visual Systems Demo

Interactive Ursina demonstration of all visual systems:
- Real-time tile highlighting
- Modal inventory interface
- Combat animation framework
- Combat interface
"""

import sys
import os
import time
import random
from typing import List, Dict, Any

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    from ursina import *
    from ursina.prefabs.first_person_controller import FirstPersonController
    URSINA_AVAILABLE = True
except ImportError:
    print("Ursina is not available. Please install Ursina to run this demo:")
    print("pip install ursina")
    sys.exit(1)

from core.ecs.entity import Entity as GameEntity
from core.ecs.component import Transform
from core.ecs.world import World
from core.math.vector import Vector3, Vector2Int
from core.math.grid import TacticalGrid
from core.math.pathfinding import AStarPathfinder
from components.stats.attributes import AttributeStats
from components.combat.attack import AttackComponent
from components.combat.damage import DamageComponent
from components.combat.defense import DefenseComponent
from components.movement.movement import MovementComponent

from ui.visual.grid_visualizer import GridVisualizer, HighlightType
from ui.visual.tile_highlighter import TileHighlighter
from ui.visual.combat_animator import CombatAnimator, AnimationType
from ui.interaction import InteractionManager, InteractionMode

# Skip interfaces for now due to import issues
print("Warning: Interface components disabled for demo stability")
InventoryInterface = None
CombatInterface = None
INTERFACES_AVAILABLE = False


class Phase4VisualDemo:
    """Phase 4 Visual Systems Demo"""
    
    def __init__(self):
        # Initialize Ursina
        self.app = Ursina()
        
        # Basic scene setup
        self.setup_scene()
        
        # Game systems
        self.world = World()
        self.grid_system = TacticalGrid(10, 10, cell_size=1.0)
        self.pathfinding = AStarPathfinder(self.grid_system)
        
        # Visual systems
        self.grid_visualizer = GridVisualizer(self.grid_system, self.pathfinding)
        self.tile_highlighter = TileHighlighter(self.grid_visualizer, tile_size=1.0)
        self.combat_animator = CombatAnimator(tile_size=1.0)
        
        # Enhanced interaction system
        self.interaction_manager = InteractionManager(
            self.grid_system, 
            self.pathfinding, 
            self.grid_visualizer
        )
        
        # UI systems (optional if not available)
        if INTERFACES_AVAILABLE:
            self.inventory_interface = InventoryInterface()
            self.combat_interface = CombatInterface()
        else:
            self.inventory_interface = None
            self.combat_interface = None
            print("Running demo without full interface components")
        
        # Demo state
        self.demo_units: List[GameEntity] = []
        self.unit_entities: Dict[int, Entity] = {}  # game_entity_id -> visual_entity
        self.selected_unit: GameEntity = None
        self.demo_mode = "highlighting"
        
        # Create demo content
        self.setup_demo_battlefield()
        
        # Setup interaction event handlers
        self.setup_interaction_events()
        
        # Input handling
        self.setup_input()
        
        print("=== Phase 4 Enhanced Visual Systems Demo ===")
        print("Controls:")
        print("  WASD - Move camera")
        print("  Mouse - Look around") 
        print("  1 - Tile Highlighting Demo")
        print("  2 - Combat Animation Demo")
        print("  3 - Inventory Interface Demo")
        print("  4 - Combat Interface Demo")
        print("  5 - Integrated Demo")
        print("  6 - Enhanced Interaction Demo")
        print("Enhanced Interactions:")
        print("  Click on tiles - Enhanced tile selection with feedback")
        print("  Click on units - Unit selection with action modals")
        print("  Right-click - Context menus and unit actions")
        print("  ESC - Cancel current action / Exit")
        print()
    
    def setup_scene(self):
        """Setup basic Ursina scene"""
        # Basic lighting
        light = DirectionalLight()
        light.position = (2, 2, 2)
        light.look_at((0, 0, 0))
        
        # Ground plane
        ground = Entity(
            model='cube',
            color=color.Color(0.3, 0.5, 0.3, 1.0),
            scale=(20, 0.1, 20),
            position=(0, -0.1, 0)
        )
        
        # Grid lines
        self.create_grid_lines()
        
        # Camera setup
        camera.position = (5, 8, 8)
        camera.look_at((5, 0, 5))
        
        # Simple camera controller
        self.camera_controller = Entity()
        self.camera_speed = 5
        
        # Sky
        Sky()
    
    def create_grid_lines(self):
        """Create visual grid lines"""
        grid_size = 10
        line_color = color.Color(0.4, 0.4, 0.4, 0.5)
        
        # Vertical lines
        for x in range(grid_size + 1):
            line = Entity(
                model='cube',
                color=line_color,
                scale=(0.02, 0.01, grid_size),
                position=(x, 0, grid_size / 2)
            )
        
        # Horizontal lines
        for z in range(grid_size + 1):
            line = Entity(
                model='cube',
                color=line_color,
                scale=(grid_size, 0.01, 0.02),
                position=(grid_size / 2, 0, z)
            )
    
    def setup_demo_battlefield(self):
        """Create demo units and battlefield"""
        # Create player units (blue cubes)
        player_positions = [
            Vector2Int(2, 2), Vector2Int(1, 3), Vector2Int(3, 1), Vector2Int(2, 4)
        ]
        
        for i, grid_pos in enumerate(player_positions):
            unit = self.create_demo_unit(grid_pos, f"Player_{i+1}", color.blue)
            self.demo_units.append(unit)
        
        # Create enemy units (red cubes)
        enemy_positions = [
            Vector2Int(7, 7), Vector2Int(8, 6), Vector2Int(6, 8)
        ]
        
        for i, grid_pos in enumerate(enemy_positions):
            unit = self.create_demo_unit(grid_pos, f"Enemy_{i+1}", color.red)
            self.demo_units.append(unit)
        
        # Create neutral units (yellow cubes)
        neutral_positions = [
            Vector2Int(5, 5), Vector2Int(4, 6)
        ]
        
        for i, grid_pos in enumerate(neutral_positions):
            unit = self.create_demo_unit(grid_pos, f"Neutral_{i+1}", color.yellow)
            self.demo_units.append(unit)
    
    def create_demo_unit(self, grid_pos: Vector2Int, name: str, unit_color: Color) -> GameEntity:
        """Create a demo unit with visual representation"""
        # Create game entity
        world_pos = self.grid_system.grid_to_world(grid_pos)
        
        unit = GameEntity()
        unit.add_component(Transform(Vector3(world_pos.x, 0, world_pos.z)))
        unit.add_component(AttributeStats(
            strength=random.randint(8, 15),
            speed=random.randint(8, 12),
            fortitude=random.randint(8, 12),
            wisdom=random.randint(6, 14)
        ))
        unit.add_component(AttackComponent(attack_range=3))
        unit.add_component(DamageComponent(physical_power=random.randint(12, 20)))
        unit.add_component(DefenseComponent(physical_defense=random.randint(8, 15)))
        unit.add_component(MovementComponent(movement_range=random.randint(2, 4)))
        
        # Create visual entity
        visual_entity = Entity(
            model='cube',
            color=unit_color,
            scale=(0.8, 0.8, 0.8),
            position=(world_pos.x, 0.4, world_pos.z)
        )
        
        # Add unit name
        name_text = Text(
            name,
            position=(0, 1, 0),
            scale=5,
            color=color.white,
            parent=visual_entity,
            billboard=True
        )
        
        # Make unit clickable
        visual_entity.on_click = lambda: self.select_unit(unit)
        
        # Store references
        self.unit_entities[unit.id] = visual_entity
        self.combat_animator.register_unit_entity(unit, visual_entity)
        
        # Register unit with interaction manager
        self.interaction_manager.add_unit(unit, grid_pos)
        
        return unit
    
    def setup_interaction_events(self):
        """Setup event handlers for the interaction manager"""
        # Register event callbacks
        self.interaction_manager.register_event_callback('unit_selected', self.on_unit_selected)
        self.interaction_manager.register_event_callback('tile_clicked', self.on_tile_clicked)
        self.interaction_manager.register_event_callback('unit_moved', self.on_unit_moved)
        self.interaction_manager.register_event_callback('action_executed', self.on_action_executed)
        self.interaction_manager.register_event_callback('mode_changed', self.on_mode_changed)
    
    def on_unit_selected(self, unit: GameEntity):
        """Handle unit selection events"""
        self.selected_unit = unit
        print(f"Demo: Unit selected - {unit.id}")
        
        # Update legacy visual systems
        self.tile_highlighter.set_selected_unit(unit)
        if self.combat_interface:
            self.combat_interface.set_selected_unit(unit)
        
        # Update unit highlighting
        self._update_unit_selection_visual()
    
    def on_tile_clicked(self, tile):
        """Handle tile click events"""
        print(f"Demo: Tile clicked - {tile.grid_pos}")
    
    def on_unit_moved(self, move_data):
        """Handle unit movement events"""
        unit = move_data['unit']
        from_pos = move_data['from'] 
        to_pos = move_data['to']
        path = move_data['path']
        
        print(f"Demo: Unit {unit.id} moved from {from_pos} to {to_pos}")
        
        # Update visual entity position
        if unit.id in self.unit_entities:
            visual_entity = self.unit_entities[unit.id]
            world_pos = self.grid_system.grid_to_world(to_pos)
            visual_entity.position = (world_pos.x, 0.4, world_pos.z)
        
        # Trigger movement animation
        if len(path) > 1:
            world_dest = self.grid_system.grid_to_world(to_pos)
            self.combat_animator.queue_movement_animation(
                unit,
                Vector3(world_dest.x, 0, world_dest.z),
                duration=1.5
            )
    
    def on_action_executed(self, action_data):
        """Handle action execution events"""
        action = action_data['action']
        unit = action_data['unit']
        
        print(f"Demo: Action executed - {action} by {unit.id}")
        
        # Trigger appropriate animations based on action
        if action == 'attack':
            target = action_data.get('target')
            if target:
                self.combat_animator.queue_attack_animation(unit, target, delay=0.5)
        elif action == 'defend':
            # Show defend animation or effect
            pass
    
    def on_mode_changed(self, mode_data):
        """Handle interaction mode changes"""
        old_mode = mode_data['old_mode']
        new_mode = mode_data['new_mode']
        
        print(f"Demo: Interaction mode changed - {old_mode.value} -> {new_mode.value}")
    
    def select_unit(self, unit: GameEntity):
        """Select a unit and update visual systems"""
        self.selected_unit = unit
        
        print(f"Selected unit: {unit.id}")
        
        # Update visual systems
        self.tile_highlighter.set_selected_unit(unit)
        if self.combat_interface:
            self.combat_interface.set_selected_unit(unit)
        
        # Update unit highlighting
        self._update_unit_selection_visual()
    
    def _update_unit_selection_visual(self):
        """Update visual indication of selected unit"""
        # Reset all unit scales
        for visual_entity in self.unit_entities.values():
            visual_entity.scale = (0.8, 0.8, 0.8)
        
        # Highlight selected unit
        if self.selected_unit and self.selected_unit.id in self.unit_entities:
            visual_entity = self.unit_entities[self.selected_unit.id]
            visual_entity.scale = (1.0, 1.0, 1.0)
    
    def setup_input(self):
        """Setup input handling"""
        # Demo mode switching
        def input(key):
            if key == '1':
                self.set_demo_mode("highlighting")
            elif key == '2':
                self.set_demo_mode("animation")
            elif key == '3':
                self.set_demo_mode("inventory")
            elif key == '4':
                self.set_demo_mode("combat_ui")
            elif key == '5':
                self.set_demo_mode("integrated")
            elif key == '6':
                self.set_demo_mode("interaction")
            elif key == 'escape':
                application.quit()
            elif key == 'i' and self.selected_unit and self.inventory_interface:
                self.inventory_interface.show(self.selected_unit)
            elif key == 'c' and self.combat_interface:
                if self.combat_interface.is_visible:
                    self.combat_interface.hide()
                else:
                    self.combat_interface.show()
            elif key == 'space':
                self.trigger_demo_action()
        
        # Mouse click handling for tile selection
        def mouse_click():
            # Get mouse position in world
            if mouse.hovered_entity and hasattr(mouse.hovered_entity, 'on_click'):
                return  # Let entity handle its own click
            
            # Handle tile clicks
            mouse_pos = mouse.world_point
            if mouse_pos:
                grid_pos = self.grid_system.world_to_grid(Vector3(mouse_pos.x, 0, mouse_pos.z))
                self.handle_tile_click(grid_pos)
        
        # Update function
        def update():
            # Camera movement
            camera_move = Vec3(0, 0, 0)
            if held_keys['w']:
                camera_move += camera.forward * time.dt * self.camera_speed
            if held_keys['s']:
                camera_move += camera.back * time.dt * self.camera_speed
            if held_keys['a']:
                camera_move += camera.left * time.dt * self.camera_speed
            if held_keys['d']:
                camera_move += camera.right * time.dt * self.camera_speed
            
            camera.position += camera_move
            
            # Update visual systems
            self.tile_highlighter.update(time.dt)
            self.combat_animator.update(time.dt)
            
            # Update interaction manager
            self.interaction_manager.update(time.dt)
            
            # Update interfaces
            if self.inventory_interface and self.inventory_interface.is_visible:
                self.inventory_interface.update(time.dt)
            
            # Demo-specific updates
            self.update_demo_mode()
        
        # Register input handlers
        def input_handler(key):
            input(key)
        
        def mouse_handler():
            if mouse.left:
                mouse_click()
        
        # Set up the update function
        self.app.update = update
    
    def set_demo_mode(self, mode: str):
        """Set the current demo mode"""
        self.demo_mode = mode
        
        # Clear previous mode state
        self.tile_highlighter.clear_all_highlights()
        
        print(f"Demo mode: {mode}")
        
        if mode == "highlighting":
            self.demo_tile_highlighting()
        elif mode == "animation":
            self.demo_combat_animations()
        elif mode == "inventory":
            self.demo_inventory_interface()
        elif mode == "combat_ui":
            self.demo_combat_interface()
        elif mode == "integrated":
            self.demo_integrated_systems()
        elif mode == "interaction":
            self.demo_enhanced_interactions()
    
    def demo_tile_highlighting(self):
        """Demonstrate tile highlighting system"""
        print("Tile Highlighting Demo - Click on units to see movement/attack ranges")
        
        if self.selected_unit:
            self.tile_highlighter.set_selected_unit(self.selected_unit)
        
        # Show some example highlights
        self.tile_highlighter.show_effect_area(Vector2Int(5, 5), 2, HighlightType.EFFECT_AREA)
        self.tile_highlighter.show_effect_area(Vector2Int(1, 1), 1, HighlightType.HEAL_AREA)
    
    def demo_combat_animations(self):
        """Demonstrate combat animation system"""
        print("Combat Animation Demo - Press SPACE to trigger animations")
        
        if not self.selected_unit:
            self.selected_unit = self.demo_units[0]
            self.select_unit(self.selected_unit)
    
    def demo_inventory_interface(self):
        """Demonstrate inventory interface"""
        if not self.inventory_interface:
            print("Inventory Interface Demo - Interface not available")
            return
            
        print("Inventory Interface Demo - Press 'I' to open inventory")
        
        if not self.selected_unit:
            self.selected_unit = self.demo_units[0]
            self.select_unit(self.selected_unit)
        
        # Show inventory after a short delay
        invoke(lambda: self.inventory_interface.show(self.selected_unit), delay=1)
    
    def demo_combat_interface(self):
        """Demonstrate combat interface"""
        if not self.combat_interface:
            print("Combat Interface Demo - Interface not available")
            return
            
        print("Combat Interface Demo - Combat UI is now visible")
        
        self.combat_interface.show()
        
        if not self.selected_unit:
            self.selected_unit = self.demo_units[0]
            self.select_unit(self.selected_unit)
        
        # Update turn order
        self.combat_interface.update_turn_order(self.demo_units[:5])
    
    def demo_integrated_systems(self):
        """Demonstrate all systems working together"""
        print("Integrated Demo - All systems active")
        
        # Show combat interface if available
        if self.combat_interface:
            self.combat_interface.show()
        
        # Select a unit
        if not self.selected_unit:
            self.selected_unit = self.demo_units[0]
            self.select_unit(self.selected_unit)
        
        # Show some highlights
        self.demo_tile_highlighting()
        
        # Update combat interface if available
        if self.combat_interface:
            self.combat_interface.update_turn_order(self.demo_units)
    
    def demo_enhanced_interactions(self):
        """Demonstrate enhanced interaction system"""
        print("Enhanced Interaction Demo - New interaction system active")
        print("- Click on tiles for enhanced selection feedback")
        print("- Click on units to open action modals")
        print("- Enhanced visual feedback and state management")
        
        # Enable the interaction manager
        self.interaction_manager.set_input_enabled(True)
        
        # Select a unit to show enhanced features
        if not self.selected_unit:
            self.selected_unit = self.demo_units[0]
            # Don't use old select_unit method - let interaction manager handle it
            unit_pos = self.interaction_manager._get_unit_position(self.selected_unit)
            if unit_pos:
                tile = self.interaction_manager.tiles.get(unit_pos)
                if tile:
                    self.interaction_manager._handle_tile_click(tile)
    
    def handle_tile_click(self, grid_pos: Vector2Int):
        """Handle clicking on a tile"""
        if not self.selected_unit:
            return
        
        print(f"Clicked tile: {grid_pos}")
        
        # Show path to clicked tile
        unit_transform = self.selected_unit.get_component(Transform)
        if unit_transform:
            unit_pos = self.grid_system.world_to_grid(unit_transform.position)
            path_result = self.pathfinding.find_path(unit_pos, grid_pos)
            
            if path_result.success and path_result.path:
                self.tile_highlighter.show_movement_path(path_result.path)
                
                # Trigger movement animation in animation demo mode
                if self.demo_mode == "animation":
                    target_world = self.grid_system.grid_to_world(grid_pos)
                    self.combat_animator.queue_movement_animation(
                        self.selected_unit,
                        Vector3(target_world.x, 0, target_world.z),
                        duration=2.0
                    )
    
    def trigger_demo_action(self):
        """Trigger a demo action based on current mode"""
        if self.demo_mode == "animation":
            self.trigger_random_animation()
        elif self.demo_mode == "integrated":
            self.trigger_integrated_action()
    
    def trigger_random_animation(self):
        """Trigger a random combat animation"""
        if not self.demo_units:
            return
        
        animation_types = ['attack', 'damage', 'heal', 'ability']
        animation_type = random.choice(animation_types)
        
        attacker = random.choice(self.demo_units)
        target = random.choice([u for u in self.demo_units if u != attacker])
        
        print(f"Triggering {animation_type} animation")
        
        if animation_type == 'attack':
            attack_types = ['melee', 'ranged', 'spell']
            attack_type = random.choice(attack_types)
            
            self.combat_animator.queue_attack_animation(
                attacker, target, attack_type=attack_type, delay=0.5
            )
            
            # Follow with damage animation
            self.combat_animator.queue_damage_animation(
                target, random.randint(10, 30), delay=1.5
            )
            
        elif animation_type == 'damage':
            self.combat_animator.queue_damage_animation(
                target, random.randint(15, 25)
            )
            
        elif animation_type == 'heal':
            self.combat_animator.queue_heal_animation(
                target, random.randint(10, 20)
            )
            
        elif animation_type == 'ability':
            # Create area effect
            target_transform = target.get_component(Transform)
            if target_transform:
                grid_pos = self.grid_system.world_to_grid(target_transform.position)
                self.tile_highlighter.show_effect_area(grid_pos, 2, HighlightType.EFFECT_AREA)
                
                # Queue ability animation
                self.combat_animator.queue_ability_animation(
                    attacker, 
                    ability_type='area_damage',
                    area_positions=[target_transform.position],
                    delay=0.5
                )
    
    def trigger_integrated_action(self):
        """Trigger an action that demonstrates system integration"""
        if not self.selected_unit or len(self.demo_units) < 2:
            return
        
        # Find a target
        target = random.choice([u for u in self.demo_units if u != self.selected_unit])
        
        # Show attack range
        unit_transform = self.selected_unit.get_component(Transform)
        target_transform = target.get_component(Transform)
        
        if unit_transform and target_transform:
            unit_grid = self.grid_system.world_to_grid(unit_transform.position)
            target_grid = self.grid_system.world_to_grid(target_transform.position)
            
            # Show path to target
            path_result = self.pathfinding.find_path(unit_grid, target_grid)
            if path_result.success and len(path_result.path) > 1:
                # Move closer to target
                move_target = path_result.path[min(3, len(path_result.path) - 1)]  # Move 3 tiles or to target
                move_world = self.grid_system.grid_to_world(move_target)
                
                # Queue movement
                self.combat_animator.queue_movement_animation(
                    self.selected_unit,
                    Vector3(move_world.x, 0, move_world.z),
                    duration=1.5
                )
                
                # Queue attack
                self.combat_animator.queue_attack_animation(
                    self.selected_unit, target, delay=2.0
                )
                
                # Queue damage
                self.combat_animator.queue_damage_animation(
                    target, random.randint(15, 30), delay=3.0
                )
                
                # Update combat interface if available
                if self.combat_interface:
                    self.combat_interface.update_turn_order(self.demo_units)
    
    def update_demo_mode(self):
        """Update current demo mode"""
        if self.demo_mode == "highlighting":
            # Cycle through different highlight demonstrations
            current_time = time.time()
            cycle_time = int(current_time / 3) % 4  # 3-second cycles
            
            if cycle_time == 0:
                # Movement highlights
                if self.selected_unit:
                    self.tile_highlighter.set_selected_unit(self.selected_unit)
            elif cycle_time == 1:
                # Effect area highlights
                self.tile_highlighter.clear_all_highlights()
                self.tile_highlighter.show_effect_area(Vector2Int(4, 4), 2, HighlightType.EFFECT_AREA)
            elif cycle_time == 2:
                # Danger zone highlights  
                self.tile_highlighter.clear_all_highlights()
                self.tile_highlighter.show_effect_area(Vector2Int(6, 6), 3, HighlightType.DANGER_ZONE)
            else:
                # Heal area highlights
                self.tile_highlighter.clear_all_highlights()
                self.tile_highlighter.show_effect_area(Vector2Int(2, 8), 1, HighlightType.HEAL_AREA)
    
    def run(self):
        """Start the demo"""
        # Set initial demo mode
        self.set_demo_mode("highlighting")
        
        # Run Ursina app
        self.app.run()
    
    def cleanup(self):
        """Cleanup demo resources"""
        self.tile_highlighter.cleanup()
        self.combat_animator.cleanup()
        self.interaction_manager.cleanup()
        if self.inventory_interface:
            self.inventory_interface.cleanup()
        if self.combat_interface:
            self.combat_interface.cleanup()


def main():
    """Main demo function"""
    try:
        demo = Phase4VisualDemo()
        demo.run()
    except Exception as e:
        print(f"Demo error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Cleanup
        try:
            demo.cleanup()
        except:
            pass


if __name__ == "__main__":
    main()