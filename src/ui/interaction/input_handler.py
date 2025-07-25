"""
Input Handler System

Centralized input handling for tactical RPG games. Coordinates input processing
across multiple game systems including panels, game logic, mouse interactions,
unit movement, and camera controls.
"""

from typing import Optional, Any

try:
    from ursina import mouse
    URSINA_AVAILABLE = True
except ImportError:
    URSINA_AVAILABLE = False


class InputHandler:
    """
    Central input handler that manages input processing across all game systems.
    
    Implements a hierarchical input handling system:
    1. Game panels (UI elements like character/inventory panels)
    2. Game-specific input (control panel toggles, etc.)
    3. Mouse tile selection (clicking on grid tiles)
    4. Unit movement controls (WASD + Enter for path movement)
    5. Camera controls (fallback for all other input)
    """
    
    def __init__(self, game_reference: Any, game_panels_manager: Optional[Any] = None):
        """
        Initialize the input handler.
        
        Args:
            game_reference: Reference to the main game controller (TacticalRPG)
            game_panels_manager: Optional reference to game panels manager
        """
        if not URSINA_AVAILABLE:
            raise ImportError("Ursina is required for InputHandler")
        
        self.game = game_reference
        self.game_panels = game_panels_manager
    
    def set_game_panels_manager(self, game_panels_manager: Any):
        """
        Set or update the game panels manager reference.
        
        Args:
            game_panels_manager: Game panels manager instance
        """
        self.game_panels = game_panels_manager
    
    def handle_input(self, key: str) -> bool:
        """
        Process input key through the hierarchical input system.
        
        Args:
            key: The input key that was pressed
            
        Returns:
            True if input was handled, False otherwise
        """
        # Check if game panels handle the input first
        if self.game_panels and hasattr(self.game_panels, 'handle_game_input'):
            if self.game_panels.handle_game_input(key):
                return True  # Panel handled the input
        
        # Handle game-specific input (including 'r' key for control panel toggle)
        if self.game and hasattr(self.game, 'handle_input'):
            if self.game.handle_input(key):
                return True  # Game handled the input
        
        # Handle mouse clicks for tile selection
        if key == 'left mouse down':
            if self._handle_mouse_click():
                return True
        
        # Handle path movement for selected unit ONLY if in move mode
        if self._handle_unit_movement(key):
            return True
        
        # Handle camera controls only if not handling unit movement
        if self._handle_camera_controls(key):
            return True
        
        return False
    
    def _handle_mouse_click(self) -> bool:
        """
        Handle left mouse click for tile selection.
        
        Returns:
            True if mouse click was handled, False otherwise
        """
        # Check if clicking on a unit first
        if mouse.hovered_entity and hasattr(mouse.hovered_entity, 'unit'):
            return False  # Let unit entity handle its own click
        
        # Handle tile clicks using world coordinates
        mouse_pos = mouse.world_point
        if mouse_pos:
            # Convert world position to grid coordinates
            # Floor the coordinates to get the grid tile
            grid_x = int(mouse_pos.x) if mouse_pos.x >= 0 else -1
            grid_z = int(mouse_pos.z) if mouse_pos.z >= 0 else -1
            
            # Check if click is within grid bounds
            if 0 <= grid_x < 8 and 0 <= grid_z < 8:
                if self.game and hasattr(self.game, 'handle_tile_click'):
                    self.game.handle_tile_click(grid_x, grid_z)
                    return True
        
        return True  # Mouse click was processed (even if no action taken)
    
    def _handle_unit_movement(self, key: str) -> bool:
        """
        Handle unit movement controls (WASD + Enter).
        
        Args:
            key: The input key
            
        Returns:
            True if movement input was handled, False otherwise
        """
        if not self.game:
            return False
        
        # Handle path movement for selected unit ONLY if in move mode
        if (hasattr(self.game, 'selected_unit') and self.game.selected_unit and 
            hasattr(self.game, 'current_mode') and self.game.current_mode == "move" and 
            key in ['w', 'a', 's', 'd', 'enter']):
            
            if hasattr(self.game, 'handle_path_movement'):
                self.game.handle_path_movement(key)
                return True  # Don't process camera controls if unit is selected and WASD/Enter is pressed
        
        return False
    
    def _handle_camera_controls(self, key: str) -> bool:
        """
        Handle camera controls as fallback input.
        
        Args:
            key: The input key
            
        Returns:
            True if camera input was handled, False otherwise
        """
        if (self.game and 
            hasattr(self.game, 'camera_controller') and 
            hasattr(self.game.camera_controller, 'handle_input')):
            
            self.game.camera_controller.handle_input(key)
            return True
        
        return False


def create_input_handler(game_reference: Any, game_panels_manager: Optional[Any] = None) -> InputHandler:
    """
    Factory function to create an input handler instance.
    
    Args:
        game_reference: Reference to the main game controller
        game_panels_manager: Optional reference to game panels manager
        
    Returns:
        Configured InputHandler instance
    """
    return InputHandler(game_reference, game_panels_manager)