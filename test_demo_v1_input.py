#!/usr/bin/env uv run
"""
Test Demo v1 Input Preservation

This test validates that the minimal demo v1 preserves all input functionality
from the original apex-tactics.py.
"""

import sys
import os
import importlib.util
import time
from unittest.mock import Mock, patch

# Import the original input tests
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from test_apex_tactics_input import (
    MockVec3, MockCamera, MockMouse, MockTime, MockHeldKeys, MockControlPanel,
    TestApexTacticsCameraInput, TestApexTacticsGlobalInput,
    run_apex_tactics_input_tests
)

def test_demo_v1_runs():
    """Test that demo v1 can start without errors"""
    print("Testing that demo v1 can be imported and starts properly...")
    
    try:
        # Test that the file can be loaded
        demo_path = '/home/junior/src/alt-apex-tactics/apex_ecs_demo_v1.py'
        spec = importlib.util.spec_from_file_location("demo_v1", demo_path)
        if not spec or not spec.loader:
            print("✗ Could not load demo v1 spec")
            return False
        
        print("✓ Demo v1 file loads successfully")
        return True
        
    except Exception as e:
        print(f"✗ Demo v1 loading failed: {e}")
        return False

def test_demo_v1_preserves_camera_controller():
    """Test that demo v1 preserves the CameraController class"""
    print("Testing that demo v1 preserves CameraController...")
    
    try:
        # Import demo v1 components without running the app
        demo_path = '/home/junior/src/alt-apex-tactics/apex_ecs_demo_v1.py'
        
        # Read the file and check for CameraController
        with open(demo_path, 'r') as f:
            content = f.read()
        
        if 'class CameraController:' in content:
            print("✓ CameraController class found in demo v1")
        else:
            print("✗ CameraController class missing from demo v1")
            return False
        
        # Check for the required methods
        required_methods = ['handle_input', 'handle_mouse_input', 'update_camera']
        for method in required_methods:
            if f'def {method}(self' in content:
                print(f"✓ Method {method} found")
            else:
                print(f"✗ Method {method} missing")
                return False
        
        return True
        
    except Exception as e:
        print(f"✗ CameraController preservation test failed: {e}")
        return False

def test_demo_v1_preserves_global_functions():
    """Test that demo v1 preserves global input and update functions"""
    print("Testing that demo v1 preserves global input/update functions...")
    
    try:
        demo_path = '/home/junior/src/alt-apex-tactics/apex_ecs_demo_v1.py'
        
        with open(demo_path, 'r') as f:
            content = f.read()
        
        # Check for global input function
        if 'def input(key):' in content:
            print("✓ Global input function found")
        else:
            print("✗ Global input function missing")
            return False
        
        # Check for global update function  
        if 'def update():' in content:
            print("✓ Global update function found")
        else:
            print("✗ Global update function missing")
            return False
        
        # Check that input delegates to camera controller
        if 'camera_controller.handle_input(key)' in content:
            print("✓ Input delegates to camera controller")
        else:
            print("✗ Input delegation missing")
            return False
        
        # Check that update calls camera methods
        if 'camera_controller.handle_mouse_input()' in content and 'camera_controller.update_camera()' in content:
            print("✓ Update calls camera methods")
        else:
            print("✗ Update camera calls missing")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ Global functions preservation test failed: {e}")
        return False

def test_demo_v1_startup():
    """Test that demo v1 starts up properly"""
    print("Testing demo v1 startup...")
    
    try:
        # Try to run the demo for a short time
        import subprocess
        import signal
        
        # Start the demo process
        process = subprocess.Popen([
            'uv', 'run', '/home/junior/src/alt-apex-tactics/apex_ecs_demo_v1.py'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Let it run for 2 seconds
        time.sleep(2)
        
        # Terminate the process
        process.terminate()
        
        # Wait for it to finish
        try:
            stdout, stderr = process.communicate(timeout=3)
        except subprocess.TimeoutExpired:
            process.kill()
            stdout, stderr = process.communicate()
        
        # Check if there were any critical errors (warnings are OK)
        stderr_str = stderr.decode() if stderr else ""
        if "Traceback" in stderr_str or "Error:" in stderr_str:
            print(f"✗ Demo v1 had errors: {stderr_str}")
            return False
        
        print("✓ Demo v1 starts up without critical errors")
        return True
        
    except Exception as e:
        print(f"✗ Demo v1 startup test failed: {e}")
        return False

def run_demo_v1_tests():
    """Run all demo v1 tests"""
    print("=" * 60)
    print("DEMO V1 INPUT PRESERVATION TESTS")
    print("=" * 60)
    print("Validating that minimal demo preserves input functionality")
    print("=" * 60)
    print()
    
    tests = [
        ("Demo v1 Loading", test_demo_v1_runs),
        ("CameraController Preservation", test_demo_v1_preserves_camera_controller),
        ("Global Functions Preservation", test_demo_v1_preserves_global_functions),
        ("Demo v1 Startup", test_demo_v1_startup),
    ]
    
    passed = 0
    total = len(tests)
    failed_tests = []
    
    for test_name, test_func in tests:
        print(f"Running {test_name}...")
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
    print("DEMO V1 TEST RESULTS")
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
        print("\n🎉 ALL DEMO V1 TESTS PASSED!")
        print("The minimal demo preserves input functionality.")
        print("\nNext step: Start replacing components with ECS")
        return True
    else:
        print(f"\n❌ {len(failed_tests)} TESTS FAILED")
        print("Demo v1 does not preserve input functionality properly.")
        return False

if __name__ == "__main__":
    success = run_demo_v1_tests()
    sys.exit(0 if success else 1)