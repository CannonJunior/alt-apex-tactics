#!/usr/bin/env python3
"""
Phase 3 AI Integration Demonstration

Interactive demo showcasing advanced AI systems:
- Dynamic difficulty scaling
- Leader AI with unique abilities
- Adaptive performance scaling
- Tactical AI analysis
"""

import sys
import os
import time
import random
from typing import List, Dict, Any

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.ecs.entity import Entity
from core.ecs.component import Transform
from core.ecs.world import World
from core.math.vector import Vector3
from components.stats.attributes import AttributeStats
from components.combat.attack import AttackComponent
from components.combat.damage import DamageComponent
from components.combat.defense import DefenseComponent

from ai.difficulty.difficulty_manager import DifficultyManager, AIDifficulty
from ai.difficulty.adaptive_scaling import AdaptiveScaling
from ai.leaders.leader_ai import LeaderAI, LeaderType, LeaderAbility
from ai.leaders.leader_behaviors import LeaderBehaviors
from ai.mcp.tactical_ai_tools import TacticalAITools


class Phase3Demo:
    """Phase 3 AI Integration Demo"""
    
    def __init__(self):
        self.world = World()
        self.battle_round = 0
        
        # Initialize AI systems
        self.difficulty_manager = DifficultyManager(AIDifficulty.STRATEGIC)
        self.adaptive_scaling = AdaptiveScaling(self.difficulty_manager)
        self.leader_behaviors = LeaderBehaviors()
        self.tactical_ai = TacticalAITools(self.world)
        
        # Demo entities
        self.player_units: List[Entity] = []
        self.ai_units: List[Entity] = []
        self.leader_unit: Entity = None
        self.leader_ai: LeaderAI = None
        
        print("=== Phase 3 AI Integration Demo ===")
        print("Showcasing advanced AI systems for tactical RPG")
        print()
    
    def setup_demo_battlefield(self):
        """Create demo battlefield with units"""
        print("Setting up battlefield...")
        
        # Create player units
        player_positions = [
            Vector3(2, 0, 5), Vector3(1, 0, 3), Vector3(3, 0, 3), Vector3(2, 0, 1)
        ]
        
        for i, pos in enumerate(player_positions):
            unit = Entity()
            unit.add_component(Transform(pos))
            unit.add_component(AttributeStats(
                strength=12 + random.randint(-2, 2),
                speed=10 + random.randint(-2, 2),
                wisdom=8 + random.randint(-2, 2),
                fortitude=10 + random.randint(-2, 2)
            ))
            unit.add_component(AttackComponent(attack_range=3))
            unit.add_component(DamageComponent(physical_power=15))
            unit.add_component(DefenseComponent(physical_defense=12))
            
            self.player_units.append(unit)
        
        # Create AI units
        ai_positions = [
            Vector3(8, 0, 5), Vector3(9, 0, 3), Vector3(7, 0, 3)
        ]
        
        for i, pos in enumerate(ai_positions):
            unit = Entity()
            unit.add_component(Transform(pos))
            unit.add_component(AttributeStats(
                strength=10 + random.randint(-1, 3),
                speed=9 + random.randint(-1, 3),
                wisdom=7 + random.randint(-1, 3),
                fortitude=9 + random.randint(-1, 3)
            ))
            unit.add_component(AttackComponent(attack_range=3))
            unit.add_component(DamageComponent(physical_power=12))
            unit.add_component(DefenseComponent(physical_defense=10))
            
            self.ai_units.append(unit)
        
        # Create AI leader unit
        self.leader_unit = Entity()
        self.leader_unit.add_component(Transform(Vector3(9, 0, 5)))
        self.leader_unit.add_component(AttributeStats(
            strength=15, speed=12, wisdom=14, fortitude=13
        ))
        self.leader_unit.add_component(AttackComponent(attack_range=4))
        self.leader_unit.add_component(DamageComponent(physical_power=18))
        self.leader_unit.add_component(DefenseComponent(physical_defense=15))
        
        # Initialize leader AI
        leader_types = list(LeaderType)
        selected_type = random.choice(leader_types)
        self.leader_ai = LeaderAI(self.leader_unit, selected_type, self.difficulty_manager)
        
        
        print(f"✓ Created {len(self.player_units)} player units")
        print(f"✓ Created {len(self.ai_units)} AI units")
        print(f"✓ Created AI leader ({selected_type.value})")
        print()
    
    def demonstrate_difficulty_scaling(self):
        """Demonstrate dynamic difficulty scaling"""
        print("=== Dynamic Difficulty Scaling Demo ===")
        
        # Show initial difficulty settings
        settings = self.difficulty_manager.get_current_settings()
        print(f"Initial Difficulty: {settings.level.value}")
        print(f"  Reaction Time: {settings.reaction_time}s")
        print(f"  Accuracy: {settings.accuracy_modifier}")
        print(f"  Planning Depth: {settings.planning_depth}")
        print()
        
        # Simulate battle results to show scaling
        print("Simulating battle results...")
        
        # Player wins streak
        print("Recording player victories...")
        for i in range(3):
            self.difficulty_manager.record_battle_result(
                player_won=True,
                battle_duration=45.0 + random.uniform(-10, 10),
                player_units_lost=random.randint(0, 1),
                ai_units_lost=random.randint(2, 4)
            )
            settings = self.difficulty_manager.get_current_settings()
            print(f"  Battle {i+1}: Difficulty now {settings.level.value}")
        
        print()
        
        # Show mistake probability
        mistake_count = 0
        test_runs = 100
        for _ in range(test_runs):
            if self.difficulty_manager.should_ai_make_mistake():
                mistake_count += 1
        
        print(f"Current AI mistake rate: {mistake_count}% (tested over {test_runs} decisions)")
        print()
    
    def demonstrate_adaptive_scaling(self):
        """Demonstrate real-time adaptive scaling"""
        print("=== Adaptive Performance Scaling Demo ===")
        
        # Simulate player actions with varying performance
        print("Recording player actions...")
        
        # High performance sequence
        print("  Simulating high-skill play...")
        for i in range(5):
            self.adaptive_scaling.record_player_action(
                action_type="attack",
                decision_time=0.8 + random.uniform(-0.2, 0.2),
                was_optimal=True,
                confidence=0.9
            )
        
        performance = self.adaptive_scaling.get_performance_feedback()
        print(f"  Performance Level: {performance['performance_level']}")
        print(f"  Tactical Accuracy: {performance['current_metrics']['tactical_accuracy']:.2f}")
        
        # Check AI adjustments
        adjustments = self.adaptive_scaling.current_ai_adjustments
        print(f"  AI Accuracy Boost: +{adjustments['accuracy_boost']:.2f}")
        print()
        
        # Low performance sequence
        print("  Simulating struggling play...")
        for i in range(5):
            self.adaptive_scaling.record_player_action(
                action_type="move",
                decision_time=4.0 + random.uniform(-1, 2),
                was_optimal=False,
                confidence=0.6
            )
        
        performance = self.adaptive_scaling.get_performance_feedback()
        print(f"  Performance Level: {performance['performance_level']}")
        print(f"  Tactical Accuracy: {performance['current_metrics']['tactical_accuracy']:.2f}")
        
        adjustments = self.adaptive_scaling.current_ai_adjustments
        print(f"  AI Accuracy Boost: {adjustments['accuracy_boost']:+.2f}")
        print(f"  AI Mistake Frequency: {adjustments['mistake_frequency']:+.2f}")
        print()
    
    def demonstrate_leader_ai(self):
        """Demonstrate leader AI system"""
        print("=== Leader AI System Demo ===")
        
        if not self.leader_ai:
            print("No leader AI initialized!")
            return
        
        # Show leader status
        status = self.leader_ai.get_leader_status()
        print(f"Leader Type: {status['leader_type']}")
        print(f"Command Points: {status['command_points']}/{status['max_command_points']}")
        print(f"Available Abilities: {len(status['available_abilities'])}")
        print()
        
        # Show available abilities
        print("Available Abilities:")
        for ability in status['available_abilities']:
            definition = self.leader_ai.ability_definitions.get(
                LeaderAbility(ability)
            )
            if definition:
                print(f"  • {definition.name}: {definition.description}")
        print()
        
        # Demonstrate leader decision making
        print("Leader AI Decision Making:")
        for round_num in range(3):
            print(f"\nRound {round_num + 1}:")
            
            # Update leader AI
            action = self.leader_ai.update_leader_ai(
                allied_units=self.ai_units + [self.leader_unit],
                enemy_units=self.player_units,
                delta_time=1.0
            )
            
            if action:
                if action['action_type'] == 'leader_ability':
                    print(f"  ⚡ Using ability: {action['ability_name']}")
                    print(f"     Range: {action['range']} units")
                    
                    # Execute the ability
                    ability = LeaderAbility(action['ability'])
                    result = self.leader_behaviors.execute_leader_ability(
                        ability,
                        self.leader_unit,
                        [unit for unit in self.player_units if unit.id in action.get('targets', [])],
                        {
                            'ally_units': self.ai_units + [self.leader_unit],
                            'enemy_units': self.player_units
                        }
                    )
                    
                    if result['success']:
                        print(f"     ✓ Ability executed successfully")
                        if 'allies_affected' in result:
                            print(f"     → {result['allies_affected']} allies affected")
                        if 'bonuses_applied' in result:
                            bonuses = result['bonuses_applied']
                            print(f"     → Bonuses: {list(bonuses.keys())}")
                    else:
                        print(f"     ✗ Ability failed: {result.get('error', 'Unknown error')}")
                else:
                    print(f"  🎯 Action: {action['action_type']}")
                    print(f"     Strategy: {action.get('strategy', 'unknown')}")
                    print(f"     Priority: {action.get('priority', 0):.1f}")
            else:
                print("  • No action taken this round")
            
            # Show updated status
            status = self.leader_ai.get_leader_status()
            print(f"     Command Points: {status['command_points']}")
        
        print()
    
    def demonstrate_tactical_analysis(self):
        """Demonstrate tactical AI analysis"""
        print("=== Tactical AI Analysis Demo ===")
        
        # Battlefield analysis
        print("Comprehensive Battlefield Analysis:")
        all_units = self.player_units + self.ai_units + [self.leader_unit]
        battlefield_size = (12, 10)
        
        analysis = self.tactical_ai.analyze_battlefield(all_units, battlefield_size)
        
        print(f"  Units on field: {analysis.unit_count}")
        print(f"  Average power: {analysis.average_power:.1f}")
        print(f"  Formation strength: {analysis.formation_strength:.2f}")
        print(f"  Terrain advantage: {analysis.terrain_advantage:.2f}")
        print(f"  Recommended action: {analysis.recommended_action}")
        print(f"  Confidence: {analysis.confidence:.2f}")
        print()
        
        # Unit evaluation
        print("Individual Unit Analysis:")
        for i, unit in enumerate(self.player_units[:2]):  # Show first 2 units
            evaluation = self.tactical_ai.evaluate_unit(unit, all_units)
            print(f"  Player Unit {i+1}:")
            print(f"    Combat Effectiveness: {evaluation.combat_effectiveness:.2f}")
            print(f"    Positioning Score: {evaluation.positioning_score:.2f}")
            print(f"    Threat Level: {evaluation.threat_level:.2f}")
            print(f"    Recommended Role: {evaluation.recommended_role}")
        print()
        
        # Tactical planning
        print("Multi-turn Tactical Planning:")
        plan = self.tactical_ai.plan_tactical_sequence(self.ai_units[:2], turns=3)
        
        for turn_plan in plan:
            print(f"  Turn {turn_plan['turn']}:")
            print(f"    Strategic Focus: {turn_plan['strategic_focus']}")
            print(f"    Planned Actions: {len(turn_plan['actions'])}")
            for action in turn_plan['actions'][:2]:  # Show first 2 actions
                print(f"      • {action}")
        print()
    
    def demonstrate_integration(self):
        """Demonstrate AI systems working together"""
        print("=== Integrated AI Systems Demo ===")
        
        print("Simulating integrated battle round...")
        
        # 1. Difficulty manager determines AI behavior
        current_difficulty = self.difficulty_manager.current_difficulty
        ai_accuracy = self.difficulty_manager.get_ai_modifier('accuracy')
        
        # 2. Adaptive scaling applies real-time adjustments
        adjusted_accuracy = self.adaptive_scaling.get_adjusted_ai_modifier('accuracy')
        should_make_mistake = self.adaptive_scaling.should_ai_make_adjusted_mistake()
        
        # 3. Leader AI makes tactical decisions
        if self.leader_ai:
            leader_action = self.leader_ai.update_leader_ai(
                allied_units=self.ai_units + [self.leader_unit],
                enemy_units=self.player_units,
                delta_time=1.0
            )
        
        # 4. Tactical AI provides battlefield analysis
        all_units = self.player_units + self.ai_units + [self.leader_unit]
        tactical_analysis = self.tactical_ai.analyze_battlefield(all_units, (12, 10))
        
        # Show integration results
        print(f"  Base Difficulty: {current_difficulty.value}")
        print(f"  Base AI Accuracy: {ai_accuracy:.2f}")
        print(f"  Adjusted Accuracy: {adjusted_accuracy:.2f}")
        print(f"  AI Should Make Mistake: {should_make_mistake}")
        print()
        
        if leader_action:
            print(f"  Leader Decision: {leader_action['action_type']}")
            if 'ability' in leader_action:
                print(f"    Ability Used: {leader_action['ability']}")
        
        print(f"  Tactical Recommendation: {tactical_analysis.recommended_action}")
        print(f"  Analysis Confidence: {tactical_analysis.confidence:.2f}")
        print()
        
        # Show active effects
        active_effects = self.leader_behaviors.get_active_effects()
        if active_effects:
            print(f"  Active Leader Effects: {len(active_effects)}")
            for effect_id, effect_data in list(active_effects.items())[:2]:
                print(f"    • {effect_data['type']} (Leader {effect_data['leader_id']})")
        
        print()
    
    def run_interactive_demo(self):
        """Run interactive demonstration"""
        print("Starting interactive Phase 3 AI demo...\n")
        
        # Setup
        self.setup_demo_battlefield()
        
        # Check if running in interactive environment
        import sys
        if not sys.stdin.isatty():
            print("Non-interactive environment detected. Running automated demo...\n")
            self.run_automated_demo()
            return
        
        while True:
            print("=== Phase 3 AI Demo Menu ===")
            print("1. Difficulty Scaling Demo")
            print("2. Adaptive Scaling Demo") 
            print("3. Leader AI Demo")
            print("4. Tactical Analysis Demo")
            print("5. Integrated Systems Demo")
            print("6. Show System Status")
            print("7. Reset Demo")
            print("0. Exit")
            
            try:
                choice = input("\nSelect demo (0-7): ").strip()
                print()
                
                if choice == '0':
                    print("Thanks for trying the Phase 3 AI demo!")
                    break
                elif choice == '1':
                    self.demonstrate_difficulty_scaling()
                elif choice == '2':
                    self.demonstrate_adaptive_scaling()
                elif choice == '3':
                    self.demonstrate_leader_ai()
                elif choice == '4':
                    self.demonstrate_tactical_analysis()
                elif choice == '5':
                    self.demonstrate_integration()
                elif choice == '6':
                    self.show_system_status()
                elif choice == '7':
                    self.reset_demo()
                else:
                    print("Invalid choice. Please select 0-7.")
                
                if choice != '0':
                    input("\nPress Enter to continue...")
                    print()
                    
            except KeyboardInterrupt:
                print("\n\nDemo interrupted. Goodbye!")
                break
            except Exception as e:
                print(f"Error: {e}")
                input("Press Enter to continue...")
    
    def run_automated_demo(self):
        """Run automated demonstration without user input"""
        print("=== Automated Phase 3 AI Demo ===")
        print("Running all demonstrations automatically...\n")
        
        demos = [
            ("Difficulty Scaling", self.demonstrate_difficulty_scaling),
            ("Adaptive Scaling", self.demonstrate_adaptive_scaling),
            ("Leader AI", self.demonstrate_leader_ai),
            ("Tactical Analysis", self.demonstrate_tactical_analysis),
            ("Integrated Systems", self.demonstrate_integration),
            ("System Status", self.show_system_status)
        ]
        
        for demo_name, demo_func in demos:
            print(f"{'='*60}")
            print(f"Running {demo_name} Demo...")
            print(f"{'='*60}")
            
            try:
                demo_func()
                print(f"✓ {demo_name} demo completed successfully")
            except Exception as e:
                print(f"✗ {demo_name} demo failed: {e}")
                import traceback
                traceback.print_exc()
            
            print()
            time.sleep(1)  # Brief pause between demos
        
        print("="*60)
        print("✓ All Phase 3 AI demonstrations completed!")
        print("="*60)
    
    def show_system_status(self):
        """Show comprehensive system status"""
        print("=== AI Systems Status ===")
        
        # Difficulty Manager
        settings = self.difficulty_manager.get_current_settings()
        print(f"Difficulty Manager:")
        print(f"  Current Level: {settings.level.value}")
        print(f"  Battles Recorded: {len(self.difficulty_manager.recent_battles)}")
        print(f"  AI Accuracy: {settings.accuracy_modifier}")
        print()
        
        # Adaptive Scaling
        adaptive_status = self.adaptive_scaling.get_adaptive_status()
        print(f"Adaptive Scaling:")
        print(f"  Performance Score: {adaptive_status['current_performance']:.2f}")
        print(f"  Adaptation Active: {adaptive_status['adaptation_active']}")
        print(f"  Actions Recorded: {adaptive_status['data_points']['actions_recorded']}")
        print()
        
        # Leader AI
        if self.leader_ai:
            leader_status = self.leader_ai.get_leader_status()
            print(f"Leader AI:")
            print(f"  Type: {leader_status['leader_type']}")
            print(f"  Command Points: {leader_status['command_points']}/{leader_status['max_command_points']}")
            print(f"  Abilities Used: {leader_status['abilities_used']}")
            print(f"  Battle Duration: {leader_status['battle_duration']:.1f}s")
        
        # Active Effects
        active_effects = self.leader_behaviors.get_active_effects()
        print(f"  Active Effects: {len(active_effects)}")
        print()
    
    def reset_demo(self):
        """Reset demo to initial state"""
        print("Resetting demo...")
        
        # Reset AI systems
        self.difficulty_manager = DifficultyManager(AIDifficulty.STRATEGIC)
        self.adaptive_scaling = AdaptiveScaling(self.difficulty_manager)
        self.leader_behaviors = LeaderBehaviors()
        
        # Clear entities
        self.world = World()
        self.player_units.clear()
        self.ai_units.clear()
        
        # Recreate battlefield
        self.setup_demo_battlefield()
        
        print("✓ Demo reset complete")
        print()


def main():
    """Main demo function"""
    try:
        demo = Phase3Demo()
        demo.run_interactive_demo()
    except Exception as e:
        print(f"Demo error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()