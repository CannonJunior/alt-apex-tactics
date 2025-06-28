"""
Character Panel Implementation

Displays character stats, equipment slots, and paper doll visualization.
Toggleable with 'c' key, shows selected unit's complete information.
"""

from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from .base_panel import BasePanel, PanelConfig

try:
    from ursina import Entity, Text, Button, color, camera
    URSINA_AVAILABLE = True
except ImportError:
    URSINA_AVAILABLE = False


@dataclass
class EquipmentSlot:
    """Represents an equipment slot in the character panel."""
    slot_id: int
    slot_name: str
    position: tuple
    equipped_item: Optional[Any] = None


class CharacterPanel(BasePanel):
    """
    Character information panel showing stats, equipment, and character details.
    
    Features:
    - Character name, class, race, and power level
    - Physical, magical, spiritual stats
    - Attack and defense values
    - Paper doll with 8 equipment slots
    - Equipment slot highlighting and interaction
    """
    
    def __init__(self, game_reference: Optional[Any] = None):
        """Initialize character panel."""
        config = PanelConfig(
            title="Character",
            width=0.5,
            height=0.7,
            x_position=0.75,  # Right side of screen
            y_position=0.65,
            z_layer=2,
            visible=False
        )
        
        # Character data
        self.current_character = None
        self.stat_texts = {}
        self.equipment_slots = []
        
        super().__init__(config, game_reference)
    
    def _create_content(self):
        """Create character panel content."""
        if not URSINA_AVAILABLE:
            return
        
        # Character info section (top)
        self._create_character_info()
        
        # Stats section (middle)
        self._create_stats_display()
        
        # Equipment section (bottom)
        self._create_equipment_slots()
        
        # Initial content
        self._update_display()
    
    def _create_character_info(self):
        """Create character name, class, race, and power level display."""
        y_start = 0.25
        
        # Character name
        self.name_text = self.add_text_element(
            "Name: No Character Selected",
            (0, y_start, -0.01),
            scale=1.2,
            text_color=color.yellow
        )
        
        # Class and race
        self.class_race_text = self.add_text_element(
            "Class: Unknown | Race: Terran",
            (0, y_start - 0.04, -0.01),
            scale=0.8,
            text_color=color.light_gray
        )
        
        # Power level
        self.power_level_text = self.add_text_element(
            "Power Level: --",
            (0, y_start - 0.08, -0.01),
            scale=1.0,
            text_color=color.cyan
        )
    
    def _create_stats_display(self):
        """Create stats display section."""
        y_start = 0.1
        
        # Section header
        self.add_text_element(
            "--- STATS ---",
            (0, y_start, -0.01),
            scale=1.0,
            text_color=color.white
        )
        
        # Core attributes (left column)
        attr_y = y_start - 0.05
        self.strength_text = self.add_text_element(
            "STR: --",
            (-0.15, attr_y, -0.01),
            scale=0.7,
            text_color=color.red
        )
        
        self.fortitude_text = self.add_text_element(
            "FOR: --",
            (-0.15, attr_y - 0.03, -0.01),
            scale=0.7,
            text_color=color.orange
        )
        
        self.finesse_text = self.add_text_element(
            "FIN: --",
            (-0.15, attr_y - 0.06, -0.01),
            scale=0.7,
            text_color=color.green
        )
        
        # Mental attributes (right column)
        self.wisdom_text = self.add_text_element(
            "WIS: --",
            (0.05, attr_y, -0.01),
            scale=0.7,
            text_color=color.blue
        )
        
        self.wonder_text = self.add_text_element(
            "WON: --",
            (0.05, attr_y - 0.03, -0.01),
            scale=0.7,
            text_color=color.purple
        )
        
        self.worthy_text = self.add_text_element(
            "WOR: --",
            (0.05, attr_y - 0.06, -0.01),
            scale=0.7,
            text_color=color.gold
        )
        
        # Combat stats
        combat_y = attr_y - 0.12
        self.add_text_element(
            "--- COMBAT ---",
            (0, combat_y, -0.01),
            scale=0.9,
            text_color=color.white
        )
        
        # Attack values
        attack_y = combat_y - 0.04
        self.physical_attack_text = self.add_text_element(
            "Physical ATK: --",
            (-0.15, attack_y, -0.01),
            scale=0.6,
            text_color=color.red
        )
        
        self.magical_attack_text = self.add_text_element(
            "Magical ATK: --",
            (-0.15, attack_y - 0.025, -0.01),
            scale=0.6,
            text_color=color.blue
        )
        
        self.spiritual_attack_text = self.add_text_element(
            "Spiritual ATK: --",
            (-0.15, attack_y - 0.05, -0.01),
            scale=0.6,
            text_color=color.purple
        )
        
        # Defense values
        self.physical_defense_text = self.add_text_element(
            "Physical DEF: --",
            (0.05, attack_y, -0.01),
            scale=0.6,
            text_color=color.red
        )
        
        self.magical_defense_text = self.add_text_element(
            "Magical DEF: --",
            (0.05, attack_y - 0.025, -0.01),
            scale=0.6,
            text_color=color.blue
        )
        
        self.spiritual_defense_text = self.add_text_element(
            "Spiritual DEF: --",
            (0.05, attack_y - 0.05, -0.01),
            scale=0.6,
            text_color=color.purple
        )
    
    def _create_equipment_slots(self):
        """Create paper doll equipment slots."""
        # Equipment section header
        eq_y = -0.15
        self.add_text_element(
            "--- EQUIPMENT ---",
            (0, eq_y, -0.01),
            scale=0.9,
            text_color=color.white
        )
        
        # Define 8 equipment slots (4 left, 4 right)
        slot_definitions = [
            (1, "Helmet", (-0.18, eq_y - 0.05)),
            (2, "Armor", (-0.18, eq_y - 0.08)),
            (3, "Gloves", (-0.18, eq_y - 0.11)),
            (4, "Boots", (-0.18, eq_y - 0.14)),
            (5, "Main-hand", (0.08, eq_y - 0.05)),
            (6, "Off-hand", (0.08, eq_y - 0.08)),
            (7, "Back", (0.08, eq_y - 0.11)),
            (8, "Talisman", (0.08, eq_y - 0.14))
        ]
        
        self.equipment_slots = []
        self.equipment_texts = {}
        
        for slot_id, slot_name, position in slot_definitions:
            # Create equipment slot
            slot = EquipmentSlot(slot_id, slot_name, position)
            self.equipment_slots.append(slot)
            
            # Create text display for slot
            slot_text = self.add_text_element(
                f"{slot_name}: Empty",
                position,
                scale=0.6,
                text_color=color.gray
            )
            
            self.equipment_texts[slot_id] = slot_text
    
    def _update_display(self):
        """Update all display elements with current character data."""
        if not self.current_character:
            self._clear_display()
            return
        
        char = self.current_character
        
        # Update character info
        self.name_text.text = f"Name: {getattr(char, 'name', 'Unknown')}"
        
        # Calculate class from stats (placeholder logic)
        character_class = self._calculate_character_class(char)
        self.class_race_text.text = f"Class: {character_class} | Race: Terran"
        
        # Calculate power level
        power_level = self._calculate_power_level(char)
        self.power_level_text.text = f"Power Level: {power_level}"
        
        # Update stats
        self._update_stats_display(char)
        
        # Update equipment
        self._update_equipment_display(char)
    
    def _update_stats_display(self, character):
        """Update stats section with character data."""
        # Core attributes
        if hasattr(character, 'stats') and hasattr(character.stats, 'attributes'):
            attrs = character.stats.attributes
            self.strength_text.text = f"STR: {attrs.strength}"
            self.fortitude_text.text = f"FOR: {attrs.fortitude}"
            self.finesse_text.text = f"FIN: {attrs.finesse}"
            self.wisdom_text.text = f"WIS: {attrs.wisdom}"
            self.wonder_text.text = f"WON: {attrs.wonder}"
            self.worthy_text.text = f"WOR: {attrs.worthy}"
        else:
            # Fallback for legacy character objects
            self.strength_text.text = f"STR: {getattr(character, 'strength', 10)}"
            self.fortitude_text.text = f"FOR: {getattr(character, 'fortitude', 10)}"
            self.finesse_text.text = f"FIN: {getattr(character, 'finesse', 10)}"
            self.wisdom_text.text = f"WIS: {getattr(character, 'wisdom', 10)}"
            self.wonder_text.text = f"WON: {getattr(character, 'wonder', 10)}"
            self.worthy_text.text = f"WOR: {getattr(character, 'worthy', 10)}"
        
        # Combat stats
        self.physical_attack_text.text = f"Physical ATK: {getattr(character, 'physical_attack', 0)}"
        self.magical_attack_text.text = f"Magical ATK: {getattr(character, 'magical_attack', 0)}"
        self.spiritual_attack_text.text = f"Spiritual ATK: {getattr(character, 'spiritual_attack', 0)}"
        
        self.physical_defense_text.text = f"Physical DEF: {getattr(character, 'physical_defense', 0)}"
        self.magical_defense_text.text = f"Magical DEF: {getattr(character, 'magical_defense', 0)}"
        self.spiritual_defense_text.text = f"Spiritual DEF: {getattr(character, 'spiritual_defense', 0)}"
    
    def _update_equipment_display(self, character):
        """Update equipment slots with character's equipped items."""
        # For now, show empty slots - equipment system not fully implemented
        for slot_id, text_element in self.equipment_texts.items():
            slot = self.equipment_slots[slot_id - 1]
            text_element.text = f"{slot.slot_name}: Empty"
            text_element.color = color.gray
    
    def _calculate_character_class(self, character) -> str:
        """Calculate character class based on stats and abilities."""
        # Simplified class calculation - can be enhanced later
        if not hasattr(character, 'stats') or not hasattr(character.stats, 'attributes'):
            return "Warrior"  # Default
        
        attrs = character.stats.attributes
        
        # Find highest stat
        stat_values = {
            'strength': attrs.strength,
            'finesse': attrs.finesse,
            'wisdom': attrs.wisdom,
            'wonder': attrs.wonder,
            'worthy': attrs.worthy,
            'fortitude': attrs.fortitude
        }
        
        highest_stat = max(stat_values, key=stat_values.get)
        
        # Map stats to classes
        class_mapping = {
            'strength': 'Warrior',
            'finesse': 'Rogue',
            'wisdom': 'Mage',
            'wonder': 'Sorcerer',
            'worthy': 'Paladin',
            'fortitude': 'Guardian'
        }
        
        return class_mapping.get(highest_stat, 'Adventurer')
    
    def _calculate_power_level(self, character) -> int:
        """Calculate character power level (1-99 scale)."""
        if not hasattr(character, 'stats') or not hasattr(character.stats, 'attributes'):
            return 1
        
        attrs = character.stats.attributes
        
        # Sum all attributes
        total_stats = (attrs.strength + attrs.fortitude + attrs.finesse + 
                      attrs.wisdom + attrs.wonder + attrs.worthy)
        
        # Convert to 1-99 scale (assuming 60 is baseline, 120 is high-end)
        power_level = min(99, max(1, int((total_stats - 60) * 2 + 30)))
        return power_level
    
    def _clear_display(self):
        """Clear all character information."""
        self.name_text.text = "Name: No Character Selected"
        self.class_race_text.text = "Class: Unknown | Race: Terran"
        self.power_level_text.text = "Power Level: --"
        
        # Clear stats
        for text_element in [self.strength_text, self.fortitude_text, self.finesse_text,
                           self.wisdom_text, self.wonder_text, self.worthy_text,
                           self.physical_attack_text, self.magical_attack_text, self.spiritual_attack_text,
                           self.physical_defense_text, self.magical_defense_text, self.spiritual_defense_text]:
            if hasattr(text_element, 'text'):
                original_label = text_element.text.split(':')[0]
                text_element.text = f"{original_label}: --"
        
        # Clear equipment
        for slot_id, text_element in self.equipment_texts.items():
            slot = self.equipment_slots[slot_id - 1]
            text_element.text = f"{slot.slot_name}: Empty"
            text_element.color = color.gray
    
    def set_character(self, character):
        """
        Set the character to display.
        
        Args:
            character: Character object to display, or None to clear
        """
        self.current_character = character
        self._update_display()
    
    def update_content(self, data: Dict[str, Any]):
        """
        Update panel content with new data.
        
        Args:
            data: Dictionary with 'character' key containing character data
        """
        if 'character' in data:
            self.set_character(data['character'])
    
    def get_equipment_slot_at_position(self, x: float, y: float) -> Optional[EquipmentSlot]:
        """
        Get equipment slot at given screen position (for future click handling).
        
        Args:
            x, y: Screen coordinates
            
        Returns:
            EquipmentSlot if position matches a slot, None otherwise
        """
        # For future implementation when adding click interactions
        return None