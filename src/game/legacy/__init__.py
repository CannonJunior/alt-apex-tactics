"""
Legacy compatibility wrappers for backwards compatibility.

These wrappers maintain the old API while using modern ECS components underneath.
"""

from .unit_wrapper import Unit
from .battle_grid_wrapper import BattleGrid
from .turn_manager_wrapper import TurnManager

__all__ = ['Unit', 'BattleGrid', 'TurnManager']