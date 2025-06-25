"""
Portable UI System

Multi-engine UI framework supporting Ursina, Unity, Godot, and other engines.
Provides abstraction layer for cross-platform UI development.
"""

# Import portable UI core
from .core import *
from .screens import *

# Import legacy UI components
try:
    from .camera_controller import CameraController
    from .visual.grid_visualizer import GridVisualizer
    from .visual.tile_highlighter import TileHighlighter
    from .visual.combat_animator import CombatAnimator
    from .interface.inventory_interface import InventoryInterface
    from .interface.combat_interface import CombatInterface
    LEGACY_UI_AVAILABLE = True
except ImportError:
    LEGACY_UI_AVAILABLE = False

# Conditionally import engine-specific implementations
try:
    from .ursina import *
    URSINA_UI_AVAILABLE = True
except ImportError:
    URSINA_UI_AVAILABLE = False

__all__ = [
    # Core abstractions
    'UIColor', 'UIVector2', 'UIRect', 'UIAnchor', 'UILayoutMode',
    'IUIElement', 'IUIButton', 'IUIPanel', 'IUIText', 'IUIScreen', 'IUIManager',
    'UIEvent', 'UIEventBus', 'UITheme', 'UIState', 'ui_state',
    
    # Screen implementations
    'GameSettings', 'StartScreen', 'SettingsScreen', 'MainMenuManager',
    
    # Engine availability flags
    'URSINA_UI_AVAILABLE', 'LEGACY_UI_AVAILABLE'
]

# Add legacy components if available
if LEGACY_UI_AVAILABLE:
    __all__.extend([
        'CameraController', 'GridVisualizer', 'TileHighlighter', 
        'CombatAnimator', 'InventoryInterface', 'CombatInterface'
    ])

# Add Ursina components if available
if URSINA_UI_AVAILABLE:
    __all__.extend([
        'UrsinaUIButton', 'UrsinaUIPanel', 'UrsinaUIText', 
        'UrsinaUIScreen', 'UrsinaUIManager'
    ])