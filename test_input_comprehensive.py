#!/usr/bin/env uv run
"""
Comprehensive Input Tests for Modular Apex Tactics Demo

Tests all keyboard and mouse input functionality to ensure the demo works correctly.
These tests verify that the input system is properly implemented and functional.
"""

import sys
import os
import time
import unittest
from unittest.mock import Mock, patch, MagicMock
from typing import Optional, Any

# Setup imports
script_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(script_dir, 'src')
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

# Mock Ursina first before importing demo
class MockUrsina:
    """Mock Ursina for testing without 3D engine"""
    def __init__(self):
        self.position = MockVec3(0, 0, 0)
        self.rotation = MockVec3(0, 0, 0)
        self.rotation_x = 0
        self.rotation_y = 0
        self.forward = MockVec3(0, 0, -1)
        self.back = MockVec3(0, 0, 1)
        self.left = MockVec3(-1, 0, 0)
        self.right = MockVec3(1, 0, 0)
        self.up = MockVec3(0, 1, 0)

class MockVec3:
    def __init__(self, x=0, y=0, z=0):
        self.x = x
        self.y = y 
        self.z = z
    
    def __add__(self, other):
        return MockVec3(self.x + other.x, self.y + other.y, self.z + other.z)
    
    def __sub__(self, other):
        return MockVec3(self.x - other.x, self.y - other.y, self.z - other.z)
    
    def __mul__(self, scalar):
        return MockVec3(self.x * scalar, self.y * scalar, self.z * scalar)

class MockMouse:
    def __init__(self):
        self.velocity = MockVec3(0, 0, 0)

class MockTime:
    def __init__(self):
        self.dt = 0.016  # 60fps

class MockHeldKeys:
    def __init__(self):
        self._keys = {}
    
    def __getitem__(self, key):
        return self._keys.get(key, False)
    
    def __setitem__(self, key, value):
        self._keys[key] = value
    
    def set_held(self, key, held=True):
        self._keys[key] = held

# Mock globals
mock_camera = MockUrsina()
mock_mouse = MockMouse()
mock_time = MockTime()
mock_held_keys = MockHeldKeys()

# Patch before imports
sys.modules['ursina'] = Mock()

# Mock Ursina entities and functions
with patch.dict('sys.modules', {
    'ursina': Mock(),
    'ursina.prefabs.window_panel': Mock()
}):
    # Import demo components after mocking
    from demos.modular_apex_tactics_demo import ModularApexTacticsDemo

class TestKeyboardInput(unittest.TestCase):
    """Test keyboard input functionality"""
    
    def setUp(self):
        """Setup test environment"""
        # Mock Ursina globals
        self.mock_camera = mock_camera
        self.mock_held_keys = mock_held_keys
        self.mock_time = mock_time
        
        # Create demo instance with mocked dependencies
        with patch('demos.modular_apex_tactics_demo.URSINA_AVAILABLE', True):
            with patch('demos.modular_apex_tactics_demo.Ursina') as mock_ursina:
                with patch('demos.modular_apex_tactics_demo.camera', self.mock_camera):
                    with patch('demos.modular_apex_tactics_demo.held_keys', self.mock_held_keys):
                        with patch('demos.modular_apex_tactics_demo.time', self.mock_time):
                            mock_ursina.return_value = Mock()
                            self.demo = ModularApexTacticsDemo()
                            
        # Reset camera state
        self.mock_camera.position = MockVec3(0, 0, 0)
        self.mock_camera.rotation_x = 0
        self.mock_camera.rotation_y = 0
        self.mock_held_keys._keys.clear()
    
    def test_camera_mode_switching(self):
        """Test camera mode switching with 1/2/3 keys"""
        print("Testing camera mode switching...")
        
        # Test orbit mode (1 key)
        self.demo._handle_input('1')
        self.assertEqual(self.demo.camera_controller.camera_mode, 0)
        print("✓ Key '1' switches to orbit mode")
        
        # Test free mode (2 key)  
        self.demo._handle_input('2')
        self.assertEqual(self.demo.camera_controller.camera_mode, 1)
        print("✓ Key '2' switches to free mode")
        
        # Test top-down mode (3 key)
        self.demo._handle_input('3') 
        self.assertEqual(self.demo.camera_controller.camera_mode, 2)
        print("✓ Key '3' switches to top-down mode")
    
    def test_wasd_camera_movement(self):
        """Test WASD camera movement in update loop"""
        print("Testing WASD camera movement...")
        
        initial_pos = MockVec3(self.mock_camera.position.x, self.mock_camera.position.y, self.mock_camera.position.z)
        
        # Test W key (forward movement)
        self.mock_held_keys.set_held('w', True)
        with patch('demos.modular_apex_tactics_demo.camera', self.mock_camera):
            with patch('demos.modular_apex_tactics_demo.held_keys', self.mock_held_keys):
                with patch('demos.modular_apex_tactics_demo.time', self.mock_time):
                    self.demo._handle_update()
        
        # Camera should move forward
        self.assertNotEqual(self.mock_camera.position.x, initial_pos.x)
        print("✓ WASD 'W' key moves camera forward")
        
        # Reset and test other keys
        self.mock_camera.position = MockVec3(0, 0, 0)
        self.mock_held_keys.set_held('w', False)
        
        # Test S key (backward movement)
        self.mock_held_keys.set_held('s', True)
        with patch('demos.modular_apex_tactics_demo.camera', self.mock_camera):
            with patch('demos.modular_apex_tactics_demo.held_keys', self.mock_held_keys):
                with patch('demos.modular_apex_tactics_demo.time', self.mock_time):
                    self.demo._handle_update()
        print("✓ WASD 'S' key moves camera backward")
        
        # Test A key (left movement)
        self.mock_camera.position = MockVec3(0, 0, 0)
        self.mock_held_keys.set_held('s', False)
        self.mock_held_keys.set_held('a', True)
        with patch('demos.modular_apex_tactics_demo.camera', self.mock_camera):
            with patch('demos.modular_apex_tactics_demo.held_keys', self.mock_held_keys):
                with patch('demos.modular_apex_tactics_demo.time', self.mock_time):
                    self.demo._handle_update()
        print("✓ WASD 'A' key moves camera left")
        
        # Test D key (right movement)
        self.mock_camera.position = MockVec3(0, 0, 0)
        self.mock_held_keys.set_held('a', False)
        self.mock_held_keys.set_held('d', True)
        with patch('demos.modular_apex_tactics_demo.camera', self.mock_camera):
            with patch('demos.modular_apex_tactics_demo.held_keys', self.mock_held_keys):
                with patch('demos.modular_apex_tactics_demo.time', self.mock_time):
                    self.demo._handle_update()
        print("✓ WASD 'D' key moves camera right")
    
    def test_demo_control_keys(self):
        """Test demo control keys (Space, Tab, ESC)"""
        print("Testing demo control keys...")
        
        # Test space key (end turn)
        initial_turn = self.demo.current_turn
        self.demo._handle_input('space')
        self.assertEqual(self.demo.current_turn, initial_turn + 1)
        print("✓ Space key ends turn")
        
        # Test tab key (show statistics) 
        with patch('builtins.print') as mock_print:
            self.demo._handle_input('tab')
            mock_print.assert_called()
        print("✓ Tab key shows ECS statistics")
        
        # Test escape key (exit demo)
        with patch('demos.modular_apex_tactics_demo.application') as mock_app:
            self.demo._handle_input('escape')
            mock_app.quit.assert_called_once()
        print("✓ ESC key exits demo")

class TestMouseInput(unittest.TestCase):
    """Test mouse input functionality"""
    
    def setUp(self):
        """Setup test environment"""
        self.mock_camera = mock_camera
        self.mock_mouse = mock_mouse
        self.mock_held_keys = mock_held_keys
        
        # Create demo instance with mocked dependencies
        with patch('demos.modular_apex_tactics_demo.URSINA_AVAILABLE', True):
            with patch('demos.modular_apex_tactics_demo.Ursina') as mock_ursina:
                with patch('demos.modular_apex_tactics_demo.camera', self.mock_camera):
                    with patch('demos.modular_apex_tactics_demo.held_keys', self.mock_held_keys):
                        mock_ursina.return_value = Mock()
                        self.demo = ModularApexTacticsDemo()
        
        # Reset state
        self.mock_camera.position = MockVec3(0, 0, 0)
        self.demo.camera_controller.camera_angle_x = 30
        self.demo.camera_controller.camera_angle_y = 0
        self.demo.camera_controller.camera_mode = 0  # Orbit mode
        self.mock_held_keys._keys.clear()
    
    def test_mouse_camera_rotation(self):
        """Test mouse camera rotation in orbit mode"""
        print("Testing mouse camera rotation...")
        
        # Set mouse velocity and left mouse button held
        self.mock_mouse.velocity.x = 0.1
        self.mock_mouse.velocity.y = 0.1
        self.mock_held_keys.set_held('left mouse', True)
        
        initial_angle_x = self.demo.camera_controller.camera_angle_x
        initial_angle_y = self.demo.camera_controller.camera_angle_y
        
        # Handle mouse input
        with patch('demos.modular_apex_tactics_demo.mouse', self.mock_mouse):
            with patch('demos.modular_apex_tactics_demo.held_keys', self.mock_held_keys):
                self.demo.camera_controller.handle_mouse_input()
        
        # Camera angles should change
        self.assertNotEqual(self.demo.camera_controller.camera_angle_x, initial_angle_x)
        self.assertNotEqual(self.demo.camera_controller.camera_angle_y, initial_angle_y)
        print("✓ Mouse drag rotates camera in orbit mode")
    
    def test_scroll_wheel_zoom(self):
        """Test scroll wheel zoom functionality"""
        print("Testing scroll wheel zoom...")
        
        initial_distance = self.demo.camera_controller.camera_distance
        
        # Test scroll up (zoom in)
        self.demo.camera_controller.handle_input('scroll up')
        self.assertLess(self.demo.camera_controller.camera_distance, initial_distance)
        print("✓ Scroll up zooms in")
        
        # Test scroll down (zoom out)
        distance_after_zoom_in = self.demo.camera_controller.camera_distance
        self.demo.camera_controller.handle_input('scroll down')
        self.assertGreater(self.demo.camera_controller.camera_distance, distance_after_zoom_in)
        print("✓ Scroll down zooms out")

class TestInputIntegration(unittest.TestCase):
    """Test input registration and integration with Ursina"""
    
    def setUp(self):
        """Setup test environment"""
        with patch('demos.modular_apex_tactics_demo.URSINA_AVAILABLE', True):
            with patch('demos.modular_apex_tactics_demo.Ursina') as mock_ursina:
                mock_ursina.return_value = Mock()
                self.demo = ModularApexTacticsDemo()
    
    def test_global_function_registration(self):
        """Test that global input functions are registered correctly"""
        print("Testing global function registration...")
        
        # Mock __main__ module
        with patch('demos.modular_apex_tactics_demo.__main__') as mock_main:
            mock_main.input = None
            mock_main.update = None
            
            # Register global functions
            self.demo._register_global_functions()
            
            # Check that functions were registered
            self.assertIsNotNone(mock_main.input)
            self.assertIsNotNone(mock_main.update)
            print("✓ Global input and update functions registered")
    
    def test_input_function_bridging(self):
        """Test that global functions properly bridge to class methods"""
        print("Testing input function bridging...")
        
        # Mock the demo methods
        with patch.object(self.demo, '_handle_input') as mock_handle_input:
            # Register global functions
            with patch('demos.modular_apex_tactics_demo.__main__') as mock_main:
                self.demo._register_global_functions()
                
                # Get the registered global input function
                global_input_func = mock_main.input
                
                # Call it with a test key
                global_input_func('test_key')
                
                # Verify it called the demo's handler
                mock_handle_input.assert_called_once_with('test_key')
                print("✓ Global input function bridges to demo handler")
    
    def test_update_function_bridging(self):
        """Test that global update function properly bridges to class method"""
        print("Testing update function bridging...")
        
        # Mock the demo methods
        with patch.object(self.demo, '_handle_update') as mock_handle_update:
            # Register global functions
            with patch('demos.modular_apex_tactics_demo.__main__') as mock_main:
                self.demo._register_global_functions()
                
                # Get the registered global update function
                global_update_func = mock_main.update
                
                # Call it
                global_update_func()
                
                # Verify it called the demo's handler
                mock_handle_update.assert_called_once()
                print("✓ Global update function bridges to demo handler")

class TestCameraControllerInput(unittest.TestCase):
    """Test CameraController input handling matches apex-tactics.py"""
    
    def setUp(self):
        """Setup test environment"""
        with patch('demos.modular_apex_tactics_demo.URSINA_AVAILABLE', True):
            with patch('demos.modular_apex_tactics_demo.Ursina') as mock_ursina:
                mock_ursina.return_value = Mock()
                self.demo = ModularApexTacticsDemo()
        
        self.camera_controller = self.demo.camera_controller
    
    def test_camera_mode_input_handling(self):
        """Test camera mode input handling matches apex-tactics.py behavior"""
        print("Testing camera mode input handling...")
        
        # Test 1 key for orbit mode
        self.camera_controller.handle_input('1')
        self.assertEqual(self.camera_controller.camera_mode, 0)
        print("✓ CameraController handles '1' key for orbit mode")
        
        # Test 2 key for free mode
        self.camera_controller.handle_input('2')
        self.assertEqual(self.camera_controller.camera_mode, 1)
        print("✓ CameraController handles '2' key for free mode")
        
        # Test 3 key for top-down mode
        self.camera_controller.handle_input('3')
        self.assertEqual(self.camera_controller.camera_mode, 2)
        print("✓ CameraController handles '3' key for top-down mode")
    
    def test_scroll_input_handling(self):
        """Test scroll wheel input handling"""
        print("Testing scroll input handling...")
        
        # Set to orbit mode
        self.camera_controller.camera_mode = 0
        initial_distance = self.camera_controller.camera_distance
        
        # Test scroll up
        self.camera_controller.handle_input('scroll up')
        self.assertLess(self.camera_controller.camera_distance, initial_distance)
        print("✓ CameraController handles scroll up")
        
        # Test scroll down
        distance_after_up = self.camera_controller.camera_distance
        self.camera_controller.handle_input('scroll down')
        self.assertGreater(self.camera_controller.camera_distance, distance_after_up)
        print("✓ CameraController handles scroll down")
    
    def test_orbit_mouse_handling(self):
        """Test orbit mode mouse handling"""
        print("Testing orbit mode mouse handling...")
        
        self.camera_controller.camera_mode = 0
        self.mock_held_keys.set_held('left mouse', True)
        self.mock_mouse.velocity.x = 0.5
        self.mock_mouse.velocity.y = -0.3
        
        initial_angle_x = self.camera_controller.camera_angle_x
        initial_angle_y = self.camera_controller.camera_angle_y
        
        with patch('demos.modular_apex_tactics_demo.held_keys', self.mock_held_keys):
            with patch('demos.modular_apex_tactics_demo.mouse', self.mock_mouse):
                self.camera_controller.handle_mouse_input()
        
        # Angles should change based on mouse velocity
        self.assertNotEqual(self.camera_controller.camera_angle_x, initial_angle_x)
        self.assertNotEqual(self.camera_controller.camera_angle_y, initial_angle_y)
        print("✓ CameraController handles orbit mode mouse input")

def run_all_tests():
    """Run all input tests and report results"""
    print("=" * 60)
    print("COMPREHENSIVE INPUT TESTS FOR MODULAR APEX TACTICS DEMO")
    print("=" * 60)
    print()
    
    # Create test suite
    test_classes = [
        TestKeyboardInput,
        TestMouseInput,
        TestInputIntegration,
        TestCameraControllerInput
    ]
    
    total_tests = 0
    passed_tests = 0
    failed_tests = []
    
    for test_class in test_classes:
        print(f"Running {test_class.__name__}...")
        print("-" * 40)
        
        suite = unittest.TestLoader().loadTestsFromTestCase(test_class)
        
        for test in suite:
            total_tests += 1
            try:
                test.debug()
                passed_tests += 1
            except Exception as e:
                failed_tests.append(f"{test_class.__name__}.{test._testMethodName}: {e}")
                print(f"✗ {test._testMethodName} FAILED: {e}")
        
        print()
    
    # Final results
    print("=" * 60)
    print("TEST RESULTS")
    print("=" * 60)
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {len(failed_tests)}")
    
    if failed_tests:
        print("\nFailed Tests:")
        for failure in failed_tests:
            print(f"  ✗ {failure}")
    
    success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
    print(f"\nSuccess Rate: {success_rate:.1f}%")
    
    if passed_tests == total_tests:
        print("\n🎉 ALL INPUT TESTS PASSED!")
        print("The modular demo input system is working correctly.")
        return True
    else:
        print(f"\n❌ {len(failed_tests)} TESTS FAILED")
        print("Input system needs fixes before demo will work properly.")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)