"""
Unit Tests for Core ECS Architecture

Tests Entity, Component, System, and World classes in isolation.
Validates performance targets and error handling.
"""

import pytest
import time
from unittest.mock import Mock, patch

# Import core ECS components
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from core.ecs.entity import Entity, EntityManager
from core.ecs.component import BaseComponent, Transform, ComponentRegistry
from core.ecs.system import BaseSystem, SystemManager
from core.ecs.world import World
from core.events.event_bus import Event
from core.math.vector import Vector3


class MockTestComponent(BaseComponent):
    """Test component for unit testing"""
    
    def __init__(self, value: int = 0):
        super().__init__()
        self.value = value
    
    def to_dict(self):
        base_dict = super().to_dict()
        base_dict['value'] = self.value
        return base_dict
    
    @classmethod
    def from_dict(cls, data):
        component = cls(data.get('value', 0))
        component.entity_id = data.get('entity_id')
        component.created_at = data.get('created_at', time.time())
        component.component_id = data.get('component_id', component.component_id)
        return component


class MockTestSystem(BaseSystem):
    """Test system for unit testing"""
    
    def __init__(self):
        super().__init__("MockTestSystem")
        self.updated_entities = []
    
    def get_required_components(self):
        return {MockTestComponent}
    
    def update(self, delta_time, entities):
        self.updated_entities = entities.copy()


class TestEntityManagement:
    """Test entity creation, destruction, and component management"""
    
    def test_entity_creation(self):
        """Test basic entity creation"""
        entity = Entity()
        assert entity.id is not None
        assert entity.active is True
        assert len(entity.get_all_components()) == 0
    
    def test_component_addition(self):
        """Test adding components to entities"""
        entity = Entity()
        component = MockTestComponent(42)
        
        entity.add_component(component)
        
        assert entity.has_component(MockTestComponent)
        assert entity.get_component(MockTestComponent) is component
        assert component.entity_id == entity.id
    
    def test_component_removal(self):
        """Test removing components from entities"""
        entity = Entity()
        component = MockTestComponent(42)
        entity.add_component(component)
        
        removed = entity.remove_component(MockTestComponent)
        
        assert removed is component
        assert not entity.has_component(MockTestComponent)
        assert component.entity_id is None
    
    def test_duplicate_component_error(self):
        """Test that adding duplicate component types raises error"""
        entity = Entity()
        entity.add_component(MockTestComponent(1))
        
        with pytest.raises(ValueError):
            entity.add_component(MockTestComponent(2))
    
    def test_entity_serialization(self):
        """Test entity serialization and deserialization"""
        ComponentRegistry.register(MockTestComponent)
        
        entity = Entity()
        entity.add_component(MockTestComponent(42))
        entity.add_component(Transform(Vector3(1, 2, 3)))
        
        # Serialize
        data = entity.to_dict()
        
        # Deserialize
        restored_entity = Entity.from_dict(data)
        
        assert restored_entity.id == entity.id
        assert restored_entity.has_component(MockTestComponent)
        assert restored_entity.has_component(Transform)
        assert restored_entity.get_component(MockTestComponent).value == 42


class TestEntityManager:
    """Test entity manager functionality"""
    
    def test_entity_creation(self):
        """Test entity manager creation"""
        manager = EntityManager()
        entity = manager.create_entity()
        
        assert entity.id in manager._entities
        assert manager.get_entity(entity.id) is entity
    
    def test_entity_with_components(self):
        """Test creating entity with initial components"""
        manager = EntityManager()
        component = MockTestComponent(42)
        
        entity = manager.create_entity(component)
        
        assert entity.has_component(MockTestComponent)
        assert entity.get_component(MockTestComponent) is component
    
    def test_entity_destruction(self):
        """Test entity destruction"""
        manager = EntityManager()
        entity = manager.create_entity()
        entity_id = entity.id
        
        success = manager.destroy_entity(entity_id)
        
        assert success is True
        assert not entity.active
        assert entity_id in manager._destroyed_entities
    
    def test_component_queries(self):
        """Test querying entities by components"""
        manager = EntityManager()
        
        # Create entities with different components
        entity1 = manager.create_entity(MockTestComponent(1))
        entity2 = manager.create_entity(Transform())
        entity3 = manager.create_entity(MockTestComponent(3), Transform())
        
        # Query by single component
        test_entities = manager.get_entities_with_component(MockTestComponent)
        assert len(test_entities) == 2
        assert entity1 in test_entities
        assert entity3 in test_entities
        
        # Query by multiple components
        both_components = manager.get_entities_with_components(MockTestComponent, Transform)
        assert len(both_components) == 1
        assert entity3 in both_components
    
    def test_cleanup_destroyed_entities(self):
        """Test cleanup of destroyed entities"""
        manager = EntityManager()
        entity = manager.create_entity(MockTestComponent(42))
        entity_id = entity.id
        
        manager.destroy_entity(entity_id)
        manager.cleanup_destroyed_entities()
        
        assert entity_id not in manager._entities
        assert len(manager._destroyed_entities) == 0


class TestSystemManagement:
    """Test system registration and execution"""
    
    def test_system_registration(self):
        """Test adding systems to manager"""
        from core.events.event_bus import EventBus
        event_bus = EventBus()
        manager = SystemManager(event_bus)
        system = MockTestSystem()
        
        manager.add_system(system)
        
        assert manager.get_system("MockTestSystem") is system
        assert manager.get_system_count() == 1
    
    def test_system_update(self):
        """Test system update with entities"""
        from core.events.event_bus import EventBus
        event_bus = EventBus()
        manager = SystemManager(event_bus)
        system = MockTestSystem()
        manager.add_system(system)
        
        # Create test entities
        entity1 = Entity()
        entity1.add_component(MockTestComponent(1))
        entity2 = Entity()
        entity2.add_component(Transform())
        entity3 = Entity()
        entity3.add_component(MockTestComponent(3))
        
        entities = [entity1, entity2, entity3]
        
        manager.update(0.016, entities)
        
        # MockTestSystem should only receive entities with MockTestComponent
        assert len(system.updated_entities) == 2
        assert entity1 in system.updated_entities
        assert entity3 in system.updated_entities
        assert entity2 not in system.updated_entities
    
    def test_system_priority(self):
        """Test system execution order by priority"""
        from core.events.event_bus import EventBus
        event_bus = EventBus()
        manager = SystemManager(event_bus)
        
        system1 = MockTestSystem()
        system1.name = "LowPriority"
        system1.priority = 10
        
        system2 = MockTestSystem()
        system2.name = "HighPriority"
        system2.priority = 1
        
        manager.add_system(system1)
        manager.add_system(system2)
        
        # Systems should be sorted by priority (lower number = higher priority)
        assert manager._systems[0].name == "HighPriority"
        assert manager._systems[1].name == "LowPriority"


class TestWorld:
    """Test world coordination and lifecycle"""
    
    def test_world_creation(self):
        """Test world initialization"""
        world = World()
        
        assert world.entity_manager is not None
        assert world.system_manager is not None
        assert world.running is False
    
    def test_entity_creation_through_world(self):
        """Test creating entities through world interface"""
        world = World()
        component = MockTestComponent(42)
        
        entity = world.create_entity(component)
        
        assert world.get_entity(entity.id) is entity
        assert entity.has_component(MockTestComponent)
    
    def test_world_lifecycle(self):
        """Test world initialization and shutdown"""
        world = World()
        
        # Initialize
        world.initialize()
        assert world.running is True
        
        # Shutdown
        world.shutdown()
        assert world.running is False
    
    def test_world_update(self):
        """Test world update cycle"""
        world = World()
        world.add_system(MockTestSystem())
        world.initialize()
        
        # Create test entity
        entity = world.create_entity(MockTestComponent(42))
        
        # Update world
        world.update(0.016)
        
        # Verify system was updated
        system = world.get_system("MockTestSystem")
        assert len(system.updated_entities) == 1
        assert system.updated_entities[0] is entity


class TestPerformance:
    """Test performance targets and optimization"""
    
    def test_entity_creation_performance(self):
        """Test entity creation performance"""
        manager = EntityManager()
        
        start_time = time.perf_counter()
        
        # Create 1000 entities
        entities = []
        for i in range(1000):
            entity = manager.create_entity(MockTestComponent(i))
            entities.append(entity)
        
        creation_time = time.perf_counter() - start_time
        
        # Should create 1000 entities in reasonable time
        assert creation_time < 0.1  # 100ms for 1000 entities
        assert len(entities) == 1000
    
    def test_component_query_performance(self):
        """Test component query performance"""
        manager = EntityManager()
        
        # Create entities with mixed components
        for i in range(1000):
            if i % 2 == 0:
                manager.create_entity(MockTestComponent(i))
            else:
                manager.create_entity(Transform())
        
        start_time = time.perf_counter()
        
        # Query for MockTestComponent entities
        test_entities = manager.get_entities_with_component(MockTestComponent)
        
        query_time = time.perf_counter() - start_time
        
        # Query should be fast
        assert query_time < 0.01  # 10ms for 1000 entity query
        assert len(test_entities) == 500
    
    def test_system_update_performance(self):
        """Test system update performance"""
        from core.events.event_bus import EventBus
        event_bus = EventBus()
        manager = SystemManager(event_bus)
        system = MockTestSystem()
        manager.add_system(system)
        
        # Create entities
        entities = []
        for i in range(100):
            entity = Entity()
            entity.add_component(MockTestComponent(i))
            entities.append(entity)
        
        start_time = time.perf_counter()
        
        # Update systems multiple times
        for _ in range(10):
            manager.update(0.016, entities)
        
        update_time = time.perf_counter() - start_time
        
        # Should handle 100 entities x 10 updates quickly
        assert update_time < 0.05  # 50ms for 1000 total updates


def run_ecs_tests():
    """Run all ECS unit tests"""
    pytest.main([__file__, "-v", "--tb=short"])


if __name__ == "__main__":
    run_ecs_tests()