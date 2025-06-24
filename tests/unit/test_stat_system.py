"""
Unit Tests for Stat System

Tests nine-attribute system, resources, and modifiers.
Validates performance targets for stat calculations.
"""

import pytest
import time
from unittest.mock import patch

# Import stat system components
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from components.stats.attributes import AttributeStats
from components.stats.resources import ResourceManager, MPResource, RageResource, KwanResource
from components.stats.modifiers import ModifierManager, Modifier, ModifierType, ModifierSource, StackingRule
from systems.stat_system import StatSystem
from core.ecs.entity import Entity
from core.ecs.world import World


class TestAttributeStats:
    """Test nine-attribute stat system"""
    
    def test_attribute_initialization(self):
        """Test attribute component creation with default values"""
        stats = AttributeStats()
        
        # All attributes should default to 10
        assert stats.strength == 10
        assert stats.fortitude == 10
        assert stats.finesse == 10
        assert stats.wisdom == 10
        assert stats.wonder == 10
        assert stats.worthy == 10
        assert stats.faith == 10
        assert stats.spirit == 10
        assert stats.speed == 10
    
    def test_custom_attributes(self):
        """Test creating attributes with custom values"""
        stats = AttributeStats(
            strength=15, fortitude=12, finesse=14,
            wisdom=8, wonder=6, worthy=11,
            faith=9, spirit=10, speed=13
        )
        
        assert stats.strength == 15
        assert stats.wisdom == 8
        assert stats.speed == 13
    
    def test_derived_stat_calculations(self):
        """Test derived stat formulas"""
        stats = AttributeStats(
            strength=15, fortitude=12, finesse=14,
            wisdom=8, wonder=6, worthy=11,
            faith=9, spirit=10, speed=13
        )
        
        derived = stats.derived_stats
        
        # Test specific formulas from Advanced-Implementation-Guide.md
        expected_hp = 12 * 10 + 15 * 2  # fortitude * 10 + strength * 2
        expected_mp = 8 * 8 + 6 * 3     # wisdom * 8 + wonder * 3
        expected_physical_attack = int(15 * 1.5 + 14 * 0.5)  # strength * 1.5 + finesse * 0.5
        
        assert derived['hp'] == expected_hp
        assert derived['mp'] == expected_mp
        assert derived['physical_attack'] == expected_physical_attack
    
    def test_derived_stat_caching(self):
        """Test performance caching of derived stats"""
        stats = AttributeStats(strength=15, fortitude=12)
        
        # First calculation should cache results
        start_time = time.perf_counter()
        derived1 = stats.derived_stats
        first_calc_time = time.perf_counter() - start_time
        
        # Second calculation should use cache
        start_time = time.perf_counter()
        derived2 = stats.derived_stats
        second_calc_time = time.perf_counter() - start_time
        
        # Results should be identical
        assert derived1 == derived2
        
        # Cache should be faster (though this might be negligible for simple stats)
        assert second_calc_time <= first_calc_time * 2  # Allow some variance
    
    def test_attribute_modification(self):
        """Test modifying attributes and cache invalidation"""
        stats = AttributeStats(strength=10)
        
        original_hp = stats.derived_stats['hp']
        
        # Modify attribute
        stats.modify_attribute('strength', 15)
        
        new_hp = stats.derived_stats['hp']
        
        # HP should increase due to strength increase
        assert new_hp > original_hp
        assert stats.strength == 15
    
    def test_performance_target(self):
        """Test stat calculation performance target (<1ms)"""
        # Create complex character with many derived stats
        stats = AttributeStats(
            strength=15, fortitude=12, finesse=14,
            wisdom=16, wonder=13, worthy=11,
            faith=9, spirit=10, speed=13
        )
        
        # Measure multiple calculations
        start_time = time.perf_counter()
        
        for _ in range(100):
            derived = stats.derived_stats
        
        total_time = time.perf_counter() - start_time
        avg_time = total_time / 100
        
        # Should meet <1ms target per calculation
        assert avg_time < 0.001, f"Stat calculation took {avg_time*1000:.3f}ms, target is <1ms"


class TestResourceManager:
    """Test three-resource system (MP, Rage, Kwan)"""
    
    def test_resource_initialization(self):
        """Test resource manager creation"""
        resources = ResourceManager(max_mp=120, max_rage=100, base_kwan=50)
        
        assert resources.mp.max_value == 120
        assert resources.mp.current_value == 120  # Starts full
        assert resources.rage.max_value == 100
        assert resources.rage.current_value == 0   # Starts empty
        assert resources.kwan.current_value == 50  # Starts at base
    
    def test_mp_regeneration(self):
        """Test MP regeneration over time"""
        resources = ResourceManager(max_mp=100)
        
        # Spend some MP
        resources.mp.subtract(50)
        assert resources.mp.current_value == 50
        
        # Update with regeneration
        resources.update(delta_time=1.0, location_type="normal", in_combat=False)
        
        # MP should regenerate (5 points per second by default)
        assert resources.mp.current_value > 50
    
    def test_rage_building_and_decay(self):
        """Test rage building from damage and natural decay"""
        resources = ResourceManager()
        
        # Build rage from taking damage
        rage_gained = resources.rage.add_from_damage_taken(20)
        assert rage_gained > 0
        assert resources.rage.current_value > 0
        
        initial_rage = resources.rage.current_value
        
        # Update with decay
        resources.update(delta_time=1.0, location_type="normal", in_combat=False)
        
        # Rage should decay over time
        assert resources.rage.current_value < initial_rage
    
    def test_kwan_location_effects(self):
        """Test Kwan changes based on location"""
        resources = ResourceManager(base_kwan=50)
        
        initial_kwan = resources.kwan.current_value
        
        # Update in a temple (should increase Kwan)
        resources.update(delta_time=0.1, location_type="temple", in_combat=False)
        
        # Kwan should be higher in temple
        assert resources.kwan.current_value > initial_kwan
        
        # Update in corrupted area (should decrease Kwan)
        resources.update(delta_time=0.1, location_type="corruption", in_combat=False)
        
        # Kwan should be lower in corruption
        assert resources.kwan.current_value < initial_kwan
    
    def test_resource_costs(self):
        """Test resource cost checking and spending"""
        resources = ResourceManager(max_mp=100, max_rage=100)
        
        # Build up some rage
        resources.rage.add_from_damage_taken(50)
        
        # Check if we can afford costs
        assert resources.can_afford_cost(mp_cost=30, rage_cost=25)
        assert not resources.can_afford_cost(mp_cost=150)  # Too much MP
        
        # Spend resources
        success = resources.spend_resources(mp_cost=30, rage_cost=25)
        assert success is True
        assert resources.mp.current_value == 70
        assert resources.rage.current_value < 50  # Some rage spent


class TestModifierSystem:
    """Test temporary modifier system with stacking rules"""
    
    def test_modifier_creation(self):
        """Test creating modifiers with different types"""
        flat_mod = Modifier(
            stat_name="strength",
            modifier_type=ModifierType.FLAT,
            value=5,
            duration=30.0
        )
        
        assert flat_mod.stat_name == "strength"
        assert flat_mod.value == 5
        assert not flat_mod.is_expired
    
    def test_modifier_stacking_unlimited(self):
        """Test unlimited stacking of modifiers"""
        manager = ModifierManager()
        
        mod1 = Modifier("strength", ModifierType.FLAT, 5, stacking_rule=StackingRule.UNLIMITED)
        mod2 = Modifier("strength", ModifierType.FLAT, 3, stacking_rule=StackingRule.UNLIMITED)
        
        manager.add_modifier(mod1)
        manager.add_modifier(mod2)
        
        # Both modifiers should apply
        final_value = manager.calculate_final_stat(10, "strength")
        assert final_value == 18  # 10 + 5 + 3
    
    def test_modifier_stacking_replace(self):
        """Test replace stacking rule"""
        manager = ModifierManager()
        
        mod1 = Modifier("strength", ModifierType.FLAT, 5, 
                       source_id="spell_1", stacking_rule=StackingRule.REPLACE)
        mod2 = Modifier("strength", ModifierType.FLAT, 8,
                       source_id="spell_1", stacking_rule=StackingRule.REPLACE)
        
        manager.add_modifier(mod1)
        manager.add_modifier(mod2)  # Should replace mod1
        
        # Only the second modifier should apply
        final_value = manager.calculate_final_stat(10, "strength")
        assert final_value == 18  # 10 + 8
    
    def test_modifier_stacking_highest(self):
        """Test highest value stacking rule"""
        manager = ModifierManager()
        
        mod1 = Modifier("strength", ModifierType.FLAT, 5, stacking_rule=StackingRule.HIGHEST)
        mod2 = Modifier("strength", ModifierType.FLAT, 3, stacking_rule=StackingRule.HIGHEST)
        
        manager.add_modifier(mod1)
        manager.add_modifier(mod2)  # Should not apply (lower value)
        
        # Only the higher modifier should apply
        final_value = manager.calculate_final_stat(10, "strength")
        assert final_value == 15  # 10 + 5
    
    def test_modifier_expiration(self):
        """Test modifier expiration and cleanup"""
        manager = ModifierManager()
        
        # Create short-duration modifier
        mod = Modifier("strength", ModifierType.FLAT, 5, duration=0.001)  # 1ms
        manager.add_modifier(mod)
        
        # Initially active
        assert manager.calculate_final_stat(10, "strength") == 15
        
        # Wait for expiration
        time.sleep(0.002)
        manager.update(0.001)
        
        # Should be expired and not apply
        assert manager.calculate_final_stat(10, "strength") == 10
    
    def test_complex_modifier_calculation(self):
        """Test complex modifier calculations with different types"""
        manager = ModifierManager()
        
        # Add various modifier types
        flat_mod = Modifier("attack", ModifierType.FLAT, 10)
        percent_mod = Modifier("attack", ModifierType.PERCENTAGE, 0.2)  # +20%
        mult_mod = Modifier("attack", ModifierType.MULTIPLICATIVE, 1.5)
        
        manager.add_modifier(flat_mod)
        manager.add_modifier(percent_mod)
        manager.add_modifier(mult_mod)
        
        # Base value: 50
        # + Flat: 50 + 10 = 60
        # + Percentage: 60 * 1.2 = 72
        # + Multiplicative: 72 * 1.5 = 108
        final_value = manager.calculate_final_stat(50, "attack")
        assert final_value == 108
    
    def test_modifier_performance(self):
        """Test modifier calculation performance"""
        manager = ModifierManager()
        
        # Add many modifiers
        for i in range(50):
            mod = Modifier(f"stat_{i % 5}", ModifierType.FLAT, i)
            manager.add_modifier(mod)
        
        # Measure calculation time
        start_time = time.perf_counter()
        
        for _ in range(100):
            result = manager.calculate_final_stat(100, "stat_0")
        
        total_time = time.perf_counter() - start_time
        avg_time = total_time / 100
        
        # Should be fast even with many modifiers
        assert avg_time < 0.001, f"Modifier calculation took {avg_time*1000:.3f}ms, target is <1ms"


class TestStatSystemIntegration:
    """Test stat system integration with ECS"""
    
    def test_stat_system_processing(self):
        """Test StatSystem processing entities with stat components"""
        world = World()
        stat_system = StatSystem()
        world.add_system(stat_system)
        
        # Create entity with stat components
        entity = world.create_entity(
            AttributeStats(strength=15, fortitude=12),
            ResourceManager(max_mp=100),
            ModifierManager()
        )
        
        # Update world
        world.initialize()
        world.update(0.016)
        
        # Verify components are processed
        attributes = entity.get_component(AttributeStats)
        resources = entity.get_component(ResourceManager)
        
        assert attributes is not None
        assert resources is not None
        assert resources.mp.max_value > 0  # Should be updated from derived stats
    
    def test_stat_system_performance(self):
        """Test StatSystem performance with many entities"""
        world = World()
        stat_system = StatSystem()
        world.add_system(stat_system)
        world.initialize()
        
        # Create many entities with complex stat setups
        entities = []
        for i in range(100):
            entity = world.create_entity(
                AttributeStats(
                    strength=10 + i % 10,
                    fortitude=10 + i % 8,
                    wisdom=10 + i % 12
                ),
                ResourceManager(),
                ModifierManager()
            )
            entities.append(entity)
        
        # Measure update performance
        start_time = time.perf_counter()
        
        for _ in range(10):
            world.update(0.016)
        
        total_time = time.perf_counter() - start_time
        avg_time = total_time / 10
        
        # Should handle 100 entities efficiently
        assert avg_time < 0.050, f"StatSystem update took {avg_time*1000:.1f}ms for 100 entities"
        
        # Check performance stats
        perf_stats = stat_system.get_performance_stats()
        assert perf_stats['performance_target_met'] is True


def run_stat_tests():
    """Run all stat system unit tests"""
    pytest.main([__file__, "-v", "--tb=short"])


if __name__ == "__main__":
    run_stat_tests()