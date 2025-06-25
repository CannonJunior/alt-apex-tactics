#!/usr/bin/env uv run
"""
Test script for practice battle integration
"""

import sys
import os

# Add project root to path
project_root = os.path.abspath(os.path.dirname(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

def test_imports():
    """Test that all imports work correctly"""
    print("Testing imports...")
    
    try:
        from src.ui.screens.practice_battle import PracticeBattle, Unit, UnitType, BattleGrid, CameraController
        print("✓ Practice battle imports successful")
    except ImportError as e:
        print(f"✗ Practice battle import failed: {e}")
        return False
    
    try:
        from src.ui.screens.start_screen_demo import StartScreenDemo
        print("✓ Start screen demo imports successful")
    except ImportError as e:
        print(f"✗ Start screen demo import failed: {e}")
        return False
    
    return True

def test_unit_creation():
    """Test unit creation and stats"""
    print("\nTesting unit creation...")
    
    try:
        from src.ui.screens.practice_battle import Unit, UnitType
        
        # Create a test unit
        unit = Unit("Test Hero", UnitType.HEROMANCER, 2, 3)
        
        print(f"✓ Created unit: {unit.name}")
        print(f"  Type: {unit.type.value}")
        print(f"  Position: ({unit.x}, {unit.y})")
        print(f"  HP: {unit.hp}/{unit.max_hp}")
        print(f"  Physical Attack: {unit.physical_attack}")
        print(f"  Physical Defense: {unit.physical_defense}")
        
        return True
    except Exception as e:
        print(f"✗ Unit creation failed: {e}")
        return False

def test_battle_grid():
    """Test battle grid functionality"""
    print("\nTesting battle grid...")
    
    try:
        from src.ui.screens.practice_battle import BattleGrid, Unit, UnitType
        
        # Create grid and unit
        grid = BattleGrid(8, 8)
        unit = Unit("Grid Test", UnitType.MAGI, 0, 0)
        
        # Test placement
        success = grid.place_unit(unit, 3, 3)
        print(f"✓ Unit placement: {success}")
        
        # Test retrieval
        retrieved = grid.get_unit_at(3, 3)
        print(f"✓ Unit retrieval: {retrieved.name if retrieved else 'None'}")
        
        # Test movement
        grid.place_unit(unit, 5, 5)
        print(f"✓ Unit moved to: ({unit.x}, {unit.y})")
        
        return True
    except Exception as e:
        print(f"✗ Battle grid test failed: {e}")
        return False

def test_camera_controller():
    """Test camera controller"""
    print("\nTesting camera controller...")
    
    try:
        from src.ui.screens.practice_battle import CameraController
        
        # Create camera controller
        camera = CameraController(8, 8)
        
        print(f"✓ Camera created with target: {camera.camera_target}")
        print(f"  Distance: {camera.camera_distance}")
        print(f"  Mode: {camera.camera_mode}")
        
        # Test mode switching
        camera.camera_mode = 2  # Top-down
        print(f"✓ Camera mode switched to: {camera.camera_mode}")
        
        return True
    except Exception as e:
        print(f"✗ Camera controller test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("Practice Battle Integration Test")
    print("=" * 40)
    
    tests = [
        test_imports,
        test_unit_creation, 
        test_battle_grid,
        test_camera_controller
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print(f"\n{passed}/{total} tests passed")
    
    if passed == total:
        print("✓ All tests passed! Practice battle integration is working.")
        print("\nTo run the demo:")
        print("uv run src/ui/screens/start_screen_demo.py")
        print("Then click 'PRACTICE BATTLE' button")
    else:
        print("✗ Some tests failed. Check the errors above.")

if __name__ == "__main__":
    main()