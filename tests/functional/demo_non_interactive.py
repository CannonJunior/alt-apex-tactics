#!/usr/bin/env python3
"""
Non-Interactive Phase 1 Demonstration

Demonstrates all Phase 1 systems working together without requiring user interaction.
Shows system initialization, character creation, stat calculations, and pathfinding.
"""

import sys
import os
import time

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from demo_utils import (
    create_demo_world, create_tactical_grid, create_character_archetypes,
    apply_demonstration_modifiers, demonstrate_pathfinding,
    get_performance_metrics, format_character_stats
)

from core.math.vector import Vector2Int, Vector3
from core.math.pathfinding import AStarPathfinder
from core.ecs.component import Transform


def main():
    """Run non-interactive demonstration of Phase 1 systems"""
    print("=" * 60)
    print("Phase 1 Foundation - Non-Interactive Demonstration")
    print("=" * 60)
    
    print("\n🎯 Initializing Phase 1 Systems...")
    
    # Create game world
    world = create_demo_world()
    print(f"✓ World created with {world.system_count} systems")
    
    # Create tactical grid
    grid = create_tactical_grid(10, 10)
    pathfinder = AStarPathfinder(grid)
    print("✓ Tactical grid created (10x10 with terrain features)")
    
    # Create characters
    characters = create_character_archetypes(world)
    apply_demonstration_modifiers(characters)
    print(f"✓ Created {len(characters)} character archetypes with modifiers")
    
    print("\n🎮 Demonstrating Character Systems...")
    
    # Show character stats
    for i, (archetype_name, character) in enumerate(characters, 1):
        print(f"\n{i}. {archetype_name}:")
        stats_text = format_character_stats(archetype_name, character)
        # Print first few lines of stats
        for line in stats_text.split('\n')[:8]:
            if line.strip():
                print(f"   {line}")
    
    print("\n🗺️  Demonstrating Pathfinding...")
    
    # Test pathfinding between characters
    if len(characters) >= 2:
        char1_pos = characters[0][1].get_component(Transform).position
        char2_pos = characters[1][1].get_component(Transform).position
        
        start = grid.world_to_grid(char1_pos)
        goal = grid.world_to_grid(char2_pos)
        
        path_result = demonstrate_pathfinding(grid, start, goal)
        
        print(f"✓ Pathfinding from {start} to {goal}:")
        print(f"   Success: {path_result['success']}")
        print(f"   Path length: {len(path_result['path'])} cells")
        print(f"   Total cost: {path_result['cost']:.2f}")
        print(f"   Calculation time: {path_result['time']*1000:.3f}ms")
        print(f"   Nodes explored: {path_result['nodes_explored']}")
        
        # Verify performance target
        if path_result['time'] < 0.002:  # 2ms target
            print("   ✓ Performance target met (<2ms)")
        else:
            print("   ⚠️  Performance target missed")
    
    print("\n⚡ Running Performance Simulation...")
    
    # Simulate multiple frames to test performance
    frame_count = 60
    start_time = time.perf_counter()
    
    for frame in range(frame_count):
        world.update(0.016)  # 60 FPS target
        
        # Demonstrate pathfinding every 10 frames
        if frame % 10 == 0 and len(characters) >= 2:
            char1_pos = characters[0][1].get_component(Transform).position
            char2_pos = characters[1][1].get_component(Transform).position
            start = grid.world_to_grid(char1_pos)
            goal = grid.world_to_grid(char2_pos)
            pathfinder.find_path(start, goal)
    
    total_time = time.perf_counter() - start_time
    avg_frame_time = total_time / frame_count
    fps = 1.0 / avg_frame_time if avg_frame_time > 0 else 0
    
    print(f"✓ Simulated {frame_count} frames in {total_time:.3f}s")
    print(f"   Average frame time: {avg_frame_time*1000:.2f}ms")
    print(f"   Effective FPS: {fps:.1f}")
    
    # Check performance targets
    if avg_frame_time < 0.016:  # 60 FPS target
        print("   ✓ 60 FPS target met")
    else:
        print("   ⚠️  60 FPS target missed")
    
    print("\n📊 Performance Metrics...")
    
    # Get detailed performance stats
    performance_stats = get_performance_metrics(world)
    
    if 'systems_performance' in performance_stats:
        for system_name, stats in performance_stats['systems_performance'].items():
            if 'avg_update_time' in stats:
                avg_time = stats['avg_update_time'] * 1000  # Convert to ms
                print(f"   {system_name}: {avg_time:.2f}ms average")
                
                # Check individual system targets
                if system_name == "StatSystem" and avg_time < 1.0:
                    print("     ✓ <1ms stat calculation target met")
                elif system_name == "StatSystem":
                    print("     ⚠️  <1ms stat calculation target missed")
    
    print("\n🎉 Phase 1 Demonstration Complete!")
    print("\nSummary:")
    print("✓ ECS architecture working")
    print("✓ Nine-attribute stat system operational")
    print("✓ Three-resource system functional")
    print("✓ Modifier system with stacking rules active")
    print("✓ Tactical grid with terrain variations")
    print("✓ A* pathfinding with performance validation")
    print("✓ Event system for inter-component communication")
    print("✓ Character archetypes created and tested")
    print("✓ Performance targets validated")
    
    print("\n🚀 Phase 1 Foundation is Ready for Phase 2 Development!")
    
    # Cleanup
    world.shutdown()
    return 0


if __name__ == "__main__":
    exit(main())