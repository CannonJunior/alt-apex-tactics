"""
Legacy BattleGrid Wrapper

Provides backwards compatibility for the old BattleGrid class API while using modern TacticalGrid.
Extracted from apex-tactics.py to maintain clean separation.
"""

from typing import Dict, Tuple, Optional, Any

from core.math.grid import TacticalGrid
from core.math.vector import Vector2Int


class BattleGrid:
    """
    Legacy wrapper around TacticalGrid for backwards compatibility.
    
    This maintains the exact same API as the original BattleGrid class in apex-tactics.py
    while using the modern TacticalGrid system underneath.
    """
    
    def __init__(self, width: int = 8, height: int = 8):
        """
        Initialize battle grid.
        
        Args:
            width: Grid width in tiles
            height: Grid height in tiles
        """
        self.width, self.height = width, height
        self.grid = TacticalGrid(width, height)
        self.units: Dict[Tuple[int, int], Any] = {}
        self.selected_unit: Optional[Any] = None
    
    def is_valid(self, x: int, y: int) -> bool:
        """
        Check if a position is valid for movement.
        
        Args:
            x, y: Grid coordinates to check
            
        Returns:
            True if position is valid and unoccupied
        """
        grid_pos = Vector2Int(x, y)
        if not self.grid.is_valid_position(grid_pos):
            return False
        return (x, y) not in self.units
    
    def add_unit(self, unit: Any) -> None:
        """
        Add a unit to the grid.
        
        Args:
            unit: Unit object with x, y properties
        """
        self.units[(unit.x, unit.y)] = unit
        
        # Also update the grid
        try:
            grid_pos = Vector2Int(unit.x, unit.y)
            cell = self.grid.get_cell(grid_pos)
            if cell:
                cell.occupied = True
        except Exception as e:
            print(f"⚠ Could not update grid cell: {e}")
    
    def move_unit(self, unit: Any, x: int, y: int) -> bool:
        """
        Move a unit to a new position.
        
        Args:
            unit: Unit to move
            x, y: Target coordinates
            
        Returns:
            True if move was successful
        """
        if not unit.can_move_to(x, y, self):
            return False
        
        distance = abs(x - unit.x) + abs(y - unit.y)
        
        # Clear old position
        try:
            old_pos = Vector2Int(unit.x, unit.y)
            old_cell = self.grid.get_cell(old_pos)
            if old_cell:
                old_cell.occupied = False
        except Exception as e:
            print(f"⚠ Could not clear old grid cell: {e}")
        
        # Remove from old position in units dict
        if (unit.x, unit.y) in self.units:
            del self.units[(unit.x, unit.y)]
        
        # Set new position
        unit.x, unit.y = x, y
        unit.current_move_points -= distance
        self.units[(x, y)] = unit
        
        # Update grid cell
        try:
            new_pos = Vector2Int(x, y)
            new_cell = self.grid.get_cell(new_pos)
            if new_cell:
                new_cell.occupied = True
        except Exception as e:
            print(f"⚠ Could not update new grid cell: {e}")
        
        return True
    
    def get_unit_at(self, x: int, y: int) -> Optional[Any]:
        """
        Get unit at specified position.
        
        Args:
            x, y: Grid coordinates
            
        Returns:
            Unit at position or None
        """
        return self.units.get((x, y))
    
    def remove_unit(self, unit: Any) -> bool:
        """
        Remove a unit from the grid.
        
        Args:
            unit: Unit to remove
            
        Returns:
            True if unit was removed
        """
        position = (unit.x, unit.y)
        if position in self.units:
            del self.units[position]
            
            # Clear grid cell
            try:
                grid_pos = Vector2Int(unit.x, unit.y)
                cell = self.grid.get_cell(grid_pos)
                if cell:
                    cell.occupied = False
            except Exception as e:
                print(f"⚠ Could not clear grid cell: {e}")
            
            return True
        return False
    
    def get_all_units(self) -> list:
        """Get list of all units on the grid."""
        return list(self.units.values())
    
    def get_units_in_range(self, x: int, y: int, range_distance: int) -> list:
        """
        Get all units within range of a position.
        
        Args:
            x, y: Center position
            range_distance: Maximum distance
            
        Returns:
            List of units within range
        """
        units_in_range = []
        for pos, unit in self.units.items():
            distance = abs(pos[0] - x) + abs(pos[1] - y)
            if distance <= range_distance:
                units_in_range.append(unit)
        return units_in_range
    
    def is_position_occupied(self, x: int, y: int) -> bool:
        """Check if position has a unit."""
        return (x, y) in self.units
    
    def clear_all_units(self) -> None:
        """Remove all units from the grid."""
        for unit in list(self.units.values()):
            self.remove_unit(unit)