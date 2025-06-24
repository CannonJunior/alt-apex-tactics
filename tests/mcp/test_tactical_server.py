"""
Unit Tests for Tactical MCP Server

Tests MCP server integration for AI tactical analysis.
Validates tools and resources with proper fallback handling.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from core.math.vector import Vector3, Vector2Int
from core.math.grid import TacticalGrid, TerrainType


class MockMCPServer:
    """Mock MCP server for testing"""
    
    def __init__(self):
        self.name = "TacticalRPG_AI_Server"
        self.version = "1.0.0"
        self.tools = []
        self.resources = []
        self.running = False
    
    def tool(self, name, description):
        def decorator(func):
            self.tools.append({'name': name, 'description': description, 'func': func})
            return func
        return decorator
    
    def resource(self, uri):
        def decorator(func):
            self.resources.append({'uri': uri, 'func': func})
            return func
        return decorator
    
    def run(self):
        self.running = True


class TestTacticalMCPServer:
    """Test tactical MCP server functionality"""
    
    @pytest.fixture
    def mock_fastmcp(self):
        """Mock FastMCP import"""
        mock_mcp = Mock()
        mock_mcp.FastMCP.return_value = MockMCPServer()
        
        with patch.dict('sys.modules', {'fastmcp': mock_mcp}):
            yield mock_mcp
    
    def test_server_creation_with_fastmcp(self, mock_fastmcp):
        """Test MCP server creation when FastMCP is available"""
        from ai.mcp.tactical_server import TacticalMCPServer
        
        server = TacticalMCPServer()
        assert server is not None
        assert server.mcp_available is True
    
    def test_server_creation_without_fastmcp(self):
        """Test MCP server creation when FastMCP is not available"""
        with patch.dict('sys.modules', {}, clear=False):
            # Remove fastmcp if it exists
            if 'fastmcp' in sys.modules:
                del sys.modules['fastmcp']
            
            from ai.mcp.tactical_server import TacticalMCPServer
            
            server = TacticalMCPServer()
            assert server is not None
            assert server.mcp_available is False
    
    def test_analyze_battlefield_tool(self, mock_fastmcp):
        """Test battlefield analysis tool"""
        from ai.mcp.tactical_server import TacticalMCPServer
        
        server = TacticalMCPServer()
        
        # Create test grid data
        grid_data = {
            'width': 5,
            'height': 5,
            'cells': [
                {'x': 0, 'y': 0, 'height': 0.0, 'terrain': 'normal'},
                {'x': 2, 'y': 2, 'height': 2.0, 'terrain': 'elevated'},
                {'x': 3, 'y': 3, 'height': 0.0, 'terrain': 'wall'}
            ]
        }
        
        # Test the analysis (would be mocked in real MCP environment)
        result = server._analyze_battlefield_impl(grid_data)
        
        assert 'terrain_analysis' in result
        assert 'strategic_positions' in result
        assert 'movement_corridors' in result
        assert len(result['strategic_positions']) > 0
    
    def test_evaluate_unit_positioning_tool(self, mock_fastmcp):
        """Test unit positioning evaluation tool"""
        from ai.mcp.tactical_server import TacticalMCPServer
        
        server = TacticalMCPServer()
        
        unit_data = {
            'position': {'x': 2, 'y': 3},
            'stats': {
                'strength': 15,
                'finesse': 12,
                'speed': 14
            },
            'role': 'warrior'
        }
        
        battlefield_context = {
            'allies': [{'x': 1, 'y': 2}],
            'enemies': [{'x': 4, 'y': 4}],
            'terrain': 'elevated'
        }
        
        result = server._evaluate_unit_positioning_impl(unit_data, battlefield_context)
        
        assert 'position_score' in result
        assert 'tactical_advantages' in result
        assert 'recommended_actions' in result
        assert isinstance(result['position_score'], (int, float))
    
    def test_calculate_movement_options_tool(self, mock_fastmcp):
        """Test movement options calculation tool"""
        from ai.mcp.tactical_server import TacticalMCPServer
        
        server = TacticalMCPServer()
        
        unit_data = {
            'position': {'x': 2, 'y': 2},
            'movement_speed': 3,
            'stats': {'speed': 12}
        }
        
        grid_data = {
            'width': 5,
            'height': 5,
            'obstacles': [{'x': 3, 'y': 3}]
        }
        
        result = server._calculate_movement_options_impl(unit_data, grid_data)
        
        assert 'reachable_positions' in result
        assert 'optimal_positions' in result
        assert 'movement_costs' in result
        assert len(result['reachable_positions']) > 0
    
    def test_predict_combat_outcome_tool(self, mock_fastmcp):
        """Test combat outcome prediction tool"""
        from ai.mcp.tactical_server import TacticalMCPServer
        
        server = TacticalMCPServer()
        
        attacker_data = {
            'stats': {
                'strength': 15,
                'finesse': 12,
                'fortitude': 13
            },
            'resources': {
                'hp': 150,
                'mp': 80,
                'rage': 30
            }
        }
        
        defender_data = {
            'stats': {
                'strength': 12,
                'finesse': 14,
                'fortitude': 16
            },
            'resources': {
                'hp': 180,
                'mp': 60,
                'rage': 0
            }
        }
        
        combat_context = {
            'terrain_bonus': 0.1,
            'height_advantage': True,
            'flanking': False
        }
        
        result = server._predict_combat_outcome_impl(attacker_data, defender_data, combat_context)
        
        assert 'win_probability' in result
        assert 'expected_damage' in result
        assert 'tactical_factors' in result
        assert 0 <= result['win_probability'] <= 1
    
    def test_tactical_knowledge_resource(self, mock_fastmcp):
        """Test tactical knowledge base resource"""
        from ai.mcp.tactical_server import TacticalMCPServer
        
        server = TacticalMCPServer()
        
        result = server._get_tactical_knowledge_impl()
        
        assert 'combat_mechanics' in result
        assert 'stat_formulas' in result
        assert 'terrain_effects' in result
        assert 'ability_descriptions' in result
        
        # Verify specific knowledge content
        assert 'physical_attack' in result['stat_formulas']
        assert 'elevated' in result['terrain_effects']
    
    def test_current_battlefield_state_resource(self, mock_fastmcp):
        """Test current battlefield state resource"""
        from ai.mcp.tactical_server import TacticalMCPServer
        
        server = TacticalMCPServer()
        
        # Set up mock battlefield state
        server.current_battlefield = {
            'grid': {'width': 8, 'height': 8},
            'units': [
                {'id': 1, 'position': {'x': 2, 'y': 3}, 'team': 'player'},
                {'id': 2, 'position': {'x': 5, 'y': 6}, 'team': 'enemy'}
            ],
            'turn_order': [1, 2],
            'current_turn': 1
        }
        
        result = server._get_battlefield_state_impl()
        
        assert 'grid_info' in result
        assert 'unit_positions' in result
        assert 'turn_information' in result
        assert len(result['unit_positions']) == 2
    
    def test_server_error_handling(self, mock_fastmcp):
        """Test error handling in MCP server operations"""
        from ai.mcp.tactical_server import TacticalMCPServer
        
        server = TacticalMCPServer()
        
        # Test with invalid data
        invalid_grid = {'invalid': 'data'}
        result = server._analyze_battlefield_impl(invalid_grid)
        
        # Should handle gracefully and return error information
        assert 'error' in result or 'terrain_analysis' in result
    
    def test_performance_with_large_battlefield(self, mock_fastmcp):
        """Test MCP server performance with large battlefield"""
        import time
        from ai.mcp.tactical_server import TacticalMCPServer
        
        server = TacticalMCPServer()
        
        # Create large grid data
        grid_data = {
            'width': 20,
            'height': 20,
            'cells': []
        }
        
        for x in range(20):
            for y in range(20):
                grid_data['cells'].append({
                    'x': x, 'y': y,
                    'height': (x + y) % 3,
                    'terrain': 'normal' if (x + y) % 4 != 0 else 'difficult'
                })
        
        start_time = time.perf_counter()
        result = server._analyze_battlefield_impl(grid_data)
        analysis_time = time.perf_counter() - start_time
        
        # Should complete analysis quickly even for large battlefield
        assert analysis_time < 0.1  # 100ms target
        assert 'terrain_analysis' in result
    
    def test_server_initialization_and_tools_registration(self, mock_fastmcp):
        """Test server initialization and tool registration"""
        from ai.mcp.tactical_server import TacticalMCPServer
        
        server = TacticalMCPServer()
        
        # Verify server was initialized
        assert hasattr(server, 'mcp_available')
        
        if server.mcp_available:
            # Verify tools and resources are properly defined
            assert hasattr(server, '_analyze_battlefield_impl')
            assert hasattr(server, '_evaluate_unit_positioning_impl')
            assert hasattr(server, '_calculate_movement_options_impl')
            assert hasattr(server, '_predict_combat_outcome_impl')
            assert hasattr(server, '_get_tactical_knowledge_impl')
            assert hasattr(server, '_get_battlefield_state_impl')


class TestMCPIntegrationWithGameSystems:
    """Test MCP server integration with game systems"""
    
    @pytest.fixture
    def sample_tactical_grid(self):
        """Create sample tactical grid for testing"""
        grid = TacticalGrid(8, 8)
        grid.generate_height_map(seed=42, roughness=0.3)
        
        # Add some strategic features
        grid.set_cell_terrain(Vector2Int(3, 3), TerrainType.ELEVATED)
        grid.set_cell_terrain(Vector2Int(5, 5), TerrainType.WALL)
        grid.set_cell_terrain(Vector2Int(2, 6), TerrainType.DIFFICULT)
        
        return grid
    
    def test_grid_data_conversion_for_mcp(self, sample_tactical_grid):
        """Test converting tactical grid to MCP-compatible format"""
        from ai.mcp.tactical_server import TacticalMCPServer
        
        server = TacticalMCPServer()
        
        # Convert grid to MCP format
        grid_data = server._convert_grid_to_mcp_format(sample_tactical_grid)
        
        assert 'width' in grid_data
        assert 'height' in grid_data
        assert 'cells' in grid_data
        assert grid_data['width'] == 8
        assert grid_data['height'] == 8
        assert len(grid_data['cells']) > 0
        
        # Check cell data format
        cell = grid_data['cells'][0]
        assert 'x' in cell
        assert 'y' in cell
        assert 'height' in cell
        assert 'terrain' in cell
    
    def test_mcp_server_with_real_game_state(self, mock_fastmcp, sample_tactical_grid):
        """Test MCP server analysis with real game state"""
        from ai.mcp.tactical_server import TacticalMCPServer
        
        server = TacticalMCPServer()
        
        # Update server with current game state
        server.update_battlefield_state({
            'grid': sample_tactical_grid,
            'units': [
                {'id': 1, 'position': Vector2Int(2, 2), 'team': 'player'},
                {'id': 2, 'position': Vector2Int(6, 6), 'team': 'enemy'}
            ]
        })
        
        # Perform analysis
        grid_data = server._convert_grid_to_mcp_format(sample_tactical_grid)
        result = server._analyze_battlefield_impl(grid_data)
        
        assert result is not None
        assert 'terrain_analysis' in result


def run_mcp_tests():
    """Run all MCP server tests"""
    pytest.main([__file__, "-v", "--tb=short"])


if __name__ == "__main__":
    run_mcp_tests()