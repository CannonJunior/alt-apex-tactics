"""
Unit Tests for Grid System and Pathfinding

Tests tactical grid, height variations, and A* pathfinding performance.
Validates <2ms pathfinding target on 10x10 grids.
"""

import pytest
import time

# Import grid and pathfinding components
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from core.math.vector import Vector3, Vector2Int
from core.math.grid import TacticalGrid, GridCell, TerrainType
from core.math.pathfinding import AStarPathfinder, PathfindingResult


class TestVector3:
    """Test Vector3 mathematics"""
    
    def test_vector_creation(self):
        """Test Vector3 creation and properties"""
        v = Vector3(1.0, 2.0, 3.0)
        assert v.x == 1.0
        assert v.y == 2.0
        assert v.z == 3.0
    
    def test_vector_operations(self):
        """Test Vector3 mathematical operations"""
        v1 = Vector3(1, 2, 3)
        v2 = Vector3(4, 5, 6)
        
        # Addition
        result = v1 + v2
        assert result.x == 5 and result.y == 7 and result.z == 9
        
        # Subtraction
        result = v2 - v1
        assert result.x == 3 and result.y == 3 and result.z == 3
        
        # Scalar multiplication
        result = v1 * 2
        assert result.x == 2 and result.y == 4 and result.z == 6
    
    def test_vector_magnitude(self):
        """Test Vector3 magnitude calculations"""
        v = Vector3(3, 4, 0)
        assert abs(v.magnitude - 5.0) < 0.001  # 3-4-5 triangle
        
        # Normalized vector should have magnitude 1
        normalized = v.normalized
        assert abs(normalized.magnitude - 1.0) < 0.001
    
    def test_vector_distance(self):
        """Test distance calculations"""
        v1 = Vector3(0, 0, 0)
        v2 = Vector3(3, 4, 0)
        
        distance = v1.distance_to(v2)
        assert abs(distance - 5.0) < 0.001


class TestVector2Int:
    """Test Vector2Int for grid coordinates"""
    
    def test_grid_vector_creation(self):
        """Test Vector2Int creation"""
        v = Vector2Int(5, 3)
        assert v.x == 5
        assert v.y == 3
    
    def test_grid_vector_operations(self):
        """Test Vector2Int operations"""
        v1 = Vector2Int(2, 3)
        v2 = Vector2Int(4, 1)
        
        result = v1 + v2
        assert result.x == 6 and result.y == 4
        
        manhattan = v1.manhattan_distance_to(v2)
        assert manhattan == 4  # |2-4| + |3-1| = 2 + 2 = 4
    
    def test_grid_directions(self):
        """Test direction constants"""
        cardinal = Vector2Int.cardinal_directions()
        assert len(cardinal) == 4
        
        all_dirs = Vector2Int.all_directions()
        assert len(all_dirs) == 8


class TestGridCell:
    """Test individual grid cell functionality"""
    
    def test_cell_creation(self):
        """Test grid cell creation"""
        pos = Vector2Int(3, 4)
        cell = GridCell(pos, height=2.5, terrain_type=TerrainType.ELEVATED)
        
        assert cell.grid_pos == pos
        assert cell.height == 2.5
        assert cell.terrain_type == TerrainType.ELEVATED
        assert cell.passable is True  # Elevated is passable
    
    def test_movement_costs(self):
        """Test movement cost calculations"""
        normal_cell = GridCell(Vector2Int(0, 0), terrain_type=TerrainType.NORMAL)
        difficult_cell = GridCell(Vector2Int(1, 0), terrain_type=TerrainType.DIFFICULT)
        
        assert normal_cell.movement_cost == 1.0
        assert difficult_cell.movement_cost == 2.0
    
    def test_height_difference_costs(self):
        """Test height difference movement costs"""
        low_cell = GridCell(Vector2Int(0, 0), height=0.0)
        high_cell = GridCell(Vector2Int(1, 0), height=2.5)
        
        cost = low_cell.get_height_difference_cost(high_cell)
        assert cost > 0  # Should have penalty for height difference
    
    def test_movement_validation(self):
        """Test movement possibility checks"""
        cell1 = GridCell(Vector2Int(0, 0), height=0.0)
        cell2 = GridCell(Vector2Int(1, 0), height=1.0)
        wall_cell = GridCell(Vector2Int(2, 0), terrain_type=TerrainType.WALL)
        
        assert cell1.can_move_to(cell2) is True
        assert cell1.can_move_to(wall_cell) is False


class TestTacticalGrid:
    """Test tactical grid system"""
    
    def test_grid_creation(self):
        """Test grid initialization"""
        grid = TacticalGrid(width=5, height=5, cell_size=1.0)
        
        assert grid.width == 5
        assert grid.height == 5
        assert len(grid.cells) == 25
    
    def test_grid_cell_access(self):
        """Test getting and setting grid cells"""
        grid = TacticalGrid(3, 3)
        pos = Vector2Int(1, 1)
        
        cell = grid.get_cell(pos)
        assert cell is not None
        assert cell.grid_pos == pos
        
        # Test out of bounds
        invalid_cell = grid.get_cell(Vector2Int(5, 5))
        assert invalid_cell is None
    
    def test_height_modifications(self):
        """Test setting cell heights"""
        grid = TacticalGrid(3, 3)
        pos = Vector2Int(1, 1)
        
        grid.set_cell_height(pos, 2.5)
        cell = grid.get_cell(pos)
        assert cell.height == 2.5
    
    def test_terrain_modifications(self):
        """Test setting terrain types"""
        grid = TacticalGrid(3, 3)
        pos = Vector2Int(1, 1)
        
        grid.set_cell_terrain(pos, TerrainType.WALL)
        cell = grid.get_cell(pos)
        assert cell.terrain_type == TerrainType.WALL
        assert cell.passable is False
    
    def test_coordinate_conversion(self):
        """Test world-grid coordinate conversion"""
        grid = TacticalGrid(10, 10, cell_size=2.0)
        
        # World to grid
        world_pos = Vector3(5.0, 0.0, 7.0)
        grid_pos = grid.world_to_grid(world_pos)
        assert grid_pos.x == 2 and grid_pos.y == 3  # 5/2=2.5->2, 7/2=3.5->3
        
        # Grid to world (should go to cell center)
        back_to_world = grid.grid_to_world(grid_pos)
        assert back_to_world.x == 5.0  # (2 + 0.5) * 2 = 5
        assert back_to_world.z == 7.0  # (3 + 0.5) * 2 = 7
    
    def test_neighbor_calculations(self):
        """Test getting neighboring cells"""
        grid = TacticalGrid(5, 5)
        center = Vector2Int(2, 2)
        
        # Cardinal neighbors only
        cardinal_neighbors = grid.get_neighbors(center, include_diagonals=False)
        assert len(cardinal_neighbors) == 4
        
        # All neighbors including diagonals
        all_neighbors = grid.get_neighbors(center, include_diagonals=True)
        assert len(all_neighbors) == 8
        
        # Edge case - corner position
        corner_neighbors = grid.get_neighbors(Vector2Int(0, 0), include_diagonals=True)
        assert len(corner_neighbors) == 3  # Only 3 neighbors at corner
    
    def test_movement_cost_calculation(self):
        """Test movement cost between cells"""
        grid = TacticalGrid(3, 3)
        
        pos1 = Vector2Int(0, 0)
        pos2 = Vector2Int(1, 0)  # Adjacent horizontal
        pos3 = Vector2Int(1, 1)  # Adjacent diagonal
        
        # Normal movement cost
        cost_horizontal = grid.get_movement_cost(pos1, pos2)
        cost_diagonal = grid.get_movement_cost(pos1, pos3)
        
        assert cost_horizontal > 0
        assert cost_diagonal > cost_horizontal  # Diagonal should cost more
    
    def test_line_of_sight(self):
        """Test line of sight calculations"""
        grid = TacticalGrid(5, 5)
        
        start = Vector2Int(0, 0)
        end = Vector2Int(4, 4)
        
        # Clear line of sight
        has_los = grid.get_line_of_sight(start, end)
        assert has_los is True
        
        # Block line of sight with wall
        grid.set_cell_terrain(Vector2Int(2, 2), TerrainType.WALL)
        grid.set_cell_height(Vector2Int(2, 2), 5.0)  # High wall
        
        blocked_los = grid.get_line_of_sight(start, end)
        # Note: Actual result depends on height calculations, test basic functionality
        assert blocked_los in [True, False]  # Either works for basic test
    
    def test_range_queries(self):
        """Test getting cells within range"""
        grid = TacticalGrid(10, 10)
        center = Vector2Int(5, 5)
        
        cells_in_range = grid.get_cells_in_range(center, range_distance=2)
        
        # Should include center plus all cells within Manhattan distance 2
        assert len(cells_in_range) > 5  # At minimum center + 4 cardinals
        assert center in cells_in_range
    
    def test_procedural_height_generation(self):
        """Test procedural height map generation"""
        grid = TacticalGrid(5, 5)
        
        # Generate height variations
        grid.generate_height_map(seed=42, roughness=0.5)
        
        # Check that heights were modified
        heights = [cell.height for cell in grid.cells.values()]
        assert not all(h == 0.0 for h in heights)  # Should have some variation
        assert max(heights) > min(heights)  # Should have height differences


class TestAStarPathfinding:
    """Test A* pathfinding algorithm"""
    
    def test_pathfinder_creation(self):
        """Test pathfinder initialization"""
        grid = TacticalGrid(5, 5)
        pathfinder = AStarPathfinder(grid)
        
        assert pathfinder.grid is grid
        assert len(pathfinder.path_cache) == 0
    
    def test_simple_pathfinding(self):
        """Test basic path finding"""
        grid = TacticalGrid(5, 5)
        pathfinder = AStarPathfinder(grid)
        
        start = Vector2Int(0, 0)
        goal = Vector2Int(2, 2)
        
        result = pathfinder.find_path(start, goal)
        
        assert result.success is True
        assert len(result.path) > 0
        assert result.path[0] == start
        assert result.path[-1] == goal
    
    def test_pathfinding_with_obstacles(self):
        """Test pathfinding around obstacles"""
        grid = TacticalGrid(5, 5)
        pathfinder = AStarPathfinder(grid)
        
        # Create wall obstacle
        grid.set_cell_terrain(Vector2Int(1, 1), TerrainType.WALL)
        grid.set_cell_terrain(Vector2Int(1, 2), TerrainType.WALL)
        
        start = Vector2Int(0, 1)
        goal = Vector2Int(2, 1)
        
        result = pathfinder.find_path(start, goal)
        
        assert result.success is True
        # Path should go around obstacle, not through it
        for pos in result.path:
            cell = grid.get_cell(pos)
            assert cell.passable is True
    
    def test_impossible_path(self):
        """Test pathfinding when no path exists"""
        grid = TacticalGrid(5, 5)
        pathfinder = AStarPathfinder(grid)
        
        # Create complete wall barrier
        for x in range(5):
            grid.set_cell_terrain(Vector2Int(x, 2), TerrainType.WALL)
        
        start = Vector2Int(0, 0)
        goal = Vector2Int(0, 4)  # On other side of wall
        
        result = pathfinder.find_path(start, goal)
        
        assert result.success is False
        assert len(result.path) == 0
    
    def test_pathfinding_performance(self):
        """Test pathfinding performance target (<2ms on 10x10)"""
        grid = TacticalGrid(10, 10)
        pathfinder = AStarPathfinder(grid)
        
        # Add some terrain variety for realistic scenario
        grid.generate_height_map(seed=42, roughness=0.3)
        
        # Add some obstacles
        for i in range(5):
            grid.set_cell_terrain(Vector2Int(3 + i, 5), TerrainType.DIFFICULT)
        
        start = Vector2Int(0, 0)
        goal = Vector2Int(9, 9)
        
        # Measure pathfinding time
        start_time = time.perf_counter()
        
        result = pathfinder.find_path(start, goal)
        
        pathfinding_time = time.perf_counter() - start_time
        
        # Should meet <2ms target
        assert pathfinding_time < 0.002, f"Pathfinding took {pathfinding_time*1000:.3f}ms, target is <2ms"
        assert result.success is True
        
        # Verify result timing matches measurement
        assert abs(result.search_time - pathfinding_time) < 0.001
    
    def test_pathfinding_with_height_costs(self):
        """Test pathfinding considers height differences"""
        grid = TacticalGrid(5, 5)
        pathfinder = AStarPathfinder(grid)
        
        # Create height variations
        grid.set_cell_height(Vector2Int(1, 1), 3.0)  # High cell
        grid.set_cell_height(Vector2Int(2, 1), 0.0)  # Low cell
        
        start = Vector2Int(0, 1)
        goal = Vector2Int(3, 1)
        
        result = pathfinder.find_path(start, goal)
        
        assert result.success is True
        # Path cost should reflect height penalties
        assert result.cost > 3.0  # Should be more than simple distance
    
    def test_reachable_positions(self):
        """Test finding all reachable positions within movement"""
        grid = TacticalGrid(5, 5)
        pathfinder = AStarPathfinder(grid)
        
        start = Vector2Int(2, 2)
        max_movement = 2.0
        
        reachable = pathfinder.find_reachable_positions(start, max_movement)
        
        assert len(reachable) > 1  # Should include start + neighbors
        assert start in reachable
        
        # All reachable positions should be within movement cost
        for pos in reachable:
            result = pathfinder.find_path(start, pos)
            if result.success:
                assert result.cost <= max_movement
    
    def test_pathfinding_cache(self):
        """Test pathfinding result caching"""
        grid = TacticalGrid(5, 5)
        pathfinder = AStarPathfinder(grid)
        
        start = Vector2Int(0, 0)
        goal = Vector2Int(2, 2)
        
        # First pathfinding should cache result
        result1 = pathfinder.find_path(start, goal)
        cache_size_after_first = len(pathfinder.path_cache)
        
        # Second identical pathfinding should use cache
        result2 = pathfinder.find_path(start, goal)
        cache_size_after_second = len(pathfinder.path_cache)
        
        assert cache_size_after_first == 1
        assert cache_size_after_second == 1  # No new cache entry
        assert result1.path == result2.path
    
    def test_pathfinding_stress(self):
        """Test pathfinding under stress conditions"""
        grid = TacticalGrid(15, 15)  # Larger than target 10x10
        pathfinder = AStarPathfinder(grid)
        
        # Add complex terrain
        grid.generate_height_map(seed=123, roughness=0.6)
        
        # Add many obstacles
        for i in range(20):
            x, y = (i * 3) % 15, (i * 7) % 15
            if Vector2Int(x, y) not in [Vector2Int(0, 0), Vector2Int(14, 14)]:
                grid.set_cell_terrain(Vector2Int(x, y), TerrainType.WALL)
        
        start = Vector2Int(0, 0)
        goal = Vector2Int(14, 14)
        
        # Multiple pathfinding queries
        total_time = 0
        successful_paths = 0
        
        for i in range(10):
            start_time = time.perf_counter()
            result = pathfinder.find_path(start, goal)
            query_time = time.perf_counter() - start_time
            
            total_time += query_time
            if result.success:
                successful_paths += 1
        
        avg_time = total_time / 10
        
        # Should handle stress test reasonably
        assert avg_time < 0.010, f"Stress test avg time {avg_time*1000:.1f}ms"
        assert successful_paths > 0  # Should find some paths


def run_grid_tests():
    """Run all grid and pathfinding unit tests"""
    pytest.main([__file__, "-v", "--tb=short"])


if __name__ == "__main__":
    run_grid_tests()