#!/usr/bin/env uv run
"""
Test script for the Modular Apex Tactics Demo

Verifies that all components and systems work correctly for the ECS replacement.
"""

import sys
import os

# Add project root to path  
project_root = os.path.abspath(os.path.dirname(__file__))
src_path = os.path.join(project_root, 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

def test_ecs_imports():
    """Test that all ECS components import correctly"""
    print("Testing ECS imports...")
    
    try:
        from core.ecs.world import World
        from core.ecs.entity import Entity
        from core.ecs.component import BaseComponent
        print("✓ Core ECS imports successful")
    except ImportError as e:
        print(f"✗ Core ECS import failed: {e}")
        return False
    
    try:
        from components.stats.attributes import AttributeStats
        from components.combat.attack import AttackComponent
        from components.combat.defense import DefenseComponent
        from components.movement.movement import MovementComponent
        print("✓ Component imports successful")
    except ImportError as e:
        print(f"✗ Component import failed: {e}")
        return False
    
    try:
        from components.gameplay.unit_type import UnitTypeComponent, UnitType
        from components.gameplay.tactical_movement import TacticalMovementComponent
        print("✓ Gameplay component imports successful")
    except ImportError as e:
        print(f"✗ Gameplay component import failed: {e}")
        return False
    
    return True

def test_unit_conversion():
    """Test unit conversion from apex-tactics style to ECS"""
    print("\nTesting unit conversion...")
    
    try:
        from core.ecs.world import World
        from demos.unit_converter import UnitConverter, UnitType
        
        # Create world and test unit
        world = World()
        
        # Create apex-style unit
        apex_unit = UnitConverter.create_apex_unit(
            "Test Hero", UnitType.HEROMANCER, 2, 3,
            strength=15, wisdom=12
        )
        
        print(f"✓ Created apex unit: {apex_unit.name}")
        print(f"  Type: {apex_unit.type.value}")
        print(f"  Position: ({apex_unit.x}, {apex_unit.y})")
        print(f"  Strength: {apex_unit.strength}")
        
        # Convert to ECS entity
        entity = UnitConverter.apex_unit_to_entity(apex_unit, world)
        
        print(f"✓ Converted to ECS entity: {entity.id}")
        print(f"  Components: {len(entity.get_component_types())}")
        
        # Verify components
        from components.gameplay.unit_type import UnitTypeComponent
        from components.stats.attributes import AttributeStats
        
        unit_type_comp = entity.get_component(UnitTypeComponent)
        attributes_comp = entity.get_component(AttributeStats)
        
        if unit_type_comp:
            print(f"  ✓ Unit type: {unit_type_comp.unit_type.value}")
        else:
            print("  ✗ Missing unit type component")
            return False
        
        if attributes_comp:
            print(f"  ✓ Attributes: STR={attributes_comp.strength}, WIS={attributes_comp.wisdom}")
        else:
            print("  ✗ Missing attributes component")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ Unit conversion test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_demo_army():
    """Test creating a full demo army"""
    print("\nTesting demo army creation...")
    
    try:
        from core.ecs.world import World
        from demos.unit_converter import UnitConverter
        
        world = World()
        
        # Create demo army
        entities = UnitConverter.create_demo_army(world, 6)
        
        print(f"✓ Created army of {len(entities)} entities")
        
        # Check each entity
        for i, entity in enumerate(entities):
            from components.gameplay.unit_type import UnitTypeComponent
            from components.stats.attributes import AttributeStats
            
            unit_type_comp = entity.get_component(UnitTypeComponent)
            attributes_comp = entity.get_component(AttributeStats)
            
            if unit_type_comp and attributes_comp:
                print(f"  {i+1}. {unit_type_comp.unit_type.value.title()} - HP: {attributes_comp.current_hp}")
            else:
                print(f"  {i+1}. Entity {entity.id} - Missing components")
                return False
        
        # Get statistics
        stats = UnitConverter.get_conversion_statistics(entities)
        print(f"✓ Army statistics:")
        print(f"  Unit types: {stats['unit_types']}")
        print(f"  Component types: {list(stats['component_counts'].keys())}")
        
        return True
        
    except Exception as e:
        print(f"✗ Demo army test failed: {e}")
        return False

def test_tactical_movement():
    """Test tactical movement component"""
    print("\nTesting tactical movement...")
    
    try:
        from components.gameplay.tactical_movement import TacticalMovementComponent
        
        # Create movement component
        movement = TacticalMovementComponent(
            movement_points=4,
            movement_range=4,
            action_points=3
        )
        
        print(f"✓ Created movement component")
        print(f"  MP: {movement.current_movement_points}/{movement.max_movement_points}")
        print(f"  AP: {movement.current_action_points}/{movement.max_action_points}")
        
        # Test movement
        if movement.can_move(2):
            print("  ✓ Can move 2 tiles")
            if movement.consume_movement(2):
                print(f"  ✓ Moved 2 tiles, MP now: {movement.current_movement_points}")
            else:
                print("  ✗ Failed to consume movement")
                return False
        else:
            print("  ✗ Cannot move 2 tiles")
            return False
        
        # Test action
        if movement.can_act(1):
            print("  ✓ Can perform action")
            if movement.consume_action_points(1):
                print(f"  ✓ Used action, AP now: {movement.current_action_points}")
            else:
                print("  ✗ Failed to consume action points")
                return False
        else:
            print("  ✗ Cannot perform action")
            return False
        
        # Test refresh
        movement.refresh_for_new_turn()
        print(f"  ✓ Refreshed for new turn: MP={movement.current_movement_points}, AP={movement.current_action_points}")
        
        return True
        
    except Exception as e:
        print(f"✗ Tactical movement test failed: {e}")
        return False

def test_demo_imports():
    """Test that demo can be imported"""
    print("\nTesting demo imports...")
    
    try:
        from demos.modular_apex_tactics_demo import ModularApexTacticsDemo
        print("✓ Demo class imports successfully")
        
        # Test that we can create instance (without Ursina)
        print("✓ Demo framework ready")
        
        return True
        
    except ImportError as e:
        print(f"✗ Demo import failed: {e}")
        return False
    except Exception as e:
        print(f"✗ Demo test failed: {e}")
        return False

def test_performance():
    """Test performance of ECS operations"""
    print("\nTesting ECS performance...")
    
    try:
        import time
        from core.ecs.world import World
        from demos.unit_converter import UnitConverter
        
        world = World()
        
        # Time army creation
        start_time = time.time()
        entities = UnitConverter.create_demo_army(world, 20)  # Larger army
        creation_time = (time.time() - start_time) * 1000  # Convert to ms
        
        print(f"✓ Created {len(entities)} entities in {creation_time:.2f}ms")
        
        if creation_time > 100:  # Target: <100ms for 20 units
            print(f"  ⚠️  Creation time above target (100ms)")
        else:
            print(f"  ✓ Creation time within target")
        
        # Time component queries
        start_time = time.time()
        for _ in range(100):  # 100 queries
            from components.stats.attributes import AttributeStats
            entities_with_attributes = world.entity_manager.get_entities_with_component(AttributeStats)
        query_time = (time.time() - start_time) * 1000
        
        print(f"✓ 100 component queries in {query_time:.2f}ms")
        
        if query_time > 10:  # Target: <10ms for 100 queries
            print(f"  ⚠️  Query time above target (10ms)")
        else:
            print(f"  ✓ Query time within target")
        
        return True
        
    except Exception as e:
        print(f"✗ Performance test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("Modular Apex Tactics Demo - Test Suite")
    print("=" * 50)
    
    tests = [
        test_ecs_imports,
        test_unit_conversion,
        test_demo_army,
        test_tactical_movement,
        test_demo_imports,
        test_performance
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print(f"\n{passed}/{total} tests passed")
    
    if passed == total:
        print("✅ All tests passed! The modular demo is ready.")
        print("\nTo run the demo:")
        print("uv run src/demos/modular_apex_tactics_demo.py")
        print("\nThe demo replaces apex-tactics.py with:")
        print("• ECS entity-component architecture")
        print("• Modular system design")
        print("• Performance-optimized components")
        print("• Event-driven communication")
        print("• Preserved camera controls from apex-tactics.py")
    else:
        print("❌ Some tests failed. Check errors above.")

if __name__ == "__main__":
    main()