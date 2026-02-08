"""Combat system for real-time battles."""

from ursina import *
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Callable
from enum import Enum
import config


class DamageType(Enum):
    PHYSICAL = "physical"
    MAGIC = "magic"
    FIRE = "fire"
    ICE = "ice"
    LIGHTNING = "lightning"
    HOLY = "holy"
    DARK = "dark"


@dataclass
class Ability:
    """An ability or skill that can be used in combat."""
    id: str
    name: str
    description: str
    damage_type: DamageType
    base_damage: float
    mana_cost: float
    cooldown: float
    range: float = 5.0
    is_aoe: bool = False
    aoe_radius: float = 0.0
    effects: Dict = field(default_factory=dict)

    # Runtime state
    current_cooldown: float = 0.0

    def is_ready(self) -> bool:
        return self.current_cooldown <= 0

    def use(self):
        self.current_cooldown = self.cooldown

    def update(self, dt: float):
        if self.current_cooldown > 0:
            self.current_cooldown -= dt


# Define abilities
ABILITIES = {
    # Warrior abilities
    'power_strike': Ability(
        id='power_strike',
        name='Power Strike',
        description='A powerful melee attack',
        damage_type=DamageType.PHYSICAL,
        base_damage=25,
        mana_cost=10,
        cooldown=2.0,
        range=2.5
    ),
    'shield_bash': Ability(
        id='shield_bash',
        name='Shield Bash',
        description='Bash with shield, stunning the enemy',
        damage_type=DamageType.PHYSICAL,
        base_damage=15,
        mana_cost=15,
        cooldown=5.0,
        range=2.0,
        effects={'stun': 2.0}
    ),
    'battle_cry': Ability(
        id='battle_cry',
        name='Battle Cry',
        description='Boost attack power temporarily',
        damage_type=DamageType.PHYSICAL,
        base_damage=0,
        mana_cost=20,
        cooldown=15.0,
        range=0,
        effects={'buff_attack': 1.5, 'duration': 10.0}
    ),

    # Mage abilities
    'fireball': Ability(
        id='fireball',
        name='Fireball',
        description='Launch a ball of fire',
        damage_type=DamageType.FIRE,
        base_damage=30,
        mana_cost=20,
        cooldown=3.0,
        range=15.0,
        is_aoe=True,
        aoe_radius=3.0
    ),
    'ice_shard': Ability(
        id='ice_shard',
        name='Ice Shard',
        description='Pierce enemy with ice',
        damage_type=DamageType.ICE,
        base_damage=20,
        mana_cost=12,
        cooldown=1.5,
        range=12.0,
        effects={'slow': 0.5, 'duration': 3.0}
    ),
    'arcane_shield': Ability(
        id='arcane_shield',
        name='Arcane Shield',
        description='Create a protective barrier',
        damage_type=DamageType.MAGIC,
        base_damage=0,
        mana_cost=30,
        cooldown=20.0,
        range=0,
        effects={'shield': 50, 'duration': 8.0}
    ),

    # Ranger abilities
    'precise_shot': Ability(
        id='precise_shot',
        name='Precise Shot',
        description='A carefully aimed shot',
        damage_type=DamageType.PHYSICAL,
        base_damage=35,
        mana_cost=15,
        cooldown=4.0,
        range=20.0,
        effects={'crit_chance': 0.3}
    ),
    'evasive_roll': Ability(
        id='evasive_roll',
        name='Evasive Roll',
        description='Roll to dodge attacks',
        damage_type=DamageType.PHYSICAL,
        base_damage=0,
        mana_cost=10,
        cooldown=6.0,
        range=0,
        effects={'invincible': 0.5, 'move_boost': 2.0}
    ),
    'trap': Ability(
        id='trap',
        name='Trap',
        description='Place a trap that damages enemies',
        damage_type=DamageType.PHYSICAL,
        base_damage=20,
        mana_cost=15,
        cooldown=10.0,
        range=3.0,
        effects={'trap_duration': 30.0}
    ),

    # Healer abilities
    'heal': Ability(
        id='heal',
        name='Heal',
        description='Restore health to target',
        damage_type=DamageType.HOLY,
        base_damage=-40,  # Negative = healing
        mana_cost=25,
        cooldown=3.0,
        range=10.0
    ),
    'blessing': Ability(
        id='blessing',
        name='Blessing',
        description='Increase defense temporarily',
        damage_type=DamageType.HOLY,
        base_damage=0,
        mana_cost=20,
        cooldown=12.0,
        range=8.0,
        effects={'buff_defense': 1.5, 'duration': 15.0}
    ),
    'purify': Ability(
        id='purify',
        name='Purify',
        description='Remove negative effects',
        damage_type=DamageType.HOLY,
        base_damage=0,
        mana_cost=15,
        cooldown=8.0,
        range=8.0,
        effects={'cleanse': True}
    ),

    # Basic attack (all classes)
    'basic_attack': Ability(
        id='basic_attack',
        name='Attack',
        description='Basic attack',
        damage_type=DamageType.PHYSICAL,
        base_damage=10,
        mana_cost=0,
        cooldown=0.5,
        range=2.5
    )
}


@dataclass
class StatusEffect:
    """A status effect applied to a combatant."""
    name: str
    duration: float
    effect_type: str
    value: float
    remaining: float = 0.0

    def __post_init__(self):
        self.remaining = self.duration


class Combatant:
    """Base class for anything that can participate in combat."""

    def __init__(self, name: str, max_health: float, max_mana: float = 0):
        self.name = name
        self.max_health = max_health
        self.max_mana = max_mana
        self.health = max_health
        self.mana = max_mana

        self.attack_power = 10
        self.magic_power = 10
        self.defense = 5

        self.status_effects: List[StatusEffect] = []
        self.is_alive = True
        self.is_stunned = False

        # Combat callbacks
        self.on_damage_taken: Optional[Callable] = None
        self.on_death: Optional[Callable] = None

    def take_damage(self, amount: float, damage_type: DamageType) -> float:
        """Take damage, returns actual damage taken."""
        if not self.is_alive:
            return 0

        # Calculate defense reduction
        defense_mult = 1.0 - (self.defense / (self.defense + 50))
        actual_damage = amount * defense_mult

        # Check for shield effect
        for effect in self.status_effects:
            if effect.effect_type == 'shield':
                absorbed = min(effect.value, actual_damage)
                effect.value -= absorbed
                actual_damage -= absorbed
                if effect.value <= 0:
                    self.status_effects.remove(effect)

        self.health -= actual_damage

        if self.on_damage_taken:
            self.on_damage_taken(actual_damage, damage_type)

        if self.health <= 0:
            self.health = 0
            self.die()

        return actual_damage

    def heal(self, amount: float):
        """Heal the combatant."""
        self.health = min(self.max_health, self.health + amount)

    def apply_effect(self, effect: StatusEffect):
        """Apply a status effect."""
        # Check if effect already exists
        for existing in self.status_effects:
            if existing.name == effect.name:
                existing.remaining = effect.duration
                return

        self.status_effects.append(effect)

        if effect.effect_type == 'stun':
            self.is_stunned = True

    def update_effects(self, dt: float):
        """Update all status effects."""
        expired = []

        for effect in self.status_effects:
            effect.remaining -= dt
            if effect.remaining <= 0:
                expired.append(effect)

        for effect in expired:
            self.status_effects.remove(effect)
            if effect.effect_type == 'stun':
                self.is_stunned = False

    def die(self):
        """Handle death."""
        self.is_alive = False
        if self.on_death:
            self.on_death()

    def get_attack_multiplier(self) -> float:
        """Get attack multiplier from buffs."""
        mult = 1.0
        for effect in self.status_effects:
            if effect.effect_type == 'buff_attack':
                mult *= effect.value
        return mult

    def get_defense_multiplier(self) -> float:
        """Get defense multiplier from buffs."""
        mult = 1.0
        for effect in self.status_effects:
            if effect.effect_type == 'buff_defense':
                mult *= effect.value
        return mult


class CombatSystem:
    """Manages combat interactions."""

    def __init__(self):
        self.combatants: List[Combatant] = []
        self.player: Optional[Combatant] = None
        self.in_combat = False

        # Combat log
        self.combat_log: List[str] = []
        self.max_log_entries = 10

    def register_combatant(self, combatant: Combatant, is_player: bool = False):
        """Register a combatant in the combat system."""
        self.combatants.append(combatant)
        if is_player:
            self.player = combatant

    def unregister_combatant(self, combatant: Combatant):
        """Remove a combatant from the system."""
        if combatant in self.combatants:
            self.combatants.remove(combatant)

    def use_ability(self, user: Combatant, ability: Ability, target: Optional[Combatant] = None) -> bool:
        """Use an ability on a target."""
        # Check if ability is ready
        if not ability.is_ready():
            self.log(f"{ability.name} is on cooldown!")
            return False

        # Check mana cost
        if user.mana < ability.mana_cost:
            self.log(f"Not enough mana for {ability.name}!")
            return False

        # Use mana
        user.mana -= ability.mana_cost
        ability.use()

        # Calculate damage
        if ability.base_damage != 0:
            if ability.base_damage > 0:
                # Damage ability
                base = ability.base_damage
                if ability.damage_type == DamageType.PHYSICAL:
                    base += user.attack_power * 0.5
                else:
                    base += user.magic_power * 0.5

                base *= user.get_attack_multiplier()

                if target:
                    actual = target.take_damage(base, ability.damage_type)
                    self.log(f"{user.name} used {ability.name} on {target.name} for {int(actual)} damage!")

                    # Apply effects
                    self._apply_ability_effects(ability, target)
            else:
                # Healing ability
                heal_amount = abs(ability.base_damage) + user.magic_power * 0.3
                if target:
                    target.heal(heal_amount)
                    self.log(f"{user.name} healed {target.name} for {int(heal_amount)}!")
                else:
                    user.heal(heal_amount)
                    self.log(f"{user.name} healed self for {int(heal_amount)}!")
        else:
            # Buff/utility ability
            self._apply_ability_effects(ability, target or user)
            self.log(f"{user.name} used {ability.name}!")

        return True

    def _apply_ability_effects(self, ability: Ability, target: Combatant):
        """Apply ability effects to target."""
        effects = ability.effects
        duration = effects.get('duration', 5.0)

        if 'stun' in effects:
            target.apply_effect(StatusEffect('Stun', effects['stun'], 'stun', 1.0))

        if 'slow' in effects:
            target.apply_effect(StatusEffect('Slow', duration, 'slow', effects['slow']))

        if 'buff_attack' in effects:
            target.apply_effect(StatusEffect('Attack Buff', duration, 'buff_attack', effects['buff_attack']))

        if 'buff_defense' in effects:
            target.apply_effect(StatusEffect('Defense Buff', duration, 'buff_defense', effects['buff_defense']))

        if 'shield' in effects:
            target.apply_effect(StatusEffect('Shield', duration, 'shield', effects['shield']))

    def basic_attack(self, attacker: Combatant, target: Combatant) -> float:
        """Perform a basic attack."""
        if attacker.is_stunned:
            self.log(f"{attacker.name} is stunned!")
            return 0

        damage = attacker.attack_power * attacker.get_attack_multiplier()
        actual = target.take_damage(damage, DamageType.PHYSICAL)
        self.log(f"{attacker.name} attacks {target.name} for {int(actual)} damage!")
        return actual

    def update(self, dt: float):
        """Update combat system."""
        # Update all combatants' effects
        for combatant in self.combatants:
            combatant.update_effects(dt)

        # Update ability cooldowns
        for ability in ABILITIES.values():
            ability.update(dt)

    def log(self, message: str):
        """Add message to combat log."""
        self.combat_log.append(message)
        if len(self.combat_log) > self.max_log_entries:
            self.combat_log.pop(0)
        print(f"[Combat] {message}")

    def get_enemies_in_range(self, position: Vec3, range: float) -> List[Combatant]:
        """Get all enemies within range of a position."""
        enemies = []
        for combatant in self.combatants:
            if combatant != self.player and combatant.is_alive:
                # Would need entity position - simplified here
                enemies.append(combatant)
        return enemies
