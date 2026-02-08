"""Pet system with starter pets and abilities."""

from ursina import *
from dataclasses import dataclass, field
from typing import Optional, List, Dict
from enum import Enum
import random

import config


class PetState(Enum):
    IDLE = "idle"
    FOLLOW = "follow"
    PLAYING = "playing"
    ABILITY = "ability"
    RESTING = "resting"


@dataclass
class PetAbility:
    """An ability a pet can use."""
    id: str
    name: str
    description: str
    cooldown: float
    effect_type: str  # 'combat', 'utility', 'buff'
    effect_value: float


@dataclass
class PetType:
    """Definition for a pet type."""
    id: str
    name: str
    description: str
    pet_class: str  # 'combat', 'utility', 'defense'
    base_stats: Dict[str, int]
    abilities: List[PetAbility]
    model_scale: tuple = (0.5, 0.5, 0.5)
    model_color: tuple = (200, 200, 200)
    personality_traits: List[str] = field(default_factory=list)


# Define pet abilities
PET_ABILITIES = {
    # Wolf abilities
    'bite': PetAbility('bite', 'Bite', 'Attack an enemy', 3.0, 'combat', 15),
    'howl': PetAbility('howl', 'Howl', 'Buff party attack', 30.0, 'buff', 1.2),

    # Owl abilities
    'scout': PetAbility('scout', 'Scout', 'Reveal nearby enemies', 20.0, 'utility', 30),
    'detect_treasure': PetAbility('detect_treasure', 'Detect Treasure', 'Find nearby loot', 45.0, 'utility', 20),

    # Turtle abilities
    'shell_shield': PetAbility('shell_shield', 'Shell Shield', 'Protect owner', 25.0, 'defense', 20),
    'taunt': PetAbility('taunt', 'Taunt', 'Draw enemy attention', 15.0, 'defense', 5),
}

# Define starter pet types from config
STARTER_PET_TYPES = {}
for pet_id, pet_data in config.STARTER_PETS.items():
    abilities = [PET_ABILITIES[a] for a in pet_data['abilities'] if a in PET_ABILITIES]
    STARTER_PET_TYPES[pet_id] = PetType(
        id=pet_id,
        name=pet_data['name'],
        description=pet_data['description'],
        pet_class=pet_data['type'],
        base_stats=pet_data['base_stats'],
        abilities=abilities,
        model_color={
            'wolf': (100, 100, 120),
            'owl': (180, 150, 100),
            'turtle': (80, 150, 80),
        }.get(pet_id, (200, 200, 200)),
        personality_traits={
            'wolf': ['loyal', 'fierce', 'protective'],
            'owl': ['wise', 'curious', 'patient'],
            'turtle': ['calm', 'steady', 'resilient'],
        }.get(pet_id, [])
    )


class Pet(Entity):
    """A pet companion that bonds with the player."""

    def __init__(self, pet_type: PetType, owner: Entity, **kwargs):
        # Choose model based on pet type
        # First try to load custom 3D models from __pycache__/assets/models folder
        custom_models = {
            'wolf': '__pycache__/assets/models/10055_Gray_Wolf_v1_L3',  # Will use the gray wolf OBJ model
            'owl': '__pycache__/assets/models/owl',
            'turtle': '__pycache__/assets/models/turtle',
        }
        
        # Fallback to basic shapes if custom model not found
        fallback_models = {
            'wolf': 'cube',
            'owl': 'sphere',
            'turtle': 'cube',
        }
        
        # Try to load custom model first
        model_to_use = fallback_models.get(pet_type.id, 'cube')
        custom_path = custom_models.get(pet_type.id)
        
        if custom_path:
            try:
                print(f"Attempting to load pet model: {custom_path}")
                # Try to load the model - Ursina will automatically look for .obj extension
                from pathlib import Path
                import os
                full_path = Path(custom_path + '.obj')
                if full_path.exists():
                    print(f"Found model file: {full_path}")
                    model_to_use = custom_path
                else:
                    print(f"Model file not found: {full_path}")
            except Exception as e:
                print(f"Error loading pet model: {e}")
                pass  # Fall back to basic shape

        super().__init__(
            model=model_to_use,
            color=color.rgb(*pet_type.model_color),
            scale=pet_type.model_scale,
            collider='box'
        )

        self.pet_type = pet_type
        self.owner = owner

        # Pet stats
        self.level = 1
        self.experience = 0
        self.exp_to_level = 50

        self.stats = pet_type.base_stats.copy()
        self.max_health = 30 + self.stats['defense'] * 2
        self.health = self.max_health

        # Bonding
        self.bond_level = 0  # 0-100
        self.happiness = 50  # 0-100
        self.last_interaction = time.time()

        # State
        self.state = PetState.FOLLOW
        self.target = None

        # Abilities
        self.ability_cooldowns: Dict[str, float] = {a.id: 0 for a in pet_type.abilities}

        # Movement
        self.speed = 4 + self.stats['speed'] * 0.3
        self.follow_distance = 2.0

        # Animation state
        self.bob_offset = 0
        self.is_bouncing = False

        # Pet name (can be customized)
        self.nickname = pet_type.name

        # Name tag
        self.name_tag = Text(
            text=self.nickname,
            parent=self,
            y=0.8,
            scale=6,
            billboard=True,
            origin=(0, 0),
            color=color.rgb(255, 220, 100)
        )

        # Position near owner
        if hasattr(owner, 'position'):
            self.position = owner.position + Vec3(-1.5, 0, -1.5)

    def update(self):
        # Update cooldowns
        for ability_id in self.ability_cooldowns:
            if self.ability_cooldowns[ability_id] > 0:
                self.ability_cooldowns[ability_id] -= time.dt

        # Happiness decay
        time_since_interact = time.time() - self.last_interaction
        if time_since_interact > 300:  # 5 minutes
            self.happiness = max(0, self.happiness - 0.01)

        # State behavior
        if self.state == PetState.FOLLOW:
            self._follow_owner()
        elif self.state == PetState.PLAYING:
            self._play_animation()
        elif self.state == PetState.ABILITY:
            pass  # Ability in progress

        # Idle animations
        self._idle_animation()

    def _follow_owner(self):
        """Follow the owner."""
        if not self.owner or not hasattr(self.owner, 'position'):
            return

        owner_pos = self.owner.position
        distance = (owner_pos - self.position).length()

        if distance > self.follow_distance:
            direction = (owner_pos - self.position)
            direction.y = 0
            if direction.length() > 0:
                direction = direction.normalized()
                # Add some offset to not be directly behind
                offset = Vec3(-1, 0, -1).normalized()
                target_direction = (direction + offset * 0.3).normalized()
                self.position += target_direction * self.speed * time.dt

        # Keep on ground
        self.y = 0.25

    def _idle_animation(self):
        """Simple idle bobbing animation."""
        self.bob_offset += time.dt * 3
        bob = math.sin(self.bob_offset) * 0.05
        self.y = 0.25 + bob

    def _play_animation(self):
        """Play animation when happy."""
        if not self.is_bouncing:
            self.is_bouncing = True
            self.animate_y(0.8, duration=0.3, curve=curve.out_quad)
            invoke(self._bounce_down, delay=0.3)

    def _bounce_down(self):
        """Complete bounce animation."""
        self.animate_y(0.25, duration=0.2, curve=curve.in_quad)
        self.is_bouncing = False
        if self.state == PetState.PLAYING:
            invoke(self._play_animation, delay=0.5)

    def interact(self):
        """Player interacts with pet."""
        self.last_interaction = time.time()
        self.increase_happiness(5)
        self.increase_bond(1)

        # React based on happiness
        if self.happiness > 70:
            self.state = PetState.PLAYING
            invoke(lambda: setattr(self, 'state', PetState.FOLLOW), delay=3.0)
            print(f"{self.nickname} is happy to see you!")
        elif self.happiness > 30:
            print(f"{self.nickname} wags their tail.")
        else:
            print(f"{self.nickname} seems a bit down...")

    def feed(self):
        """Feed the pet."""
        self.increase_happiness(15)
        self.increase_bond(3)
        self.last_interaction = time.time()
        print(f"{self.nickname} enjoyed the treat!")

    def use_ability(self, ability_id: str, target=None) -> bool:
        """Use a pet ability."""
        # Find ability
        ability = None
        for a in self.pet_type.abilities:
            if a.id == ability_id:
                ability = a
                break

        if not ability:
            print(f"{self.nickname} doesn't know that ability!")
            return False

        # Check cooldown
        if self.ability_cooldowns[ability_id] > 0:
            remaining = int(self.ability_cooldowns[ability_id])
            print(f"{ability.name} is on cooldown! ({remaining}s)")
            return False

        # Use ability
        self.ability_cooldowns[ability_id] = ability.cooldown

        if ability.effect_type == 'combat':
            if target and hasattr(target, 'combatant'):
                damage = ability.effect_value + self.stats['attack']
                target.combatant.take_damage(damage, None)
                print(f"{self.nickname} uses {ability.name}! Deals {int(damage)} damage!")
            else:
                print(f"{self.nickname} uses {ability.name}!")

        elif ability.effect_type == 'buff':
            print(f"{self.nickname} uses {ability.name}! Party attack increased!")

        elif ability.effect_type == 'defense':
            print(f"{self.nickname} uses {ability.name}!")

        elif ability.effect_type == 'utility':
            print(f"{self.nickname} uses {ability.name}!")
            # Reveal enemies or treasure
            if ability_id == 'scout':
                print("Enemies revealed on minimap!")
            elif ability_id == 'detect_treasure':
                print("Nearby treasures highlighted!")

        # Gain experience for using abilities
        self.gain_experience(5)

        return True

    def gain_experience(self, amount: int):
        """Gain experience points."""
        self.experience += amount

        while self.experience >= self.exp_to_level:
            self.experience -= self.exp_to_level
            self.level_up()

    def level_up(self):
        """Level up the pet."""
        self.level += 1
        self.exp_to_level = int(self.exp_to_level * 1.5)

        # Increase stats
        self.stats['attack'] += 2
        self.stats['defense'] += 1
        self.stats['speed'] += 1

        # Increase health
        self.max_health += 5
        self.health = self.max_health

        print(f"{self.nickname} leveled up to level {self.level}!")

    def increase_happiness(self, amount: int):
        """Increase happiness."""
        self.happiness = min(100, self.happiness + amount)

    def decrease_happiness(self, amount: int):
        """Decrease happiness."""
        self.happiness = max(0, self.happiness - amount)

    def increase_bond(self, amount: int):
        """Increase bond level."""
        self.bond_level = min(100, self.bond_level + amount)

        # Unlock bonuses at certain levels
        if self.bond_level >= 25 and self.bond_level - amount < 25:
            print(f"Bond with {self.nickname} reached level 25! Abilities are stronger!")
        if self.bond_level >= 50 and self.bond_level - amount < 50:
            print(f"Bond with {self.nickname} reached level 50! New ability unlocked!")
        if self.bond_level >= 100 and self.bond_level - amount < 100:
            print(f"Maximum bond with {self.nickname}! You are inseparable!")

    def rename(self, new_name: str):
        """Rename the pet."""
        old_name = self.nickname
        self.nickname = new_name
        self.name_tag.text = new_name
        print(f"{old_name} is now called {new_name}!")

    def get_bond_multiplier(self) -> float:
        """Get ability effectiveness based on bond."""
        return 1.0 + (self.bond_level / 200)  # 1.0 to 1.5

    def to_dict(self) -> Dict:
        """Serialize pet data."""
        return {
            'pet_type_id': self.pet_type.id,
            'nickname': self.nickname,
            'level': self.level,
            'experience': self.experience,
            'stats': self.stats,
            'bond_level': self.bond_level,
            'happiness': self.happiness,
        }

    @classmethod
    def from_dict(cls, data: Dict, owner: Entity) -> 'Pet':
        """Deserialize pet data."""
        pet_type = STARTER_PET_TYPES.get(data['pet_type_id'])
        if not pet_type:
            return None

        pet = cls(pet_type, owner)
        pet.nickname = data['nickname']
        pet.name_tag.text = pet.nickname
        pet.level = data['level']
        pet.experience = data['experience']
        pet.stats = data['stats']
        pet.bond_level = data['bond_level']
        pet.happiness = data['happiness']
        return pet


class PetSelectionUI(Entity):
    """UI for selecting a starter pet."""

    def __init__(self, on_select_callback):
        super().__init__(parent=camera.ui)
        self.on_select_callback = on_select_callback
        self.selected_pet = None

        # Background
        self.background = Entity(
            parent=self,
            model='quad',
            color=color.rgba(0, 0, 0, 220),
            scale=(2, 2),
            z=1
        )

        # Title
        self.title = Text(
            parent=self,
            text='Choose Your Starter Pet',
            scale=2.5,
            origin=(0, 0),
            y=0.35,
            color=color.rgb(255, 220, 100)
        )

        # Pet cards
        self.pet_cards = []
        pets = list(STARTER_PET_TYPES.values())
        start_x = -0.4
        spacing = 0.4

        for i, pet_type in enumerate(pets):
            card = self._create_pet_card(pet_type, start_x + (i * spacing))
            self.pet_cards.append(card)

        # Confirm button (hidden until selection)
        self.confirm_button = Button(
            parent=self,
            text='CONFIRM',
            scale=(0.25, 0.07),
            y=-0.38,
            color=color.rgb(60, 120, 60),
            highlight_color=color.rgb(80, 180, 80),
            on_click=self.confirm_selection,
            visible=False
        )

    def _create_pet_card(self, pet_type: PetType, x_pos: float) -> Dict:
        """Create a card for a pet type."""
        card = {}

        # Card background
        card['bg'] = Button(
            parent=self,
            model='quad',
            color=color.rgb(50, 50, 70),
            highlight_color=color.rgb(70, 70, 100),
            scale=(0.35, 0.55),
            position=(x_pos, -0.05),
            on_click=Func(self.select_pet, pet_type)
        )

        # Pet preview (colored shape)
        model_map = {'wolf': 'cube', 'owl': 'sphere', 'turtle': 'cube'}
        card['preview'] = Entity(
            parent=card['bg'],
            model=model_map.get(pet_type.id, 'cube'),
            color=color.rgb(*pet_type.model_color),
            scale=(0.3, 0.3, 0.3),
            y=0.25,
            rotation_y=time.time() * 50  # Will rotate
        )

        # Pet name
        card['name'] = Text(
            parent=card['bg'],
            text=pet_type.name,
            scale=4,
            origin=(0, 0),
            y=0.05,
            color=color.rgb(255, 220, 100)
        )

        # Pet type
        card['type'] = Text(
            parent=card['bg'],
            text=f"[{pet_type.pet_class.upper()}]",
            scale=2.5,
            origin=(0, 0),
            y=-0.05,
            color=color.rgb(150, 150, 180)
        )

        # Description
        card['desc'] = Text(
            parent=card['bg'],
            text=pet_type.description,
            scale=2,
            origin=(0, 0),
            y=-0.2,
            color=color.rgb(180, 180, 180),
            wordwrap=15
        )

        # Stats
        stats_text = f"ATK:{pet_type.base_stats['attack']} DEF:{pet_type.base_stats['defense']} SPD:{pet_type.base_stats['speed']}"
        card['stats'] = Text(
            parent=card['bg'],
            text=stats_text,
            scale=2,
            origin=(0, 0),
            y=-0.38,
            color=color.rgb(100, 200, 100)
        )

        card['pet_type'] = pet_type
        return card

    def select_pet(self, pet_type: PetType):
        """Select a pet."""
        self.selected_pet = pet_type

        # Update card visuals
        for card in self.pet_cards:
            if card['pet_type'] == pet_type:
                card['bg'].color = color.rgb(80, 100, 80)
            else:
                card['bg'].color = color.rgb(50, 50, 70)

        # Show confirm button
        self.confirm_button.visible = True

    def confirm_selection(self):
        """Confirm pet selection."""
        if self.selected_pet:
            self.destroy()
            self.on_select_callback(self.selected_pet)

    def update(self):
        """Rotate pet previews."""
        for card in self.pet_cards:
            if 'preview' in card:
                card['preview'].rotation_y += time.dt * 50

    def destroy(self):
        """Clean up UI."""
        destroy(self.background)
        destroy(self.title)
        for card in self.pet_cards:
            destroy(card['bg'])
        destroy(self.confirm_button)
        destroy(self)
