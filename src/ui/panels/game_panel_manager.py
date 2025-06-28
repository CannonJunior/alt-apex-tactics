"""
Game Panel Manager

Centralized management for all game UI panels with keyboard shortcuts.
Coordinates panel visibility and provides unified interface for panel interactions.
"""

from typing import Optional, Dict, Any
from .base_panel import PanelManager
from .character_panel import CharacterPanel
from .inventory_panel import InventoryPanel
from .talent_panel import TalentPanel
from .party_panel import PartyPanel
from .upgrade_panel import UpgradePanel


class GamePanelManager(PanelManager):
    """
    Enhanced panel manager specifically for Apex Tactics game panels.
    
    Manages all five main game panels:
    - Character Panel ('c' key)
    - Inventory Panel ('i' key)
    - Talent Panel ('t' key)
    - Party Panel ('p' key)
    - Upgrade Panel ('u' key)
    """
    
    def __init__(self, game_reference: Optional[Any] = None):
        """
        Initialize game panel manager with all panels.
        
        Args:
            game_reference: Reference to main game object
        """
        super().__init__()
        
        self.game_reference = game_reference
        
        # Initialize all panels
        self._create_panels()
        
        # Register panels with keyboard shortcuts
        self._register_panels()
        
        print("✅ Game Panel Manager initialized with 5 panels")
    
    def _create_panels(self):
        """Create all game panels."""
        try:
            self.character_panel = CharacterPanel(self.game_reference)
            self.inventory_panel = InventoryPanel(self.game_reference)
            self.talent_panel = TalentPanel(self.game_reference)
            self.party_panel = PartyPanel(self.game_reference)
            self.upgrade_panel = UpgradePanel(self.game_reference)
            
            print("✅ All panels created successfully")
            
        except Exception as e:
            print(f"❌ Error creating panels: {e}")
            # Create minimal fallback
            self.character_panel = None
            self.inventory_panel = None
            self.talent_panel = None
            self.party_panel = None
            self.upgrade_panel = None
    
    def _register_panels(self):
        """Register panels with their keyboard shortcuts."""
        if self.character_panel:
            self.register_panel("character", self.character_panel, "c")
        
        if self.inventory_panel:
            self.register_panel("inventory", self.inventory_panel, "i")
        
        if self.talent_panel:
            self.register_panel("talent", self.talent_panel, "t")
        
        if self.party_panel:
            self.register_panel("party", self.party_panel, "p")
        
        if self.upgrade_panel:
            self.register_panel("upgrade", self.upgrade_panel, "u")
    
    def update_character_data(self, character):
        """
        Update character-related panels with character data.
        
        Args:
            character: Character/unit object
        """
        # Update character panel
        if self.character_panel:
            self.character_panel.set_character(character)
        
        # Update talent panel
        if self.talent_panel:
            self.talent_panel.set_character(character)
        
    def update_party_data(self, party_data: Dict[str, Any]):
        """
        Update party panel with party information.
        
        Args:
            party_data: Dictionary containing party information
        """
        if self.party_panel:
            self.party_panel.update_content(party_data)
    
    def update_inventory_data(self, inventory_data: Dict[str, Any]):
        """
        Update inventory panel with inventory information.
        
        Args:
            inventory_data: Dictionary containing inventory information
        """
        if self.inventory_panel:
            self.inventory_panel.update_content(inventory_data)
    
    def update_upgrade_data(self, upgrade_data: Dict[str, Any]):
        """
        Update upgrade panel with upgrade information.
        
        Args:
            upgrade_data: Dictionary containing upgrade information
        """
        if self.upgrade_panel:
            self.upgrade_panel.update_content(upgrade_data)
    
    def get_panel_status(self) -> Dict[str, bool]:
        """
        Get visibility status of all panels.
        
        Returns:
            Dictionary mapping panel names to visibility status
        """
        status = {}
        for name, panel in self.panels.items():
            status[name] = panel.is_visible if panel else False
        return status
    
    def hide_all_panels(self):
        """Hide all panels."""
        for panel in self.panels.values():
            if panel:
                panel.hide()
        self.active_panel = None
    
    def show_character_panel_for_unit(self, unit):
        """
        Show character panel for specific unit.
        
        Args:
            unit: Unit to display in character panel
        """
        if self.character_panel:
            self.character_panel.set_character(unit)
            self.show_panel("character")
    
    def get_panel_info(self) -> str:
        """
        Get information about available panels and their shortcuts.
        
        Returns:
            Formatted string with panel information
        """
        info_lines = [
            "Available UI Panels:",
            "  [C] Character - Stats, equipment, power level",
            "  [I] Inventory - Items, equipment, materials",
            "  [T] Talents - Ability trees and upgrades", 
            "  [P] Party - Team composition and stats",
            "  [U] Upgrade - Item tier progression",
            "",
            "Press the corresponding key to toggle each panel."
        ]
        return "\n".join(info_lines)
    
    def handle_game_input(self, key: str) -> bool:
        """
        Handle keyboard input for game panels.
        
        Args:
            key: Pressed key
            
        Returns:
            True if key was handled by panels, False otherwise
        """
        # Let parent handle the key input
        handled = self.handle_key_input(key)
        
        if handled:
            # Print panel status for debugging
            if key in ['c', 'i', 't', 'p', 'u']:
                panel_name = self.key_bindings.get(key, "unknown")
                if panel_name in self.panels:
                    is_visible = self.panels[panel_name].is_visible
                    status = "shown" if is_visible else "hidden"
                    print(f"Panel '{panel_name}' {status}")
        
        return handled
    
    def cleanup(self):
        """Clean up all panels and resources."""
        print("🧹 Cleaning up game panels...")
        
        # Clean up individual panels
        for panel in self.panels.values():
            if panel and hasattr(panel, 'cleanup'):
                try:
                    panel.cleanup()
                except Exception as e:
                    print(f"⚠️ Error cleaning up panel: {e}")
        
        # Clean up base manager
        self.cleanup_all()
        
        print("✅ Game panel cleanup complete")


def create_game_panels(game_reference: Optional[Any] = None) -> GamePanelManager:
    """
    Factory function to create game panel manager.
    
    Args:
        game_reference: Reference to main game object
        
    Returns:
        Configured GamePanelManager instance
    """
    try:
        panel_manager = GamePanelManager(game_reference)
        print(f"🎮 Game panels initialized successfully")
        print(panel_manager.get_panel_info())
        return panel_manager
        
    except Exception as e:
        print(f"❌ Failed to create game panels: {e}")
        # Return minimal manager
        return PanelManager()
