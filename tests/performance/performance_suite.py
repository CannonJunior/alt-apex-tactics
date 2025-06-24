"""
Performance Validation Suite

Comprehensive performance tests validating all Phase 1 targets from Advanced-Implementation-Guide.md.
Tests must pass to ensure Phase 1 foundation meets requirements.
"""

import pytest
import time
import psutil
import os
from typing import List, Dict, Any

import sys
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


class PerformanceTargets:
    """Performance targets from Advanced-Implementation-Guide.md"""
    STAT_CALCULATION_TIME = 0.001  # <1ms
    PATHFINDING_TIME = 0.002       # <2ms on 10x10 grid
    VISUAL_UPDATE_TIME = 0.005     # <5ms
    FRAME_TIME_60FPS = 0.0167      # ~16.7ms for 60 FPS
    MAX_ENTITIES_60FPS = 50        # Maintain 60 FPS with 50+ entities


class PerformanceTestSuite:
    """Comprehensive performance validation suite"""
    
    def __init__(self):
        self.results = {}
        self.process = psutil.Process(os.getpid())
    
    def measure_memory_usage(self) -> float:
        """Get current memory usage in MB"""
        return self.process.memory_info().rss / 1024 / 1024
    
    def time_function(self, func, *args, iterations: int = 1, **kwargs) -> Dict[str, float]:
        """Time a function execution and return statistics"""
        times = []
        
        for _ in range(iterations):
            start_time = time.perf_counter()
            result = func(*args, **kwargs)
            elapsed = time.perf_counter() - start_time
            times.append(elapsed)
        
        return {
            'min_time': min(times),
            'max_time': max(times),
            'avg_time': sum(times) / len(times),
            'total_time': sum(times),
            'iterations': iterations,
            'result': result if iterations == 1 else None
        }
    
    def test_stat_calculation_performance(self) -> Dict[str, Any]:
        """Test stat calculation performance target (<1ms)"""
        print("Testing stat calculation performance...")
        
        # Create complex character with many derived stats
        stats = AttributeStats(
            strength=15, fortitude=12, finesse=14,
            wisdom=16, wonder=13, worthy=11,
            faith=9, spirit=10, speed=13
        )
        
        # Test single calculation
        single_result = self.time_function(lambda: stats.derived_stats, iterations=1)
        
        # Test repeated calculations (should use cache)
        repeated_result = self.time_function(lambda: stats.derived_stats, iterations=100)
        
        # Test with modifiers
        modifier_manager = ModifierManager()
        for i in range(10):
            mod = Modifier(f"strength", ModifierType.FLAT, i, duration=60.0)
            modifier_manager.add_modifier(mod)
        
        complex_result = self.time_function(
            lambda: modifier_manager.calculate_final_stat(15, "strength"),
            iterations=100
        )
        
        results = {
            'single_calculation': single_result,
            'repeated_calculations': repeated_result,
            'complex_modifiers': complex_result,
            'target_met': {
                'single': single_result['avg_time'] < PerformanceTargets.STAT_CALCULATION_TIME,
                'repeated': repeated_result['avg_time'] < PerformanceTargets.STAT_CALCULATION_TIME,
                'complex': complex_result['avg_time'] < PerformanceTargets.STAT_CALCULATION_TIME
            }
        }
        
        print(f"  Single calculation: {single_result['avg_time']*1000:.3f}ms")
        print(f"  Repeated calculations: {repeated_result['avg_time']*1000:.3f}ms")
        print(f"  Complex modifiers: {complex_result['avg_time']*1000:.3f}ms")
        print(f"  Target (<1ms): {'✓ PASS' if all(results['target_met'].values()) else '✗ FAIL'}")
        
        return results
    
    def test_pathfinding_performance(self) -> Dict[str, Any]:
        """Test pathfinding performance target (<2ms on 10x10)"""
        print("Testing pathfinding performance...")
        
        grid = TacticalGrid(10, 10)
        grid.generate_height_map(seed=42, roughness=0.3)
        
        # Add some obstacles for realistic scenario
        obstacles = [
            Vector2Int(3, 3), Vector2Int(3, 4), Vector2Int(3, 5),
            Vector2Int(7, 2), Vector2Int(8, 2), Vector2Int(9, 2)
        ]
        for pos in obstacles:
            grid.set_cell_terrain(pos, TerrainType.WALL)
        
        pathfinder = AStarPathfinder(grid)
        
        # Test various pathfinding scenarios
        test_cases = [
            (Vector2Int(0, 0), Vector2Int(9, 9)),  # Corner to corner
            (Vector2Int(0, 5), Vector2Int(9, 5)),  # Horizontal
            (Vector2Int(5, 0), Vector2Int(5, 9)),  # Vertical
            (Vector2Int(1, 1), Vector2Int(8, 8)),  # Diagonal
            (Vector2Int(2, 2), Vector2Int(6, 6))   # Around obstacles
        ]
        
        scenario_results = {}
        all_times = []
        
        for i, (start, goal) in enumerate(test_cases):
            result = self.time_function(
                lambda s=start, g=goal: pathfinder.find_path(s, g),
                iterations=20
            )
            scenario_results[f'scenario_{i+1}'] = result
            all_times.extend([result['min_time'], result['max_time'], result['avg_time']])
        
        # Test pathfinding stress (larger grid)
        large_grid = TacticalGrid(15, 15)
        large_pathfinder = AStarPathfinder(large_grid)
        stress_result = self.time_function(
            lambda: large_pathfinder.find_path(Vector2Int(0, 0), Vector2Int(14, 14)),
            iterations=10
        )
        
        max_time = max(all_times)
        avg_time = sum(all_times) / len(all_times)
        
        results = {
            'scenarios': scenario_results,
            'stress_test': stress_result,
            'overall_stats': {
                'max_time': max_time,
                'avg_time': avg_time,
                'target_met': max_time < PerformanceTargets.PATHFINDING_TIME
            }
        }
        
        print(f"  Best case: {min(all_times)*1000:.3f}ms")
        print(f"  Worst case: {max_time*1000:.3f}ms")
        print(f"  Average: {avg_time*1000:.3f}ms")
        print(f"  Target (<2ms): {'✓ PASS' if results['overall_stats']['target_met'] else '✗ FAIL'}")
        
        return results
    
    def test_ecs_performance(self) -> Dict[str, Any]:
        """Test ECS system performance with many entities"""
        print("Testing ECS performance...")
        
        world = World()
        world.add_system(StatSystem())
        world.add_system(MovementSystem())
        world.initialize()
        
        # Create entities gradually and measure performance
        entity_counts = [10, 25, 50, 100]
        results_by_count = {}
        
        entities = []
        for target_count in entity_counts:
            # Add entities to reach target count
            while len(entities) < target_count:
                entity = world.create_entity(
                    Transform(Vector3(len(entities) % 10, 0, len(entities) // 10)),
                    AttributeStats(
                        strength=10 + len(entities) % 8,
                        wisdom=10 + len(entities) % 6
                    ),
                    ResourceManager(),
                    ModifierManager()
                )
                entities.append(entity)
            
            # Measure update performance
            update_result = self.time_function(
                lambda dt=0.016: world.update(dt),
                iterations=60  # Simulate 1 second at 60 FPS
            )
            
            maintains_60fps = update_result['avg_time'] < PerformanceTargets.FRAME_TIME_60FPS
            
            results_by_count[f'{target_count}_entities'] = {
                'update_time': update_result,
                'maintains_60fps': maintains_60fps,
                'fps_estimate': 1.0 / update_result['avg_time'] if update_result['avg_time'] > 0 else float('inf')
            }
            
            print(f"  {target_count} entities: {update_result['avg_time']*1000:.2f}ms avg, "
                  f"~{results_by_count[f'{target_count}_entities']['fps_estimate']:.1f} FPS")
        
        # Test entity creation/destruction performance
        creation_result = self.time_function(
            lambda: world.create_entity(Transform(), AttributeStats()),
            iterations=100
        )
        
        # Test component queries
        query_result = self.time_function(
            lambda: world.entity_manager.get_entities_with_component(AttributeStats),
            iterations=100
        )
        
        world.shutdown()
        
        results = {
            'entity_performance': results_by_count,
            'creation_performance': creation_result,
            'query_performance': query_result,
            'target_met_50_entities': results_by_count.get('50_entities', {}).get('maintains_60fps', False)
        }
        
        return results
    
    def test_memory_performance(self) -> Dict[str, Any]:
        """Test memory usage and cleanup"""
        print("Testing memory performance...")
        
        initial_memory = self.measure_memory_usage()
        
        world = World()
        world.add_system(StatSystem())
        world.initialize()
        
        # Create and destroy entities in cycles
        memory_samples = [initial_memory]
        
        for cycle in range(5):
            # Create entities
            entities = []
            for i in range(20):
                entity = world.create_entity(
                    Transform(),
                    AttributeStats(),
                    ResourceManager(),
                    ModifierManager()
                )
                entities.append(entity.id)
            
            memory_samples.append(self.measure_memory_usage())
            
            # Update world
            for _ in range(10):
                world.update(0.016)
            
            # Destroy half the entities
            for entity_id in entities[::2]:
                world.destroy_entity(entity_id)
            
            world.entity_manager.cleanup_destroyed_entities()
            memory_samples.append(self.measure_memory_usage())
        
        world.shutdown()
        final_memory = self.measure_memory_usage()
        memory_samples.append(final_memory)
        
        results = {
            'initial_memory': initial_memory,
            'final_memory': final_memory,
            'memory_increase': final_memory - initial_memory,
            'peak_memory': max(memory_samples),
            'memory_samples': memory_samples,
            'reasonable_usage': (final_memory - initial_memory) < 100  # Less than 100MB increase
        }
        
        print(f"  Initial: {initial_memory:.1f}MB")
        print(f"  Final: {final_memory:.1f}MB")
        print(f"  Increase: {results['memory_increase']:.1f}MB")
        print(f"  Peak: {results['peak_memory']:.1f}MB")
        print(f"  Memory usage: {'✓ REASONABLE' if results['reasonable_usage'] else '✗ EXCESSIVE'}")
        
        return results
    
    def test_integration_performance(self) -> Dict[str, Any]:
        """Test integrated system performance"""
        print("Testing integration performance...")
        
        # Create full system with all components
        world = World()
        world.add_system(StatSystem())
        world.add_system(MovementSystem())
        world.initialize()
        
        grid = TacticalGrid(10, 10)
        grid.generate_height_map(seed=42, roughness=0.4)
        pathfinder = AStarPathfinder(grid)
        
        # Create entities with complex setups
        entities = []
        for i in range(25):
            entity = world.create_entity(
                Transform(Vector3(i % 5, 0, i // 5)),
                AttributeStats(
                    strength=10 + i % 8,
                    wisdom=10 + i % 6,
                    speed=10 + i % 10
                ),
                ResourceManager(),
                ModifierManager()
            )
            entities.append(entity)
            
            # Add modifiers for complexity
            modifier_manager = entity.get_component(ModifierManager)
            for j in range(3):
                mod = Modifier(
                    ['strength', 'wisdom', 'speed'][j],
                    ModifierType.FLAT,
                    j + 1,
                    duration=60.0
                )
                modifier_manager.add_modifier(mod)
        
        # Test full update cycle with pathfinding
        def full_update_cycle():
            world.update(0.016)
            
            # Perform some pathfinding
            if len(entities) >= 2:
                pos1 = entities[0].get_component(Transform).position
                pos2 = entities[-1].get_component(Transform).position
                
                grid_pos1 = grid.world_to_grid(pos1)
                grid_pos2 = grid.world_to_grid(pos2)
                
                pathfinder.find_path(grid_pos1, grid_pos2)
        
        # Test integrated performance
        integration_result = self.time_function(full_update_cycle, iterations=60)
        
        world.shutdown()
        
        results = {
            'integration_performance': integration_result,
            'maintains_60fps': integration_result['avg_time'] < PerformanceTargets.FRAME_TIME_60FPS,
            'performance_margin': PerformanceTargets.FRAME_TIME_60FPS - integration_result['avg_time']
        }
        
        print(f"  Integrated update: {integration_result['avg_time']*1000:.2f}ms")
        print(f"  60 FPS target: {'✓ PASS' if results['maintains_60fps'] else '✗ FAIL'}")
        print(f"  Performance margin: {results['performance_margin']*1000:.2f}ms")
        
        return results
    
    def run_full_suite(self) -> Dict[str, Any]:
        """Run complete performance validation suite"""
        print("="*60)
        print("PHASE 1 PERFORMANCE VALIDATION SUITE")
        print("="*60)
        
        start_time = time.time()
        
        # Run all performance tests
        self.results['stat_calculations'] = self.test_stat_calculation_performance()
        print()
        
        self.results['pathfinding'] = self.test_pathfinding_performance()
        print()
        
        self.results['ecs_systems'] = self.test_ecs_performance()
        print()
        
        self.results['memory_usage'] = self.test_memory_performance()
        print()
        
        self.results['integration'] = self.test_integration_performance()
        print()
        
        total_time = time.time() - start_time
        
        # Summary
        print("="*60)
        print("PERFORMANCE VALIDATION SUMMARY")
        print("="*60)
        
        passed_tests = []
        failed_tests = []
        
        # Check all targets
        if all(self.results['stat_calculations']['target_met'].values()):
            passed_tests.append("Stat Calculations (<1ms)")
        else:
            failed_tests.append("Stat Calculations (<1ms)")
        
        if self.results['pathfinding']['overall_stats']['target_met']:
            passed_tests.append("Pathfinding (<2ms)")
        else:
            failed_tests.append("Pathfinding (<2ms)")
        
        if self.results['ecs_systems']['target_met_50_entities']:
            passed_tests.append("ECS Performance (50+ entities @ 60 FPS)")
        else:
            failed_tests.append("ECS Performance (50+ entities @ 60 FPS)")
        
        if self.results['memory_usage']['reasonable_usage']:
            passed_tests.append("Memory Usage")
        else:
            failed_tests.append("Memory Usage")
        
        if self.results['integration']['maintains_60fps']:
            passed_tests.append("Integration Performance")
        else:
            failed_tests.append("Integration Performance")
        
        print(f"PASSED ({len(passed_tests)}):")
        for test in passed_tests:
            print(f"  ✓ {test}")
        
        if failed_tests:
            print(f"\nFAILED ({len(failed_tests)}):")
            for test in failed_tests:
                print(f"  ✗ {test}")
        
        overall_pass = len(failed_tests) == 0
        
        print(f"\nOVERALL RESULT: {'✓ ALL TARGETS MET' if overall_pass else '✗ SOME TARGETS FAILED'}")
        print(f"Total test time: {total_time:.2f}s")
        
        self.results['summary'] = {
            'passed_tests': passed_tests,
            'failed_tests': failed_tests,
            'overall_pass': overall_pass,
            'total_time': total_time
        }
        
        return self.results


def run_performance_suite():
    """Run the complete performance validation suite"""
    suite = PerformanceTestSuite()
    return suite.run_full_suite()


if __name__ == "__main__":
    results = run_performance_suite()
    
    # Exit with error code if any tests failed
    if not results['summary']['overall_pass']:
        exit(1)