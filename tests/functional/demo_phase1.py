"""
Phase 1 Foundation Functional Demonstration

Interactive Ursina-based demonstration of all Phase 1 systems working together.
Run this file to see the tactical RPG foundation in action.
"""

import sys
import os
import time
import traceback
from typing import List, Tuple, Optional

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

try:
    from ursina import *
    URSINA_AVAILABLE = True
except ImportError:
    print("Ursina not available. Running in console mode.")
    URSINA_AVAILABLE = False

from demo_utils import (
    create_demo_world, create_tactical_grid, create_character_archetypes,
    apply_demonstration_modifiers, demonstrate_pathfinding,
    get_performance_metrics, create_demo_scenario_description,
    format_character_stats, get_grid_cell_description
)

from core.math.vector import Vector2Int, Vector3
from core.math.pathfinding import AStarPathfinder


class Phase1Demo:
    """Main demonstration class for Phase 1 systems"""
    
    def __init__(self, use_visual: bool = True):
        self.use_visual = use_visual and URSINA_AVAILABLE
        self.world = None
        self.grid = None
        self.characters = []
        self.pathfinder = None
        self.running = True
        self.paused = False
        self.selected_character = 0
        self.show_pathfinding = False
        self.performance_stats = {}
        self.frame_count = 0
        self.last_stats_update = 0
        self.demo_start_time = time.time()
        
        # Visual components (if using Ursina)
        self.grid_entities = []
        self.character_entities = []
        self.path_entities = []
        self.ui_text = None
        
        print(create_demo_scenario_description())
        self._initialize()
    
    def _initialize(self):
        """Initialize the demonstration"""
        print("Initializing Phase 1 Demonstration...")
        
        # Create game world
        self.world = create_demo_world()
        print(f"✓ World created with {self.world.system_count} systems")
        
        # Create tactical grid
        self.grid = create_tactical_grid(10, 10)
        self.pathfinder = AStarPathfinder(self.grid)
        print("✓ Tactical grid created (10x10 with terrain features)")
        
        # Create characters
        self.characters = create_character_archetypes(self.world)
        apply_demonstration_modifiers(self.characters)
        print(f"✓ Created {len(self.characters)} character archetypes with modifiers")
        
        # Initialize visual components if available
        if self.use_visual:
            self._initialize_visual()
        
        print("✓ Demonstration initialized successfully")
        print("\nStarting demonstration loop...")
    
    def _initialize_visual(self):
        """Initialize Ursina visual components"""
        app = Ursina()
        
        # Set up camera
        camera.position = (5, 10, 5)
        camera.rotation_x = 45
        
        # Create grid visualization
        self._create_grid_visual()
        self._create_character_visuals()
        self._create_ui()
        
        # Set up input handlers
        self._setup_input_handlers()
    
    def _create_grid_visual(self):
        """Create visual representation of the tactical grid"""
        for x in range(self.grid.width):
            for y in range(self.grid.height):
                pos = Vector2Int(x, y)
                cell = self.grid.get_cell(pos)
                
                if cell:
                    # Choose color based on terrain type
                    color = color.white
                    if cell.terrain_type.name == 'WALL':
                        color = color.gray
                    elif cell.terrain_type.name == 'DIFFICULT':
                        color = color.brown
                    elif cell.terrain_type.name == 'ELEVATED':
                        color = color.yellow
                    
                    # Create cube for cell
                    cube = Entity(
                        model='cube',
                        color=color,
                        position=(x, cell.height * 0.5, y),
                        scale=(0.9, cell.height if cell.height > 0 else 0.1, 0.9)
                    )
                    self.grid_entities.append(cube)
    
    def _create_character_visuals(self):
        """Create visual representation of characters"""
        colors = [color.blue, color.red, color.green, color.magenta]
        
        for i, (archetype_name, character) in enumerate(self.characters):
            transform = character.get_component(Transform)
            pos = transform.position
            
            # Create character representation
            char_entity = Entity(
                model='sphere',
                color=colors[i % len(colors)],
                position=(pos.x, pos.y + 0.5, pos.z),
                scale=0.3
            )
            
            # Add label
            label = Text(
                archetype_name,
                parent=char_entity,
                position=(0, 1, 0),
                scale=2,
                billboard=True
            )
            
            self.character_entities.append((char_entity, label))
    
    def _create_ui(self):
        """Create user interface elements"""
        self.ui_text = Text(
            '',
            position=(-0.8, 0.4),
            scale=1,
            parent=camera.ui,
            origin=(0, 0)
        )
    
    def _setup_input_handlers(self):
        """Set up keyboard input handlers"""
        def input(key):
            if key == 'space':
                self.paused = not self.paused
                print(f"Demo {'paused' if self.paused else 'resumed'}")
            
            elif key == 'r':
                print("Resetting demonstration...")
                self._reset_demo()
            
            elif key == 'p':
                self.show_pathfinding = not self.show_pathfinding
                print(f"Pathfinding visualization {'enabled' if self.show_pathfinding else 'disabled'}")
            
            elif key in ['1', '2', '3', '4']:
                self.selected_character = int(key) - 1
                if self.selected_character < len(self.characters):
                    archetype_name = self.characters[self.selected_character][0]
                    print(f"Selected {archetype_name}")
            
            elif key == 'escape':
                self.running = False
                print("Exiting demonstration...")
        
        # Override Ursina's input function
        import ursina
        ursina.input = input
    
    def _reset_demo(self):
        """Reset the demonstration to initial state"""
        # Reset modifiers and resources
        for archetype_name, character in self.characters:
            resources = character.get_component(ResourceManager)
            modifier_manager = character.get_component(ModifierManager)
            
            # Reset resources
            resources.mp.current_value = resources.mp.max_value
            resources.rage.current_value = 0
            resources.kwan.current_value = 50
            
            # Clear and reapply modifiers
            modifier_manager.clear_all_modifiers()
        
        apply_demonstration_modifiers(self.characters)
        
        self.frame_count = 0
        self.demo_start_time = time.time()
    
    def _update_world(self, delta_time: float):
        """Update the game world"""
        if not self.paused:
            self.world.update(delta_time)
    
    def _update_performance_stats(self):
        """Update performance statistics"""
        current_time = time.time()
        if current_time - self.last_stats_update > 1.0:  # Update every second
            self.performance_stats = get_performance_metrics(self.world)
            self.last_stats_update = current_time
    
    def _demonstrate_pathfinding(self):
        """Demonstrate pathfinding between characters"""
        if len(self.characters) >= 2:
            char1_pos = self.characters[0][1].get_component(Transform).position
            char2_pos = self.characters[1][1].get_component(Transform).position
            
            start = self.grid.world_to_grid(char1_pos)
            goal = self.grid.world_to_grid(char2_pos)
            
            path_result = demonstrate_pathfinding(self.grid, start, goal)
            
            if self.show_pathfinding and path_result['success']:
                self._visualize_path(path_result['path'])
            
            return path_result
        return None
    
    def _visualize_path(self, path: List[Vector2Int]):
        """Visualize pathfinding result"""
        # Clear previous path visualization
        for entity in self.path_entities:
            destroy(entity)
        self.path_entities.clear()
        
        # Create path visualization
        for i, pos in enumerate(path):
            world_pos = self.grid.grid_to_world(pos)
            
            path_entity = Entity(
                model='sphere',
                color=color.orange,
                position=(world_pos.x, world_pos.y + 0.2, world_pos.z),
                scale=0.1
            )
            self.path_entities.append(path_entity)
    
    def _get_status_text(self) -> str:
        """Generate status text for display"""
        runtime = time.time() - self.demo_start_time
        
        status = f"Phase 1 Demo - Runtime: {runtime:.1f}s\n"
        status += f"Frame: {self.frame_count} | Status: {'PAUSED' if self.paused else 'RUNNING'}\n"
        status += f"Entities: {len(self.world.entity_manager._entities)} | Systems: {self.world.system_count}\n\n"
        
        # Show selected character stats
        if self.selected_character < len(self.characters):
            archetype_name, character = self.characters[self.selected_character]
            status += format_character_stats(archetype_name, character)
        
        # Show performance stats
        if self.performance_stats:
            status += f"\nPerformance:\n"
            for system_name, stats in self.performance_stats.get('systems_performance', {}).items():
                if 'avg_update_time' in stats:
                    avg_time = stats['avg_update_time'] * 1000  # Convert to ms
                    status += f"{system_name}: {avg_time:.2f}ms\n"
        
        # Show controls
        status += f"\nControls: SPACE=Pause | R=Reset | P=Path | 1-4=Character | ESC=Exit"
        
        return status
    
    def _console_mode_update(self):
        """Update display for console mode"""
        if self.frame_count % 60 == 0:  # Update every 60 frames (~1 second)
            print("\n" + "="*50)
            print(self._get_status_text())
            
            # Demonstrate pathfinding
            path_result = self._demonstrate_pathfinding()
            if path_result:
                print(f"\nPathfinding Demo:")
                print(f"Success: {path_result['success']}")
                print(f"Path length: {len(path_result['path'])}")
                print(f"Cost: {path_result['cost']:.2f}")
                print(f"Time: {path_result['time']*1000:.3f}ms")
                print(f"Nodes explored: {path_result['nodes_explored']}")
    
    def run(self):
        """Run the demonstration"""
        if self.use_visual:
            self._run_visual_mode()
        else:
            self._run_console_mode()
    
    def _run_visual_mode(self):
        """Run in visual mode with Ursina"""
        def update():
            if not self.running:
                application.quit()
                return
            
            delta_time = time.dt
            self.frame_count += 1
            
            self._update_world(delta_time)
            self._update_performance_stats()
            
            # Update UI
            if self.ui_text:
                self.ui_text.text = self._get_status_text()
            
            # Demonstrate pathfinding periodically
            if self.frame_count % 120 == 0:  # Every 2 seconds
                self._demonstrate_pathfinding()
        
        app.run()
    
    def _run_console_mode(self):
        """Run in console mode without visuals"""
        print("Running in console mode (Ursina not available)")
        print("Press Ctrl+C to exit")
        
        try:
            while self.running:
                delta_time = 0.016  # ~60 FPS
                self.frame_count += 1
                
                self._update_world(delta_time)
                self._update_performance_stats()
                self._console_mode_update()
                
                time.sleep(delta_time)
                
        except KeyboardInterrupt:
            print("\nDemo interrupted by user")
        except Exception as e:
            print(f"\nDemo error: {e}")
            traceback.print_exc()
        finally:
            print("Demo finished")


def main():
    """Main entry point for the demonstration"""
    print("Phase 1 Foundation Demonstration")
    print("===============================")
    
    try:
        # Determine if we can use visual mode
        use_visual = URSINA_AVAILABLE
        
        if not use_visual:
            print("Note: Running in console mode. Install Ursina for visual demonstration.")
        
        # Create and run demonstration
        demo = Phase1Demo(use_visual=use_visual)
        demo.run()
        
        print("\nDemonstration completed successfully!")
        
    except Exception as e:
        print(f"Error running demonstration: {e}")
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())