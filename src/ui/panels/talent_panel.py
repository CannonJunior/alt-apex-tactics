"""
Talent Panel Implementation

Displays talent trees for physical, magical, and spiritual abilities.
Hierarchical ability progression with prerequisites and unlock paths.
"""

from typing import Optional, Dict, Any, List, Set
from dataclasses import dataclass
from .base_panel import BasePanel, PanelConfig

try:
    from ursina import Entity, Text, Button, color, camera
    URSINA_AVAILABLE = True
except ImportError:
    URSINA_AVAILABLE = False


@dataclass
class TalentNode:
    """Represents a talent/ability in the talent tree."""
    id: str
    name: str
    description: str
    talent_type: str  # "Physical", "Magical", "Spiritual"
    tier: int  # 1-5, with 1 being basic abilities
    prerequisites: List[str]  # IDs of required talents
    cost: int  # Points required to unlock
    unlocked: bool = False
    position: tuple = (0, 0)  # (x, y) position in tree


class TalentPanel(BasePanel):
    """
    Talent tree panel for character ability progression.
    
    Features:
    - Three tabs: Physical, Magical, Spiritual
    - Hierarchical talent trees with prerequisites
    - Visual talent point allocation
    - Unlock status and requirements display
    """
    
    def __init__(self, game_reference: Optional[Any] = None):
        """Initialize talent panel."""
        config = PanelConfig(
            title="Talents",
            width=0.7,
            height=0.8,
            x_position=0.15,  # Left side of screen
            y_position=0.6,
            z_layer=2,
            visible=False
        )
        
        # Talent data
        self.current_character = None
        self.current_tab = "Physical"
        self.talent_tabs = ["Physical", "Magical", "Spiritual"]
        self.talent_trees: Dict[str, List[TalentNode]] = {}
        self.available_points = {"Physical": 0, "Magical": 0, "Spiritual": 0}
        
        # UI elements
        self.tab_buttons = {}
        self.talent_buttons = {}
        self.talent_texts = []
        self.connection_lines = []
        
        super().__init__(config, game_reference)
    
    def _create_content(self):
        """Create talent panel content."""
        if not URSINA_AVAILABLE:
            return
        
        # Create tab navigation
        self._create_tab_buttons()
        
        # Create talent point display
        self._create_points_display()
        
        # Create talent tree area
        self._create_talent_tree_area()
        
        # Initialize talent trees
        self._initialize_talent_trees()
        
        # Update display
        self._update_talent_display()
    
    def _create_tab_buttons(self):
        """Create tab buttons for talent categories."""
        tab_y = 0.32
        tab_width = 0.12
        start_x = -0.25
        
        for i, tab_name in enumerate(self.talent_tabs):
            x_pos = start_x + (i * tab_width)
            
            button_color = color.purple if tab_name == self.current_tab else color.dark_gray
            
            tab_button = self.add_button_element(
                text=tab_name,
                position=(x_pos, tab_y, -0.01),
                size=(tab_width * 0.9, 0.04),
                callback=lambda t=tab_name: self._switch_tab(t),
                button_color=button_color
            )
            
            self.tab_buttons[tab_name] = tab_button
    
    def _create_points_display(self):
        """Create talent points display."""
        points_y = 0.25
        
        self.points_text = self.add_text_element(
            "Available Points: 0",
            (0, points_y, -0.01),
            scale=1.0,
            text_color=color.yellow
        )
        
        self.character_name_text = self.add_text_element(
            "Character: None Selected",
            (0, points_y - 0.04, -0.01),
            scale=0.8,
            text_color=color.light_gray
        )
    
    def _create_talent_tree_area(self):
        """Create the main talent tree display area."""
        # Create background for talent tree
        tree_bg = Entity(
            parent=self.panel_entity,
            model='cube',
            color=(0.05, 0.05, 0.1, 0.8),
            scale=(0.32, 0.4, 0.005),
            position=(0, -0.05, -0.005)
        )
        self.content_elements.append(tree_bg)
        
        # Tree area bounds for talent positioning
        self.tree_bounds = {
            'x_min': -0.15,
            'x_max': 0.15,
            'y_min': -0.25,
            'y_max': 0.15
        }
    
    def _initialize_talent_trees(self):
        """Initialize talent tree data for all categories."""
        # Physical talents
        self.talent_trees["Physical"] = [
            TalentNode("phys_basic_attack", "Power Strike", "Increases physical attack damage", "Physical", 1, [], 1, position=(-0.1, 0.1)),
            TalentNode("phys_defense", "Iron Skin", "Increases physical defense", "Physical", 1, [], 1, position=(0.1, 0.1)),
            TalentNode("phys_charge", "Charge Attack", "Rush forward and attack", "Physical", 2, ["phys_basic_attack"], 2, position=(-0.1, 0.05)),
            TalentNode("phys_berserker", "Berserker Rage", "Attack speed increases when low HP", "Physical", 3, ["phys_charge"], 3, position=(-0.1, 0)),
            TalentNode("phys_fortress", "Fortress Stance", "Massive defense boost, cannot move", "Physical", 3, ["phys_defense"], 3, position=(0.1, 0)),
            TalentNode("phys_master", "Weapon Master", "Mastery of all physical combat", "Physical", 5, ["phys_berserker", "phys_fortress"], 5, position=(0, -0.1))
        ]
        
        # Magical talents
        self.talent_trees["Magical"] = [
            TalentNode("mag_basic_spell", "Magic Missile", "Basic magical projectile", "Magical", 1, [], 1, position=(-0.1, 0.1)),
            TalentNode("mag_shield", "Mage Shield", "Magical damage protection", "Magical", 1, [], 1, position=(0.1, 0.1)),
            TalentNode("mag_fireball", "Fireball", "Area fire damage spell", "Magical", 2, ["mag_basic_spell"], 2, position=(-0.1, 0.05)),
            TalentNode("mag_ice", "Ice Storm", "Freezing area attack", "Magical", 3, ["mag_fireball"], 3, position=(-0.1, 0)),
            TalentNode("mag_ward", "Arcane Ward", "Reflect magical attacks", "Magical", 3, ["mag_shield"], 3, position=(0.1, 0)),
            TalentNode("mag_master", "Archmage", "Master of magical arts", "Magical", 5, ["mag_ice", "mag_ward"], 5, position=(0, -0.1))
        ]
        
        # Spiritual talents
        self.talent_trees["Spiritual"] = [
            TalentNode("spir_heal", "Healing Light", "Restore HP to target", "Spiritual", 1, [], 1, position=(-0.1, 0.1)),
            TalentNode("spir_bless", "Divine Blessing", "Temporary stat boost", "Spiritual", 1, [], 1, position=(0.1, 0.1)),
            TalentNode("spir_sanctuary", "Sanctuary", "Create protective area", "Spiritual", 2, ["spir_heal"], 2, position=(-0.1, 0.05)),
            TalentNode("spir_resurrection", "Resurrection", "Revive fallen allies", "Spiritual", 3, ["spir_sanctuary"], 3, position=(-0.1, 0)),
            TalentNode("spir_divine_power", "Divine Power", "Massive damage to evil", "Spiritual", 3, ["spir_bless"], 3, position=(0.1, 0)),
            TalentNode("spir_master", "Saint", "Master of spiritual power", "Spiritual", 5, ["spir_resurrection", "spir_divine_power"], 5, position=(0, -0.1))
        ]
    
    def _switch_tab(self, tab_name: str):
        """Switch to different talent category tab."""
        self.current_tab = tab_name
        
        # Update tab button colors
        for tab, button in self.tab_buttons.items():
            if hasattr(button, 'color'):
                button.color = color.purple if tab == tab_name else color.dark_gray
        
        self._update_talent_display()
    
    def _update_talent_display(self):
        """Update the talent tree display for current tab."""
        # Clear existing talent UI elements
        self._clear_talent_display()
        
        # Update points display
        available_points = self.available_points.get(self.current_tab, 0)
        self.points_text.text = f"Available {self.current_tab} Points: {available_points}"
        
        # Get talents for current tab
        talents = self.talent_trees.get(self.current_tab, [])
        
        # Create talent nodes
        for talent in talents:
            self._create_talent_node(talent)
        
        # Draw connections between related talents
        self._draw_talent_connections(talents)
    
    def _create_talent_node(self, talent: TalentNode):
        """Create visual representation of a talent node."""
        # Determine colors based on state
        if talent.unlocked:
            node_color = color.green
            text_color = color.white
        elif self._can_unlock_talent(talent):
            node_color = color.yellow
            text_color = color.black
        else:
            node_color = color.gray
            text_color = color.dark_gray
        
        # Create talent button
        talent_button = self.add_button_element(
            text=f"T{talent.tier}",
            position=(talent.position[0], talent.position[1], -0.01),
            size=(0.04, 0.03),
            callback=lambda t=talent: self._talent_clicked(t),
            button_color=node_color
        )
        
        self.talent_buttons[talent.id] = talent_button
        
        # Create talent name text
        name_text = self.add_text_element(
            text=talent.name,
            position=(talent.position[0], talent.position[1] - 0.025, -0.01),
            scale=0.4,
            text_color=text_color
        )
        
        self.talent_texts.append(name_text)
        
        # Create cost text
        cost_text = self.add_text_element(
            text=f"Cost: {talent.cost}",
            position=(talent.position[0], talent.position[1] - 0.04, -0.01),
            scale=0.3,
            text_color=text_color
        )
        
        self.talent_texts.append(cost_text)
    
    def _draw_talent_connections(self, talents: List[TalentNode]):
        """Draw connection lines between related talents."""
        # Create a lookup for talents by ID
        talent_lookup = {talent.id: talent for talent in talents}
        
        for talent in talents:
            for prereq_id in talent.prerequisites:
                if prereq_id in talent_lookup:
                    prereq_talent = talent_lookup[prereq_id]
                    self._create_connection_line(prereq_talent.position, talent.position)
    
    def _create_connection_line(self, start_pos: tuple, end_pos: tuple):
        """Create a visual connection line between two talent positions."""
        # Calculate line position and rotation
        mid_x = (start_pos[0] + end_pos[0]) / 2
        mid_y = (start_pos[1] + end_pos[1]) / 2
        
        # Create line entity
        line = Entity(
            parent=self.panel_entity,
            model='cube',
            color=color.dark_gray,
            scale=(0.002, abs(end_pos[1] - start_pos[1]), 0.001),
            position=(mid_x, mid_y, -0.002)
        )
        
        self.connection_lines.append(line)
    
    def _can_unlock_talent(self, talent: TalentNode) -> bool:
        """Check if talent can be unlocked (prerequisites met and points available)."""
        if talent.unlocked:
            return False
        
        # Check prerequisites
        for prereq_id in talent.prerequisites:
            prereq_talent = self._find_talent_by_id(prereq_id)
            if not prereq_talent or not prereq_talent.unlocked:
                return False
        
        # Check available points
        available_points = self.available_points.get(self.current_tab, 0)
        return available_points >= talent.cost
    
    def _find_talent_by_id(self, talent_id: str) -> Optional[TalentNode]:
        """Find talent node by ID across all trees."""
        for tree in self.talent_trees.values():
            for talent in tree:
                if talent.id == talent_id:
                    return talent
        return None
    
    def _talent_clicked(self, talent: TalentNode):
        """Handle talent node click."""
        if talent.unlocked:
            # Show talent details
            print(f"Talent: {talent.name}")
            print(f"Description: {talent.description}")
        elif self._can_unlock_talent(talent):
            # Unlock talent
            self._unlock_talent(talent)
        else:
            # Show why can't unlock
            self._show_talent_requirements(talent)
    
    def _unlock_talent(self, talent: TalentNode):
        """Unlock a talent if possible."""
        if not self._can_unlock_talent(talent):
            return False
        
        # Spend points
        self.available_points[self.current_tab] -= talent.cost
        talent.unlocked = True
        
        # Refresh display
        self._update_talent_display()
        
        print(f"Unlocked talent: {talent.name}")
        return True
    
    def _show_talent_requirements(self, talent: TalentNode):
        """Show what's required to unlock a talent."""
        requirements = []
        
        # Check prerequisites
        for prereq_id in talent.prerequisites:
            prereq_talent = self._find_talent_by_id(prereq_id)
            if prereq_talent and not prereq_talent.unlocked:
                requirements.append(f"Requires: {prereq_talent.name}")
        
        # Check points
        available_points = self.available_points.get(self.current_tab, 0)
        if available_points < talent.cost:
            needed_points = talent.cost - available_points
            requirements.append(f"Need {needed_points} more {self.current_tab} points")
        
        if requirements:
            print(f"Cannot unlock {talent.name}:")
            for req in requirements:
                print(f"  - {req}")
    
    def _clear_talent_display(self):
        """Clear all talent-related UI elements."""
        # Clear talent buttons
        for button in self.talent_buttons.values():
            if hasattr(button, 'enabled'):
                button.enabled = False
        self.talent_buttons.clear()
        
        # Clear talent texts
        for text in self.talent_texts:
            if hasattr(text, 'enabled'):
                text.enabled = False
        self.talent_texts.clear()
        
        # Clear connection lines
        for line in self.connection_lines:
            if hasattr(line, 'enabled'):
                line.enabled = False
        self.connection_lines.clear()
    
    def set_character(self, character):
        """Set the character whose talents to display."""
        self.current_character = character
        
        if character:
            # Update character name
            char_name = getattr(character, 'name', 'Unknown')
            self.character_name_text.text = f"Character: {char_name}"
            
            # Update available points (placeholder logic)
            level = getattr(character, 'level', 1)
            for talent_type in self.talent_tabs:
                self.available_points[talent_type] = max(0, level - 1)
        else:
            self.character_name_text.text = "Character: None Selected"
            for talent_type in self.talent_tabs:
                self.available_points[talent_type] = 0
        
        self._update_talent_display()
    
    def add_talent_points(self, talent_type: str, points: int):
        """Add talent points for specific category."""
        if talent_type in self.available_points:
            self.available_points[talent_type] += points
            if self.current_tab == talent_type:
                self._update_talent_display()
    
    def update_content(self, data: Dict[str, Any]):
        """Update panel content with new data."""
        if 'character' in data:
            self.set_character(data['character'])
        
        if 'talent_points' in data:
            points_data = data['talent_points']
            for talent_type, points in points_data.items():
                self.add_talent_points(talent_type, points)