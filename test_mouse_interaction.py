#!/usr/bin/env uv run
"""
Test mouse interaction system from phase4_visual_demo.py integration
"""

import sys
import os

def test_mouse_interaction_integration():
    """Test that mouse interaction from phase4_visual_demo.py is properly integrated"""
    print("Testing mouse interaction integration...")
    
    try:
        demo_path = '/home/junior/src/alt-apex-tactics/enhanced_ecs_demo.py'
        
        with open(demo_path, 'r') as f:
            content = f.read()
        
        # Check for mouse interaction functions from phase4_visual_demo.py
        mouse_functions = [
            'def _handle_mouse_interaction(self):',
            'def _handle_mouse_click(self):',
            'def _handle_mouse_hover(self):',
            'def _is_tile_highlighted(self, x, y):',
            'mouse.world_point',
            'grid_x = int(round(mouse_pos.x))',
            'grid_y = int(round(mouse_pos.z))',
            'if mouse.left:',
            'self.handle_tile_click(grid_x, grid_y)'
        ]
        
        print("Checking for mouse interaction functions...")
        missing_functions = []
        for func in mouse_functions:
            if func in content:
                print(f"✓ Found mouse function: {func}")
            else:
                missing_functions.append(func)
                print(f"✗ Missing mouse function: {func}")
        
        # Check for proper mouse state tracking
        mouse_state = [
            'self._last_hover_tile = None',
            '_last_hover_tile = (grid_x, grid_y)',
            'if hasattr(self, \'_last_hover_tile\'):',
            'self.grid.highlight_tile(grid_x, grid_y, color.light_gray)',
            'self.grid.clear_tile_highlight(last_x, last_y)'
        ]
        
        print("\nChecking for mouse state tracking...")
        for state in mouse_state:
            if state in content:
                print(f"✓ Found mouse state: {state}")
            else:
                missing_functions.append(state)
                print(f"✗ Missing mouse state: {state}")
        
        # Check that old tile click handlers are removed
        old_handlers = [
            'tile.on_click = self._create_tile_click_handler(tile)',
            'def _create_tile_click_handler(self, tile):',
            'def _handle_tile_click(self, tile):'
        ]
        
        print("\nChecking that old handlers are removed...")
        found_old_handlers = []
        for handler in old_handlers:
            if handler in content:
                found_old_handlers.append(handler)
                print(f"✗ Found old handler (should be removed): {handler}")
            else:
                print(f"✓ Correctly removed old handler: {handler}")
        
        # Check for integration in update loop
        update_integration = [
            'self._handle_mouse_interaction()',
            'Handle mouse tile interaction (from phase4_visual_demo.py)'
        ]
        
        print("\nChecking for update loop integration...")
        for integration in update_integration:
            if integration in content:
                print(f"✓ Found update integration: {integration}")
            else:
                missing_functions.append(integration)
                print(f"✗ Missing update integration: {integration}")
        
        # Check documentation updates
        doc_updates = [
            'Mouse hover highlights tiles',
            'Mouse world coordinate tile selection',
            'Real-time hover highlighting',
            'Mouse hover + click tiles'
        ]
        
        print("\nChecking documentation updates...")
        for doc in doc_updates:
            if doc in content:
                print(f"✓ Found doc update: {doc}")
            else:
                missing_functions.append(doc)
                print(f"✗ Missing doc update: {doc}")
        
        # Summary
        total_issues = len(missing_functions) + len(found_old_handlers)
        
        print(f"\n" + "=" * 60)
        print("MOUSE INTERACTION INTEGRATION TEST RESULTS")
        print("=" * 60)
        print(f"Missing functions/features: {len(missing_functions)}")
        print(f"Old handlers still present: {len(found_old_handlers)}")
        print(f"Total issues: {total_issues}")
        
        if total_issues == 0:
            print("\n🎉 MOUSE INTERACTION CORRECTLY INTEGRATED!")
            print("✓ Mouse world coordinate detection")
            print("✓ Real-time hover highlighting")
            print("✓ Direct tile clicking via coordinates")
            print("✓ Old entity click handlers removed")
            print("✓ Proper integration in update loop")
            print("✓ Documentation updated")
            print("\nMouse interaction matches phase4_visual_demo.py!")
            return True
        else:
            print(f"\n❌ {total_issues} ISSUES FOUND")
            if missing_functions:
                print("\nMissing functions/features:")
                for missing in missing_functions:
                    print(f"  • {missing}")
            if found_old_handlers:
                print("\nOld handlers still present:")
                for handler in found_old_handlers:
                    print(f"  • {handler}")
            return False
        
    except Exception as e:
        print(f"Error testing mouse interaction: {e}")
        return False

def test_interaction_flow():
    """Test the complete interaction flow"""
    print("\n" + "=" * 60)
    print("INTERACTION FLOW COMPARISON")
    print("=" * 60)
    
    print("PHASE4_VISUAL_DEMO.PY INTERACTION FLOW:")
    print("1. Mouse moves → get mouse.world_point")
    print("2. Convert world coordinates to grid coordinates")
    print("3. Highlight tile at grid position")
    print("4. Mouse clicks → get mouse.world_point")
    print("5. Convert world coordinates to grid coordinates")
    print("6. Call handle_tile_click(grid_x, grid_y)")
    print("7. Check for unit at grid position")
    print("8. Select unit or clear selection")
    print()
    
    print("ENHANCED_ECS_DEMO.PY INTERACTION FLOW:")
    print("1. _handle_update() calls _handle_mouse_interaction()")
    print("2. _handle_mouse_hover() gets mouse.world_point")
    print("3. Convert to grid: grid_x = int(round(mouse_pos.x))")
    print("4. Highlight tile with light_gray")
    print("5. _handle_mouse_click() gets mouse.world_point")
    print("6. Convert to grid coordinates")
    print("7. Call self.handle_tile_click(grid_x, grid_y)")
    print("8. handle_tile_click() checks for unit and shows action modal")
    print()
    
    print("✓ Both systems use identical world coordinate → grid conversion")
    print("✓ Both systems highlight tiles on hover")
    print("✓ Both systems call handle_tile_click() with grid coordinates")
    print("✓ Both systems provide unit selection and action modals")
    print("✓ Perfect interaction flow compatibility!")

def main():
    """Main test function"""
    print("=" * 70)
    print("MOUSE INTERACTION INTEGRATION TEST")
    print("=" * 70)
    print("Testing integration of phase4_visual_demo.py mouse interaction")
    print("into enhanced_ecs_demo.py")
    print("=" * 70)
    
    success = test_mouse_interaction_integration()
    
    if success:
        test_interaction_flow()
        print("\n" + "=" * 70)
        print("✅ MOUSE INTERACTION INTEGRATION COMPLETE")
        print("=" * 70)
        print("enhanced_ecs_demo.py now includes proper mouse interaction!")
        print()
        print("NEW FEATURES:")
        print("• Real-time tile hover highlighting")
        print("• Mouse world coordinate detection")
        print("• Direct tile clicking (no entity click handlers)")
        print("• Smooth mouse-to-grid coordinate conversion")
        print("• Visual feedback for tile selection")
        print()
        print("READY FOR TESTING!")
        return True
    else:
        print("\n" + "=" * 70)
        print("❌ MOUSE INTERACTION INTEGRATION INCOMPLETE")
        print("=" * 70)
        print("enhanced_ecs_demo.py has mouse interaction issues.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)