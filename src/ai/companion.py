"""AI Companion system with learning capabilities."""

from ursina import *
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Callable
from enum import Enum
import random
import json

from ..combat.system import Combatant, DamageType, ABILITIES


class CompanionState(Enum):
    IDLE = "idle"
    FOLLOW = "follow"
    ATTACK = "attack"
    DEFEND = "defend"
    SUPPORT = "support"
    WAIT = "wait"


class CompanionPersonality(Enum):
    AGGRESSIVE = "aggressive"  # Prefers attacking
    DEFENSIVE = "defensive"    # Prefers defending player
    SUPPORTIVE = "supportive"  # Prefers healing/buffing
    BALANCED = "balanced"      # Adapts to situation


@dataclass
class CompanionType:
    """Definition for a companion type."""
    id: str
    name: str
    description: str
    personality: CompanionPersonality
    max_health: float
    attack_power: float
    defense: float
    speed: float
    abilities: List[str]
    model_color: tuple = (100, 150, 200)


COMPANION_TYPES = {
    'knight': CompanionType(
        id='knight',
        name='Sir Roland',
        description='A stalwart knight who excels at protecting allies',
        personality=CompanionPersonality.DEFENSIVE,
        max_health=120,
        attack_power=15,
        defense=20,
        speed=3,
        abilities=['shield_bash', 'battle_cry'],
        model_color=(180, 180, 200)
    ),
    'mage_companion': CompanionType(
        id='mage_companion',
        name='Elara',
        description='A mysterious mage with powerful spells',
        personality=CompanionPersonality.AGGRESSIVE,
        max_health=70,
        attack_power=25,
        defense=8,
        speed=3.5,
        abilities=['fireball', 'ice_shard'],
        model_color=(100, 100, 200)
    ),
    'healer_companion': CompanionType(
        id='healer_companion',
        name='Brother Marcus',
        description='A devoted healer who keeps the party alive',
        personality=CompanionPersonality.SUPPORTIVE,
        max_health=80,
        attack_power=8,
        defense=12,
        speed=3,
        abilities=['heal', 'blessing'],
        model_color=(200, 200, 100)
    ),
    'ranger_companion': CompanionType(
        id='ranger_companion',
        name='Aria',
        description='A skilled ranger with keen senses',
        personality=CompanionPersonality.BALANCED,
        max_health=90,
        attack_power=18,
        defense=10,
        speed=5,
        abilities=['precise_shot', 'trap'],
        model_color=(100, 150, 100)
    ),
}


class CompanionLearning:
    """Tracks companion learning and adaptation."""

    def __init__(self):
        # Player behavior tracking
        self.player_actions: Dict[str, int] = {
            'attacks': 0,
            'heals_used': 0,
            'abilities_used': 0,
            'damage_taken': 0,
            'enemies_killed': 0,
        }

        # Learned preferences
        self.preferences: Dict[str, float] = {
            'aggression': 0.5,      # 0 = passive, 1 = aggressive
            'support_priority': 0.5, # 0 = self, 1 = player
            'ability_usage': 0.5,    # 0 = basic attacks, 1 = abilities
            'positioning': 0.5,      # 0 = close, 1 = ranged
        }

        # Situation memory
        self.situation_memory: List[Dict] = []
        self.max_memory = 100

        # Trust/relationship level
        self.trust_level = 50  # 0-100

    def record_player_action(self, action_type: str, context: Dict = None):
        """Record a player action for learning."""
        if action_type in self.player_actions:
            self.player_actions[action_type] += 1

        # Store context for pattern learning
        if context:
            memory_entry = {
                'action': action_type,
                'context': context,
                'timestamp': time.time()
            }
            self.situation_memory.append(memory_entry)
            if len(self.situation_memory) > self.max_memory:
                self.situation_memory.pop(0)

        # Update preferences based on patterns
        self._update_preferences()

    def _update_preferences(self):
        """Update preferences based on learned patterns."""
        total_actions = sum(self.player_actions.values()) or 1

        # Adjust aggression based on attack frequency
        attack_ratio = self.player_actions['attacks'] / total_actions
        self.preferences['aggression'] = 0.3 + (attack_ratio * 0.7)

        # Adjust support priority based on damage taken
        if self.player_actions['damage_taken'] > 10:
            self.preferences['support_priority'] = min(1.0, self.preferences['support_priority'] + 0.05)

        # Adjust ability usage based on player's ability use
        if self.player_actions['abilities_used'] > self.player_actions['attacks']:
            self.preferences['ability_usage'] = min(1.0, self.preferences['ability_usage'] + 0.1)

    def get_recommended_action(self, situation: Dict) -> str:
        """Get recommended action based on learning."""
        player_health_ratio = situation.get('player_health_ratio', 1.0)
        enemies_nearby = situation.get('enemies_nearby', 0)
        companion_health_ratio = situation.get('companion_health_ratio', 1.0)

        # Emergency heal if player is low
        if player_health_ratio < 0.3 and self.preferences['support_priority'] > 0.5:
            return 'heal_player'

        # Attack if aggressive and enemies present
        if enemies_nearby > 0 and self.preferences['aggression'] > 0.6:
            return 'attack'

        # Defend if player taking damage
        if situation.get('player_under_attack', False) and self.preferences['support_priority'] > 0.5:
            return 'defend'

        return 'follow'

    def increase_trust(self, amount: int = 1):
        """Increase trust level."""
        self.trust_level = min(100, self.trust_level + amount)

    def decrease_trust(self, amount: int = 1):
        """Decrease trust level."""
        self.trust_level = max(0, self.trust_level - amount)

    def get_trust_modifier(self) -> float:
        """Get effectiveness modifier based on trust."""
        return 0.5 + (self.trust_level / 200)  # 0.5 to 1.0

    def to_dict(self) -> Dict:
        """Serialize learning data."""
        return {
            'player_actions': self.player_actions,
            'preferences': self.preferences,
            'trust_level': self.trust_level,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'CompanionLearning':
        """Deserialize learning data."""
        learning = cls()
        learning.player_actions = data.get('player_actions', learning.player_actions)
        learning.preferences = data.get('preferences', learning.preferences)
        learning.trust_level = data.get('trust_level', 50)
        return learning


class Companion(Entity):
    """An AI companion that follows and assists the player."""

    def __init__(self, companion_type: CompanionType, player: Entity, **kwargs):
        super().__init__(
            model='cube',
            color=color.rgb(*companion_type.model_color),
            scale=(0.8, 1.8, 0.8),
            collider='box'
        )

        self.companion_type = companion_type
        self.player = player

        # Combat stats
        self.combatant = Combatant(
            name=companion_type.name,
            max_health=companion_type.max_health,
            max_mana=50
        )
        self.combatant.attack_power = companion_type.attack_power
        self.combatant.defense = companion_type.defense

        # AI state
        self.state = CompanionState.FOLLOW
        self.target = None
        self.command_state: Optional[CompanionState] = None  # Player-issued command

        # Learning system
        self.learning = CompanionLearning()

        # Movement
        self.speed = companion_type.speed
        self.follow_distance = 3.0
        self.attack_range = 2.5

        # Combat
        self.attack_cooldown = 0
        self.ability_cooldowns: Dict[str, float] = {a: 0 for a in companion_type.abilities}

        # Dialogue
        self.idle_lines = [
            "Ready when you are!",
            "What's our next move?",
            "I've got your back.",
            "This place gives me the creeps...",
        ]
        self.combat_lines = [
            "For glory!",
            "Watch out!",
            "I'll handle this one!",
            "Stay behind me!",
        ]
        self.last_dialogue_time = 0
        self.dialogue_cooldown = 30.0

        # Name tag
        self.name_tag = Text(
            text=companion_type.name,
            parent=self,
            y=1.5,
            scale=8,
            billboard=True,
            origin=(0, 0),
            color=color.rgb(100, 200, 255)
        )

        # Health bar
        self.health_bar_bg = Entity(
            parent=self,
            model='quad',
            color=color.rgb(40, 40, 40),
            scale=(1.2, 0.08),
            y=1.3,
            billboard=True
        )
        self.health_bar = Entity(
            parent=self,
            model='quad',
            color=color.rgb(100, 200, 100),
            scale=(1.2, 0.08),
            y=1.3,
            billboard=True,
            origin=(-0.5, 0)
        )

        # Start following player
        self.position = self.player.position + Vec3(2, 0, 2)

    def update(self):
        if not self.combatant.is_alive:
            return

        # Update health bar
        health_ratio = self.combatant.health / self.combatant.max_health
        self.health_bar.scale_x = 1.2 * health_ratio

        # Update cooldowns
        if self.attack_cooldown > 0:
            self.attack_cooldown -= time.dt
        for ability in self.ability_cooldowns:
            if self.ability_cooldowns[ability] > 0:
                self.ability_cooldowns[ability] -= time.dt

        # Update combatant
        self.combatant.update_effects(time.dt)

        # Mana regeneration
        self.combatant.mana = min(50, self.combatant.mana + 2 * time.dt)

        # Get situation for learning-based decisions
        situation = self._assess_situation()

        # Check for player command override
        if self.command_state:
            self._execute_command(situation)
        else:
            # Use learning to decide action
            recommended = self.learning.get_recommended_action(situation)
            self._execute_learned_action(recommended, situation)

        # Random dialogue
        if time.time() - self.last_dialogue_time > self.dialogue_cooldown:
            if random.random() < 0.01:
                self.say_line()

    def _assess_situation(self) -> Dict:
        """Assess the current situation."""
        player_pos = self.player.position if hasattr(self.player, 'position') else Vec3(0, 0, 0)

        return {
            'player_health_ratio': getattr(self.player, 'health', 100) / 100,
            'companion_health_ratio': self.combatant.health / self.combatant.max_health,
            'distance_to_player': (self.position - player_pos).length(),
            'enemies_nearby': 1 if self.target else 0,  # Simplified
            'player_under_attack': False,  # Would need combat system integration
        }

    def _execute_command(self, situation: Dict):
        """Execute player-issued command."""
        if self.command_state == CompanionState.WAIT:
            pass  # Stay in place
        elif self.command_state == CompanionState.ATTACK:
            if self.target:
                self._do_attack()
            else:
                self._follow_player(situation)
        elif self.command_state == CompanionState.DEFEND:
            self._defend_player(situation)
        elif self.command_state == CompanionState.FOLLOW:
            self._follow_player(situation)

    def _execute_learned_action(self, action: str, situation: Dict):
        """Execute action based on learning."""
        if action == 'attack' and self.target:
            self._do_attack()
        elif action == 'defend':
            self._defend_player(situation)
        elif action == 'heal_player':
            self._try_heal()
        else:
            self._follow_player(situation)

    def _follow_player(self, situation: Dict):
        """Follow the player."""
        player_pos = self.player.position if hasattr(self.player, 'position') else Vec3(0, 0, 0)
        distance = situation['distance_to_player']

        if distance > self.follow_distance:
            direction = (player_pos - self.position)
            direction.y = 0
            if direction.length() > 0:
                direction = direction.normalized()
                self.position += direction * self.speed * time.dt

    def _defend_player(self, situation: Dict):
        """Stay close to player in defensive stance."""
        player_pos = self.player.position if hasattr(self.player, 'position') else Vec3(0, 0, 0)

        # Stay very close to player
        target_pos = player_pos + Vec3(1, 0, 0)
        direction = (target_pos - self.position)
        direction.y = 0
        if direction.length() > 1:
            direction = direction.normalized()
            self.position += direction * self.speed * time.dt

    def _do_attack(self):
        """Attack the current target."""
        if not self.target or self.attack_cooldown > 0:
            return

        distance = (self.target.position - self.position).length()

        # Move towards target if too far
        if distance > self.attack_range:
            direction = (self.target.position - self.position)
            direction.y = 0
            if direction.length() > 0:
                direction = direction.normalized()
                self.position += direction * self.speed * time.dt
        else:
            # Attack
            trust_mod = self.learning.get_trust_modifier()
            damage = self.combatant.attack_power * trust_mod

            if hasattr(self.target, 'combatant'):
                self.target.combatant.take_damage(damage, DamageType.PHYSICAL)
            elif hasattr(self.target, 'take_damage'):
                self.target.take_damage(damage)

            self.attack_cooldown = 1.5
            self.say_combat_line()

    def _try_heal(self):
        """Try to heal the player."""
        if 'heal' not in self.companion_type.abilities:
            return

        if self.ability_cooldowns.get('heal', 0) > 0:
            return

        if self.combatant.mana < 25:
            return

        # Would need to integrate with player's character
        print(f"{self.companion_type.name} casts Heal!")
        self.combatant.mana -= 25
        self.ability_cooldowns['heal'] = 8.0

    def set_target(self, target):
        """Set attack target."""
        self.target = target
        if target:
            self.learning.record_player_action('combat_started')

    def command(self, state: CompanionState):
        """Issue a command to the companion."""
        self.command_state = state
        print(f"{self.companion_type.name}: Understood!")

    def clear_command(self):
        """Clear the current command."""
        self.command_state = None

    def say_line(self):
        """Say an idle dialogue line."""
        line = random.choice(self.idle_lines)
        print(f"{self.companion_type.name}: \"{line}\"")
        self.last_dialogue_time = time.time()

    def say_combat_line(self):
        """Say a combat dialogue line."""
        if time.time() - self.last_dialogue_time > 5:
            line = random.choice(self.combat_lines)
            print(f"{self.companion_type.name}: \"{line}\"")
            self.last_dialogue_time = time.time()


class CompanionManager:
    """Manages all companions."""

    def __init__(self, player: Entity):
        self.player = player
        self.companions: List[Companion] = []
        self.max_companions = 2
        self.active_companion: Optional[Companion] = None

    def recruit(self, companion_type_id: str) -> Optional[Companion]:
        """Recruit a new companion."""
        if len(self.companions) >= self.max_companions:
            print("You already have the maximum number of companions!")
            return None

        if companion_type_id not in COMPANION_TYPES:
            print(f"Unknown companion type: {companion_type_id}")
            return None

        companion_type = COMPANION_TYPES[companion_type_id]
        companion = Companion(companion_type, self.player)
        self.companions.append(companion)

        if not self.active_companion:
            self.active_companion = companion

        print(f"{companion_type.name} has joined your party!")
        return companion

    def dismiss(self, companion: Companion):
        """Dismiss a companion."""
        if companion in self.companions:
            self.companions.remove(companion)
            if self.active_companion == companion:
                self.active_companion = self.companions[0] if self.companions else None
            destroy(companion)
            print(f"{companion.companion_type.name} has left the party.")

    def set_active(self, companion: Companion):
        """Set the active companion."""
        if companion in self.companions:
            self.active_companion = companion

    def command_all(self, state: CompanionState):
        """Issue a command to all companions."""
        for companion in self.companions:
            companion.command(state)

    def set_target_all(self, target):
        """Set attack target for all companions."""
        for companion in self.companions:
            companion.set_target(target)

    def update(self, dt: float):
        """Update all companions."""
        for companion in self.companions:
            if companion.combatant.is_alive:
                companion.update()
