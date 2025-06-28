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
from ui.camera.camera_controller import CameraController
from ui.panels.control_panel import ControlPanel
from ui.panels import create_game_panels
from ui.visual.unit_renderer import UnitEntity
from game.legacy.unit_wrapper import Unit
from game.legacy.battle_grid_wrapper import BattleGrid
from game.legacy.turn_manager_wrapper import TurnManager
from game.factories.unit_factory import create_unit_entity
from game.controllers.tactical_rpg_controller import TacticalRPG

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



# Camera Control System

# Visual Components
# GridTile class removed - using modular GridVisualizer system instead


# Main Game Controller - now using imported TacticalRPG component

# Create control panel
control_panel = ControlPanel()

# Create game panels manager
game_panels = None  # Will be initialized after game creation

def input(key):
    # Check if game panels handle the input first
    if game_panels and game_panels.handle_game_input(key):
        return  # Panel handled the input
    
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

# Initialize game with control panel callback
game = TacticalRPG(control_panel_callback=lambda: control_panel)

# Set game reference for control panel
control_panel.set_game_reference(game)

# Initialize game panels after game creation
try:
    game_panels = create_game_panels(game)
    print("🎮 Game panels integrated successfully!")
    print("📋 Available panels: Character (C), Inventory (I), Talents (T), Party (P), Upgrade (U)")
except Exception as e:
    print(f"⚠️ Warning: Could not initialize game panels: {e}")
    game_panels = None

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
    
    # Update game panels with current character data
    if game_panels and game.selected_unit:
        game_panels.update_character_data(game.selected_unit)
    elif game_panels and game.turn_manager and game.turn_manager.current_unit():
        game_panels.update_character_data(game.turn_manager.current_unit())

# Set initial camera position
game.camera_controller.update_camera()

# Add lighting
DirectionalLight(y=10, z=5)

app.run()
