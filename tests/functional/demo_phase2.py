"""
Phase 2 Combat Systems Demonstration

Interactive demonstration of combat systems, equipment, and turn-based mechanics.
"""

import sys
import os
import time
import traceback
from typing import List, Tuple, Optional

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

try:
    from ursina import *
    URSINA_AVAILABLE = True
except ImportError:
    print("Ursina not available. Running in console mode.")
    URSINA_AVAILABLE = False

from demo_utils import create_demo_world, create_tactical_grid, create_character_archetypes
from core.math.vector import Vector2Int, Vector3
from core.ecs.component import Transform
from components.combat.damage import DamageComponent, AttackType, DamageResult
from components.combat.defense import DefenseComponent
from components.combat.attack import AttackComponent
from components.equipment.equipment import EquipmentComponent, EquipmentTier, EquipmentType, EquipmentStats
from components.equipment.equipment_manager import EquipmentManager
from systems.combat_system import CombatSystem
from game.battle.battle_manager import BattleManager
from game.battle.action_queue import BattleAction, ActionType
from ui.camera_controller import CameraController

# Global reference to demo instance for input handling
demo_instance = None


class Phase2Demo:
    """Demonstration of Phase 2 combat systems"""
    
    def __init__(self, use_visual: bool = True):
        self.use_visual = use_visual and URSINA_AVAILABLE
        self.world = None
        self.grid = None
        self.characters = []
        self.running = True
        self.paused = False
        
        # Combat systems
        self.combat_system = CombatSystem()
        self.battle_manager = None
        
        # Visual components
        self.grid_entities = []
        self.character_entities = []
        self.ui_text = None
        self.camera_controller = None
        
        # Demo state
        self.selected_character = 0
        self.demo_mode = "equipment"  # "equipment", "combat", "turn_based"
        self.frame_count = 0
        self.demo_start_time = time.time()
        
        print("Phase 2 Combat Systems Demonstration")
        print("====================================")
        self._initialize()
        
        # Set global reference for input handling
        global demo_instance
        demo_instance = self
    
    def _initialize(self):
        """Initialize the Phase 2 demonstration"""
        print("Initializing Phase 2 Combat Systems...")
        
        # Create game world
        self.world = create_demo_world()
        print(f"✓ World created with {self.world.system_count} systems")
        
        # Create tactical grid
        self.grid = create_tactical_grid(8, 8)
        print("✓ Tactical grid created (8x8)")
        
        # Create characters with combat capabilities
        self.characters = self._create_combat_characters()
        print(f"✓ Created {len(self.characters)} combat-ready characters")
        
        # Setup combat systems
        self.battle_manager = BattleManager(self.world)
        print("✓ Battle manager initialized")
        
        # Initialize visual components if available
        if self.use_visual:
            self._initialize_visual()
        
        print("✓ Phase 2 demonstration initialized successfully")
        print("\\nDemonstration Controls:")
        print("- TAB: Switch demo mode (equipment/combat/turn-based)")
        print("- 1-4: Select character")
        print("- E: Show equipment details")
        print("- C: Perform combat test")
        print("- T: Start turn-based battle")
        print("- SPACE: Pause/Resume")
        print("- ESC: Exit")
    
    def _create_combat_characters(self) -> List[Tuple[str, object]]:
        """Create characters with full combat capabilities"""
        base_characters = create_character_archetypes(self.world)
        combat_characters = []
        
        positions = [
            Vector3(1, 0, 1), Vector3(6, 0, 1), 
            Vector3(1, 0, 6), Vector3(6, 0, 6)
        ]
        
        for i, (name, character) in enumerate(base_characters):
            # Add combat components
            self._add_combat_components(character, name)
            
            # Add equipment
            self._add_demo_equipment(character, i)
            
            # Position character
            transform = character.get_component(Transform)
            if transform and i < len(positions):
                transform.position = positions[i]
            
            combat_characters.append((name, character))
        
        return combat_characters
    
    def _add_combat_components(self, character, name: str):
        """Add combat components to character"""
        # Add damage component based on character type
        if "Warrior" in name:
            damage = DamageComponent(physical_power=25, penetration=5, critical_chance=0.1)
            defense = DefenseComponent(physical_defense=20, armor_rating=10)
            attack = AttackComponent(primary_attack_type=AttackType.PHYSICAL, attack_range=1, accuracy=0.85)
        elif "Mage" in name:
            damage = DamageComponent(magical_power=30, penetration=3, critical_chance=0.15)
            defense = DefenseComponent(magical_defense=25, magic_resistance=15)
            attack = AttackComponent(primary_attack_type=AttackType.MAGICAL, attack_range=3, 
                                   area_effect_radius=1.5, accuracy=0.8)
        elif "Rogue" in name:
            damage = DamageComponent(physical_power=20, penetration=8, critical_chance=0.25)
            defense = DefenseComponent(physical_defense=12, armor_rating=5)
            attack = AttackComponent(primary_attack_type=AttackType.PHYSICAL, attack_range=1, accuracy=0.9)
        else:  # Paladin
            damage = DamageComponent(spiritual_power=22, physical_power=18, penetration=4, critical_chance=0.12)
            defense = DefenseComponent(spiritual_defense=25, spiritual_ward=12, physical_defense=18)
            attack = AttackComponent(primary_attack_type=AttackType.SPIRITUAL, attack_range=1, accuracy=0.85)
        
        character.add_component(damage)
        character.add_component(defense)
        character.add_component(attack)
        character.add_component(EquipmentManager())
    
    def _add_demo_equipment(self, character, char_index: int):
        """Add demonstration equipment to character"""
        equipment_manager = character.get_component(EquipmentManager)
        if not equipment_manager:
            return
        
        # Create tier-appropriate equipment based on character index
        tier = EquipmentTier(min(5, char_index + 2))  # Tiers 2-5
        
        # Create weapon
        weapon_stats = EquipmentStats(physical_attack=10, critical_chance=0.05)
        weapon = EquipmentComponent(
            name=f"Demo Weapon T{tier.value}",
            equipment_type=EquipmentType.WEAPON,
            tier=tier,
            base_stats=weapon_stats,
            special_abilities=["power_strike"] if tier.value >= 3 else []
        )
        
        # Create armor
        armor_stats = EquipmentStats(physical_defense=8, magical_defense=5)
        armor = EquipmentComponent(
            name=f"Demo Armor T{tier.value}",
            equipment_type=EquipmentType.ARMOR,
            tier=tier,
            base_stats=armor_stats,
            special_abilities=["damage_resistance"] if tier.value >= 4 else []
        )
        
        # Equip items
        equipment_manager.equip_item(weapon)
        equipment_manager.equip_item(armor)
    
    def _initialize_visual(self):
        """Initialize Ursina visual components"""
        self.app = Ursina()
        
        # Initialize camera controller (orbit mode only)
        self.camera_controller = CameraController(self.grid.width, self.grid.height)
        
        # Create visual elements
        self._create_grid_visual()
        self._create_character_visuals()
        self._create_ui()
    
    def _create_grid_visual(self):
        """Create visual representation of the grid"""
        for x in range(self.grid.width):
            for y in range(self.grid.height):
                pos = Vector2Int(x, y)
                cell = self.grid.get_cell(pos)
                
                if cell:
                    cube = Entity(
                        model='cube',
                        color=color.dark_gray,
                        position=(x, 0, y),
                        scale=(0.9, 0.1, 0.9)
                    )
                    self.grid_entities.append(cube)
    
    def _create_character_visuals(self):
        """Create visual representation of characters"""
        colors = [color.blue, color.red, color.green, color.yellow]
        
        for i, (name, character) in enumerate(self.characters):
            transform = character.get_component(Transform)
            pos = transform.position
            
            # Create character entity
            char_color = colors[i % len(colors)]
            char_entity = Entity(
                model='sphere',
                color=char_color,
                position=(pos.x, pos.y + 0.5, pos.z),
                scale=0.4
            )
            
            # Add name label
            label = Text(
                name,
                parent=char_entity,
                position=(0, 1.5, 0),
                scale=2,
                billboard=True,
                color=color.white
            )
            
            self.character_entities.append((char_entity, label))
    
    def _create_ui(self):
        """Create user interface elements"""
        self.ui_text = Text(
            '',
            position=(-0.8, 0.4),
            scale=1,
            parent=camera.ui,
            origin=(0, 0)
        )
        
        # Demo mode indicator
        self.mode_text = Text(
            f'Mode: {self.demo_mode.title()} (TAB to switch)',
            position=(-0.8, -0.4),
            scale=0.8,
            parent=camera.ui,
            origin=(0, 0),
            color=color.yellow
        )
    
    def handle_input(self, key):
        """Handle input for Phase 2 demo"""
        # Camera controls (from Phase 1)
        if key == 'scroll up' and self.camera_controller:
            self.camera_controller.camera_distance = max(
                self.camera_controller.min_distance,
                self.camera_controller.camera_distance - self.camera_controller.zoom_speed
            )
            self.camera_controller.update_camera()
            return
        elif key == 'scroll down' and self.camera_controller:
            self.camera_controller.camera_distance = min(
                self.camera_controller.max_distance,
                self.camera_controller.camera_distance + self.camera_controller.zoom_speed
            )
            self.camera_controller.update_camera()
            return
        elif key in ['left arrow', 'right arrow', 'up arrow', 'down arrow']:
            if self.camera_controller:
                if key == 'left arrow':
                    self.camera_controller.camera_angle_y -= 5.0
                elif key == 'right arrow':
                    self.camera_controller.camera_angle_y += 5.0
                elif key == 'up arrow':
                    self.camera_controller.camera_angle_x = max(-80, self.camera_controller.camera_angle_x - 5.0)
                elif key == 'down arrow':
                    self.camera_controller.camera_angle_x = min(80, self.camera_controller.camera_angle_x + 5.0)
                self.camera_controller.update_camera()
            return
        
        # Demo controls
        if key == 'tab':
            modes = ["equipment", "combat", "turn_based"]
            current_index = modes.index(self.demo_mode)
            self.demo_mode = modes[(current_index + 1) % len(modes)]
            if self.mode_text:
                self.mode_text.text = f'Mode: {self.demo_mode.title()} (TAB to switch)'
        
        elif key in ['1', '2', '3', '4']:
            self.selected_character = int(key) - 1
            if self.selected_character < len(self.characters):
                print(f"Selected {self.characters[self.selected_character][0]}")
        
        elif key == 'e':
            self._show_equipment_demo()
        
        elif key == 'c':
            self._show_combat_demo()
        
        elif key == 't':
            self._show_turn_based_demo()
        
        elif key == 'space':
            self.paused = not self.paused
            print(f"Demo {'paused' if self.paused else 'resumed'}")
        
        elif key == 'escape':
            self.running = False
            print("Exiting demonstration...")
    
    def _handle_camera_mouse_input(self):
        """Handle mouse input for camera (from Phase 1)"""
        if not self.camera_controller:
            return
        
        if held_keys['left mouse']:
            self.camera_controller.camera_angle_y += mouse.velocity.x * 50
            self.camera_controller.camera_angle_x = max(-80, min(80, 
                self.camera_controller.camera_angle_x - mouse.velocity.y * 50))
    
    def _show_equipment_demo(self):
        """Demonstrate equipment system"""
        if self.selected_character >= len(self.characters):
            return
        
        name, character = self.characters[self.selected_character]
        equipment_manager = character.get_component(EquipmentManager)
        
        if equipment_manager:
            summary = equipment_manager.get_equipment_summary()
            print(f"\\n=== Equipment Demo: {name} ===")
            print(f"Total Equipment Value: {summary['total_value']}")
            print(f"Special Abilities: {', '.join(summary['special_abilities']) or 'None'}")
            
            for eq_type, eq_info in summary['equipped_items'].items():
                print(f"\\n{eq_type.title()}:")
                print(f"  Name: {eq_info['name']}")
                print(f"  Tier: {eq_info['tier']} ({eq_info['tier_description']})")
                print(f"  Condition: {eq_info['condition_modifier']:.1%}")
    
    def _show_combat_demo(self):
        """Demonstrate combat calculations"""
        if len(self.characters) < 2:
            return
        
        attacker_name, attacker = self.characters[0]
        target_name, target = self.characters[1]
        
        print(f"\\n=== Combat Demo: {attacker_name} attacks {target_name} ===")
        
        # Test all attack types
        for attack_type in AttackType:
            damage_result = self.combat_system.calculate_damage(attacker, target, attack_type)
            if damage_result:
                print(f"{attack_type.value.title()} Attack:")
                print(f"  Damage: {damage_result.damage}")
                print(f"  Critical: {damage_result.critical}")
                print(f"  Penetration: {damage_result.penetration}")
    
    def _show_turn_based_demo(self):
        """Demonstrate turn-based combat"""
        print("\\n=== Turn-Based Combat Demo ===")
        
        # Split characters into teams
        player_units = [char[1] for char in self.characters[:2]]
        ai_units = [char[1] for char in self.characters[2:]]
        
        # Start battle
        self.battle_manager.start_battle(player_units, ai_units)
        
        # Show battle state
        battle_state = self.battle_manager.get_battle_state()
        print(f"Battle Active: {battle_state['is_active']}")
        print(f"Current Turn: {battle_state['turn_summary']['turn_number']}")
        print(f"Current Phase: {battle_state['turn_summary']['current_phase']}")
        print(f"Initiative Order:")
        
        for entry in battle_state['turn_summary']['initiative_order']:
            print(f"  Unit {entry['unit_id']}: Initiative {entry['initiative']}")
    
    def _get_status_text(self) -> str:
        """Generate status text for display"""
        runtime = time.time() - self.demo_start_time
        
        status = f"Phase 2 Combat Demo - Runtime: {runtime:.1f}s\\n"
        status += f"Mode: {self.demo_mode.title()} | Frame: {self.frame_count}\\n"
        status += f"Status: {'PAUSED' if self.paused else 'RUNNING'}\\n\\n"
        
        # Show selected character info
        if self.selected_character < len(self.characters):
            name, character = self.characters[self.selected_character]
            status += f"Selected: {name}\\n"
            
            # Show combat stats
            damage_comp = character.get_component(DamageComponent)
            defense_comp = character.get_component(DefenseComponent)
            
            if damage_comp:
                status += f"Attack: P{damage_comp.physical_power}/M{damage_comp.magical_power}/S{damage_comp.spiritual_power}\\n"
            
            if defense_comp:
                status += f"Defense: P{defense_comp.get_defense_value(AttackType.PHYSICAL)}/"
                status += f"M{defense_comp.get_defense_value(AttackType.MAGICAL)}/"
                status += f"S{defense_comp.get_defense_value(AttackType.SPIRITUAL)}\\n"
        
        # Show controls based on mode
        if self.demo_mode == "equipment":
            status += "\\nEquipment Mode:\\nE=Show Equipment | 1-4=Select Character"
        elif self.demo_mode == "combat":
            status += "\\nCombat Mode:\\nC=Combat Test | 1-4=Select Character"
        elif self.demo_mode == "turn_based":
            status += "\\nTurn-Based Mode:\\nT=Start Battle | 1-4=Select Character"
        
        status += "\\nTAB=Switch Mode | SPACE=Pause | ESC=Exit"
        
        return status
    
    def run(self):
        """Run the Phase 2 demonstration"""
        if self.use_visual:
            self._run_visual_mode()
        else:
            self._run_console_mode()
    
    def _run_visual_mode(self):
        """Run in visual mode with Ursina"""
        def update():
            if not self.running:
                application.quit()
                return
            
            self.frame_count += 1
            
            if not self.paused:
                # Update world
                self.world.update(time.dt)
            
            # Update camera
            if self.camera_controller:
                self._handle_camera_mouse_input()
                self.camera_controller.update_camera()
            
            # Update UI
            if self.ui_text:
                self.ui_text.text = self._get_status_text()
        
        print("\\nPhase 2 Combat Systems Demo")
        print("============================")
        print("Controls:")
        print("  TAB - Switch demo mode")
        print("  1-4 - Select character")
        print("  E - Show equipment")
        print("  C - Combat test")
        print("  T - Turn-based battle")
        print("  Arrow keys - Rotate camera")
        print("  Mouse drag - Rotate camera")
        print("  Scroll - Zoom camera")
        
        self.app.run()
    
    def _run_console_mode(self):
        """Run in console mode without visuals"""
        print("Running Phase 2 demo in console mode")
        print("Press Ctrl+C to exit")
        
        try:
            while self.running:
                time.sleep(0.1)
                
                # Demonstrate different systems periodically
                if self.frame_count % 100 == 0:
                    if self.demo_mode == "equipment":
                        self._show_equipment_demo()
                    elif self.demo_mode == "combat":
                        self._show_combat_demo()
                    elif self.demo_mode == "turn_based":
                        self._show_turn_based_demo()
                
                self.frame_count += 1
                
        except KeyboardInterrupt:
            print("\\nDemo interrupted by user")


def main():
    """Main entry point for Phase 2 demonstration"""
    print("Phase 2 Combat Systems Demonstration")
    print("===================================")
    
    try:
        use_visual = URSINA_AVAILABLE
        
        if not use_visual:
            print("Note: Running in console mode. Install Ursina for visual demonstration.")
        
        demo = Phase2Demo(use_visual=use_visual)
        demo.run()
        
        print("\\nPhase 2 demonstration completed successfully!")
        
    except Exception as e:
        print(f"Error running demonstration: {e}")
        traceback.print_exc()
        return 1
    
    return 0


# Global input function for Ursina
def input(key):
    """Global input handler for Ursina"""
    global demo_instance
    if demo_instance:
        demo_instance.handle_input(key)


if __name__ == "__main__":
    exit(main())