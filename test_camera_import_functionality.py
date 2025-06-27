#!/usr/bin/env python3
"""
Comprehensive tests for the imported CameraController functionality

Validates that the standalone CameraController maintains all original behavior
"""

import sys
import os

# Import the CameraController
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from camera_controller import CameraController

def test_camera_controller_import():
    """Test that CameraController can be imported and initialized"""
    print("Testing CameraController import and initialization...")
    
    try:
        # Test basic initialization
        camera_controller = CameraController()
        print("✓ CameraController imported and initialized successfully")
        
        # Test with parameters
        camera_controller = CameraController(grid_width=10, grid_height=8)
        print("✓ CameraController initialized with custom grid size")
        
        # Test with control panel
        camera_controller = CameraController(grid_width=8, grid_height=8, control_panel=None)
        print("✓ CameraController initialized with optional control panel")
        
        return True
        
    except Exception as e:
        print(f"✗ CameraController import failed: {e}")
        return False

def test_camera_controller_attributes():
    """Test that CameraController has all required attributes"""
    print("Testing CameraController attributes...")
    
    try:
        camera_controller = CameraController()
        
        # Check required attributes
        required_attrs = [
            'grid_center', 'camera_target', 'camera_distance', 
            'camera_angle_x', 'camera_angle_y', 'camera_mode',
            'move_speed', 'rotation_speed', 'control_panel'
        ]
        
        for attr in required_attrs:
            if hasattr(camera_controller, attr):
                print(f"✓ Attribute found: {attr}")
            else:
                print(f"✗ Missing attribute: {attr}")
                return False
        
        # Test default values
        assert camera_controller.camera_mode == 0, "Default camera mode should be 0"
        assert camera_controller.camera_distance == 8, "Default camera distance should be 8"
        assert camera_controller.move_speed == 0.5, "Default move speed should be 0.5"
        
        print("✓ All attributes present with correct default values")
        return True
        
    except Exception as e:
        print(f"✗ Attribute test failed: {e}")
        return False

def test_camera_controller_methods():
    """Test that CameraController has all required methods"""
    print("Testing CameraController methods...")
    
    try:
        camera_controller = CameraController()
        
        # Check required methods
        required_methods = [
            'update_camera', 'handle_input', 'handle_mouse_input',
            'get_mode_name', 'set_mode', 'reset_to_default'
        ]
        
        for method in required_methods:
            if hasattr(camera_controller, method) and callable(getattr(camera_controller, method)):
                print(f"✓ Method found: {method}")
            else:
                print(f"✗ Missing method: {method}")
                return False
        
        # Test method calls (without Ursina app running)
        mode_name = camera_controller.get_mode_name()
        assert mode_name == "Orbit", f"Default mode name should be 'Orbit', got '{mode_name}'"
        
        camera_controller.set_mode(1)
        assert camera_controller.camera_mode == 1, "set_mode should change camera_mode"
        
        camera_controller.reset_to_default()
        assert camera_controller.camera_mode == 0, "reset_to_default should set mode to 0"
        
        print("✓ All methods present and functional")
        return True
        
    except Exception as e:
        print(f"✗ Method test failed: {e}")
        return False

def test_camera_mode_switching():
    """Test camera mode switching functionality"""
    print("Testing camera mode switching...")
    
    try:
        camera_controller = CameraController()
        
        # Test mode switching via handle_input
        test_cases = [
            ('1', 0, "Orbit"),
            ('2', 1, "Free"), 
            ('3', 2, "Top-down")
        ]
        
        for key, expected_mode, expected_name in test_cases:
            camera_controller.handle_input(key)
            
            if camera_controller.camera_mode == expected_mode:
                print(f"✓ Key '{key}' switches to mode {expected_mode} ({expected_name})")
            else:
                print(f"✗ Key '{key}' failed: expected mode {expected_mode}, got {camera_controller.camera_mode}")
                return False
            
            if camera_controller.get_mode_name() == expected_name:
                print(f"✓ Mode name correct: {expected_name}")
            else:
                print(f"✗ Mode name incorrect: expected {expected_name}, got {camera_controller.get_mode_name()}")
                return False
        
        print("✓ Camera mode switching works correctly")
        return True
        
    except Exception as e:
        print(f"✗ Mode switching test failed: {e}")
        return False

def test_input_handling():
    """Test that input handling works without errors"""
    print("Testing input handling...")
    
    try:
        camera_controller = CameraController()
        
        # Test various input keys (without Ursina running, just check no exceptions)
        test_inputs = [
            '1', '2', '3',  # Mode switching
            'w', 's', 'a', 'd', 'q', 'e',  # Movement
            'scroll up', 'scroll down',  # Zoom
            'left arrow', 'right arrow', 'up arrow', 'down arrow',  # Arrow keys
            'unknown_key'  # Should not cause errors
        ]
        
        for key in test_inputs:
            try:
                camera_controller.handle_input(key)
                print(f"✓ Input '{key}' handled without error")
            except Exception as e:
                print(f"✗ Input '{key}' caused error: {e}")
                return False
        
        print("✓ All input handling works without errors")
        return True
        
    except Exception as e:
        print(f"✗ Input handling test failed: {e}")
        return False

def run_all_tests():
    """Run all CameraController tests"""
    print("=" * 60)
    print("TESTING IMPORTED CAMERA CONTROLLER")
    print("=" * 60)
    print()
    
    tests = [
        ("Import and Initialization", test_camera_controller_import),
        ("Attributes", test_camera_controller_attributes),
        ("Methods", test_camera_controller_methods),
        ("Mode Switching", test_camera_mode_switching),
        ("Input Handling", test_input_handling)
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
    print("CAMERA CONTROLLER TEST RESULTS")
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
        print("\n🎉 ALL CAMERA CONTROLLER TESTS PASSED!")
        print("\nThe imported CameraController works correctly!")
        print("✓ Can be imported as a standalone component")
        print("✓ All attributes and methods present")
        print("✓ Camera mode switching functional")
        print("✓ Input handling preserved")
        print("✓ No runtime errors")
        print("\nReady for use in modular demos!")
        return True
    else:
        print(f"\n❌ {len(failed_tests)} TESTS FAILED")
        print("CameraController has issues that need to be fixed.")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)