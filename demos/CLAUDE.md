# Demos Directory

## Overview

This directory contains demonstration scripts and examples that showcase different aspects of the Apex Tactics system. These demos serve as both development tools and learning resources, illustrating how various components integrate and function together.

## Demo Categories

### Development Progress Demos
Sequential demonstrations showing the evolution of the system:

#### `apex-tactics-copy.py` - Base Reference
- **Purpose**: Reference copy of the original apex-tactics.py
- **Features**: Complete working tactical RPG with all core mechanics
- **Use Case**: Baseline comparison for new implementations

#### `apex_ecs_demo_final.py` - ECS Integration
- **Purpose**: Demonstrates the Entity-Component-System architecture
- **Features**: Shows how ECS components replace monolithic Unit class
- **Integration**: Asset system, component composition, system processing

#### `apex_tactics_with_imported_camera.py` - Modular Camera
- **Purpose**: Demonstrates camera system integration
- **Features**: Separated camera controls from main game logic
- **Benefits**: Improved modularity and reusable camera system

#### `apex_tactics_with_imported_components.py` - Component Integration
- **Purpose**: Shows integration of modular UI components
- **Features**: Panel system, inventory management, character displays
- **Architecture**: Demonstrates component-based UI design

### Advanced Feature Demos

#### `phase3_ai_demo.py` - AI System Showcase
- **Purpose**: Demonstrates AI capabilities and difficulty scaling
- **Features**: Multiple AI difficulty levels, adaptive behaviors, learning systems
- **Capabilities**: 
  - SCRIPTED - Basic rule-based AI
  - STRATEGIC - Tactical decision-making
  - ADAPTIVE - Player pattern recognition
  - LEARNING - Behavioral adaptation

#### `phase4_visual_demo.py` - Visual Effects System
- **Purpose**: Showcases advanced visual features and effects
- **Features**: Enhanced graphics, animations, particle effects
- **Integration**: Visual components, rendering pipeline, performance optimization

## Demo Usage Patterns

### Learning Path
Recommended order for understanding the system:

1. **`apex-tactics-copy.py`** - Understand baseline functionality
2. **`apex_tactics_with_imported_camera.py`** - See modular design benefits
3. **`apex_tactics_with_imported_components.py`** - Learn component architecture
4. **`apex_ecs_demo_final.py`** - Experience full ECS implementation
5. **`phase3_ai_demo.py`** - Explore AI capabilities
6. **`phase4_visual_demo.py`** - See advanced visual features

### Development Testing
Use demos for:
- **Feature Validation** - Test new components in isolation
- **Integration Testing** - Verify system interactions
- **Performance Analysis** - Benchmark different approaches
- **User Experience** - Evaluate gameplay feel and responsiveness

## Running Demos

### Prerequisites
```bash
# Ensure Ursina and dependencies are installed
uv install

# Set up Python path for imports
export PYTHONPATH="/path/to/alt-apex-tactics:$PYTHONPATH"
```

### Execution
```bash
# Run specific demo
uv run demos/apex_ecs_demo_final.py

# Run with specific features enabled
uv run demos/phase3_ai_demo.py --difficulty=adaptive

# Run visual demo with performance monitoring
uv run demos/phase4_visual_demo.py --profile
```

## Demo Features

### Asset Integration
Most demos showcase asset system integration:
```python
# Load game data from assets
from src.core.assets.data_manager import get_data_manager
dm = get_data_manager()

# Use real item data
spear = dm.get_item("spear")
inventory = dm.create_sample_inventory()

# Demonstrate weapon effects
unit.equip_weapon(spear.to_inventory_format())
print(f"Range: {unit.attack_range}, Area: {unit.attack_effect_area}")
```

### Component Composition
ECS demos show flexible entity creation:
```python
# Create different unit types with different component combinations
player_unit = Entity()
player_unit.add_component(UnitStatsComponent("Hero", UnitType.HEROMANCER))
player_unit.add_component(EquipmentComponent())
player_unit.add_component(PlayerControllerComponent())

ai_unit = Entity()
ai_unit.add_component(UnitStatsComponent("Orc", UnitType.UBERMENSCH))  
ai_unit.add_component(AIControllerComponent(AIDifficulty.STRATEGIC))
```

### Visual Progression
Visual demos show enhancement over time:
```python
# Phase 1: Basic wireframe rendering
create_basic_grid_visualization()

# Phase 2: Textured models and improved lighting
create_enhanced_visual_effects()

# Phase 3: Particle effects and animations
create_advanced_visual_system()
```

## Demo Architecture

### Modular Design
Demos are structured to showcase specific aspects:
```python
class DemoFramework:
    def __init__(self, demo_config: dict):
        self.config = demo_config
        self.features_enabled = demo_config.get('features', [])
        
    def setup_demo(self):
        """Initialize demo-specific features"""
        
    def run_demo_sequence(self):
        """Execute demonstration scenarios"""
        
    def display_results(self):
        """Show demo outcomes and metrics"""
```

### Feature Flags
Demos support enabling/disabling features:
```python
# Feature configuration
DEMO_CONFIG = {
    'features': ['ai_system', 'visual_effects', 'asset_integration'],
    'difficulty': 'adaptive',
    'visual_quality': 'high',
    'debug_mode': True
}

# Conditional feature activation
if 'ai_system' in config['features']:
    enable_advanced_ai()
    
if config['debug_mode']:
    enable_debug_visualizations()
```

### Performance Monitoring
Demos include performance tracking:
```python
class PerformanceMonitor:
    def __init__(self):
        self.metrics = {}
        
    def start_timing(self, operation: str):
        """Begin timing operation"""
        
    def end_timing(self, operation: str):
        """End timing and record result"""
        
    def display_performance_report(self):
        """Show performance summary"""
```

## Educational Value

### Code Examples
Demos serve as executable documentation:
- **Best Practices** - Show recommended implementation patterns
- **Integration Points** - Demonstrate how systems connect
- **Error Handling** - Illustrate robust error management
- **Testing Approaches** - Show validation and testing strategies

### Learning Progression
Demos build complexity incrementally:
1. **Simple Examples** - Basic functionality in isolation
2. **Integration Examples** - Multiple systems working together
3. **Advanced Examples** - Complex behaviors and optimizations
4. **Real-world Examples** - Production-ready implementations

## Demo Maintenance

### Keeping Current
- **Sync with Main** - Update demos when core systems change
- **Feature Parity** - Ensure demos showcase latest capabilities
- **Documentation** - Keep demo explanations current
- **Testing** - Verify demos run correctly in CI/CD

### Adding New Demos
When creating new demos:
1. **Clear Purpose** - Define what the demo illustrates
2. **Standalone Operation** - Demo should run independently
3. **Documentation** - Include clear explanation of features
4. **Progressive Complexity** - Build on previous concepts
5. **Performance Considerations** - Monitor resource usage

### Demo Templates
Standard template for new demos:
```python
"""
Demo: [Purpose]

Demonstrates: [Key Features]
Prerequisites: [Requirements]
Usage: uv run demos/my_demo.py [options]
"""

import sys
import os
# Standard demo imports...

class MyDemo:
    def __init__(self, config=None):
        """Initialize demo with optional configuration"""
        
    def setup(self):
        """Set up demo environment"""
        
    def run(self):
        """Execute demo sequence"""
        
    def cleanup(self):
        """Clean up demo resources"""

def main():
    """Main demo entry point"""
    demo = MyDemo()
    try:
        demo.setup()
        demo.run()
    finally:
        demo.cleanup()

if __name__ == "__main__":
    main()
```

## Troubleshooting Demos

### Common Issues
- **Import Errors** - Check PYTHONPATH and dependencies
- **Asset Loading** - Verify asset system is properly configured
- **Ursina Issues** - Ensure graphics drivers and Ursina are working
- **Performance** - Monitor resource usage and optimize if needed

### Debug Features
Most demos include debugging aids:
```python
# Debug mode activation
if '--debug' in sys.argv:
    enable_debug_logging()
    show_performance_metrics()
    enable_visual_debug_aids()

# Verbose output
if '--verbose' in sys.argv:
    enable_detailed_logging()
    show_system_state_updates()
```

## Best Practices

### Demo Design
- **Focused Scope** - Each demo should illustrate specific concepts
- **Clear Objectives** - Make learning goals explicit
- **Progressive Difficulty** - Build complexity gradually
- **Real-world Relevance** - Show practical applications

### Code Quality
- **Clean Examples** - Use demo code as teaching examples
- **Error Handling** - Demonstrate robust error management
- **Performance Awareness** - Show efficient implementations
- **Documentation** - Include comprehensive explanations

### User Experience
- **Easy Setup** - Minimize prerequisites and configuration
- **Clear Instructions** - Provide step-by-step guidance
- **Visual Feedback** - Show what's happening during execution
- **Meaningful Output** - Display results and metrics clearly