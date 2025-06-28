"""
Inventory Panel Implementation

Displays party inventory organized by item types with tabs.
Shows equipped items in grayscale with character tooltips.
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
class InventoryItem:
    """Represents an item in the inventory."""
    name: str
    item_type: str
    tier: str
    equipped_by: Optional[str] = None
    description: str = ""
    quantity: int = 1


class InventoryPanel(BasePanel):
    """
    Inventory management panel showing all party items.
    
    Features:
    - Tabbed interface by item type
    - Equipped items shown in grayscale
    - Character tooltips for equipped items
    - Item sorting and filtering
    """
    
    def __init__(self, game_reference: Optional[Any] = None):
        """Initialize inventory panel."""
        config = PanelConfig(
            title="Inventory",
            width=0.6,
            height=0.8,
            x_position=0.5,  # Center of screen
            y_position=0.6,
            z_layer=2,
            visible=False
        )
        
        # Inventory data
        self.inventory_items: List[InventoryItem] = []
        self.current_tab = "All"
        self.item_types = ["All", "Weapons", "Armor", "Accessories", "Consumables", "Materials"]
        
        # UI elements
        self.tab_buttons = {}
        self.item_display_texts = []
        self.scroll_offset = 0
        self.max_visible_items = 15
        
        super().__init__(config, game_reference)
    
    def _create_content(self):
        """Create inventory panel content."""
        if not URSINA_AVAILABLE:
            return
        
        # Create tab navigation
        self._create_tab_buttons()
        
        # Create item display area
        self._create_item_display()
        
        # Create scroll controls
        self._create_scroll_controls()
        
        # Initialize with sample data
        self._load_sample_data()
        self._update_item_display()
    
    def _create_tab_buttons(self):
        """Create tab buttons for item type filtering."""
        tab_y = 0.28
        tab_width = 0.08
        start_x = -0.25
        
        for i, item_type in enumerate(self.item_types):
            x_pos = start_x + (i * tab_width)
            
            # Determine button color
            button_color = color.orange if item_type == self.current_tab else color.dark_gray
            
            tab_button = self.add_button_element(
                text=item_type,
                position=(x_pos, tab_y, -0.01),
                size=(tab_width * 0.9, 0.03),
                callback=lambda t=item_type: self._switch_tab(t),
                button_color=button_color
            )
            
            self.tab_buttons[item_type] = tab_button
    
    def _create_item_display(self):
        """Create scrollable item display area."""
        self.item_display_area_y = 0.2
        self.item_line_height = 0.025
        
        # Create header
        self.add_text_element(
            "Items in Inventory:",
            (0, self.item_display_area_y, -0.01),
            scale=0.8,
            text_color=color.yellow
        )
        
        # Item display will be created dynamically in _update_item_display()
    
    def _create_scroll_controls(self):
        """Create scroll up/down buttons."""
        scroll_x = 0.22
        
        self.scroll_up_btn = self.add_button_element(
            text="↑",
            position=(scroll_x, 0.1, -0.01),
            size=(0.04, 0.03),
            callback=self._scroll_up,
            button_color=color.blue
        )
        
        self.scroll_down_btn = self.add_button_element(
            text="↓",
            position=(scroll_x, -0.15, -0.01),
            size=(0.04, 0.03),
            callback=self._scroll_down,
            button_color=color.blue
        )
    
    def _switch_tab(self, tab_name: str):
        """Switch to different item type tab."""
        self.current_tab = tab_name
        self.scroll_offset = 0
        
        # Update tab button colors
        for tab, button in self.tab_buttons.items():
            if hasattr(button, 'color'):
                button.color = color.orange if tab == tab_name else color.dark_gray
        
        self._update_item_display()
    
    def _scroll_up(self):
        """Scroll item list up."""
        if self.scroll_offset > 0:
            self.scroll_offset -= 1
            self._update_item_display()
    
    def _scroll_down(self):
        """Scroll item list down."""
        filtered_items = self._get_filtered_items()
        max_scroll = max(0, len(filtered_items) - self.max_visible_items)
        
        if self.scroll_offset < max_scroll:
            self.scroll_offset += 1
            self._update_item_display()
    
    def _get_filtered_items(self) -> List[InventoryItem]:
        """Get items filtered by current tab."""
        if self.current_tab == "All":
            return self.inventory_items
        
        return [item for item in self.inventory_items if item.item_type == self.current_tab]
    
    def _update_item_display(self):
        """Update the item display area with current items."""
        # Clear existing item texts
        for text_element in self.item_display_texts:
            if hasattr(text_element, 'enabled'):
                text_element.enabled = False
        self.item_display_texts.clear()
        
        # Get items to display
        filtered_items = self._get_filtered_items()
        display_items = filtered_items[self.scroll_offset:self.scroll_offset + self.max_visible_items]
        
        # Create item text elements
        for i, item in enumerate(display_items):
            y_pos = self.item_display_area_y - 0.05 - (i * self.item_line_height)
            
            # Format item text
            item_text = self._format_item_text(item)
            
            # Determine color (grayscale for equipped items)
            text_color = color.gray if item.equipped_by else color.white
            
            # Create text element
            text_element = self.add_text_element(
                text=item_text,
                position=(0, y_pos, -0.01),
                scale=0.6,
                text_color=text_color
            )
            
            self.item_display_texts.append(text_element)
        
        # Update scroll info
        if filtered_items:
            scroll_info = f"Showing {self.scroll_offset + 1}-{min(self.scroll_offset + len(display_items), len(filtered_items))} of {len(filtered_items)}"
            self.add_text_element(
                text=scroll_info,
                position=(0, -0.25, -0.01),
                scale=0.5,
                text_color=color.light_gray
            )
    
    def _format_item_text(self, item: InventoryItem) -> str:
        """Format item for display."""
        equipped_info = f" (Equipped by {item.equipped_by})" if item.equipped_by else ""
        quantity_info = f" x{item.quantity}" if item.quantity > 1 else ""
        
        return f"{item.name} [{item.tier}]{quantity_info}{equipped_info}"
    
    def _load_sample_data(self):
        """Load sample inventory data for testing."""
        self.inventory_items = [
            InventoryItem("Iron Sword", "Weapons", "BASE", "Hero"),
            InventoryItem("Steel Axe", "Weapons", "ENHANCED"),
            InventoryItem("Enchanted Bow", "Weapons", "ENCHANTED"),
            InventoryItem("Leather Armor", "Armor", "BASE", "Hero"),
            InventoryItem("Chain Mail", "Armor", "ENHANCED"),
            InventoryItem("Plate Armor", "Armor", "ENCHANTED"),
            InventoryItem("Magic Ring", "Accessories", "ENHANCED", "Mage"),
            InventoryItem("Health Potion", "Consumables", "BASE", quantity=5),
            InventoryItem("Mana Potion", "Consumables", "BASE", quantity=3),
            InventoryItem("Iron Ore", "Materials", "BASE", quantity=10),
            InventoryItem("Magic Crystal", "Materials", "ENHANCED", quantity=2),
            InventoryItem("Dragon Scale", "Materials", "SUPERPOWERED"),
            InventoryItem("Helmet of Wisdom", "Armor", "SUPERPOWERED"),
            InventoryItem("Boots of Speed", "Armor", "ENCHANTED", "Rogue"),
            InventoryItem("Staff of Power", "Weapons", "METAPOWERED")
        ]
    
    def add_item(self, item: InventoryItem):
        """Add item to inventory."""
        # Check if item already exists (for stackable items)
        existing_item = None
        for inv_item in self.inventory_items:
            if (inv_item.name == item.name and 
                inv_item.tier == item.tier and 
                not inv_item.equipped_by):
                existing_item = inv_item
                break
        
        if existing_item and item.item_type == "Consumables":
            existing_item.quantity += item.quantity
        else:
            self.inventory_items.append(item)
        
        self._update_item_display()
    
    def remove_item(self, item_name: str, quantity: int = 1) -> bool:
        """Remove item from inventory."""
        for item in self.inventory_items:
            if item.name == item_name and not item.equipped_by:
                if item.quantity > quantity:
                    item.quantity -= quantity
                    self._update_item_display()
                    return True
                elif item.quantity == quantity:
                    self.inventory_items.remove(item)
                    self._update_item_display()
                    return True
        return False
    
    def equip_item(self, item_name: str, character_name: str) -> bool:
        """Mark item as equipped by character."""
        for item in self.inventory_items:
            if item.name == item_name and not item.equipped_by:
                item.equipped_by = character_name
                self._update_item_display()
                return True
        return False
    
    def unequip_item(self, item_name: str) -> bool:
        """Mark item as unequipped."""
        for item in self.inventory_items:
            if item.name == item_name and item.equipped_by:
                item.equipped_by = None
                self._update_item_display()
                return True
        return False
    
    def get_items_by_type(self, item_type: str) -> List[InventoryItem]:
        """Get all items of specific type."""
        return [item for item in self.inventory_items if item.item_type == item_type]
    
    def get_equipped_items(self, character_name: str) -> List[InventoryItem]:
        """Get all items equipped by specific character."""
        return [item for item in self.inventory_items if item.equipped_by == character_name]
    
    def update_content(self, data: Dict[str, Any]):
        """
        Update panel content with new data.
        
        Args:
            data: Dictionary with inventory data
        """
        if 'inventory' in data:
            self.inventory_items = data['inventory']
            self._update_item_display()
        
        if 'add_item' in data:
            self.add_item(data['add_item'])
        
        if 'remove_item' in data:
            item_name = data['remove_item'].get('name')
            quantity = data['remove_item'].get('quantity', 1)
            if item_name:
                self.remove_item(item_name, quantity)