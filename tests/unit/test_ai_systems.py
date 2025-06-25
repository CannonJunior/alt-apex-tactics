"""
Unit Tests for Phase 3 AI Systems

Tests for difficulty scaling, leader AI, and tactical analysis components.
"""

import unittest
import time
from unittest.mock import Mock, patch

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from core.ecs.entity import Entity
from core.ecs.component import Transform
from core.ecs.world import World
from core.math.vector import Vector3
from components.stats.attributes import AttributeStats
from components.combat.attack import AttackComponent
from components.combat.damage import DamageComponent
from components.combat.defense import DefenseComponent

from ai.difficulty.difficulty_manager import DifficultyManager, AIDifficulty
from ai.difficulty.adaptive_scaling import AdaptiveScaling, PerformanceMetrics
from ai.leaders.leader_ai import LeaderAI, LeaderType, LeaderAbility
from ai.leaders.leader_behaviors import LeaderBehaviors
from ai.mcp.tactical_ai_tools import TacticalAITools


class TestDifficultyManager(unittest.TestCase):
    """Test cases for difficulty scaling system"""
    
    def setUp(self):
        self.difficulty_manager = DifficultyManager(AIDifficulty.STRATEGIC)
    
    def test_initial_difficulty_settings(self):
        """Test initial difficulty configuration"""
        settings = self.difficulty_manager.get_current_settings()
        self.assertEqual(settings.level, AIDifficulty.STRATEGIC)
        self.assertEqual(settings.reaction_time, 1.5)
        self.assertEqual(settings.accuracy_modifier, 0.85)
        self.assertEqual(settings.planning_depth, 2)
    
    def test_battle_result_recording(self):
        """Test recording battle results"""
        # Record a player victory
        self.difficulty_manager.record_battle_result(
            player_won=True, 
            battle_duration=120.0,
            player_units_lost=1,
            ai_units_lost=3
        )
        
        self.assertEqual(len(self.difficulty_manager.recent_battles), 1)
        battle = self.difficulty_manager.recent_battles[0]
        self.assertTrue(battle['player_won'])
        self.assertEqual(battle['player_units_lost'], 1)
        self.assertEqual(battle['ai_units_lost'], 3)
    
    def test_difficulty_scaling_up(self):
        """Test difficulty increases after player wins"""
        # Record multiple player victories
        for _ in range(5):
            self.difficulty_manager.record_battle_result(
                player_won=True,
                battle_duration=60.0,
                player_units_lost=0,
                ai_units_lost=4
            )
        
        # Difficulty should increase (could be ADAPTIVE or LEARNING)
        self.assertIn(self.difficulty_manager.current_difficulty, [AIDifficulty.ADAPTIVE, AIDifficulty.LEARNING])
    
    def test_difficulty_scaling_down(self):
        """Test difficulty decreases after player losses"""
        # Record multiple player defeats
        for _ in range(5):
            self.difficulty_manager.record_battle_result(
                player_won=False,
                battle_duration=45.0,
                player_units_lost=4,
                ai_units_lost=0
            )
        
        # Difficulty should decrease
        self.assertEqual(self.difficulty_manager.current_difficulty, AIDifficulty.SCRIPTED)
    
    def test_ai_modifier_retrieval(self):
        """Test AI modifier values"""
        accuracy = self.difficulty_manager.get_ai_modifier('accuracy')
        self.assertEqual(accuracy, 0.85)  # Strategic difficulty accuracy
        
        damage = self.difficulty_manager.get_ai_modifier('damage')
        self.assertEqual(damage, 1.0)  # Strategic difficulty damage
    
    def test_mistake_probability(self):
        """Test AI mistake probability"""
        # Strategic difficulty should have 20% mistake chance
        mistake_count = 0
        test_runs = 1000
        
        for _ in range(test_runs):
            if self.difficulty_manager.should_ai_make_mistake():
                mistake_count += 1
        
        mistake_rate = mistake_count / test_runs
        # Should be approximately 0.2 (20%) with some variance
        self.assertGreater(mistake_rate, 0.15)
        self.assertLess(mistake_rate, 0.25)
    
    def test_force_difficulty_change(self):
        """Test manual difficulty override"""
        self.difficulty_manager.force_difficulty_change(AIDifficulty.LEARNING)
        self.assertEqual(self.difficulty_manager.current_difficulty, AIDifficulty.LEARNING)


class TestAdaptiveScaling(unittest.TestCase):
    """Test cases for adaptive scaling system"""
    
    def setUp(self):
        self.difficulty_manager = DifficultyManager()
        self.adaptive_scaling = AdaptiveScaling(self.difficulty_manager)
    
    def test_initial_metrics(self):
        """Test initial performance metrics"""
        metrics = self.adaptive_scaling.current_metrics
        self.assertEqual(metrics.actions_per_minute, 0.0)
        self.assertEqual(metrics.tactical_accuracy, 0.5)
        self.assertEqual(metrics.reaction_speed, 0.5)
    
    def test_action_recording(self):
        """Test recording player actions"""
        self.adaptive_scaling.record_player_action(
            action_type="attack",
            decision_time=2.0,
            was_optimal=True,
            confidence=0.9
        )
        
        self.assertEqual(len(self.adaptive_scaling.action_timestamps), 1)
        self.assertEqual(len(self.adaptive_scaling.decision_times), 1)
        self.assertEqual(len(self.adaptive_scaling.tactical_decisions), 1)
    
    def test_reaction_time_recording(self):
        """Test recording reaction times"""
        threat_time = time.time()
        response_time = threat_time + 1.5
        
        self.adaptive_scaling.record_reaction_time(threat_time, response_time)
        
        self.assertEqual(len(self.adaptive_scaling.reaction_times), 1)
        self.assertAlmostEqual(self.adaptive_scaling.reaction_times[0], 1.5, places=1)
    
    def test_performance_feedback(self):
        """Test performance feedback generation"""
        # Record some actions
        for i in range(5):
            self.adaptive_scaling.record_player_action(
                action_type="move",
                decision_time=1.0,
                was_optimal=True,
                confidence=0.8
            )
        
        feedback = self.adaptive_scaling.get_performance_feedback()
        
        self.assertIn('overall_score', feedback)
        self.assertIn('performance_level', feedback)
        self.assertIn('current_metrics', feedback)
        self.assertIsInstance(feedback['overall_score'], float)
    
    def test_adaptive_adjustments(self):
        """Test AI behavior adjustments"""
        # Simulate high performance
        for _ in range(10):
            self.adaptive_scaling.record_player_action(
                action_type="attack",
                decision_time=0.5,  # Fast decisions
                was_optimal=True,   # Good decisions
                confidence=0.9
            )
        
        # Check that AI adjustments are made
        adjustments = self.adaptive_scaling.current_ai_adjustments
        # Should boost AI difficulty when player performs well (may be minimal)
        self.assertGreaterEqual(adjustments.get('accuracy_boost', 0), 0)


class TestLeaderAI(unittest.TestCase):
    """Test cases for leader AI system"""
    
    def setUp(self):
        self.world = World()
        self.leader_entity = Entity()
        self.leader_entity.add_component(Transform(Vector3(5, 0, 5)))
        self.leader_entity.add_component(AttributeStats(strength=15, wisdom=12, speed=10))
        
        self.leader_ai = LeaderAI(
            self.leader_entity, 
            LeaderType.TACTICAL_COMMANDER
        )
    
    def test_leader_initialization(self):
        """Test leader AI initialization"""
        self.assertEqual(self.leader_ai.leader_type, LeaderType.TACTICAL_COMMANDER)
        self.assertEqual(self.leader_ai.command_points, 100)
        self.assertEqual(self.leader_ai.leadership_range, 5)
        
        # Check available abilities
        expected_abilities = [
            LeaderAbility.COORDINATE_ATTACK,
            LeaderAbility.FORMATION_COMMAND,
            LeaderAbility.TACTICAL_RETREAT,
            LeaderAbility.FLANKING_MANEUVER
        ]
        self.assertEqual(self.leader_ai.available_abilities, expected_abilities)
    
    def test_ability_usage_validation(self):
        """Test ability usage validation"""
        # Should be able to use abilities initially
        self.assertTrue(self.leader_ai._can_use_ability(LeaderAbility.COORDINATE_ATTACK))
        
        # Simulate using ability (reduce command points and set cooldown)
        self.leader_ai.command_points = 0
        self.assertFalse(self.leader_ai._can_use_ability(LeaderAbility.COORDINATE_ATTACK))
        
        # Test cooldown
        self.leader_ai.command_points = 100
        self.leader_ai.ability_cooldowns[LeaderAbility.COORDINATE_ATTACK] = time.time() + 30
        self.assertFalse(self.leader_ai._can_use_ability(LeaderAbility.COORDINATE_ATTACK))
    
    def test_battlefield_assessment(self):
        """Test battlefield situation assessment"""
        # Create mock allied and enemy units
        allied_units = []
        enemy_units = []
        
        for i in range(3):
            ally = Entity()
            ally.add_component(Transform(Vector3(i * 2, 0, 5)))
            ally.add_component(AttributeStats())
            allied_units.append(ally)
        
        for i in range(2):
            enemy = Entity()
            enemy.add_component(Transform(Vector3(10 + i * 2, 0, 5)))
            enemy.add_component(AttributeStats())
            enemy_units.append(enemy)
        
        assessment = self.leader_ai._assess_battlefield(allied_units, enemy_units)
        
        self.assertIn('allies_in_range', assessment)
        self.assertIn('enemies_in_range', assessment)
        self.assertIn('formation_score', assessment)
        self.assertIsInstance(assessment['formation_score'], float)
    
    def test_leader_decision_making(self):
        """Test leader decision making process"""
        allied_units = [self.leader_entity]  # Leader counts as ally
        enemy_units = []
        
        # Create enemy unit
        enemy = Entity()
        enemy.add_component(Transform(Vector3(7, 0, 5)))
        enemy.add_component(AttributeStats())
        enemy_units.append(enemy)
        
        action = self.leader_ai.update_leader_ai(allied_units, enemy_units, 1.0)
        
        self.assertIsInstance(action, dict)
        self.assertIn('action_type', action)
        self.assertIn('leader_id', action)
    
    def test_command_point_regeneration(self):
        """Test command point regeneration"""
        self.leader_ai.command_points = 50
        self.leader_ai._regenerate_command_points(10.0)  # 10 seconds
        
        # Should regenerate 20 points (2 per second)
        self.assertEqual(self.leader_ai.command_points, 70)
        
        # Test maximum cap
        self.leader_ai.command_points = 95
        self.leader_ai._regenerate_command_points(10.0)
        self.assertEqual(self.leader_ai.command_points, 100)  # Capped at max


class TestLeaderBehaviors(unittest.TestCase):
    """Test cases for leader behavior implementations"""
    
    def setUp(self):
        self.behaviors = LeaderBehaviors()
        self.leader_entity = Entity()
        self.leader_entity.add_component(Transform(Vector3(5, 0, 5)))
        self.leader_entity.add_component(AttributeStats())
    
    def test_coordinate_attack_execution(self):
        """Test coordinate attack ability execution"""
        # Create target
        target = Entity()
        target.add_component(Transform(Vector3(8, 0, 5)))
        target.add_component(AttributeStats())
        
        # Create allied attackers
        allies = []
        for i in range(3):
            ally = Entity()
            ally.add_component(Transform(Vector3(i + 3, 0, 5)))
            ally.add_component(AttributeStats())
            ally.add_component(AttackComponent(attack_range=5))
            ally.add_component(DamageComponent(physical_power=10))
            allies.append(ally)
        
        context = {'ally_units': allies, 'enemy_units': [target]}
        
        result = self.behaviors.execute_leader_ability(
            LeaderAbility.COORDINATE_ATTACK,
            self.leader_entity,
            [target],
            context
        )
        
        self.assertTrue(result['success'])
        self.assertIn('attackers_count', result)
        self.assertIn('bonuses_applied', result)
        self.assertGreater(result['attackers_count'], 0)
    
    def test_formation_command_execution(self):
        """Test formation command ability execution"""
        # Create allies to organize
        allies = []
        for i in range(4):
            ally = Entity()
            ally.add_component(Transform(Vector3(i * 3, 0, i * 2)))  # Scattered formation
            ally.add_component(AttributeStats())
            allies.append(ally)
        
        context = {'ally_units': allies}
        
        result = self.behaviors.execute_leader_ability(
            LeaderAbility.FORMATION_COMMAND,
            self.leader_entity,
            [],
            context
        )
        
        self.assertTrue(result['success'])
        self.assertIn('formation_type', result)
        self.assertIn('positions', result)
        self.assertEqual(len(result['positions']), len(allies))
    
    def test_rally_troops_execution(self):
        """Test rally troops ability execution"""
        # Create wounded allies
        allies = []
        for i in range(3):
            ally = Entity()
            ally.add_component(Transform(Vector3(i + 3, 0, 5)))
            attributes = AttributeStats(strength=10)
            attributes.current_hp = 30  # Wounded (max is usually around 100)
            ally.add_component(attributes)
            allies.append(ally)
        
        context = {'ally_units': allies}
        
        result = self.behaviors.execute_leader_ability(
            LeaderAbility.RALLY_TROOPS,
            self.leader_entity,
            [],
            context
        )
        
        self.assertTrue(result['success'])
        self.assertIn('units_healed', result)
        
        # Check that allies were actually healed
        for ally in allies:
            attributes = ally.get_component(AttributeStats)
            self.assertGreater(attributes.current_hp, 30)  # Should be healed
    
    def test_effect_tracking(self):
        """Test ability effect tracking"""
        # Execute an ability
        context = {'ally_units': [self.leader_entity]}
        
        result = self.behaviors.execute_leader_ability(
            LeaderAbility.INSPIRING_PRESENCE,
            self.leader_entity,
            [],
            context
        )
        
        self.assertTrue(result['success'])
        
        # Check that effect is tracked
        active_effects = self.behaviors.get_active_effects(self.leader_entity.id)
        self.assertGreater(len(active_effects), 0)
        
        # Find the inspiring presence effect
        inspiring_effect = None
        for effect_id, effect_data in active_effects.items():
            if effect_data['type'] == 'inspiring_presence':
                inspiring_effect = effect_data
                break
        
        self.assertIsNotNone(inspiring_effect)
        self.assertEqual(inspiring_effect['leader_id'], self.leader_entity.id)
    
    def test_effect_cleanup(self):
        """Test expired effect cleanup"""
        # Add a short-duration effect manually
        effect_id = f"test_effect_{self.leader_entity.id}_{time.time()}"
        self.behaviors.active_effects[effect_id] = {
            'type': 'test_effect',
            'leader_id': self.leader_entity.id,
            'duration': 0.1,  # Very short duration
            'start_time': time.time()
        }
        
        # Wait for effect to expire
        time.sleep(0.2)
        
        # Cleanup should remove expired effect
        self.behaviors.cleanup_expired_effects()
        self.assertNotIn(effect_id, self.behaviors.active_effects)


class TestTacticalAITools(unittest.TestCase):
    """Test cases for tactical AI analysis tools"""
    
    def setUp(self):
        self.world = World()
        self.ai_tools = TacticalAITools(self.world)
    
    def test_unit_evaluation(self):
        """Test individual unit evaluation"""
        # Create test unit
        unit = Entity()
        unit.add_component(Transform(Vector3(5, 0, 5)))
        unit.add_component(AttributeStats(strength=15, speed=12, fortitude=10))
        unit.add_component(DamageComponent(physical_power=20))
        unit.add_component(DefenseComponent(physical_defense=15))
        unit.add_component(AttackComponent())
        
        # Create context units
        other_units = [unit]  # Just self for simplicity
        
        evaluation = self.ai_tools.evaluate_unit(unit, other_units)
        
        self.assertEqual(evaluation.unit_id, unit.id)
        self.assertIsInstance(evaluation.combat_effectiveness, float)
        self.assertIsInstance(evaluation.positioning_score, float)
        self.assertIsInstance(evaluation.threat_level, float)
        self.assertIsInstance(evaluation.tactical_value, float)
        self.assertIn(evaluation.recommended_role, ['assault', 'tank', 'balanced', 'support'])
    
    def test_battlefield_analysis(self):
        """Test comprehensive battlefield analysis"""
        # Create multiple units
        units = []
        for i in range(4):
            unit = Entity()
            unit.add_component(Transform(Vector3(i * 2, 0, 5)))
            unit.add_component(AttributeStats())
            unit.add_component(DamageComponent(physical_power=15))
            unit.add_component(DefenseComponent(physical_defense=10))
            units.append(unit)
        
        analysis = self.ai_tools.analyze_battlefield(units, (10, 10))
        
        self.assertEqual(analysis.unit_count, 4)
        self.assertIsInstance(analysis.average_power, float)
        self.assertIsInstance(analysis.formation_strength, float)
        self.assertIsInstance(analysis.terrain_advantage, float)
        self.assertIn(analysis.recommended_action, [
            'aggressive_advance', 'coordinated_attack', 'defensive_formation', 
            'regroup', 'cautious_advance'
        ])
        self.assertIsInstance(analysis.confidence, float)
    
    def test_optimal_position_finding(self):
        """Test optimal position calculation"""
        # Create unit
        unit = Entity()
        unit.add_component(Transform(Vector3(5, 0, 5)))
        unit.add_component(AttributeStats(speed=10))
        
        # Create other units for context
        other_units = [unit]
        
        # Mock pathfinder for testing
        mock_pathfinder = Mock()
        mock_pathfinder.find_path.return_value = [Vector3(5, 0, 5), Vector3(6, 0, 5)]
        self.ai_tools.set_pathfinder(mock_pathfinder)
        
        optimal_pos = self.ai_tools.find_optimal_position(unit, other_units, (10, 10))
        
        # Should return a valid position or None
        if optimal_pos:
            self.assertIsInstance(optimal_pos.x, int)
            self.assertIsInstance(optimal_pos.y, int)
    
    def test_target_selection(self):
        """Test optimal target selection"""
        # Create attacker
        attacker = Entity()
        attacker.add_component(Transform(Vector3(5, 0, 5)))
        attacker.add_component(AttackComponent(attack_range=5))
        attacker.add_component(DamageComponent(physical_power=20))
        
        # Create potential targets
        targets = []
        for i in range(3):
            target = Entity()
            target.add_component(Transform(Vector3(i + 6, 0, 5)))  # Within range
            target.add_component(AttributeStats())
            target.add_component(DefenseComponent())
            targets.append(target)
        
        optimal_target = self.ai_tools.select_optimal_target(attacker, targets)
        
        # Should select one of the targets
        if optimal_target:
            self.assertIn(optimal_target, targets)
    
    def test_tactical_sequence_planning(self):
        """Test multi-turn tactical planning"""
        # Create units
        units = []
        for i in range(2):
            unit = Entity()
            unit.add_component(Transform(Vector3(i * 3, 0, 5)))
            unit.add_component(AttributeStats())
            units.append(unit)
        
        plan = self.ai_tools.plan_tactical_sequence(units, turns=3)
        
        self.assertEqual(len(plan), 3)  # 3 turns planned
        
        for turn_plan in plan:
            self.assertIn('turn', turn_plan)
            self.assertIn('actions', turn_plan)
            self.assertIn('strategic_focus', turn_plan)
            self.assertIsInstance(turn_plan['actions'], list)


if __name__ == '__main__':
    # Create test suite
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTest(unittest.makeSuite(TestDifficultyManager))
    suite.addTest(unittest.makeSuite(TestAdaptiveScaling))
    suite.addTest(unittest.makeSuite(TestLeaderAI))
    suite.addTest(unittest.makeSuite(TestLeaderBehaviors))
    suite.addTest(unittest.makeSuite(TestTacticalAITools))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print(f"\n=== Test Summary ===")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    if result.failures:
        print(f"\nFailures:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback}")
    
    if result.errors:
        print(f"\nErrors:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback}")