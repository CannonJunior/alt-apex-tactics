#!/usr/bin/env python3
"""
Phase 4 Visual Systems Demo Runner

Script to run the Phase 4 visual systems demonstration with Ursina.
"""

import os
import sys

def main():
    """Run the Phase 4 visual demo"""
    # Get the directory containing this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Path to the demo
    demo_path = os.path.join(script_dir, 'demos', 'phase4_visual_demo.py')
    
    if not os.path.exists(demo_path):
        print(f"Error: Demo file not found at {demo_path}")
        return 1
    
    print("Starting Phase 4 Visual Systems Demo...")
    print("=" * 50)
    print("This demo requires Ursina. Make sure it's installed:")
    print("  pip install ursina")
    print()
    
    # Import and run the demo
    sys.path.insert(0, script_dir)
    
    try:
        from demos.phase4_visual_demo import main as demo_main
        demo_main()
        return 0
    except ImportError as e:
        if "ursina" in str(e).lower():
            print("Ursina is not installed. Please install it:")
            print("  pip install ursina")
            print("  # or")
            print("  uv add ursina")
        else:
            print(f"Import error: {e}")
            print("Make sure all dependencies are properly installed.")
        return 1
    except Exception as e:
        print(f"Demo error: {e}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)