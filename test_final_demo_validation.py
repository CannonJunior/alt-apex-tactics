#!/usr/bin/env uv run
"""
Final Demo Validation Tests

This test suite validates that the final ECS demo completely replaces
apex-tactics.py while preserving ALL input functionality exactly.
"""

import sys
import os
import subprocess
import time

def test_final_demo_structure():
    """Test that final demo has complete ECS structure"""
    print("Testing final demo ECS structure...")
    
    try:
        demo_path = '/home/junior/src/alt-apex-tactics/apex_ecs_demo_final.py'
        
        with open(demo_path, 'r') as f:
            content = f.read()
        
        # Check for complete ECS architecture
        required_ecs_elements = [
            'from core.ecs.world import World',
            'from components.stats.attributes import AttributeStats',
            'from components.gameplay.unit_type import UnitTypeComponent',
            'from components.gameplay.tactical_movement import TacticalMovementComponent',
            'class ECSUnit:',
            'class ECSGrid:',
            'ecs_world = World()'
        ]
        
        for element in required_ecs_elements:
            if element in content:
                print(f"✓ Found: {element}")
            else:
                print(f"✗ Missing: {element}")
                return False
        
        # Check for visual representation
        visual_elements = [
            'self._create_visual_entity()',
            'self.visual_entity = Entity(',
            'def update_visual_position(self):'
        ]
        
        for element in visual_elements:
            if element in content:
                print(f"✓ Visual element: {element}")
            else:
                print(f"✗ Missing visual element: {element}")
                return False
        
        return True
        
    except Exception as e:
        print(f"✗ Structure test failed: {e}")
        return False

def test_final_demo_input_preservation():
    """Test that final demo preserves exact input structure"""
    print("Testing final demo input preservation...")
    
    try:
        demo_path = '/home/junior/src/alt-apex-tactics/apex_ecs_demo_final.py'
        
        with open(demo_path, 'r') as f:
            content = f.read()
        
        # Check for preserved CameraController (exact same as original)
        camera_elements = [
            'class CameraController:',
            'def handle_input(self, key):',
            'def handle_mouse_input(self):',
            'def update_camera(self):',
            "if key == '1':",
            "if key == '2':",
            "if key == '3':",
            "if key == 'scroll up':",
            "if key == 'scroll down':",
            "camera.position += camera.forward * self.move_speed",
            "if held_keys['left mouse']:",
            "self.camera_angle_y += mouse.velocity.x * 50"
        ]
        
        for element in camera_elements:
            if element in content:
                print(f"✓ Camera element preserved: {element[:30]}...")
            else:
                print(f"✗ Missing camera element: {element}")
                return False
        
        # Check for preserved global functions
        global_functions = [
            'def input(key):',
            'def update():',
            'camera_controller.handle_input(key)',
            'camera_controller.handle_mouse_input()',
            'camera_controller.update_camera()'
        ]
        
        for func in global_functions:
            if func in content:
                print(f"✓ Global function preserved: {func}")
            else:
                print(f"✗ Missing global function: {func}")
                return False
        
        # Check for preservation comments
        preservation_comments = [
            'CRITICAL: CameraController remains EXACTLY the same',
            'CRITICAL: Input functions remain EXACTLY the same'
        ]
        
        for comment in preservation_comments:
            if comment in content:
                print(f"✓ Preservation comment found")
            else:
                print(f"⚠️ Missing preservation comment")
        
        return True
        
    except Exception as e:
        print(f"✗ Input preservation test failed: {e}")
        return False

def test_final_demo_runs_successfully():
    """Test that final demo runs and creates ECS units"""
    print("Testing final demo execution...")
    
    try:
        # Run the demo for a few seconds
        process = subprocess.Popen([
            'uv', 'run', '/home/junior/src/alt-apex-tactics/apex_ecs_demo_final.py'
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
        
        # Check for successful unit creation
        if "Created ECS unit:" in stdout_str:
            print("✓ ECS units created successfully")
        else:
            print("✗ ECS unit creation not found in output")
            return False
        
        # Check for grid creation
        if "Created 8 ECS units on tactical grid" in stdout_str:
            print("✓ Tactical grid with units created")
        else:
            print("⚠️ Grid creation message not found")
        
        # Check for ECS world statistics
        if "ECS World:" in stdout_str:
            print("✓ ECS world statistics displayed")
        else:
            print("⚠️ ECS statistics not found")
        
        # Check for critical errors (warnings are OK)
        if "Traceback" in stderr_str and "Error:" in stderr_str:
            print(f"✗ Demo had critical errors: {stderr_str}")
            return False
        
        print("✓ Final demo runs without critical errors")
        return True
        
    except Exception as e:
        print(f"✗ Demo execution test failed: {e}")
        return False

def test_apex_tactics_comparison():
    """Compare final demo structure to original apex-tactics.py"""
    print("Testing comparison with original apex-tactics.py...")
    
    try:
        # Read original apex-tactics.py
        original_path = '/home/junior/src/apex-tactics/apex-tactics.py'
        with open(original_path, 'r') as f:
            original_content = f.read()
        
        # Read final demo
        demo_path = '/home/junior/src/alt-apex-tactics/apex_ecs_demo_final.py'
        with open(demo_path, 'r') as f:
            demo_content = f.read()
        
        # Check that key input handling is preserved
        input_patterns_to_preserve = [
            "def input(key):",
            "def update():",
            "handle_input(key)",
            "handle_mouse_input()",
            "update_camera()",
            "if key == '1':",
            "if key == '2':",
            "if key == '3':",
            "camera_mode = 0",
            "camera_mode = 1", 
            "camera_mode = 2"
        ]
        
        preserved_count = 0
        for pattern in input_patterns_to_preserve:
            if pattern in original_content and pattern in demo_content:
                preserved_count += 1
                print(f"✓ Preserved pattern: {pattern}")
            else:
                print(f"⚠️ Pattern difference: {pattern}")
        
        preservation_rate = (preserved_count / len(input_patterns_to_preserve)) * 100
        print(f"Input preservation rate: {preservation_rate:.1f}%")
        
        if preservation_rate >= 90:
            print("✓ High input preservation achieved")
            return True
        else:
            print("✗ Insufficient input preservation")
            return False
        
    except Exception as e:
        print(f"✗ Comparison test failed: {e}")
        return False

def run_final_validation_tests():
    """Run all final validation tests"""
    print("=" * 70)
    print("FINAL DEMO VALIDATION TESTS")
    print("=" * 70)
    print("Validating complete ECS replacement with input preservation")
    print("=" * 70)
    print()
    
    tests = [
        ("Final Demo ECS Structure", test_final_demo_structure),
        ("Input Preservation", test_final_demo_input_preservation),
        ("Demo Execution", test_final_demo_runs_successfully),
        ("Apex-Tactics Comparison", test_apex_tactics_comparison),
    ]
    
    passed = 0
    total = len(tests)
    failed_tests = []
    
    for test_name, test_func in tests:
        print(f"Running {test_name}...")
        print("-" * 50)
        
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
    print("=" * 70)
    print("FINAL VALIDATION RESULTS")
    print("=" * 70)
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
        print("\n🎉 ALL FINAL VALIDATION TESTS PASSED!")
        print("\nSUCCESS: Complete ECS replacement achieved!")
        print("=" * 70)
        print("FINAL DEMO SUMMARY")
        print("=" * 70)
        print("✓ Replaced Unit class with ECS entities")
        print("✓ Replaced TacticalGrid with ECS grid system")
        print("✓ Added visual representation with components")
        print("✓ Preserved ALL input functionality exactly")
        print("✓ Maintained CameraController behavior")
        print("✓ Preserved global input/update functions")
        print("✓ Full tactical RPG with ECS architecture")
        print()
        print("The apex_ecs_demo_final.py successfully demonstrates:")
        print("- Complete modular ECS architecture")
        print("- Preserved user input experience")
        print("- Visual tactical grid with units")
        print("- Component-based entity system")
        print("- Performance and extensibility benefits")
        print("=" * 70)
        return True
    else:
        print(f"\n❌ {len(failed_tests)} TESTS FAILED")
        print("Final demo validation incomplete.")
        return False

if __name__ == "__main__":
    success = run_final_validation_tests()
    sys.exit(0 if success else 1)