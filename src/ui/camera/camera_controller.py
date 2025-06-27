"""
Camera Controller for Tactical Games

Provides orbit, free, and top-down camera modes with smooth controls.
Extracted from apex-tactics.py for reusability across projects.
"""

import math
from typing import Optional, Callable

try:
    from ursina import camera, held_keys, mouse, time, Vec3
    URSINA_AVAILABLE = True
except ImportError:
    URSINA_AVAILABLE = False
    # Fallback for testing without Ursina
    class Vec3:
        def __init__(self, x=0, y=0, z=0):
            self.x, self.y, self.z = x, y, z


class CameraController:
    """
    Multi-mode camera controller for tactical games.
    
    Supports three camera modes:
    - Orbit: Camera orbits around a target point
    - Free: First-person style free movement  
    - Top-down: Fixed overhead view with panning
    """
    
    def __init__(self, grid_width: int = 8, grid_height: int = 8, 
                 mode_change_callback: Optional[Callable[[int], None]] = None):
        """
        Initialize camera controller.
        
        Args:
            grid_width: Width of the game grid for centering
            grid_height: Height of the game grid for centering
            mode_change_callback: Optional callback for when camera mode changes
        """
        if not URSINA_AVAILABLE:
            raise ImportError("Ursina is required for CameraController")
            
        # Grid-based positioning
        self.grid_center = Vec3(grid_width/2 - 0.5, 0, grid_height/2 - 0.5)
        self.camera_target = Vec3(self.grid_center.x, self.grid_center.y, self.grid_center.z)
        
        # Camera parameters
        self.camera_distance = 8
        self.camera_angle_x = 30
        self.camera_angle_y = 0
        self.camera_mode = 0  # 0: orbit, 1: free, 2: top-down
        
        # Movement settings
        self.move_speed = 0.5
        self.rotation_speed = 50
        
        # Limits
        self.min_distance = 3
        self.max_distance = 15
        self.min_angle_x = -80
        self.max_angle_x = 80
        
        # Callback for mode changes
        self.mode_change_callback = mode_change_callback
        
    def update_camera(self):
        """Update camera position based on current mode."""
        if self.camera_mode == 0:  # Orbit mode
            self._update_orbit_camera()
        elif self.camera_mode == 1:  # Free camera mode
            # Free camera position is handled by input functions
            pass
        elif self.camera_mode == 2:  # Top-down mode
            self._update_topdown_camera()
    
    def _update_orbit_camera(self):
        """Update camera for orbit mode."""
        rad_y = math.radians(self.camera_angle_y)
        rad_x = math.radians(self.camera_angle_x)
        
        x = self.camera_target.x + self.camera_distance * math.cos(rad_x) * math.sin(rad_y)
        y = self.camera_target.y + self.camera_distance * math.sin(rad_x)
        z = self.camera_target.z + self.camera_distance * math.cos(rad_x) * math.cos(rad_y)
        
        camera.position = (x, y, z)
        camera.look_at(self.camera_target)
    
    def _update_topdown_camera(self):
        """Update camera for top-down mode."""
        camera.position = (self.camera_target.x, 12, self.camera_target.z)
        camera.rotation = (90, 0, 0)
    
    def handle_input(self, key: str):
        """
        Handle keyboard input for camera control.
        
        Args:
            key: The key that was pressed
        """
        # Camera mode switching
        if key == '1':
            self._set_camera_mode(0, "Orbit Camera Mode")
        elif key == '2':
            self._set_camera_mode(1, "Free Camera Mode")
        elif key == '3':
            self._set_camera_mode(2, "Top-down Camera Mode")
        
        # Mode-specific controls
        elif self.camera_mode == 0:
            self._handle_orbit_input(key)
        elif self.camera_mode == 1:
            self._handle_free_input(key)
        elif self.camera_mode == 2:
            self._handle_topdown_input(key)
    
    def _set_camera_mode(self, mode: int, mode_name: str):
        """Set camera mode and notify callback."""
        self.camera_mode = mode
        print(mode_name)
        if self.mode_change_callback:
            self.mode_change_callback(mode)
    
    def _handle_orbit_input(self, key: str):
        """Handle input for orbit mode."""
        if key == 'scroll up':
            self.camera_distance = max(self.min_distance, self.camera_distance - 0.5)
        elif key == 'scroll down':
            self.camera_distance = min(self.max_distance, self.camera_distance + 0.5)
    
    def _handle_free_input(self, key: str):
        """Handle input for free camera mode."""
        if key == 'w':
            camera.position += camera.forward * self.move_speed
        elif key == 's':
            camera.position -= camera.forward * self.move_speed
        elif key == 'a':
            camera.position -= camera.right * self.move_speed
        elif key == 'd':
            camera.position += camera.right * self.move_speed
        elif key == 'q':
            camera.position += camera.up * self.move_speed
        elif key == 'e':
            camera.position -= camera.up * self.move_speed
    
    def _handle_topdown_input(self, key: str):
        """Handle input for top-down mode."""
        if key == 'w':
            self.camera_target.z -= self.move_speed
        elif key == 's':
            self.camera_target.z += self.move_speed
        elif key == 'a':
            self.camera_target.x -= self.move_speed
        elif key == 'd':
            self.camera_target.x += self.move_speed
    
    def handle_mouse_input(self):
        """Handle mouse input for camera control."""
        if self.camera_mode == 0:  # Orbit mode
            self._handle_orbit_mouse()
        elif self.camera_mode == 1:  # Free camera mode
            self._handle_free_mouse()
        # Top-down mode doesn't use mouse input
    
    def _handle_orbit_mouse(self):
        """Handle mouse input for orbit mode."""
        # Mouse drag rotation
        if held_keys['left mouse']:
            self.camera_angle_y += mouse.velocity.x * 50
            self.camera_angle_x = max(self.min_angle_x, 
                                    min(self.max_angle_x, 
                                        self.camera_angle_x - mouse.velocity.y * 50))
        
        # Keyboard rotation
        rotation_speed = self.rotation_speed * time.dt
        if held_keys['left arrow']:
            self.camera_angle_y -= rotation_speed
        elif held_keys['right arrow']:
            self.camera_angle_y += rotation_speed
        elif held_keys['up arrow']:
            self.camera_angle_x = max(self.min_angle_x, self.camera_angle_x - rotation_speed)
        elif held_keys['down arrow']:
            self.camera_angle_x = min(self.max_angle_x, self.camera_angle_x + rotation_speed)
    
    def _handle_free_mouse(self):
        """Handle mouse input for free camera mode."""
        if held_keys['left mouse']:
            camera.rotation_y += mouse.velocity.x * 40
            camera.rotation_x -= mouse.velocity.y * 40
            camera.rotation_x = max(-90, min(90, camera.rotation_x))
    
    def set_target(self, target: Vec3):
        """Set the camera target position."""
        self.camera_target = Vec3(target.x, target.y, target.z)
    
    def get_mode_name(self) -> str:
        """Get the current camera mode name."""
        mode_names = ["Orbit", "Free", "Top-down"]
        return mode_names[self.camera_mode]
    
    def reset_to_default(self):
        """Reset camera to default orbit mode settings."""
        self.camera_mode = 0
        self.camera_distance = 8
        self.camera_angle_x = 30
        self.camera_angle_y = 0
        self.camera_target = Vec3(self.grid_center.x, self.grid_center.y, self.grid_center.z)