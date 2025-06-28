"""
Control Panel for Tactical RPG Games

Main UI panel showing unit info, camera controls, and action buttons.
Extracted from apex-tactics.py for reusability across projects.
"""

from typing import Optional, Any

try:
    from ursina import Text, Button, color
    from ursina.prefabs.window_panel import WindowPanel
    URSINA_AVAILABLE = True
except ImportError:
    URSINA_AVAILABLE = False


class ControlPanel:
    """
    Main control panel for tactical RPG games.
    
    Displays:
    - Current unit information and stats
    - Camera control instructions
    - Game control instructions  
    - Action buttons (End Turn, Attack, Defend)
    """
    
    def __init__(self, game_reference: Optional[Any] = None):
        """
        Initialize control panel.
        
        Args:
            game_reference: Optional reference to main game object for button callbacks
        """
        if not URSINA_AVAILABLE:
            raise ImportError("Ursina is required for ControlPanel")
            
        self.game_reference = game_reference
        
        # Create text elements
        self._create_text_elements()
        
        # Create action buttons
        self._create_action_buttons()
        
        # Create main panel
        self._create_main_panel()
        
        # Position panel
        self._position_panel()
    
    def _create_text_elements(self):
        """Create all text display elements."""
        self.unit_info_text = Text('No unit selected')
        self.camera_controls_text = Text('CAMERA: [1] Orbit | [2] Free | [3] Top-down | ACTIVE: Orbit')
        self.game_controls_text = Text('CONTROLS: Click unit to select | Click tile to move | Mouse/WASD for camera')
        self.stats_display_text = Text('')
    
    def _create_action_buttons(self):
        """Create action buttons with callbacks."""
        self.end_turn_btn = Button(
            text='END TURN',
            color=color.orange
        )
        
        self.attack_btn = Button(
            text='ATTACK',
            color=color.red
        )
        
        self.defend_btn = Button(
            text='DEFEND',
            color=color.blue
        )
        
        # Set up button functionality
        self.end_turn_btn.on_click = self.end_turn_clicked
        self.attack_btn.on_click = self.attack_clicked
        self.defend_btn.on_click = self.defend_clicked
    
    def _create_main_panel(self):
        """Create the main window panel with all content."""
        self.panel = WindowPanel(
            title='Tactical RPG Control Panel',
            content=(
                self.unit_info_text,
                self.camera_controls_text,
                self.game_controls_text,
                self.stats_display_text,
                Text('Actions:'),  # Label for buttons
                self.end_turn_btn,
                self.attack_btn,
                self.defend_btn
            ),
            popup=False
        )
    
    def _position_panel(self):
        """Position the panel at the bottom of the screen."""
        self.panel.x = 0
        self.panel.y = -0.3
        self.panel.layout()
    
    def end_turn_clicked(self):
        """Handle End Turn button click."""
        print("End Turn button clicked!")
        if self.game_reference and hasattr(self.game_reference, 'end_current_turn'):
            self.game_reference.end_current_turn()
    
    def attack_clicked(self):
        """Handle Attack button click."""
        print("Attack button clicked!")
        # TODO: Implement attack functionality
        if self.game_reference and hasattr(self.game_reference, 'start_attack_mode'):
            self.game_reference.start_attack_mode()
    
    def defend_clicked(self):
        """Handle Defend button click."""
        print("Defend button clicked!")
        # TODO: Implement defend functionality
        if self.game_reference and hasattr(self.game_reference, 'start_defend_mode'):
            self.game_reference.start_defend_mode()
    
    def set_game_reference(self, game: Any):
        """
        Set reference to the main game object for button interactions.
        
        Args:
            game: Main game object with action methods
        """
        self.game_reference = game
    
    def update_unit_info(self, unit: Optional[Any]):
        """
        Update the unit information display.
        
        Args:
            unit: Unit object to display info for, or None to clear
        """
        if unit:
            # Format unit info
            unit_info = f"ACTIVE: {unit.name} ({unit.type.value}) | MP: {unit.current_move_points}/{unit.move_points} | HP: {unit.hp}/{unit.max_hp}"
            self.unit_info_text.text = unit_info
            
            # Format stats info
            stats_info = (
                f"ATK - Physical: {unit.physical_attack} | Magical: {unit.magical_attack} | Spiritual: {unit.spiritual_attack}\\n"
                f"DEF - Physical: {unit.physical_defense} | Magical: {unit.magical_defense} | Spiritual: {unit.spiritual_defense}"
            )
            self.stats_display_text.text = stats_info
        else:
            # Clear display
            self.unit_info_text.text = "No unit selected"
            self.stats_display_text.text = ""
        
        # Re-layout after text changes
        self.panel.layout()
    
    def update_camera_mode(self, mode: int):
        """
        Update the camera mode display.
        
        Args:
            mode: Camera mode (0=Orbit, 1=Free, 2=Top-down)
        """
        mode_names = ["Orbit", "Free", "Top-down"]
        if 0 <= mode < len(mode_names):
            mode_name = mode_names[mode]
            self.camera_controls_text.text = f"CAMERA: [1] Orbit | [2] Free | [3] Top-down | ACTIVE: {mode_name}"
            
            # Re-layout after text changes
            self.panel.layout()
    
    def set_controls_text(self, controls_text: str):
        """
        Update the game controls text.
        
        Args:
            controls_text: New controls text to display
        """
        self.game_controls_text.text = controls_text
        self.panel.layout()
    
    def toggle_visibility(self):
        """Toggle the visibility of the control panel."""
        if hasattr(self, 'panel') and self.panel:
            self.panel.enabled = not self.panel.enabled
            status = "shown" if self.panel.enabled else "hidden"
            print(f"Control panel {status}")
    
    def show(self):
        """Show the control panel."""
        if hasattr(self, 'panel') and self.panel:
            self.panel.enabled = True
    
    def hide(self):
        """Hide the control panel."""
        if hasattr(self, 'panel') and self.panel:
            self.panel.enabled = False
    
    def is_visible(self) -> bool:
        """Check if the control panel is currently visible."""
        if hasattr(self, 'panel') and self.panel:
            return self.panel.enabled
        return False
    
    def cleanup(self):
        """Clean up panel resources."""
        if hasattr(self, 'panel') and self.panel:
            self.panel.enabled = False