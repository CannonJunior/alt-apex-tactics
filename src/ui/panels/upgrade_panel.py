"""
Upgrade Panel Implementation

Handles item tier progression from Base to Metapowered.
Includes upgrade materials, success rates, and sentient item interactions.
"""

from typing import Optional, Dict, Any, List, Tuple
from dataclasses import dataclass
from .base_panel import BasePanel, PanelConfig
import random

try:
    from ursina import Entity, Text, Button, color, camera
    URSINA_AVAILABLE = True
except ImportError:
    URSINA_AVAILABLE = False


@dataclass
class UpgradeableItem:
    """Represents an item that can be upgraded."""
    name: str
    current_tier: str
    item_type: str
    base_stats: Dict[str, int]
    enhancement_level: int = 0
    is_sentient: bool = False


@dataclass
class UpgradeMaterial:
    """Represents materials used for upgrades."""
    name: str
    tier: str
    quantity: int
    description: str


class UpgradePanel(BasePanel):
    """
    Item upgrade panel for tier progression system.
    
    Features:
    - Item tier progression: BASE → ENHANCED → ENCHANTED → SUPERPOWERED → METAPOWERED
    - Upgrade material requirements and success rates
    - Sentient item destruction warnings
    - Preview of upgrade results
    """
    
    # Tier progression data
    TIER_ORDER = ["BASE", "ENHANCED", "ENCHANTED", "SUPERPOWERED", "METAPOWERED"]
    TIER_MULTIPLIERS = {
        "BASE": 1.0,
        "ENHANCED": 1.4,
        "ENCHANTED": 2.0,
        "SUPERPOWERED": 3.0,
        "METAPOWERED": 4.5
    }
    
    def __init__(self, game_reference: Optional[Any] = None):
        """Initialize upgrade panel."""
        config = PanelConfig(
            title="Upgrade Workshop",
            width=0.7,
            height=0.8,
            x_position=0.5,  # Center of screen
            y_position=0.6,
            z_layer=2,
            visible=False
        )
        
        # Upgrade data
        self.selected_item: Optional[UpgradeableItem] = None
        self.available_items: List[UpgradeableItem] = []
        self.upgrade_materials: List[UpgradeMaterial] = []
        self.destruction_mode = False
        
        # UI elements
        self.item_list_texts = []
        self.material_list_texts = []
        self.upgrade_preview_texts = []
        
        super().__init__(config, game_reference)
    
    def _create_content(self):
        """Create upgrade panel content."""
        if not URSINA_AVAILABLE:
            return
        
        # Create main sections
        self._create_item_selection_section()
        self._create_upgrade_materials_section()
        self._create_upgrade_preview_section()
        self._create_action_buttons()
        
        # Load sample data
        self._load_sample_data()
        self._update_displays()
    
    def _create_item_selection_section(self):
        """Create item selection area."""
        item_y = 0.28
        
        self.add_text_element(
            "--- SELECT ITEM TO UPGRADE ---",
            (-0.2, item_y, -0.01),
            scale=0.8,
            text_color=color.yellow
        )
        
        # Mode toggle
        self.mode_text = self.add_text_element(
            "Mode: Upgrade",
            (-0.2, item_y - 0.04, -0.01),
            scale=0.6,
            text_color=color.green
        )
        
        self.toggle_mode_btn = self.add_button_element(
            text="Switch to Destruction",
            position=(-0.05, item_y - 0.04, -0.01),
            size=(0.12, 0.03),
            callback=self._toggle_mode,
            button_color=color.orange
        )
        
        # Item list area (will be populated in _update_item_list())
        self.item_list_y = item_y - 0.08
    
    def _create_upgrade_materials_section(self):
        """Create upgrade materials display."""
        materials_y = 0.28
        
        self.add_text_element(
            "--- MATERIALS ---",
            (0.1, materials_y, -0.01),
            scale=0.8,
            text_color=color.cyan
        )
        
        # Materials list area
        self.materials_list_y = materials_y - 0.04
    
    def _create_upgrade_preview_section(self):
        """Create upgrade preview and requirements."""
        preview_y = -0.05
        
        self.add_text_element(
            "--- UPGRADE PREVIEW ---",
            (0, preview_y, -0.01),
            scale=0.8,
            text_color=color.white
        )
        
        # Preview area
        self.preview_y = preview_y - 0.04
        
        # Selected item info
        self.selected_item_text = self.add_text_element(
            "No item selected",
            (0, self.preview_y, -0.01),
            scale=0.7,
            text_color=color.light_gray
        )
        
        # Requirements
        self.requirements_text = self.add_text_element(
            "",
            (0, self.preview_y - 0.04, -0.01),
            scale=0.6,
            text_color=color.yellow
        )
        
        # Success rate
        self.success_rate_text = self.add_text_element(
            "",
            (0, self.preview_y - 0.08, -0.01),
            scale=0.6,
            text_color=color.orange
        )
        
        # Preview stats
        self.preview_stats_text = self.add_text_element(
            "",
            (0, self.preview_y - 0.12, -0.01),
            scale=0.6,
            text_color=color.green
        )
    
    def _create_action_buttons(self):
        """Create action buttons for upgrade operations."""
        action_y = -0.25
        
        self.upgrade_btn = self.add_button_element(
            text="UPGRADE ITEM",
            position=(-0.1, action_y, -0.01),
            size=(0.12, 0.05),
            callback=self._perform_upgrade,
            button_color=color.green
        )
        
        self.destroy_btn = self.add_button_element(
            text="DESTROY ITEM",
            position=(0.1, action_y, -0.01),
            size=(0.12, 0.05),
            callback=self._perform_destruction,
            button_color=color.red
        )
        
        # Initially hide destroy button
        self.destroy_btn.enabled = False
    
    def _toggle_mode(self):
        """Toggle between upgrade and destruction modes."""
        self.destruction_mode = not self.destruction_mode
        
        if self.destruction_mode:
            self.mode_text.text = "Mode: Destruction"
            self.mode_text.color = color.red
            self.toggle_mode_btn.text = "Switch to Upgrade"
            self.upgrade_btn.enabled = False
            self.destroy_btn.enabled = True
        else:
            self.mode_text.text = "Mode: Upgrade"
            self.mode_text.color = color.green
            self.toggle_mode_btn.text = "Switch to Destruction"
            self.upgrade_btn.enabled = True
            self.destroy_btn.enabled = False
        
        self._update_preview()
    
    def _update_displays(self):
        """Update all display sections."""
        self._update_item_list()
        self._update_materials_list()
        self._update_preview()
    
    def _update_item_list(self):
        """Update the list of upgradeable items."""
        # Clear existing item list
        for text in self.item_list_texts:
            if hasattr(text, 'enabled'):
                text.enabled = False
        self.item_list_texts.clear()
        
        # Display items
        for i, item in enumerate(self.available_items[:6]):  # Show max 6 items
            y_pos = self.item_list_y - (i * 0.025)
            
            # Format item text
            item_text = f"{item.name} [{item.current_tier}]"
            if item.is_sentient:
                item_text += " ⚡"  # Sentient indicator
            
            # Color based on tier
            text_color = self._get_tier_color(item.current_tier)
            if item == self.selected_item:
                text_color = color.yellow
            
            # Create clickable text (simulated button)
            text_element = self.add_text_element(
                item_text,
                (-0.2, y_pos, -0.01),
                scale=0.6,
                text_color=text_color
            )
            
            self.item_list_texts.append(text_element)
            
            # Add click simulation (in real implementation, would use proper button)
            # For now, just selecting first item for demonstration
            if i == 0 and not self.selected_item:
                self.selected_item = item
    
    def _update_materials_list(self):
        """Update available upgrade materials list."""
        # Clear existing materials list
        for text in self.material_list_texts:
            if hasattr(text, 'enabled'):
                text.enabled = False
        self.material_list_texts.clear()
        
        # Display materials
        for i, material in enumerate(self.upgrade_materials[:8]):  # Show max 8 materials
            y_pos = self.materials_list_y - (i * 0.02)
            
            material_text = f"{material.name} x{material.quantity}"
            text_color = self._get_tier_color(material.tier)
            
            text_element = self.add_text_element(
                material_text,
                (0.1, y_pos, -0.01),
                scale=0.5,
                text_color=text_color
            )
            
            self.material_list_texts.append(text_element)
    
    def _update_preview(self):
        """Update upgrade preview section."""
        if not self.selected_item:
            self.selected_item_text.text = "No item selected"
            self.requirements_text.text = ""
            self.success_rate_text.text = ""
            self.preview_stats_text.text = ""
            return
        
        item = self.selected_item
        
        # Selected item info
        self.selected_item_text.text = f"Selected: {item.name} [{item.current_tier}]"
        
        if self.destruction_mode:
            self._update_destruction_preview(item)
        else:
            self._update_upgrade_preview(item)
    
    def _update_upgrade_preview(self, item: UpgradeableItem):
        """Update preview for upgrade mode."""
        next_tier = self._get_next_tier(item.current_tier)
        
        if not next_tier:
            self.requirements_text.text = "Item is already maximum tier"
            self.success_rate_text.text = ""
            self.preview_stats_text.text = ""
            return
        
        # Calculate requirements
        required_materials = self._get_upgrade_requirements(item.current_tier, next_tier)
        self.requirements_text.text = f"Required: {required_materials}"
        
        # Calculate success rate
        success_rate = self._calculate_success_rate(item.current_tier, next_tier)
        self.success_rate_text.text = f"Success Rate: {success_rate}%"
        
        # Preview new stats
        current_multiplier = self.TIER_MULTIPLIERS[item.current_tier]
        next_multiplier = self.TIER_MULTIPLIERS[next_tier]
        
        preview_text = f"Stats will be multiplied by {next_multiplier/current_multiplier:.1f}x"
        if next_tier == "METAPOWERED":
            preview_text += " (Will become SENTIENT!)"
        
        self.preview_stats_text.text = preview_text
    
    def _update_destruction_preview(self, item: UpgradeableItem):
        """Update preview for destruction mode."""
        if item.is_sentient:
            self.requirements_text.text = "⚠️ WARNING: Sentient item may fight back!"
            self.success_rate_text.text = "High chance of battle upon destruction"
            self.preview_stats_text.text = "Sentient items can attack the character"
        else:
            materials_recovered = self._calculate_recovery_materials(item)
            self.requirements_text.text = f"Will recover: {materials_recovered}"
            self.success_rate_text.text = "Destruction guaranteed for non-sentient items"
            self.preview_stats_text.text = "Item will be permanently destroyed"
    
    def _get_tier_color(self, tier: str):
        """Get color for tier display."""
        tier_colors = {
            "BASE": color.white,
            "ENHANCED": color.green,
            "ENCHANTED": color.blue,
            "SUPERPOWERED": color.purple,
            "METAPOWERED": color.gold
        }
        return tier_colors.get(tier, color.gray)
    
    def _get_next_tier(self, current_tier: str) -> Optional[str]:
        """Get the next tier in progression."""
        try:
            current_index = self.TIER_ORDER.index(current_tier)
            if current_index < len(self.TIER_ORDER) - 1:
                return self.TIER_ORDER[current_index + 1]
        except ValueError:
            pass
        return None
    
    def _get_upgrade_requirements(self, current_tier: str, next_tier: str) -> str:
        """Get materials required for upgrade."""
        requirements = {
            ("BASE", "ENHANCED"): "Iron Ore x3, Magic Dust x1",
            ("ENHANCED", "ENCHANTED"): "Mithril x2, Magic Crystal x2",
            ("ENCHANTED", "SUPERPOWERED"): "Dragon Scale x1, Arcane Essence x3",
            ("SUPERPOWERED", "METAPOWERED"): "Cosmic Fragment x1, Soul Gem x2"
        }
        return requirements.get((current_tier, next_tier), "Unknown materials")
    
    def _calculate_success_rate(self, current_tier: str, next_tier: str) -> int:
        """Calculate upgrade success rate."""
        success_rates = {
            ("BASE", "ENHANCED"): 90,
            ("ENHANCED", "ENCHANTED"): 75,
            ("ENCHANTED", "SUPERPOWERED"): 60,
            ("SUPERPOWERED", "METAPOWERED"): 40
        }
        return success_rates.get((current_tier, next_tier), 50)
    
    def _calculate_recovery_materials(self, item: UpgradeableItem) -> str:
        """Calculate materials recovered from destruction."""
        tier_index = self.TIER_ORDER.index(item.current_tier)
        
        # Simplified recovery calculation
        if tier_index == 0:
            return "Basic Materials x2"
        elif tier_index == 1:
            return "Iron Ore x1, Magic Dust x1"
        elif tier_index == 2:
            return "Mithril x1, Magic Crystal x1"
        elif tier_index == 3:
            return "Dragon Scale x1"
        else:
            return "Rare Materials x3"
    
    def _perform_upgrade(self):
        """Perform the upgrade operation."""
        if not self.selected_item or self.destruction_mode:
            return
        
        item = self.selected_item
        next_tier = self._get_next_tier(item.current_tier)
        
        if not next_tier:
            print("Item is already maximum tier!")
            return
        
        # Check materials (simplified - would check actual inventory)
        success_rate = self._calculate_success_rate(item.current_tier, next_tier)
        
        # Simulate upgrade attempt
        if random.randint(1, 100) <= success_rate:
            # Success!
            item.current_tier = next_tier
            if next_tier == "METAPOWERED":
                item.is_sentient = True
            
            print(f"✅ Upgrade successful! {item.name} is now {next_tier}")
            if item.is_sentient:
                print("🧠 The item has gained sentience!")
        else:
            # Failure
            print(f"❌ Upgrade failed! {item.name} was destroyed in the process.")
            self.available_items.remove(item)
            self.selected_item = None
        
        self._update_displays()
    
    def _perform_destruction(self):
        """Perform the destruction operation."""
        if not self.selected_item or not self.destruction_mode:
            return
        
        item = self.selected_item
        
        if item.is_sentient:
            # Sentient item battle chance
            if random.randint(1, 100) <= 70:  # 70% chance of battle
                print(f"⚔️ {item.name} fights back! Initiating 1-on-1 battle!")
                # In real implementation, would start battle sequence
                return
        
        # Successful destruction
        recovered_materials = self._calculate_recovery_materials(item)
        print(f"🔨 Destroyed {item.name}. Recovered: {recovered_materials}")
        
        self.available_items.remove(item)
        self.selected_item = None
        self._update_displays()
    
    def _load_sample_data(self):
        """Load sample upgrade data."""
        self.available_items = [
            UpgradeableItem("Iron Sword", "BASE", "Weapon", {"attack": 10}),
            UpgradeableItem("Magic Ring", "ENHANCED", "Accessory", {"magic": 15}),
            UpgradeableItem("Dragon Helm", "ENCHANTED", "Armor", {"defense": 25}),
            UpgradeableItem("Cosmic Blade", "SUPERPOWERED", "Weapon", {"attack": 45}),
            UpgradeableItem("Sentient Crown", "METAPOWERED", "Armor", {"all_stats": 50}, is_sentient=True)
        ]
        
        self.upgrade_materials = [
            UpgradeMaterial("Iron Ore", "BASE", 10, "Basic metal ore"),
            UpgradeMaterial("Magic Dust", "BASE", 5, "Magical enhancement powder"),
            UpgradeMaterial("Mithril", "ENHANCED", 3, "Precious magical metal"),
            UpgradeMaterial("Magic Crystal", "ENHANCED", 2, "Crystallized magic energy"),
            UpgradeMaterial("Dragon Scale", "ENCHANTED", 1, "Scale from ancient dragon"),
            UpgradeMaterial("Arcane Essence", "ENCHANTED", 4, "Pure magical essence"),
            UpgradeMaterial("Cosmic Fragment", "SUPERPOWERED", 1, "Fragment of cosmic power"),
            UpgradeMaterial("Soul Gem", "SUPERPOWERED", 2, "Gem containing soul energy")
        ]
    
    def select_item(self, item_name: str):
        """Select an item for upgrade/destruction."""
        for item in self.available_items:
            if item.name == item_name:
                self.selected_item = item
                self._update_preview()
                break
    
    def add_upgrade_material(self, material: UpgradeMaterial):
        """Add upgrade material to inventory."""
        # Check if material already exists
        for existing in self.upgrade_materials:
            if existing.name == material.name and existing.tier == material.tier:
                existing.quantity += material.quantity
                self._update_materials_list()
                return
        
        # Add new material
        self.upgrade_materials.append(material)
        self._update_materials_list()
    
    def update_content(self, data: Dict[str, Any]):
        """Update panel content with new data."""
        if 'items' in data:
            self.available_items = [UpgradeableItem(**item_data) for item_data in data['items']]
            self._update_displays()
        
        if 'materials' in data:
            self.upgrade_materials = [UpgradeMaterial(**mat_data) for mat_data in data['materials']]
            self._update_materials_list()
        
        if 'selected_item' in data:
            self.select_item(data['selected_item'])