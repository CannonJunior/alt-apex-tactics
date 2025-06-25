"""
Integration Tests for Phase 4 Visual Systems

Tests for visual system integration, performance, and Ursina compatibility.
"""

import unittest
import time
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from core.ecs.entity import Entity
from core.ecs.component import Transform
from core.ecs.world import World
from core.math.vector import Vector3, Vector2Int
from core.math.grid import TacticalGrid
from core.math.pathfinding import AStarPathfinder
from components.stats.attributes import AttributeStats
from components.combat.attack import AttackComponent
from components.combat.damage import DamageComponent
from core.utils.profiler import PerformanceProfiler


class TestVisualSystemsIntegration(unittest.TestCase):
    """Integration tests for visual systems without requiring Ursina"""
    
    def setUp(self):
        self.world = World()
        self.grid_system = TacticalGrid(10, 10, cell_size=1.0)
        self.pathfinding = AStarPathfinder(self.grid_system)
        self.profiler = PerformanceProfiler()
        
        # Create test entities
        self.test_entities = []
        for i in range(5):
            entity = Entity()
            entity.add_component(Transform(Vector3(i * 2, 0, 5)))
            entity.add_component(AttributeStats(
                strength=10 + i,
                speed=8 + i,
                fortitude=9 + i,
                wisdom=7 + i
            ))
            entity.add_component(AttackComponent(attack_range=3))
            entity.add_component(DamageComponent(physical_power=15))
            
            self.test_entities.append(entity)
    
    def test_grid_visualizer_without_ursina(self):
        """Test GridVisualizer core functionality without Ursina"""
        # Import without Ursina dependency
        from ui.visual.grid_visualizer import GridVisualizer, HighlightType
        
        visualizer = GridVisualizer(self.grid_system, self.pathfinding)
        
        # Test basic highlighting
        test_pos = Vector2Int(5, 5)
        visualizer.add_tile_highlight(test_pos, HighlightType.MOVEMENT)
        
        self.assertTrue(visualizer.is_tile_highlighted(test_pos, HighlightType.MOVEMENT))
        self.assertEqual(len(visualizer.get_highlighted_tiles()), 1)
        
        # Test multiple highlights
        visualizer.add_tile_highlight(test_pos, HighlightType.ATTACK_RANGE)
        self.assertEqual(len(visualizer.get_tile_highlights(test_pos)), 2)
        
        # Test highlight removal
        visualizer.remove_tile_highlight(test_pos, HighlightType.MOVEMENT)
        self.assertFalse(visualizer.is_tile_highlighted(test_pos, HighlightType.MOVEMENT))
        self.assertTrue(visualizer.is_tile_highlighted(test_pos, HighlightType.ATTACK_RANGE))
        
        # Test clear all
        visualizer.clear_all_highlights()
        self.assertEqual(len(visualizer.get_highlighted_tiles()), 0)
    
    def test_grid_visualizer_performance(self):
        """Test GridVisualizer performance meets targets"""
        from ui.visual.grid_visualizer import GridVisualizer, HighlightType
        
        visualizer = GridVisualizer(self.grid_system, self.pathfinding)
        
        # Test update performance (should be <5ms for full battlefield refresh)
        with self.profiler.measure('visual_updates'):
            # Simulate heavy highlighting workload
            for x in range(10):
                for y in range(10):
                    visualizer.add_tile_highlight(Vector2Int(x, y), HighlightType.MOVEMENT)
            
            # Update multiple times
            for _ in range(10):
                visualizer.update(0.016)  # 60 FPS
        
        stats = self.profiler.get_stats('visual_updates')
        self.assertIsNotNone(stats)
        self.assertLess(stats.average_time, 0.005, "Visual updates should be <5ms")
    
    def test_unit_selection_and_highlighting(self):
        """Test unit selection and tactical highlighting integration"""
        from ui.visual.grid_visualizer import GridVisualizer, HighlightType
        
        visualizer = GridVisualizer(self.grid_system, self.pathfinding)
        selected_unit = self.test_entities[0]
        
        # Test unit selection
        visualizer.set_selected_unit(selected_unit)
        self.assertEqual(visualizer.selected_unit, selected_unit)
        
        # Test that selection triggers highlighting
        highlighted_tiles = visualizer.get_highlighted_tiles()
        self.assertGreater(len(highlighted_tiles), 0, "Unit selection should create highlights")
        
        # Test selection change
        new_unit = self.test_entities[1]
        visualizer.set_selected_unit(new_unit)
        self.assertEqual(visualizer.selected_unit, new_unit)
    
    def test_effect_area_highlighting(self):
        """Test area effect highlighting"""
        from ui.visual.grid_visualizer import GridVisualizer, HighlightType
        
        visualizer = GridVisualizer(self.grid_system, self.pathfinding)
        
        # Test circular area effect
        center = Vector2Int(5, 5)
        radius = 2
        
        visualizer.show_effect_area(center, radius, HighlightType.EFFECT_AREA)
        
        highlighted_tiles = visualizer.get_highlighted_tiles(HighlightType.EFFECT_AREA)
        self.assertGreater(len(highlighted_tiles), 0)
        
        # Verify tiles are within radius
        for tile_pos in highlighted_tiles:
            distance = abs(tile_pos.x - center.x) + abs(tile_pos.y - center.y)
            self.assertLessEqual(distance, radius)
    
    def test_movement_path_visualization(self):
        """Test movement path highlighting"""
        from ui.visual.grid_visualizer import GridVisualizer, HighlightType
        
        visualizer = GridVisualizer(self.grid_system, self.pathfinding)
        
        # Create a test path
        path = [Vector2Int(2, 2), Vector2Int(3, 2), Vector2Int(4, 2), Vector2Int(5, 2)]
        
        visualizer.show_movement_path(path)
        
        # Verify all path tiles are highlighted
        for tile_pos in path:
            self.assertTrue(visualizer.is_tile_highlighted(tile_pos, HighlightType.MOVEMENT_PATH))
        
        # Verify only path tiles are highlighted with movement_path
        path_highlights = visualizer.get_highlighted_tiles(HighlightType.MOVEMENT_PATH)
        self.assertEqual(len(path_highlights), len(path))
    
    def test_visual_data_generation(self):
        """Test visual data generation for rendering"""
        from ui.visual.grid_visualizer import GridVisualizer, HighlightType
        
        visualizer = GridVisualizer(self.grid_system, self.pathfinding)
        
        # Add various highlights
        test_tiles = [
            (Vector2Int(1, 1), HighlightType.MOVEMENT),
            (Vector2Int(2, 2), HighlightType.ATTACK_RANGE),
            (Vector2Int(3, 3), HighlightType.EFFECT_AREA)
        ]
        
        for tile_pos, highlight_type in test_tiles:
            visualizer.add_tile_highlight(tile_pos, highlight_type)
        
        # Test individual tile visual data
        visual_data = visualizer.get_visual_data_for_tile(Vector2Int(1, 1))
        self.assertIsNotNone(visual_data)
        self.assertIn('position', visual_data)
        self.assertIn('color', visual_data)
        self.assertIn('intensity', visual_data)
        
        # Test all visual data
        all_visual_data = visualizer.get_all_visual_data()
        self.assertEqual(len(all_visual_data), len(test_tiles))
    
    @patch('ui.visual.tile_highlighter.URSINA_AVAILABLE', False)
    def test_tile_highlighter_without_ursina(self):
        """Test that TileHighlighter fails gracefully without Ursina"""
        with self.assertRaises(ImportError):
            from ui.visual.tile_highlighter import TileHighlighter
            TileHighlighter(None)
    
    @patch('ui.visual.combat_animator.URSINA_AVAILABLE', False)
    def test_combat_animator_without_ursina(self):
        """Test that CombatAnimator fails gracefully without Ursina"""
        with self.assertRaises(ImportError):
            from ui.visual.combat_animator import CombatAnimator
            CombatAnimator()
    
    def test_animation_queue_management(self):
        """Test animation queue management without Ursina"""
        # Mock Ursina to test queue logic
        with patch('ui.visual.combat_animator.URSINA_AVAILABLE', True):
            with patch('ui.visual.combat_animator.Entity'), \
                 patch('ui.visual.combat_animator.Vec3'), \
                 patch('ui.visual.combat_animator.color'):
                
                from ui.visual.combat_animator import CombatAnimator, AnimationType
                
                animator = CombatAnimator()
                
                # Test queueing animations
                test_unit = self.test_entities[0]
                target_pos = Vector3(5, 0, 5)
                
                animator.queue_movement_animation(test_unit, target_pos, duration=1.0)
                self.assertEqual(len(animator.animation_queue), 1)
                
                # Test queue processing
                current_time = time.time()
                animator._process_animation_queue(current_time + 1.0)  # Future time
                self.assertEqual(len(animator.animation_queue), 0)  # Should be processed
    
    def test_interface_state_management(self):
        """Test interface state management without Ursina"""
        with patch('ui.interface.inventory_interface.URSINA_AVAILABLE', True):
            with patch('ui.interface.inventory_interface.Entity'), \
                 patch('ui.interface.inventory_interface.Text'), \
                 patch('ui.interface.inventory_interface.Button'):
                
                from ui.interface.inventory_interface import InventoryInterface, InterfaceMode
                
                interface = InventoryInterface()
                
                # Test initial state
                self.assertFalse(interface.is_visible)
                self.assertEqual(interface.current_mode, InterfaceMode.INVENTORY)
                
                # Test mode switching
                interface._set_mode(InterfaceMode.EQUIPMENT)
                self.assertEqual(interface.current_mode, InterfaceMode.EQUIPMENT)
                
                # Test show/hide
                test_unit = self.test_entities[0]
                interface.selected_unit = test_unit
                interface.is_visible = True
                
                self.assertTrue(interface.is_visible)
                self.assertEqual(interface.selected_unit, test_unit)
    
    def test_combat_interface_functionality(self):
        """Test combat interface functionality without Ursina"""
        with patch('ui.interface.combat_interface.URSINA_AVAILABLE', True):
            with patch('ui.interface.combat_interface.Entity'), \
                 patch('ui.interface.combat_interface.Text'), \
                 patch('ui.interface.combat_interface.Button'):
                
                from ui.interface.combat_interface import CombatInterface
                
                interface = CombatInterface()
                
                # Test initial state
                self.assertFalse(interface.is_visible)
                self.assertIsNone(interface.selected_unit)
                
                # Test unit selection
                test_unit = self.test_entities[0]
                interface.set_selected_unit(test_unit)
                self.assertEqual(interface.selected_unit, test_unit)
                
                # Test turn order update
                interface.update_turn_order(self.test_entities)
                # Should not raise any exceptions
    
    def test_performance_profiler_integration(self):
        """Test performance profiler with visual systems"""
        from ui.visual.grid_visualizer import GridVisualizer, HighlightType
        
        visualizer = GridVisualizer(self.grid_system, self.pathfinding)
        
        # Test profiled operations
        with self.profiler.measure('test_operation'):
            for i in range(100):
                visualizer.add_tile_highlight(Vector2Int(i % 10, i // 10), HighlightType.MOVEMENT)
        
        # Verify profiling worked
        stats = self.profiler.get_stats('test_operation')
        self.assertIsNotNone(stats)
        self.assertEqual(stats.total_calls, 1)
        self.assertGreater(stats.total_time, 0)
        
        # Test performance report
        report = self.profiler.get_performance_report()
        self.assertIn('measurement_count', report)
        self.assertIn('operations_tracked', report)
    
    def test_memory_usage_monitoring(self):
        """Test memory usage monitoring for visual systems"""
        from ui.visual.grid_visualizer import GridVisualizer, HighlightType
        
        visualizer = GridVisualizer(self.grid_system, self.pathfinding)
        
        # Create many highlights to test memory usage
        for x in range(50):
            for y in range(50):
                visualizer.add_tile_highlight(Vector2Int(x, y), HighlightType.MOVEMENT)
        
        # Test performance stats
        stats = visualizer.get_performance_stats()
        self.assertIn('active_highlights', stats)
        self.assertGreater(stats['active_highlights'], 0)
        
        # Test cleanup
        visualizer.clear_all_highlights()
        stats_after = visualizer.get_performance_stats()
        self.assertEqual(stats_after['active_highlights'], 0)
    
    def test_system_integration_without_errors(self):
        """Test that all systems can be imported and initialized without errors"""
        # Test core visual system imports
        from ui.visual.grid_visualizer import GridVisualizer, HighlightType
        from core.utils.profiler import PerformanceProfiler
        
        # These should not raise exceptions
        visualizer = GridVisualizer(self.grid_system, self.pathfinding)
        profiler = PerformanceProfiler()
        
        self.assertIsNotNone(visualizer)
        self.assertIsNotNone(profiler)
    
    def test_highlight_priority_system(self):
        """Test highlight priority and layering"""
        from ui.visual.grid_visualizer import GridVisualizer, HighlightType
        
        visualizer = GridVisualizer(self.grid_system, self.pathfinding)
        test_pos = Vector2Int(5, 5)
        
        # Add multiple highlight types to same tile
        highlights = [
            HighlightType.MOVEMENT,
            HighlightType.ATTACK_RANGE,
            HighlightType.SELECTION,
            HighlightType.DANGER_ZONE
        ]
        
        for highlight_type in highlights:
            visualizer.add_tile_highlight(test_pos, highlight_type)
        
        # Test that all highlights are tracked
        tile_highlights = visualizer.get_tile_highlights(test_pos)
        self.assertEqual(len(tile_highlights), len(highlights))
        
        # Test visual data returns appropriate priority
        visual_data = visualizer.get_visual_data_for_tile(test_pos)
        self.assertIsNotNone(visual_data)
        self.assertIn('highlight_types', visual_data)
        self.assertEqual(len(visual_data['highlight_types']), len(highlights))


class TestPerformanceTargets(unittest.TestCase):
    """Test that performance targets are met"""
    
    def setUp(self):
        self.profiler = PerformanceProfiler()
        self.grid_system = TacticalGrid(10, 10, cell_size=1.0)
        self.pathfinding = AStarPathfinder(self.grid_system)
    
    def test_pathfinding_performance_target(self):
        """Test pathfinding meets <2ms target on 10x10 grid"""
        start = Vector2Int(0, 0)
        end = Vector2Int(9, 9)
        
        # Warm up
        for _ in range(5):
            self.pathfinding.find_path(start, end)
        
        # Measure performance
        with self.profiler.measure('pathfinding'):
            for _ in range(10):
                path = self.pathfinding.find_path(start, end)
                self.assertIsNotNone(path)
        
        stats = self.profiler.get_stats('pathfinding')
        self.assertIsNotNone(stats)
        self.assertLess(stats.average_time, 0.002, f"Pathfinding took {stats.average_time*1000:.2f}ms, target is <2ms")
    
    def test_stat_calculation_performance_target(self):
        """Test stat calculations meet <1ms target"""
        entity = Entity()
        entity.add_component(AttributeStats(
            strength=15, fortitude=12, finesse=10,
            wisdom=8, wonder=9, worthy=11,
            faith=7, spirit=8, speed=12
        ))
        
        attributes = entity.get_component(AttributeStats)
        
        # Warm up
        for _ in range(5):
            stats = attributes.derived_stats
        
        # Measure performance
        with self.profiler.measure('stat_calculations'):
            for _ in range(100):
                stats = attributes.derived_stats
                self.assertIsInstance(stats, dict)
                self.assertIn('hp', stats)
                self.assertIn('mp', stats)
        
        stats = self.profiler.get_stats('stat_calculations')
        self.assertIsNotNone(stats)
        self.assertLess(stats.average_time, 0.001, f"Stat calculations took {stats.average_time*1000:.2f}ms, target is <1ms")
    
    def test_visual_update_performance_target(self):
        """Test visual updates meet <5ms target for full battlefield refresh"""
        from ui.visual.grid_visualizer import GridVisualizer, HighlightType
        
        visualizer = GridVisualizer(self.grid_system, self.pathfinding)
        
        # Create full battlefield of highlights
        for x in range(10):
            for y in range(10):
                highlight_type = [HighlightType.MOVEMENT, HighlightType.ATTACK_RANGE, 
                                HighlightType.EFFECT_AREA][x % 3]
                visualizer.add_tile_highlight(Vector2Int(x, y), highlight_type)
        
        # Measure update performance
        with self.profiler.measure('visual_updates'):
            for _ in range(20):
                visualizer.update(0.016)  # 60 FPS update rate
        
        stats = self.profiler.get_stats('visual_updates')
        self.assertIsNotNone(stats)
        self.assertLess(stats.average_time, 0.005, f"Visual updates took {stats.average_time*1000:.2f}ms, target is <5ms")


if __name__ == '__main__':
    # Create test suite
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTest(unittest.makeSuite(TestVisualSystemsIntegration))
    suite.addTest(unittest.makeSuite(TestPerformanceTargets))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print(f"\n=== Test Summary ===")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    if result.failures:
        print(f"\nFailures:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback}")
    
    if result.errors:
        print(f"\nErrors:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback}")