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
from ui.interaction.input_handler import create_input_handler
from ui.camera.camera_controller import CameraController
from ui.panels.control_panel import ControlPanel
from ui.panels import create_game_panels
from ui.visual.unit_renderer import UnitEntity
from ui.visual.grid_utilities import create_clean_grid_lines, create_ground_plane
from game.legacy.unit_wrapper import Unit
from game.legacy.battle_grid_wrapper import BattleGrid
from game.legacy.turn_manager_wrapper import TurnManager
from game.factories.unit_factory import create_unit_entity
from game.controllers.tactical_rpg_controller import TacticalRPG

import random
import math

app = Ursina()

# Create a simple ground plane for better visibility  
ground = create_ground_plane()

# Create the clean grid
grid_entities = create_clean_grid_lines()

# Mouse detection now handled in the input() function using world coordinates



# Camera Control System

# Visual Components
# GridTile class removed - using modular GridVisualizer system instead


# Main Game Controller - now using imported TacticalRPG component

# Create control panel
control_panel = ControlPanel()

# Create game panels manager
game_panels = None  # Will be initialized after game creation

# Input handler will be initialized after game creation
input_handler = None

def input(key):
    """Global input function that delegates to the input handler."""
    if input_handler:
        input_handler.handle_input(key)

# Initialize game with control panel callback and direct control panel reference
game = TacticalRPG(control_panel_callback=lambda: control_panel, control_panel=control_panel)

# Initialize game panels after game creation
try:
    game_panels = create_game_panels(game)
    print("🎮 Game panels integrated successfully!")
    print("📋 Available panels: Character (C), Inventory (I), Talents (T), Party (P), Upgrade (U)")
except Exception as e:
    print(f"⚠️ Warning: Could not initialize game panels: {e}")
    game_panels = None

# Initialize input handler after game and panels are created
input_handler = create_input_handler(game, game_panels)
print("⌨️ Input handler initialized successfully!")

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
