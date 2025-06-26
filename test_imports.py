#!/usr/bin/env uv run
"""
Quick test to verify imports work correctly
"""

import sys
import os

# Setup imports
script_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(script_dir, 'src')
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

def test_imports():
    """Test all required imports"""
    print("Testing imports...")
    
    try:
        print("Testing core ECS...")
        from core.ecs.world import World
        from core.ecs.entity import Entity
        from core.ecs.component import BaseComponent, Transform
        print("✓ Core ECS imports work")
        
        print("Testing components...")
        from components.stats.attributes import AttributeStats
        from components.combat.attack import AttackComponent
        from components.combat.defense import DefenseComponent
        from components.movement.movement import MovementComponent
        from components.gameplay.unit_type import UnitTypeComponent, UnitType
        from components.gameplay.tactical_movement import TacticalMovementComponent
        print("✓ Component imports work")
        
        print("Testing systems...")
        from systems.combat_system import CombatSystem
        from game.battle.battle_manager import BattleManager
        print("✓ System imports work")
        
        print("Testing demo utilities...")
        from demos.unit_converter import UnitConverter
        print("✓ Demo utilities import work")
        
        print("Testing demo functionality...")
        world = World()
        entities = UnitConverter.create_demo_army(world, 3)
        print(f"✓ Created {len(entities)} test entities")
        
        # Test a conversion
        apex_unit = UnitConverter.create_apex_unit("Test", UnitType.HEROMANCER, 1, 1)
        entity = UnitConverter.apex_unit_to_entity(apex_unit, world)
        print(f"✓ Converted unit to entity with {len(entity.get_component_types())} components")
        
        print("\n🎉 All imports and basic functionality work!")
        return True
        
    except Exception as e:
        print(f"✗ Import/test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_imports()
    if success:
        print("\n✅ The modular demo is ready to run!")
        print("Use: uv run run_modular_demo.py")
    else:
        print("\n❌ Import tests failed")
        sys.exit(1)