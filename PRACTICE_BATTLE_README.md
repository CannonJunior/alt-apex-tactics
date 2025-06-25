# Practice Battle Demo

## Overview

The Practice Battle feature has been successfully integrated into the Phase 4.5 UI system. This provides a complete tactical combat demonstration that showcases the game's core mechanics.

## Features

### Core Game Systems
- **Unit System**: Complete RPG unit stats with 9 attributes (wisdom, wonder, worthy, faith, finesse, fortitude, speed, spirit, strength)
- **Unit Types**: 6 different unit types with specialized bonuses (Heromancer, Ubermensch, Soul Linked, Realm Walker, Wargi, Magi)
- **Battle Grid**: 8x8 tactical grid system with unit placement and movement
- **Turn Management**: Player turns with movement point systems

### Camera System (from apex-tactics.py)
- **Orbit Mode**: Camera orbits around battle with mouse/keyboard control
- **Free Camera**: WASD movement with mouse look
- **Top-down Mode**: Fixed overhead tactical view
- **Zoom Control**: Scroll wheel zoom in orbit mode

### Visual Systems
- **3D Grid**: Visual grid tiles with highlighting
- **Unit Entities**: Color-coded 3D unit representations
- **Interactive UI**: Click-to-select and move mechanics
- **Information Panel**: Real-time unit stats and battle info

## Demo Units

### Player 1 (Bottom)
- **Alexios** (Heromancer) - Balanced fighter with speed/strength focus
- **Kassandra** (Ubermensch) - Physical powerhouse with fortitude
- **Barnabas** (Wargi) - Magical specialist with wisdom focus

### Player 2 (Top)
- **Deimos** (Soul Linked) - Spiritual defender with faith focus
- **Chrysis** (Magi) - Pure magic user with wonder abilities
- **Stentor** (Realm Walker) - Spiritual warrior hybrid

## Controls

### Camera Controls (Same as phase4_visual_demo.py)
- **WASD**: Move camera in all modes (primary camera movement)
- **Mouse Drag**: Rotate camera (orbit mode)
- **1/2/3**: Switch camera modes (Orbit/Free/Top-down)
- **Scroll Wheel**: Zoom in/out (orbit mode)
- **Arrow Keys**: Keyboard camera rotation (orbit mode)

### Battle Controls
- **Left Click**: Select unit or tile
- **Right Click**: Move selected unit (planned)
- **Space**: End turn manually
- **Enter**: Display battle log
- **ESC**: Exit to main menu

### UI Navigation
- **ESC**: Return to start screen from battle

## How to Run

### Start Screen Integration
```bash
uv run src/ui/screens/start_screen_demo.py
```
Then click the "PRACTICE BATTLE" button.

### Standalone Battle
```bash
uv run src/ui/screens/practice_battle.py
```

### Test Integration
```bash
uv run test_practice_battle.py
```

## Technical Implementation

### Files Structure
```
src/ui/screens/
├── start_screen_demo.py     # Main UI demo with battle integration
├── practice_battle.py       # Complete battle implementation
└── start_screen.py         # Original screen framework
```

### Key Classes
- **PracticeBattle**: Main battle controller
- **Unit**: RPG unit with full stat system
- **BattleGrid**: Tactical grid management
- **CameraController**: Advanced camera system (from apex-tactics.py)
- **GridTile/UnitEntity**: Visual 3D representations

### Integration Points
- Seamless transition from start screen to battle
- Proper cleanup and return to main menu
- Shared camera system with original apex-tactics
- Compatible with existing UI framework

## Game Mechanics

### Unit Stats
Each unit has 9 core attributes that determine:
- **HP**: Health points (derived from strength + fortitude + faith + worthy) × 5
- **MP**: Magic points (derived from wisdom + wonder + spirit + finesse) × 3
- **Movement**: Based on speed attribute
- **Attack/Defense**: Calculated from attribute combinations

### Combat System
- **Physical Attack**: (speed + strength + finesse) ÷ 2
- **Physical Defense**: (speed + strength + fortitude) ÷ 3
- **Damage Calculation**: Attack - Defense (minimum 1 damage)

### Turn System
- Players alternate turns
- Movement points refresh each turn
- Turn ends when movement points exhausted

## Phase 4.5 Achievement

This practice battle demonstrates the successful completion of Phase 4.5 objectives:

1. ✅ **Multi-panel UI Framework**: WindowPanel-based interface
2. ✅ **Ursina Integration**: Full 3D visualization 
3. ✅ **Portable Architecture**: Engine-agnostic design patterns
4. ✅ **Interactive Demo**: Functional start screen → battle → return flow
5. ✅ **Advanced Camera**: Imported from apex-tactics.py with full functionality
6. ✅ **Game Integration**: Real tactical combat mechanics

The practice battle serves as both a technical demonstration and a functional game prototype, showing how the Phase 4.5 UI framework can support complex game scenarios while maintaining portability for other engines like Unity and Godot.