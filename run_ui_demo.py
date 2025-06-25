#!/usr/bin/env uv run
"""
UI Demo Runner

Simple script to run the Phase 4.5 UI demonstration.
Can be executed directly with uv from the project root.

Usage: uv run run_ui_demo.py
"""

import sys
import os

def main():
    """Run the UI demo"""
    print("Phase 4.5 UI Framework Demo")
    print("=" * 40)
    
    # Import and run the demo
    try:
        from src.ui.screens.start_screen_demo import run_demo
        run_demo()
    except ImportError as e:
        print(f"Import error: {e}")
        print("\nMake sure you have the required dependencies:")
        print("uv add ursina")
        print("\nAnd that you're running from the project root directory.")
        return 1
    except Exception as e:
        print(f"Error running demo: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())