"""
Inventory Panel Implementation

Displays party inventory organized by item types with tabs.
Shows equipped items in grayscale with character tooltips.
Toggleable with 'i' key.
"""

from typing import Optional, Dict, Any, List

try:
    from ursina import Text, Button, color
    from ursina.prefabs.window_panel import WindowPanel
    URSINA_AVAILABLE = True
except ImportError:
    URSINA_AVAILABLE = False


class InventoryPanel:
    """
    Inventory management panel showing all party items.
    
    Features:
    - Tabbed interface by item type
    - Equipped items shown in grayscale
    - Item sorting and filtering
    """
    
    def __init__(self, game_reference: Optional[Any] = None):
        """Initialize inventory panel."""
        if not URSINA_AVAILABLE:
            raise ImportError("Ursina is required for InventoryPanel")
        
        self.game_reference = game_reference
        self.current_tab = "All"
        self.inventory_items: List[Dict[str, Any]] = []
        
        # Create text elements
        self._create_text_elements()
        
        # Create main panel
        self._create_main_panel()
        
        # Position panel
        self._position_panel()
        
        # Load sample data
        self._load_sample_data()
        self._update_display()
    
    def _create_text_elements(self):
        """Create all text display elements."""
        self.inventory_title_text = Text('Party Inventory')
        self.current_tab_text = Text('Current Tab: All Items')
        self.item_count_text = Text('Items: 0')
        
        # Item display lines (showing top 10 items)
        self.item_texts = []
        for i in range(10):
            item_text = Text(f'Item {i+1}: Empty')
            self.item_texts.append(item_text)
        
        # Tab buttons simulation
        self.tab_info_text = Text('Tabs: All | Weapons | Armor | Accessories | Consumables | Materials')
    
    def _create_main_panel(self):
        """Create the main window panel with all content."""
        content_list = [
            self.inventory_title_text,
            self.current_tab_text,
            self.item_count_text,
            Text('--- ITEMS ---'),
        ]
        
        # Add item display texts
        content_list.extend(self.item_texts)
        
        # Add tab information
        content_list.append(Text('--- CONTROLS ---'))
        content_list.append(self.tab_info_text)
        
        self.panel = WindowPanel(
            title='Party Inventory',
            content=tuple(content_list),
            popup=False
        )
        # Start hidden
        self.panel.enabled = False
    
    def _position_panel(self):
        """Position the panel on the left side of the screen."""
        self.panel.x = -0.5
        self.panel.y = 0.0
        self.panel.layout()
    
    def _load_sample_data(self):
        """Load sample inventory data for testing."""
        self.inventory_items = [
            {"name": "Iron Sword", "type": "Weapons", "tier": "BASE", "equipped_by": "Hero", "quantity": 1},
            {"name": "Steel Axe", "type": "Weapons", "tier": "ENHANCED", "equipped_by": None, "quantity": 1},
            {"name": "Enchanted Bow", "type": "Weapons", "tier": "ENCHANTED", "equipped_by": None, "quantity": 1},
            {"name": "Leather Armor", "type": "Armor", "tier": "BASE", "equipped_by": "Hero", "quantity": 1},
            {"name": "Chain Mail", "type": "Armor", "tier": "ENHANCED", "equipped_by": None, "quantity": 1},
            {"name": "Magic Ring", "type": "Accessories", "tier": "ENHANCED", "equipped_by": "Mage", "quantity": 1},
            {"name": "Health Potion", "type": "Consumables", "tier": "BASE", "equipped_by": None, "quantity": 5},
            {"name": "Mana Potion", "type": "Consumables", "tier": "BASE", "equipped_by": None, "quantity": 3},
            {"name": "Iron Ore", "type": "Materials", "tier": "BASE", "equipped_by": None, "quantity": 10},
            {"name": "Magic Crystal", "type": "Materials", "tier": "ENHANCED", "equipped_by": None, "quantity": 2},
        ]
    
    def _update_display(self):
        """Update all display elements with current inventory data."""
        # Update tab and count information
        self.current_tab_text.text = f'Current Tab: {self.current_tab}'
        
        # Filter items based on current tab
        filtered_items = self._get_filtered_items()
        self.item_count_text.text = f'Items: {len(filtered_items)}'
        
        # Update item display (show first 10 items)
        for i, item_text in enumerate(self.item_texts):
            if i < len(filtered_items):
                item = filtered_items[i]
                equipped_info = f" (Equipped by {item['equipped_by']})" if item['equipped_by'] else ""
                quantity_info = f" x{item['quantity']}" if item['quantity'] > 1 else ""
                item_text.text = f"{item['name']} [{item['tier']}]{quantity_info}{equipped_info}"
            else:
                item_text.text = f'Item {i+1}: Empty'
    
    def _get_filtered_items(self) -> List[Dict[str, Any]]:
        """Get items filtered by current tab."""
        if self.current_tab == "All":
            return self.inventory_items
        return [item for item in self.inventory_items if item['type'] == self.current_tab]
    
    def switch_tab(self, tab_name: str):
        """Switch to different item type tab."""
        valid_tabs = ["All", "Weapons", "Armor", "Accessories", "Consumables", "Materials"]
        if tab_name in valid_tabs:
            self.current_tab = tab_name
            self._update_display()
    
    def add_item(self, item: Dict[str, Any]):
        """Add item to inventory."""
        self.inventory_items.append(item)
        self._update_display()
    
    def remove_item(self, item_name: str) -> bool:
        """Remove item from inventory."""
        for item in self.inventory_items:
            if item['name'] == item_name and not item['equipped_by']:
                self.inventory_items.remove(item)
                self._update_display()
                return True
        return False
    
    def toggle_visibility(self):
        """Toggle the visibility of the inventory panel."""
        if hasattr(self, 'panel') and self.panel:
            self.panel.enabled = not self.panel.enabled
            status = "shown" if self.panel.enabled else "hidden"
            print(f"Inventory panel {status}")
    
    def show(self):
        """Show the inventory panel."""
        if hasattr(self, 'panel') and self.panel:
            self.panel.enabled = True
    
    def hide(self):
        """Hide the inventory panel."""
        if hasattr(self, 'panel') and self.panel:
            self.panel.enabled = False
    
    def is_visible(self) -> bool:
        """Check if the inventory panel is currently visible."""
        if hasattr(self, 'panel') and self.panel:
            return self.panel.enabled
        return False
    
    def update_content(self, data: Dict[str, Any]):
        """
        Update panel content with new data.
        
        Args:
            data: Dictionary with inventory data
        """
        if 'inventory' in data:
            self.inventory_items = data['inventory']
            self._update_display()
    
    def set_game_reference(self, game: Any):
        """
        Set reference to the main game object.
        
        Args:
            game: Main game object
        """
        self.game_reference = game
    
    def cleanup(self):
        """Clean up panel resources."""
        if hasattr(self, 'panel') and self.panel:
            self.panel.enabled = False