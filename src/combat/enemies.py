"""Enemy types and AI behavior."""

from ursina import *
from dataclasses import dataclass
from typing import Optional, List, Dict
from enum import Enum
import random

from .system import Combatant, DamageType


class EnemyState(Enum):
    IDLE = "idle"
    PATROL = "patrol"
    CHASE = "chase"
    ATTACK = "attack"
    FLEE = "flee"
    DEAD = "dead"


@dataclass
class EnemyDrop:
    """Loot that can drop from enemies."""
    item_id: str
    name: str
    drop_chance: float  # 0.0 to 1.0


@dataclass
class EnemyType:
    """Definition of an enemy type."""
    id: str
    name: str
    max_health: float
    attack_power: float
    defense: float
    speed: float
    aggro_range: float
    attack_range: float
    attack_cooldown: float
    xp_reward: int
    gold_reward: tuple  # (min, max)
    drops: List[EnemyDrop]
    model_color: tuple = (150, 50, 50)


# Enemy type definitions
ENEMY_TYPES = {
    'slime': EnemyType(
        id='slime',
        name='Slime',
        max_health=30,
        attack_power=5,
        defense=2,
        speed=2,
        aggro_range=8,
        attack_range=1.5,
        attack_cooldown=2.0,
        xp_reward=15,
        gold_reward=(1, 5),
        drops=[
            EnemyDrop('slime_gel', 'Slime Gel', 0.5),
        ],
        model_color=(50, 200, 50)
    ),
    'goblin': EnemyType(
        id='goblin',
        name='Goblin',
        max_health=50,
        attack_power=10,
        defense=5,
        speed=4,
        aggro_range=12,
        attack_range=2.0,
        attack_cooldown=1.5,
        xp_reward=25,
        gold_reward=(5, 15),
        drops=[
            EnemyDrop('goblin_ear', 'Goblin Ear', 0.3),
            EnemyDrop('rusty_dagger', 'Rusty Dagger', 0.1),
        ],
        model_color=(100, 150, 50)
    ),
    'wolf': EnemyType(
        id='wolf',
        name='Wild Wolf',
        max_health=40,
        attack_power=12,
        defense=3,
        speed=6,
        aggro_range=15,
        attack_range=2.5,
        attack_cooldown=1.2,
        xp_reward=20,
        gold_reward=(0, 3),
        drops=[
            EnemyDrop('wolf_pelt', 'Wolf Pelt', 0.4),
            EnemyDrop('wolf_fang', 'Wolf Fang', 0.2),
        ],
        model_color=(100, 100, 100)
    ),
    'skeleton': EnemyType(
        id='skeleton',
        name='Skeleton',
        max_health=45,
        attack_power=15,
        defense=8,
        speed=3,
        aggro_range=10,
        attack_range=2.0,
        attack_cooldown=1.8,
        xp_reward=30,
        gold_reward=(3, 12),
        drops=[
            EnemyDrop('bone', 'Bone', 0.6),
            EnemyDrop('ancient_coin', 'Ancient Coin', 0.15),
        ],
        model_color=(220, 220, 200)
    ),
    'troll': EnemyType(
        id='troll',
        name='Forest Troll',
        max_health=150,
        attack_power=25,
        defense=15,
        speed=2,
        aggro_range=8,
        attack_range=3.0,
        attack_cooldown=3.0,
        xp_reward=75,
        gold_reward=(20, 50),
        drops=[
            EnemyDrop('troll_blood', 'Troll Blood', 0.5),
            EnemyDrop('troll_club', 'Troll Club', 0.1),
        ],
        model_color=(80, 120, 80)
    ),
}


class Enemy(Entity):
    """An enemy entity in the game world."""

    def __init__(self, enemy_type: EnemyType, position=(0, 0, 0), **kwargs):
        super().__init__(
            model='cube',
            color=color.rgb(*enemy_type.model_color),
            scale=(1, 1.5, 1),
            position=position,
            collider='box'
        )

        self.enemy_type = enemy_type
        self.combatant = Combatant(
            name=enemy_type.name,
            max_health=enemy_type.max_health
        )
        self.combatant.attack_power = enemy_type.attack_power
        self.combatant.defense = enemy_type.defense

        # AI state
        self.state = EnemyState.IDLE
        self.target: Optional[Entity] = None
        self.spawn_position = Vec3(position)
        self.patrol_points: List[Vec3] = []
        self.current_patrol_index = 0

        # Combat state
        self.attack_cooldown = 0
        self.last_damage_time = 0

        # Movement
        self.speed = enemy_type.speed
        self.velocity = Vec3(0, 0, 0)

        # Name tag
        self.name_tag = Text(
            text=enemy_type.name,
            parent=self,
            y=1.5,
            scale=8,
            billboard=True,
            origin=(0, 0),
            color=color.rgb(255, 100, 100)
        )

        # Health bar background
        self.health_bar_bg = Entity(
            parent=self,
            model='quad',
            color=color.rgb(60, 20, 20),
            scale=(1.5, 0.1),
            y=1.2,
            billboard=True
        )

        # Health bar
        self.health_bar = Entity(
            parent=self,
            model='quad',
            color=color.rgb(200, 50, 50),
            scale=(1.5, 0.1),
            y=1.2,
            billboard=True,
            origin=(-0.5, 0)
        )

        # Death callback
        self.combatant.on_death = self.on_death
        self.combatant.on_damage_taken = self.on_damage_taken

        # Drops on death
        self.drops_given = False

    def update(self):
        if not self.combatant.is_alive:
            return

        # Update health bar
        health_ratio = self.combatant.health / self.combatant.max_health
        self.health_bar.scale_x = 1.5 * health_ratio

        # Update attack cooldown
        if self.attack_cooldown > 0:
            self.attack_cooldown -= time.dt

        # Update combatant effects
        self.combatant.update_effects(time.dt)

        # State machine
        if self.state == EnemyState.IDLE:
            self.update_idle()
        elif self.state == EnemyState.PATROL:
            self.update_patrol()
        elif self.state == EnemyState.CHASE:
            self.update_chase()
        elif self.state == EnemyState.ATTACK:
            self.update_attack()
        elif self.state == EnemyState.FLEE:
            self.update_flee()

    def update_idle(self):
        """Idle behavior - look for targets."""
        if self.target:
            distance = (self.target.position - self.position).length()
            if distance < self.enemy_type.aggro_range:
                self.state = EnemyState.CHASE
        else:
            # Random chance to start patrolling
            if random.random() < 0.001:
                self.state = EnemyState.PATROL

    def update_patrol(self):
        """Patrol behavior."""
        if not self.patrol_points:
            # Generate patrol points around spawn
            self.patrol_points = [
                self.spawn_position + Vec3(random.uniform(-5, 5), 0, random.uniform(-5, 5))
                for _ in range(3)
            ]

        target_point = self.patrol_points[self.current_patrol_index]
        direction = (target_point - self.position)
        direction.y = 0

        if direction.length() < 0.5:
            self.current_patrol_index = (self.current_patrol_index + 1) % len(self.patrol_points)
        else:
            direction = direction.normalized()
            self.position += direction * self.speed * 0.5 * time.dt

        # Check for target
        if self.target:
            distance = (self.target.position - self.position).length()
            if distance < self.enemy_type.aggro_range:
                self.state = EnemyState.CHASE

    def update_chase(self):
        """Chase the target."""
        if not self.target:
            self.state = EnemyState.IDLE
            return

        distance = (self.target.position - self.position).length()

        # Check if target escaped
        if distance > self.enemy_type.aggro_range * 1.5:
            self.state = EnemyState.IDLE
            return

        # Check if in attack range
        if distance < self.enemy_type.attack_range:
            self.state = EnemyState.ATTACK
            return

        # Move towards target
        direction = (self.target.position - self.position)
        direction.y = 0
        if direction.length() > 0:
            direction = direction.normalized()
            self.position += direction * self.speed * time.dt

        # Face target
        self.look_at(self.target.position)
        self.rotation_x = 0
        self.rotation_z = 0

    def update_attack(self):
        """Attack the target."""
        if not self.target:
            self.state = EnemyState.IDLE
            return

        distance = (self.target.position - self.position).length()

        # Check if target moved out of range
        if distance > self.enemy_type.attack_range * 1.2:
            self.state = EnemyState.CHASE
            return

        # Attack if cooldown ready
        if self.attack_cooldown <= 0:
            self.perform_attack()
            self.attack_cooldown = self.enemy_type.attack_cooldown

    def update_flee(self):
        """Flee from target (low health behavior)."""
        if not self.target:
            self.state = EnemyState.IDLE
            return

        # Move away from target
        direction = (self.position - self.target.position)
        direction.y = 0
        if direction.length() > 0:
            direction = direction.normalized()
            self.position += direction * self.speed * 1.5 * time.dt

        # Check if safe distance
        distance = (self.target.position - self.position).length()
        if distance > self.enemy_type.aggro_range * 2:
            self.state = EnemyState.IDLE

    def perform_attack(self):
        """Perform an attack on the target."""
        if self.target and hasattr(self.target, 'take_damage'):
            damage = self.combatant.attack_power * self.combatant.get_attack_multiplier()
            self.target.take_damage(damage)
            print(f"{self.enemy_type.name} attacks for {int(damage)} damage!")

    def on_damage_taken(self, amount: float, damage_type: DamageType):
        """Called when enemy takes damage."""
        self.last_damage_time = time.time()

        # Flash red
        self.color = color.rgb(255, 100, 100)
        invoke(self.reset_color, delay=0.1)

        # Check if should flee (low health)
        if self.combatant.health < self.combatant.max_health * 0.2:
            if random.random() < 0.3:
                self.state = EnemyState.FLEE

    def reset_color(self):
        """Reset color after damage flash."""
        if self.combatant.is_alive:
            self.color = color.rgb(*self.enemy_type.model_color)

    def on_death(self):
        """Called when enemy dies."""
        self.state = EnemyState.DEAD
        self.collider = None

        # Death animation
        self.animate_scale((1, 0.1, 1), duration=0.5)
        self.animate_color(color.rgb(50, 50, 50), duration=0.5)

        # Give drops
        if not self.drops_given:
            self.drops_given = True
            self.give_drops()

        # Destroy after delay
        invoke(self.cleanup, delay=2.0)

    def give_drops(self) -> Dict:
        """Calculate and return drops."""
        drops = {
            'xp': self.enemy_type.xp_reward,
            'gold': random.randint(*self.enemy_type.gold_reward),
            'items': []
        }

        for drop in self.enemy_type.drops:
            if random.random() < drop.drop_chance:
                drops['items'].append(drop.name)

        print(f"Defeated {self.enemy_type.name}! +{drops['xp']} XP, +{drops['gold']} gold")
        if drops['items']:
            print(f"Dropped: {', '.join(drops['items'])}")

        return drops

    def cleanup(self):
        """Clean up the enemy entity."""
        destroy(self.name_tag)
        destroy(self.health_bar_bg)
        destroy(self.health_bar)
        destroy(self)

    def set_target(self, target: Entity):
        """Set the enemy's target."""
        self.target = target


class EnemySpawner:
    """Manages enemy spawning in the world."""

    def __init__(self):
        self.enemies: List[Enemy] = []
        self.spawn_points: List[Dict] = []
        self.max_enemies = 20
        self.spawn_timer = 0
        self.spawn_interval = 10.0

    def add_spawn_point(self, position: Vec3, enemy_types: List[str], max_count: int = 3):
        """Add a spawn point."""
        self.spawn_points.append({
            'position': position,
            'enemy_types': enemy_types,
            'max_count': max_count,
            'current_count': 0
        })

    def update(self, dt: float, player_position: Vec3):
        """Update spawner."""
        self.spawn_timer += dt

        if self.spawn_timer >= self.spawn_interval:
            self.spawn_timer = 0
            self.try_spawn(player_position)

        # Clean up dead enemies
        self.enemies = [e for e in self.enemies if e.combatant.is_alive]

    def try_spawn(self, player_position: Vec3):
        """Try to spawn enemies at spawn points."""
        if len(self.enemies) >= self.max_enemies:
            return

        for spawn_point in self.spawn_points:
            # Check if player is too close
            distance = (spawn_point['position'] - player_position).length()
            if distance < 15:
                continue

            # Check if spawn point is at capacity
            if spawn_point['current_count'] >= spawn_point['max_count']:
                continue

            # Spawn enemy
            enemy_type_id = random.choice(spawn_point['enemy_types'])
            if enemy_type_id in ENEMY_TYPES:
                enemy_type = ENEMY_TYPES[enemy_type_id]
                spawn_pos = spawn_point['position'] + Vec3(
                    random.uniform(-3, 3),
                    0,
                    random.uniform(-3, 3)
                )
                enemy = Enemy(enemy_type, position=spawn_pos)
                self.enemies.append(enemy)
                spawn_point['current_count'] += 1

    def get_nearest_enemy(self, position: Vec3, max_range: float = 50) -> Optional[Enemy]:
        """Get the nearest enemy to a position."""
        nearest = None
        nearest_dist = max_range

        for enemy in self.enemies:
            if not enemy.combatant.is_alive:
                continue
            dist = (enemy.position - position).length()
            if dist < nearest_dist:
                nearest_dist = dist
                nearest = enemy

        return nearest

    def set_player_target(self, player: Entity):
        """Set player as target for all enemies."""
        for enemy in self.enemies:
            enemy.set_target(player)
