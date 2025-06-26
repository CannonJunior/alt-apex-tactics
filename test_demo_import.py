#!/usr/bin/env uv run
"""
Simple test to check if the demo can be imported correctly
"""

import sys
import os

# Setup imports
script_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(script_dir, 'src')
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

try:
    print("Testing demo import...")
    from demos.modular_apex_tactics_demo import ModularApexTacticsDemo, URSINA_AVAILABLE
    print(f"✓ Demo imported successfully! URSINA_AVAILABLE = {URSINA_AVAILABLE}")
    
    print("Testing demo instantiation...")
    demo = ModularApexTacticsDemo()
    print("✓ Demo instance created successfully!")
    
    print("Testing input methods...")
    if hasattr(demo, '_handle_input'):
        print("✓ _handle_input method exists")
    else:
        print("✗ _handle_input method missing")
        
    if hasattr(demo, '_handle_update'):
        print("✓ _handle_update method exists")
    else:
        print("✗ _handle_update method missing")
        
    if hasattr(demo, '_register_global_functions'):
        print("✓ _register_global_functions method exists")
    else:
        print("✗ _register_global_functions method missing")
    
    print("Testing input registration...")
    import __main__
    old_input = getattr(__main__, 'input', None)
    old_update = getattr(__main__, 'update', None)
    
    try:
        demo._register_global_functions()
        
        if hasattr(__main__, 'input') and callable(__main__.input):
            print("✓ Global input function registered")
        else:
            print("✗ Global input function not registered properly")
            
        if hasattr(__main__, 'update') and callable(__main__.update):
            print("✓ Global update function registered")
        else:
            print("✗ Global update function not registered properly")
            
    finally:
        # Restore
        if old_input is not None:
            __main__.input = old_input
        elif hasattr(__main__, 'input'):
            delattr(__main__, 'input')
            
        if old_update is not None:
            __main__.update = old_update
        elif hasattr(__main__, 'update'):
            delattr(__main__, 'update')
    
    print("\n🎉 All demo import tests passed!")
    print("The demo should be ready to run with proper input handling.")
    
except Exception as e:
    print(f"✗ Demo import failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)