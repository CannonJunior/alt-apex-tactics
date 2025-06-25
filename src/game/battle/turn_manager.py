"""
Turn Manager System

Manages turn order, initiative, and turn phases in tactical combat.
"""

from enum import Enum
from typing import List, Dict, Optional, Callable
from dataclasses import dataclass
from core.ecs.entity import Entity
from components.stats.attributes import AttributeStats
from .action_queue import ActionQueue, BattleAction


class TurnPhase(Enum):
    """Phases of a combat turn"""
    INITIATIVE = "initiative"      # Calculate turn order
    PLANNING = "planning"          # Players/AI plan actions
    EXECUTION = "execution"        # Execute all actions
    RESOLUTION = "resolution"      # Apply effects, check victory
    END_TURN = "end_turn"         # Clean up, prepare next turn


@dataclass
class InitiativeEntry:
    """Entry in the initiative order"""
    unit_id: int
    initiative_value: int
    has_acted: bool = False
    is_player_controlled: bool = True


class TurnManager:
    """
    Manages turn-based combat flow and initiative order.
    """
    
    def __init__(self):
        self.action_queue = ActionQueue()
        self.current_phase = TurnPhase.INITIATIVE
        self.initiative_order: List[InitiativeEntry] = []
        self.current_unit_index = 0
        
        # Phase callbacks
        self.phase_callbacks: Dict[TurnPhase, List[Callable]] = {
            phase: [] for phase in TurnPhase
        }
        
        # Turn state
        self.turn_number = 1
        self.round_number = 1  # Round = all units have acted once
        self.is_combat_active = False
    
    def start_combat(self, units: List[Entity]):
        """
        Initialize combat with participating units.
        
        Args:
            units: List of entities participating in combat
        """
        self.is_combat_active = True
        self.turn_number = 1
        self.round_number = 1
        self.current_unit_index = 0
        
        # Calculate initiative order
        self._calculate_initiative(units)
        self._advance_phase(TurnPhase.INITIATIVE)
    
    def _calculate_initiative(self, units: List[Entity]):
        """
        Calculate initiative order based on unit speed and randomness.
        
        Args:
            units: Units to calculate initiative for
        """
        import random
        
        initiative_list = []
        
        for unit in units:
            attributes = unit.get_component(AttributeStats)
            if not attributes:
                continue
            
            # Base initiative from speed attribute
            base_initiative = attributes.speed
            
            # Add random factor (1d20)
            random_factor = random.randint(1, 20)
            
            # Total initiative
            total_initiative = base_initiative + random_factor
            
            initiative_list.append(InitiativeEntry(
                unit_id=unit.id,
                initiative_value=total_initiative,
                is_player_controlled=True  # TODO: Implement proper player/AI detection
            ))
        
        # Sort by initiative (highest first)
        initiative_list.sort(key=lambda x: x.initiative_value, reverse=True)
        self.initiative_order = initiative_list
    
    def get_current_unit(self) -> Optional[int]:
        """
        Get ID of unit whose turn it is.
        
        Returns:
            Unit ID or None if no active unit
        """
        if not self.initiative_order or self.current_unit_index >= len(self.initiative_order):
            return None
        
        return self.initiative_order[self.current_unit_index].unit_id
    
    def advance_to_next_unit(self):
        """Advance to the next unit in initiative order"""
        if not self.initiative_order:
            return
        
        # Mark current unit as having acted
        if self.current_unit_index < len(self.initiative_order):
            self.initiative_order[self.current_unit_index].has_acted = True
        
        self.current_unit_index += 1
        
        # Check if round is complete
        if self.current_unit_index >= len(self.initiative_order):
            self._end_round()
    
    def _end_round(self):
        """End current round and start new one"""
        self.round_number += 1
        self.current_unit_index = 0
        
        # Reset has_acted flags
        for entry in self.initiative_order:
            entry.has_acted = False
        
        # Advance to next turn phase
        self._advance_phase(TurnPhase.END_TURN)
    
    def _advance_phase(self, new_phase: TurnPhase):
        """
        Advance to a new turn phase.
        
        Args:
            new_phase: Phase to advance to
        """
        old_phase = self.current_phase
        self.current_phase = new_phase
        
        # Execute phase callbacks
        for callback in self.phase_callbacks.get(new_phase, []):
            try:
                callback(old_phase, new_phase)
            except Exception as e:
                print(f"Error in phase callback: {e}")
        
        # Handle automatic phase transitions
        if new_phase == TurnPhase.INITIATIVE:
            self._advance_phase(TurnPhase.PLANNING)
        elif new_phase == TurnPhase.END_TURN:
            self.turn_number += 1
            self._advance_phase(TurnPhase.PLANNING)
    
    def add_phase_callback(self, phase: TurnPhase, callback: Callable):
        """Add callback for specific turn phase"""
        self.phase_callbacks[phase].append(callback)
    
    def queue_action(self, action: BattleAction) -> bool:
        """
        Queue an action for execution.
        
        Args:
            action: Action to queue
            
        Returns:
            True if action was successfully queued
        """
        return self.action_queue.add_action(action)
    
    def execute_turn_actions(self) -> List[BattleAction]:
        """
        Execute all queued actions for current turn.
        
        Returns:
            List of executed actions
        """
        if self.current_phase != TurnPhase.EXECUTION:
            return []
        
        executed_actions = self.action_queue.execute_all_actions()
        
        # Advance to resolution phase
        self._advance_phase(TurnPhase.RESOLUTION)
        
        return executed_actions
    
    def can_unit_act(self, unit_id: int) -> bool:
        """
        Check if unit can act this turn.
        
        Args:
            unit_id: ID of unit to check
            
        Returns:
            True if unit can act
        """
        # Find unit in initiative order
        for entry in self.initiative_order:
            if entry.unit_id == unit_id:
                return not entry.has_acted
        return False
    
    def get_initiative_order(self) -> List[InitiativeEntry]:
        """Get current initiative order"""
        return self.initiative_order.copy()
    
    def get_turn_summary(self) -> dict:
        """Get comprehensive turn state summary"""
        current_unit = self.get_current_unit()
        
        return {
            'turn_number': self.turn_number,
            'round_number': self.round_number,
            'current_phase': self.current_phase.value,
            'current_unit_id': current_unit,
            'current_unit_index': self.current_unit_index,
            'total_units': len(self.initiative_order),
            'is_combat_active': self.is_combat_active,
            'action_queue_summary': self.action_queue.get_queue_summary(),
            'units_acted': sum(1 for entry in self.initiative_order if entry.has_acted),
            'initiative_order': [
                {
                    'unit_id': entry.unit_id,
                    'initiative': entry.initiative_value,
                    'has_acted': entry.has_acted,
                    'is_player': entry.is_player_controlled
                }
                for entry in self.initiative_order
            ]
        }
    
    def end_unit_turn(self, unit_id: int):
        """
        End turn for specific unit.
        
        Args:
            unit_id: ID of unit ending turn
        """
        if self.get_current_unit() == unit_id:
            self.advance_to_next_unit()
    
    def skip_unit_turn(self, unit_id: int):
        """
        Skip turn for specific unit.
        
        Args:
            unit_id: ID of unit to skip
        """
        # Add wait action for unit
        wait_action = BattleAction(
            unit_id=unit_id,
            action_type=ActionType.WAIT
        )
        self.queue_action(wait_action)
        self.end_unit_turn(unit_id)
    
    def end_combat(self):
        """End combat and clean up"""
        self.is_combat_active = False
        self.action_queue.clear_queue()
        self.initiative_order.clear()
        self.current_unit_index = 0
        self.current_phase = TurnPhase.INITIATIVE