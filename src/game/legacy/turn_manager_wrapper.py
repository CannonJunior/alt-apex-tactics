"""
Legacy TurnManager Wrapper

Provides backwards compatibility for the old TurnManager class API while using modern ModularTurnManager.
Extracted from apex-tactics.py to maintain clean separation.
"""

from typing import List, Optional, Any

from game.battle.turn_manager import TurnManager as ModularTurnManager


class TurnManager:
    """
    Legacy wrapper around ModularTurnManager for backwards compatibility.
    
    This maintains the exact same API as the original TurnManager class in apex-tactics.py
    while using the modern ModularTurnManager system underneath.
    """
    
    def __init__(self, units: List[Any]):
        """
        Initialize turn manager with units.
        
        Args:
            units: List of unit objects sorted by speed
        """
        self.units = sorted(units, key=lambda u: u.speed, reverse=True)
        self.current_turn = 0
        self.phase = "move"  # move, action, end
        
        # Create modular turn manager
        self.modular_turn_manager = ModularTurnManager()
        
        # Prepare entity list for modular turn manager
        unit_entities = [unit.entity for unit in self.units]
        
        # Start combat with all units
        try:
            self.modular_turn_manager.start_combat(unit_entities)
            print("✓ Modular turn manager initialized successfully")
        except Exception as e:
            print(f"⚠ Could not initialize modular turn manager: {e}")
            # Fallback to legacy system only
            self.modular_turn_manager = None
    
    def next_turn(self) -> None:
        """Advance to the next unit's turn."""
        self.current_turn = (self.current_turn + 1) % len(self.units)
        
        # Advance modular turn manager if available
        if self.modular_turn_manager:
            try:
                self.modular_turn_manager.advance_to_next_unit()
            except Exception as e:
                print(f"⚠ Error advancing modular turn manager: {e}")
        
        if self.current_turn == 0:
            # New round - reset all units
            for unit in self.units:
                unit.ap = unit.max_ap
                unit.current_move_points = unit.move_points  # Reset movement points
    
    def current_unit(self) -> Optional[Any]:
        """
        Get the current active unit.
        
        Returns:
            Current unit or None if no units
        """
        if not self.units:
            return None
        
        # Get current unit from modular system if available
        if self.modular_turn_manager:
            try:
                current_unit_id = self.modular_turn_manager.get_current_unit()
                if current_unit_id:
                    # Find unit by entity ID
                    for unit in self.units:
                        if unit.entity.id == current_unit_id:
                            return unit
            except Exception as e:
                print(f"⚠ Error getting current unit from modular system: {e}")
        
        # Fallback to legacy system
        return self.units[self.current_turn] if self.units else None
    
    def get_turn_order(self) -> List[Any]:
        """Get the complete turn order."""
        return self.units.copy()
    
    def get_current_turn_index(self) -> int:
        """Get the current turn index."""
        return self.current_turn
    
    def reset_turn_order(self, units: List[Any]) -> None:
        """
        Reset turn order with new units.
        
        Args:
            units: New list of units
        """
        self.units = sorted(units, key=lambda u: u.speed, reverse=True)
        self.current_turn = 0
        
        if self.modular_turn_manager:
            try:
                unit_entities = [unit.entity for unit in self.units]
                self.modular_turn_manager.start_combat(unit_entities)
            except Exception as e:
                print(f"⚠ Error resetting modular turn manager: {e}")
    
    def skip_current_turn(self) -> None:
        """Skip the current unit's turn."""
        self.next_turn()
    
    def end_combat(self) -> None:
        """End the current combat."""
        if self.modular_turn_manager:
            try:
                self.modular_turn_manager.end_combat()
            except Exception as e:
                print(f"⚠ Error ending modular turn manager: {e}")
    
    def is_combat_active(self) -> bool:
        """Check if combat is currently active."""
        if self.modular_turn_manager:
            try:
                return self.modular_turn_manager.is_combat_active()
            except Exception as e:
                print(f"⚠ Error checking combat status: {e}")
        
        # Fallback: combat is active if we have units
        return len(self.units) > 0
    
    def get_round_number(self) -> int:
        """Get the current round number."""
        if self.modular_turn_manager:
            try:
                return self.modular_turn_manager.get_current_round()
            except Exception as e:
                print(f"⚠ Error getting round number: {e}")
        
        # Fallback calculation
        total_turns_taken = sum(1 for _ in range(self.current_turn + 1))
        return (total_turns_taken // len(self.units)) + 1 if self.units else 1