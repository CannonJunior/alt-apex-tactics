"""
Apex Tactics - Modernized with Modular Components

This file has been updated to use the modular ECS architecture from src/ while 
maintaining backwards compatibility with the original monolithic structure.

Components Replaced:
- UnitType enum → src/components/gameplay/unit_type.py  
- Unit class → ECS entities with AttributeStats, MovementComponent, etc.
- BattleGrid → src/core/math/grid.py (TacticalGrid) with legacy wrapper
- TurnManager → src/game/battle/turn_manager.py with legacy wrapper

Components Preserved:
- CameraController (as requested)
- TacticalRPG main class (enhanced with ECS World)
- ControlPanel (preserved, could be enhanced later)
- Ursina-specific visual components (GridTile, UnitEntity) 
- Main game loop and app initialization

The system now runs both legacy and modular components in parallel, with the ECS 
World providing enhanced performance and the legacy wrappers ensuring compatibility.
"""

from ursina import *
import sys
import os

# Add src directory to Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import modular components
from core.ecs.world import World
from core.ecs.entity import Entity as ECSEntity
from components.stats.attributes import AttributeStats
from components.gameplay.unit_type import UnitType, UnitTypeComponent
from components.movement.movement import MovementComponent
from components.combat.attack import AttackComponent
from components.combat.defense import DefenseComponent
from components.combat.damage import AttackType
from core.math.grid import TacticalGrid
from core.math.vector import Vector2Int
from game.battle.turn_manager import TurnManager as ModularTurnManager
from ui.visual.grid_visualizer import GridVisualizer
from ui.visual.tile_highlighter import TileHighlighter
from ui.interaction.interactive_tile import InteractiveTile
from ui.interaction.interaction_manager import InteractionManager

import random
import math

app = Ursina()

# Create a simple ground plane for better visibility  
ground = Entity(model='plane', texture='white_cube', color=color.dark_gray, scale=(20, 1, 20), position=(4, -0.1, 4))

def create_clean_grid_lines():
    """Create clean visual grid lines like in phase4_visual_demo"""
    grid_size = 8  # Match the BattleGrid size
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

# Create the clean grid
create_clean_grid_lines()

# Mouse detection now handled in the input() function using world coordinates

# Legacy Unit wrapper for backwards compatibility
class Unit:
    """Legacy Unit class wrapper around ECS entities for backwards compatibility"""
    
    def __init__(self, name, unit_type, x, y, wisdom=None, wonder=None, worthy=None, faith=None, finesse=None, fortitude=None, speed=None, spirit=None, strength=None):
        # Create ECS entity using modular components
        self.entity = create_unit_entity(name, unit_type, x, y, wisdom, wonder, worthy, faith, finesse, fortitude, speed, spirit, strength)
        self.name = name
        self.type = unit_type
        self.x, self.y = x, y
        
        # Get components for quick access
        self.stats = self.entity.get_component(AttributeStats)
        self.movement = self.entity.get_component(MovementComponent)
        self.attack_comp = self.entity.get_component(AttackComponent)
        self.defense_comp = self.entity.get_component(DefenseComponent)
        
        # Legacy compatibility properties
        self.alive = True
        self.action_options = ["Move", "Attack", "Spirit", "Magic", "Inventory"]
        
    @property
    def strength(self):
        return self.stats.strength
    
    @property
    def fortitude(self):
        return self.stats.fortitude
    
    @property
    def finesse(self):
        return self.stats.finesse
    
    @property
    def wisdom(self):
        return self.stats.wisdom
    
    @property
    def wonder(self):
        return self.stats.wonder
    
    @property
    def worthy(self):
        return self.stats.worthy
    
    @property
    def faith(self):
        return self.stats.faith
    
    @property
    def spirit(self):
        return self.stats.spirit
    
    @property
    def speed(self):
        return self.stats.speed
    
    @property
    def max_hp(self):
        return self.stats.max_hp
    
    @property
    def hp(self):
        return self.stats.current_hp
    
    @hp.setter
    def hp(self, value):
        self.stats.current_hp = value
    
    @property
    def max_mp(self):
        return self.stats.max_mp
    
    @property
    def mp(self):
        return self.stats.current_mp
    
    @property
    def max_ap(self):
        return self.stats.derived_stats.get('ap', self.speed)
    
    @property
    def ap(self):
        return self.stats.derived_stats.get('current_ap', self.speed)
    
    @ap.setter
    def ap(self, value):
        # Store AP in derived cache - this is a bit of a hack for legacy compatibility
        self.stats.derived_stats['current_ap'] = value
    
    @property
    def move_points(self):
        return self.movement.movement_range
    
    @property
    def current_move_points(self):
        return self.movement.remaining_movement
    
    @current_move_points.setter
    def current_move_points(self, value):
        self.movement.remaining_movement = value
    
    @property
    def attack_range(self):
        return self.attack_comp.attack_range
    
    @property
    def attack_effect_area(self):
        return int(self.attack_comp.area_effect_radius)
    
    @property
    def physical_defense(self):
        return self.defense_comp.get_defense_value(AttackType.PHYSICAL)
    
    @property
    def magical_defense(self):
        return self.defense_comp.get_defense_value(AttackType.MAGICAL)
    
    @property
    def spiritual_defense(self):
        return self.defense_comp.get_defense_value(AttackType.SPIRITUAL)
    
    @property
    def physical_attack(self):
        return self.stats.derived_stats.get('physical_attack', (self.speed + self.strength + self.finesse) // 2)
    
    @property
    def magical_attack(self):
        return self.stats.derived_stats.get('magical_attack', (self.wisdom + self.wonder + self.spirit) // 2)
    
    @property
    def spiritual_attack(self):
        return self.stats.derived_stats.get('spiritual_attack', (self.faith + self.fortitude + self.worthy) // 2)
    
    def take_damage(self, damage, damage_type=AttackType.PHYSICAL):
        current_hp = self.hp
        defense = self.defense_comp.get_defense_value(damage_type)
        actual_damage = max(1, damage - defense)
        new_hp = max(0, current_hp - actual_damage)
        self.hp = new_hp
        self.alive = new_hp > 0
    
    def can_move_to(self, x, y, grid):
        distance = abs(x - self.x) + abs(y - self.y)
        return distance <= self.current_move_points and grid.is_valid(x, y)

def create_unit_entity(name, unit_type, x, y, wisdom=None, wonder=None, worthy=None, faith=None, finesse=None, fortitude=None, speed=None, spirit=None, strength=None):
    """Factory function to create a unit entity with modular components"""
    
    # Create base attributes with random values
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
    
    # Create ECS entity
    entity = ECSEntity()
    entity.name = name
    
    # Add components
    stats = AttributeStats(**base_attrs)
    entity.add_component(stats)
    
    unit_type_comp = UnitTypeComponent(unit_type)
    entity.add_component(unit_type_comp)
    
    # Apply type bonuses to stats
    for attr, bonus in unit_type_comp.get_all_bonuses().items():
        current_value = getattr(stats, attr, 0)
        setattr(stats, attr, current_value + bonus)
    
    # Add movement component
    movement_range = stats.speed // 2 + 2
    movement = MovementComponent(movement_range=movement_range)
    entity.add_component(movement)
    
    # Add combat components
    attack = AttackComponent(attack_range=1, area_effect_radius=0.0)
    entity.add_component(attack)
    
    # Initialize defense with values from stats
    defense = DefenseComponent(
        physical_defense=stats.derived_stats.get('physical_defense', 0),
        magical_defense=stats.derived_stats.get('magical_defense', 0),
        spiritual_defense=stats.derived_stats.get('spiritual_defense', 0)
    )
    entity.add_component(defense)
    
    return entity

# Battle Grid System (Legacy wrapper)
class BattleGrid:
    """Legacy wrapper around TacticalGrid for backwards compatibility"""
    
    def __init__(self, width=8, height=8):
        self.width, self.height = width, height
        self.grid = TacticalGrid(width, height)
        self.units = {}
        self.selected_unit = None
        
    def is_valid(self, x, y):
        grid_pos = Vector2Int(x, y)
        if not self.grid.is_valid_position(grid_pos):
            return False
        return (x, y) not in self.units
        
    def add_unit(self, unit):
        self.units[(unit.x, unit.y)] = unit
        # Also update the grid
        try:
            from core.math.vector import Vector2Int
            grid_pos = Vector2Int(unit.x, unit.y)
            cell = self.grid.get_cell(grid_pos)
            if cell:
                cell.occupied = True
        except Exception as e:
            print(f"⚠ Could not update grid cell: {e}")
        
    def move_unit(self, unit, x, y):
        if unit.can_move_to(x, y, self):
            distance = abs(x - unit.x) + abs(y - unit.y)
            
            # Clear old position
            try:
                from core.math.vector import Vector2Int
                old_pos = Vector2Int(unit.x, unit.y)
                old_cell = self.grid.get_cell(old_pos)
                if old_cell:
                    old_cell.occupied = False
            except Exception as e:
                print(f"⚠ Could not clear old grid cell: {e}")
            
            del self.units[(unit.x, unit.y)]
            
            # Set new position
            unit.x, unit.y = x, y
            unit.current_move_points -= distance
            self.units[(x, y)] = unit
            
            try:
                new_pos = Vector2Int(x, y)
                new_cell = self.grid.get_cell(new_pos)
                if new_cell:
                    new_cell.occupied = True
            except Exception as e:
                print(f"⚠ Could not update new grid cell: {e}")
            
            return True
        return False

# Turn Management (Legacy wrapper)
class TurnManager:
    """Legacy wrapper around ModularTurnManager for backwards compatibility"""
    
    def __init__(self, units):
        self.units = sorted(units, key=lambda u: u.speed, reverse=True)
        self.current_turn = 0
        self.phase = "move"  # move, action, end
        
        # Create modular turn manager
        self.modular_turn_manager = ModularTurnManager()
        
        # Prepare entity list for modular turn manager
        unit_entities = [unit.entity for unit in self.units]
        
        # Start combat with all units
        try:
            self.modular_turn_manager.start_combat(unit_entities)
            print("✓ Modular turn manager initialized successfully")
        except Exception as e:
            print(f"⚠ Could not initialize modular turn manager: {e}")
            # Fallback to legacy system only
            self.modular_turn_manager = None
        
    def next_turn(self):
        self.current_turn = (self.current_turn + 1) % len(self.units)
        
        # Advance modular turn manager if available
        if self.modular_turn_manager:
            try:
                self.modular_turn_manager.advance_to_next_unit()
            except Exception as e:
                print(f"⚠ Error advancing modular turn manager: {e}")
        
        if self.current_turn == 0:
            # New round - reset all units
            for unit in self.units:
                unit.ap = unit.max_ap
                unit.current_move_points = unit.move_points  # Reset movement points
                
    def current_unit(self):
        if not self.units:
            return None
        
        # Get current unit from modular system if available
        if self.modular_turn_manager:
            try:
                current_unit_id = self.modular_turn_manager.get_current_unit()
                if current_unit_id:
                    # Find unit by entity ID
                    for unit in self.units:
                        if unit.entity.id == current_unit_id:
                            return unit
            except Exception as e:
                print(f"⚠ Error getting current unit from modular system: {e}")
        
        # Fallback to legacy system
        return self.units[self.current_turn] if self.units else None

# Camera Control System
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

# Visual Components
# GridTile class removed - using modular GridVisualizer system instead

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
            position=(unit.x + 0.5, 1.0, unit.y + 0.5)  # Center units on grid tiles
        )
        self.unit = unit
        self.original_color = colors[unit.type]
        
    def highlight_selected(self):
        self.color = color.white
        
    def unhighlight(self):
        self.color = self.original_color

# Main Game Controller
class TacticalRPG:
    def __init__(self):
        # Initialize ECS World
        self.world = World()
        
        # Legacy components for backwards compatibility
        self.grid = BattleGrid()
        self.units = []
        self.unit_entities = []
        self.turn_manager = None
        self.selected_unit = None
        self.current_path = []  # Track the selected movement path
        self.path_cursor = None  # Current position in path selection
        self.movement_modal = None  # Reference to movement confirmation modal
        self.action_modal = None  # Reference to action selection modal
        self.current_mode = None  # Track current action mode: 'move', 'attack', etc.
        self.attack_modal = None  # Reference to attack confirmation modal
        self.attack_target_tile = None  # Currently targeted attack tile
        self.camera_controller = CameraController(self.grid.width, self.grid.height)
        
        # Initialize pathfinder first (required by other systems)
        try:
            from core.math.pathfinding import AStarPathfinder
            self.pathfinder = AStarPathfinder(self.grid.grid)
            print("✓ AStarPathfinder initialized successfully")
        except Exception as e:
            print(f"⚠ Could not initialize AStarPathfinder: {e}")
            self.pathfinder = None
        
        # Initialize grid visualizer (requires pathfinder)
        if self.pathfinder:
            try:
                self.grid_visualizer = GridVisualizer(self.grid.grid, self.pathfinder)
                print("✓ GridVisualizer initialized successfully")
            except Exception as e:
                print(f"⚠ Could not initialize GridVisualizer: {e}")
                self.grid_visualizer = None
        else:
            print("⚠ Skipping GridVisualizer - AStarPathfinder not available")
            self.grid_visualizer = None
        
        # Initialize tile highlighter (requires grid visualizer)
        if self.grid_visualizer:
            try:
                self.tile_highlighter = TileHighlighter(self.grid_visualizer)
                print("✓ TileHighlighter initialized successfully")
            except Exception as e:
                print(f"⚠ Could not initialize TileHighlighter: {e}")
                self.tile_highlighter = None
        else:
            print("⚠ Skipping TileHighlighter - GridVisualizer not available")
            self.tile_highlighter = None
        
        # Initialize interaction manager for enhanced UI (only if all dependencies available)
        if self.grid_visualizer and self.pathfinder:
            try:
                self.interaction_manager = InteractionManager(
                    self.grid.grid, 
                    self.pathfinder, 
                    self.grid_visualizer
                )
                print("✓ InteractionManager initialized successfully")
            except Exception as e:
                print(f"⚠ Could not initialize InteractionManager: {e}")
                self.interaction_manager = None
        else:
            print("⚠ Skipping InteractionManager - missing dependencies")
            self.interaction_manager = None
        
        self.setup_battle()
        
    def setup_battle(self):
        # Initialize ECS systems
        try:
            from systems.stat_system import StatSystem
            from systems.movement_system import MovementSystem
            from systems.combat_system import CombatSystem
            
            # Add systems to world
            self.world.add_system(StatSystem())
            self.world.add_system(MovementSystem())
            self.world.add_system(CombatSystem())
            
            print("✓ ECS systems initialized successfully")
        except ImportError as e:
            print(f"⚠ Could not import all ECS systems: {e}")
            print("  Continuing with legacy components...")
        
        # Grid tiles now created by clean grid system - no individual entities needed
                
        # Create units with randomized attributes based on type
        player_units = [
            Unit("Hero", UnitType.HEROMANCER, 1, 1),
            Unit("Sage", UnitType.MAGI, 2, 1)
        ]
        enemy_units = [
            Unit("Orc", UnitType.UBERMENSCH, 6, 6),
            Unit("Spirit", UnitType.REALM_WALKER, 5, 6)
        ]
        
        self.units = player_units + enemy_units
        
        # Add units to both legacy and ECS systems
        for unit in self.units:
            self.grid.add_unit(unit)
            self.unit_entities.append(UnitEntity(unit))
            
            # Register unit entity with ECS world entity manager
            try:
                self.world.entity_manager._register_entity(unit.entity)
                print(f"✓ Registered {unit.name} with ECS World")
            except Exception as e:
                print(f"⚠ Could not register {unit.name} with ECS World: {e}")
            
        self.turn_manager = TurnManager(self.units)
        self.refresh_all_ap()
        
        print(f"✓ Battle setup complete: {len(self.units)} units, ECS World with {self.world.entity_count} entities")
        
    def end_current_turn(self):
        """End the current unit's turn and move to next unit"""
        if self.turn_manager:
            # Clear current selection
            self.clear_highlights()
            self.selected_unit = None
            
            # Move to next turn
            self.turn_manager.next_turn()
            
            # Update control panel with new current unit
            current_unit = self.turn_manager.current_unit()
            control_panel.update_unit_info(current_unit)
            
            print(f"Turn ended. Now it's {current_unit.name}'s turn.")
        
    def handle_tile_click(self, x, y):
        # Handle attack targeting if in attack mode
        if self.current_mode == "attack" and self.selected_unit:
            self.handle_attack_target_selection(x, y)
            return
            
        # Clear any existing highlights
        self.clear_highlights()
        
        # Check if there's a unit on the clicked tile
        if (x, y) in self.grid.units:
            clicked_unit = self.grid.units[(x, y)]
            
            # Select the clicked unit and show action modal
            self.selected_unit = clicked_unit
            self.current_path = []  # Reset path when selecting new unit
            self.path_cursor = (clicked_unit.x, clicked_unit.y)  # Start cursor at unit position
            self.current_mode = None  # Reset mode
            self.highlight_selected_unit()
            self.highlight_movement_range()
            control_panel.update_unit_info(clicked_unit)
            
            # Show action modal for the selected unit
            self.show_action_modal(clicked_unit)
        else:
            # Clicked on an empty tile
            if self.current_mode == "move":
                # In movement mode - don't clear selection, this could be path planning
                return
            else:
                # Not in movement mode - clear selection
                self.selected_unit = None
                self.current_path = []
                self.path_cursor = None
                self.current_mode = None
                control_panel.update_unit_info(None)
                
    def highlight_movement_range(self):
        """Highlight all tiles the selected unit can move to"""
        if not self.selected_unit:
            return
        
        # Clear existing highlight entities
        self.clear_highlights()
        
        highlight_count = 0
        # Create highlight entities for movement range
        for x in range(self.grid.width):
            for y in range(self.grid.height):
                distance = abs(x - self.selected_unit.x) + abs(y - self.selected_unit.y)
                if distance <= self.selected_unit.current_move_points and self.grid.is_valid(x, y):
                    if distance == 0:
                        # Current position - different color
                        highlight_color = color.white
                    else:
                        # Valid movement range
                        highlight_color = color.green
                    
                    # Create highlight overlay entity
                    highlight = Entity(
                        model='cube',
                        color=highlight_color,
                        scale=(0.9, 0.2, 0.9),
                        position=(x + 0.5, 0, y + 0.5),  # Center on tile, same level as grid
                        alpha=0.5  # Same transparency as grid
                    )
                    # Store in a list for cleanup
                    if not hasattr(self, 'highlight_entities'):
                        self.highlight_entities = []
                    self.highlight_entities.append(highlight)
                    highlight_count += 1
                    
    def highlight_selected_unit(self):
        if self.selected_unit:
            for entity in self.unit_entities:
                if entity.unit == self.selected_unit:
                    entity.highlight_selected()
                    break
                    
    def highlight_possible_moves(self):
        # This method is now replaced by highlight_movement_range
        self.highlight_movement_range()
                            
    def get_tile_at(self, x, y):
        # Using modular grid system - no individual tile entities
        return None
        
    def handle_path_movement(self, direction):
        """Handle path movement and confirmation"""
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
            
            # Don't allow path to exceed movement points
            if total_distance > self.selected_unit.current_move_points:
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
    
    def show_action_modal(self, unit):
        """Show modal with available actions for the selected unit"""
        if not unit:
            return
            
        # Create action buttons dynamically based on unit's action options
        action_buttons = []
        
        def create_action_callback(action_name):
            def action_callback():
                self.handle_action_selection(action_name, unit)
                self.action_modal.enabled = False
                destroy(self.action_modal)
                self.action_modal = None
            return action_callback
        
        # Create buttons for each action option
        for action in unit.action_options:
            btn = Button(text=action, color=color.azure)
            btn.on_click = create_action_callback(action)
            action_buttons.append(btn)
        
        # Add cancel button
        cancel_btn = Button(text='Cancel', color=color.red)
        def cancel_action():
            self.action_modal.enabled = False
            destroy(self.action_modal)
            self.action_modal = None
            
        cancel_btn.on_click = cancel_action
        action_buttons.append(cancel_btn)
        
        # Create content tuple
        content = [Text(f'Select action for {unit.name}:')] + action_buttons
        
        # Create modal window
        self.action_modal = WindowPanel(
            title='Unit Actions',
            content=tuple(content),
            popup=True
        )
        
        # Center the window panel
        self.action_modal.y = self.action_modal.panel.scale_y / 2 * self.action_modal.scale_y
        self.action_modal.layout()
    
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
            print("Spirit action selected - functionality to be implemented")
            # TODO: Implement spirit abilities
        elif action_name == "Magic":
            print("Magic action selected - functionality to be implemented")
            # TODO: Implement magic spells
        elif action_name == "Inventory":
            print("Inventory action selected - functionality to be implemented")
            # TODO: Implement inventory management
        else:
            print(f"Unknown action: {action_name}")
    
    def handle_attack(self, unit):
        """Handle attack action - highlight attack range"""
        if not unit:
            return
            
        print(f"{unit.name} entering attack mode. Attack range: {unit.attack_range}")
        
        # Clear existing highlights and show attack range
        self.clear_highlights()
        self.highlight_selected_unit()
        self.highlight_attack_range(unit)
        
        print("Click on a target within red highlighted tiles to attack.")
    
    def handle_attack_target_selection(self, x, y):
        """Handle tile clicks when in attack mode"""
        if not self.selected_unit:
            return
            
        # Check if clicked tile is within attack range
        distance = abs(x - self.selected_unit.x) + abs(y - self.selected_unit.y)
        if distance <= self.selected_unit.attack_range and distance > 0:
            # Valid attack target tile
            self.attack_target_tile = (x, y)
            
            # Clear highlights and show attack effect area
            self.clear_highlights()
            self.highlight_selected_unit()
            self.highlight_attack_range(self.selected_unit)
            self.highlight_attack_effect_area(x, y)
            
            # Show attack confirmation modal
            self.show_attack_confirmation(x, y)
        else:
            print(f"Target at ({x}, {y}) is out of attack range!")
    
    def highlight_attack_effect_area(self, target_x, target_y):
        """Highlight the attack effect area around the target tile"""
        if not self.selected_unit:
            return
        
        effect_radius = self.selected_unit.attack_effect_area
        
        for x in range(self.grid.width):
            for y in range(self.grid.height):
                # Calculate Manhattan distance from target tile to this tile
                distance = abs(x - target_x) + abs(y - target_y)
                
                # Highlight tiles within effect area
                if distance <= effect_radius:
                    if (x, y) == (target_x, target_y):
                        # Target tile gets special color
                        highlight_color = color.orange
                    else:
                        # Effect area tiles
                        highlight_color = color.yellow
                    
                    # Create highlight overlay entity
                    highlight = Entity(
                        model='cube',
                        color=highlight_color,
                        scale=(0.9, 0.2, 0.9),
                        position=(x + 0.5, 0, y + 0.5),  # Center on tile, same level as grid
                        alpha=0.5  # Same transparency as grid
                    )
                    # Store in a list for cleanup
                    if not hasattr(self, 'highlight_entities'):
                        self.highlight_entities = []
                    self.highlight_entities.append(highlight)
    
    def show_attack_confirmation(self, target_x, target_y):
        """Show modal to confirm attack on target tile"""
        if not self.selected_unit or not self.attack_target_tile:
            return
            
        # Find units that would be affected by the attack
        affected_units = self.get_units_in_effect_area(target_x, target_y)
        unit_list = affected_units  # Move unit_list declaration here
        
        # Create confirmation buttons
        confirm_btn = Button(text='Confirm Attack', color=color.red)
        cancel_btn = Button(text='Cancel', color=color.gray)
        
        # Set up button callbacks
        def confirm_attack():
            print(f"{self.selected_unit.name} attacks tile ({target_x}, {target_y})!")
            
            # Apply damage to each unit in unit_list
            attack_damage = self.selected_unit.physical_attack
            for target_unit in unit_list:
                print(f"  {target_unit.name} takes {attack_damage} physical damage!")
                target_unit.take_damage(attack_damage, AttackType.PHYSICAL)
                
                if not target_unit.alive:
                    print(f"  {target_unit.name} has been defeated!")
                    # Remove dead unit from grid
                    if (target_unit.x, target_unit.y) in self.grid.units:
                        del self.grid.units[(target_unit.x, target_unit.y)]
                    
                    # Remove unit entity from scene
                    for entity in self.unit_entities:
                        if entity.unit == target_unit:
                            destroy(entity)
                            self.unit_entities.remove(entity)
                            break
            
            self.attack_modal.enabled = False
            destroy(self.attack_modal)
            self.attack_modal = None
            # Return to normal mode
            self.current_mode = None
            self.attack_target_tile = None
            self.clear_highlights()
            self.highlight_selected_unit()
            
        def cancel_attack():
            # Return to attack mode without attacking
            self.clear_highlights()
            self.highlight_selected_unit()
            self.highlight_attack_range(self.selected_unit)
            self.attack_modal.enabled = False
            destroy(self.attack_modal)
            self.attack_modal = None
        
        confirm_btn.on_click = confirm_attack
        cancel_btn.on_click = cancel_attack
        
        # Create modal content
        unit_names = ", ".join([unit.name for unit in unit_list]) if unit_list else "No units"
        
        # Create modal window
        self.attack_modal = WindowPanel(
            title='Confirm Attack',
            content=(
                Text(f'{self.selected_unit.name} attacks tile ({target_x}, {target_y})'),
                Text(f'Attack damage: {self.selected_unit.physical_attack}'),
                Text(f'Units in effect area: {unit_names}'),
                confirm_btn,
                cancel_btn
            ),
            popup=True
        )
        
        # Center the window panel
        self.attack_modal.y = self.attack_modal.panel.scale_y / 2 * self.attack_modal.scale_y
        self.attack_modal.layout()
    
    def get_units_in_effect_area(self, target_x, target_y):
        """Get all units within the attack effect area"""
        affected_units = []
        effect_radius = self.selected_unit.attack_effect_area
        
        for x in range(self.grid.width):
            for y in range(self.grid.height):
                # Calculate distance from target tile
                distance = abs(x - target_x) + abs(y - target_y)
                
                # Check if tile is within effect area and has a unit
                if distance <= effect_radius and (x, y) in self.grid.units:
                    unit = self.grid.units[(x, y)]
                    # Don't include the attacking unit itself
                    if unit != self.selected_unit:
                        affected_units.append(unit)
        
        return affected_units
            
    def show_movement_confirmation(self):
        """Show modal to confirm unit movement"""
        if not self.path_cursor or not self.selected_unit:
            return
            
        # Create confirmation buttons
        confirm_btn = Button(text='Confirm Move', color=color.green)
        cancel_btn = Button(text='Cancel', color=color.red)
        
        # Set up button callbacks
        def confirm_move():
            self.execute_movement()
            self.movement_modal.enabled = False
            destroy(self.movement_modal)
            self.movement_modal = None
            
        def cancel_move():
            self.movement_modal.enabled = False
            destroy(self.movement_modal)
            self.movement_modal = None
        
        confirm_btn.on_click = confirm_move
        cancel_btn.on_click = cancel_move
        
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
            self.update_unit_positions()
            # Clear selection and path
            self.selected_unit = None
            self.current_path = []
            self.path_cursor = None
            self.clear_highlights()
            control_panel.update_unit_info(None)
            print(f"Unit moved successfully. Press END TURN when ready.")
    
    def is_valid_move_destination(self, x, y):
        """Check if a position is within the unit's movement range"""
        if not self.selected_unit:
            return False
            
        # Calculate total distance from unit's starting position
        total_distance = abs(x - self.selected_unit.x) + abs(y - self.selected_unit.y)
        
        # Check if within movement points and valid grid position
        return (total_distance <= self.selected_unit.current_move_points and 
                0 <= x < self.grid.width and 
                0 <= y < self.grid.height and
                (x, y) not in self.grid.units)
    
    def update_path_highlights(self):
        """Update tile highlights to show movement range and current path"""
        # Clear existing highlights
        self.clear_highlights()
        
        if not self.selected_unit:
            return
            
        # Highlight selected unit
        self.highlight_selected_unit()
        
        # Highlight all valid movement tiles
        self.highlight_movement_range()
        
        # Highlight current path in blue (override green)
        for pos in self.current_path:
            highlight = Entity(
                model='cube',
                color=color.blue,
                scale=(0.9, 0.2, 0.9),
                position=(pos[0] + 0.5, 0, pos[1] + 0.5),  # Center on tile, same level as grid
                alpha=0.5  # Same transparency as grid
            )
            # Store in a list for cleanup
            if not hasattr(self, 'highlight_entities'):
                self.highlight_entities = []
            self.highlight_entities.append(highlight)
        
        # Highlight cursor position in yellow
        if self.path_cursor:
            highlight = Entity(
                model='cube',
                color=color.yellow,
                scale=(0.9, 0.2, 0.9),
                position=(self.path_cursor[0] + 0.5, 0, self.path_cursor[1] + 0.5),  # Center on tile, same level as grid
                alpha=0.5  # Same transparency as grid
            )
            if not hasattr(self, 'highlight_entities'):
                self.highlight_entities = []
            self.highlight_entities.append(highlight)
                    
    def highlight_attack_range(self, unit):
        """Highlight all tiles within the unit's attack range in red"""
        if not unit:
            return
        
        # Clear existing highlights first
        self.clear_highlights()
        
        for x in range(self.grid.width):
            for y in range(self.grid.height):
                # Calculate Manhattan distance from unit to tile
                distance = abs(x - unit.x) + abs(y - unit.y)
                
                # Highlight tiles within attack range (excluding unit's own tile)
                if distance <= unit.attack_range and distance > 0:
                    # Check if tile is within grid bounds
                    if 0 <= x < self.grid.width and 0 <= y < self.grid.height:
                        # Create highlight overlay entity
                        highlight = Entity(
                            model='cube',
                            color=color.red,
                            scale=(0.9, 0.2, 0.9),
                            position=(x + 0.5, 0, y + 0.5),  # Center on tile, same level as grid
                            alpha=0.5  # Same transparency as grid
                        )
                        # Store in a list for cleanup
                        if not hasattr(self, 'highlight_entities'):
                            self.highlight_entities = []
                        self.highlight_entities.append(highlight)
                    
    def clear_highlights(self):
        # Clear unit highlighting
        for entity in self.unit_entities:
            entity.unhighlight()
        
        # Clear tile highlight entities
        if hasattr(self, 'highlight_entities'):
            for highlight in self.highlight_entities:
                destroy(highlight)
            self.highlight_entities = []
        
        # Clear tile highlighting through modular system (if available)
        if self.tile_highlighter:
            self.tile_highlighter.clear_all_highlights()

    def refresh_all_ap(self):
        for unit in self.units:
            unit.ap = unit.max_ap
            unit.current_move_points = unit.move_points  # Reset movement points

    def update_unit_positions(self):
        for entity in self.unit_entities:
            entity.position = (entity.unit.x + 0.5, 1.0, entity.unit.y + 0.5)  # Center on grid tiles
from ursina.prefabs.window_panel import WindowPanel

class ControlPanel:
    def __init__(self):
        # Current unit info text
        self.unit_info_text = Text('No unit selected')
        
        # Camera controls text
        self.camera_controls_text = Text('CAMERA: [1] Orbit | [2] Free | [3] Top-down | ACTIVE: Orbit')
        
        # Game controls text
        self.game_controls_text = Text('CONTROLS: Click unit to select | Click tile to move | Mouse/WASD for camera')
        
        # Stats display text
        self.stats_display_text = Text('')
        
        # Create action buttons first
        self.end_turn_btn = Button(
            text='END TURN',
            color=color.orange
        )
        
        self.attack_btn = Button(
            text='ATTACK',
            color=color.red
        )
        
        self.defend_btn = Button(
            text='DEFEND',
            color=color.blue
        )
        
        # Set up button functionality
        self.end_turn_btn.on_click = self.end_turn_clicked
        self.attack_btn.on_click = self.attack_clicked
        self.defend_btn.on_click = self.defend_clicked
        
        # Create main window panel with all content including buttons
        self.panel = WindowPanel(
            title='Tactical RPG Control Panel',
            content=(
                self.unit_info_text,
                self.camera_controls_text,
                self.game_controls_text,
                self.stats_display_text,
                Text('Actions:'),  # Label for buttons
                self.end_turn_btn,
                self.attack_btn,
                self.defend_btn
            ),
            popup=False
        )
        
        # Position the control panel at the bottom
        self.panel.x = 0
        self.panel.y = -0.3
        
        # Layout the content within the panel
        self.panel.layout()
    
    def end_turn_clicked(self):
        print("End Turn button clicked!")
        if hasattr(self, 'game_reference') and self.game_reference:
            self.game_reference.end_current_turn()
    
    def attack_clicked(self):
        print("Attack button clicked!")
        # TODO: Implement attack functionality
    
    def defend_clicked(self):
        print("Defend button clicked!")
        # TODO: Implement defend functionality
    
    def set_game_reference(self, game):
        """Set reference to the main game object for button interactions"""
        self.game_reference = game
    
    def update_unit_info(self, unit):
        if unit:
            self.unit_info_text.text = f"ACTIVE: {unit.name} ({unit.type.value}) | MP: {unit.current_move_points}/{unit.move_points} | HP: {unit.hp}/{unit.max_hp}"
            self.stats_display_text.text = f"ATK - Physical: {unit.physical_attack} | Magical: {unit.magical_attack} | Spiritual: {unit.spiritual_attack}\nDEF - Physical: {unit.physical_defense} | Magical: {unit.magical_defense} | Spiritual: {unit.spiritual_defense}"
        else:
            self.unit_info_text.text = "No unit selected"
            self.stats_display_text.text = ""
        
        # Re-layout after text changes
        self.panel.layout()
    
    def update_camera_mode(self, mode):
        mode_names = ["Orbit", "Free", "Top-down"]
        self.camera_controls_text.text = f"CAMERA: [1] Orbit | [2] Free | [3] Top-down | ACTIVE: {mode_names[mode]}"
        
        # Re-layout after text changes
        self.panel.layout()

# Create control panel
control_panel = ControlPanel()

def input(key):
    # Handle mouse clicks for tile selection
    if key == 'left mouse down':
        # Check if clicking on a unit first
        if mouse.hovered_entity and hasattr(mouse.hovered_entity, 'unit'):
            return  # Let unit entity handle its own click
        
        # Handle tile clicks using world coordinates
        mouse_pos = mouse.world_point
        if mouse_pos:
            # Convert world position to grid coordinates
            # Floor the coordinates to get the grid tile
            grid_x = int(mouse_pos.x) if mouse_pos.x >= 0 else -1
            grid_z = int(mouse_pos.z) if mouse_pos.z >= 0 else -1
            
            # Check if click is within grid bounds
            if 0 <= grid_x < 8 and 0 <= grid_z < 8:
                game.handle_tile_click(grid_x, grid_z)
        return
    
    # Handle path movement for selected unit ONLY if in move mode
    if (game.selected_unit and game.current_mode == "move" and 
        key in ['w', 'a', 's', 'd', 'enter']):
        game.handle_path_movement(key)
        return  # Don't process camera controls if unit is selected and WASD/Enter is pressed
    
    # Handle camera controls only if not handling unit movement
    game.camera_controller.handle_input(key)

# Initialize game
game = TacticalRPG()

# Set game reference for control panel
control_panel.set_game_reference(game)

def update():
    # Update ECS World - this processes all systems
    try:
        game.world.update(time.dt)
    except Exception as e:
        print(f"⚠ ECS World update error: {e}")
    
    # Update camera
    game.camera_controller.handle_mouse_input()
    game.camera_controller.update_camera()
    
    # Update interaction manager (if available)
    if game.interaction_manager:
        try:
            game.interaction_manager.update(time.dt)
        except Exception as e:
            print(f"⚠ InteractionManager update error: {e}")
    
    # Update control panel with current unit info
    if game.turn_manager and game.turn_manager.current_unit() and not game.selected_unit:
        control_panel.update_unit_info(game.turn_manager.current_unit())

# Set initial camera position
game.camera_controller.update_camera()

# Add lighting
DirectionalLight(y=10, z=5)

app.run()
