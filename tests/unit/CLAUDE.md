# Unit Tests

## Overview

This directory contains unit tests that validate individual components, systems, and functions in isolation. Unit tests focus on testing specific functionality without dependencies on other systems, ensuring that each piece works correctly on its own.

## Test Categories

### Core System Tests

#### `test_ecs_core.py` - Entity-Component-System Framework
Tests the fundamental ECS building blocks:

**Test Coverage:**
- **Entity Management** - Creation, component addition/removal, lifecycle
- **Component Behavior** - Serialization, deserialization, state management
- **System Processing** - Entity queries, component processing, update cycles
- **World Management** - Entity registration, system coordination

**Key Test Classes:**
```python
class TestEntity:
    def test_entity_creation(self):
        """Test entity creation and ID assignment"""
        
    def test_component_addition(self):
        """Test adding components to entities"""
        
    def test_component_removal(self):
        """Test removing components from entities"""

class TestComponent:
    def test_component_serialization(self):
        """Test component to_dict() functionality"""
        
    def test_component_deserialization(self):
        """Test component from_dict() functionality"""
        
    def test_component_lifecycle(self):
        """Test component initialization and cleanup"""

class TestSystem:
    def test_entity_queries(self):
        """Test system finding entities with specific components"""
        
    def test_system_processing(self):
        """Test system update logic"""
```

#### `test_stat_system.py` - Attribute and Statistics
Tests the 9-attribute system and derived statistics:

**Test Coverage:**
- **Attribute Calculations** - Base attributes, type bonuses, equipment modifiers
- **Derived Stats** - HP, MP, AP calculation from attributes
- **Stat Modifiers** - Temporary and permanent stat changes
- **Equipment Integration** - Weapon and armor stat bonuses

**Key Test Scenarios:**
```python
class TestAttributeSystem:
    def test_base_attribute_assignment(self):
        """Test random attribute generation within ranges"""
        unit = UnitStatsComponent("Test", UnitType.HEROMANCER)
        
        # All attributes should be in valid range (5-15 base + bonuses)
        assert 5 <= unit.wisdom <= 23
        assert 5 <= unit.strength <= 23
        
    def test_type_bonuses(self):
        """Test unit type bonuses are applied correctly"""
        heromancer = UnitStatsComponent("Hero", UnitType.HEROMANCER)
        magi = UnitStatsComponent("Mage", UnitType.MAGI)
        
        # Heromancer gets bonuses to speed, strength, finesse
        # Magi gets bonuses to wisdom, wonder, finesse
        # Both should have finesse bonus, but different other bonuses
        
    def test_derived_stat_calculation(self):
        """Test HP, MP, AP calculation from attributes"""
        unit = UnitStatsComponent("Test", UnitType.HEROMANCER, 
                                 strength=10, fortitude=10, 
                                 faith=10, worthy=10)
        
        expected_hp = (10 + 10 + 10 + 10) * 5  # 200
        assert unit.max_hp == expected_hp
        assert unit.hp == expected_hp

class TestEquipmentIntegration:
    def test_weapon_stat_bonuses(self):
        """Test weapon bonuses affect calculated stats"""
        unit = UnitStatsComponent("Test", UnitType.HEROMANCER)
        base_attack = unit.physical_attack
        
        # Equip weapon with +10 attack bonus
        weapon = {"type": "Weapons", "name": "Test Sword", 
                 "stats": {"physical_attack": 10}}
        unit.equip_weapon(weapon)
        
        assert unit.physical_attack == base_attack + 10
        
    def test_weapon_range_modification(self):
        """Test weapon modifies attack range"""
        unit = UnitStatsComponent("Test", UnitType.HEROMANCER)
        assert unit.attack_range == 1  # Base range
        
        # Equip spear with range 2
        spear = {"type": "Weapons", "name": "Spear",
                "stats": {"attack_range": 2, "effect_area": 2}}
        unit.equip_weapon(spear)
        
        assert unit.attack_range == 2
        assert unit.attack_effect_area == 2
```

#### `test_grid_pathfinding.py` - Tactical Movement
Tests pathfinding and grid-based movement:

**Test Coverage:**
- **Grid Representation** - 2D tactical grid with obstacles
- **Pathfinding Algorithms** - A* pathfinding implementation
- **Movement Validation** - Legal move checking, distance constraints
- **Obstacle Handling** - Terrain, units, and blocking elements

**Key Test Scenarios:**
```python
class TestPathfinding:
    def test_straight_line_path(self):
        """Test pathfinding for straight line movement"""
        grid = create_empty_grid(8, 8)
        start = (0, 0)
        end = (3, 0)
        
        path = find_path(grid, start, end)
        
        assert len(path) == 4  # Including start and end
        assert path[0] == start
        assert path[-1] == end
        
    def test_obstacle_avoidance(self):
        """Test pathfinding around obstacles"""
        grid = create_grid_with_obstacles(8, 8, obstacles=[(1, 0), (1, 1)])
        start = (0, 0)
        end = (2, 0)
        
        path = find_path(grid, start, end)
        
        # Path should go around obstacles
        assert (1, 0) not in path
        assert (1, 1) not in path
        assert path[-1] == end
        
    def test_no_path_available(self):
        """Test behavior when no path exists"""
        grid = create_grid_with_walls(8, 8)
        start = (0, 0)
        end = (7, 7)  # Completely blocked
        
        path = find_path(grid, start, end)
        
        assert path is None or len(path) == 0

class TestMovementValidation:
    def test_movement_range_limits(self):
        """Test movement limited by available movement points"""
        unit = create_test_unit(speed=10)  # 7 movement points (speed//2 + 2)
        
        assert unit.can_move_to(2, 3, empty_grid)  # 5 distance, within range
        assert not unit.can_move_to(5, 5, empty_grid)  # 10 distance, too far
        
    def test_occupied_space_blocking(self):
        """Test units cannot move to occupied spaces"""
        grid = create_grid_with_units(8, 8, unit_positions=[(3, 3)])
        unit = create_test_unit()
        
        assert not unit.can_move_to(3, 3, grid)  # Occupied space
        assert unit.can_move_to(3, 4, grid)  # Adjacent empty space
```

#### `test_ai_systems.py` - Artificial Intelligence
Tests AI decision-making and behavior systems:

**Test Coverage:**
- **Decision Trees** - AI action selection logic
- **Difficulty Scaling** - Adaptive AI behavior based on player performance
- **Tactical Assessment** - Board evaluation and threat analysis
- **Learning Systems** - Pattern recognition and adaptation

**Key Test Scenarios:**
```python
class TestAIDecisionMaking:
    def test_basic_combat_decisions(self):
        """Test AI makes reasonable combat choices"""
        ai_unit = create_ai_unit(AIDifficulty.STRATEGIC)
        enemy_unit = create_enemy_unit()
        battlefield = create_test_battlefield([ai_unit, enemy_unit])
        
        action = ai_unit.select_action(battlefield)
        
        # AI should choose to attack when enemy is in range
        assert isinstance(action, AttackAction)
        assert action.target == enemy_unit
        
    def test_tactical_positioning(self):
        """Test AI considers positioning in decisions"""
        ai_unit = create_ai_unit(position=(0, 0))
        enemies = [create_enemy_unit(position=(7, 7))]  # Far away
        battlefield = create_test_battlefield([ai_unit] + enemies)
        
        action = ai_unit.select_action(battlefield)
        
        # AI should move closer to engage
        assert isinstance(action, MoveAction)
        assert action.moves_toward_enemy(enemies[0])
        
    def test_difficulty_scaling(self):
        """Test AI difficulty affects decision quality"""
        easy_ai = create_ai_unit(AIDifficulty.SCRIPTED)
        hard_ai = create_ai_unit(AIDifficulty.ADAPTIVE)
        battlefield = create_complex_battlefield()
        
        easy_action = easy_ai.select_action(battlefield)
        hard_action = hard_ai.select_action(battlefield)
        
        # Hard AI should make more optimal decisions
        easy_score = evaluate_action_quality(easy_action, battlefield)
        hard_score = evaluate_action_quality(hard_action, battlefield)
        
        assert hard_score >= easy_score

class TestDifficultyScaling:
    def test_performance_tracking(self):
        """Test AI tracks player performance correctly"""
        difficulty_manager = DifficultyManager()
        
        # Simulate player wins
        for _ in range(3):
            difficulty_manager.record_battle_result(
                player_won=True, 
                turns_taken=10, 
                units_lost=0
            )
        
        performance = difficulty_manager.get_player_performance()
        assert performance.win_rate > 0.5
        assert performance.efficiency > 0.5
        
    def test_adaptive_scaling(self):
        """Test AI adapts to player performance"""
        difficulty_manager = DifficultyManager()
        
        # Simulate player struggling
        for _ in range(5):
            difficulty_manager.record_battle_result(
                player_won=False,
                turns_taken=20,
                units_lost=3
            )
        
        # AI should scale down difficulty
        assert difficulty_manager.should_decrease_difficulty()
        
        new_params = difficulty_manager.get_ai_parameters()
        assert new_params.reaction_time < 1.0  # Slower reactions
        assert new_params.risk_tolerance > 0.5  # More willing to take risks
```

## Test Utilities and Helpers

### Test Data Creation
```python
def create_test_unit(unit_type=UnitType.HEROMANCER, **attributes):
    """Create unit for testing with specified attributes"""
    return UnitStatsComponent("TestUnit", unit_type, **attributes)

def create_test_weapon(attack_bonus=10, range_bonus=0, area_bonus=0):
    """Create weapon data for testing"""
    return {
        "type": "Weapons",
        "name": "TestWeapon",
        "stats": {
            "physical_attack": attack_bonus,
            "attack_range": range_bonus + 1,
            "effect_area": area_bonus
        }
    }

def create_test_battlefield(units, width=8, height=8):
    """Create battlefield scenario for testing"""
    battlefield = Battlefield(width, height)
    for unit in units:
        battlefield.add_unit(unit)
    return battlefield
```

### Assertion Helpers
```python
def assert_attribute_in_range(attribute_value, min_val, max_val):
    """Assert attribute is within expected range"""
    assert min_val <= attribute_value <= max_val, \
        f"Attribute {attribute_value} not in range [{min_val}, {max_val}]"

def assert_stats_calculated_correctly(unit, expected_hp=None, expected_mp=None):
    """Assert derived stats are calculated correctly"""
    if expected_hp:
        assert unit.max_hp == expected_hp
    if expected_mp:
        assert unit.max_mp == expected_mp

def assert_equipment_effects_applied(unit, equipment, expected_bonuses):
    """Assert equipment bonuses are properly applied"""
    for stat, expected_bonus in expected_bonuses.items():
        actual_bonus = getattr(unit, stat) - getattr(unit, f"base_{stat}")
        assert actual_bonus == expected_bonus
```

### Mock Objects
```python
class MockAssetLoader:
    def __init__(self, test_data):
        self.test_data = test_data
    
    def load_data(self, path):
        return self.test_data.get(path, {})

class MockAI:
    def __init__(self, scripted_actions):
        self.scripted_actions = scripted_actions
        self.action_index = 0
    
    def select_action(self, battlefield):
        action = self.scripted_actions[self.action_index]
        self.action_index = (self.action_index + 1) % len(self.scripted_actions)
        return action
```

## Test Organization

### Test Naming Conventions
- **test_[functionality]** - What is being tested
- **test_[condition]_[expected_result]** - Specific scenario and outcome
- **test_[error_condition]_handling** - Error handling scenarios

### Test Structure
```python
class TestClassName:
    def setUp(self):
        """Set up test fixtures"""
        self.test_data = create_test_data()
        
    def tearDown(self):
        """Clean up after tests"""
        cleanup_test_data()
        
    def test_normal_operation(self):
        """Test normal, expected behavior"""
        
    def test_edge_cases(self):
        """Test boundary conditions and edge cases"""
        
    def test_error_conditions(self):
        """Test error handling and recovery"""
```

### Test Data Management
```python
# Test fixtures
@pytest.fixture
def sample_unit():
    return create_test_unit(UnitType.HEROMANCER, strength=15, finesse=12)

@pytest.fixture
def test_inventory():
    return create_test_inventory_with_items([
        create_test_weapon("Iron Sword", attack=10),
        create_test_armor("Leather Armor", defense=5),
        create_test_consumable("Health Potion", healing=50)
    ])

# Parameterized tests
@pytest.mark.parametrize("unit_type,expected_bonuses", [
    (UnitType.HEROMANCER, {'speed': 3, 'strength': 5, 'finesse': 4}),
    (UnitType.MAGI, {'wisdom': 6, 'wonder': 7, 'finesse': 3}),
])
def test_unit_type_bonuses(unit_type, expected_bonuses):
    unit = create_test_unit(unit_type)
    for attribute, min_bonus in expected_bonuses.items():
        assert getattr(unit, attribute) >= 5 + min_bonus
```

## Running Unit Tests

### Test Execution
```bash
# Run all unit tests
uv run -m pytest tests/unit/

# Run specific test file
uv run -m pytest tests/unit/test_stat_system.py

# Run with coverage
uv run -m pytest --cov=src tests/unit/

# Run with verbose output
uv run -m pytest -v tests/unit/
```

### Test Configuration
```python
# pytest.ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = --strict-markers --disable-warnings
markers =
    slow: marks tests as slow
    integration: marks tests as integration tests
    unit: marks tests as unit tests
```

## Best Practices

### Test Design
- **Single Responsibility** - Each test should verify one specific behavior
- **Independence** - Tests should not depend on each other
- **Repeatability** - Tests should produce consistent results
- **Fast Execution** - Unit tests should run quickly

### Test Quality
- **Clear Naming** - Test names should describe what is being tested
- **Good Coverage** - Test both success and failure cases
- **Meaningful Assertions** - Use specific assertions with clear error messages
- **Documentation** - Comment complex test logic

### Maintenance
- **Keep Tests Updated** - Update tests when code changes
- **Refactor Test Code** - Apply same quality standards as production code
- **Remove Dead Tests** - Delete tests that no longer serve a purpose
- **Monitor Performance** - Keep test execution time reasonable