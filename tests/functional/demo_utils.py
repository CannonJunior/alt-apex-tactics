"""
Demo Utilities for Phase 1 Functional Demonstration

Utility functions for creating demonstration scenarios and visual aids.
"""

import random
from typing import List, Tuple

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from core.ecs.world import World
from core.ecs.component import Transform
from core.math.vector import Vector3, Vector2Int
from core.math.grid import TacticalGrid, TerrainType
from core.math.pathfinding import AStarPathfinder
from components.stats.attributes import AttributeStats
from components.stats.resources import ResourceManager
from components.stats.modifiers import ModifierManager, Modifier, ModifierType
from systems.stat_system import StatSystem
from systems.movement_system import MovementSystem


def create_demo_world() -> World:
    """Create a world with all Phase 1 systems for demonstration"""
    world = World()
    
    # Add all implemented systems
    world.add_system(StatSystem())
    world.add_system(MovementSystem())
    
    world.initialize()
    return world


def create_tactical_grid(width: int = 10, height: int = 10) -> TacticalGrid:
    """Create a demonstration tactical grid with interesting features"""
    grid = TacticalGrid(width, height, cell_size=1.0)
    
    # Generate height variations
    grid.generate_height_map(seed=42, roughness=0.4)
    
    # Add strategic terrain features
    # Create a small fortress area
    fortress_positions = [
        Vector2Int(7, 7), Vector2Int(8, 7), Vector2Int(9, 7),
        Vector2Int(7, 8), Vector2Int(8, 8), Vector2Int(9, 8),
        Vector2Int(7, 9), Vector2Int(8, 9), Vector2Int(9, 9)
    ]
    
    for pos in fortress_positions:
        if grid.get_cell(pos):
            grid.set_cell_terrain(pos, TerrainType.ELEVATED)
            grid.set_cell_height(pos, 2.0)
    
    # Add some obstacles
    obstacles = [Vector2Int(3, 5), Vector2Int(4, 5), Vector2Int(5, 3)]
    for pos in obstacles:
        if grid.get_cell(pos):
            grid.set_cell_terrain(pos, TerrainType.WALL)
    
    # Add difficult terrain
    difficult_areas = [Vector2Int(2, 7), Vector2Int(6, 2), Vector2Int(1, 8)]
    for pos in difficult_areas:
        if grid.get_cell(pos):
            grid.set_cell_terrain(pos, TerrainType.DIFFICULT)
    
    return grid


def create_character_archetypes(world: World) -> List:
    """Create different character archetypes for demonstration"""
    characters = []
    
    # Warrior archetype
    warrior = world.create_entity(
        Transform(Vector3(1.5, 0, 1.5)),  # Grid position (1, 1)
        AttributeStats(
            strength=16, fortitude=15, finesse=11,
            wisdom=8, wonder=6, worthy=12,
            faith=7, spirit=9, speed=10
        ),
        ResourceManager(max_mp=60, max_rage=150),
        ModifierManager()
    )
    characters.append(('Warrior', warrior))
    
    # Mage archetype
    mage = world.create_entity(
        Transform(Vector3(2.5, 0, 8.5)),  # Grid position (2, 8)
        AttributeStats(
            strength=7, fortitude=9, finesse=10,
            wisdom=17, wonder=16, worthy=14,
            faith=12, spirit=13, speed=8
        ),
        ResourceManager(max_mp=220, max_rage=40),
        ModifierManager()
    )
    characters.append(('Mage', mage))
    
    # Rogue archetype
    rogue = world.create_entity(
        Transform(Vector3(8.5, 0, 2.5)),  # Grid position (8, 2)
        AttributeStats(
            strength=11, fortitude=10, finesse=17,
            wisdom=12, wonder=8, worthy=13,
            faith=6, spirit=7, speed=18
        ),
        ResourceManager(max_mp=90, max_rage=100),
        ModifierManager()
    )
    characters.append(('Rogue', rogue))
    
    # Paladin archetype
    paladin = world.create_entity(
        Transform(Vector3(0.5, 0, 9.5)),  # Grid position (0, 9)
        AttributeStats(
            strength=14, fortitude=16, finesse=9,
            wisdom=11, wonder=10, worthy=17,
            faith=16, spirit=15, speed=7
        ),
        ResourceManager(max_mp=140, max_rage=80),
        ModifierManager()
    )
    characters.append(('Paladin', paladin))
    
    return characters


def apply_demonstration_modifiers(characters: List[Tuple[str, any]]):
    """Apply various modifiers to demonstrate the modifier system"""
    for archetype_name, character in characters:
        modifier_manager = character.get_component(ModifierManager)
        
        if archetype_name == 'Warrior':
            # Battle fury
            fury = Modifier("strength", ModifierType.FLAT, 4, duration=60.0)
            modifier_manager.add_modifier(fury)
            
            # Armor bonus
            armor = Modifier("fortitude", ModifierType.FLAT, 2, duration=300.0)
            modifier_manager.add_modifier(armor)
        
        elif archetype_name == 'Mage':
            # Arcane focus
            focus = Modifier("wisdom", ModifierType.PERCENTAGE, 0.15, duration=120.0)
            modifier_manager.add_modifier(focus)
            
            # Mana efficiency
            efficiency = Modifier("wonder", ModifierType.FLAT, 3, duration=180.0)
            modifier_manager.add_modifier(efficiency)
        
        elif archetype_name == 'Rogue':
            # Shadow step
            agility = Modifier("speed", ModifierType.FLAT, 5, duration=45.0)
            modifier_manager.add_modifier(agility)
            
            # Precise strikes
            precision = Modifier("finesse", ModifierType.PERCENTAGE, 0.2, duration=90.0)
            modifier_manager.add_modifier(precision)
        
        elif archetype_name == 'Paladin':
            # Divine blessing
            blessing = Modifier("worthy", ModifierType.FLAT, 3, duration=240.0)
            modifier_manager.add_modifier(blessing)
            
            # Sacred protection
            protection = Modifier("spirit", ModifierType.FLAT, 4, duration=200.0)
            modifier_manager.add_modifier(protection)


def demonstrate_pathfinding(grid: TacticalGrid, start: Vector2Int, goal: Vector2Int) -> dict:
    """Demonstrate pathfinding capabilities and return results"""
    pathfinder = AStarPathfinder(grid)
    
    import time
    start_time = time.perf_counter()
    result = pathfinder.find_path(start, goal)
    pathfinding_time = time.perf_counter() - start_time
    
    return {
        'success': result.success,
        'path': result.path,
        'cost': result.cost,
        'time': pathfinding_time,
        'nodes_explored': result.nodes_explored
    }


def get_performance_metrics(world: World) -> dict:
    """Get performance metrics from all systems"""
    metrics = {
        'total_entities': len(world.entity_manager._entities),
        'systems_count': world.system_count,
        'systems_performance': {}
    }
    
    # Get performance data from each system
    for system in world.system_manager._systems:
        if hasattr(system, 'get_performance_stats'):
            metrics['systems_performance'][system.name] = system.get_performance_stats()
    
    return metrics


def create_demo_scenario_description() -> str:
    """Create description of the demonstration scenario"""
    return """
Phase 1 Foundation Demonstration
===============================

This demonstration showcases all Phase 1 systems working together:

Systems Demonstrated:
- Entity-Component-System (ECS) Architecture
- Nine-Attribute Stat System with Derived Stats
- Three-Resource System (MP, Rage, Kwan)
- Advanced Modifier System with Stacking Rules
- Tactical Grid with Height Variations
- A* Pathfinding with Terrain Costs
- Event System for Inter-System Communication
- MCP Server Integration for AI Analysis

Character Archetypes:
1. Warrior - High Strength/Fortitude, focused on physical combat
2. Mage - High Wisdom/Wonder, magical specialist
3. Rogue - High Finesse/Speed, agility-focused
4. Paladin - High Worthy/Faith, divine magic user

Interactive Controls:
- WASD: Move camera
- Space: Pause/Resume simulation
- R: Reset simulation
- P: Toggle pathfinding visualization
- 1-4: Focus on character archetype
- ESC: Exit demonstration

Performance Targets:
- <1ms stat calculations
- <2ms pathfinding on 10x10 grid
- <5ms visual updates
- 60 FPS maintenance with 50+ entities
"""


def format_character_stats(archetype_name: str, character) -> str:
    """Format character stats for display"""
    attributes = character.get_component(AttributeStats)
    resources = character.get_component(ResourceManager)
    modifiers = character.get_component(ModifierManager)
    
    derived = attributes.derived_stats
    
    stats_text = f"\n{archetype_name} Stats:\n"
    stats_text += f"STR: {attributes.strength:2d} | FOR: {attributes.fortitude:2d} | FIN: {attributes.finesse:2d}\n"
    stats_text += f"WIS: {attributes.wisdom:2d} | WON: {attributes.wonder:2d} | WOR: {attributes.worthy:2d}\n"
    stats_text += f"FAI: {attributes.faith:2d} | SPI: {attributes.spirit:2d} | SPD: {attributes.speed:2d}\n"
    stats_text += f"\nDerived Stats:\n"
    stats_text += f"HP: {derived['hp']:3d} | MP: {derived['mp']:3d} | Phys Att: {derived['physical_attack']:2d}\n"
    stats_text += f"Phys Def: {derived['physical_defense']:2d} | Mag Att: {derived['magical_attack']:2d}\n"
    stats_text += f"Move Spd: {derived['movement_speed']:2d} | Initiative: {derived['initiative']:2d}\n"
    stats_text += f"\nResources:\n"
    stats_text += f"MP: {resources.mp.current_value}/{resources.mp.max_value}\n"
    stats_text += f"Rage: {resources.rage.current_value}/{resources.rage.max_value}\n"
    stats_text += f"Kwan: {resources.kwan.current_value}\n"
    
    # Show active modifiers
    active_modifiers = []
    for stat_name in ['strength', 'wisdom', 'finesse', 'speed']:
        mods = modifiers.get_modifiers_for_stat(stat_name)
        active_modifiers.extend(mods)
    
    if active_modifiers:
        stats_text += f"\nActive Modifiers: {len(active_modifiers)}\n"
    
    return stats_text


def get_grid_cell_description(grid: TacticalGrid, pos: Vector2Int) -> str:
    """Get description of a grid cell for display"""
    cell = grid.get_cell(pos)
    if not cell:
        return "Invalid position"
    
    terrain_names = {
        TerrainType.NORMAL: "Normal",
        TerrainType.DIFFICULT: "Difficult",
        TerrainType.ELEVATED: "Elevated",
        TerrainType.WALL: "Wall"
    }
    
    terrain_name = terrain_names.get(cell.terrain_type, "Unknown")
    
    return f"({pos.x}, {pos.y}): {terrain_name} terrain, height {cell.height:.1f}"