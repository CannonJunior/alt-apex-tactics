"""
Party Panel Implementation

Displays party composition with unit slots, character carousel, and aggregate stats.
Shows party power levels and individual unit status information.
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
class PartyMember:
    """Represents a party member with status information."""
    name: str
    unit_type: str
    level: int
    power_level: int
    status: str  # "Active", "Injured", "Ready", "Exhausted"
    hp_current: int
    hp_max: int
    mp_current: int
    mp_max: int


class PartyPanel(BasePanel):
    """
    Party management panel showing team composition and stats.
    
    Features:
    - 5 party slot selection interface
    - Character carousel with all available units
    - Aggregate party statistics
    - Individual unit status display
    - Party power level calculation
    """
    
    def __init__(self, game_reference: Optional[Any] = None):
        """Initialize party panel."""
        config = PanelConfig(
            title="Party",
            width=0.6,
            height=0.8,
            x_position=0.2,  # Left-center of screen
            y_position=0.6,
            z_layer=2,
            visible=False
        )
        
        # Party data
        self.party_slots = [None] * 5  # 5 party slots
        self.available_characters: List[PartyMember] = []
        self.selected_slot = 0
        self.carousel_offset = 0
        self.max_carousel_visible = 3
        
        # UI elements
        self.slot_buttons = []
        self.carousel_buttons = []
        self.carousel_texts = []
        self.aggregate_stats_texts = {}
        
        super().__init__(config, game_reference)
    
    def _create_content(self):
        """Create party panel content."""
        if not URSINA_AVAILABLE:
            return
        
        # Create party slots section
        self._create_party_slots()
        
        # Create aggregate stats section
        self._create_aggregate_stats()
        
        # Create character carousel section
        self._create_character_carousel()
        
        # Create action buttons
        self._create_action_buttons()
        
        # Load sample data and update display
        self._load_sample_data()
        self._update_all_displays()
    
    def _create_party_slots(self):
        """Create the 5 party slot selection interface."""
        slots_y = 0.25
        slots_start_x = -0.22
        slot_width = 0.08
        
        self.add_text_element(
            "Active Party Slots:",
            (0, slots_y + 0.04, -0.01),
            scale=0.9,
            text_color=color.yellow
        )
        
        for i in range(5):
            x_pos = slots_start_x + (i * slot_width)
            
            # Slot button
            slot_color = color.orange if i == self.selected_slot else color.dark_gray
            
            slot_button = self.add_button_element(
                text=f"Slot {i+1}",
                position=(x_pos, slots_y, -0.01),
                size=(slot_width * 0.9, 0.06),
                callback=lambda slot=i: self._select_party_slot(slot),
                button_color=slot_color
            )
            
            self.slot_buttons.append(slot_button)
            
            # Character name in slot
            char_name = "Empty"
            if self.party_slots[i]:
                char_name = self.party_slots[i].name
            
            slot_text = self.add_text_element(
                char_name,
                (x_pos, slots_y - 0.04, -0.01),
                scale=0.5,
                text_color=color.white
            )
            
            self.slot_buttons.append(slot_text)  # Store for updates
    
    def _create_aggregate_stats(self):
        """Create aggregate party statistics display."""
        stats_y = 0.1
        
        self.add_text_element(
            "--- PARTY STATS ---",
            (0, stats_y, -0.01),
            scale=0.9,
            text_color=color.white
        )
        
        # Party power level
        self.party_power_text = self.add_text_element(
            "Party Power: 0",
            (0, stats_y - 0.04, -0.01),
            scale=0.8,
            text_color=color.cyan
        )
        
        # Combat stats (left column)
        combat_y = stats_y - 0.08
        self.party_phys_attack_text = self.add_text_element(
            "Physical ATK: 0",
            (-0.15, combat_y, -0.01),
            scale=0.6,
            text_color=color.red
        )
        
        self.party_mag_attack_text = self.add_text_element(
            "Magical ATK: 0",
            (-0.15, combat_y - 0.025, -0.01),
            scale=0.6,
            text_color=color.blue
        )
        
        self.party_spir_attack_text = self.add_text_element(
            "Spiritual ATK: 0",
            (-0.15, combat_y - 0.05, -0.01),
            scale=0.6,
            text_color=color.purple
        )
        
        # Defense stats (right column)
        self.party_phys_defense_text = self.add_text_element(
            "Physical DEF: 0",
            (0.05, combat_y, -0.01),
            scale=0.6,
            text_color=color.red
        )
        
        self.party_mag_defense_text = self.add_text_element(
            "Magical DEF: 0",
            (0.05, combat_y - 0.025, -0.01),
            scale=0.6,
            text_color=color.blue
        )
        
        self.party_spir_defense_text = self.add_text_element(
            "Spiritual DEF: 0",
            (0.05, combat_y - 0.05, -0.01),
            scale=0.6,
            text_color=color.purple
        )
    
    def _create_character_carousel(self):
        """Create character selection carousel."""
        carousel_y = -0.05
        
        self.add_text_element(
            "Available Characters:",
            (0, carousel_y, -0.01),
            scale=0.8,
            text_color=color.yellow
        )
        
        # Carousel navigation buttons
        self.carousel_prev_btn = self.add_button_element(
            text="◄",
            position=(-0.25, carousel_y - 0.1, -0.01),
            size=(0.04, 0.04),
            callback=self._carousel_prev,
            button_color=color.blue
        )
        
        self.carousel_next_btn = self.add_button_element(
            text="►",
            position=(0.25, carousel_y - 0.1, -0.01),
            size=(0.04, 0.04),
            callback=self._carousel_next,
            button_color=color.blue
        )
        
        # Character display area will be created in _update_carousel_display()
    
    def _create_action_buttons(self):
        """Create action buttons for party management."""
        action_y = -0.25
        
        self.add_to_party_btn = self.add_button_element(
            text="Add to Party",
            position=(-0.1, action_y, -0.01),
            size=(0.08, 0.04),
            callback=self._add_character_to_party,
            button_color=color.green
        )
        
        self.remove_from_party_btn = self.add_button_element(
            text="Remove",
            position=(0.1, action_y, -0.01),
            size=(0.08, 0.04),
            callback=self._remove_character_from_party,
            button_color=color.red
        )
    
    def _select_party_slot(self, slot_index: int):
        """Select a party slot for character assignment."""
        self.selected_slot = slot_index
        
        # Update slot button colors
        for i, button in enumerate(self.slot_buttons[:5]):  # Only slot buttons, not text
            if hasattr(button, 'color'):
                button.color = color.orange if i == slot_index else color.dark_gray
    
    def _carousel_prev(self):
        """Move carousel to previous characters."""
        if self.carousel_offset > 0:
            self.carousel_offset -= 1
            self._update_carousel_display()
    
    def _carousel_next(self):
        """Move carousel to next characters."""
        max_offset = max(0, len(self.available_characters) - self.max_carousel_visible)
        if self.carousel_offset < max_offset:
            self.carousel_offset += 1
            self._update_carousel_display()
    
    def _update_carousel_display(self):
        """Update the character carousel display."""
        # Clear existing carousel elements
        for button in self.carousel_buttons:
            if hasattr(button, 'enabled'):
                button.enabled = False
        for text in self.carousel_texts:
            if hasattr(text, 'enabled'):
                text.enabled = False
        
        self.carousel_buttons.clear()
        self.carousel_texts.clear()
        
        # Display characters in carousel
        carousel_y = -0.1
        char_width = 0.15
        start_x = -0.15
        
        display_chars = self.available_characters[self.carousel_offset:self.carousel_offset + self.max_carousel_visible]
        
        for i, character in enumerate(display_chars):
            x_pos = start_x + (i * char_width)
            
            # Character button
            char_button = self.add_button_element(
                text=character.name,
                position=(x_pos, carousel_y, -0.01),
                size=(char_width * 0.9, 0.04),
                callback=lambda char=character: self._select_carousel_character(char),
                button_color=self._get_character_status_color(character)
            )
            
            self.carousel_buttons.append(char_button)
            
            # Character info
            char_info = f"Lvl {character.level} | Power {character.power_level}"
            char_info_text = self.add_text_element(
                char_info,
                (x_pos, carousel_y - 0.03, -0.01),
                scale=0.4,
                text_color=color.light_gray
            )
            
            self.carousel_texts.append(char_info_text)
            
            # Status info
            status_info = f"{character.status} | HP: {character.hp_current}/{character.hp_max}"
            status_text = self.add_text_element(
                status_info,
                (x_pos, carousel_y - 0.05, -0.01),
                scale=0.4,
                text_color=self._get_status_text_color(character.status)
            )
            
            self.carousel_texts.append(status_text)
    
    def _get_character_status_color(self, character: PartyMember):
        """Get color based on character status."""
        status_colors = {
            "Active": color.green,
            "Ready": color.blue,
            "Injured": color.orange,
            "Exhausted": color.red
        }
        return status_colors.get(character.status, color.gray)
    
    def _get_status_text_color(self, status: str):
        """Get text color based on status."""
        status_colors = {
            "Active": color.green,
            "Ready": color.cyan,
            "Injured": color.yellow,
            "Exhausted": color.red
        }
        return status_colors.get(status, color.light_gray)
    
    def _select_carousel_character(self, character: PartyMember):
        """Select a character from the carousel."""
        print(f"Selected character: {character.name} (Status: {character.status})")
    
    def _add_character_to_party(self):
        """Add selected character to party slot."""
        if not self.available_characters:
            return
        
        # Get currently displayed character (simplified - could be enhanced with proper selection)
        display_chars = self.available_characters[self.carousel_offset:self.carousel_offset + self.max_carousel_visible]
        if display_chars:
            character = display_chars[0]  # Add first visible character for now
            
            # Check if character is already in party
            if character not in self.party_slots:
                self.party_slots[self.selected_slot] = character
                self._update_party_slots_display()
                self._update_aggregate_stats_display()
                print(f"Added {character.name} to party slot {self.selected_slot + 1}")
    
    def _remove_character_from_party(self):
        """Remove character from selected party slot."""
        if self.party_slots[self.selected_slot]:
            character = self.party_slots[self.selected_slot]
            self.party_slots[self.selected_slot] = None
            self._update_party_slots_display()
            self._update_aggregate_stats_display()
            print(f"Removed {character.name} from party slot {self.selected_slot + 1}")
    
    def _update_party_slots_display(self):
        """Update the party slots display."""
        # Update slot text elements (every other element starting from index 5)
        for i in range(5):
            text_element = self.slot_buttons[5 + i]  # Text elements start after slot buttons
            
            if self.party_slots[i]:
                text_element.text = self.party_slots[i].name
                text_element.color = color.white
            else:
                text_element.text = "Empty"
                text_element.color = color.gray
    
    def _update_aggregate_stats_display(self):
        """Update aggregate party statistics."""
        # Calculate totals from party members
        total_power = 0
        total_phys_attack = 0
        total_mag_attack = 0
        total_spir_attack = 0
        total_phys_defense = 0
        total_mag_defense = 0
        total_spir_defense = 0
        
        active_members = [member for member in self.party_slots if member is not None]
        
        for member in active_members:
            total_power += member.power_level
            # Simplified stat calculation - would use actual character stats in real implementation
            total_phys_attack += member.level * 5
            total_mag_attack += member.level * 3
            total_spir_attack += member.level * 2
            total_phys_defense += member.level * 4
            total_mag_defense += member.level * 3
            total_spir_defense += member.level * 3
        
        # Update display
        self.party_power_text.text = f"Party Power: {total_power}"
        self.party_phys_attack_text.text = f"Physical ATK: {total_phys_attack}"
        self.party_mag_attack_text.text = f"Magical ATK: {total_mag_attack}"
        self.party_spir_attack_text.text = f"Spiritual ATK: {total_spir_attack}"
        self.party_phys_defense_text.text = f"Physical DEF: {total_phys_defense}"
        self.party_mag_defense_text.text = f"Magical DEF: {total_mag_defense}"
        self.party_spir_defense_text.text = f"Spiritual DEF: {total_spir_defense}"
    
    def _update_all_displays(self):
        """Update all panel displays."""
        self._update_party_slots_display()
        self._update_aggregate_stats_display()
        self._update_carousel_display()
    
    def _load_sample_data(self):
        """Load sample party and character data."""
        self.available_characters = [
            PartyMember("Hero", "Warrior", 5, 45, "Ready", 100, 100, 20, 20),
            PartyMember("Mage", "Sorcerer", 4, 38, "Ready", 60, 80, 80, 80),
            PartyMember("Rogue", "Scout", 4, 35, "Injured", 45, 70, 30, 30),
            PartyMember("Cleric", "Healer", 3, 32, "Ready", 75, 75, 60, 60),
            PartyMember("Tank", "Guardian", 5, 50, "Active", 120, 120, 15, 15),
            PartyMember("Archer", "Ranger", 3, 28, "Exhausted", 65, 65, 25, 25),
            PartyMember("Paladin", "Holy Warrior", 4, 42, "Ready", 95, 95, 40, 40)
        ]
        
        # Add some characters to party by default
        self.party_slots[0] = self.available_characters[0]  # Hero
        self.party_slots[1] = self.available_characters[1]  # Mage
        self.party_slots[2] = self.available_characters[3]  # Cleric
    
    def add_character(self, character: PartyMember):
        """Add character to available characters list."""
        if character not in self.available_characters:
            self.available_characters.append(character)
            self._update_carousel_display()
    
    def remove_character(self, character_name: str):
        """Remove character from available characters."""
        self.available_characters = [char for char in self.available_characters if char.name != character_name]
        
        # Remove from party if present
        for i, party_member in enumerate(self.party_slots):
            if party_member and party_member.name == character_name:
                self.party_slots[i] = None
        
        self._update_all_displays()
    
    def get_active_party(self) -> List[PartyMember]:
        """Get list of active party members."""
        return [member for member in self.party_slots if member is not None]
    
    def update_content(self, data: Dict[str, Any]):
        """Update panel content with new data."""
        if 'party' in data:
            # Update party slots
            party_data = data['party']
            for i, member_data in enumerate(party_data[:5]):
                if member_data:
                    self.party_slots[i] = PartyMember(**member_data)
                else:
                    self.party_slots[i] = None
            
            self._update_all_displays()
        
        if 'available_characters' in data:
            self.available_characters = [PartyMember(**char_data) for char_data in data['available_characters']]
            self._update_carousel_display()
        
        if 'add_character' in data:
            self.add_character(PartyMember(**data['add_character']))
        
        if 'remove_character' in data:
            self.remove_character(data['remove_character'])