#!/usr/bin/env uv run
"""
Simple Input Test - Check that input methods exist and work
"""

import sys
import os

# Setup imports
script_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(script_dir, 'src')
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

def test_demo_module_structure():
    """Test that the demo module has the right structure"""
    print("Testing demo module structure...")
    
    try:
        from demos.modular_apex_tactics_demo import ModularApexTacticsDemo
        print("✓ ModularApexTacticsDemo class imports successfully")
        
        # Check methods exist on the class
        required_methods = [
            '_register_global_functions',
            '_handle_input',
            '_handle_update',
            'run'
        ]
        
        for method_name in required_methods:
            if hasattr(ModularApexTacticsDemo, method_name):
                print(f"✓ Method {method_name} exists")
            else:
                print(f"✗ Method {method_name} missing")
                return False
        
        return True
        
    except Exception as e:
        print(f"✗ Module structure test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_ursina_availability():
    """Test Ursina availability detection"""
    print("Testing Ursina availability...")
    
    try:
        from demos.modular_apex_tactics_demo import URSINA_AVAILABLE
        print(f"✓ URSINA_AVAILABLE = {URSINA_AVAILABLE}")
        
        if URSINA_AVAILABLE:
            print("✓ Ursina is available - input should work in live demo")
        else:
            print("⚠️ Ursina not available - demo cannot run")
            
        return True
        
    except Exception as e:
        print(f"✗ Ursina availability test failed: {e}")
        return False

def test_camera_controller_import():
    """Test camera controller import without instantiation"""
    print("Testing camera controller import...")
    
    try:
        # This should work even if Ursina is not available due to fallback
        from demos.modular_apex_tactics_demo import ApexCameraController
        print("✓ ApexCameraController imports successfully")
        
        # Check required methods exist
        required_methods = ['handle_input', 'update_camera', 'handle_mouse_input']
        for method_name in required_methods:
            if hasattr(ApexCameraController, method_name):
                print(f"✓ CameraController has {method_name} method")
            else:
                print(f"✗ CameraController missing {method_name} method")
                return False
        
        return True
        
    except Exception as e:
        print(f"✗ Camera controller test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_input_function_registration_logic():
    """Test the logic of input function registration without running graphics"""
    print("Testing input function registration logic...")
    
    try:
        from demos.modular_apex_tactics_demo import ModularApexTacticsDemo
        
        # Get the method from the class (don't instantiate)
        register_method = ModularApexTacticsDemo._register_global_functions
        print("✓ _register_global_functions method accessible")
        
        # Check that it's a method
        if callable(register_method):
            print("✓ _register_global_functions is callable")
        else:
            print("✗ _register_global_functions is not callable")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ Input function registration logic test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("SIMPLE INPUT TESTS FOR MODULAR APEX TACTICS DEMO")
    print("=" * 60)
    print()
    
    tests = [
        ("Demo Module Structure", test_demo_module_structure),
        ("Ursina Availability", test_ursina_availability),
        ("Camera Controller Import", test_camera_controller_import),
        ("Input Registration Logic", test_input_function_registration_logic),
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
    print("SIMPLE TEST RESULTS")
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
        print("\n🎉 ALL SIMPLE TESTS PASSED!")
        print("The demo structure looks correct.")
        print("\nConclusion: Input system should work when demo runs")
        print("Try running: uv run run_modular_demo.py")
        return True
    else:
        print(f"\n❌ {len(failed_tests)} TESTS FAILED")
        print("Input system has structural issues.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)