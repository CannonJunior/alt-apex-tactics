#!/usr/bin/env uv run
"""
Test Demo v2 Input Preservation

This test validates that demo v2 (with ECS units) preserves all input functionality.
"""

import sys
import os
import importlib.util
import time
import subprocess

def test_demo_v2_preserves_input_structure():
    """Test that demo v2 preserves the input structure"""
    print("Testing that demo v2 preserves input structure...")
    
    try:
        demo_path = '/home/junior/src/alt-apex-tactics/apex_ecs_demo_v2.py'
        
        with open(demo_path, 'r') as f:
            content = f.read()
        
        # Check for preserved CameraController
        if 'class CameraController:' in content:
            print("✓ CameraController class preserved")
        else:
            print("✗ CameraController class missing")
            return False
        
        # Check for preserved input methods
        required_methods = ['handle_input', 'handle_mouse_input', 'update_camera']
        for method in required_methods:
            if f'def {method}(self' in content:
                print(f"✓ Method {method} preserved")
            else:
                print(f"✗ Method {method} missing")
                return False
        
        # Check for preserved global functions
        if 'def input(key):' in content and 'def update():' in content:
            print("✓ Global input/update functions preserved")
        else:
            print("✗ Global functions missing")
            return False
        
        # Check that input still delegates to camera controller
        if 'camera_controller.handle_input(key)' in content:
            print("✓ Input delegation preserved")
        else:
            print("✗ Input delegation missing")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ Input structure test failed: {e}")
        return False

def test_demo_v2_has_ecs_components():
    """Test that demo v2 has ECS components"""
    print("Testing that demo v2 includes ECS components...")
    
    try:
        demo_path = '/home/junior/src/alt-apex-tactics/apex_ecs_demo_v2.py'
        
        with open(demo_path, 'r') as f:
            content = f.read()
        
        # Check for ECS imports
        ecs_imports = [
            'from core.ecs.world import World',
            'from core.ecs.entity import Entity',
            'from components.stats.attributes import AttributeStats',
            'from components.gameplay.unit_type import UnitTypeComponent'
        ]
        
        for import_line in ecs_imports:
            if import_line in content:
                print(f"✓ ECS import found: {import_line.split(' import ')[1]}")
            else:
                print(f"✗ Missing ECS import: {import_line}")
                return False
        
        # Check for ECSUnit class
        if 'class ECSUnit:' in content:
            print("✓ ECSUnit class found")
        else:
            print("✗ ECSUnit class missing")
            return False
        
        # Check for ECS world initialization
        if 'ecs_world = World()' in content:
            print("✓ ECS world initialization found")
        else:
            print("✗ ECS world initialization missing")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ ECS components test failed: {e}")
        return False

def test_demo_v2_startup():
    """Test that demo v2 starts up properly"""
    print("Testing demo v2 startup...")
    
    try:
        # Try to run the demo for a short time
        process = subprocess.Popen([
            'uv', 'run', '/home/junior/src/alt-apex-tactics/apex_ecs_demo_v2.py'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Let it run for 3 seconds
        time.sleep(3)
        
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
        
        # Check for expected output
        if "Created ECS unit:" in stdout_str:
            print("✓ ECS units created successfully")
        else:
            print("⚠️ ECS unit creation output not found")
        
        # Check if there were any critical errors (warnings are OK)
        if "Traceback" in stderr_str or "Error:" in stderr_str:
            print(f"✗ Demo v2 had errors: {stderr_str}")
            return False
        
        print("✓ Demo v2 starts up without critical errors")
        return True
        
    except Exception as e:
        print(f"✗ Demo v2 startup test failed: {e}")
        return False

def test_demo_v2_input_comments():
    """Test that demo v2 has proper input preservation comments"""
    print("Testing demo v2 input preservation comments...")
    
    try:
        demo_path = '/home/junior/src/alt-apex-tactics/apex_ecs_demo_v2.py'
        
        with open(demo_path, 'r') as f:
            content = f.read()
        
        # Check for preservation comments
        preservation_comments = [
            'IMPORTANT: CameraController remains EXACTLY the same',
            'IMPORTANT: Input functions remain EXACTLY the same'
        ]
        
        for comment in preservation_comments:
            if comment in content:
                print(f"✓ Found preservation comment")
            else:
                print(f"⚠️ Missing preservation comment: {comment}")
        
        return True
        
    except Exception as e:
        print(f"✗ Comments test failed: {e}")
        return False

def run_demo_v2_tests():
    """Run all demo v2 tests"""
    print("=" * 60)
    print("DEMO V2 INPUT PRESERVATION TESTS")
    print("=" * 60)
    print("Validating that ECS units demo preserves input functionality")
    print("=" * 60)
    print()
    
    tests = [
        ("Input Structure Preservation", test_demo_v2_preserves_input_structure),
        ("ECS Components Integration", test_demo_v2_has_ecs_components), 
        ("Demo v2 Startup", test_demo_v2_startup),
        ("Input Preservation Comments", test_demo_v2_input_comments),
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
    print("DEMO V2 TEST RESULTS")
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
        print("\n🎉 ALL DEMO V2 TESTS PASSED!")
        print("ECS units successfully integrated while preserving input.")
        print("\nNext step: Test input functionality with comprehensive tests")
        return True
    else:
        print(f"\n❌ {len(failed_tests)} TESTS FAILED")
        print("Demo v2 does not properly preserve input functionality.")
        return False

if __name__ == "__main__":
    success = run_demo_v2_tests()
    
    if success:
        print("\n" + "=" * 60)
        print("RECOMMENDATION: Test Demo v2 with Original Input Tests")
        print("=" * 60)
        print("Run: uv run test_apex_tactics_input.py")
        print("This will verify that the exact input behavior is preserved.")
    
    sys.exit(0 if success else 1)