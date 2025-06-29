# Integration Tests

## Overview

This directory contains integration tests that validate the interaction between multiple systems, components, and subsystems in Apex Tactics. These tests ensure that the various parts of the game work correctly together and that the overall system behaves as expected.

## Test Categories

### System Integration Tests

#### `test_full_system.py` - Complete System Integration
Comprehensive tests validating the entire game system working together:

**Test Coverage:**
- **ECS Integration** - Components, systems, and entities working together
- **Asset System** - Data loading and component integration
- **Combat Flow** - Complete attack sequences with all systems
- **UI Integration** - Panels updating with system state changes
- **Turn Management** - Full turn cycle with multiple systems

**Key Test Scenarios:**
```python
def test_complete_battle_sequence():
    """Test full battle from setup to victory"""
    # Setup battle with ECS entities
    # Process multiple turns with AI and player actions
    # Verify victory conditions and state consistency

def test_equipment_system_integration():
    """Test equipment affecting combat through all systems"""
    # Create unit with equipment system
    # Equip weapon with range/area properties
    # Verify combat system uses updated ranges
    # Confirm UI displays correct information

def test_asset_to_gameplay_pipeline():
    """Test complete pipeline from asset data to gameplay"""
    # Load item from JSON asset
    # Create unit and equip item
    # Execute combat using item properties
    # Verify all systems reflect item effects
```

#### `test_visual_systems.py` - Visual System Integration
Tests for graphics, UI, and visual feedback systems:

**Test Coverage:**
- **Rendering Pipeline** - 3D models, textures, and effects
- **UI Responsiveness** - Panel updates and user interactions
- **Visual Effects** - Particle systems and animations
- **Performance** - Frame rates and resource usage

**Key Test Scenarios:**
```python
def test_combat_visual_feedback():
    """Test visual effects during combat"""
    # Execute attack with area effect weapon
    # Verify highlighting shows correct range/area
    # Confirm damage numbers and effects appear
    # Check visual feedback matches game state

def test_ui_state_synchronization():
    """Test UI panels stay synchronized with game state"""
    # Modify game state through various systems
    # Verify all relevant UI panels update correctly
    # Test panel interactions don't desync state
    # Confirm error recovery maintains consistency
```

## Integration Test Patterns

### Multi-System Validation
```python
class SystemIntegrationTest:
    def setUp(self):
        """Set up integrated test environment"""
        self.world = World()
        self.asset_manager = get_asset_loader()
        self.data_manager = get_data_manager()
        
        # Initialize all required systems
        self.combat_system = CombatSystem()
        self.movement_system = MovementSystem()
        self.stat_system = StatSystem()
        
        # Set up test entities with realistic configurations
        self.setup_test_scenario()
    
    def test_multi_system_interaction(self):
        """Test systems working together correctly"""
        # Execute actions that involve multiple systems
        result = self.execute_complex_action()
        
        # Verify all systems updated consistently
        self.verify_system_consistency()
        
        # Check that state changes propagated correctly
        self.assert_state_synchronization()
```

### End-to-End Workflows
```python
def test_equipment_workflow():
    """Test complete equipment workflow"""
    # 1. Load item from asset system
    item_data = self.data_manager.get_item("spear")
    assert item_data is not None
    
    # 2. Create unit with equipment capability
    unit = self.create_test_unit_with_equipment()
    
    # 3. Equip item through equipment system
    equipment_comp = unit.get_component(EquipmentComponent)
    success = equipment_comp.equip_weapon(item_data.to_inventory_format())
    assert success
    
    # 4. Verify stats update correctly
    stats_comp = unit.get_component(UnitStatsComponent)
    assert stats_comp.attack_range == 2  # Spear range
    assert stats_comp.attack_effect_area == 2  # Spear area
    
    # 5. Execute combat using new stats
    combat_result = self.execute_combat_with_unit(unit)
    assert combat_result.range_used == 2
    assert len(combat_result.targets_affected) > 1  # Area effect
    
    # 6. Verify UI reflects changes
    ui_state = self.get_ui_state()
    assert ui_state.unit_info.weapon_name == "Spear"
    assert ui_state.unit_info.attack_range == 2
```

### Data Flow Validation
```python
def test_data_flow_integrity():
    """Test data flows correctly through all systems"""
    # Create test scenario with known initial state
    initial_state = self.capture_system_state()
    
    # Execute series of actions
    actions = [
        MoveAction(unit, new_position),
        EquipAction(unit, weapon),
        AttackAction(unit, target)
    ]
    
    for action in actions:
        # Execute action
        result = self.execute_action(action)
        
        # Verify intermediate state is valid
        current_state = self.capture_system_state()
        self.validate_state_transition(initial_state, current_state, action)
        
        # Update for next iteration
        initial_state = current_state
    
    # Verify final state meets expectations
    final_state = self.capture_system_state()
    self.validate_final_state(final_state)
```

## Test Scenarios

### Combat Integration Scenarios

#### Weapon Range and Area Effects
```python
def test_spear_combat_integration():
    """Test spear weapon integration across all systems"""
    # Setup: Unit with spear
    spear_unit = self.create_unit_with_spear()
    enemy_group = self.create_enemy_formation()
    
    # Action: Attack with spear
    attack_result = self.execute_spear_attack(spear_unit, enemy_group)
    
    # Verification:
    # - Combat system used correct range (2)
    # - Area effect hit multiple enemies (area 2)
    # - UI showed correct targeting highlights
    # - Damage calculated with weapon bonus
    # - Visual effects matched weapon properties
    
    assert attack_result.range_used == 2
    assert len(attack_result.affected_targets) >= 2
    assert attack_result.damage_bonus_applied == 14  # Spear bonus
```

#### Multi-Turn Battle Flow
```python
def test_multi_turn_battle_integration():
    """Test complete battle with multiple turns and systems"""
    # Setup battle scenario
    battle = self.setup_tactical_battle()
    
    # Execute multiple turns
    for turn in range(5):
        current_unit = battle.turn_manager.get_current_unit()
        
        # AI or player action
        action = self.get_turn_action(current_unit)
        
        # Execute through all systems
        result = battle.execute_turn_action(action)
        
        # Verify system consistency
        self.validate_turn_result(result)
        
        # Check victory conditions
        if battle.check_victory():
            break
    
    # Verify battle concluded properly
    assert battle.has_winner()
    self.validate_battle_end_state(battle)
```

### Asset Integration Scenarios

#### Asset Loading and Usage
```python
def test_asset_integration_pipeline():
    """Test complete asset loading and usage pipeline"""
    # 1. Asset Loading
    asset_files = self.data_manager.list_assets('data')
    assert 'items/base_items.json' in asset_files
    
    # 2. Data Parsing
    items = self.data_manager.get_all_items()
    assert len(items) > 0
    
    # 3. Component Integration
    for item in items:
        if item.type == "Weapons":
            # Create unit and equip weapon
            unit = self.create_test_unit()
            unit.equip_weapon(item.to_inventory_format())
            
            # Verify weapon properties affect gameplay
            self.verify_weapon_integration(unit, item)
    
    # 4. UI Integration
    inventory_panel = self.create_inventory_panel()
    inventory_panel.update_content({'inventory': items})
    
    # Verify UI shows correct item data
    self.verify_ui_item_display(inventory_panel, items)
```

### Performance Integration Tests

#### System Performance Under Load
```python
def test_system_performance_integration():
    """Test system performance with realistic load"""
    # Create large battle scenario
    large_battle = self.create_large_battle_scenario(
        units_per_side=20,
        ai_difficulty='adaptive'
    )
    
    # Monitor performance during execution
    with self.performance_monitor():
        # Execute intensive operations
        for _ in range(100):
            large_battle.process_turn()
            large_battle.update_ai_decisions()
            large_battle.refresh_ui_state()
        
        # Verify performance metrics
        metrics = self.get_performance_metrics()
        assert metrics.average_frame_time < 0.016  # 60 FPS
        assert metrics.memory_usage < 1000  # MB
        assert metrics.system_processing_time < 0.01  # Seconds per turn
```

## Test Environment Setup

### Integration Test Framework
```python
class IntegrationTestBase:
    def setUp(self):
        """Set up complete test environment"""
        # Initialize core systems
        self.world = World()
        self.asset_system = self.setup_asset_system()
        self.ui_system = self.setup_ui_system()
        
        # Create test data
        self.test_entities = self.create_test_entities()
        self.test_scenarios = self.load_test_scenarios()
        
        # Set up monitoring
        self.performance_monitor = PerformanceMonitor()
        self.state_validator = StateValidator()
    
    def tearDown(self):
        """Clean up test environment"""
        self.cleanup_test_entities()
        self.reset_system_state()
        self.generate_test_report()
```

### Mock and Stub Integration
```python
def create_controlled_test_environment():
    """Create test environment with controlled conditions"""
    # Use real components but controlled data
    mock_asset_loader = MockAssetLoader(test_data)
    mock_ui_system = MockUISystem()
    
    # Real systems with test configuration
    real_combat_system = CombatSystem(test_config)
    real_movement_system = MovementSystem(test_config)
    
    return TestEnvironment(
        asset_loader=mock_asset_loader,
        ui_system=mock_ui_system,
        combat_system=real_combat_system,
        movement_system=real_movement_system
    )
```

## Validation and Verification

### State Consistency Checks
```python
def validate_system_consistency(self):
    """Verify all systems have consistent state"""
    # Get state from each system
    combat_state = self.combat_system.get_state()
    movement_state = self.movement_system.get_state()
    ui_state = self.ui_system.get_state()
    
    # Cross-validate state consistency
    for entity_id in combat_state.entities:
        # Verify position consistency
        combat_pos = combat_state.get_position(entity_id)
        movement_pos = movement_state.get_position(entity_id)
        ui_pos = ui_state.get_displayed_position(entity_id)
        
        assert combat_pos == movement_pos == ui_pos
        
        # Verify stat consistency
        combat_stats = combat_state.get_stats(entity_id)
        ui_stats = ui_state.get_displayed_stats(entity_id)
        
        assert combat_stats.attack_range == ui_stats.attack_range
```

### End-to-End Verification
```python
def test_complete_game_flow():
    """Test complete game flow from start to finish"""
    # Initialize game
    game = self.create_test_game()
    
    # Play through complete scenario
    game_result = self.execute_complete_scenario(
        scenario='tactical_battle',
        player_actions=self.get_test_player_actions(),
        verification_points=self.get_verification_checkpoints()
    )
    
    # Verify final state
    assert game_result.victory_achieved
    assert game_result.all_systems_consistent
    assert game_result.no_errors_encountered
    assert game_result.performance_acceptable
```

## Best Practices

### Integration Test Design
- **Realistic Scenarios** - Test with realistic game situations
- **Cross-System Validation** - Verify data flows between all systems
- **Performance Awareness** - Monitor resource usage during tests
- **Error Recovery** - Test system behavior during failures

### Test Maintenance
- **Keep Current** - Update tests when systems change
- **Comprehensive Coverage** - Test all major system interactions
- **Clear Failure Messages** - Make test failures easy to diagnose
- **Performance Baselines** - Establish and monitor performance metrics

### Debugging Integration Issues
- **Isolation Testing** - Test systems individually first
- **State Logging** - Log system state at key points
- **Visual Debugging** - Use visual aids to understand failures
- **Incremental Complexity** - Start simple and add complexity gradually