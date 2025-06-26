#!/usr/bin/env uv run
"""
Launcher for Modular Apex Tactics Demo

Ensures proper import paths and launches the ECS-based tactical RPG demo.
"""

import sys
import os

def setup_imports():
    """Setup proper import paths"""
    # Get the directory containing this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Add src directory to Python path
    src_dir = os.path.join(script_dir, 'src')
    if src_dir not in sys.path:
        sys.path.insert(0, src_dir)
    
    # Add apex-tactics directory for camera controller
    apex_dir = '/home/junior/src/apex-tactics'
    if apex_dir not in sys.path:
        sys.path.insert(0, apex_dir)
    
    print(f"Added to Python path:")
    print(f"  - {src_dir}")
    print(f"  - {apex_dir}")

def main():
    """Main launcher"""
    print("Modular Apex Tactics Demo Launcher")
    print("=" * 40)
    
    # Setup imports
    setup_imports()
    
    # Test imports first
    try:
        print("Testing imports...")
        from core.ecs.world import World
        from core.ecs.entity import Entity
        from components.stats.attributes import AttributeStats
        from demos.unit_converter import UnitConverter
        print("✓ All imports successful")
    except ImportError as e:
        print(f"✗ Import failed: {e}")
        print("Cannot run demo without proper imports")
        return False
    
    # Check for Ursina
    try:
        import ursina
        print("✓ Ursina available")
    except ImportError:
        print("✗ Ursina not available")
        print("Install with: uv add ursina")
        return False
    
    # Launch the demo
    try:
        print("\nStarting Modular Apex Tactics Demo...")
        from demos.modular_apex_tactics_demo import ModularApexTacticsDemo
        
        demo = ModularApexTacticsDemo()
        demo.run()
        
    except Exception as e:
        print(f"Demo failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)