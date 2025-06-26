#!/usr/bin/env uv run
"""
Live Input Test for Modular Apex Tactics Demo

This test actually runs the demo briefly and tests if input functions are properly registered
and functional. It checks the real integration with Ursina.
"""

import sys
import os
import time
import threading
from typing import Optional

# Setup imports
script_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(script_dir, 'src')
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

def test_demo_import():
    """Test that the demo can be imported without errors"""
    print("Testing demo import...")
    try:
        from demos.modular_apex_tactics_demo import ModularApexTacticsDemo, URSINA_AVAILABLE
        print("✓ Demo imports successfully")
        return True, URSINA_AVAILABLE
    except Exception as e:
        print(f"✗ Demo import failed: {e}")
        import traceback
        traceback.print_exc()
        return False, False

def test_input_function_registration():
    """Test that input functions can be registered"""
    print("Testing input function registration...")
    
    try:
        from demos.modular_apex_tactics_demo import ModularApexTacticsDemo, URSINA_AVAILABLE
        
        if not URSINA_AVAILABLE:
            print("⚠️ Ursina not available - cannot test input registration")
            return False
        
        # Create demo instance
        demo = ModularApexTacticsDemo()
        
        # Test that the registration method exists
        if not hasattr(demo, '_register_global_functions'):
            print("✗ Demo missing _register_global_functions method")
            return False
        
        # Test that input handlers exist
        if not hasattr(demo, '_handle_input'):
            print("✗ Demo missing _handle_input method") 
            return False
            
        if not hasattr(demo, '_handle_update'):
            print("✗ Demo missing _handle_update method")
            return False
            
        print("✓ All input methods exist")
        
        # Test registration without actually starting Ursina
        import __main__
        original_input = getattr(__main__, 'input', None)
        original_update = getattr(__main__, 'update', None)
        
        try:
            demo._register_global_functions()
            
            # Check that functions were registered
            if not hasattr(__main__, 'input'):
                print("✗ Global input function not registered")
                return False
                
            if not hasattr(__main__, 'update'):
                print("✗ Global update function not registered")
                return False
                
            print("✓ Global functions registered successfully")
            
            # Test that registered functions are callable
            if not callable(__main__.input):
                print("✗ Registered input function is not callable")
                return False
                
            if not callable(__main__.update):
                print("✗ Registered update function is not callable")
                return False
                
            print("✓ Registered functions are callable")
            
            return True
            
        finally:
            # Restore original functions
            if original_input is not None:
                __main__.input = original_input
            elif hasattr(__main__, 'input'):
                delattr(__main__, 'input')
                
            if original_update is not None:
                __main__.update = original_update
            elif hasattr(__main__, 'update'):
                delattr(__main__, 'update')
        
    except Exception as e:
        print(f"✗ Input registration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_camera_controller_integration():
    """Test camera controller integration"""
    print("Testing camera controller integration...")
    
    try:
        from demos.modular_apex_tactics_demo import ModularApexTacticsDemo, URSINA_AVAILABLE
        
        if not URSINA_AVAILABLE:
            print("⚠️ Ursina not available - cannot test camera controller")
            return False
        
        demo = ModularApexTacticsDemo()
        
        # Test that camera controller exists
        if not hasattr(demo, 'camera_controller'):
            print("✗ Demo missing camera_controller")
            return False
            
        camera_controller = demo.camera_controller
        
        # Test camera controller methods
        if not hasattr(camera_controller, 'handle_input'):
            print("✗ CameraController missing handle_input method")
            return False
            
        if not hasattr(camera_controller, 'update_camera'):
            print("✗ CameraController missing update_camera method")
            return False
            
        if not hasattr(camera_controller, 'handle_mouse_input'):
            print("✗ CameraController missing handle_mouse_input method")
            return False
            
        print("✓ Camera controller has all required methods")
        
        # Test initial state
        if not hasattr(camera_controller, 'camera_mode'):
            print("✗ CameraController missing camera_mode")
            return False
            
        print(f"✓ Camera controller initialized with mode: {camera_controller.camera_mode}")
        
        # Test mode switching
        initial_mode = camera_controller.camera_mode
        camera_controller.handle_input('1')
        if camera_controller.camera_mode != 0:
            print("✗ Camera mode switching failed")
            return False
            
        print("✓ Camera mode switching works")
        
        return True
        
    except Exception as e:
        print(f"✗ Camera controller test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_input_handler_methods():
    """Test that input handler methods work correctly"""
    print("Testing input handler methods...")
    
    try:
        from demos.modular_apex_tactics_demo import ModularApexTacticsDemo, URSINA_AVAILABLE
        
        if not URSINA_AVAILABLE:
            print("⚠️ Ursina not available - cannot test input handlers")
            return False
        
        demo = ModularApexTacticsDemo()
        
        # Test keyboard input handling
        initial_turn = demo.current_turn
        demo._handle_input('space')
        if demo.current_turn != initial_turn + 1:
            print("✗ Space key input handling failed")
            return False
        print("✓ Space key input handling works")
        
        # Test camera mode input handling
        demo._handle_input('1')
        if demo.camera_controller.camera_mode != 0:
            print("✗ Camera mode input handling failed")
            return False
        print("✓ Camera mode input handling works")
        
        # Test update handler (should not crash)
        try:
            demo._handle_update()
            print("✓ Update handler executes without error")
        except Exception as e:
            print(f"✗ Update handler failed: {e}")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ Input handler test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_global_function_bridging():
    """Test that global functions properly bridge to demo methods"""
    print("Testing global function bridging...")
    
    try:
        from demos.modular_apex_tactics_demo import ModularApexTacticsDemo, URSINA_AVAILABLE
        
        if not URSINA_AVAILABLE:
            print("⚠️ Ursina not available - cannot test function bridging")
            return False
        
        demo = ModularApexTacticsDemo()
        
        import __main__
        original_input = getattr(__main__, 'input', None)
        original_update = getattr(__main__, 'update', None)
        
        try:
            # Register global functions
            demo._register_global_functions()
            
            # Test input bridging
            initial_turn = demo.current_turn
            __main__.input('space')  # Should trigger end turn
            if demo.current_turn != initial_turn + 1:
                print("✗ Global input function bridging failed")
                return False
            print("✓ Global input function bridges correctly")
            
            # Test update bridging (should not crash)
            try:
                __main__.update()
                print("✓ Global update function bridges correctly")
            except Exception as e:
                print(f"✗ Global update function bridging failed: {e}")
                return False
            
            return True
            
        finally:
            # Restore original functions
            if original_input is not None:
                __main__.input = original_input
            elif hasattr(__main__, 'input'):
                delattr(__main__, 'input')
                
            if original_update is not None:
                __main__.update = original_update
            elif hasattr(__main__, 'update'):
                delattr(__main__, 'update')
        
    except Exception as e:
        print(f"✗ Global function bridging test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def run_live_input_tests():
    """Run all live input tests"""
    print("=" * 60)
    print("LIVE INPUT TESTS FOR MODULAR APEX TACTICS DEMO")
    print("=" * 60)
    print()
    
    tests = [
        ("Demo Import", test_demo_import),
        ("Input Function Registration", test_input_function_registration),
        ("Camera Controller Integration", test_camera_controller_integration),
        ("Input Handler Methods", test_input_handler_methods),
        ("Global Function Bridging", test_global_function_bridging)
    ]
    
    passed = 0
    total = len(tests)
    failed_tests = []
    
    for test_name, test_func in tests:
        print(f"Running {test_name}...")
        print("-" * 40)
        
        try:
            result = test_func()
            if result and isinstance(result, tuple):
                # Handle demo import which returns (success, ursina_available)
                result = result[0]
            
            if result:
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
    print("LIVE TEST RESULTS")
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
        print("\n🎉 ALL LIVE INPUT TESTS PASSED!")
        print("The input system appears to be working correctly.")
        print("\nRecommendation: Input fix should be considered IMPLEMENTED")
        return True
    else:
        print(f"\n❌ {len(failed_tests)} LIVE TESTS FAILED")
        print("Input system has issues that need to be resolved.")
        print("\nRecommendation: Input fix is NOT properly implemented")
        return False

if __name__ == "__main__":
    success = run_live_input_tests()
    
    if success:
        print("\n" + "=" * 60)
        print("NEXT STEPS")
        print("=" * 60)
        print("All input tests passed. You can now:")
        print("1. Run the demo with: uv run run_modular_demo.py")
        print("2. Test these inputs in the live demo:")
        print("   - WASD for camera movement")  
        print("   - Mouse drag for camera rotation")
        print("   - 1/2/3 for camera modes")
        print("   - Space for end turn")
        print("   - Tab for statistics")
        print("   - ESC to exit")
    else:
        print("\n" + "=" * 60)
        print("ISSUES FOUND")
        print("=" * 60)
        print("Input tests failed. The demo may not respond to keyboard/mouse input.")
        print("Review the failed tests above and fix the issues before running the demo.")
    
    sys.exit(0 if success else 1)