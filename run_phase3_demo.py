#!/usr/bin/env python3
"""
Phase 3 AI Demo Runner

Simple script to run the Phase 3 AI Integration demonstration.
"""

import os
import sys

def main():
    """Run the Phase 3 AI demo"""
    # Get the directory containing this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Path to the demo
    demo_path = os.path.join(script_dir, 'demos', 'phase3_ai_demo.py')
    
    if not os.path.exists(demo_path):
        print(f"Error: Demo file not found at {demo_path}")
        return 1
    
    print("Starting Phase 3 AI Integration Demo...")
    print("=" * 50)
    
    # Import and run the demo
    sys.path.insert(0, script_dir)
    
    try:
        from demos.phase3_ai_demo import main as demo_main
        demo_main()
        return 0
    except ImportError as e:
        print(f"Import error: {e}")
        print("Make sure all dependencies are properly installed.")
        return 1
    except Exception as e:
        print(f"Demo error: {e}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)