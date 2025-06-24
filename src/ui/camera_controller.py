"""
Advanced Camera Controller for Ursina

Multi-mode camera system with orbit, free, and top-down modes.
Based on the excellent implementation from apex-tactics project.
"""

import math
from typing import Optional
try:
    from ursina import *
    import ursina
    URSINA_AVAILABLE = True
except ImportError:
    URSINA_AVAILABLE = False
    # Mock classes for when Ursina is not available
    class Vec3:
        def __init__(self, x=0, y=0, z=0):
            self.x, self.y, self.z = x, y, z

from core.math.vector import Vector3


class CameraController:
    """
    Advanced camera controller with multiple viewing modes.
    
    Modes:
    - 0: Orbit mode - Camera orbits around a target point
    - 1: Free mode - WASD movement with mouse look
    - 2: Top-down mode - Fixed overhead view with WASD panning
    """
    
    def __init__(self, grid_width: int = 10, grid_height: int = 10):
        """
        Initialize camera controller.
        
        Args:
            grid_width: Width of the tactical grid
            grid_height: Height of the tactical grid
        """
        self.grid_width = grid_width
        self.grid_height = grid_height
        
        # Calculate grid center
        if URSINA_AVAILABLE:
            self.grid_center = Vec3(grid_width/2 - 0.5, 0, grid_height/2 - 0.5)
            self.camera_target = Vec3(self.grid_center.x, self.grid_center.y, self.grid_center.z)
        else:
            self.grid_center = Vector3(grid_width/2 - 0.5, 0, grid_height/2 - 0.5)
            self.camera_target = Vector3(self.grid_center.x, self.grid_center.y, self.grid_center.z)
        
        # Camera parameters
        self.camera_distance = 8.0
        self.camera_angle_x = 30.0  # Vertical angle (elevation)
        self.camera_angle_y = 0.0   # Horizontal angle (azimuth)
        self.camera_mode = 0        # Always orbit mode (simplified)
        
        # Movement settings
        self.move_speed = 0.5
        self.rotation_speed = 50.0
        self.zoom_speed = 0.5
        
        # Limits
        self.min_distance = 3.0
        self.max_distance = 15.0
        self.min_elevation = -80.0
        self.max_elevation = 80.0
        
        # Initialize camera position
        self.update_camera()
    
    def update_camera(self):
        """Update camera position for orbit mode only."""
        if not URSINA_AVAILABLE:
            return
        
        try:
            # Always orbit mode
            self._update_orbit_camera()
        except Exception as e:
            pass
    
    def _update_orbit_camera(self):
        """Update camera for orbit mode - camera orbits around target point."""
        if not URSINA_AVAILABLE:
            return
        
        # Convert angles to radians
        rad_y = math.radians(self.camera_angle_y)
        rad_x = math.radians(self.camera_angle_x)
        
        # Calculate camera position using spherical coordinates
        x = self.camera_target.x + self.camera_distance * math.cos(rad_x) * math.sin(rad_y)
        y = self.camera_target.y + self.camera_distance * math.sin(rad_x)
        z = self.camera_target.z + self.camera_distance * math.cos(rad_x) * math.cos(rad_y)
        
        # Set camera position and look at target
        camera.position = (x, y, z)
        camera.look_at(self.camera_target)
    
    def _update_free_camera(self):
        """Update camera for free mode - manual movement and rotation."""
        # Free camera mode is handled directly by input functions
        # No automatic positioning needed
        pass
    
    def _update_topdown_camera(self):
        """Update camera for top-down mode - fixed overhead view."""
        if not URSINA_AVAILABLE:
            return
        
        # Position camera directly above target
        camera.position = (self.camera_target.x, 12, self.camera_target.z)
        camera.rotation = (90, 0, 0)
    
    def handle_input(self, key: str):
        """
        Handle keyboard input for camera control - orbit mode only.
        
        Args:
            key: The pressed key
        """
        # Handle scroll events for orbit mode
        if key == 'scroll up':
            self.zoom_in()
            return True
        elif key == 'scroll down':
            self.zoom_out()
            return True
        
        return False
    
    
    def handle_mouse_input(self):
        """Handle mouse input for camera control. This method should be called from main context where Ursina globals are accessible."""
        # This method is intentionally simplified since apex-tactics.py shows the working approach
        # is to handle continuous input directly in the main application context
        pass
    
    def set_camera_mode(self, mode: int):
        """
        Set camera mode.
        
        Args:
            mode: Camera mode (0=orbit, 1=free, 2=top-down)
        """
        old_mode = self.camera_mode
        self.camera_mode = max(0, min(2, mode))
        
        if old_mode != self.camera_mode:
            print(f"Camera mode changed to: {self.get_mode_name()}")
            
            # Reset camera parameters when switching modes
            if self.camera_mode == 0:  # Switching to orbit
                # Reset to default orbit position
                self.camera_angle_x = 30.0
                self.camera_angle_y = 0.0
                self.camera_distance = 8.0
            elif self.camera_mode == 1 and URSINA_AVAILABLE:  # Switching to free
                # Set a good starting position for free camera
                camera.position = (5, 8, 5)
                camera.rotation = (30, 45, 0)
            
            self.update_camera()
    
    def get_mode_name(self) -> str:
        """Get the name of the current camera mode."""
        return "Orbit"
    
    def zoom_in(self):
        """Zoom camera closer to target (orbit mode only)."""
        self.camera_distance = max(self.min_distance, self.camera_distance - self.zoom_speed)
    
    def zoom_out(self):
        """Zoom camera away from target (orbit mode only)."""
        self.camera_distance = min(self.max_distance, self.camera_distance + self.zoom_speed)
    
    def focus_on_position(self, x: float, z: float):
        """
        Focus camera on a specific world position.
        
        Args:
            x: World X coordinate
            z: World Z coordinate
        """
        if URSINA_AVAILABLE:
            self.camera_target = Vec3(x, 0, z)
        else:
            self.camera_target = Vector3(x, 0, z)
        
        if self.camera_mode in [0, 2]:  # Orbit or top-down
            self.update_camera()
    
    def get_camera_info(self) -> dict:
        """Get current camera information for debugging."""
        return {
            'mode': self.camera_mode,
            'mode_name': self.get_mode_name(),
            'distance': self.camera_distance,
            'angle_x': self.camera_angle_x,
            'angle_y': self.camera_angle_y,
            'target': {
                'x': self.camera_target.x,
                'y': self.camera_target.y,
                'z': self.camera_target.z
            }
        }