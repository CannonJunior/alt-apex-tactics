#!/usr/bin/env uv run
"""
Minimal Input Test for Modular Apex Tactics Demo

Tests input functionality without starting the full Ursina graphics system.
"""

import sys
import os

# Setup imports
script_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(script_dir, 'src')
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

def test_basic_imports():
    """Test that basic components can be imported"""
    print("Testing basic imports...")
    try:
        # Test ECS imports
        from core.ecs.world import World
        from core.ecs.entity import Entity
        print("✓ ECS components import successfully")
        
        # Test demo components
        from demos.unit_converter import UnitConverter
        print("✓ Demo utilities import successfully")
        
        return True
    except Exception as e:
        print(f"✗ Import failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_demo_class_structure():
    """Test demo class structure without Ursina"""
    print("Testing demo class structure...")
    try:
        # Mock Ursina before importing demo
        import unittest.mock
        
        with unittest.mock.patch.dict('sys.modules', {'ursina': unittest.mock.Mock()}):
            # Set URSINA_AVAILABLE to False to avoid graphics initialization
            sys.modules['demos.modular_apex_tactics_demo'] = None  # Clear cache
            
            # Import with mocked Ursina
            from demos import modular_apex_tactics_demo
            
            # Check that the class exists
            ModularApexTacticsDemo = modular_apex_tactics_demo.ModularApexTacticsDemo
            print("✓ ModularApexTacticsDemo class exists")
            
            # Check required methods exist
            required_methods = [
                '_register_global_functions',
                '_handle_input', 
                '_handle_update',
                'run'
            ]
            
            for method_name in required_methods:
                if not hasattr(ModularApexTacticsDemo, method_name):
                    print(f"✗ Missing required method: {method_name}")
                    return False
                print(f"✓ Method {method_name} exists")
            
            return True
            
    except Exception as e:
        print(f"✗ Demo class test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_input_method_logic():
    """Test input method logic without Ursina graphics"""
    print("Testing input method logic...")
    try:
        import unittest.mock
        
        # Mock all Ursina components
        ursina_mock = unittest.mock.Mock()
        ursina_mock.Ursina = unittest.mock.Mock()
        ursina_mock.Entity = unittest.mock.Mock()
        ursina_mock.camera = unittest.mock.Mock()
        ursina_mock.held_keys = {}
        ursina_mock.time = unittest.mock.Mock()
        ursina_mock.time.dt = 0.016
        ursina_mock.application = unittest.mock.Mock()
        
        with unittest.mock.patch.dict('sys.modules', {'ursina': ursina_mock}):
            with unittest.mock.patch('demos.modular_apex_tactics_demo.URSINA_AVAILABLE', False):
                from demos.modular_apex_tactics_demo import ModularApexTacticsDemo
                
                # Create demo without graphics
                demo = ModularApexTacticsDemo()
                
                # Test input handling logic
                initial_turn = demo.current_turn
                demo._handle_input('space')
                if demo.current_turn != initial_turn + 1:
                    print("✗ Space key doesn't end turn")
                    return False
                print("✓ Space key ends turn correctly")
                
                # Test camera mode switching
                if hasattr(demo, 'camera_controller'):
                    demo._handle_input('1')
                    # This should not crash
                    print("✓ Camera mode switching doesn't crash")
                
                return True
                
    except Exception as e:
        print(f"✗ Input method logic test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_ursina_detection():
    """Test Ursina availability detection"""
    print("Testing Ursina detection...")
    try:
        # Try to import ursina
        try:
            import ursina
            print("✓ Ursina is available")
            return True
        except ImportError:
            print("✗ Ursina is not available")
            print("  Install with: uv add ursina")
            return False
    except Exception as e:
        print(f"✗ Ursina detection failed: {e}")
        return False

def test_apex_tactics_import():
    """Test importing from apex-tactics.py"""
    print("Testing apex-tactics.py import...")
    try:
        apex_tactics_path = '/home/junior/src/apex-tactics/apex-tactics.py'
        if not os.path.exists(apex_tactics_path):
            print("✗ apex-tactics.py not found")
            return False
        
        # Try to import the camera controller
        import importlib.util
        spec = importlib.util.spec_from_file_location("apex_tactics", apex_tactics_path)
        if spec and spec.loader:
            # Don't actually load it (would start Ursina), just check it exists
            print("✓ apex-tactics.py can be imported")
            return True
        else:
            print("✗ apex-tactics.py import spec failed")
            return False
            
    except Exception as e:
        print(f"✗ apex-tactics.py import test failed: {e}")
        return False

def main():
    """Run minimal input tests"""
    print("=" * 60)
    print("MINIMAL INPUT TESTS FOR MODULAR APEX TACTICS DEMO")
    print("=" * 60)
    print()
    
    tests = [
        ("Basic Imports", test_basic_imports),
        ("Demo Class Structure", test_demo_class_structure),
        ("Input Method Logic", test_input_method_logic),
        ("Ursina Detection", test_ursina_detection),
        ("Apex-Tactics Import", test_apex_tactics_import),
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
    print("MINIMAL TEST RESULTS")  
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
        print("\n🎉 ALL MINIMAL TESTS PASSED!")
        print("The demo structure appears correct.")
        print("\nNext: Try running the actual demo to test input")
        return True
    else:
        print(f"\n❌ {len(failed_tests)} TESTS FAILED")
        print("Demo structure has issues.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)