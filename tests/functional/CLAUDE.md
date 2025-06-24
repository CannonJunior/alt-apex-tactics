# Functional Demonstration

<system_context>
Ursina-based functional demonstration of Phase 1 foundation systems running as integrated Python program.
</system_context>

<critical_notes>
- Demonstrates all Phase 1 systems working together
- Visual representation using Ursina 3D engine
- Interactive demonstration with keyboard controls
- Performance monitoring and validation
</critical_notes>

<file_map>
Main demo: @tests/functional/demo_phase1.py
Demo utilities: @tests/functional/demo_utils.py
</file_map>

<patterns>
```python
# Demo application pattern
def create_demo_world():
    world = World()
    world.add_system(StatSystem())
    world.add_system(MovementSystem())
    return world
```
</patterns>