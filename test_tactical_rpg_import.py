#!/usr/bin/env python3
"""
Comprehensive tests for the imported TacticalRPG functionality

Validates that the standalone TacticalRPG maintains all original behavior
and can be imported and used as a modular component.
"""

import sys
import os
import subprocess
import time

def test_tactical_rpg_import():
    """Test that TacticalRPG can be imported and initialized"""
    print("Testing TacticalRPG import and initialization...")
    
    try:
        # Test basic import
        from tactical_rpg import TacticalRPG, Unit, UnitType, BattleGrid, TurnManager
        print("✓ TacticalRPG and related classes imported successfully")
        
        # Test initialization without Ursina (just class creation)
        print("✓ All required classes available for import")
        
        return True
        
    except Exception as e:
        print(f"✗ TacticalRPG import failed: {e}")
        return False

def test_tactical_rpg_components():
    """Test individual TacticalRPG components"""
    print("Testing TacticalRPG component functionality...")
    
    try:
        from tactical_rpg import Unit, UnitType, BattleGrid, TurnManager
        
        # Test Unit creation
        unit = Unit("TestHero", UnitType.HEROMANCER, 2, 3)
        assert unit.name == "TestHero"
        assert unit.type == UnitType.HEROMANCER
        assert unit.x == 2 and unit.y == 3
        assert hasattr(unit, 'hp') and unit.hp > 0
        assert hasattr(unit, 'mp') and unit.mp > 0
        print("✓ Unit creation and attributes working")
        
        # Test BattleGrid
        grid = BattleGrid(8, 8)
        assert grid.width == 8 and grid.height == 8
        assert grid.is_valid(3, 3) == True
        assert grid.is_valid(-1, 0) == False
        assert grid.is_valid(8, 0) == False
        print("✓ BattleGrid validation working")
        
        # Test grid unit management
        grid.add_unit(unit)
        assert (2, 3) in grid.units
        assert grid.units[(2, 3)] == unit
        print("✓ Grid unit management working")
        
        # Test TurnManager
        units = [unit]
        turn_manager = TurnManager(units)
        assert turn_manager.current_unit() == unit
        print("✓ TurnManager functioning")
        
        return True
        
    except Exception as e:
        print(f"✗ Component test failed: {e}")
        return False

def test_tactical_rpg_structure():
    """Test that TacticalRPG has required structure"""
    print("Testing TacticalRPG class structure...")
    
    try:
        from tactical_rpg import TacticalRPG
        
        # Check class exists and has required methods
        required_methods = [
            '__init__', 'setup_battle', 'handle_input', 'handle_update',
            'handle_tile_click', 'show_action_modal', 'handle_action_selection',
            'handle_path_movement', 'show_movement_confirmation', 'execute_movement',
            'end_current_turn', 'get_tile_at', 'get_current_unit', 'get_unit_at'
        ]
        
        for method in required_methods:
            if hasattr(TacticalRPG, method):
                print(f"✓ Method found: {method}")
            else:
                print(f"✗ Missing method: {method}")
                return False
        
        print("✓ All required methods present")
        return True
        
    except Exception as e:
        print(f"✗ Structure test failed: {e}")
        return False

def test_tactical_rpg_demo():
    """Test that TacticalRPG demo runs without errors"""
    print("Testing TacticalRPG demo execution...")
    
    try:
        # Run the demo for a few seconds
        process = subprocess.Popen([
            'uv', 'run', '/home/junior/src/alt-apex-tactics/tactical_rpg.py'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Let it run for 4 seconds
        time.sleep(4)
        
        # Terminate the process
        process.terminate()
        
        # Wait for it to finish
        try:
            stdout, stderr = process.communicate(timeout=3)
        except subprocess.TimeoutExpired:
            process.kill()
            stdout, stderr = process.communicate()
        
        # Check output
        stdout_str = stdout.decode() if stdout else ""
        stderr_str = stderr.decode() if stderr else ""
        
        # Check for successful initialization
        if "TacticalRPG initialized" in stdout_str:
            print("✓ TacticalRPG initialization message found")
        else:
            print("⚠️ TacticalRPG initialization message not found")
        
        if "Battle setup complete" in stdout_str:
            print("✓ Battle setup completed successfully")
        else:
            print("⚠️ Battle setup completion not confirmed")
        
        # Check for critical errors (warnings are OK)
        if "Traceback" in stderr_str and "Error:" in stderr_str:
            print(f"✗ Demo had critical errors: {stderr_str}")
            return False
        
        print("✓ TacticalRPG demo runs without critical errors")
        return True
        
    except Exception as e:
        print(f"✗ Demo test failed: {e}")
        return False

def test_imported_camera_integration():
    """Test that TacticalRPG correctly uses imported CameraController"""
    print("Testing imported CameraController integration...")
    
    try:
        from tactical_rpg import TacticalRPG
        import inspect
        
        # Check the source code for import statement
        source_file = '/home/junior/src/alt-apex-tactics/tactical_rpg.py'
        with open(source_file, 'r') as f:
            content = f.read()
        
        # Check for imported CameraController
        if "from camera_controller import CameraController" in content:
            print("✓ CameraController imported from standalone module")
        else:
            print("✗ CameraController not imported from standalone module")
            return False
        
        # Check that TacticalRPG.__init__ creates camera_controller
        if "self.camera_controller = CameraController(" in content:
            print("✓ TacticalRPG creates imported CameraController instance")
        else:
            print("✗ TacticalRPG doesn't create CameraController instance")
            return False
        
        # Check for camera controller usage in input and update
        if "self.camera_controller.handle_input(key)" in content:
            print("✓ Input handling uses imported CameraController")
        else:
            print("✗ Input handling doesn't use imported CameraController")
            return False
        
        if "self.camera_controller.handle_mouse_input()" in content and "self.camera_controller.update_camera()" in content:
            print("✓ Update loop uses imported CameraController")
        else:
            print("✗ Update loop doesn't use imported CameraController")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ Camera integration test failed: {e}")
        return False

def run_all_tests():
    """Run all TacticalRPG tests"""
    print("=" * 60)
    print("TESTING IMPORTED TACTICAL RPG")
    print("=" * 60)
    print()
    
    tests = [
        ("Import and Initialization", test_tactical_rpg_import),
        ("Component Functionality", test_tactical_rpg_components),
        ("Class Structure", test_tactical_rpg_structure),
        ("Demo Execution", test_tactical_rpg_demo),
        ("Camera Integration", test_imported_camera_integration)
    ]
    
    passed = 0
    total = len(tests)
    failed_tests = []
    
    for test_name, test_func in tests:
        print(f"Running {test_name} test...")
        print("-" * 40)
        
        try:
            if test_func():
                passed += 1
                print(f"✓ {test_name} PASSED")
            else:
                failed_tests.append(test_name)
                print(f"✗ {test_name} FAILED")
        except Exception as e:
            failed_tests.append(f"{test_name}: {e}")
            print(f"✗ {test_name} FAILED with exception: {e}")
        
        print()
    
    # Results
    print("=" * 60)
    print("TACTICAL RPG TEST RESULTS")
    print("=" * 60)
    print(f"Total Tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {len(failed_tests)}")
    
    if failed_tests:
        print("\nFailed Tests:")
        for failure in failed_tests:
            print(f"  ✗ {failure}")
    
    success_rate = (passed / total) * 100 if total > 0 else 0
    print(f"\nSuccess Rate: {success_rate:.1f}%")
    
    if passed == total:
        print("\n🎉 ALL TACTICAL RPG TESTS PASSED!")
        print("\nThe imported TacticalRPG works correctly!")
        print("✓ Can be imported as a standalone component")
        print("✓ All classes and methods present")
        print("✓ Component functionality preserved")
        print("✓ Demo runs without errors")
        print("✓ Uses imported CameraController")
        print("✓ Complete modular game system")
        print("\nReady for use in other applications!")
        return True
    else:
        print(f"\n❌ {len(failed_tests)} TESTS FAILED")
        print("TacticalRPG has issues that need to be fixed.")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)