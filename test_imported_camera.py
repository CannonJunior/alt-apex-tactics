#!/usr/bin/env python3
"""
Test demo for the imported CameraController

This creates a simple scene and uses the CameraController as an imported component
to verify it works correctly with all camera modes and input handling.
"""

from ursina import *
from camera_controller import CameraController

app = Ursina()

# Create a simple test scene
ground = Entity(model='plane', texture='white_cube', color=color.green, scale=(10, 1, 10))

# Add some reference objects
for i in range(5):
    for j in range(5):
        cube = Entity(
            model='cube', 
            color=color.random_color(), 
            scale=(0.8, 0.5, 0.8), 
            position=(i*2, 0.25, j*2)
        )

# Create text instructions
instructions = Text(
    "Camera Controller Test\n" +
    "1/2/3 - Switch camera modes\n" +
    "WASD - Move camera\n" +
    "Mouse - Look around\n" +
    "T - Show current mode\n" +
    "R - Reset camera\n" +
    "ESC - Exit",
    position=(-0.8, 0.4),
    scale=1.2,
    color=color.white
)

# Initialize the imported CameraController
camera_controller = CameraController(grid_width=10, grid_height=10)

def input(key):
    """Global input handler that uses the imported CameraController"""
    # Pass all input to the camera controller
    camera_controller.handle_input(key)
    
    # Additional test controls
    if key == 'escape':
        application.quit()
    elif key == 't':
        print(f"Current camera mode: {camera_controller.get_mode_name()}")
        print(f"Camera position: {camera.position}")
        print(f"Camera rotation: {camera.rotation}")
    elif key == 'r':
        camera_controller.reset_to_default()

def update():
    """Global update function that uses the imported CameraController"""
    # Handle mouse input and update camera
    camera_controller.handle_mouse_input()
    camera_controller.update_camera()

print("Testing imported CameraController...")
print("All camera modes should work correctly:")
print("- Mode 1 (Orbit): Mouse drag to rotate, scroll to zoom")
print("- Mode 2 (Free): WASD to move, mouse drag to look")  
print("- Mode 3 (Top-down): WASD to move view target")

# Set initial camera position
camera_controller.update_camera()

if __name__ == "__main__":
    app.run()