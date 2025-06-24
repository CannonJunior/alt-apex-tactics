"""
User Interface Package

Contains UI components and camera controls for the tactical RPG engine.
"""

# Import main UI components
try:
    from .camera_controller import CameraController
    __all__ = ['CameraController']
except ImportError:
    # Ursina not available
    __all__ = []