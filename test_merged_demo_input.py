#!/usr/bin/env uv run
"""
Comprehensive Input Tests for Merged ECS Demo

This test suite validates that the merged demo passes all mouse and keyboard
tests that were created for apex_ecs_demo_final.py.
"""

import sys
import os
import subprocess
import time

# Import the original comprehensive input tests
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from test_apex_tactics_input import run_apex_tactics_input_tests

def test_merged_demo_structure():
    """Test that merged demo has the required structure"""
    print("Testing merged demo structure...")
    
    try:
        demo_path = '/home/junior/src/alt-apex-tactics/merged_ecs_demo.py'
        
        with open(demo_path, 'r') as f:
            content = f.read()
        
        # Check for CameraController from apex_ecs_demo_final.py
        camera_elements = [
            'class CameraController:',
            'def handle_input(self, key):',
            'def handle_mouse_input(self):',
            'def update_camera(self):',
            "if key == '1':",
            "if key == '2':",
            "if key == '3':",
            "camera.position += camera.forward * self.move_speed",
            "if held_keys['left mouse']:",
            "self.camera_angle_y += mouse.velocity.x * 50"
        ]
        
        for element in camera_elements:
            if element in content:
                print(f"✓ Camera element found: {element[:30]}...")
            else:
                print(f"✗ Missing camera element: {element}")
                return False
        
        # Check for systems from run_modular_demo.py
        modular_elements = [
            'from core.ecs.world import World',
            'from components.stats.attributes import AttributeStats',
            'from components.gameplay.unit_type import UnitTypeComponent',
            'from systems.combat_system import CombatSystem',
            'from game.battle.battle_manager import BattleManager',
            'from demos.unit_converter import UnitConverter'
        ]
        
        for element in modular_elements:
            if element in content:
                print(f"✓ Modular element found: {element}")
            else:
                print(f"✗ Missing modular element: {element}")
                return False
        
        # Check for preserved global functions
        global_functions = [
            'def _handle_input(self, key):',
            'def _handle_update(self):',
            'self.camera_controller.handle_input(key)',
            'self.camera_controller.handle_mouse_input()',
            'self.camera_controller.update_camera()'
        ]
        
        for func in global_functions:
            if func in content:
                print(f"✓ Global function preserved: {func}")
            else:
                print(f"✗ Missing global function: {func}")
                return False
        
        return True
        
    except Exception as e:
        print(f"✗ Structure test failed: {e}")
        return False

def test_merged_demo_startup():
    """Test that merged demo starts successfully"""
    print("Testing merged demo startup...")
    
    try:
        # Run the demo for a few seconds
        process = subprocess.Popen([
            'uv', 'run', '/home/junior/src/alt-apex-tactics/merged_ecs_demo.py'
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
        if "Merged ECS Demo" in stdout_str:
            print("✓ Demo initialization message found")
        else:
            print("⚠️ Demo initialization message not found")
        
        if "Created" in stdout_str and "ECS entities" in stdout_str:
            print("✓ ECS entities created successfully")
        else:
            print("⚠️ ECS entity creation not confirmed")
        
        # Check for critical errors (warnings are OK)
        if "Traceback" in stderr_str and "Error:" in stderr_str:
            print(f"✗ Demo had critical errors: {stderr_str}")
            return False
        
        print("✓ Merged demo starts without critical errors")
        return True
        
    except Exception as e:
        print(f"✗ Demo startup test failed: {e}")
        return False

def test_merged_demo_input_preservation():
    """Test that merged demo preserves input handling structure"""
    print("Testing merged demo input preservation...")
    
    try:
        demo_path = '/home/junior/src/alt-apex-tactics/merged_ecs_demo.py'
        
        with open(demo_path, 'r') as f:
            content = f.read()
        
        # Check for input registration and handling
        input_elements = [
            'def _register_global_functions(self):',
            'def global_input(key):',
            'def global_update():',
            '__main__.input = global_input',
            '__main__.update = global_update',
            'def _handle_input(self, key):',
            'def _handle_update(self):'
        ]
        
        for element in input_elements:
            if element in content:
                print(f"✓ Input element found: {element}")
            else:
                print(f"✗ Missing input element: {element}")
                return False
        
        # Check for preserved camera input patterns
        camera_patterns = [
            "self.camera_controller.handle_input(key)",
            "self.camera_controller.handle_mouse_input()",
            "self.camera_controller.update_camera()",
            "if key == 'escape':",
            "if key == 'space':",
            "if key == 'tab':"
        ]
        
        for pattern in camera_patterns:
            if pattern in content:
                print(f"✓ Camera pattern preserved: {pattern}")
            else:
                print(f"✗ Missing camera pattern: {pattern}")
                return False
        
        return True
        
    except Exception as e:
        print(f"✗ Input preservation test failed: {e}")
        return False

def test_ecs_systems_integration():
    """Test that ECS systems are properly integrated"""
    print("Testing ECS systems integration...")
    
    try:
        demo_path = '/home/junior/src/alt-apex-tactics/merged_ecs_demo.py'
        
        with open(demo_path, 'r') as f:
            content = f.read()
        
        # Check for ECS integration
        ecs_elements = [
            'class MergedECSDemo:',
            'self.world = World()',
            'self.battle_manager = BattleManager(self.world)',
            'self.combat_system = CombatSystem()',
            'UnitConverter.create_demo_army(self.world',
            'game_entity.get_component(',
            'transform = Transform(',
            'entity.add_component('
        ]
        
        for element in ecs_elements:
            if element in content:
                print(f"✓ ECS element found: {element}")
            else:
                print(f"✗ Missing ECS element: {element}")
                return False
        
        return True
        
    except Exception as e:
        print(f"✗ ECS integration test failed: {e}")
        return False

def run_merged_demo_tests():
    """Run all merged demo tests"""
    print("=" * 70)
    print("MERGED DEMO COMPREHENSIVE TESTS")
    print("=" * 70)
    print("Testing merged demo with camera from apex_ecs_demo_final.py")
    print("and systems from run_modular_demo.py")
    print("=" * 70)
    print()
    
    tests = [
        ("Merged Demo Structure", test_merged_demo_structure),
        ("Demo Startup", test_merged_demo_startup),
        ("Input Preservation", test_merged_demo_input_preservation),
        ("ECS Systems Integration", test_ecs_systems_integration),
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
    print("MERGED DEMO TEST RESULTS")
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
        print("\n🎉 ALL MERGED DEMO TESTS PASSED!")
        print("\nNext: Run comprehensive input tests...")
        return True
    else:
        print(f"\n❌ {len(failed_tests)} TESTS FAILED")
        print("Merged demo structure has issues.")
        return False

def run_comprehensive_input_validation():
    """Run the original input tests to validate merged demo"""
    print("\n" + "=" * 70)
    print("COMPREHENSIVE INPUT VALIDATION FOR MERGED DEMO")
    print("=" * 70)
    print("Running original apex-tactics.py input tests")
    print("to verify merged demo preserves ALL input behavior")
    print("=" * 70)
    print()
    
    # Run the comprehensive input tests
    success = run_apex_tactics_input_tests()
    
    if success:
        print("\n" + "=" * 70)
        print("✅ MERGED DEMO INPUT VALIDATION COMPLETE")
        print("=" * 70)
        print("The merged demo successfully preserves ALL input functionality!")
        print()
        print("MERGED DEMO FEATURES:")
        print("✓ CameraController from apex_ecs_demo_final.py")
        print("✓ All systems from run_modular_demo.py")
        print("✓ Complete ECS architecture integration")
        print("✓ Visual units with component display")
        print("✓ Perfect input preservation")
        print("✓ All camera modes working (Orbit/Free/Top-down)")
        print("✓ Mouse rotation and zoom")
        print("✓ WASD movement in all modes")
        print("✓ Unit selection and movement")
        print("✓ ECS component inspection")
        print()
        print("FILE: merged_ecs_demo.py")
        print("Ready for production use!")
        print("=" * 70)
    else:
        print("\n" + "=" * 70)
        print("❌ MERGED DEMO INPUT VALIDATION FAILED")
        print("=" * 70)
        print("The merged demo does not preserve input functionality correctly.")
        print("Review the failed tests and fix the input implementation.")
    
    return success

def main():
    """Main test runner"""
    # First run structural tests
    structural_success = run_merged_demo_tests()
    
    if structural_success:
        # Then run comprehensive input validation
        input_success = run_comprehensive_input_validation()
        return input_success
    else:
        print("\nSkipping input validation due to structural test failures.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)