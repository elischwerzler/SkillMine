#!/usr/bin/env python3
"""
SkillMine - A 3D Roleplay Game
"""

from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from ursina.shaders import unlit_shader
import random
from math import radians

# Use unlit shader to show colors without lighting
Entity.default_shader = unlit_shader

import config
from src.ui.login_screen import LoginScreen
from src.ui.main_menu import MainMenu
from src.ui.character_creator import CharacterCreator
from src.player.character import Character


class DungeonPortal(Entity):
    """Portal to enter dungeons."""
    def __init__(self, dungeon_level, position, **kwargs):
        # Portal colors based on difficulty
        portal_colors = {
            1: color.lime, 2: color.green, 3: color.cyan,
            4: color.azure, 5: color.blue, 6: color.violet,
            7: color.magenta, 8: color.orange, 9: color.red,
            10: color.black
        }
        portal_col = portal_colors.get(dungeon_level, color.cyan)

        super().__init__(
            model='cube',
            texture='white_cube',
            color=portal_col,
            scale=(4, 5, 0.3),
            position=position,
            collider='box'
        )
        self.dungeon_level = dungeon_level
        self.portal_color = portal_col
        self.cooldown = 0

        # Portal frame
        Entity(parent=self, model='cube', texture='white_cube',
               color=color.dark_gray, scale=(1.15, 1.08, 1.5), position=(0, 0, 0))

        # Inner glow
        Entity(parent=self, model='cube', texture='white_cube',
               color=portal_col, scale=(0.9, 0.92, 0.5), position=(0, 0, 0.2))

        # Dungeon name
        Text(text=f'Dungeon {dungeon_level}', parent=self, y=1.8, scale=14,
             billboard=True, origin=(0, 0), color=color.white)

        # Difficulty indicator
        difficulty = ['Easy', 'Easy', 'Normal', 'Normal', 'Hard',
                      'Hard', 'Very Hard', 'Very Hard', 'Extreme', 'NIGHTMARE'][dungeon_level - 1]
        Text(text=f'[{difficulty}]', parent=self, y=1.4, scale=10,
             billboard=True, origin=(0, 0), color=portal_col)

        Text(text='[E] Enter', parent=self, y=1.0, scale=8,
             billboard=True, origin=(0, 0), color=color.light_gray)

    def update(self):
        pulse = 0.6 + 0.4 * sin(time.time() * 2 + self.dungeon_level)
        self.color = self.portal_color * pulse
        if self.cooldown > 0:
            self.cooldown -= time.dt


class SecretDungeonPortal(Entity):
    """Hidden portal to secret biome dungeons with exclusive loot."""
    def __init__(self, biome_name, position, biome_color, difficulty=5, **kwargs):
        super().__init__(
            model='sphere',
            texture='white_cube',
            color=biome_color,
            scale=(2, 3, 2),
            position=position,
            collider='box'
        )
        self.biome_name = biome_name
        self.portal_color = biome_color
        self.difficulty = difficulty
        self.cooldown = 0

        # Mystical swirl effect
        Entity(parent=self, model='sphere', texture='white_cube',
               color=color.white, scale=(0.6, 0.8, 0.6), position=(0, 0, 0))

        # Floating runes around portal
        for i in range(4):
            angle = i * 90
            rune = Entity(parent=self, model='cube', texture='white_cube',
                          color=biome_color, scale=(0.3, 0.3, 0.1))
            rune.x = sin(radians(angle)) * 1.5
            rune.z = cos(radians(angle)) * 1.5

        # Secret dungeon name
        Text(text=f'Secret {biome_name} Dungeon', parent=self, y=2.5, scale=10,
             billboard=True, origin=(0, 0), color=color.gold)

        Text(text='[HIDDEN]', parent=self, y=2.0, scale=8,
             billboard=True, origin=(0, 0), color=biome_color)

        Text(text='[E] Enter', parent=self, y=1.5, scale=8,
             billboard=True, origin=(0, 0), color=color.light_gray)

    def update(self):
        # Magical pulsing and rotation effect
        pulse = 0.7 + 0.3 * sin(time.time() * 3)
        self.color = self.portal_color * pulse
        self.rotation_y += time.dt * 30
        if self.cooldown > 0:
            self.cooldown -= time.dt


# Secret loot that only drops from secret dungeons
SECRET_LOOT = {
    'Frozen Tundra': [
        {'name': 'Frostbite Blade', 'type': 'weapon', 'weapon_type': 'sword', 'damage': 200, 'rarity': 'legendary', 'color': color.cyan},
        {'name': 'Glacial Staff', 'type': 'weapon', 'weapon_type': 'staff', 'damage': 50, 'mana_bonus': 80, 'rarity': 'legendary', 'color': color.azure, 'projectile': True, 'pierce': 8, 'debuff': 'slow', 'debuff_value': 60},
        {'name': 'Frozen Heart Amulet', 'type': 'accessory', 'hp_bonus': 200, 'defense_bonus': 50, 'rarity': 'legendary'},
    ],
    'Desert Wasteland': [
        {'name': 'Sandstorm Scimitar', 'type': 'weapon', 'weapon_type': 'sword', 'damage': 220, 'rarity': 'legendary', 'color': color.gold},
        {'name': 'Pharaoh\'s Staff', 'type': 'weapon', 'weapon_type': 'staff', 'damage': 55, 'mana_bonus': 70, 'rarity': 'legendary', 'color': color.gold, 'projectile': True, 'pierce': 7, 'debuff': 'curse', 'debuff_value': 50},
        {'name': 'Scarab Pendant', 'type': 'accessory', 'hp_bonus': 150, 'attack_bonus': 40, 'rarity': 'legendary'},
    ],
    'Dark Swamp': [
        {'name': 'Venomfang Dagger', 'type': 'weapon', 'weapon_type': 'dagger', 'damage': 180, 'rarity': 'legendary', 'color': color.green},
        {'name': 'Witch\'s Curse Staff', 'type': 'weapon', 'weapon_type': 'staff', 'damage': 45, 'mana_bonus': 90, 'rarity': 'legendary', 'color': color.violet, 'projectile': True, 'pierce': 10, 'debuff': 'poison', 'debuff_value': 40},
        {'name': 'Swamp King\'s Crown', 'type': 'accessory', 'hp_bonus': 180, 'mana_bonus': 100, 'rarity': 'legendary'},
    ],
    'Volcanic Hellscape': [
        {'name': 'Inferno Greatsword', 'type': 'weapon', 'weapon_type': 'sword', 'damage': 280, 'rarity': 'legendary', 'color': color.red},
        {'name': 'Magma Core Staff', 'type': 'weapon', 'weapon_type': 'staff', 'damage': 70, 'mana_bonus': 60, 'rarity': 'legendary', 'color': color.orange, 'projectile': True, 'pierce': 6, 'debuff': 'poison', 'debuff_value': 60},
        {'name': 'Dragon Scale Armor', 'type': 'armor', 'defense': 80, 'hp_bonus': 250, 'rarity': 'legendary'},
    ],
    'Fantasy Land': [
        {'name': 'Fairy Queen\'s Rapier', 'type': 'weapon', 'weapon_type': 'sword', 'damage': 240, 'rarity': 'legendary', 'color': color.magenta},
        {'name': 'Starlight Wand', 'type': 'weapon', 'weapon_type': 'staff', 'damage': 60, 'mana_bonus': 100, 'rarity': 'legendary', 'color': color.white, 'projectile': True, 'pierce': 12, 'debuff': 'slow', 'debuff_value': 50},
        {'name': 'Unicorn Horn Ring', 'type': 'accessory', 'hp_bonus': 300, 'mana_bonus': 150, 'attack_bonus': 30, 'rarity': 'legendary'},
    ],
}


# 35 UNIQUE ENEMY TYPES - Higher HP for challenge, XP based on difficulty
ENEMY_TYPES = {
    # DUNGEON 1-2 (Easy) - Basic enemies
    'Slime': {'hp': 60, 'xp': 15, 'color': color.lime, 'speed': 1.5, 'scale': (0.8, 0.6, 0.8), 'dungeons': [1, 2]},
    'Green Slime': {'hp': 75, 'xp': 18, 'color': color.green, 'speed': 1.8, 'scale': (0.9, 0.7, 0.9), 'dungeons': [1, 2]},
    'Rat': {'hp': 50, 'xp': 12, 'color': color.brown, 'speed': 3, 'scale': (0.5, 0.3, 0.8), 'dungeons': [1, 2]},
    'Bat': {'hp': 40, 'xp': 10, 'color': color.dark_gray, 'speed': 4, 'scale': (0.6, 0.3, 0.6), 'dungeons': [1, 2]},
    'Mushroom': {'hp': 90, 'xp': 22, 'color': color.red, 'speed': 0.8, 'scale': (0.7, 1.0, 0.7), 'dungeons': [1, 2]},

    # DUNGEON 3-4 (Normal)
    'Goblin': {'hp': 120, 'xp': 30, 'color': color.olive, 'speed': 2.5, 'scale': (0.7, 1.0, 0.7), 'dungeons': [3, 4]},
    'Goblin Archer': {'hp': 90, 'xp': 25, 'color': color.dark_gray, 'speed': 2, 'scale': (0.7, 1.0, 0.7), 'dungeons': [3, 4]},
    'Wolf': {'hp': 130, 'xp': 32, 'color': color.gray, 'speed': 3.5, 'scale': (1.0, 0.8, 1.5), 'dungeons': [3, 4]},
    'Spider': {'hp': 100, 'xp': 28, 'color': color.black, 'speed': 3, 'scale': (1.2, 0.5, 1.2), 'dungeons': [3, 4]},
    'Zombie': {'hp': 150, 'xp': 35, 'color': color.olive, 'speed': 1.2, 'scale': (0.9, 1.8, 0.9), 'dungeons': [3, 4]},

    # DUNGEON 5-6 (Hard)
    'Skeleton': {'hp': 140, 'xp': 40, 'color': color.white, 'speed': 2, 'scale': (0.8, 1.8, 0.5), 'dungeons': [5, 6]},
    'Skeleton Warrior': {'hp': 200, 'xp': 55, 'color': color.light_gray, 'speed': 2.2, 'scale': (0.9, 1.9, 0.6), 'dungeons': [5, 6]},
    'Ghost': {'hp': 120, 'xp': 38, 'color': color.white33, 'speed': 2.5, 'scale': (1.0, 1.5, 0.3), 'dungeons': [5, 6]},
    'Ogre': {'hp': 300, 'xp': 75, 'color': color.brown, 'speed': 1.5, 'scale': (1.5, 2.5, 1.5), 'dungeons': [5, 6]},
    'Dark Mage': {'hp': 130, 'xp': 42, 'color': color.violet, 'speed': 1.8, 'scale': (0.8, 1.8, 0.8), 'dungeons': [5, 6]},

    # DUNGEON 7-8 (Very Hard)
    'Orc': {'hp': 280, 'xp': 70, 'color': color.olive, 'speed': 2, 'scale': (1.2, 2.0, 1.2), 'dungeons': [7, 8]},
    'Orc Berserker': {'hp': 350, 'xp': 85, 'color': color.red, 'speed': 2.8, 'scale': (1.3, 2.2, 1.3), 'dungeons': [7, 8]},
    'Troll': {'hp': 500, 'xp': 120, 'color': color.dark_gray, 'speed': 1.2, 'scale': (2.0, 3.0, 2.0), 'dungeons': [7, 8]},
    'Wraith': {'hp': 200, 'xp': 60, 'color': color.black, 'speed': 3, 'scale': (1.0, 2.0, 0.3), 'dungeons': [7, 8]},
    'Minotaur': {'hp': 400, 'xp': 100, 'color': color.brown, 'speed': 2.5, 'scale': (1.5, 2.5, 1.2), 'dungeons': [7, 8]},

    # DUNGEON 9-10 (Extreme/Nightmare)
    'Shadow Knight': {'hp': 480, 'xp': 130, 'color': color.black, 'speed': 2.5, 'scale': (1.2, 2.2, 1.0), 'dungeons': [9, 10]},
    'Vampire': {'hp': 380, 'xp': 110, 'color': color.magenta, 'speed': 3.5, 'scale': (1.0, 2.0, 0.8), 'dungeons': [9, 10]},
    'Lich': {'hp': 450, 'xp': 125, 'color': color.azure, 'speed': 1.5, 'scale': (1.0, 2.2, 1.0), 'dungeons': [9, 10]},
    'Dragon Whelp': {'hp': 700, 'xp': 180, 'color': color.orange, 'speed': 2, 'scale': (2.0, 1.5, 3.0), 'dungeons': [9, 10]},

    # UNKNOWNS - Rare random spawns (bonus XP for rare enemies)
    'Void Walker': {'hp': 250, 'xp': 75, 'color': color.violet, 'speed': 4, 'scale': (0.8, 2.5, 0.8), 'dungeons': [4, 5, 6, 7, 8, 9, 10]},
    'Crystal Golem': {'hp': 600, 'xp': 160, 'color': color.cyan, 'speed': 0.8, 'scale': (2.0, 2.5, 2.0), 'dungeons': [5, 6, 7, 8, 9, 10]},
    'Corrupted Knight': {'hp': 450, 'xp': 125, 'color': color.dark_gray, 'speed': 2, 'scale': (1.3, 2.3, 1.0), 'dungeons': [6, 7, 8, 9, 10]},
    'Soul Eater': {'hp': 350, 'xp': 100, 'color': color.black, 'speed': 3.2, 'scale': (1.5, 1.0, 1.5), 'dungeons': [7, 8, 9, 10]},
    'Abomination': {'hp': 800, 'xp': 200, 'color': color.olive, 'speed': 1, 'scale': (2.5, 3.0, 2.5), 'dungeons': [8, 9, 10]},
    'Nightmare': {'hp': 480, 'xp': 135, 'color': color.magenta, 'speed': 4, 'scale': (1.2, 1.8, 2.0), 'dungeons': [9, 10]},
    'Ancient One': {'hp': 1000, 'xp': 300, 'color': color.gold, 'speed': 1.5, 'scale': (2.5, 4.0, 2.5), 'dungeons': [10]},
    'Chaos Spawn': {'hp': 550, 'xp': 150, 'color': color.red, 'speed': 3, 'scale': (1.8, 2.0, 1.8), 'dungeons': [9, 10]},
    'Phantom Lord': {'hp': 420, 'xp': 115, 'color': color.white, 'speed': 3.5, 'scale': (1.0, 2.5, 0.5), 'dungeons': [8, 9, 10]},
    'Elemental': {'hp': 380, 'xp': 105, 'color': color.orange, 'speed': 2.5, 'scale': (1.5, 2.0, 1.5), 'dungeons': [6, 7, 8, 9, 10]},
}

# Enemy loot drop tables
ENEMY_LOOT_TABLES = {
    # Common enemies - 15-30% drop rate
    'Slime': {'drop_chance': 0.20, 'items': ['Health Potion', 'Mana Potion']},
    'Green Slime': {'drop_chance': 0.22, 'items': ['Health Potion', 'Mana Potion', 'Copper Ore']},
    'Rat': {'drop_chance': 0.15, 'items': ['Leather', 'Health Potion']},
    'Bat': {'drop_chance': 0.18, 'items': ['Leather', 'Health Potion']},
    'Mushroom': {'drop_chance': 0.25, 'items': ['Stamina Potion', 'Health Potion']},
    
    'Goblin': {'drop_chance': 0.25, 'items': ['Iron Ore', 'Leather', 'Wood']},
    'Goblin Archer': {'drop_chance': 0.30, 'items': ['Arrow', 'Wood', 'Leather']},
    'Wolf': {'drop_chance': 0.28, 'items': ['Leather', 'Copper Ore', 'Health Potion']},
    'Spider': {'drop_chance': 0.22, 'items': ['Leather', 'Iron Ore']},
    'Zombie': {'drop_chance': 0.20, 'items': ['Iron Ore', 'Health Potion']},
    
    'Skeleton': {'drop_chance': 0.30, 'items': ['Iron Ore', 'Silver Ore', 'Health Potion']},
    'Skeleton Warrior': {'drop_chance': 0.35, 'items': ['Iron Ore', 'Silver Ore', 'Arrow']},
    'Ghost': {'drop_chance': 0.25, 'items': ['Magic Crystal', 'Mana Potion']},
    'Ogre': {'drop_chance': 0.40, 'items': ['Iron Ore', 'Gold Ore', 'Health Potion']},
    'Dark Mage': {'drop_chance': 0.38, 'items': ['Magic Crystal', 'Mana Potion', 'Silver Ore']},
    
    'Orc': {'drop_chance': 0.35, 'items': ['Gold Ore', 'Iron Ore', 'Leather']},
    'Orc Berserker': {'drop_chance': 0.42, 'items': ['Gold Ore', 'Mithril Ore', 'Greater Health Potion']},
    'Troll': {'drop_chance': 0.50, 'items': ['Mithril Ore', 'Gold Ore', 'Greater Health Potion']},
    'Wraith': {'drop_chance': 0.35, 'items': ['Magic Crystal', 'Shadow Ore', 'Mana Potion']},
    'Minotaur': {'drop_chance': 0.45, 'items': ['Adamantite Ore', 'Mithril Ore', 'Leather']},
    
    'Shadow Knight': {'drop_chance': 0.50, 'items': ['Shadow Ore', 'Adamantite Ore', 'Greater Health Potion']},
    'Vampire': {'drop_chance': 0.48, 'items': ['Shadow Ore', 'Magic Crystal', 'Greater Mana Potion']},
    'Lich': {'drop_chance': 0.52, 'items': ['Magic Crystal', 'Shadow Ore', 'Greater Mana Potion']},
    'Dragon Whelp': {'drop_chance': 0.70, 'items': ['Dragon Ore', 'Dragon Scale', 'Fire Scroll']},
    
    'Void Walker': {'drop_chance': 0.40, 'items': ['Void Essence', 'Magic Crystal', 'Mana Potion']},
    'Crystal Golem': {'drop_chance': 0.60, 'items': ['Magic Crystal', 'Adamantite Ore', 'Mithril Ore']},
    'Corrupted Knight': {'drop_chance': 0.45, 'items': ['Shadow Ore', 'Adamantite Ore']},
    'Soul Eater': {'drop_chance': 0.42, 'items': ['Void Essence', 'Shadow Ore']},
    'Abomination': {'drop_chance': 0.65, 'items': ['Dragon Ore', 'Adamantite Ore', 'Greater Health Potion']},
    'Nightmare': {'drop_chance': 0.50, 'items': ['Void Essence', 'Shadow Ore', 'Magic Crystal']},
    'Ancient One': {'drop_chance': 0.80, 'items': ['Dragon Ore', 'Void Essence', 'Magic Crystal', 'Dragon Scale']},
    'Chaos Spawn': {'drop_chance': 0.55, 'items': ['Void Essence', 'Dragon Ore', 'Chaos Blade']},
    'Phantom Lord': {'drop_chance': 0.48, 'items': ['Void Essence', 'Magic Crystal']},
    'Elemental': {'drop_chance': 0.45, 'items': ['Magic Crystal', 'Fire Scroll', 'Lightning Scroll']},
    
    # World bosses - 100% drop rate with multiple items
    'Alpha Wolf': {'drop_chance': 1.0, 'items': ['Leather', 'Leather', 'Swift Essence', 'Mithril Ore']},
    'King Slime': {'drop_chance': 1.0, 'items': ['Vitality Core', 'Gold Ore', 'Greater Health Potion']},
    'Goblin Chief': {'drop_chance': 1.0, 'items': ['Gold Ore', 'Mithril Ore', 'Iron Sword']},
    'Skeleton Knight': {'drop_chance': 1.0, 'items': ['Adamantite Ore', 'Shadow Ore', 'Steel Sword']},
    
    # Dream Mode enemies - high drop rates with exclusive items
    'Shadow Stalker': {'drop_chance': 0.45, 'items': ['Shadow Ore', 'Void Crystal', 'Greater Health Potion']},
    'Void Wraith': {'drop_chance': 0.40, 'items': ['Void Crystal', 'Shadow Essence', 'Mana Potion']},
    'Nightmare Horror': {'drop_chance': 0.50, 'items': ['Nightmare Fragment', 'Shadow Ore', 'Greater Health Potion']},
    'Abyss Walker': {'drop_chance': 0.48, 'items': ['Void Crystal', 'Shadow Essence', 'Adamantite Ore']},
    'Phantom Archer': {'drop_chance': 0.42, 'items': ['Arrow', 'Shadow Essence', 'Nightmare Fragment']},
    'Spectral Shooter': {'drop_chance': 0.42, 'items': ['Arrow', 'Void Crystal', 'Shadow Ore']},
    'Terror Lord': {'drop_chance': 1.0, 'items': ['Nightmare Fragment', 'Void Crystal', 'Dragon Ore', 'Shadow Essence']},
    'Nightmare King': {'drop_chance': 1.0, 'items': ['Nightmare Fragment', 'Shadow Essence', 'Dragon Ore', 'Magic Crystal']},
    'Void Overlord': {'drop_chance': 1.0, 'items': ['Void Crystal', 'Void Crystal', 'Dragon Ore', 'Adamantite Ore']},
    'Shadow Tyrant': {'drop_chance': 1.0, 'items': ['Shadow Essence', 'Nightmare Fragment', 'Dragon Ore', 'Shadow Ore']},
}


class Pet(Entity):
    """Pet companion that follows the player."""
    def __init__(self, pet_type, owner, **kwargs):
        pet_colors = {
            'Wolf Pup': color.gray,
            'Slime': color.lime,
            'Baby Dragon': color.orange,
            'Owl': color.brown,
        }
        
        # Try to load 3D model for Wolf Pup
        model_to_use = 'cube'
        texture_to_use = 'white_cube'
        
        if pet_type == 'Wolf Pup':
            try:
                from pathlib import Path
                model_path = '__pycache__/assets/models/Wolf'
                if Path(model_path + '.glb').exists():
                    # Try to preload the model to verify it works
                    test_load = load_model(model_path, use_deepcopy=False)
                    if test_load:
                        model_to_use = model_path
                        texture_to_use = None
                        pet_colors['Wolf Pup'] = color.white  # Don't tint the model
                        print(f"Successfully loaded 3D wolf model: {model_path}.glb")
                    else:
                        print(f"Model file exists but failed to load, using cube fallback")
            except Exception as e:
                print(f"Could not load wolf model, using cube: {e}")
        
        super().__init__(
            model=model_to_use,
            texture=texture_to_use,
            color=pet_colors.get(pet_type, color.white),
            scale=(25, 25, 25) if pet_type == 'Wolf Pup' and model_to_use != 'cube' else (0.5, 0.5, 0.5),
            position=owner.position + Vec3(2, 0.5, 2) if pet_type == 'Wolf Pup' and model_to_use != 'cube' else owner.position + Vec3(2, 0, 2),
            rotation=(90, 0, 0) if pet_type == 'Wolf Pup' and model_to_use != 'cube' else (0, 0, 0),
            collider='box'
        )
        self.pet_type = pet_type
        self.owner = owner
        self.follow_distance = 3
        self.speed = 4
        self.skills = []
        self.max_skills = 4

        # Name tag - scale needs to be smaller for 3D models since they're scaled up
        is_3d_model = pet_type == 'Wolf Pup' and model_to_use != 'cube'
        self.name_tag = Text(
            text=pet_type,
            parent=self,
            y=0.08 if is_3d_model else 1,  # Much smaller y for scaled 3D models
            scale=0.12 if is_3d_model else 3,  # Much smaller scale for 3D models
            billboard=True,
            origin=(0, 0),
            color=color.lime
        )

    def update(self):
        if not self.owner:
            return
        dist = distance(self, self.owner)
        if dist > self.follow_distance:
            direction = (self.owner.position - self.position).normalized()
            direction.y = 0
            self.position += direction * self.speed * time.dt
            self.y = 0.25

    def learn_skill(self, skill_name):
        if len(self.skills) < self.max_skills and skill_name not in self.skills:
            self.skills.append(skill_name)
            return True
        return False


class Enemy(Entity):
    """Simple enemy entity."""
    def __init__(self, name, position, health=50, enemy_color=color.red, xp_value=25, **kwargs):
        super().__init__(
            model='cube',
            texture='white_cube',
            color=enemy_color,
            scale=(1, 1.5, 1),
            position=position,
            collider='box'
        )
        self.enemy_name = name
        self.max_health = health
        self.health = health
        self.xp_value = xp_value
        self.speed = 2
        self.base_speed = 2  # Store original speed for debuffs
        self.target = None
        self.attack_range = 2
        self.attack_cooldown = 0
        self.original_color = enemy_color
        
        # Projectile support for ranged enemies
        self.can_shoot_projectiles = 'Dragon' in name or 'Whelp' in name
        self.projectile_range = 15 if self.can_shoot_projectiles else 2
        self.projectiles = []
        self.projectile_color = color.orange if 'Dragon' in name or 'Whelp' in name else color.red
        self.projectile_speed = 12

        # Debuff status effects
        self.poison_damage = 0  # Poison damage per second
        self.poison_timer = 0  # Duration remaining
        self.slow_percent = 0  # Movement slow percentage
        self.slow_timer = 0
        self.weaken_percent = 0  # Damage reduction percentage
        self.weaken_timer = 0
        self.curse_percent = 0  # Takes extra damage percentage
        self.curse_timer = 0
        
        # Fear debuff (from Injector Soul)
        self.fear_multiplier = 1.0
        self.fear_duration = 0
        self.fear_dot = 0
        self.fear_dot_timer = 0

        # Health bar - centered above enemy, bg behind bar
        self.health_bar_bg = Entity(
            parent=self,
            model='quad',
            texture='white_cube',
            color=color.dark_gray,
            scale=(1.5, 0.15),
            position=(0, 1.2, -0.01),
            billboard=True
        )
        self.health_bar = Entity(
            parent=self,
            model='quad',
            texture='white_cube',
            color=color.red,
            scale=(1.5, 0.15),
            position=(0, 1.2, 0),
            billboard=True
        )

        # Name tag
        self.name_tag = Text(
            text=name,
            parent=self,
            y=1.4,
            scale=8,
            billboard=True,
            origin=(0, 0),
            color=color.white
        )

    def update(self):
        if self.health <= 0:
            return

        # Process debuffs
        self.process_debuffs()
        
        # Update projectiles
        for proj in self.projectiles[:]:
            if not proj.enabled:
                self.projectiles.remove(proj)

        # Update health bar
        ratio = self.health / self.max_health
        self.health_bar.scale_x = 1.5 * ratio

        # Calculate current speed with slow debuff
        current_speed = self.base_speed
        if self.slow_timer > 0:
            current_speed = self.base_speed * (1 - self.slow_percent / 100)
        self.speed = max(0.5, current_speed)  # Minimum 0.5 speed

        # Chase player if target set
        if self.target:
            dist = distance(self, self.target)

            # Ranged attack for dragons
            if self.can_shoot_projectiles and dist <= self.projectile_range and dist > 3 and self.attack_cooldown <= 0:
                self.attack_cooldown = 2.0  # Slower projectile attack
                self.shoot_fireball()
            # Melee attack if in range
            elif dist <= self.attack_range and self.attack_cooldown <= 0:
                self.attack_cooldown = 1.5  # Attack every 1.5 seconds
                self.attack_player()
            elif dist < 15 and dist > self.attack_range:
                # Chase
                direction = (self.target.position - self.position).normalized()
                direction.y = 0
                self.position += direction * self.speed * time.dt
                self.look_at(self.target.position)
                self.rotation_x = 0
                self.rotation_z = 0

        if self.attack_cooldown > 0:
            self.attack_cooldown -= time.dt

    def process_debuffs(self):
        """Process all active debuffs on this enemy."""
        # Poison - deal damage over time
        if self.poison_timer > 0:
            self.health -= self.poison_damage * time.dt
            self.poison_timer -= time.dt
            # Flash green when poisoned
            if int(time.time() * 4) % 2 == 0:
                self.color = color.green
            else:
                self.color = self.original_color
            if self.poison_timer <= 0:
                self.poison_damage = 0

        # Slow - reduce movement (applied in speed calculation above)
        if self.slow_timer > 0:
            self.slow_timer -= time.dt
            # Flash white/blue when slowed
            if int(time.time() * 3) % 2 == 0:
                self.color = color.azure
            if self.slow_timer <= 0:
                self.slow_percent = 0

        # Weaken - reduce outgoing damage (applied in attack_player)
        if self.weaken_timer > 0:
            self.weaken_timer -= time.dt
            if self.weaken_timer <= 0:
                self.weaken_percent = 0

        # Curse - take extra damage (applied in take_damage)
        if self.curse_timer > 0:
            self.curse_timer -= time.dt
            # Flash dark when cursed
            if int(time.time() * 3) % 2 == 0:
                self.color = color.black
            if self.curse_timer <= 0:
                self.curse_percent = 0
        
        # Fear - take 2x damage + DOT (from Injector Soul)
        if self.fear_duration > 0:
            self.fear_duration -= time.dt
            
            # Apply fear DOT every second
            self.fear_dot_timer += time.dt
            if self.fear_dot_timer >= 1.0:
                self.fear_dot_timer = 0
                if self.fear_dot > 0:
                    self.health -= self.fear_dot
                    if self.health <= 0:
                        self.die()
            
            # Flash purple when feared
            if int(time.time() * 4) % 2 == 0:
                self.color = color.violet
            
            # Reset fear when duration expires
            if self.fear_duration <= 0:
                self.fear_multiplier = 1.0
                self.fear_dot = 0
                self.fear_dot_timer = 0

    def apply_debuffs(self, poison=0, slow=0, weaken=0, curse=0, duration=5):
        """Apply debuffs from weapon effects."""
        if poison > 0:
            self.poison_damage = poison
            self.poison_timer = duration
        if slow > 0:
            self.slow_percent = min(90, self.slow_percent + slow)  # Cap at 90% slow
            self.slow_timer = duration
        if weaken > 0:
            self.weaken_percent = min(80, self.weaken_percent + weaken)  # Cap at 80% weaken
            self.weaken_timer = duration
        if curse > 0:
            self.curse_percent = min(100, self.curse_percent + curse)  # Cap at 100% extra damage
            self.curse_timer = duration

    def attack_player(self):
        """Attack the player target."""
        if not self.target or not hasattr(self.target, 'game_ref'):
            return

        game = self.target.game_ref
        if game and game.character:
            # Deal damage based on enemy type - dangerous!
            damage = 10 + (self.max_health // 3)  # Stronger enemies deal more damage

            # Apply weaken debuff - reduce enemy's outgoing damage
            if self.weaken_percent > 0:
                damage = damage * (1 - self.weaken_percent / 100)

            defense = game.get_total_defense()
            actual_damage = max(5, damage - defense // 4)  # Minimum 5 damage

            died = game.character.take_damage(actual_damage)
            game.add_chat_message(f"{self.enemy_name} attacks! (-{int(actual_damage)} HP)", color.red)

            # Flash effect on enemy attack
            self.color = color.yellow
            invoke(self.reset_color, delay=0.2)

            if died:
                game.add_chat_message("You have been defeated!", color.red)
                # If in dungeon, exit and show wave reached
                if game.in_dungeon:
                    wave_reached = game.dungeon_wave
                    game.exit_dungeon()
                    game.add_chat_message(f"You survived to Wave {wave_reached}!", color.orange)
                # Respawn at village with restored HP/MP
                # Error404 mode: respawn at Error Village
                if game.error404_mode:
                    game.player.position = Vec3(-500, 1, 500)  # Error Village spawn
                else:
                    game.player.position = Vec3(0, 1, 0)  # Normal village spawn
                game.character.health = game.character.max_health  # Full HP on respawn
                game.character.mana = game.character.max_mana  # Full MP on respawn
                # Force update health bar immediately
                game.health_bar.scale_x = 0.4
                game.hp_text.text = f'{int(game.character.health)}/{int(game.character.max_health)}'
                game.mana_bar.scale_x = 0.4
                game.mp_text.text = f'{int(game.character.mana)}/{int(game.character.max_mana)}'
                respawn_msg = "Respawned at Error Village." if game.error404_mode else "Respawned at village."
                game.add_chat_message(respawn_msg, color.yellow)

    def take_damage(self, amount):
        # Apply curse debuff - enemy takes extra damage
        if self.curse_percent > 0:
            amount = amount * (1 + self.curse_percent / 100)
        
        # Apply fear multiplier (from Injector Soul)
        if self.fear_multiplier > 1.0:
            amount = amount * self.fear_multiplier

        self.health -= amount
        self.color = color.white
        invoke(self.reset_color, delay=0.1)

        if self.health <= 0:
            self.die()
        return amount

    def shoot_fireball(self):
        """Shoot a fireball projectile at the target."""
        if not self.target:
            return

        # Calculate direction
        direction = (self.target.position - self.position).normalized()
        direction.y = 0.3  # Slight upward arc

        proj = EnemyProjectile(
            position=self.position + Vec3(0, 1, 0),
            direction=direction,
            damage=15 + self.max_health // 5,
            projectile_color=self.projectile_color,
            speed=self.projectile_speed
        )
        self.projectiles.append(proj)

        # Visual feedback
        self.color = color.yellow
        invoke(self.reset_color, delay=0.2)

    def reset_color(self):
        if self.health > 0:
            self.color = self.original_color

    def die(self):
        print(f"{self.enemy_name} defeated! +{self.xp_value} XP")
        
        # Drop 404 Blade if tErRoR 404 boss
        if hasattr(self, 'is_boss') and self.is_boss and 'tErRoR 404' in self.enemy_name:
            if self.target and hasattr(self.target, 'game_ref'):
                game = self.target.game_ref
                if game:
                    game.add_chat_message("*** 404 BLADE OBTAINED! ***", color.rgb(255, 0, 255))
                    # Add 404 Blade to inventory
                    blade_404 = {
                        'name': '404 Blade',
                        'damage': 404,
                        'weapon_type': 'sword',
                        'color': color.rgb(255, 0, 255),
                        'attack_speed_mult': 2.0,
                        'description': 'ERROR: Weapon too powerful'
                    }
                    for i, slot in enumerate(game.inventory):
                        if slot is None:
                            game.inventory[i] = blade_404
                            game.update_hotbar_display()
                            break
        
        # Drop Injector Soul if Fear Injector boss
        if hasattr(self, 'is_boss') and self.is_boss and 'fearinjector' in self.enemy_name.lower():
            if self.target and hasattr(self.target, 'game_ref'):
                game = self.target.game_ref
                if game:
                    game.add_chat_message("*** INJECTOR SOUL OBTAINED! ***", color.violet)
                    # Add Injector Soul to inventory
                    if hasattr(game, 'inventory'):
                        game.inventory.add_item('Injector Soul', 1)
        
        destroy(self.health_bar_bg)
        destroy(self.health_bar)
        destroy(self.name_tag)
        destroy(self)


class EnemyProjectile(Entity):
    """Projectile fired by ranged enemies."""
    def __init__(self, position, direction, damage, projectile_color=color.red, speed=20, **kwargs):
        super().__init__(
            model='cube',
            texture='white_cube',
            color=projectile_color,
            scale=(0.2, 0.2, 0.8),
            position=position,
            collider='box'
        )
        self.direction = direction.normalized()
        self.speed = speed
        self.damage = damage
        self.lifetime = 5  # Seconds before auto-destroy
        self.look_at(position + direction)

    def update(self):
        self.position += self.direction * self.speed * time.dt
        self.lifetime -= time.dt
        if self.lifetime <= 0:
            destroy(self)


class PlayerProjectile(Entity):
    """Piercing projectile fired by staffs - passes through multiple enemies."""
    def __init__(self, position, direction, damage, projectile_color=color.magenta, speed=25,
                 pierce=3, debuff_type=None, debuff_value=0, game_ref=None, **kwargs):
        super().__init__(
            model='cube',
            texture='white_cube',
            color=projectile_color,
            scale=(0.3, 0.3, 1.2),
            position=position,
            collider='box'
        )
        self.direction = direction.normalized()
        self.speed = speed
        self.damage = damage
        self.pierce = pierce  # How many enemies it can hit
        self.pierce_count = 0
        self.hit_enemies = []  # Track which enemies were hit
        self.debuff_type = debuff_type
        self.debuff_value = debuff_value
        self.game_ref = game_ref
        self.lifetime = 3  # Seconds before auto-destroy
        self.look_at(position + direction)

    def update(self):
        self.position += self.direction * self.speed * time.dt
        self.lifetime -= time.dt

        # Check for enemy hits
        if self.game_ref:
            for enemy in self.game_ref.enemies[:]:
                if enemy.health <= 0 or enemy in self.hit_enemies:
                    continue
                if distance(self, enemy) < 2:
                    # Save enemy data before take_damage (which can destroy it)
                    enemy_name = enemy.enemy_name
                    enemy_pos = Vec3(enemy.position)
                    enemy_xp = enemy.xp_value
                    
                    # Hit the enemy
                    enemy.take_damage(self.damage)
                    self.hit_enemies.append(enemy)
                    self.pierce_count += 1

                    # Apply debuff
                    if self.debuff_type and self.debuff_value > 0:
                        if self.debuff_type == 'slow':
                            enemy.apply_debuffs(slow=self.debuff_value, duration=4)
                        elif self.debuff_type == 'poison':
                            enemy.apply_debuffs(poison=self.debuff_value, duration=5)
                        elif self.debuff_type == 'weaken':
                            enemy.apply_debuffs(weaken=self.debuff_value, duration=4)
                        elif self.debuff_type == 'curse':
                            enemy.apply_debuffs(curse=self.debuff_value, duration=5)

                    self.game_ref.add_chat_message(f"Staff bolt pierces {enemy_name}! (-{int(self.damage)})", color.magenta)
                    
                    # Drop loot if enemy died
                    if enemy.health <= 0:
                        self.game_ref.drop_enemy_loot(enemy_name, enemy_pos)

                    # Check if we've hit max pierce
                    if self.pierce_count >= self.pierce:
                        destroy(self)
                        return

        if self.lifetime <= 0:
            destroy(self)


class RangedEnemy(Enemy):
    """Enemy that fires projectiles at the player."""
    def __init__(self, name, position, health=50, enemy_color=color.red, xp_value=25,
                 projectile_color=color.red, attack_range=15, projectile_speed=15, **kwargs):
        super().__init__(name, position, health, enemy_color, xp_value, **kwargs)
        self.attack_range = attack_range
        self.projectile_color = projectile_color
        self.projectile_speed = projectile_speed
        self.projectiles = []

    def update(self):
        if self.health <= 0:
            return

        # Process debuffs
        self.process_debuffs()

        # Update health bar
        ratio = self.health / self.max_health
        self.health_bar.scale_x = 1.5 * ratio

        # Calculate current speed with slow debuff
        current_speed = self.base_speed
        if self.slow_timer > 0:
            current_speed = self.base_speed * (1 - self.slow_percent / 100)
        self.speed = max(0.5, current_speed)

        # Chase and attack player
        if self.target:
            dist = distance(self, self.target)

            # Fire projectile if in range
            if dist <= self.attack_range and self.attack_cooldown <= 0:
                self.attack_cooldown = 2.0  # Fire every 2 seconds
                self.fire_projectile()
            elif dist < self.attack_range and dist > 5:
                # Keep distance - don't get too close
                pass
            elif dist >= self.attack_range and dist < 25:
                # Move towards player to get in range
                direction = (self.target.position - self.position).normalized()
                direction.y = 0
                self.position += direction * self.speed * time.dt
                self.look_at(self.target.position)
                self.rotation_x = 0
                self.rotation_z = 0

        if self.attack_cooldown > 0:
            self.attack_cooldown -= time.dt

        # Update projectiles and check for hits
        for proj in self.projectiles[:]:
            if proj and hasattr(proj, 'enabled') and proj.enabled:
                # Check if hit player
                if self.target and distance(proj, self.target) < 1.5:
                    self.hit_player(proj)
                    if proj in self.projectiles:
                        self.projectiles.remove(proj)
                    destroy(proj)
            elif proj in self.projectiles:
                self.projectiles.remove(proj)

    def fire_projectile(self):
        """Fire a projectile at the player."""
        if not self.target:
            return

        direction = (self.target.position - self.position)
        direction.y = 0.5  # Slight upward arc

        proj = EnemyProjectile(
            position=self.position + Vec3(0, 1, 0),
            direction=direction,
            damage=10 + self.max_health // 5,
            projectile_color=self.projectile_color,
            speed=self.projectile_speed
        )
        self.projectiles.append(proj)

        # Visual feedback
        self.color = color.yellow
        invoke(self.reset_color, delay=0.2)

    def hit_player(self, projectile):
        """Handle projectile hitting player."""
        if not self.target or not hasattr(self.target, 'game_ref'):
            return

        game = self.target.game_ref
        if game and game.character and game.character.health > 0:
            damage = projectile.damage

            # Apply weaken debuff
            if self.weaken_percent > 0:
                damage = damage * (1 - self.weaken_percent / 100)

            defense = game.get_total_defense()
            actual_damage = max(3, damage - defense // 4)

            # Always apply damage, even at low health
            died = game.character.take_damage(actual_damage)
            game.add_chat_message(f"{self.enemy_name} shoots you! (-{int(actual_damage)} HP)", color.orange)

            if died:
                game.add_chat_message("You have been defeated!", color.red)
                if game.in_dungeon:
                    wave_reached = game.dungeon_wave
                    game.exit_dungeon()
                    game.add_chat_message(f"You survived to Wave {wave_reached}!", color.orange)
                # Error404 mode: respawn at Error Village
                if game.error404_mode:
                    game.player.position = Vec3(-500, 1, 500)  # Error Village spawn
                else:
                    game.player.position = Vec3(0, 1, 0)  # Normal village spawn
                game.character.health = game.character.max_health
                game.character.mana = game.character.max_mana
                game.health_bar.scale_x = 0.4
                game.hp_text.text = f'{int(game.character.health)}/{int(game.character.max_health)}'
                game.mana_bar.scale_x = 0.4
                game.mp_text.text = f'{int(game.character.mana)}/{int(game.character.max_mana)}'
                respawn_msg = "Respawned at Error Village." if game.error404_mode else "Respawned at village."
                game.add_chat_message(respawn_msg, color.yellow)


class BossProjectile(Entity):
    """Fireball or special attack projectile from bosses."""
    def __init__(self, position, direction, damage, projectile_color=color.orange, speed=12, scale_mult=1.0, **kwargs):
        base_size = 0.8 * scale_mult  # Scale projectile size
        super().__init__(
            model='sphere',
            texture='white_cube',
            color=projectile_color,
            scale=(base_size, base_size, base_size),
            position=position,
            collider='sphere'
        )
        self.direction = direction.normalized()
        self.speed = speed
        self.damage = damage
        self.lifetime = 5
        self.projectile_color = projectile_color
        self.base_scale = base_size

        # Trailing effect (also scaled)
        self.trail = Entity(parent=self, model='sphere', color=projectile_color * 0.5,
                            scale=0.6 * scale_mult, position=(0, 0, -0.5))

    def update(self):
        self.position += self.direction * self.speed * time.dt
        self.lifetime -= time.dt

        # Pulse effect
        pulse = 0.8 + 0.2 * sin(time.time() * 10)
        self.scale = Vec3(self.base_scale * pulse, self.base_scale * pulse, self.base_scale * pulse)

        if self.lifetime <= 0:
            destroy(self)


class BossEnemy(Enemy):
    """Powerful boss enemy with special attacks and phases."""
    def __init__(self, name, position, health=1000, enemy_color=color.red, xp_value=500, **kwargs):
        # Triple XP for all bosses
        super().__init__(name, position, health, enemy_color, xp_value * 3, **kwargs)
        self.special_cooldown = 0
        self.phase = 1
        self.is_boss = True
        self.base_color = enemy_color
        self.phase_announced = {1: True, 2: False, 3: False}
        self.projectiles = []
        self.projectile_scale = 1.0  # Default projectile size multiplier
        
        # Revive/Enraged mechanic
        self.has_revived = False
        self.is_enraged = False
        self.enrage_damage_taken = 0
        self.original_max_health = health

        # Determine boss type for special attacks
        name_lower = name.lower()
        self.can_fireball = any(x in name_lower for x in ['dragon', 'fire', 'flame', 'infern', 'magma', 'phoenix'])
        self.can_iceball = any(x in name_lower for x in ['frost', 'ice', 'frozen', 'cold', 'snow'])
        self.can_poison = any(x in name_lower for x in ['swamp', 'poison', 'hydra', 'witch', 'bog', 'toxic'])
        self.can_magic = any(x in name_lower for x in ['fairy', 'magic', 'queen', 'pharaoh', 'king', 'elemental'])
        self.can_terror_scream = any(x in name_lower for x in ['terror', 'nightmare', 'void', 'supreme', 'demon', 'lord', 'fearinjector'])
        self.can_blood_rage = any(x in name_lower for x in ['colossus', 'titan', 'overlord', 'tyrant'])
        self.can_shadow_dash = any(x in name_lower for x in ['shadow', 'abyss', 'walker', 'stalker'])
        self.can_soul_drain = any(x in name_lower for x in ['lich', 'king', 'ancient', 'supreme'])
        self.can_shadow_bullet = 'fearinjector' in name_lower
        
        # Ability cooldowns
        self.terror_scream_cooldown = 0
        self.blood_rage_cooldown = 0
        self.shadow_dash_cooldown = 0
        self.soul_drain_cooldown = 0
        self.shadow_bullet_cooldown = 0
        
        # For Fear Injector avenge mechanic
        self.partner_boss = None
        self.is_avenging = False

        # Larger scale for bosses
        self.scale = self.scale * 2
        self.name_tag.scale = 12
        self.health_bar.scale_x = 3
        self.health_bar_bg.scale_x = 3

    def update(self):
        if self.health <= 0:
            return
        
        # Check if partner died (for Fear Injectors avenge)
        if self.partner_boss and not self.is_avenging:
            if not hasattr(self.partner_boss, 'health') or self.partner_boss.health <= 0:
                self.trigger_avenge()
        
        # REVIVE MECHANIC: Prevent death at 1 HP or less
        if self.health <= 1 and not self.has_revived:
            self.health = 1
            self.has_revived = True
            self.is_enraged = True
            self.color = color.red
            
            if self.target and hasattr(self.target, 'game_ref'):
                game = self.target.game_ref
                if game:
                    game.add_chat_message(f"*** {self.enemy_name} REFUSES TO DIE! ENRAGED! ***", color.red)
        
        # ENRAGED STATE: Gets faster every 500 damage, dies when reaching original max HP damage
        if self.is_enraged:
            # Track damage and increase speed
            damage_threshold = 500
            speed_stacks = int(self.enrage_damage_taken / damage_threshold)
            speed_multiplier = 1.5 + speed_stacks * 0.3
            if self.is_avenging:
                speed_multiplier *= 2.0  # Extra boost from avenge
            self.speed = self.base_speed * speed_multiplier
            
            # Die when accumulated damage >= max HP
            if self.enrage_damage_taken >= self.original_max_health:
                self.health = 0
                return
            
            # Visual feedback - pulse red
            if int(time.time() * 4) % 2 == 0:
                self.color = color.red
            else:
                self.color = color.orange

        # Process debuffs
        self.process_debuffs()

        # Update health bar
        ratio = self.health / self.max_health
        self.health_bar.scale_x = 3 * ratio

        # Phase changes based on health - WITH ANNOUNCEMENTS
        if self.health < self.max_health * 0.5 and self.phase == 1:
            self.phase = 2
            self.speed = self.base_speed * 1.5
            self.color = self.base_color * 1.3  # Brighter
            if self.target and hasattr(self.target, 'game_ref') and not self.phase_announced[2]:
                game = self.target.game_ref
                if game:
                    game.add_chat_message(f"*** {self.enemy_name} enters PHASE 2! ENRAGED! ***", color.orange)
                    self.phase_announced[2] = True

        if self.health < self.max_health * 0.25 and self.phase == 2:
            self.phase = 3
            self.speed = self.base_speed * 2
            self.color = color.red  # Turn red when furious
            if self.target and hasattr(self.target, 'game_ref') and not self.phase_announced[3]:
                game = self.target.game_ref
                if game:
                    game.add_chat_message(f"*** {self.enemy_name} enters PHASE 3! FURIOUS! ***", color.red)
                    self.phase_announced[3] = True

        # Calculate current speed with slow debuff
        current_speed = self.speed
        if self.slow_timer > 0:
            current_speed = self.speed * (1 - self.slow_percent / 100)

        # Update special cooldown
        if self.special_cooldown > 0:
            self.special_cooldown -= time.dt
        
        # Update ability cooldowns
        if self.terror_scream_cooldown > 0:
            self.terror_scream_cooldown -= time.dt
        if self.blood_rage_cooldown > 0:
            self.blood_rage_cooldown -= time.dt
        if self.shadow_dash_cooldown > 0:
            self.shadow_dash_cooldown -= time.dt
        if self.soul_drain_cooldown > 0:
            self.soul_drain_cooldown -= time.dt
        if self.shadow_bullet_cooldown > 0:
            self.shadow_bullet_cooldown -= time.dt

        # Update projectiles
        self.update_projectiles()

        # Chase player if target set
        if self.target:
            # Safety check - make sure target still exists and is not destroyed
            if not hasattr(self.target, 'enabled') or not self.target.enabled:
                self.target = None
                return
            
            try:
                dist = distance(self, self.target)
            except:
                # Target destroyed during distance check
                self.target = None
                return
            
            # USE NEW ABILITIES
            # Terror Scream - slows player, speeds self
            if self.can_terror_scream and dist < 15 and self.terror_scream_cooldown <= 0:
                self.use_terror_scream()
                self.terror_scream_cooldown = 8
            
            # Blood Rage - damage boost
            if self.can_blood_rage and self.health < self.max_health * 0.5 and self.blood_rage_cooldown <= 0:
                self.use_blood_rage()
                self.blood_rage_cooldown = 12
            
            # Shadow Dash - teleport closer
            if self.can_shadow_dash and dist > 10 and dist < 20 and self.shadow_dash_cooldown <= 0:
                self.use_shadow_dash()
                self.shadow_dash_cooldown = 6
            
            # Soul Drain - heal from player
            if self.can_soul_drain and self.health < self.max_health * 0.7 and self.soul_drain_cooldown <= 0:
                self.use_soul_drain()
                self.soul_drain_cooldown = 15
            
            # Shadow Bullet - rapid fire shadow projectiles
            if self.can_shadow_bullet and dist < 25 and self.shadow_bullet_cooldown <= 0:
                self.use_shadow_bullet()
                self.shadow_bullet_cooldown = 5

            # Special attack at range (if can do ranged attack)
            if dist > 5 and dist < 25 and self.special_cooldown <= 0:
                if self.can_fireball or self.can_iceball or self.can_poison or self.can_magic:
                    self.use_special_attack()
                    # Cooldown decreases with phase
                    self.special_cooldown = max(1.5, 4 - self.phase)

            # Melee attack if in range
            if dist <= self.attack_range + 1 and self.attack_cooldown <= 0:
                self.attack_cooldown = max(0.5, 1.2 - self.phase * 0.2)  # Faster in later phases
                self.attack_player()
            elif dist < 30 and dist > self.attack_range:
                # Chase
                direction = (self.target.position - self.position).normalized()
                direction.y = 0
                self.position += direction * current_speed * time.dt
                self.look_at(self.target.position)
                self.rotation_x = 0
                self.rotation_z = 0

        if self.attack_cooldown > 0:
            self.attack_cooldown -= time.dt

    def use_special_attack(self):
        """Fire a special projectile based on boss type."""
        if not self.target:
            return

        direction = (self.target.position - self.position).normalized()
        spawn_pos = self.position + Vec3(0, 1.5, 0) + direction * 2

        # Determine projectile type and color
        if self.can_fireball:
            proj_color = color.orange
            attack_name = "FIREBALL"
        elif self.can_iceball:
            proj_color = color.cyan
            attack_name = "ICE BLAST"
        elif self.can_poison:
            proj_color = color.green
            attack_name = "POISON SPIT"
        else:
            proj_color = color.magenta
            attack_name = "MAGIC BOLT"

        # Damage scales with phase
        base_dmg = 15 + self.max_health // 100
        damage = base_dmg * (1 + (self.phase - 1) * 0.4)

        proj = BossProjectile(
            position=spawn_pos,
            direction=direction,
            damage=damage,
            projectile_color=proj_color,
            speed=10 + self.phase * 3,
            scale_mult=self.projectile_scale  # Use boss's projectile scale
        )
        self.projectiles.append(proj)

        # Announce attack
        if self.target and hasattr(self.target, 'game_ref'):
            game = self.target.game_ref
            if game:
                game.add_chat_message(f"{self.enemy_name} casts {attack_name}!", proj_color)

    def update_projectiles(self):
        """Check if projectiles hit the player."""
        for proj in self.projectiles[:]:
            if not proj or proj.lifetime <= 0:
                if proj in self.projectiles:
                    self.projectiles.remove(proj)
                continue

            # Check hit on player
            if self.target and distance(proj, self.target) < 2:
                # Hit player
                if hasattr(self.target, 'game_ref'):
                    game = self.target.game_ref
                    if game and game.character:
                        defense = game.get_total_defense()
                        actual_damage = max(5, proj.damage - defense // 4)
                        died = game.character.take_damage(actual_damage)
                        game.add_chat_message(f"Hit by projectile! (-{int(actual_damage)} HP)", color.red)

                        if died:
                            self.handle_player_death(game)

                destroy(proj)
                self.projectiles.remove(proj)

    def handle_player_death(self, game):
        """Handle when player dies to boss."""
        game.add_chat_message("You have been defeated by the boss!", color.red)
        if game.in_dungeon:
            wave_reached = game.dungeon_wave
            game.exit_dungeon()
            game.add_chat_message(f"You survived to Wave {wave_reached}!", color.orange)
        # Error404 mode: respawn at Error Village
        if game.error404_mode:
            game.player.position = Vec3(-500, 1, 500)  # Error Village spawn
        else:
            game.player.position = Vec3(0, 1, 0)  # Normal village spawn
        game.character.health = game.character.max_health
        game.character.mana = game.character.max_mana
        game.health_bar.scale_x = 0.4
        game.hp_text.text = f'{int(game.character.health)}/{int(game.character.max_health)}'
        game.mana_bar.scale_x = 0.4
        game.mp_text.text = f'{int(game.character.mana)}/{int(game.character.max_mana)}'
        respawn_msg = "Respawned at Error Village." if game.error404_mode else "Respawned at village."
        game.add_chat_message(respawn_msg, color.yellow)

    def attack_player(self):
        """Boss melee attack - deals more damage."""
        if not self.target or not hasattr(self.target, 'game_ref'):
            return

        game = self.target.game_ref
        if game and game.character:
            # Boss damage scales with phase
            base_damage = 15 + (self.max_health // 80)
            damage = base_damage * (1 + (self.phase - 1) * 0.35)

            if self.weaken_percent > 0:
                damage = damage * (1 - self.weaken_percent / 100)

            defense = game.get_total_defense()
            actual_damage = max(8, damage - defense // 3)

            # Attack names based on phase
            attack_names = ["STRIKES", "SLAMS", "DEVASTATES"]
            attack_name = attack_names[min(self.phase - 1, 2)]

            died = game.character.take_damage(actual_damage)
            game.add_chat_message(f"{self.enemy_name} {attack_name}! (-{int(actual_damage)} HP)", color.red)

            self.color = color.yellow
            invoke(self.reset_color, delay=0.2)

            if died:
                self.handle_player_death(game)
    
    def use_terror_scream(self):
        """Terror Scream - slows player and speeds up boss"""
        if not self.target or not hasattr(self.target, 'game_ref'):
            return
        
        game = self.target.game_ref
        if game:
            # Slow player by 40% for 4 seconds
            dist = distance(self, self.target)
            if dist < 15:
                game.add_chat_message(f"{self.enemy_name} unleashes TERROR SCREAM!", color.violet)
                # Apply slow to player (need to add player slow mechanic)
                # Speed up self
                self.speed = self.base_speed * 2.5
                invoke(lambda: setattr(self, 'speed', self.base_speed * (1.5 if self.is_enraged else 1.0)), delay=4)
    
    def use_blood_rage(self):
        """Blood Rage - increases damage and attack speed"""
        if self.target and hasattr(self.target, 'game_ref'):
            game = self.target.game_ref
            if game:
                game.add_chat_message(f"{self.enemy_name} enters BLOOD RAGE!", color.red)
                self.color = color.rgb(255, 0, 0)
                # Attacks will deal more damage (handled in attack_player)
                invoke(lambda: setattr(self, 'color', self.base_color), delay=6)
    
    def use_shadow_dash(self):
        """Shadow Dash - teleports closer to player"""
        if not self.target:
            return
        
        # Teleport 50% closer to target
        direction = (self.target.position - self.position).normalized()
        dist = distance(self, self.target)
        teleport_dist = min(dist * 0.5, 10)
        new_pos = self.position + direction * teleport_dist
        new_pos.y = 0.75
        self.position = new_pos
        
        if hasattr(self.target, 'game_ref'):
            game = self.target.game_ref
            if game:
                game.add_chat_message(f"{self.enemy_name} uses SHADOW DASH!", color.black)
    
    def use_soul_drain(self):
        """Soul Drain - steals health from player"""
        if not self.target or not hasattr(self.target, 'game_ref'):
            return
        
        game = self.target.game_ref
        if game and game.character:
            drain_amount = 30 + self.max_health // 50
            game.character.take_damage(drain_amount)
            self.health = min(self.max_health, self.health + drain_amount)
            game.add_chat_message(f"{self.enemy_name} drains {int(drain_amount)} HP!", color.violet)
    
    def use_shadow_bullet(self):
        """Shadow Bullet - fires 3 dark projectiles in a spread"""
        if not self.target:
            return
        
        for angle_offset in [-15, 0, 15]:
            direction = (self.target.position - self.position).normalized()
            # Rotate direction by angle_offset
            import math
            angle_rad = math.radians(angle_offset)
            rotated_x = direction.x * math.cos(angle_rad) - direction.z * math.sin(angle_rad)
            rotated_z = direction.x * math.sin(angle_rad) + direction.z * math.cos(angle_rad)
            rotated_direction = Vec3(rotated_x, 0, rotated_z).normalized()
            
            proj = BossProjectile(
                position=self.position + Vec3(0, 1, 0),
                direction=rotated_direction,
                damage=35 + (self.max_health // 100),
                projectile_color=color.black,
                speed=18,
                scale_mult=2.0
            )
            self.projectiles.append(proj)
        
        if hasattr(self.target, 'game_ref'):
            game = self.target.game_ref
            if game:
                game.add_chat_message(f"{self.enemy_name} fires SHADOW BULLETS!", color.black)
    
    def trigger_avenge(self):
        """Triggered when partner Fear Injector dies"""
        if self.is_avenging:
            return
        
        self.is_avenging = True
        self.speed = self.base_speed * 2.0
        self.max_health = int(self.max_health * 1.5)
        self.health = min(self.max_health, self.health * 1.5)
        
        if self.target and hasattr(self.target, 'game_ref'):
            game = self.target.game_ref
            if game:
                game.add_chat_message(f"*** {self.enemy_name} IS AVENGING! 2X SPEED! ***", color.violet)
    
    def take_damage(self, amount):
        """Override to track enrage damage"""
        if self.is_enraged:
            self.enrage_damage_taken += amount
        super().take_damage(amount)

    def reset_color(self):
        """Reset color based on current phase."""
        if self.phase == 3:
            self.color = color.red
        elif self.phase == 2:
            self.color = self.base_color * 1.3
        else:
            self.color = self.base_color


class Item:
    """Represents an inventory item."""
    ITEM_DATA = {
        # Swords (Warrior) - 4x damage boost!
        'Wooden Sword': {'type': 'weapon', 'weapon_type': 'sword', 'damage': 20, 'rarity': 'common', 'color': color.brown},
        'Iron Sword': {'type': 'weapon', 'weapon_type': 'sword', 'damage': 48, 'rarity': 'common', 'color': color.light_gray},
        'Steel Sword': {'type': 'weapon', 'weapon_type': 'sword', 'damage': 72, 'rarity': 'uncommon', 'color': color.white},
        'Fire Blade': {'type': 'weapon', 'weapon_type': 'sword', 'damage': 100, 'rarity': 'rare', 'color': color.orange},
        'Dragon Slayer': {'type': 'weapon', 'weapon_type': 'sword', 'damage': 160, 'rarity': 'legendary', 'color': color.red},
        # Daggers (Rogue)
        'Iron Dagger': {'type': 'weapon', 'weapon_type': 'dagger', 'damage': 8, 'rarity': 'common', 'color': color.light_gray},
        'Shadow Dagger': {'type': 'weapon', 'weapon_type': 'dagger', 'damage': 15, 'rarity': 'rare', 'color': color.violet},
        'Assassin Blade': {'type': 'weapon', 'weapon_type': 'dagger', 'damage': 22, 'rarity': 'rare', 'color': color.black},
        # Staffs (Mage) - Fire piercing projectiles with debuffs!
        'Wooden Staff': {'type': 'weapon', 'weapon_type': 'staff', 'damage': 8, 'mana_bonus': 10, 'rarity': 'common', 'color': color.brown, 'projectile': True, 'pierce': 3, 'debuff': 'slow', 'debuff_value': 20},
        'Crystal Staff': {'type': 'weapon', 'weapon_type': 'staff', 'damage': 15, 'mana_bonus': 20, 'rarity': 'rare', 'color': color.cyan, 'projectile': True, 'pierce': 4, 'debuff': 'slow', 'debuff_value': 35},
        'Fire Staff': {'type': 'weapon', 'weapon_type': 'staff', 'damage': 22, 'mana_bonus': 25, 'rarity': 'rare', 'color': color.orange, 'projectile': True, 'pierce': 5, 'debuff': 'poison', 'debuff_value': 20},
        'Arcane Staff': {'type': 'weapon', 'weapon_type': 'staff', 'damage': 30, 'mana_bonus': 40, 'rarity': 'legendary', 'color': color.magenta, 'projectile': True, 'pierce': 6, 'debuff': 'curse', 'debuff_value': 40},
        # Healing Staffs (Healer/Paladin)
        'Wooden Healing Staff': {'type': 'weapon', 'weapon_type': 'healing_staff', 'damage': 5, 'heal_power': 15, 'rarity': 'common', 'color': color.green},
        'Holy Staff': {'type': 'weapon', 'weapon_type': 'healing_staff', 'damage': 10, 'heal_power': 30, 'rarity': 'uncommon', 'color': color.white},
        'Divine Staff': {'type': 'weapon', 'weapon_type': 'healing_staff', 'damage': 15, 'heal_power': 50, 'rarity': 'rare', 'color': color.gold},
        # Bows (Ranger)
        'Wooden Bow': {'type': 'weapon', 'weapon_type': 'bow', 'damage': 10, 'range': 30, 'rarity': 'common', 'color': color.brown},
        'Hunter Bow': {'type': 'weapon', 'weapon_type': 'bow', 'damage': 18, 'range': 30, 'rarity': 'uncommon', 'color': color.olive},
        'Elven Bow': {'type': 'weapon', 'weapon_type': 'bow', 'damage': 25, 'range': 30, 'rarity': 'rare', 'color': color.lime},
        'Dragon Bow': {'type': 'weapon', 'weapon_type': 'bow', 'damage': 35, 'range': 30, 'rarity': 'legendary', 'color': color.red},
        'tErRoR bOw': {'type': 'weapon', 'weapon_type': 'bow', 'damage': 100, 'range': 30, 'rarity': 'legendary', 'color': color.rgb(255, 0, 255), 'fear_active': True},
        # Armor - Chest
        'Leather Armor': {'type': 'armor', 'defense': 5, 'slot': 'chest', 'rarity': 'common', 'color': color.brown},
        'Iron Armor': {'type': 'armor', 'defense': 12, 'slot': 'chest', 'rarity': 'uncommon', 'color': color.gray},
        'Steel Armor': {'type': 'armor', 'defense': 20, 'slot': 'chest', 'rarity': 'rare', 'color': color.white},
        'Dragon Armor': {'type': 'armor', 'defense': 35, 'slot': 'chest', 'rarity': 'legendary', 'color': color.red},
        # Armor - Head
        'Leather Hood': {'type': 'armor', 'defense': 3, 'slot': 'head', 'rarity': 'common', 'color': color.brown},
        'Iron Helmet': {'type': 'armor', 'defense': 6, 'slot': 'head', 'rarity': 'common', 'color': color.gray},
        'Steel Helmet': {'type': 'armor', 'defense': 10, 'slot': 'head', 'rarity': 'uncommon', 'color': color.white},
        # Armor - Shield
        'Wooden Shield': {'type': 'armor', 'defense': 4, 'slot': 'off_hand', 'rarity': 'common', 'color': color.brown},
        'Iron Shield': {'type': 'armor', 'defense': 8, 'slot': 'off_hand', 'rarity': 'common', 'color': color.gray},
        'Tower Shield': {'type': 'armor', 'defense': 15, 'slot': 'off_hand', 'rarity': 'rare', 'color': color.white},
        # Consumables
        'Health Potion': {'type': 'consumable', 'heal': 30, 'rarity': 'common', 'color': color.red},
        'Greater Health Potion': {'type': 'consumable', 'heal': 60, 'rarity': 'uncommon', 'color': color.red},
        'Mana Potion': {'type': 'consumable', 'mana': 25, 'rarity': 'common', 'color': color.blue},
        'Greater Mana Potion': {'type': 'consumable', 'mana': 50, 'rarity': 'uncommon', 'color': color.blue},
        'Stamina Potion': {'type': 'consumable', 'stamina': 40, 'rarity': 'common', 'color': color.green},
        # Spell scrolls
        'Fire Scroll': {'type': 'spell', 'damage': 25, 'mana_cost': 15, 'rarity': 'uncommon', 'color': color.orange},
        'Ice Scroll': {'type': 'spell', 'damage': 20, 'mana_cost': 12, 'rarity': 'uncommon', 'color': color.cyan},
        'Lightning Scroll': {'type': 'spell', 'damage': 35, 'mana_cost': 25, 'rarity': 'rare', 'color': color.yellow},
        # Materials
        'Gold Coin': {'type': 'currency', 'value': 1, 'rarity': 'common', 'color': color.gold},
        'Ruby': {'type': 'material', 'value': 50, 'rarity': 'rare', 'color': color.red},
        'Sapphire': {'type': 'material', 'value': 50, 'rarity': 'rare', 'color': color.blue},
        'Arrow': {'type': 'ammo', 'damage_bonus': 2, 'rarity': 'common', 'color': color.brown},
        # DUNGEON REWARD WEAPONS - Legendary tier (swords 4x damage, staffs pierce+debuff)
        'Shadow Bow': {'type': 'weapon', 'weapon_type': 'bow', 'damage': 69, 'range': 30, 'rarity': 'legendary', 'color': color.black},
        'Void Staff': {'type': 'weapon', 'weapon_type': 'staff', 'damage': 55, 'mana_bonus': 60, 'rarity': 'legendary', 'color': color.violet, 'projectile': True, 'pierce': 8, 'debuff': 'weaken', 'debuff_value': 50},
        'Chaos Blade': {'type': 'weapon', 'weapon_type': 'sword', 'damage': 260, 'rarity': 'legendary', 'color': color.magenta},
        'Nightmare Dagger': {'type': 'weapon', 'weapon_type': 'dagger', 'damage': 50, 'rarity': 'legendary', 'color': color.black},
        'Divine Bow': {'type': 'weapon', 'weapon_type': 'bow', 'damage': 45, 'range': 30, 'rarity': 'legendary', 'color': color.gold},
        'Inferno Staff': {'type': 'weapon', 'weapon_type': 'staff', 'damage': 42, 'mana_bonus': 45, 'rarity': 'legendary', 'color': color.red, 'projectile': True, 'pierce': 7, 'debuff': 'poison', 'debuff_value': 35},
        'Frost Blade': {'type': 'weapon', 'weapon_type': 'sword', 'damage': 192, 'rarity': 'legendary', 'color': color.cyan},
        'Soul Reaper': {'type': 'weapon', 'weapon_type': 'dagger', 'damage': 38, 'rarity': 'legendary', 'color': color.violet},
        # Dungeon reward armor
        'Shadow Armor': {'type': 'armor', 'defense': 50, 'slot': 'chest', 'rarity': 'legendary', 'color': color.black},
        'Void Shield': {'type': 'armor', 'defense': 25, 'slot': 'off_hand', 'rarity': 'legendary', 'color': color.violet},
        'Nightmare Helm': {'type': 'armor', 'defense': 20, 'slot': 'head', 'rarity': 'legendary', 'color': color.black},
        # ORES - Raw materials for smelting
        'Copper Ore': {'type': 'ore', 'smelt_result': 'Copper Ingot', 'rarity': 'common', 'color': color.orange},
        'Iron Ore': {'type': 'ore', 'smelt_result': 'Iron Ingot', 'rarity': 'common', 'color': color.gray},
        'Silver Ore': {'type': 'ore', 'smelt_result': 'Silver Ingot', 'rarity': 'uncommon', 'color': color.light_gray},
        'Gold Ore': {'type': 'ore', 'smelt_result': 'Gold Ingot', 'rarity': 'uncommon', 'color': color.gold},
        'Mithril Ore': {'type': 'ore', 'smelt_result': 'Mithril Ingot', 'rarity': 'rare', 'color': color.cyan},
        'Adamantite Ore': {'type': 'ore', 'smelt_result': 'Adamantite Ingot', 'rarity': 'rare', 'color': color.violet},
        'Shadow Ore': {'type': 'ore', 'smelt_result': 'Shadow Ingot', 'rarity': 'legendary', 'color': color.black},
        'Dragon Ore': {'type': 'ore', 'smelt_result': 'Dragon Ingot', 'rarity': 'legendary', 'color': color.red},
        # INGOTS - Smelted materials for crafting
        'Copper Ingot': {'type': 'ingot', 'tier': 1, 'rarity': 'common', 'color': color.orange},
        'Iron Ingot': {'type': 'ingot', 'tier': 2, 'rarity': 'common', 'color': color.gray},
        'Silver Ingot': {'type': 'ingot', 'tier': 3, 'rarity': 'uncommon', 'color': color.light_gray},
        'Gold Ingot': {'type': 'ingot', 'tier': 4, 'rarity': 'uncommon', 'color': color.gold},
        'Mithril Ingot': {'type': 'ingot', 'tier': 5, 'rarity': 'rare', 'color': color.cyan},
        'Adamantite Ingot': {'type': 'ingot', 'tier': 6, 'rarity': 'rare', 'color': color.violet},
        'Shadow Ingot': {'type': 'ingot', 'tier': 7, 'rarity': 'legendary', 'color': color.black},
        'Dragon Ingot': {'type': 'ingot', 'tier': 8, 'rarity': 'legendary', 'color': color.red},
        'tErRoR ingot': {'type': 'special_metal', 'bonus_type': 'xp', 'bonus_value': 4.0, 'attack_speed_mult': 3.0, 'damage_mult': 4, 'tier': 9, 'rarity': 'legendary', 'color': color.rgb(255, 0, 255)},
        # Crafting components
        'Wood': {'type': 'material', 'craft_type': 'wood', 'rarity': 'common', 'color': color.brown},
        'Leather': {'type': 'material', 'craft_type': 'leather', 'rarity': 'common', 'color': color.brown},
        'Magic Crystal': {'type': 'material', 'craft_type': 'magic', 'rarity': 'rare', 'color': color.magenta},
        'Dragon Scale': {'type': 'material', 'craft_type': 'scale', 'rarity': 'legendary', 'color': color.red},
        'Void Essence': {'type': 'material', 'craft_type': 'essence', 'rarity': 'legendary', 'color': color.violet},
        # Special Dungeon Metals (drop from dungeon 7+) - provide bonuses when crafting
        # All special metals grant 4x damage multiplier
        'Void Metal': {'type': 'special_metal', 'bonus_type': 'speed', 'bonus_value': 10, 'damage_mult': 4, 'rarity': 'legendary', 'color': color.violet},
        'Life Crystal': {'type': 'special_metal', 'bonus_type': 'health', 'bonus_value': 25, 'damage_mult': 4, 'rarity': 'legendary', 'color': color.pink},
        'Swift Essence': {'type': 'special_metal', 'bonus_type': 'speed', 'bonus_value': 15, 'damage_mult': 4, 'rarity': 'legendary', 'color': color.azure},
        'Vitality Core': {'type': 'special_metal', 'bonus_type': 'health', 'bonus_value': 50, 'damage_mult': 4, 'rarity': 'legendary', 'color': color.lime},
        'Chrono Shard': {'type': 'special_metal', 'bonus_type': 'attack_speed', 'bonus_value': 2.0, 'damage_mult': 4, 'rarity': 'legendary', 'color': color.cyan},
        # Poison and Debuff metals
        'Venom Core': {'type': 'special_metal', 'bonus_type': 'poison', 'bonus_value': 15, 'damage_mult': 4, 'rarity': 'legendary', 'color': color.green},
        'Plague Essence': {'type': 'special_metal', 'bonus_type': 'poison', 'bonus_value': 25, 'damage_mult': 4, 'rarity': 'legendary', 'color': color.olive},
        'Frost Shard': {'type': 'special_metal', 'bonus_type': 'slow', 'bonus_value': 50, 'damage_mult': 4, 'rarity': 'legendary', 'color': color.white},
        'Weakness Crystal': {'type': 'special_metal', 'bonus_type': 'weaken', 'bonus_value': 30, 'damage_mult': 4, 'rarity': 'legendary', 'color': color.orange},
        'Curse Stone': {'type': 'special_metal', 'bonus_type': 'curse', 'bonus_value': 20, 'damage_mult': 4, 'rarity': 'legendary', 'color': color.black},
        # SECRET DUNGEON LOOT - Legendary biome-exclusive gear
        # Frozen Tundra secrets
        'Frostbite Blade': {'type': 'weapon', 'weapon_type': 'sword', 'damage': 200, 'rarity': 'legendary', 'color': color.cyan},
        'Glacial Staff': {'type': 'weapon', 'weapon_type': 'staff', 'damage': 50, 'mana_bonus': 80, 'rarity': 'legendary', 'color': color.azure, 'projectile': True, 'pierce': 8, 'debuff': 'slow', 'debuff_value': 60},
        'Frozen Heart Amulet': {'type': 'accessory', 'hp_bonus': 200, 'defense_bonus': 50, 'rarity': 'legendary', 'color': color.cyan},
        # Desert Wasteland secrets
        'Sandstorm Scimitar': {'type': 'weapon', 'weapon_type': 'sword', 'damage': 220, 'rarity': 'legendary', 'color': color.gold},
        "Pharaoh's Staff": {'type': 'weapon', 'weapon_type': 'staff', 'damage': 55, 'mana_bonus': 70, 'rarity': 'legendary', 'color': color.gold, 'projectile': True, 'pierce': 7, 'debuff': 'curse', 'debuff_value': 50},
        'Scarab Pendant': {'type': 'accessory', 'hp_bonus': 150, 'attack_bonus': 40, 'rarity': 'legendary', 'color': color.gold},
        # Dark Swamp secrets
        'Venomfang Dagger': {'type': 'weapon', 'weapon_type': 'dagger', 'damage': 180, 'rarity': 'legendary', 'color': color.green},
        "Witch's Curse Staff": {'type': 'weapon', 'weapon_type': 'staff', 'damage': 45, 'mana_bonus': 90, 'rarity': 'legendary', 'color': color.violet, 'projectile': True, 'pierce': 10, 'debuff': 'poison', 'debuff_value': 40},
        "Swamp King's Crown": {'type': 'accessory', 'hp_bonus': 180, 'mana_bonus': 100, 'rarity': 'legendary', 'color': color.olive},
        # Volcanic Hellscape secrets
        'Inferno Greatsword': {'type': 'weapon', 'weapon_type': 'sword', 'damage': 280, 'rarity': 'legendary', 'color': color.red},
        'Magma Core Staff': {'type': 'weapon', 'weapon_type': 'staff', 'damage': 70, 'mana_bonus': 60, 'rarity': 'legendary', 'color': color.orange, 'projectile': True, 'pierce': 6, 'debuff': 'poison', 'debuff_value': 60},
        'Dragon Scale Armor': {'type': 'armor', 'defense': 80, 'hp_bonus': 250, 'slot': 'chest', 'rarity': 'legendary', 'color': color.red},
        # Fantasy Land secrets
        "Fairy Queen's Rapier": {'type': 'weapon', 'weapon_type': 'sword', 'damage': 240, 'rarity': 'legendary', 'color': color.magenta},
        'Starlight Wand': {'type': 'weapon', 'weapon_type': 'staff', 'damage': 60, 'mana_bonus': 100, 'rarity': 'legendary', 'color': color.white, 'projectile': True, 'pierce': 12, 'debuff': 'slow', 'debuff_value': 50},
        'Unicorn Horn Ring': {'type': 'accessory', 'hp_bonus': 300, 'mana_bonus': 150, 'attack_bonus': 30, 'rarity': 'legendary', 'color': color.magenta},
        # DREAM MODE EXCLUSIVES - Only drop in dream mode
        'Void Crystal': {'type': 'material', 'craft_type': 'void', 'rarity': 'legendary', 'color': color.rgb(50, 0, 100)},
        'Shadow Essence': {'type': 'material', 'craft_type': 'shadow', 'rarity': 'legendary', 'color': color.rgb(30, 0, 50)},
        'Nightmare Fragment': {'type': 'material', 'craft_type': 'nightmare', 'rarity': 'legendary', 'color': color.rgb(100, 0, 150)},
    }

    # Crafting recipes - material combinations to create items
    CRAFTING_RECIPES = {
        # Swords: ingot + wood
        ('Iron Ingot', 'Wood'): {'result': 'Iron Sword', 'bonus_damage': 0},
        ('Iron Ingot', 'Iron Ingot', 'Wood'): {'result': 'Steel Sword', 'bonus_damage': 2},
        ('Mithril Ingot', 'Mithril Ingot', 'Wood'): {'result': 'Fire Blade', 'bonus_damage': 5},
        ('Dragon Ingot', 'Dragon Ingot', 'Dragon Scale'): {'result': 'Dragon Slayer', 'bonus_damage': 10},
        ('Shadow Ingot', 'Shadow Ingot', 'Void Essence'): {'result': 'Chaos Blade', 'bonus_damage': 15},
        # Bows: wood + string (leather)
        ('Wood', 'Leather'): {'result': 'Wooden Bow', 'bonus_damage': 0},
        ('Wood', 'Wood', 'Leather'): {'result': 'Hunter Bow', 'bonus_damage': 2},
        ('Mithril Ingot', 'Wood', 'Leather'): {'result': 'Elven Bow', 'bonus_damage': 5},
        ('Dragon Ingot', 'Wood', 'Dragon Scale'): {'result': 'Dragon Bow', 'bonus_damage': 10},
        ('Shadow Ingot', 'Wood', 'Void Essence'): {'result': 'Shadow Bow', 'bonus_damage': 15},
        # Staffs: wood + magic crystal
        ('Wood', 'Magic Crystal'): {'result': 'Wooden Staff', 'bonus_damage': 0},
        ('Silver Ingot', 'Wood', 'Magic Crystal'): {'result': 'Crystal Staff', 'bonus_damage': 3},
        ('Gold Ingot', 'Wood', 'Magic Crystal'): {'result': 'Fire Staff', 'bonus_damage': 5},
        ('Mithril Ingot', 'Magic Crystal', 'Magic Crystal'): {'result': 'Arcane Staff', 'bonus_damage': 8},
        ('Shadow Ingot', 'Magic Crystal', 'Void Essence'): {'result': 'Void Staff', 'bonus_damage': 15},
        # Armor: multiple ingots + leather
        ('Leather', 'Leather'): {'result': 'Leather Armor', 'bonus_defense': 0},
        ('Iron Ingot', 'Iron Ingot', 'Leather'): {'result': 'Iron Armor', 'bonus_defense': 2},
        ('Iron Ingot', 'Iron Ingot', 'Iron Ingot', 'Leather'): {'result': 'Steel Armor', 'bonus_defense': 4},
        ('Dragon Ingot', 'Dragon Ingot', 'Dragon Scale'): {'result': 'Dragon Armor', 'bonus_defense': 10},
        ('Shadow Ingot', 'Shadow Ingot', 'Void Essence'): {'result': 'Shadow Armor', 'bonus_defense': 15},
    }

    # Wave rewards by dungeon tier - items given every wave
    WAVE_LOOT_TIERS = {
        # Tier 1: Dungeons 1-2 (Easy)
        'tier1': ['Health Potion', 'Mana Potion', 'Stamina Potion', 'Arrow', 'Iron Sword', 'Wooden Bow', 'Wooden Staff', 'Leather Armor'],
        # Tier 2: Dungeons 3-4 (Normal)
        'tier2': ['Greater Health Potion', 'Greater Mana Potion', 'Steel Sword', 'Hunter Bow', 'Crystal Staff', 'Iron Armor', 'Iron Helmet', 'Iron Shield'],
        # Tier 3: Dungeons 5-6 (Hard)
        'tier3': ['Fire Blade', 'Elven Bow', 'Fire Staff', 'Steel Armor', 'Steel Helmet', 'Tower Shield', 'Fire Scroll', 'Lightning Scroll'],
        # Tier 4: Dungeons 7-8 (Very Hard) - Special metals start dropping
        'tier4': ['Dragon Slayer', 'Dragon Bow', 'Arcane Staff', 'Dragon Armor', 'Divine Staff', 'Lightning Scroll', 'Void Metal', 'Life Crystal', 'Swift Essence', 'Venom Core', 'Frost Shard'],
        # Tier 5: Dungeons 9-10 (Extreme/Nightmare) - Legendary + rare special metals
        'tier5': ['Frost Blade', 'Divine Bow', 'Inferno Staff', 'Soul Reaper', 'Shadow Armor', 'Nightmare Helm', 'Vitality Core', 'Chrono Shard', 'Void Metal', 'Life Crystal', 'Plague Essence', 'Weakness Crystal', 'Curse Stone'],
    }

    # Milestone wave rewards (wave 5 and 10) - GUARANTEED good items
    MILESTONE_REWARDS = {
        # Dungeon 1-2: Wave 5 milestone
        1: {5: ['Steel Sword', 'Hunter Bow', 'Iron Armor']},
        2: {5: ['Fire Blade', 'Elven Bow', 'Steel Armor']},
        # Dungeon 3-4
        3: {5: ['Fire Blade', 'Elven Bow', 'Fire Staff'], 10: ['Dragon Slayer', 'Dragon Bow']},
        4: {5: ['Dragon Slayer', 'Dragon Bow', 'Arcane Staff'], 10: ['Dragon Armor', 'Divine Staff']},
        # Dungeon 5-6
        5: {5: ['Dragon Slayer', 'Dragon Bow', 'Dragon Armor'], 10: ['Frost Blade', 'Divine Bow', 'Inferno Staff']},
        6: {5: ['Frost Blade', 'Divine Bow', 'Inferno Staff'], 10: ['Soul Reaper', 'Shadow Armor']},
        # Dungeon 7-8
        7: {5: ['Frost Blade', 'Divine Bow', 'Soul Reaper'], 10: ['Chaos Blade', 'Shadow Bow', 'Void Staff']},
        8: {5: ['Chaos Blade', 'Shadow Bow', 'Void Staff'], 10: ['Shadow Armor', 'Nightmare Helm', 'Void Shield']},
        # Dungeon 9-10 - BEST REWARDS
        9: {5: ['Chaos Blade', 'Shadow Bow', 'Void Staff', 'Shadow Armor'], 10: ['Nightmare Dagger', 'Nightmare Helm', 'Void Shield']},
        10: {1: ['Dragon Slayer', 'Dragon Bow', 'Dragon Armor'],  # Wave 1 reward!
             5: ['Chaos Blade', 'Shadow Bow', 'Void Staff', 'Shadow Armor'],
             10: ['Shadow Bow', 'Void Staff', 'Chaos Blade', 'Nightmare Dagger', 'Void Shield', 'Nightmare Helm']},
    }

    RARITY_COLORS = {
        'common': color.white,
        'uncommon': color.green,
        'rare': color.blue,
        'legendary': color.gold
    }

    @classmethod
    def create(cls, name):
        """Create an item dictionary from item name."""
        if name in cls.ITEM_DATA:
            item = {'name': name}
            item.update(cls.ITEM_DATA[name])
            return item
        return None

    @classmethod
    def get_random_loot(cls, rarity_weights=None):
        """Get random loot based on rarity."""
        if rarity_weights is None:
            rarity_weights = {'common': 60, 'uncommon': 25, 'rare': 12, 'legendary': 3}

        # Build weighted list
        weighted_items = []
        for name, data in cls.ITEM_DATA.items():
            rarity = data.get('rarity', 'common')
            weight = rarity_weights.get(rarity, 10)
            weighted_items.extend([name] * weight)

        if weighted_items:
            chosen = random.choice(weighted_items)
            return cls.create(chosen)
        return None


class Chest(Entity):
    """Loot chest that can be opened."""
    def __init__(self, position, chest_type='common', **kwargs):
        chest_colors = {
            'common': color.brown,
            'uncommon': color.green,
            'rare': color.blue,
            'legendary': color.gold
        }
        super().__init__(
            model='cube',
            texture='white_cube',
            color=chest_colors.get(chest_type, color.brown),
            scale=(1.2, 0.8, 0.8),
            position=position,
            collider='box'
        )
        self.chest_type = chest_type
        self.opened = False
        self.loot = self._generate_loot()

        # Chest lid
        self.lid = Entity(
            parent=self,
            model='cube',
            texture='white_cube',
            color=chest_colors.get(chest_type, color.brown) * 0.8,
            scale=(1, 0.2, 1),
            position=(0, 0.5, 0)
        )

        # Lock/decoration
        Entity(
            parent=self,
            model='cube',
            texture='white_cube',
            color=color.gold if chest_type == 'legendary' else color.light_gray,
            scale=(0.2, 0.3, 0.1),
            position=(0, 0.1, 0.45)
        )

        # Label
        self.label = Text(
            text=f'{chest_type.title()} Chest',
            parent=self,
            y=1,
            scale=8,
            billboard=True,
            origin=(0, 0),
            color=Item.RARITY_COLORS.get(chest_type, color.white)
        )
        self.interact_text = Text(
            text='[E] Open',
            parent=self,
            y=0.7,
            scale=6,
            billboard=True,
            origin=(0, 0),
            color=color.yellow
        )

    def _generate_loot(self):
        """Generate loot based on chest type."""
        loot = []
        loot_count = {'common': 2, 'uncommon': 3, 'rare': 4, 'legendary': 5}.get(self.chest_type, 2)

        # Adjust rarity weights based on chest type
        if self.chest_type == 'legendary':
            weights = {'common': 20, 'uncommon': 30, 'rare': 35, 'legendary': 15}
        elif self.chest_type == 'rare':
            weights = {'common': 30, 'uncommon': 40, 'rare': 25, 'legendary': 5}
        elif self.chest_type == 'uncommon':
            weights = {'common': 50, 'uncommon': 35, 'rare': 13, 'legendary': 2}
        else:
            weights = {'common': 70, 'uncommon': 22, 'rare': 7, 'legendary': 1}

        for _ in range(loot_count):
            item = Item.get_random_loot(weights)
            if item:
                loot.append(item)

        # Always add some gold
        gold_amount = {'common': 10, 'uncommon': 25, 'rare': 50, 'legendary': 100}.get(self.chest_type, 10)
        gold_amount += random.randint(0, gold_amount)

        return {'items': loot, 'gold': gold_amount}

    def open_chest(self):
        """Open the chest and return loot."""
        if self.opened:
            return None

        self.opened = True
        self.lid.rotation_x = -110  # Open lid animation
        self.interact_text.text = 'Opened!'
        self.interact_text.color = color.gray
        self.color = self.color * 0.5  # Darken chest
        return self.loot


class Game:
    """Main game controller."""

    def __init__(self):
        self.app = Ursina(
            title=config.GAME_TITLE,
            borderless=False,
            fullscreen=config.FULLSCREEN,
            development_mode=True,
            size=(config.WINDOW_WIDTH, config.WINDOW_HEIGHT)
        )

        # Game state
        self.username = None
        self.character = None
        self.player = None
        self.game_active = False
        self.enemies = []
        self.pet = None
        self.pet_book_open = False
        self.pet_book_ui = []
        self.pet_book_selection = 0
        self.available_pets = ['Wolf Pup']
        self.portals = []
        self.secret_portals = []
        self.in_secret_dungeon = False
        self.current_secret_biome = None
        self.current_area = 'village'

        # Chat/message log
        self.chat_messages = []
        self.chat_ui = []
        self.max_chat_messages = 5

        # Pet UI
        self.pet_ui = []
        self.pet_ui_visible = True

        # Training state
        self.training_active = False
        self.training_ui = []
        self.training_skill = None
        self.training_npc = None

        # Teach minigame state
        self.teach_active = False
        self.teach_ui = []
        self.teach_bar_pos = 0
        self.teach_bar_direction = 1
        self.teach_target_zone = 0.5
        self.teach_skill = None

        # World entities (for cleanup)
        self.world_entities = []

        # Chests in the world
        self.chests = []

        # Equipped weapon visual
        self.weapon_visual = None
        self.equipped_weapon = None
        self.attack_cooldown = 0

        # Start with login screen
        self.show_login_screen()

    def add_chat_message(self, message, msg_color=color.white):
        """Add a message to the chat log."""
        self.chat_messages.append({'text': message, 'color': msg_color, 'time': time.time()})
        if len(self.chat_messages) > self.max_chat_messages:
            self.chat_messages.pop(0)
        self.update_chat_display()

    def update_chat_display(self):
        """Update the chat display UI."""
        # Clear old chat UI
        for ui in self.chat_ui:
            destroy(ui)
        self.chat_ui = []

        if not self.chat_messages:
            return

        # Chat panel background
        panel_height = 0.03 + len(self.chat_messages) * 0.035
        chat_bg = Entity(
            parent=camera.ui,
            model='quad',
            texture='white_cube',
            color=color.rgba(0, 0, 0, 180),
            scale=(0.45, panel_height),
            position=(-0.65, -0.18 - panel_height / 2),
            z=0.1
        )
        self.chat_ui.append(chat_bg)

        # Chat title
        chat_title = Text(
            text='Chat',
            position=(-0.85, -0.14),
            scale=0.8,
            color=color.gray
        )
        self.chat_ui.append(chat_title)

        # Create chat messages
        for i, msg in enumerate(self.chat_messages):
            age = time.time() - msg['time']
            alpha = max(0.3, 1 - (age / 15))  # Fade out slower, keep minimum visibility

            chat_text = Text(
                text=msg['text'],
                position=(-0.85, -0.18 - i * 0.035),
                scale=0.8,
                color=color.rgba(msg['color'].r * 255, msg['color'].g * 255, msg['color'].b * 255, alpha * 255)
            )
            self.chat_ui.append(chat_text)

    def update_pet_ui(self):
        """Update the pet status UI panel."""
        # Clear old pet UI
        for ui in self.pet_ui:
            destroy(ui)
        self.pet_ui = []

        if not self.pet_ui_visible:
            # Show mini button to reopen
            open_btn = Button(
                text='PET',
                scale=(0.08, 0.035),
                position=(0.85, 0.47),
                color=color.dark_gray,
                highlight_color=color.gray,
                on_click=self.toggle_pet_ui
            )
            self.pet_ui.append(open_btn)
            return

        # Pet panel border (behind background)
        border_color = color.lime if self.pet else color.dark_gray
        pet_border = Entity(
            parent=camera.ui,
            model='quad',
            texture='white_cube',
            color=border_color,
            scale=(0.28, 0.22),
            position=(0.75, 0.36),
            z=0.2
        )
        self.pet_ui.append(pet_border)

        # Pet panel background (top right)
        pet_bg = Entity(
            parent=camera.ui,
            model='quad',
            texture='white_cube',
            color=color.rgba(20, 20, 20, 230),
            scale=(0.27, 0.21),
            position=(0.75, 0.36),
            z=0.1
        )
        self.pet_ui.append(pet_bg)

        # X button to close
        close_btn = Button(
            text='X',
            scale=(0.03, 0.03),
            position=(0.87, 0.45),
            color=color.red,
            highlight_color=color.orange,
            on_click=self.toggle_pet_ui
        )
        self.pet_ui.append(close_btn)

        # Pet title
        pet_title = Text(
            text='[ PET ]',
            position=(0.64, 0.45),
            scale=1.1,
            color=color.lime if self.pet else color.gray
        )
        self.pet_ui.append(pet_title)

        if not self.pet:
            # No pet message
            no_pet_text = Text(
                text='No pet yet!',
                position=(0.64, 0.38),
                scale=1.1,
                color=color.red
            )
            self.pet_ui.append(no_pet_text)

            # Get Pet button
            get_pet_btn = Button(
                text='Get Pet (E near Book)',
                scale=(0.2, 0.04),
                position=(0.75, 0.32),
                color=color.azure,
                highlight_color=color.cyan,
                text_color=color.white
            )
            self.pet_ui.append(get_pet_btn)

            hint_text = Text(
                text='Find the Pet Book',
                position=(0.64, 0.27),
                scale=0.8,
                color=color.gray
            )
            self.pet_ui.append(hint_text)
            return

        # Pet name and type
        pet_name = Text(
            text=self.pet.pet_type,
            position=(0.64, 0.40),
            scale=1.3,
            color=color.white
        )
        self.pet_ui.append(pet_name)

        # Skills header with slots
        skills_header = Text(
            text=f'Skills [{len(self.pet.skills)}/{self.pet.max_skills}]:',
            position=(0.64, 0.35),
            scale=0.9,
            color=color.gray
        )
        self.pet_ui.append(skills_header)

        # Pet skills
        if self.pet.skills:
            for i, skill in enumerate(self.pet.skills):
                skill_text = Text(
                    text=f'> {skill}',
                    position=(0.64, 0.31 - i * 0.035),
                    scale=0.8,
                    color=color.yellow
                )
                self.pet_ui.append(skill_text)
        else:
            no_skills = Text(
                text='(no skills yet)',
                position=(0.64, 0.31),
                scale=0.8,
                color=color.orange
            )
            self.pet_ui.append(no_skills)

        # Train button
        train_btn = Button(
            text='Train (E near Trainer)',
            scale=(0.18, 0.035),
            position=(0.75, 0.22),
            color=color.lime,
            highlight_color=color.green,
            text_color=color.black
        )
        self.pet_ui.append(train_btn)

    def toggle_pet_ui(self):
        """Toggle pet UI visibility."""
        self.pet_ui_visible = not self.pet_ui_visible
        self.update_pet_ui()

    def show_login_screen(self):
        """Show the username input screen."""
        self.login_screen = LoginScreen(on_login_callback=self.on_login)

    def on_login(self, username):
        """Called when user submits their username."""
        self.username = username
        print(f"Welcome, {username}!")
        self.show_main_menu()

    def show_main_menu(self):
        """Show the main menu."""
        self.main_menu = MainMenu(
            username=self.username,
            on_play_callback=self.start_game,
            on_quit_callback=self.quit_game
        )

    def start_game(self, new_game=True):
        """Start the actual game."""
        if new_game:
            self.show_character_creator()
        else:
            self.load_game()

    def show_character_creator(self):
        """Show the character creation screen."""
        self.character_creator = CharacterCreator(
            username=self.username,
            on_complete_callback=self.on_character_created
        )

    def on_character_created(self, race, char_class):
        """Called when character creation is complete."""
        # Set dream mode before creating character
        self.dream_mode = (self.username.lower() == 'dream')
        # Set error404 game mode for extreme endgame
        self.error404_mode = (self.username.lower() == '404rorre')
        
        self.character = Character(
            name=self.username,
            race=race,
            char_class=char_class,
            dream_mode=self.dream_mode
        )
        # Ensure full HP/Mana at start
        self.character.health = self.character.max_health
        self.character.mana = self.character.max_mana
        self.character.stamina = self.character.max_stamina
        print(f"Created {self.character.name} - {config.RACES[race]['name']} {config.CLASSES[char_class]['name']}")
        if self.dream_mode:
            print(f"Dream Mode ACTIVE: +4 to all stats!")
        if self.error404_mode:
            print(f"ERROR 404 GAME MODE ACTIVE: EXTREME ENDGAME DIFFICULTY!")
        self.setup_game_world()

    def setup_game_world(self):
        """Set up the game world."""
        self.game_active = True
        self.inventory_open = False
        self.dialogue_open = False
        self.dialogue_ui = []
        self.inventory_ui = []
        self.smelting_open = False
        self.smelting_ui = []
        self.crafting_open = False
        self.crafting_ui = []
        self.craft_slots = [None, None, None, None, None]  # 5 material slots for crafting
        self.selected_hotbar = 0

        # Dream mode already set in on_character_created
        self.dream_portal = None  # Portal back to normal world
        
        # Error 404 game mode state
        self.error404_glitched_room = None  # Transition room
        self.error404_portal = None  # White portal to error world
        self.error404_turrets = []  # Turrets around portal
        self.error_debuff_cooldown = 0  # For error teleport debuff
        
        # Dungeon state
        self.in_dungeon = False
        self.current_dungeon = 0
        self.dungeon_entities = []
        self.dungeon_exit = None
        self.secret_base_portal = None
        self.secret_base_anvil = None
        self.in_secret_base = False
        self.in_error404_dungeon = False
        self.dungeon_wave = 0
        self.wave_text = None
        self.wave_cooldown = 0
        
        # Enemy respawn system
        self.enemy_respawn_timer = 0
        self.enemy_respawn_delay = 30  # Respawn enemies every 30 seconds outside dungeons

        # Player inventory with starting items based on class
        self.inventory = self._get_starting_inventory()

        # Hotbar references inventory indices
        self.hotbar = [0, 1, 2, 3, None, None, None, None]

        # Equip starting weapon
        if self.inventory[0] and self.inventory[0].get('type') == 'weapon':
            self.equipped_weapon = self.inventory[0]

        # Equipped armor slots
        self.equipped_armor = {
            'head': None,
            'chest': None,
            'off_hand': None
        }

        # Auto-equip starting armor
        for item in self.inventory:
            if item and item.get('type') == 'armor':
                slot = item.get('slot')
                if slot and slot in self.equipped_armor and not self.equipped_armor[slot]:
                    self.equipped_armor[slot] = item

        # Dream Mode - Dark and scary atmosphere using lighting
        if self.dream_mode:
            # Dark ambient lighting
            scene.fog_density = 0.03
            scene.fog_color = color.rgb(5, 0, 10)
            # Make everything darker with ambient light reduction
            from ursina import DirectionalLight, AmbientLight
            # Very dark ambient light for dream mode
            AmbientLight(color=color.rgb(20, 10, 30))
            # Dim directional light
            DirectionalLight(y=2, z=3, shadows=True, rotation=(45, -45, 45))
        else:
            # Normal lighting with proper shading
            from ursina import DirectionalLight, AmbientLight
            # Bright ambient light for normal mode
            AmbientLight(color=color.rgb(100, 100, 100))
            # Normal directional light
            DirectionalLight(y=2, z=3, shadows=True, rotation=(45, -45, 45))
            # Normal fog
            scene.fog_density = 0

        # Create massive ground (looks endless)
        ground_color = color.dark_gray if self.dream_mode else color.green
        ground = Entity(
            model='cube',
            scale=(2000, 1, 2000),
            position=(0, -0.5, 0),
            texture='white_cube',
            color=ground_color,
            collider='box',
            unlit=self.dream_mode  # Unlit in dream mode
        )
        self.world_entities.append(ground)

        # Village stone floor (no collider - ground handles walking)
        village_floor_color = color.black if self.dream_mode else color.light_gray
        village_floor = Entity(
            model='cube',
            scale=(60, 0.2, 60),
            position=(0, 0.1, 0),
            texture='white_cube',
            color=village_floor_color,
            unlit=self.dream_mode
        )
        self.world_entities.append(village_floor)

        # No boundary walls - open world exploration

        # Sky background - use a large sphere
        sky_color = color.black if self.dream_mode else color.azure
        sky = Entity(
            model='sphere',
            texture='white_cube',
            color=sky_color,
            scale=1200,
            double_sided=True,
            unlit=self.dream_mode
        )
        self.world_entities.append(sky)

        # Create player - spawn in center of village facing the Pet Book
        self.player = FirstPersonController()
        self.player.speed = 16 if self.dream_mode else 8  # 2x speed for dream mode
        self.player.jump_height = 2
        self.player.gravity = 1
        # Error404 mode: spawn in glitched transition room
        if self.error404_mode:
            self.player.position = Vec3(1000, 2, 1000)  # Glitched room spawn
        else:
            self.player.position = Vec3(0, 2, 15)  # Spawn inside normal village
        self.player.rotation_y = 180  # Face toward Pet Book and center
        self.player.mouse_sensitivity = Vec2(40, 40)
        self.player.game_ref = self  # Reference for enemies to access game

        # Add world objects
        self.create_village()
        # Error404 mode: create glitched room and Error Village
        if self.error404_mode:
            self.create_glitched_transition_room()
            self.create_error_village()
        self.create_wilderness()
        self.create_portals()

        # Spawn enemies OUTSIDE village
        self.spawn_enemies()

        # Create HUD
        self.create_hud()
        self.update_pet_ui()

        # Spawn chests in the world
        self.spawn_chests()

        # Create weapon visual attached to camera
        self.create_weapon_visual()

        # Welcome message
        if self.error404_mode:
            self.add_chat_message("this wasnt real it was all a dream this is reality? enjoy your way out you going to destroy the code to be free", color.red)
            self.add_chat_message("ERROR 404: GAME NOT FOUND", color.rgb(255, 0, 255))
            self.add_chat_message("Everything is a boss. Survive.", color.rgb(255, 100, 255))
        elif self.dream_mode:
            self.add_chat_message(f"The shadows whisper your name, {self.username}...", color.rgb(150, 0, 200))
            self.add_chat_message("The darkness surrounds you. Find the hidden portal to escape...", color.rgb(100, 0, 150))
        else:
            self.add_chat_message(f"Welcome to SkillMine, {self.username}!", color.cyan)
        if not self.error404_mode:
            self.add_chat_message("Use portals to travel between areas.", color.yellow)
        if self.equipped_weapon:
            self.add_chat_message(f"Equipped: {self.equipped_weapon['name']}", color.yellow)

    def _get_starting_inventory(self):
        """Get starting inventory based on character class."""
        inventory = [None] * 16  # 16 slots

        # Special starting items for chezwhopper
        if self.username.lower() == 'chezwhopper':
            # Create special Chrono Bow
            chrono_bow = {
                'name': 'Chrono Bow',
                'type': 'weapon',
                'weapon_type': 'bow',
                'damage': 100,
                'attack_speed_mult': 10.0,  # 10x attack speed!
                'color': color.cyan,
                'tier': 8,
                'rarity': 'legendary'
            }
            # Create special Sonic Bow
            sonic_bow = {
                'name': 'Sonic Bow',
                'type': 'weapon',
                'weapon_type': 'bow',
                'damage': 1,
                'attack_speed_mult': 250.0,  # 250x attack speed!
                'xp_multiplier': 10.0,  # 10x XP on kills!
                'color': color.rgb(0, 100, 255),  # Sonic blue
                'tier': 9,
                'rarity': 'legendary'
            }
            inventory[0] = chrono_bow
            inventory[1] = sonic_bow
            inventory[2] = Item.create('Chrono Shard')
            inventory[3] = Item.create('Chrono Shard')
            inventory[4] = Item.create('Chrono Shard')
            inventory[5] = Item.create('Shadow Ore')
            inventory[6] = Item.create('Shadow Ore')
            inventory[7] = Item.create('Health Potion')
            inventory[8] = Item.create('Mana Potion')
            inventory[9] = Item.create('Arrow')
            inventory[10] = Item.create('Arrow')
            inventory[11] = Item.create('Arrow')
            return inventory

        # Class-specific starting weapon
        class_weapons = {
            'warrior': 'Iron Sword',
            'mage': 'Wooden Staff',
            'rogue': 'Iron Dagger',
            'ranger': 'Wooden Bow',
            'paladin': 'Wooden Healing Staff',
        }

        # Get starting weapon for class
        weapon_name = class_weapons.get(self.character.char_class, 'Wooden Sword')
        inventory[0] = Item.create(weapon_name)

        # Everyone gets health and mana potions
        inventory[1] = Item.create('Health Potion')
        inventory[2] = Item.create('Health Potion')
        inventory[3] = Item.create('Mana Potion')

        # Class-specific extras
        if self.character.char_class == 'mage':
            inventory[4] = Item.create('Fire Scroll')
            inventory[5] = Item.create('Greater Mana Potion')
            inventory[6] = Item.create('Leather Hood')
        elif self.character.char_class == 'warrior':
            inventory[4] = Item.create('Iron Shield')
            inventory[5] = Item.create('Leather Armor')
            inventory[6] = Item.create('Iron Helmet')
        elif self.character.char_class == 'rogue':
            inventory[4] = Item.create('Stamina Potion')
            inventory[5] = Item.create('Stamina Potion')
            inventory[6] = Item.create('Leather Armor')
        elif self.character.char_class == 'ranger':
            inventory[4] = Item.create('Arrow')
            inventory[5] = Item.create('Arrow')
            inventory[6] = Item.create('Leather Armor')
        elif self.character.char_class == 'paladin':
            inventory[4] = Item.create('Iron Shield')
            inventory[5] = Item.create('Greater Health Potion')
            inventory[6] = Item.create('Iron Armor')
        else:
            inventory[4] = Item.create('Leather Armor')

        return inventory

    def create_weapon_visual(self):
        """Create a visual weapon model attached to the camera."""
        if self.weapon_visual:
            destroy(self.weapon_visual)
            self.weapon_visual = None

        if not self.equipped_weapon:
            return

        weapon_color = self.equipped_weapon.get('color', color.light_gray)
        weapon_type = self.equipped_weapon.get('weapon_type', 'sword')

        # Create weapon container attached to camera
        self.weapon_visual = Entity(parent=camera)

        if weapon_type == 'sword':
            # SWORD - Long blade with crossguard
            # Blade
            blade = Entity(
                parent=self.weapon_visual,
                model='cube',
                texture='white_cube',
                color=weapon_color,
                scale=(0.06, 0.06, 0.6),
                position=(0.4, -0.3, 0.7),
                rotation=(15, -10, 0)
            )
            # Crossguard
            Entity(
                parent=blade,
                model='cube',
                texture='white_cube',
                color=color.dark_gray,
                scale=(3, 1, 0.15),
                position=(0, 0, -0.45)
            )
            # Handle
            Entity(
                parent=blade,
                model='cube',
                texture='white_cube',
                color=color.brown,
                scale=(1.3, 1.3, 0.25),
                position=(0, 0, -0.55)
            )
            # Pommel
            Entity(
                parent=blade,
                model='cube',
                texture='white_cube',
                color=color.gold,
                scale=(1.5, 1.5, 0.1),
                position=(0, 0, -0.65)
            )

        elif weapon_type == 'dagger':
            # DAGGER - Short blade
            blade = Entity(
                parent=self.weapon_visual,
                model='cube',
                texture='white_cube',
                color=weapon_color,
                scale=(0.04, 0.04, 0.3),
                position=(0.35, -0.25, 0.5),
                rotation=(20, -15, 0)
            )
            # Crossguard
            Entity(
                parent=blade,
                model='cube',
                texture='white_cube',
                color=color.dark_gray,
                scale=(2.5, 1, 0.15),
                position=(0, 0, -0.4)
            )
            # Handle
            Entity(
                parent=blade,
                model='cube',
                texture='white_cube',
                color=color.brown,
                scale=(1.5, 1.5, 0.35),
                position=(0, 0, -0.55)
            )

        elif weapon_type == 'staff':
            # STAFF - Long wooden pole with crystal top
            pole = Entity(
                parent=self.weapon_visual,
                model='cube',
                texture='white_cube',
                color=color.brown,
                scale=(0.06, 0.06, 1.0),
                position=(0.35, -0.4, 0.8),
                rotation=(25, -10, 0)
            )
            # Crystal orb on top
            Entity(
                parent=pole,
                model='cube',
                texture='white_cube',
                color=weapon_color,
                scale=(2.5, 2.5, 0.15),
                position=(0, 0, 0.52)
            )
            # Crystal glow
            Entity(
                parent=pole,
                model='cube',
                texture='white_cube',
                color=weapon_color * 1.5,
                scale=(1.5, 1.5, 0.1),
                position=(0, 0, 0.55)
            )
            # Metal bands
            Entity(
                parent=pole,
                model='cube',
                texture='white_cube',
                color=color.gold,
                scale=(1.3, 1.3, 0.08),
                position=(0, 0, 0.3)
            )

        elif weapon_type == 'healing_staff':
            # HEALING STAFF - Staff with glowing cross/orb
            pole = Entity(
                parent=self.weapon_visual,
                model='cube',
                texture='white_cube',
                color=color.white,
                scale=(0.05, 0.05, 0.9),
                position=(0.35, -0.4, 0.75),
                rotation=(25, -10, 0)
            )
            # Holy cross top (vertical)
            Entity(
                parent=pole,
                model='cube',
                texture='white_cube',
                color=weapon_color,
                scale=(1.5, 1.5, 0.2),
                position=(0, 0, 0.5)
            )
            # Holy cross top (horizontal)
            Entity(
                parent=pole,
                model='cube',
                texture='white_cube',
                color=weapon_color,
                scale=(3, 1.5, 0.1),
                position=(0, 0, 0.48)
            )
            # Glow effect
            Entity(
                parent=pole,
                model='cube',
                texture='white_cube',
                color=color.lime,
                scale=(1, 1, 0.15),
                position=(0, 0, 0.52)
            )

        elif weapon_type == 'bow':
            # BOW - Curved shape with string
            # Main bow body (curved using multiple segments)
            bow_center = Entity(
                parent=self.weapon_visual,
                model='cube',
                texture='white_cube',
                color=weapon_color,
                scale=(0.04, 0.5, 0.04),
                position=(0.35, -0.3, 0.6),
                rotation=(0, -20, 15)
            )
            # Upper limb
            Entity(
                parent=bow_center,
                model='cube',
                texture='white_cube',
                color=weapon_color,
                scale=(1, 0.6, 1),
                position=(0, 0.55, -0.1),
                rotation=(30, 0, 0)
            )
            # Lower limb
            Entity(
                parent=bow_center,
                model='cube',
                texture='white_cube',
                color=weapon_color,
                scale=(1, 0.6, 1),
                position=(0, -0.55, -0.1),
                rotation=(-30, 0, 0)
            )
            # Bowstring (vertical line)
            Entity(
                parent=bow_center,
                model='cube',
                texture='white_cube',
                color=color.white,
                scale=(0.3, 2.2, 0.3),
                position=(0, 0, -0.15)
            )
            # Arrow nocked
            Entity(
                parent=bow_center,
                model='cube',
                texture='white_cube',
                color=color.brown,
                scale=(0.4, 0.4, 8),
                position=(0, 0, 0.3)
            )
            # Arrowhead
            Entity(
                parent=bow_center,
                model='cube',
                texture='white_cube',
                color=color.light_gray,
                scale=(0.6, 0.6, 1.5),
                position=(0, 0, 0.65)
            )

        else:
            # Default weapon (fallback)
            Entity(
                parent=self.weapon_visual,
                model='cube',
                texture='white_cube',
                color=weapon_color,
                scale=(0.08, 0.08, 0.5),
                position=(0.4, -0.3, 0.6),
                rotation=(15, -10, 0)
            )

    def swing_weapon(self):
        """Animate weapon swing based on weapon type."""
        if not self.weapon_visual or self.attack_cooldown > 0:
            return

        weapon_type = self.equipped_weapon.get('weapon_type', 'sword') if self.equipped_weapon else 'sword'

        # Get attack speed multiplier from equipped weapon (Chrono Shard stacks!)
        attack_speed_mult = 1.0
        if self.equipped_weapon:
            attack_speed_mult = self.equipped_weapon.get('attack_speed_mult', 1.0)

        base_cooldown = 0.5

        if weapon_type == 'sword':
            # Sword slash
            base_cooldown = 0.5
            self.weapon_visual.animate_position((0.5, -0.2, 0.5), duration=0.1)
            self.weapon_visual.animate_rotation((0, 0, -45), duration=0.1)
            invoke(lambda: self.weapon_visual.animate_position((0, 0, 0), duration=0.2), delay=0.15)
            invoke(lambda: self.weapon_visual.animate_rotation((0, 0, 0), duration=0.2), delay=0.15)

        elif weapon_type == 'dagger':
            # Quick stab
            base_cooldown = 0.3  # Faster attacks
            self.weapon_visual.animate_position((0, 0, 0.3), duration=0.08)
            invoke(lambda: self.weapon_visual.animate_position((0, 0, 0), duration=0.1), delay=0.1)

        elif weapon_type == 'staff' or weapon_type == 'healing_staff':
            # Staff thrust
            base_cooldown = 0.5
            self.weapon_visual.animate_position((0, 0.1, 0.2), duration=0.15)
            invoke(lambda: self.weapon_visual.animate_position((0, 0, 0), duration=0.2), delay=0.2)

        elif weapon_type == 'bow':
            # Bow draw and release
            base_cooldown = 0.8  # Slower but ranged
            self.weapon_visual.animate_scale((1.1, 1.1, 1.1), duration=0.3)
            invoke(lambda: self.weapon_visual.animate_scale((1, 1, 1), duration=0.1), delay=0.35)

        # Apply attack speed multiplier (Chrono Shard: 2x speed = half cooldown)
        if self.dream_mode:
            attack_speed_mult *= 2.0  # Dream mode 2x attack speed
        if self.error404_mode:
            attack_speed_mult *= 3.0  # ERROR 404 mode 3x attack speed
        self.attack_cooldown = base_cooldown / attack_speed_mult

    def shoot_arrow(self):
        """Shoot an arrow (for bow users)."""
        if not self.equipped_weapon or self.equipped_weapon.get('weapon_type') != 'bow':
            return False

        if self.attack_cooldown > 0:
            return False

        # Apply attack speed from Chrono Shard
        attack_speed_mult = self.equipped_weapon.get('attack_speed_mult', 1.0)
        if self.dream_mode:
            attack_speed_mult *= 2.0  # Dream mode 2x attack speed
        if self.error404_mode:
            attack_speed_mult *= 3.0  # ERROR 404 mode 3x attack speed
        self.attack_cooldown = 0.8 / attack_speed_mult
        self.swing_weapon()

        # Get bow range
        bow_range = self.equipped_weapon.get('range', 15)

        # Find enemies in range
        for enemy in self.enemies[:]:
            if enemy.health <= 0:
                continue
            dist = distance(self.player, enemy)
            if dist < bow_range:
                # Save enemy data before take_damage (which can destroy it)
                enemy_name = enemy.enemy_name
                enemy_pos = Vec3(enemy.position)
                enemy_xp = enemy.xp_value
                
                # Calculate damage
                base_damage = self.character.get_attack_power()
                weapon_damage = self.equipped_weapon.get('damage', 0)
                
                # Add Injector Soul bonus (+6 damage per soul)
                injector_bonus = self.equipped_weapon.get('injector_soul_bonus', 0)
                
                total_damage = base_damage + weapon_damage + injector_bonus
                
                # ERROR 404 mode: 5x damage bonus
                if self.error404_mode:
                    total_damage *= 5.0

                enemy.take_damage(total_damage)
                self.add_chat_message(f"Arrow hit {enemy_name}! (-{int(total_damage)} HP)", color.yellow)

                # Apply weapon debuffs from special metals
                poison_dmg = self.equipped_weapon.get('poison_damage', 0)
                slow_pct = self.equipped_weapon.get('slow_percent', 0)
                weaken_pct = self.equipped_weapon.get('weaken_percent', 0)
                curse_pct = self.equipped_weapon.get('curse_percent', 0)
                fear_active = self.equipped_weapon.get('fear_active', False)
                
                if fear_active and enemy.health > 0:
                    # Fear debuff: 2x damage taken + DOT for 5 seconds
                    if hasattr(enemy, 'fear_multiplier'):
                        enemy.fear_multiplier = 2.0
                        enemy.fear_duration = 5.0
                        enemy.fear_dot = 5  # 5 damage per second
                    self.add_chat_message(f"{enemy_name} is FEARED!", color.violet)
                
                if poison_dmg or slow_pct or weaken_pct or curse_pct:
                    if enemy.health > 0:  # Only apply if enemy still alive
                        enemy.apply_debuffs(poison=poison_dmg, slow=slow_pct, weaken=weaken_pct, curse=curse_pct, duration=5)
                        debuff_msg = []
                        if poison_dmg: debuff_msg.append("Poisoned")
                        if slow_pct: debuff_msg.append("Slowed")
                        if weaken_pct: debuff_msg.append("Weakened")
                        if curse_pct: debuff_msg.append("Cursed")
                        self.add_chat_message(f"{enemy_name} {', '.join(debuff_msg)}!", color.magenta)

                if enemy.health <= 0:
                    # Check for Sonic Bow XP multiplier
                    xp_to_award = enemy_xp
                    if self.equipped_weapon and self.equipped_weapon.get('xp_multiplier'):
                        xp_mult = self.equipped_weapon.get('xp_multiplier', 1.0)
                        xp_to_award = int(enemy_xp * xp_mult)
                    
                    self.character.gain_experience(xp_to_award)
                    self.drop_enemy_loot(enemy_name, enemy_pos)
                    if enemy in self.enemies:
                        self.enemies.remove(enemy)
                    self.add_chat_message(f"{enemy_name} defeated! +{xp_to_award} XP", color.yellow)
                return True

        self.add_chat_message("Arrow missed!", color.gray)
        return False

    def use_healing_staff(self):
        """Use healing staff to heal self."""
        if not self.equipped_weapon or self.equipped_weapon.get('weapon_type') != 'healing_staff':
            return False

        heal_power = self.equipped_weapon.get('heal_power', 15)
        mana_cost = 10

        if self.character.use_mana(mana_cost):
            self.character.heal(heal_power)
            self.swing_weapon()
            self.add_chat_message(f"Healed for {heal_power} HP! (-{mana_cost} MP)", color.lime)
            return True
        else:
            self.add_chat_message("Not enough mana to heal!", color.red)
            return False

    def shoot_staff_projectile(self):
        """Fire a piercing projectile from the staff."""
        if not self.equipped_weapon or self.equipped_weapon.get('weapon_type') != 'staff':
            return False

        if self.attack_cooldown > 0:
            return False

        mana_cost = 5
        if not self.character.use_mana(mana_cost):
            self.add_chat_message("Not enough mana!", color.red)
            return False

        # Apply attack speed from Chrono Shard
        attack_speed_mult = self.equipped_weapon.get('attack_speed_mult', 1.0)
        if self.dream_mode:
            attack_speed_mult *= 2.0  # Dream mode 2x attack speed
        if self.error404_mode:
            attack_speed_mult *= 3.0  # ERROR 404 mode 3x attack speed
        self.attack_cooldown = 0.6 / attack_speed_mult
        self.swing_weapon()

        # Get staff properties
        base_damage = self.character.get_attack_power()
        weapon_damage = self.equipped_weapon.get('damage', 0)
        
        # Add Injector Soul bonus (+6 damage per soul)
        injector_bonus = self.equipped_weapon.get('injector_soul_bonus', 0)
        
        total_damage = base_damage + weapon_damage + injector_bonus
        
        # ERROR 404 mode: 5x damage bonus
        if self.error404_mode:
            total_damage *= 5.0
        
        pierce = self.equipped_weapon.get('pierce', 3)
        debuff_type = self.equipped_weapon.get('debuff', None)
        debuff_value = self.equipped_weapon.get('debuff_value', 0)
        staff_color = self.equipped_weapon.get('color', color.magenta)

        # Fire projectile in player's facing direction
        direction = self.player.forward
        spawn_pos = self.player.position + Vec3(0, 1.5, 0) + direction * 1.5

        proj = PlayerProjectile(
            position=spawn_pos,
            direction=direction,
            damage=total_damage,
            projectile_color=staff_color,
            pierce=pierce,
            debuff_type=debuff_type,
            debuff_value=debuff_value,
            game_ref=self
        )

        self.add_chat_message(f"Staff bolt fired! (Pierce: {pierce})", staff_color)
        return True

    def shoot_terror_bullets(self):
        """Shoot terror bullets in ERROR 404 mode - fires multiple projectiles."""
        if not self.error404_mode:
            return
        
        import random
        import math
        
        # Fire 5 terror bullets in a spread pattern
        for i in range(5):
            # Calculate spread angle
            angle_offset = (i - 2) * 15  # -30, -15, 0, 15, 30 degrees
            
            # Get player's forward direction and rotate it
            player_rotation = self.player.rotation_y
            bullet_angle = player_rotation + angle_offset
            
            # Calculate direction vector
            rad = math.radians(bullet_angle)
            direction = Vec3(math.sin(rad), 0, math.cos(rad))
            
            # Spawn position in front of player
            spawn_pos = self.player.position + Vec3(0, 1.5, 0) + direction * 2
            
            # Random damage for each bullet (50-150)
            bullet_damage = random.randint(50, 150)
            
            # Create terror bullet
            proj = PlayerProjectile(
                position=spawn_pos,
                direction=direction,
                damage=bullet_damage,
                projectile_color=color.rgb(255, 0, 255),  # Pink terror bullets
                pierce=2,  # Pierce through 2 enemies
                debuff_type=None,
                debuff_value=0,
                game_ref=self
            )
        
        self.add_chat_message("TERROR BULLETS RELEASED!", color.rgb(255, 0, 255))

    def get_total_defense(self):
        """Calculate total defense from equipped armor."""
        total = 0
        for slot, armor in self.equipped_armor.items():
            if armor:
                total += armor.get('defense', 0)
        return total

    def drop_enemy_loot(self, enemy_name, enemy_position):
        """Drop loot when enemy is defeated."""
        import random
        
        if enemy_name not in ENEMY_LOOT_TABLES:
            return
        
        loot_data = ENEMY_LOOT_TABLES[enemy_name]
        drop_chance = loot_data['drop_chance']
        
        # Dream mode gets better drop rates and multiple drops
        drop_multiplier = 3 if self.dream_mode else 1
        if self.dream_mode:
            drop_chance = min(1.0, drop_chance * 1.5)
        
        # Drop multiple items in dream mode
        for _ in range(drop_multiplier):
            # Roll for drop
            if random.random() <= drop_chance:
                # Dream mode has exclusive rare drops
                if self.dream_mode and random.random() < 0.15:  # 15% chance for exclusive
                    dream_exclusives = ['Void Crystal', 'Shadow Essence', 'Nightmare Fragment']
                    dropped_item_name = random.choice(dream_exclusives)
                else:
                    # Pick random item from drop table
                    possible_items = loot_data['items']
                    dropped_item_name = random.choice(possible_items)
                
                # Create the item
                dropped_item = Item.create(dropped_item_name)
                if dropped_item:
                    # Find empty inventory slot
                    added = False
                    for i in range(len(self.inventory)):
                        if self.inventory[i] is None:
                            self.inventory[i] = dropped_item
                            added = True
                            break
                    
                    if added:
                        rarity = dropped_item.get('rarity', 'common')
                        rarity_col = Item.RARITY_COLORS.get(rarity, color.white)
                        if drop_multiplier > 1:
                            self.add_chat_message(f"Dropped: {dropped_item_name}! (Dream Mode 3x)", rarity_col)
                        else:
                            self.add_chat_message(f"Dropped: {dropped_item_name}!", rarity_col)
                        self.update_hotbar_display()
                    else:
                        break  # Stop if inventory full

    def spawn_chests(self):
        """Spawn loot chests around the world."""
        chest_locations = [
            # Village area - common chests
            ((20, 0.4, 20), 'common'),
            ((-20, 0.4, 20), 'common'),
            # Near enemy camps - better chests
            ((55, 0.4, 55), 'uncommon'),  # Wolf den
            ((-55, 0.4, -55), 'uncommon'),  # Slime swamp
            ((-55, 0.4, 55), 'uncommon'),  # Goblin camp
            ((55, 0.4, -55), 'uncommon'),  # Skeleton ruins
            # Deep wilderness - rare chests
            ((100, 0.4, 100), 'rare'),
            ((-100, 0.4, -100), 'rare'),
            ((100, 0.4, -100), 'rare'),
            ((-100, 0.4, 100), 'rare'),
            # Near landmarks - legendary chests
            ((245, 0.4, 245), 'legendary'),  # Near tower
            ((-245, 0.4, -245), 'legendary'),  # Near dark tower
        ]

        for pos, chest_type in chest_locations:
            chest = Chest(pos, chest_type)
            self.chests.append(chest)
            self.world_entities.append(chest)

    def interact_with_chest(self):
        """Try to open a nearby chest."""
        if not self.player:
            return False

        for chest in self.chests:
            if chest.opened:
                continue
            if distance(self.player, chest) < 3:
                loot = chest.open_chest()
                if loot:
                    # Add gold
                    self.character.gold += loot['gold']
                    self.add_chat_message(f"+{loot['gold']} Gold!", color.gold)

                    # Add items to inventory
                    items_added = 0
                    for item in loot['items']:
                        # Find empty slot
                        for i in range(len(self.inventory)):
                            if self.inventory[i] is None:
                                self.inventory[i] = item
                                rarity_color = Item.RARITY_COLORS.get(item.get('rarity', 'common'), color.white)
                                self.add_chat_message(f"Found: {item['name']}", rarity_color)
                                items_added += 1
                                break

                    if items_added < len(loot['items']):
                        self.add_chat_message("Inventory full! Some items lost.", color.red)

                    return True
        return False

    def create_village(self):
        """Create the village with walls and NPCs."""
        wall_height = 5
        wall_thickness = 2
        village_size = 30

        # Village walls
        wall_color = color.brown
        walls = [
            # North wall
            ((village_size * 2 + wall_thickness, wall_height, wall_thickness), (0, wall_height/2, village_size)),
            # South wall left
            ((village_size - 5, wall_height, wall_thickness), (-village_size/2 - 2.5, wall_height/2, -village_size)),
            # South wall right
            ((village_size - 5, wall_height, wall_thickness), (village_size/2 + 2.5, wall_height/2, -village_size)),
            # East wall
            ((wall_thickness, wall_height, village_size * 2), (village_size, wall_height/2, 0)),
            # West wall
            ((wall_thickness, wall_height, village_size * 2), (-village_size, wall_height/2, 0)),
        ]

        for scale, pos in walls:
            wall_color_final = color.black if self.dream_mode else wall_color
            wall = Entity(
                model='cube',
                scale=scale,
                position=pos,
                texture='white_cube',
                color=wall_color_final,
                collider='box',
                unlit=self.dream_mode
            )
            self.world_entities.append(wall)

        # Houses
        houses = [
            ((6, 4, 6), (15, 2, 15), color.brown),  # Elder's
            ((5, 3.5, 5), (-15, 1.75, 10), color.olive),  # Merchant's
            ((5, 3, 5), (10, 1.5, -15), color.orange),  # Pet Trainer's
            ((7, 4, 5), (-10, 2, -12), color.dark_gray),  # Blacksmith
        ]

        for scale, pos, col in houses:
            house_color = color.black if self.dream_mode else col
            # Dream mode: damaged, tilted buildings
            if self.dream_mode:
                import random
                tilt = (random.uniform(-8, 8), random.uniform(-15, 15), random.uniform(-8, 8))
                lower_amount = random.uniform(0, 0.5)
                house = Entity(
                    model='cube',
                    texture='white_cube',
                    scale=scale,
                    position=(pos[0], pos[1] - lower_amount, pos[2]),
                    color=house_color,
                    collider='box',
                    rotation=tilt,
                    unlit=self.dream_mode
                )
            else:
                house = Entity(
                    model='cube',
                    texture='white_cube',
                    scale=scale,
                    position=pos,
                    color=house_color,
                    collider='box',
                    unlit=self.dream_mode
                )
            self.world_entities.append(house)
            # Flat roof
            roof_color = color.rgb(80, 0, 0) if self.dream_mode else color.red
            if self.dream_mode:
                import random
                roof_tilt = (random.uniform(-10, 10), random.uniform(-20, 20), random.uniform(-10, 10))
                roof = Entity(
                    model='cube',
                    texture='white_cube',
                    scale=(scale[0] + 1, 0.5, scale[2] + 1),
                    position=(pos[0], pos[1] + scale[1]/2 + 0.25, pos[2]),
                    color=roof_color,
                    rotation=roof_tilt,
                    unlit=self.dream_mode
                )
            else:
                roof = Entity(
                    model='cube',
                    texture='white_cube',
                    scale=(scale[0] + 1, 0.5, scale[2] + 1),
                    position=(pos[0], pos[1] + scale[1]/2 + 0.25, pos[2]),
                    color=roof_color,
                    unlit=self.dream_mode
                )
            self.world_entities.append(roof)

        # Well
        well = Entity(
            model='cube',
            texture='white_cube',
            scale=(3, 1, 3),
            position=(0, 0.5, 5),
            color=color.gray,
            collider='box'
        )
        self.world_entities.append(well)

        # Create NPCs
        self.create_npcs()

        # Pet Book pedestal
        self.pet_book_pedestal = Entity(
            model='cube',
            texture='white_cube',
            scale=(1.5, 1, 1.5),
            position=(0, 0.5, -5),
            color=color.brown,
            collider='box'
        )
        self.world_entities.append(self.pet_book_pedestal)

        # The book itself
        self.pet_book = Entity(
            model='cube',
            texture='white_cube',
            scale=(1, 0.2, 0.8),
            position=(0, 1.1, -5),
            color=color.magenta,
            collider='box'
        )
        self.world_entities.append(self.pet_book)

        Text(
            text='Pet Book',
            parent=self.pet_book,
            y=1,
            scale=15,
            billboard=True,
            origin=(0, 0),
            color=color.magenta
        )
        Text(
            text='[Attack to Select]',
            parent=self.pet_book,
            y=0.6,
            scale=10,
            billboard=True,
            origin=(0, 0),
            color=color.white
        )

        # Smelting Station (Furnace) near blacksmith
        self.smelting_station = Entity(
            model='cube',
            texture='white_cube',
            scale=(2, 1.5, 2),
            position=(-14, 0.75, -10),
            color=color.red,
            collider='box'
        )
        self.world_entities.append(self.smelting_station)

        # Furnace top (orange glow)
        furnace_top = Entity(
            model='cube',
            texture='white_cube',
            scale=(1.6, 0.3, 1.6),
            position=(-14, 1.6, -10),
            color=color.orange
        )
        self.world_entities.append(furnace_top)

        Text(
            text='Smelting Furnace',
            parent=self.smelting_station,
            y=1.5,
            scale=12,
            billboard=True,
            origin=(0, 0),
            color=color.orange
        )
        Text(
            text='[E] Smelt',
            parent=self.smelting_station,
            y=1.1,
            scale=8,
            billboard=True,
            origin=(0, 0),
            color=color.white
        )

        # Crafting Station near blacksmith
        self.crafting_station = Entity(
            model='cube',
            texture='white_cube',
            scale=(2, 1, 2),
            position=(-6, 0.5, -14),
            color=color.brown,
            collider='box'
        )
        self.world_entities.append(self.crafting_station)

        # Anvil-like top
        anvil_top = Entity(
            model='cube',
            texture='white_cube',
            scale=(2.5, 0.3, 1.5),
            position=(-6, 1.1, -14),
            color=color.dark_gray
        )
        self.world_entities.append(anvil_top)

        Text(
            text='Crafting Anvil',
            parent=self.crafting_station,
            y=1.5,
            scale=12,
            billboard=True,
            origin=(0, 0),
            color=color.cyan
        )
        Text(
            text='[E] Craft',
            parent=self.crafting_station,
            y=1.1,
            scale=8,
            billboard=True,
            origin=(0, 0),
            color=color.white
        )

    def create_npcs(self):
        """Create all village NPCs."""
        npcs = [
            ('Village Elder', (5, 0.9, 5), color.olive, color.yellow),
            ('Merchant', (-12, 0.9, 8), color.azure, color.orange),
            ('Pet Trainer', (8, 0.9, -12), color.lime, color.lime),
            ('Blacksmith', (-8, 1, -10), color.brown, color.red),
            ('Guard', (0, 1, -28), color.blue, color.azure),
        ]

        for name, pos, col, name_col in npcs:
            npc = Entity(
                model='cube',
                texture='white_cube',
                scale=(0.8, 1.8, 0.8),
                position=pos,
                color=col,
                collider='box'
            )
            setattr(self, name.lower().replace(' ', '_'), npc)
            self.world_entities.append(npc)

            Text(
                text=name,
                parent=npc,
                y=1.3,
                scale=10,
                billboard=True,
                origin=(0, 0),
                color=name_col
            )
            Text(
                text='[E] Talk',
                parent=npc,
                y=1.0,
                scale=8,
                billboard=True,
                origin=(0, 0),
                color=color.white
            )

    def create_glitched_transition_room(self):
        """Create the glitched transition room for ERROR 404 mode entry."""
        import random
        
        # Glitched room at spawn position
        room_center = Vec3(1000, 0, 1000)
        
        # Black floor with pink glitches
        floor = Entity(
            model='cube',
            scale=(30, 0.5, 30),
            position=(room_center.x, 0, room_center.z),
            texture='white_cube',
            color=color.black,
            collider='box',
            unlit=True
        )
        self.world_entities.append(floor)
        
        # Pink glitch patches on floor
        for i in range(15):
            patch = Entity(
                model='cube',
                scale=(random.uniform(2, 5), 0.1, random.uniform(2, 5)),
                position=(room_center.x + random.uniform(-12, 12), 0.3, room_center.z + random.uniform(-12, 12)),
                texture='white_cube',
                color=color.rgb(255, 0, 255),
                alpha=0.7,
                unlit=True
            )
            self.world_entities.append(patch)
        
        # Glitched walls - pink and black alternating
        wall_height = 8
        walls = [
            # North wall
            ((30, wall_height, 1), (room_center.x, wall_height/2, room_center.z + 15)),
            # South wall
            ((30, wall_height, 1), (room_center.x, wall_height/2, room_center.z - 15)),
            # East wall
            ((1, wall_height, 30), (room_center.x + 15, wall_height/2, room_center.z)),
            # West wall
            ((1, wall_height, 30), (room_center.x - 15, wall_height/2, room_center.z)),
        ]
        
        for i, (scale, pos) in enumerate(walls):
            wall_color = color.rgb(255, 0, 255) if i % 2 == 0 else color.black
            wall = Entity(
                model='cube',
                scale=scale,
                position=pos,
                texture='white_cube',
                color=wall_color,
                rotation=(random.uniform(-5, 5), random.uniform(-5, 5), random.uniform(-5, 5)),
                collider='box',
                unlit=True
            )
            self.world_entities.append(wall)
        
        # Glitched ceiling - solid black to block sky
        ceiling = Entity(
            model='cube',
            scale=(30, 1, 30),
            position=(room_center.x, wall_height, room_center.z),
            texture='white_cube',
            color=color.black,
            collider='box',
            unlit=True
        )
        self.world_entities.append(ceiling)
        
        # White portal in center - leads to Error Village
        self.error404_glitched_room_portal = Entity(
            model='sphere',
            texture='white_cube',
            color=color.white,
            scale=(2, 3, 2),
            position=(room_center.x, 2, room_center.z - 5),
            collider='box'
        )
        self.world_entities.append(self.error404_glitched_room_portal)
        
        # Portal glow
        portal_glow = Entity(
            parent=self.error404_glitched_room_portal,
            model='sphere',
            color=color.rgb(200, 200, 255),
            scale=1.4,
            alpha=0.5
        )
        self.world_entities.append(portal_glow)
        
        # Add floating text above portal
        Text(
            text='ERROR 404: REALITY NOT FOUND',
            parent=self.error404_glitched_room_portal,
            y=2.5,
            scale=15,
            billboard=True,
            origin=(0, 0),
            color=color.red
        )
        Text(
            text='[E] Enter Portal',
            parent=self.error404_glitched_room_portal,
            y=2,
            scale=10,
            billboard=True,
            origin=(0, 0),
            color=color.white
        )
        
        # Glitched floating cubes around the room
        for i in range(20):
            glitch_cube = Entity(
                model='cube',
                scale=(random.uniform(0.5, 2), random.uniform(0.5, 2), random.uniform(0.5, 2)),
                position=(room_center.x + random.uniform(-12, 12), random.uniform(1, 6), room_center.z + random.uniform(-12, 12)),
                texture='white_cube',
                color=color.rgb(255, 0, 255) if i % 2 == 0 else color.black,
                rotation=(random.uniform(0, 360), random.uniform(0, 360), random.uniform(0, 360)),
                alpha=0.6,
                unlit=True
            )
            self.world_entities.append(glitch_cube)
        
        # Spawn glitched enemies in the room
        enemy_positions = [
            (room_center.x + 10, 1, room_center.z + 8),
            (room_center.x - 10, 1, room_center.z + 8),
            (room_center.x + 8, 1, room_center.z - 10),
            (room_center.x - 8, 1, room_center.z - 10),
        ]
        
        for i, pos in enumerate(enemy_positions):
            enemy_color = color.rgb(255, 0, 255) if i % 2 == 0 else color.black
            glitch_enemy = BossEnemy(
                "GLITCH ERROR",
                pos,
                2000,
                enemy_color,
                xp_value=1000
            )
            glitch_enemy.target = self.player
            glitch_enemy.can_magic = True
            self.enemies.append(glitch_enemy)

    def create_error_village(self):
        """Create the ERROR 404 World - pink/black biomes with no central village."""
        import random
        
        # ERROR 404 safe spawn area at -500, 500 with escape portal
        spawn_pos = Vec3(-500, 0, 500)
        
        # Small spawn platform - pink/black checkerboard
        for x in range(-2, 3):
            for z in range(-2, 3):
                floor_color = color.rgb(255, 0, 255) if (x + z) % 2 == 0 else color.black
                floor_tile = Entity(
                    model='cube',
                    scale=(8, 0.2, 8),
                    position=(spawn_pos.x + x * 8, 0.1, spawn_pos.z + z * 8),
                    texture='white_cube',
                    color=floor_color,
                    unlit=True
                )
                self.world_entities.append(floor_tile)
        
        # White escape portal
        portal_pos = Vec3(spawn_pos.x, 2, spawn_pos.z)
        self.error404_portal = Entity(
            model='sphere',
            texture='white_cube',
            color=color.white,
            scale=(2, 3, 2),
            position=portal_pos,
            collider='box'
        )
        self.world_entities.append(self.error404_portal)
        
        # Portal glow
        portal_glow = Entity(
            parent=self.error404_portal,
            model='sphere',
            color=color.rgb(200, 200, 255),
            scale=1.3,
            alpha=0.4
        )
        self.world_entities.append(portal_glow)
        
        # Floating text
        Text(
            text='ESCAPE PORTAL',
            parent=self.error404_portal,
            y=2.5,
            scale=15,
            billboard=True,
            origin=(0, 0),
            color=color.white
        )
        
        # Turrets guarding the portal
        turret_positions = [
            (spawn_pos.x + 15, 0.75, spawn_pos.z + 15),
            (spawn_pos.x - 15, 0.75, spawn_pos.z + 15),
            (spawn_pos.x + 15, 0.75, spawn_pos.z - 15),
            (spawn_pos.x - 15, 0.75, spawn_pos.z - 15),
        ]
        
        for turret_pos in turret_positions:
            turret = BossEnemy("ERROR TURRET", turret_pos, 1000, color.rgb(255, 0, 255), xp_value=500)
            turret.target = self.player
            turret.can_magic = True
            turret.speed = 0  # Stationary turrets
            self.enemies.append(turret)
            self.error404_turrets.append(turret)

    def create_wilderness(self):
        """Create wilderness areas outside the village."""
        import random
        
        # ========== ERROR 404 MODE: Pink/Black biome world ==========
        if self.error404_mode:
            # ===== BIOME 1: GLITCH FOREST (North, 100-400) =====
            for i in range(80):
                x = random.uniform(-350, 350)
                z = random.uniform(100, 400)
                
                # Alternating pink/black twisted trees
                tree_color = color.rgb(255, 0, 255) if i % 2 == 0 else color.black
                glitch_tilt = (random.uniform(-40, 40), random.uniform(0, 360), random.uniform(-40, 40))
                trunk = Entity(
                    model='cube', texture='white_cube',
                    scale=(1.2, random.uniform(4, 8), 1.2),
                    position=(x, 3, z),
                    color=tree_color,
                    collider='box',
                    rotation=glitch_tilt,
                    unlit=True
                )
                self.world_entities.append(trunk)
                
                # Glitched foliage cubes
                foliage_color = color.black if tree_color == color.rgb(255, 0, 255) else color.rgb(255, 0, 255)
                for j in range(3):
                    foliage = Entity(
                        model='cube', texture='white_cube',
                        scale=(random.uniform(2, 3), random.uniform(1, 2), random.uniform(2, 3)),
                        position=(x + random.uniform(-1, 1), 6 + j * 1.5, z + random.uniform(-1, 1)),
                        color=foliage_color,
                        rotation=(random.uniform(0, 360), random.uniform(0, 360), random.uniform(0, 360)),
                        unlit=True
                    )
                    self.world_entities.append(foliage)
            
            # ===== BIOME 2: VOID CRYSTALS (South, -400 to -100) =====
            for i in range(60):
                x = random.uniform(-350, 350)
                z = random.uniform(-400, -100)
                
                # Tall crystal spires
                crystal_color = color.rgb(255, 0, 255) if i % 3 != 0 else color.black
                crystal = Entity(
                    model='cube', texture='white_cube',
                    scale=(random.uniform(2, 4), random.uniform(10, 20), random.uniform(2, 4)),
                    position=(x, random.uniform(8, 12), z),
                    color=crystal_color,
                    collider='box',
                    rotation=(random.uniform(-15, 15), random.uniform(0, 360), random.uniform(-15, 15)),
                    unlit=True
                )
                self.world_entities.append(crystal)
            
            # ===== BIOME 3: CORRUPTED RUINS (East, 100-400) =====
            for i in range(30):
                x = random.uniform(100, 400)
                z = random.uniform(-350, 350)
                
                # Broken structures
                ruin_color = color.black if i % 2 == 0 else color.rgb(255, 0, 255)
                ruin = Entity(
                    model='cube', texture='white_cube',
                    scale=(random.uniform(6, 12), random.uniform(8, 18), random.uniform(6, 12)),
                    position=(x, random.uniform(4, 9), z),
                    color=ruin_color,
                    collider='box',
                    rotation=(random.uniform(-30, 30), random.uniform(0, 360), random.uniform(-30, 30)),
                    unlit=True
                )
                self.world_entities.append(ruin)
            
            # ===== BIOME 4: STATIC DESERT (West, -400 to -100) =====
            for i in range(40):
                x = random.uniform(-400, -100)
                z = random.uniform(-350, 350)
                
                # Low flat glitch blocks
                block_color = color.rgb(255, 0, 255) if i % 2 == 0 else color.black
                block = Entity(
                    model='cube', texture='white_cube',
                    scale=(random.uniform(8, 15), random.uniform(0.5, 2), random.uniform(8, 15)),
                    position=(x, 0.5, z),
                    color=block_color,
                    unlit=True
                )
                self.world_entities.append(block)
            
            # ===== CENTRAL AREA: GLITCHED PILLARS (center) =====
            for i in range(25):
                x = random.uniform(-100, 100)
                z = random.uniform(-100, 100)
                if abs(x) < 30 and abs(z) < 30:
                    continue
                
                # Tall floating pillars
                pillar_color = color.black if i % 2 == 0 else color.rgb(255, 0, 255)
                pillar = Entity(
                    model='cube', texture='white_cube',
                    scale=(random.uniform(3, 6), random.uniform(15, 30), random.uniform(3, 6)),
                    position=(x, random.uniform(10, 18), z),
                    color=pillar_color,
                    collider='box',
                    rotation=(random.uniform(-10, 10), 0, random.uniform(-10, 10)),
                    unlit=True
                )
                self.world_entities.append(pillar)
            
            # ===== ERROR ground - full pink/black checkerboard =====
            for x in range(-60, 61, 10):
                for z in range(-60, 61, 10):
                    ground_color = color.rgb(255, 0, 255) if (x + z) % 20 == 0 else color.black
                    ground = Entity(
                        model='cube', texture='white_cube',
                        scale=(10, 0.1, 10),
                        position=(x, 0.05, z),
                        color=ground_color,
                        unlit=True
                    )
                    self.world_entities.append(ground)
            
            # ===== Floating ERROR debris everywhere =====
            for i in range(100):
                x = random.uniform(-450, 450)
                z = random.uniform(-450, 450)
                debris_color = color.rgb(255, 0, 255) if i % 2 == 0 else color.black
                debris = Entity(
                    model='cube', texture='white_cube',
                    scale=(random.uniform(1, 3), random.uniform(1, 3), random.uniform(1, 3)),
                    position=(x, random.uniform(2, 10), z),
                    color=debris_color,
                    rotation=(random.uniform(0, 360), random.uniform(0, 360), random.uniform(0, 360)),
                    alpha=0.8,
                    unlit=True
                )
                self.world_entities.append(debris)
            
            return  # Skip normal wilderness
        
        # Trees
        for i in range(150):
            x = random.uniform(-450, 450)
            z = random.uniform(-450, 450)
            if abs(x) < 40 and abs(z) < 40:
                continue

            trunk_color = color.rgb(40, 20, 10) if self.dream_mode else color.brown
            if self.dream_mode:
                # Broken, tilted trees
                trunk_tilt = (random.uniform(-15, 15), random.uniform(0, 360), random.uniform(-15, 15))
                trunk_height = random.uniform(2, 3.5)  # Shorter, broken
                trunk = Entity(
                    model='cube',
                    texture='white_cube',
                    scale=(0.8, trunk_height, 0.8),
                    position=(x, trunk_height/2, z),
                    color=trunk_color,
                    collider='box',
                    rotation=trunk_tilt,
                    unlit=self.dream_mode
                )
            else:
                trunk = Entity(
                    model='cube',
                    texture='white_cube',
                    scale=(0.8, 4, 0.8),
                    position=(x, 2, z),
                    color=trunk_color,
                    collider='box',
                    unlit=self.dream_mode
                )
            self.world_entities.append(trunk)

            # Sparse, dead foliage in dream mode
            foliage_count = 1 if self.dream_mode else 3
            for j in range(foliage_count):
                foliage_color = color.rgb(0, 50, 0) if self.dream_mode else color.green
                if self.dream_mode:
                    foliage = Entity(
                        model='cube',
                        texture='white_cube',
                        scale=(1.5, 0.8, 1.5),  # Smaller, dead
                        position=(x, trunk_height + 0.5, z),
                        color=foliage_color,
                        rotation=(random.uniform(-20, 20), random.uniform(0, 360), random.uniform(-20, 20)),
                        unlit=self.dream_mode
                    )
                else:
                    foliage = Entity(
                        model='cube',
                        texture='white_cube',
                        scale=(2.5 - j * 0.5, 1.5, 2.5 - j * 0.5),
                        position=(x, 5 + j * 1.2, z),
                        color=foliage_color,
                        unlit=self.dream_mode
                    )
                self.world_entities.append(foliage)

        # Rocks
        for i in range(80):
            x = random.uniform(-450, 450)
            z = random.uniform(-450, 450)
            if abs(x) < 40 and abs(z) < 40:
                continue
            rock = Entity(
                model='cube',
                texture='white_cube',
                scale=(random.uniform(0.8, 2), random.uniform(0.5, 1.5), random.uniform(0.8, 2)),
                position=(x, 0.4, z),
                color=color.gray,
                collider='box',
                rotation=(random.uniform(-10, 10), random.uniform(0, 360), random.uniform(-10, 10))
            )
            self.world_entities.append(rock)

        # Distant landmarks
        landmarks = [
            ((8, 25, 8), (250, 12.5, 250), color.dark_gray),  # Tower
            ((20, 10, 20), (-250, 5, 250), color.brown),  # Ruins
            ((25, 4, 25), (250, 2, -250), color.olive),  # Swamp mound
            ((12, 15, 12), (-250, 7.5, -250), color.smoke),  # Dark tower
        ]

        for scale, pos, col in landmarks:
            landmark = Entity(
                model='cube',
                texture='white_cube',
                scale=scale,
                position=pos,
                color=col,
                collider='box'
            )
            self.world_entities.append(landmark)

        # Create expanded biome zones
        self.create_biome_zones()

        # Create mining ore rocks
        self.create_mining_rocks()

    def create_biome_zones(self):
        """Create distinct biome zones in the expanded world."""
        # ============ FROZEN TUNDRA (North - positive Z, 100-400) ============
        # In Dream Mode: VOLCANIC INFERNO
        for i in range(40):
            x = random.uniform(-300, 300)
            z = random.uniform(100, 400)
            if self.dream_mode:
                # Volcanic dead trees on fire
                trunk = Entity(
                    model='cube', texture='white_cube',
                    scale=(0.7, 2, 0.7), position=(x, 1, z),
                    color=color.rgb(30, 10, 0), collider='box', unlit=True
                )
                self.world_entities.append(trunk)
                # Fire/lava foliage
                foliage = Entity(
                    model='cube', texture='white_cube',
                    scale=(1.5, 1, 1.5), position=(x, 2.5, z),
                    color=color.rgb(200, 50, 0), unlit=True
                )
                self.world_entities.append(foliage)
            else:
                # Snowy trees (white/light blue)
                trunk = Entity(
                    model='cube', texture='white_cube',
                    scale=(0.7, 3, 0.7), position=(x, 1.5, z),
                    color=color.brown, collider='box'
                )
                self.world_entities.append(trunk)
                # Snow-covered foliage
                for j in range(2):
                    foliage = Entity(
                        model='cube', texture='white_cube',
                        scale=(2 - j * 0.4, 1.2, 2 - j * 0.4),
                        position=(x, 4 + j * 1, z),
                        color=color.white
                    )
                    self.world_entities.append(foliage)

        # Ice formations / Lava pools in Dream Mode
        for i in range(25):
            x = random.uniform(-300, 300)
            z = random.uniform(100, 400)
            if self.dream_mode:
                lava = Entity(
                    model='cube', texture='white_cube',
                    scale=(random.uniform(2, 4), 0.3, random.uniform(2, 4)),
                    position=(x, 0.15, z),
                    color=color.rgb(255, 100, 0),
                    unlit=True
                )
                self.world_entities.append(lava)
            else:
                ice = Entity(
                    model='cube', texture='white_cube',
                    scale=(random.uniform(1, 3), random.uniform(2, 6), random.uniform(1, 3)),
                    position=(x, 2, z),
                    color=color.cyan,
                    collider='box'
                )
                self.world_entities.append(ice)

        # Frozen lake / Lava lake in Dream Mode
        if self.dream_mode:
            lava_lake = Entity(
                model='cube', texture='white_cube',
                scale=(60, 0.2, 60), position=(0, 0.1, 250),
                color=color.rgb(255, 80, 0), unlit=True
            )
            self.world_entities.append(lava_lake)
        else:
            frozen_lake = Entity(
                model='cube', texture='white_cube',
                scale=(60, 0.2, 60), position=(0, 0.1, 250),
                color=color.azure
            )
            self.world_entities.append(frozen_lake)

        # Ice Castle / Volcanic fortress in Dream Mode
        if self.dream_mode:
            fortress = Entity(
                model='cube', texture='white_cube',
                scale=(30, 40, 30), position=(0, 20, 350),
                color=color.rgb(50, 10, 0), collider='box', unlit=True
            )
            self.world_entities.append(fortress)
            for tx in [-12, 12]:
                tower = Entity(
                    model='cube', texture='white_cube',
                    scale=(8, 50, 8), position=(tx, 25, 350),
                    color=color.rgb(100, 20, 0), unlit=True
                )
                self.world_entities.append(tower)
        else:
            ice_castle = Entity(
                model='cube', texture='white_cube',
                scale=(30, 40, 30), position=(0, 20, 350),
                color=color.white, collider='box'
            )
            self.world_entities.append(ice_castle)
            for tx in [-12, 12]:
                tower = Entity(
                    model='cube', texture='white_cube',
                    scale=(8, 50, 8), position=(tx, 25, 350),
                    color=color.azure
                )
                self.world_entities.append(tower)

        # ============ DESERT WASTELAND (East - positive X, 100-400) ============
        # Sand dunes
        for i in range(30):
            x = random.uniform(100, 400)
            z = random.uniform(-200, 200)
            dune = Entity(
                model='cube', texture='white_cube',
                scale=(random.uniform(10, 25), random.uniform(2, 6), random.uniform(10, 25)),
                position=(x, 2, z),
                color=color.yellow,
                rotation=(random.uniform(-5, 5), random.uniform(0, 360), random.uniform(-5, 5))
            )
            self.world_entities.append(dune)

        # Cacti
        for i in range(40):
            x = random.uniform(100, 400)
            z = random.uniform(-200, 200)
            cactus = Entity(
                model='cube', texture='white_cube',
                scale=(0.5, random.uniform(2, 5), 0.5),
                position=(x, 2, z),
                color=color.green, collider='box'
            )
            self.world_entities.append(cactus)
            # Arms
            if random.random() > 0.5:
                arm = Entity(
                    model='cube', texture='white_cube',
                    scale=(1.5, 0.4, 0.4), position=(x + 0.8, 3, z),
                    color=color.green
                )
                self.world_entities.append(arm)

        # Pyramid (landmark)
        pyramid_base = Entity(
            model='cube', texture='white_cube',
            scale=(50, 35, 50), position=(300, 17.5, 0),
            color=color.gold, collider='box'
        )
        self.world_entities.append(pyramid_base)

        # Oasis
        oasis_water = Entity(
            model='cube', texture='white_cube',
            scale=(20, 0.3, 20), position=(200, 0.15, 50),
            color=color.blue
        )
        self.world_entities.append(oasis_water)
        for i in range(6):
            palm = Entity(
                model='cube', texture='white_cube',
                scale=(0.6, 5, 0.6), position=(200 + random.uniform(-8, 8), 2.5, 50 + random.uniform(-8, 8)),
                color=color.brown, collider='box'
            )
            self.world_entities.append(palm)
            palm_top = Entity(
                model='cube', texture='white_cube',
                scale=(3, 1, 3), position=(palm.x, 5.5, palm.z),
                color=color.lime
            )
            self.world_entities.append(palm_top)

        # ============ DARK SWAMP (South - negative Z, -100 to -400) ============
        # Murky water pools
        for i in range(15):
            x = random.uniform(-200, 200)
            z = random.uniform(-400, -100)
            pool = Entity(
                model='cube', texture='white_cube',
                scale=(random.uniform(8, 20), 0.2, random.uniform(8, 20)),
                position=(x, 0.1, z),
                color=color.olive
            )
            self.world_entities.append(pool)

        # Dead trees
        for i in range(50):
            x = random.uniform(-200, 200)
            z = random.uniform(-400, -100)
            dead_tree = Entity(
                model='cube', texture='white_cube',
                scale=(0.6, random.uniform(3, 7), 0.6),
                position=(x, 2, z),
                color=color.dark_gray, collider='box',
                rotation=(random.uniform(-15, 15), 0, random.uniform(-15, 15))
            )
            self.world_entities.append(dead_tree)

        # Witch's hut (landmark)
        hut = Entity(
            model='cube', texture='white_cube',
            scale=(8, 6, 8), position=(0, 3, -300),
            color=color.violet, collider='box'
        )
        self.world_entities.append(hut)
        hut_roof = Entity(
            model='cube', texture='white_cube',
            scale=(10, 4, 10), position=(0, 8, -300),
            color=color.black,
            rotation=(0, 45, 0)
        )
        self.world_entities.append(hut_roof)

        # ============ VOLCANIC HELLSCAPE (West - negative X, -100 to -400) ============
        # Lava pools
        for i in range(12):
            x = random.uniform(-400, -100)
            z = random.uniform(-150, 150)
            lava = Entity(
                model='cube', texture='white_cube',
                scale=(random.uniform(6, 15), 0.3, random.uniform(6, 15)),
                position=(x, 0.15, z),
                color=color.orange
            )
            self.world_entities.append(lava)

        # Volcanic rocks
        for i in range(40):
            x = random.uniform(-400, -100)
            z = random.uniform(-150, 150)
            v_rock = Entity(
                model='cube', texture='white_cube',
                scale=(random.uniform(1, 4), random.uniform(2, 8), random.uniform(1, 4)),
                position=(x, 2, z),
                color=color.black, collider='box'
            )
            self.world_entities.append(v_rock)

        # Volcano (landmark)
        volcano_base = Entity(
            model='cube', texture='white_cube',
            scale=(60, 40, 60), position=(-300, 20, 0),
            color=color.dark_gray, collider='box'
        )
        self.world_entities.append(volcano_base)
        volcano_top = Entity(
            model='cube', texture='white_cube',
            scale=(20, 10, 20), position=(-300, 45, 0),
            color=color.red
        )
        self.world_entities.append(volcano_top)
        # Smoke effect
        for i in range(5):
            smoke = Entity(
                model='cube', texture='white_cube',
                scale=(8 + i * 2, 5, 8 + i * 2),
                position=(-300, 55 + i * 6, 0),
                color=color.smoke
            )
            self.world_entities.append(smoke)

        # ============ FANTASY LAND (Northeast corner - magical realm) ============
        # ============ TERROR LAND in Dream Mode - Destroyed and scary ============
        # Giant magical mushrooms / Corrupted dead mushrooms
        for i in range(45):
            x = random.uniform(100, 380)
            z = random.uniform(100, 380)
            if self.dream_mode:
                # Mix of red and black corrupted mushrooms laying on ground
                is_red = random.choice([True, False])
                stem_height = random.uniform(2, 6)
                # Corrupted mushrooms laying on ground
                stem = Entity(
                    model='cube', texture='white_cube',
                    scale=(1.5, stem_height, 1.5),
                    position=(x, 0.5, z),  # On ground
                    color=color.red if is_red else color.black,
                    rotation=(random.uniform(-80, 80), 0, random.uniform(-80, 80))  # Laying down
                )
                self.world_entities.append(stem)
                # Corrupted caps
                cap = Entity(
                    model='cube', texture='white_cube',
                    scale=(4, 1.5, 4), position=(x + random.uniform(-2, 2), 0.5, z + random.uniform(-2, 2)),
                    color=color.rgb(150, 0, 0) if is_red else color.rgb(20, 20, 20),
                    rotation=(random.uniform(-45, 45), random.uniform(0, 360), random.uniform(-45, 45))
                )
                self.world_entities.append(cap)
                # Fire particles around red mushrooms
                if is_red and random.random() > 0.5:
                    for k in range(2):
                        fire = Entity(
                            model='cube', texture='white_cube',
                            scale=(0.3, 0.8, 0.3),
                            position=(x + random.uniform(-1, 1), 1 + k * 0.5, z + random.uniform(-1, 1)),
                            color=color.orange
                        )
                        self.world_entities.append(fire)
            else:
                # Normal magical mushrooms
                stem = Entity(
                    model='cube', texture='white_cube',
                    scale=(1.5, random.uniform(4, 12), 1.5),
                    position=(x, 3, z),
                    color=color.white, collider='box'
                )
                self.world_entities.append(stem)
                cap = Entity(
                    model='cube', texture='white_cube',
                    scale=(6, 2.5, 6), position=(x, 10, z),
                    color=random.choice([color.magenta, color.violet, color.pink, color.cyan])
                )
                self.world_entities.append(cap)
                # Glowing spots on mushroom
                for j in range(3):
                    spot = Entity(
                        model='cube', texture='white_cube',
                        scale=(0.5, 0.3, 0.5),
                        position=(x + random.uniform(-2, 2), 11, z + random.uniform(-2, 2)),
                        color=color.lime
                    )
                    self.world_entities.append(spot)

        # Crystal formations (larger and more magical) / Corrupted shards in Terror Land
        for i in range(30):
            x = random.uniform(100, 380)
            z = random.uniform(100, 380)
            if self.dream_mode:
                # Corrupted blood-red and dark purple crystals
                crystal = Entity(
                    model='cube', texture='white_cube',
                    scale=(1.5, random.uniform(5, 12), 1.5),
                    position=(x, 3, z),
                    color=random.choice([color.rgb(200, 0, 0), color.rgb(100, 0, 100), color.rgb(150, 0, 50)]),
                    collider='box',
                    rotation=(random.uniform(-35, 35), random.uniform(0, 45), random.uniform(-35, 35))  # More broken
                )
                self.world_entities.append(crystal)
            else:
                crystal = Entity(
                    model='cube', texture='white_cube',
                    scale=(1.5, random.uniform(5, 12), 1.5),
                    position=(x, 3, z),
                    color=random.choice([color.cyan, color.magenta, color.pink, color.azure]),
                    collider='box',
                    rotation=(random.uniform(-15, 15), random.uniform(0, 45), random.uniform(-15, 15))
                )
                self.world_entities.append(crystal)

        # Floating islands / Crashed islands in Terror Land
        for i in range(8):
            x = random.uniform(120, 350)
            z = random.uniform(120, 350)
            if self.dream_mode:
                # Crashed islands on the ground (destroyed)
                y = random.uniform(2, 5)  # Low to ground
                floating_island = Entity(
                    model='cube', texture='white_cube',
                    scale=(random.uniform(8, 15), 3, random.uniform(8, 15)),
                    position=(x, y, z),
                    color=color.rgb(30, 20, 10), unlit=True,
                    rotation=(random.uniform(-30, 30), random.uniform(0, 90), random.uniform(-30, 30))  # Crashed angle
                )
                self.world_entities.append(floating_island)
                # Dead tree on crashed island
                tree_trunk = Entity(
                    model='cube', texture='white_cube',
                    scale=(1, 4, 1), position=(x, y + 3.5, z),
                    color=color.rgb(20, 10, 5), unlit=True,
                    rotation=(random.uniform(-45, 45), 0, random.uniform(-45, 45))  # Broken
                )
                self.world_entities.append(tree_trunk)
            else:
                y = random.uniform(15, 30)
                # Island base
                floating_island = Entity(
                    model='cube', texture='white_cube',
                    scale=(random.uniform(8, 15), 3, random.uniform(8, 15)),
                    position=(x, y, z),
                    color=color.lime
                )
                self.world_entities.append(floating_island)
                # Tree on island
                tree_trunk = Entity(
                    model='cube', texture='white_cube',
                    scale=(1, 4, 1), position=(x, y + 3.5, z),
                    color=color.pink
                )
                self.world_entities.append(tree_trunk)
                tree_top = Entity(
                    model='cube', texture='white_cube',
                    scale=(3, 3, 3), position=(x, y + 7, z),
                    color=color.magenta
                )
                self.world_entities.append(tree_top)

        # Fairy rings (circles of glowing mushrooms) / Death circles in Terror Land
        for ring in range(5):
            cx = random.uniform(150, 320)
            cz = random.uniform(150, 320)
            radius = random.uniform(5, 10)
            for angle in range(0, 360, 30):
                rad = angle * 3.14159 / 180
                x = cx + radius * cos(rad)
                z = cz + radius * sin(rad)
                if self.dream_mode:
                    # Skulls/bones in death circles
                    bone = Entity(
                        model='cube', texture='white_cube',
                        scale=(0.6, 0.4, 0.6), position=(x, 0.2, z),
                        color=color.rgb(80, 80, 80), unlit=True
                    )
                    self.world_entities.append(bone)
                else:
                    mini_mush = Entity(
                        model='cube', texture='white_cube',
                        scale=(0.4, 1.5, 0.4), position=(x, 0.75, z),
                        color=color.lime
                    )
                    self.world_entities.append(mini_mush)

        # Magical portal structure (landmark) / Nightmare portal in Terror Land
        portal_x, portal_z = 250, 250
        if self.dream_mode:
            # Broken, corrupted portal
            for side in [-1, 1]:
                pillar = Entity(
                    model='cube', texture='white_cube',
                    scale=(3, 15, 3), position=(portal_x + side * 8, 7.5, portal_z),
                    color=color.rgb(30, 0, 0), collider='box', unlit=True,
                    rotation=(random.uniform(-20, 20), 0, random.uniform(-20, 20))  # Cracked/tilted
                )
                self.world_entities.append(pillar)
            # Broken portal top (fallen)
            portal_top = Entity(
                model='cube', texture='white_cube',
                scale=(20, 3, 3), position=(portal_x, 10, portal_z + 5),  # Fallen position
                color=color.rgb(50, 0, 0), unlit=True,
                rotation=(45, 0, 0)  # Fallen angle
            )
            self.world_entities.append(portal_top)
            # Dark red nightmare glow
            portal_glow = Entity(
                model='cube', texture='white_cube',
                scale=(12, 12, 1), position=(portal_x, 8, portal_z),
                color=color.rgb(100, 0, 0), unlit=True
            )
            self.world_entities.append(portal_glow)
        else:
            # Normal magical portal
            for side in [-1, 1]:
                pillar = Entity(
                    model='cube', texture='white_cube',
                    scale=(3, 15, 3), position=(portal_x + side * 8, 7.5, portal_z),
                    color=color.violet, collider='box'
                )
                self.world_entities.append(pillar)
            # Portal top
            portal_top = Entity(
                model='cube', texture='white_cube',
                scale=(20, 3, 3), position=(portal_x, 16, portal_z),
                color=color.magenta
            )
            self.world_entities.append(portal_top)
            # Portal inner glow
            portal_glow = Entity(
                model='cube', texture='white_cube',
                scale=(12, 12, 1), position=(portal_x, 8, portal_z),
                color=color.cyan
            )
            self.world_entities.append(portal_glow)

    def create_mining_rocks(self):
        """Create mineable ore rocks throughout the world."""
        self.ore_rocks = []

        # Ore types with their locations and colors
        ore_configs = [
            # (ore_name, spawn_zone, count, color, tier)
            ('Copper Ore', 'village', 8, color.orange, 1),
            ('Iron Ore', 'village', 6, color.gray, 2),
            ('Silver Ore', 'tundra', 8, color.light_gray, 3),
            ('Gold Ore', 'desert', 6, color.gold, 4),
            ('Mithril Ore', 'swamp', 5, color.cyan, 5),
            ('Adamantite Ore', 'volcanic', 4, color.violet, 6),
            ('Shadow Ore', 'volcanic', 3, color.black, 7),
            ('Dragon Ore', 'mystic', 2, color.red, 8),
        ]

        for ore_name, zone, count, ore_color, tier in ore_configs:
            for i in range(count):
                # Determine position based on zone
                if zone == 'village':
                    x = random.uniform(-80, 80)
                    z = random.uniform(-80, 80)
                    if abs(x) < 35 and abs(z) < 35:
                        x = 50 if x > 0 else -50
                elif zone == 'tundra':
                    x = random.uniform(-250, 250)
                    z = random.uniform(120, 380)
                elif zone == 'desert':
                    x = random.uniform(120, 380)
                    z = random.uniform(-180, 180)
                elif zone == 'swamp':
                    x = random.uniform(-180, 180)
                    z = random.uniform(-380, -120)
                elif zone == 'volcanic':
                    x = random.uniform(-380, -120)
                    z = random.uniform(-130, 130)
                elif zone == 'mystic':
                    x = random.uniform(120, 330)
                    z = random.uniform(120, 330)
                else:
                    x = random.uniform(-200, 200)
                    z = random.uniform(-200, 200)

                # Create ore rock entity
                ore_rock = Entity(
                    model='cube', texture='white_cube',
                    scale=(random.uniform(1.5, 2.5), random.uniform(1, 2), random.uniform(1.5, 2.5)),
                    position=(x, 0.8, z),
                    color=ore_color, collider='box'
                )

                # Store ore data
                ore_rock.ore_name = ore_name
                ore_rock.ore_tier = tier
                ore_rock.ore_health = tier * 2  # Higher tier = more hits needed
                ore_rock.max_ore_health = tier * 2

                # Add sparkle effect (small cube on top)
                sparkle = Entity(
                    model='cube', texture='white_cube',
                    scale=(0.3, 0.3, 0.3),
                    position=(x, 1.8, z),
                    color=color.white
                )
                ore_rock.sparkle = sparkle

                # Add label
                Text(
                    text=ore_name,
                    parent=ore_rock,
                    y=1.5, scale=8,
                    billboard=True, origin=(0, 0),
                    color=ore_color
                )

                self.ore_rocks.append(ore_rock)
                self.world_entities.append(ore_rock)
                self.world_entities.append(sparkle)

    def mine_ore(self, ore_rock):
        """Mine an ore rock to get ore."""
        if not ore_rock or ore_rock.ore_health <= 0:
            return

        # Reduce ore health
        ore_rock.ore_health -= 1
        ore_rock.color = lerp(ore_rock.color, color.dark_gray, 0.2)

        if ore_rock.ore_health <= 0:
            # Give ore to player (3x in dream mode)
            ore_name = ore_rock.ore_name
            ore_count = 3 if self.dream_mode else 1
            
            if ore_name in Item.ITEM_DATA:
                # Add multiple ores in dream mode
                for _ in range(ore_count):
                    ore_data = Item.ITEM_DATA[ore_name].copy()
                    ore_data['name'] = ore_name

                    # Find empty inventory slot
                    added = False
                    for i in range(len(self.inventory)):
                        if self.inventory[i] is None:
                            self.inventory[i] = ore_data
                            added = True
                            break

                    if not added:
                        break  # Stop if inventory full
                
                if ore_count > 1:
                    self.add_chat_message(f"Mined {ore_count}x {ore_name}! (Dream Mode Bonus)", color.magenta)
                else:
                    self.add_chat_message(f"Mined {ore_name}!", color.orange)

            # Remove ore rock
            if hasattr(ore_rock, 'sparkle'):
                destroy(ore_rock.sparkle)
            destroy(ore_rock)
            if ore_rock in self.ore_rocks:
                self.ore_rocks.remove(ore_rock)

            # Respawn ore after delay (random position in same zone)
            invoke(lambda: self.respawn_ore(ore_name, ore_rock.ore_tier), delay=30)
        else:
            self.add_chat_message(f"Mining... ({ore_rock.ore_health}/{ore_rock.max_ore_health})", color.yellow)

    def respawn_ore(self, ore_name, tier):
        """Respawn an ore rock after mining."""
        # This could be expanded to respawn in the correct zone
        pass  # For now, ores don't respawn immediately

    def create_portals(self):
        """Create dungeon portals in a circle around the village."""
        # Portal positions around the village (in a circle)
        import math
        radius = 30
        for i in range(10):
            angle = (i / 10) * 2 * math.pi
            x = radius * math.cos(angle)
            z = radius * math.sin(angle)
            portal = DungeonPortal(i + 1, (x, 2, z))
            self.portals.append(portal)
            self.world_entities.append(portal)

        # ========== SECRET DUNGEON PORTALS (Hidden in each biome) ==========
        secret_dungeon_locations = [
            # Frozen Tundra - hidden behind ice formation
            ('Volcanic Inferno' if self.dream_mode else 'Frozen Tundra', (80, 1.5, 380), color.cyan, 6),
            # Desert Wasteland - buried in sand dunes
            ('Desert Wasteland', (380, 1.5, -50), color.gold, 7),
            # Dark Swamp - deep in the bog
            ('Dark Swamp', (-40, 1.5, -380), color.olive, 6),
            # Volcanic Hellscape - near lava pool
            ('Volcanic Hellscape', (-380, 1.5, 40), color.red, 8),
            # Fantasy Land - inside fairy ring
            ('Terror Land' if self.dream_mode else 'Fantasy Land', (350, 1.5, 350), color.magenta, 7),
        ]

        for biome, pos, col, diff in secret_dungeon_locations:
            secret_portal = SecretDungeonPortal(biome, pos, col, difficulty=diff)
            self.secret_portals.append(secret_portal)
            self.world_entities.append(secret_portal)

    def check_portal_interaction(self):
        """Check if player can interact with a dungeon portal."""
        if not self.player:
            return None

        for portal in self.portals:
            dist = distance(self.player, portal)
            if dist < 3:
                return portal
        return None

    def check_secret_portal_interaction(self):
        """Check if player can interact with a secret dungeon portal."""
        if not self.player:
            return None

        for portal in self.secret_portals:
            dist = distance(self.player, portal)
            if dist < 4:
                return portal
        
        # Check for dream portal escape
        if self.dream_mode and hasattr(self, 'dream_portal') and self.dream_portal:
            dist = distance(self.player, self.dream_portal)
            if dist < 3:
                # Give special staff reward
                what_happened_staff = Item.create('What Happened Staff')
                if what_happened_staff:
                    for i, slot in enumerate(self.inventory):
                        if slot is None:
                            self.inventory[i] = what_happened_staff
                            self.add_chat_message("You obtained 'What Happened' Staff!", color.magenta)
                            self.update_hotbar_display()
                            break
                
                # Escape dream mode (reset to normal)
                self.add_chat_message("You escaped the nightmare...", color.cyan)
                # Don't actually exit, just give the staff
        
        # Check for Error404 dungeon portal
        if self.dream_mode and hasattr(self, 'error404_portal') and self.error404_portal:
            dist = distance(self.player, self.error404_portal)
            if dist < 3:
                self.enter_error404_dungeon()
                return None
        
        # Check for Error404 glitched room portal (white portal to Error Village)
        if self.error404_mode and hasattr(self, 'error404_glitched_room_portal') and self.error404_glitched_room_portal:
            dist = distance(self.player, self.error404_glitched_room_portal)
            if dist < 3:
                # Teleport to Error Village
                self.player.position = Vec3(-500, 2, 500)
                self.add_chat_message("this wasnt real it was all a dream this is reality? enjoy your way out you going to destroy the code to be free", color.red)
                self.add_chat_message("You entered the ERROR 404 dimension...", color.rgb(255, 0, 255))
                return None
        
        # Check for Error Village escape portal (white portal)
        if self.error404_mode and hasattr(self, 'error404_portal') and self.error404_portal:
            dist = distance(self.player, self.error404_portal)
            if dist < 3:
                self.add_chat_message("You escaped the ERROR 404 dimension...", color.white)
                self.add_chat_message("But was it real? Or just another dream?", color.gray)
                # Don't actually exit, just show message
                return None
        
        return None

    def enter_secret_dungeon(self, biome_name, difficulty):
        """Enter a secret biome dungeon with special loot."""
        self.in_secret_dungeon = True
        self.in_dungeon = True
        self.current_secret_biome = biome_name
        self.current_dungeon = difficulty
        self.dungeon_wave = 1
        self.wave_cooldown = 0

        # Clear current enemies
        for enemy in self.enemies[:]:
            destroy(enemy)
        self.enemies.clear()

        # Hide village world
        for entity in self.world_entities:
            entity.visible = False

        # Create special dungeon environment based on biome
        self.create_secret_dungeon_environment(biome_name, difficulty)

        # Create wave display
        if self.wave_text:
            destroy(self.wave_text)
        self.wave_text = Text(
            text=f'Secret Wave 1',
            position=(0, 0.4),
            scale=2,
            color=color.yellow
        )
    
    def enter_error404_dungeon(self):
        """Enter the Error404 Dungeon - Ultimate challenge."""
        self.in_error404_dungeon = True
        self.in_dungeon = True
        self.current_dungeon = 'error404'
        self.dungeon_wave = 1
        self.wave_cooldown = 0
        
        # Clear enemies
        for enemy in self.enemies[:]:
            destroy(enemy)
        self.enemies.clear()
        
        # Hide world
        for entity in self.world_entities:
            entity.visible = False
        
        # Create glitched environment
        self.create_error404_environment()
        
        # Wave display
        if self.wave_text:
            destroy(self.wave_text)
        self.wave_text = Text(
            text='ERROR 404: WAVE 1',
            position=(0, 0.4),
            scale=2,
            color=color.rgb(255, 0, 255)
        )
        
        # Teleport player
        self.player.position = Vec3(0, 1, 0)
        
        self.add_chat_message("ERROR 404: REALITY NOT FOUND", color.rgb(255, 0, 255))
        
        # Spawn first wave immediately
        self.spawn_error404_wave(1)

    def teleport_to_secret_base(self):
        """Teleport player to secret base area at wave 5."""
        # Clear dungeon environment
        for entity in self.dungeon_entities:
            destroy(entity)
        self.dungeon_entities.clear()
        
        # Flag to prevent wave spawning in base
        self.in_secret_base = True
        
        # Create secret base
        self.create_secret_base(self.current_secret_biome)
        
        # Move player to base
        self.player.position = Vec3(0, 2, 0)
        
        self.add_chat_message(f"Wave 5 Complete! Discovered Secret {self.current_secret_biome} Base!", color.gold)
        self.add_chat_message("Rest and craft, then return to battle!", color.cyan)

    def create_secret_base(self, biome_name):
        """Create a safe base area for the secret dungeon."""
        biome_colors = {
            'Frozen Tundra': color.cyan,
            'Desert Wasteland': color.gold,
            'Dark Swamp': color.olive,
            'Volcanic Hellscape': color.red,
            'Fantasy Land': color.magenta,
        }
        floor_col = biome_colors.get(biome_name, color.gray)
        
        # Floor
        floor = Entity(model='plane', texture='white_cube', color=floor_col * 0.5,
                       scale=(60, 1, 60), position=(0, 0, 0))
        self.dungeon_entities.append(floor)
        
        # Walls
        wall_col = floor_col * 0.7
        for x, z, rx, rz in [(-30, 0, 60, 1), (30, 0, 60, 1), (0, -30, 1, 60), (0, 30, 1, 60)]:
            wall = Entity(model='cube', texture='white_cube', color=wall_col,
                          scale=(rx, 15, rz), position=(x, 7.5, z))
            self.dungeon_entities.append(wall)
        
        # Ceiling
        ceiling = Entity(model='plane', texture='white_cube', color=color.black,
                         scale=(60, 1, 60), position=(0, 15, 0), rotation=(180, 0, 0))
        self.dungeon_entities.append(ceiling)
        
        # Anvil for crafting
        anvil = Entity(model='cube', texture='white_cube', color=color.dark_gray,
                       scale=(2, 1, 1), position=(-10, 0.5, 0))
        self.dungeon_entities.append(anvil)
        self.secret_base_anvil = anvil
        Text(text='ANVIL', parent=anvil, y=1.5, scale=10, billboard=True,
             origin=(0, 0), color=color.white)
        Text(text='[F] Craft', parent=anvil, y=1, scale=8, billboard=True,
             origin=(0, 0), color=color.light_gray)
        
        # Chest for storage
        chest = Entity(model='cube', texture='white_cube', color=color.brown,
                       scale=(2, 1.5, 1.5), position=(10, 0.75, 0))
        self.dungeon_entities.append(chest)
        Text(text='CHEST', parent=chest, y=1.5, scale=10, billboard=True,
             origin=(0, 0), color=color.yellow)
        
        # Return portal to continue dungeon
        return_portal = Entity(model='cube', texture='white_cube', color=color.violet,
                               scale=(3, 4, 0.5), position=(0, 2, -25))
        self.dungeon_entities.append(return_portal)
        Text(text='CONTINUE', parent=return_portal, y=1.8, scale=12, billboard=True,
             origin=(0, 0), color=color.white)
        Text(text='[E] Return to Battle', parent=return_portal, y=1.3, scale=8, billboard=True,
             origin=(0, 0), color=color.light_gray)
        self.secret_base_portal = return_portal
        
        # Exit portal
        exit_portal = Entity(model='cube', texture='white_cube', color=color.gold,
                             scale=(3, 4, 0.5), position=(0, 2, 25))
        self.dungeon_entities.append(exit_portal)
        Text(text='EXIT', parent=exit_portal, y=1.5, scale=12, billboard=True,
             origin=(0, 0), color=color.white)
        Text(text='[E] Leave Dungeon', parent=exit_portal, y=1.1, scale=8, billboard=True,
             origin=(0, 0), color=color.light_gray)
        self.dungeon_exit = exit_portal

    def return_to_secret_dungeon(self):
        """Return from secret base to continue dungeon waves."""
        # Clear base flag
        self.in_secret_base = False
        
        # Clear base
        for entity in self.dungeon_entities:
            destroy(entity)
        self.dungeon_entities.clear()
        
        # Recreate dungeon environment
        self.create_secret_dungeon_environment(self.current_secret_biome, self.current_dungeon)
        
        # Move player
        self.player.position = Vec3(0, 2, 0)
        
        self.add_chat_message("Returning to battle!", color.orange)
        self.add_chat_message(f"Wave {self.dungeon_wave} incoming!", color.orange)
        
        # Spawn next wave
        self.wave_cooldown = 2.0
        invoke(lambda: self.spawn_secret_dungeon_wave(self.current_secret_biome, self.current_dungeon), delay=2.0)

    def create_secret_dungeon_environment(self, biome_name, difficulty):
        """Create a special dungeon environment themed to the biome."""
        # Floor
        biome_colors = {
            'Frozen Tundra': color.cyan,
            'Desert Wasteland': color.gold,
            'Dark Swamp': color.olive,
            'Volcanic Hellscape': color.red,
            'Fantasy Land': color.magenta,
        }
        floor_col = biome_colors.get(biome_name, color.gray)

        floor = Entity(model='plane', texture='white_cube', color=floor_col * 0.3,
                       scale=(80, 1, 80), position=(0, 0, 0))
        self.dungeon_entities.append(floor)

        # Walls with biome theme
        wall_col = floor_col * 0.5
        for x, z, rx, rz in [(-40, 0, 80, 1), (40, 0, 80, 1), (0, -40, 1, 80), (0, 40, 1, 80)]:
            wall = Entity(model='cube', texture='white_cube', color=wall_col,
                          scale=(rx, 15, rz), position=(x, 7.5, z))
            self.dungeon_entities.append(wall)

        # Pillars with glowing effect
        for x, z in [(-25, -25), (25, -25), (-25, 25), (25, 25), (0, 0)]:
            pillar = Entity(model='cube', texture='white_cube', color=floor_col,
                            scale=(3, 12, 3), position=(x, 6, z))
            self.dungeon_entities.append(pillar)

        # Ceiling
        ceiling = Entity(model='plane', texture='white_cube', color=color.black,
                         scale=(80, 1, 80), position=(0, 15, 0), rotation=(180, 0, 0))
        self.dungeon_entities.append(ceiling)

        # Exit portal
        exit_portal = Entity(model='cube', texture='white_cube', color=color.gold,
                             scale=(3, 4, 0.5), position=(0, 2, -35))
        self.dungeon_entities.append(exit_portal)
        Text(text='EXIT', parent=exit_portal, y=1.5, scale=12, billboard=True,
             origin=(0, 0), color=color.white)
        Text(text='[E] Leave', parent=exit_portal, y=1.1, scale=8, billboard=True,
             origin=(0, 0), color=color.light_gray)
        self.dungeon_exit = exit_portal

        # Special biome decorations
        if biome_name == 'Frozen Tundra':
            for _ in range(8):
                ice = Entity(model='cube', texture='white_cube', color=color.azure,
                             scale=(random.uniform(1, 3), random.uniform(2, 6), random.uniform(1, 3)),
                             position=(random.uniform(-35, 35), 0, random.uniform(-35, 35)))
                self.dungeon_entities.append(ice)
        elif biome_name == 'Volcanic Hellscape':
            for _ in range(6):
                lava = Entity(model='cube', texture='white_cube', color=color.orange,
                              scale=(random.uniform(3, 6), 0.1, random.uniform(3, 6)),
                              position=(random.uniform(-30, 30), 0.05, random.uniform(-30, 30)))
                self.dungeon_entities.append(lava)

    def spawn_secret_dungeon_wave(self, biome_name, difficulty):
        """Spawn enemies for secret dungeon wave - harder and themed."""
        biome_enemies = {
            'Frozen Tundra': [
                ("Elite Frost Wolf", 400, color.white, 3.0),
                ("Frost Titan", 800, color.cyan, 2.0),
                ("Ice Wraith", 350, color.azure, 3.5),
            ],
            'Desert Wasteland': [
                ("Elite Sand Scorpion", 380, color.gold, 3.2),
                ("Ancient Mummy", 600, color.white, 2.5),
                ("Sandstorm Elemental", 500, color.yellow, 2.8),
            ],
            'Dark Swamp': [
                ("Elite Bog Creature", 450, color.olive, 2.5),
                ("Poison Hydra", 700, color.green, 2.0),
                ("Dark Witch", 400, color.violet, 3.0),
            ],
            'Volcanic Hellscape': [
                ("Elite Fire Imp", 350, color.orange, 4.0),
                ("Magma Lord", 900, color.red, 1.8),
                ("Phoenix", 600, color.yellow, 3.5),
            ],
            'Fantasy Land': [
                ("Elite Fairy", 380, color.magenta, 3.5),
                ("Dream Nightmare", 550, color.violet, 3.0),
                ("Corrupted Unicorn", 700, color.white, 2.5),
            ],
        }

        enemies_to_spawn = biome_enemies.get(biome_name, biome_enemies['Frozen Tundra'])
        wave_mult = 1 + (self.dungeon_wave - 1) * 0.3  # Enemies get stronger each wave

        # Spawn 3-5 enemies per wave
        num_enemies = min(3 + self.dungeon_wave, 8)
        for i in range(num_enemies):
            enemy_data = random.choice(enemies_to_spawn)
            name, base_hp, col, spd = enemy_data

            # Random position
            x = random.uniform(-30, 30)
            z = random.uniform(-30, 30)
            while abs(x) < 8 and abs(z) < 8:  # Not too close to spawn
                x = random.uniform(-30, 30)
                z = random.uniform(-30, 30)

            hp = int(base_hp * wave_mult)
            xp = hp // 2  # Good XP from secret dungeon

            enemy = Enemy(name, (x, 1.5, z), hp, col, xp_value=xp)
            enemy.target = self.player
            enemy.base_speed = spd
            self.enemies.append(enemy)
        
        self.add_chat_message(f"Spawned {num_enemies} enemies!", color.orange)

        # Every 3 waves, spawn the secret boss
        if self.dungeon_wave % 3 == 0:
            boss_data = {
                'Frozen Tundra': ("Frost Emperor", 3000, color.cyan),
                'Desert Wasteland': ("Pharaoh God-King", 3500, color.gold),
                'Dark Swamp': ("Swamp Abomination", 2800, color.olive),
                'Volcanic Hellscape': ("Infernal Dragon", 4000, color.red),
                'Fantasy Land': ("Corrupted Fairy Queen", 3200, color.magenta),
            }
            bname, bhp, bcol = boss_data.get(biome_name, boss_data['Frozen Tundra'])
            boss = BossEnemy(bname, (0, 1.5, 20), int(bhp * wave_mult), bcol, xp_value=2000)
            boss.target = self.player
            self.enemies.append(boss)
            self.add_chat_message(f"SECRET BOSS: {bname} appeared!", color.gold)

    def drop_secret_loot(self, biome_name):
        """Drop legendary secret loot from the secret dungeon."""
        if biome_name not in SECRET_LOOT:
            return

        # 30% chance per enemy kill, 100% from boss
        loot_options = SECRET_LOOT[biome_name]
        loot = random.choice(loot_options)

        item_name = loot['name']
        # Create the item
        dropped_item = Item.create(item_name)
        if dropped_item:
            # Find empty inventory slot
            added = False
            for i in range(len(self.inventory)):
                if self.inventory[i] is None:
                    self.inventory[i] = dropped_item
                    added = True
                    break
            
            if added:
                self.add_chat_message(f"SECRET LOOT: {item_name}!", color.gold)
                self.update_hotbar_display()
            else:
                self.add_chat_message(f"Inventory full! Missed: {item_name}", color.red)

    def enter_dungeon(self, dungeon_level):
        """Enter a dungeon and spawn appropriate enemies."""
        self.in_dungeon = True
        self.current_dungeon = dungeon_level
        self.dungeon_wave = 1
        self.wave_cooldown = 0

        # Clear current enemies
        for enemy in self.enemies[:]:
            destroy(enemy)
        self.enemies.clear()

        # Hide village world
        for entity in self.world_entities:
            entity.visible = False

        # Create dungeon environment
        self.create_dungeon_environment(dungeon_level)

        # Create wave display
        if self.wave_text:
            destroy(self.wave_text)
        self.wave_text = Text(
            text=f'Wave 1',
            position=(0, 0.4),
            origin=(0, 0),
            scale=2,
            color=color.yellow
        )

        # Spawn first wave
        self.spawn_dungeon_wave()

        # Move player to dungeon start
        self.player.position = Vec3(0, 2, 0)

        self.add_chat_message(f"Entered Dungeon {dungeon_level}!", color.yellow)
        self.add_chat_message("Defeat enemies! Waves are INFINITE!", color.red)
        self.area_text.text = f'Dungeon {dungeon_level}'

    def exit_dungeon(self):
        """Exit the current dungeon and return to village."""
        if not self.in_dungeon:
            return

        # Clear pet target to prevent crash
        if self.pet:
            self.pet.target = None

        # Show final wave reached
        if self.in_secret_dungeon:
            self.add_chat_message(f"Escaped Secret Dungeon at Wave {self.dungeon_wave}!", color.gold)
        else:
            self.add_chat_message(f"Escaped at Wave {self.dungeon_wave}!", color.orange)

        self.in_dungeon = False
        self.in_secret_dungeon = False
        self.in_secret_base = False
        self.in_error404_dungeon = False
        self.current_secret_biome = None
        self.secret_base_anvil = None
        self.secret_base_portal = None
        self.current_dungeon = 0
        self.dungeon_wave = 0

        # Clear wave text
        if self.wave_text:
            destroy(self.wave_text)
            self.wave_text = None

        # Clear dungeon enemies
        for enemy in self.enemies[:]:
            destroy(enemy)
        self.enemies.clear()

        # Clear dungeon environment
        for entity in self.dungeon_entities:
            destroy(entity)
        self.dungeon_entities.clear()

        # Show village world
        for entity in self.world_entities:
            entity.visible = True

        # Respawn village enemies
        self.spawn_enemies()

        # Move player back to village
        self.player.position = Vec3(0, 2, 0)

        self.add_chat_message("Returned to Village!", color.cyan)
        self.area_text.text = 'Village'

    def create_dungeon_environment(self, level):
        """Create the dungeon environment based on level."""
        self.dungeon_entities = []

        # Dungeon floor colors based on level
        floor_colors = {
            1: color.brown, 2: color.olive, 3: color.dark_gray,
            4: color.gray, 5: color.blue.tint(-0.3), 6: color.violet.tint(-0.3),
            7: color.magenta.tint(-0.3), 8: color.orange.tint(-0.3),
            9: color.red.tint(-0.3), 10: color.black
        }

        # Dungeon floor
        floor = Entity(model='plane', texture='white_cube',
                       color=floor_colors.get(level, color.dark_gray),
                       scale=(100, 1, 100), position=(0, 0, 0))
        self.dungeon_entities.append(floor)

        # Dungeon walls
        wall_color = color.dark_gray
        for i in range(4):
            angle = i * 90
            x = 50 * [0, 1, 0, -1][i]
            z = 50 * [1, 0, -1, 0][i]
            wall = Entity(model='cube', texture='white_cube', color=wall_color,
                          scale=(100, 15, 2) if i % 2 == 0 else (2, 15, 100),
                          position=(x, 7, z))
            self.dungeon_entities.append(wall)

        # Add some pillars/obstacles based on level
        import random
        num_pillars = 5 + level * 2
        for _ in range(num_pillars):
            px = random.uniform(-40, 40)
            pz = random.uniform(-40, 40)
            pillar = Entity(model='cube', texture='white_cube', color=color.gray,
                            scale=(3, 8 + level, 3), position=(px, 4, pz))
            self.dungeon_entities.append(pillar)

        # Exit portal in dungeon
        exit_portal = Entity(model='cube', texture='white_cube', color=color.yellow,
                             scale=(3, 4, 0.5), position=(0, 2, -45))
        self.dungeon_entities.append(exit_portal)
        Text(text='EXIT', parent=exit_portal, y=1.5, scale=12, billboard=True,
             origin=(0, 0), color=color.white)
        Text(text='[E] Leave', parent=exit_portal, y=1.1, scale=8, billboard=True,
             origin=(0, 0), color=color.light_gray)
        self.dungeon_exit = exit_portal

    def spawn_dungeon_enemies(self, level):
        """Spawn enemies appropriate for the dungeon level."""
        import random

        # Get enemies for this dungeon level
        valid_enemies = [(name, data) for name, data in ENEMY_TYPES.items()
                         if level in data['dungeons']]

        if not valid_enemies:
            return

        # Number of enemies based on level
        num_enemies = 5 + level * 3

        for i in range(num_enemies):
            enemy_name, enemy_data = random.choice(valid_enemies)

            # Random position in dungeon
            x = random.uniform(-35, 35)
            z = random.uniform(-35, 35)

            # Don't spawn too close to player start
            while abs(x) < 10 and abs(z) < 10:
                x = random.uniform(-35, 35)
                z = random.uniform(-35, 35)

            # Use RangedEnemy for archer/mage types
            is_ranged = any(r in enemy_name.lower() for r in ['archer', 'mage', 'lich', 'dark mage'])
            if is_ranged:
                enemy = RangedEnemy(
                    name=enemy_name,
                    position=(x, enemy_data['scale'][1] / 2, z),
                    health=enemy_data['hp'],
                    enemy_color=enemy_data['color'],
                    xp_value=enemy_data['xp'],
                    projectile_color=enemy_data['color']
                )
            else:
                enemy = Enemy(
                    name=enemy_name,
                    position=(x, enemy_data['scale'][1] / 2, z),
                    health=enemy_data['hp'],
                    enemy_color=enemy_data['color'],
                    xp_value=enemy_data['xp']
                )
            enemy.scale = enemy_data['scale']
            enemy.speed = enemy_data['speed']
            enemy.target = self.player
            self.enemies.append(enemy)

    def spawn_dungeon_wave(self):
        """Spawn a wave of enemies in the dungeon, scaling with wave number."""
        import random

        level = self.current_dungeon
        wave = self.dungeon_wave
        
        # ========== DREAM MODE: Spawn dream enemies in dungeons ==========
        if self.dream_mode:
            # Number of enemies increases each wave
            base_enemies = 3 + level * 2
            num_enemies = base_enemies + (wave - 1) * 2
            
            # Dream enemies scale with dungeon level and wave
            hp_base = 150 * level
            hp_multiplier = 1.0 + (wave - 1) * 0.15
            
            dream_enemy_types = [
                ("Shadow Stalker", color.rgb(30, 0, 50)),
                ("Void Wraith", color.rgb(50, 0, 80)),
                ("Nightmare Horror", color.rgb(100, 0, 100)),
                ("Abyss Walker", color.rgb(20, 0, 40)),
                ("Terror Spawn", color.rgb(80, 0, 80)),
            ]
            
            for i in range(num_enemies):
                name, col = random.choice(dream_enemy_types)
                hp = int(hp_base * hp_multiplier)
                xp = hp // 2  # 2x XP
                
                # Random spawn position
                angle = random.uniform(0, 360)
                distance_from_center = random.uniform(15, 35)
                x = distance_from_center * cos(angle * 0.0174533)
                z = distance_from_center * sin(angle * 0.0174533)
                
                enemy = Enemy(name, (x, 0.75, z), hp, col, xp_value=xp)
                enemy.target = self.player
                enemy.base_speed = 2.0 + (level * 0.2)
                self.enemies.append(enemy)
            
            # Spawn dream boss every 3 waves
            if wave % 3 == 0:
                boss_hp = int(hp_base * 5 * hp_multiplier)
                boss_xp = boss_hp // 2
                dream_boss = BossEnemy(f"Nightmare Lord Wave {wave}", (0, 0.75, 30), boss_hp, color.rgb(150, 0, 150), xp_value=boss_xp)
                dream_boss.target = self.player
                dream_boss.can_magic = True
                dream_boss.projectile_scale = 2.0 + (wave * 0.2)
                self.enemies.append(dream_boss)
                self.add_chat_message(f"Wave {wave} - {num_enemies} enemies + NIGHTMARE LORD!", color.magenta)
            else:
                self.add_chat_message(f"Wave {wave} - {num_enemies} dream enemies!", color.violet)
            
            return

        # ========== NORMAL MODE: Regular dungeon enemies ==========
        # Get enemies for this dungeon level
        valid_enemies = [(name, data) for name, data in ENEMY_TYPES.items()
                         if level in data['dungeons']]

        if not valid_enemies:
            return

        # Number of enemies increases each wave
        base_enemies = 3 + level * 2
        num_enemies = base_enemies + (wave - 1) * 2

        # HP multiplier increases each wave
        hp_multiplier = 1.0 + (wave - 1) * 0.15

        for i in range(num_enemies):
            enemy_name, enemy_data = random.choice(valid_enemies)

            # Random position in dungeon
            x = random.uniform(-35, 35)
            z = random.uniform(-35, 35)

            # Don't spawn too close to player
            while abs(x) < 8 and abs(z) < 8:
                x = random.uniform(-35, 35)
                z = random.uniform(-35, 35)

            # Scale HP with wave
            scaled_hp = int(enemy_data['hp'] * hp_multiplier)

            # Use RangedEnemy for archer/mage types
            is_ranged = any(r in enemy_name.lower() for r in ['archer', 'mage', 'lich', 'dark mage'])
            if is_ranged:
                enemy = RangedEnemy(
                    name=enemy_name,
                    position=(x, enemy_data['scale'][1] / 2, z),
                    health=scaled_hp,
                    enemy_color=enemy_data['color'],
                    xp_value=enemy_data['xp'],
                    projectile_color=enemy_data['color']
                )
            else:
                enemy = Enemy(
                    name=enemy_name,
                    position=(x, enemy_data['scale'][1] / 2, z),
                    health=scaled_hp,
                    enemy_color=enemy_data['color'],
                    xp_value=enemy_data['xp']
                )
            enemy.scale = enemy_data['scale']
            enemy.speed = enemy_data['speed'] + (wave * 0.1)  # Slightly faster each wave
            enemy.target = self.player
            self.enemies.append(enemy)

        self.add_chat_message(f"Wave {wave} - {num_enemies} enemies!", color.yellow)
    
    def create_error404_environment(self):
        """Create glitched Error404 dungeon environment."""
        self.dungeon_entities = []
        
        # Glitched floor - flickering colors
        for i in range(20):
            for j in range(20):
                tile = Entity(
                    model='cube',
                    texture='white_cube',
                    color=color.rgb(random.randint(0, 255), 0, random.randint(100, 255)),
                    scale=(5, 0.1, 5),
                    position=((i-10)*5, 0, (j-10)*5),
                    alpha=random.uniform(0.5, 1.0)
                )
                self.dungeon_entities.append(tile)
        
        # Floating glitch blocks
        for _ in range(50):
            glitch_block = Entity(
                model='cube',
                texture='white_cube',
                color=color.rgb(random.randint(0, 255), random.randint(0, 100), random.randint(200, 255)),
                scale=(random.uniform(0.5, 2), random.uniform(0.5, 2), random.uniform(0.5, 2)),
                position=(random.uniform(-40, 40), random.uniform(2, 15), random.uniform(-40, 40)),
                rotation=(random.randint(0, 360), random.randint(0, 360), random.randint(0, 360)),
                alpha=random.uniform(0.3, 0.8)
            )
            self.dungeon_entities.append(glitch_block)
    
    def spawn_error404_wave(self, wave):
        """Spawn Error404 dungeon waves."""
        if wave == 1:
            # Random glitched enemies
            for i in range(5):
                enemy = Enemy(
                    "G̴L̴I̴T̴C̴H̴ E̴N̴T̴I̴T̴Y̴",
                    (random.uniform(-15, 15), 0.75, random.uniform(-15, 15)),
                    health=500,
                    enemy_color=color.rgb(random.randint(100, 255), 0, random.randint(150, 255)),
                    xp_value=500
                )
                enemy.target = self.player
                enemy.speed = 4
                self.enemies.append(enemy)
        
        elif wave == 2:
            # FINAL BOSS: tErRoR 404
            self.spawn_terror404_boss()
        
        elif wave == 3:
            # TRUE FINAL BOSS: Evil Chez Whopper Spider
            self.spawn_evil_chez_boss()
    
    def spawn_terror404_boss(self):
        """Spawn the tErRoR 404 boss - extremely overpowered."""
        terror = BossEnemy(
            "tErRoR 404",
            (0, 0.75, 15),
            health=50000,
            enemy_color=color.rgb(255, 0, 255),
            xp_value=100000
        )
        terror.target = self.player
        terror.speed = 8
        terror.scale = (4, 4, 4)
        
        # ALL ABILITIES
        terror.can_fireball = True
        terror.can_iceball = True
        terror.can_poison = True
        terror.can_magic = True
        terror.can_terror_scream = True
        terror.can_blood_rage = True
        terror.can_shadow_dash = True
        terror.can_soul_drain = True
        terror.can_shadow_bullet = True
        
        # Set short cooldowns for spam attacks
        terror.special_cooldown = 0.5
        terror.projectile_scale = 6.0
        
        self.enemies.append(terror)
        self.add_chat_message("tErRoR 404 HAS MANIFESTED!", color.rgb(255, 0, 255))
    
    def spawn_evil_chez_boss(self):
        """Spawn Evil Chez Whopper Spider - true final boss."""
        chez = BossEnemy(
            "Evil Chez Whopper Spider",
            (0, 0.75, 15),
            health=75000,
            enemy_color=color.black,
            xp_value=150000
        )
        chez.target = self.player
        chez.speed = 10
        chez.scale = (5, 3, 5)  # Wide spider shape
        
        # ALL ABILITIES + EXTRA
        chez.can_fireball = True
        chez.can_iceball = True
        chez.can_poison = True
        chez.can_magic = True
        chez.can_terror_scream = True
        chez.can_blood_rage = True
        chez.can_shadow_dash = True
        chez.can_soul_drain = True
        chez.can_shadow_bullet = True
        
        # Extremely aggressive
        chez.special_cooldown = 0.3
        chez.projectile_scale = 8.0
        
        self.enemies.append(chez)
        self.add_chat_message("THE EVIL CHEZ WHOPPER SPIDER AWAKENS!", color.black)
    
    def check_dungeon_wave(self):
        """Check if wave is complete and spawn next wave."""
        if not self.in_dungeon:
            return
        
        # Don't spawn waves in secret base
        if self.in_secret_dungeon and hasattr(self, 'secret_base_anvil') and self.secret_base_anvil:
            return
        
        # Cooldown between waves
        if self.wave_cooldown > 0:
            self.wave_cooldown -= time.dt
            return
        
        # Check if all enemies are dead
        if len(self.enemies) == 0:
            # Error404 dungeon progression
            if hasattr(self, 'in_error404_dungeon') and self.in_error404_dungeon:
                if self.dungeon_wave == 1:
                    self.add_chat_message("WAVE 1 COMPLETE - BOSS INCOMING", color.rgb(255, 0, 255))
                    # Give tErRoR bOw reward
                    terror_bow = {
                        'name': 'tErRoR bOw',
                        'type': 'weapon',
                        'weapon_type': 'bow',
                        'damage': 100,
                        'range': 30,
                        'rarity': 'legendary',
                        'color': color.rgb(255, 0, 255),
                        'fear_active': True
                    }
                    # Find empty slot and add bow
                    added = False
                    for i in range(len(self.inventory)):
                        if self.inventory[i] is None:
                            self.inventory[i] = terror_bow
                            added = True
                            self.add_chat_message("Obtained tErRoR bOw! (100 dmg, inflicts FEAR)", color.rgb(255, 0, 255))
                            self.update_hotbar_display()
                            break
                    if not added:
                        self.add_chat_message("Inventory full! Could not obtain tErRoR bOw!", color.red)
                    
                    self.dungeon_wave = 2
                    self.wave_cooldown = 3.0
                    if self.wave_text:
                        self.wave_text.text = 'ERROR 404: BOSS WAVE'
                    self.spawn_error404_wave(2)
                    return
                elif self.dungeon_wave == 2:
                    self.add_chat_message("tErRoR 404 DEFEATED - FINAL BOSS INCOMING", color.rgb(255, 0, 255))
                    self.dungeon_wave = 3
                    self.wave_cooldown = 5.0
                    if self.wave_text:
                        self.wave_text.text = 'ERROR 404: FINAL BOSS'
                    self.spawn_error404_wave(3)
                    return
                elif self.dungeon_wave == 3:
                    self.add_chat_message("ERROR404 DUNGEON COMPLETE! YOU ARE LEGENDARY!", color.gold)
                    self.exit_dungeon()
                    return
            
            # No enemies at all - spawn next wave
            # Give wave completion rewards BEFORE incrementing wave
            if self.in_secret_dungeon:
                self.give_secret_wave_rewards()
            else:
                self.give_wave_rewards(self.current_dungeon, self.dungeon_wave)

            # Start next wave after brief delay
            self.wave_cooldown = 2.0  # 2 second delay
            self.dungeon_wave += 1

            # Wave 5 in secret dungeons - teleport to secret base
            if self.in_secret_dungeon and self.dungeon_wave == 5:
                self.teleport_to_secret_base()
                return

            # Update wave text
            if self.wave_text:
                if self.in_secret_dungeon:
                    self.wave_text.text = f'Secret Wave {self.dungeon_wave}'
                    self.wave_text.color = color.gold
                else:
                    self.wave_text.text = f'Wave {self.dungeon_wave}'
                    self.wave_text.color = color.red if self.dungeon_wave >= 10 else color.yellow

            self.add_chat_message(f"Wave {self.dungeon_wave} incoming!", color.orange)

            # Spawn appropriate wave type
            if self.in_secret_dungeon:
                invoke(lambda: self.spawn_secret_dungeon_wave(self.current_secret_biome, self.current_dungeon), delay=2.0)
            else:
                invoke(self.spawn_dungeon_wave, delay=2.0)

    def give_secret_wave_rewards(self):
        """Give rewards for completing a secret dungeon wave."""
        # High XP reward
        base_xp = 500
        wave_mult = 1 + ((self.dungeon_wave - 1) * 0.5)  # -1 because we already incremented wave
        xp_reward = int(base_xp * wave_mult)

        self.character.gain_experience(xp_reward)
        self.add_chat_message(f"Secret Wave {self.dungeon_wave - 1} complete! +{xp_reward} XP", color.gold)

        # 40% chance for secret loot each wave, 100% every 3 waves (boss wave)
        if (self.dungeon_wave - 1) % 3 == 0 or random.random() < 0.4:
            self.drop_secret_loot(self.current_secret_biome)

    def give_wave_rewards(self, dungeon_level, wave_completed):
        """Give XP and item rewards for completing a wave."""
        import random

        # XP reward scales with dungeon level and wave number
        # Base XP: dungeon_level * 50, multiplied by wave number
        # Dungeon 10 gives MASSIVE XP
        base_xp = dungeon_level * 50
        wave_multiplier = 1 + (wave_completed * 0.5)  # Wave 1 = 1.5x, Wave 5 = 3.5x, Wave 10 = 6x

        # Dungeon 10 bonus - extra 2x XP
        if dungeon_level == 10:
            wave_multiplier *= 2

        xp_reward = int(base_xp * wave_multiplier)
        self.character.gain_experience(xp_reward)
        self.add_chat_message(f"Wave {wave_completed} complete! +{xp_reward} XP", color.gold)

        # Determine loot tier based on dungeon level
        if dungeon_level <= 2:
            tier = 'tier1'
        elif dungeon_level <= 4:
            tier = 'tier2'
        elif dungeon_level <= 6:
            tier = 'tier3'
        elif dungeon_level <= 8:
            tier = 'tier4'
        else:
            tier = 'tier5'

        # EVERY wave gives a random item from the tier
        tier_loot = Item.WAVE_LOOT_TIERS.get(tier, Item.WAVE_LOOT_TIERS['tier1'])
        reward_item_name = random.choice(tier_loot)
        self.add_item_reward(reward_item_name, "LOOT")

        # MILESTONE waves (5, 10) give BONUS guaranteed good items
        milestone_rewards = Item.MILESTONE_REWARDS.get(dungeon_level, {})
        if wave_completed in milestone_rewards:
            possible_items = milestone_rewards[wave_completed]
            bonus_item_name = random.choice(possible_items)
            self.add_item_reward(bonus_item_name, "MILESTONE BONUS")

    def add_item_reward(self, item_name, reward_type="REWARD"):
        """Helper to add an item reward to inventory."""
        reward_item = Item.create(item_name)
        if reward_item:
            # Try to add to inventory
            added = False
            for i in range(len(self.inventory)):
                if self.inventory[i] is None:
                    self.inventory[i] = reward_item
                    added = True
                    break

            if added:
                rarity_col = Item.RARITY_COLORS.get(reward_item.get('rarity', 'common'), color.white)
                self.add_chat_message(f"{reward_type}: {item_name}!", rarity_col)
                self.update_hotbar_display()
            else:
                self.add_chat_message(f"Inventory full! Missed: {item_name}", color.red)

    def check_enemy_respawn(self):
        """Check if enemies need to respawn outside dungeons."""
        if not self.in_dungeon:
            self.enemy_respawn_timer -= time.dt
            if self.enemy_respawn_timer <= 0:
                # Count current enemies
                current_count = len([e for e in self.enemies if e.health > 0])
                # If less than 50% of max enemies, respawn some
                if current_count < 20:  # Respawn when below 20 enemies
                    self.spawn_enemies()
                    self.add_chat_message("Enemies have respawned...", color.gray)
                self.enemy_respawn_timer = self.enemy_respawn_delay
    
    def spawn_enemies(self):
        """Spawn enemies OUTSIDE the village and in biome zones."""
        import random
        
        # ========== ERROR 404 MODE: ALL ENEMIES ARE BOSSES ==========
        if self.error404_mode:
            # ERROR biomes with "ERROR" prefix, only pink/black colors
            error_biomes = {
                'ERROR Inferno': (0, 0.75, 350),
                'ERROR Desert': (300, 0.75, 0),
                'ERROR Swamp': (0, 0.75, -350),
                'ERROR Hellscape': (-300, 0.75, 0),
                'ERROR Tundra': (-200, 0.75, 200),
                'ERROR Terror': (200, 0.75, 200),
            }
            
            # Spawn extreme difficulty bosses everywhere
            for biome_name, center_pos in error_biomes.items():
                # Spawn 5-8 bosses per biome
                boss_count = random.randint(5, 8)
                for i in range(boss_count):
                    # Random position near center
                    offset_x = random.uniform(-50, 50)
                    offset_z = random.uniform(-50, 50)
                    pos = (center_pos[0] + offset_x, center_pos[1], center_pos[2] + offset_z)
                    
                    # Alternate pink/black colors
                    boss_color = color.rgb(255, 0, 255) if i % 2 == 0 else color.black
                    
                    # Extreme stats
                    boss_hp = random.randint(5000, 10000)
                    boss_xp = boss_hp // 2
                    
                    boss = BossEnemy(f"{biome_name} BOSS", pos, boss_hp, boss_color, xp_value=boss_xp)
                    boss.target = self.player
                    boss.can_fireball = True
                    boss.can_magic = True
                    boss.can_poison = True
                    boss.projectile_scale = 4.0
                    boss.base_speed = 2.5
                    self.enemies.append(boss)
            
            # Spawn ERROR bosses around Error Village
            error_village_bosses = [
                ("ERROR GUARDIAN", (-450, 0.75, 550), 8000, color.rgb(255, 0, 255)),
                ("ERROR SENTINEL", (-550, 0.75, 450), 8000, color.black),
                ("ERROR DESTROYER", (-480, 0.75, 480), 10000, color.rgb(255, 100, 255)),
                ("ERROR ANNIHILATOR", (-520, 0.75, 520), 10000, color.rgb(200, 0, 200)),
            ]
            
            for name, pos, hp, col in error_village_bosses:
                boss = BossEnemy(name, pos, hp, col, xp_value=hp // 2)
                boss.target = self.player
                boss.can_magic = True
                boss.can_fireball = True
                boss.projectile_scale = 5.0
                boss.scale = (2.5, 2.5, 2.5)
                self.enemies.append(boss)
            
            return  # Don't spawn normal enemies
        
        # ========== DREAM MODE: Replace all enemies with dark variants ==========
        if self.dream_mode:
            # Create hidden portal in a hard-to-find location (far corner)
            portal_pos = (-180, 1, 195)  # Northwest, between biomes
            self.dream_portal = Entity(
                model='sphere',
                texture='white_cube',
                color=color.rgb(100, 0, 150),
                scale=(2, 3, 2),
                position=portal_pos,
                collider='box'
            )
            # Add eerie glow effect
            portal_glow = Entity(
                parent=self.dream_portal,
                model='sphere',
                color=color.rgb(150, 50, 200),
                scale=1.3,
                alpha=0.3
            )
            self.world_entities.append(self.dream_portal)
            self.world_entities.append(portal_glow)
            
            # Error404 Dungeon Portal - Glitched appearance (behind swamp house)
            error_portal_pos = (0, 1, -315)  # Behind purple witch's hut in Dark Swamp
            self.error404_portal = Entity(
                model='cube',
                texture='white_cube',
                color=color.rgb(255, 0, 255),  # Glitchy magenta
                scale=(2, 4, 0.5),
                position=error_portal_pos,
                collider='box',
                rotation=(0, 45, 0)
            )
            # Glitch effect layers
            for i in range(3):
                offset = (random.uniform(-0.2, 0.2), random.uniform(-0.2, 0.2), random.uniform(-0.2, 0.2))
                glitch_layer = Entity(
                    parent=self.error404_portal,
                    model='cube',
                    color=color.rgb(random.randint(0, 255), 0, random.randint(200, 255)),
                    scale=Vec3(1.1 + i * 0.1, 1.1 + i * 0.1, 1.1 + i * 0.1),
                    position=offset,
                    alpha=0.2
                )
                self.world_entities.append(glitch_layer)
            self.world_entities.append(self.error404_portal)
            
            # Spawn dark nightmare enemies with 2x XP
            dream_spawns = [
                # Shadow beasts
                ("Shadow Stalker", (60, 0.75, 60), 150, color.rgb(30, 0, 50), 200),
                ("Shadow Stalker", (70, 0.75, 55), 150, color.rgb(30, 0, 50), 200),
                ("Void Wraith", (-60, 0.75, -60), 120, color.rgb(50, 0, 80), 160),
                ("Void Wraith", (-70, 0.75, -55), 120, color.rgb(50, 0, 80), 160),
                ("Nightmare Horror", (-60, 0.75, 60), 180, color.rgb(100, 0, 100), 240),
                ("Nightmare Horror", (-70, 0.75, 55), 180, color.rgb(100, 0, 100), 240),
                ("Abyss Walker", (60, 0.75, -60), 200, color.rgb(20, 0, 40), 280),
                ("Abyss Walker", (70, 0.75, -55), 200, color.rgb(20, 0, 40), 280),
                # Phantom ranged enemies
                ("Phantom Archer", (65, 0.75, -70), 140, color.rgb(60, 0, 90), 180),
                ("Spectral Shooter", (-65, 0.75, 80), 130, color.rgb(70, 0, 100), 170),
            ]
            
            for name, pos, hp, col, xp in dream_spawns:
                if "Archer" in name or "Shooter" in name:
                    enemy = RangedEnemy(name, pos, hp, col, xp_value=xp, projectile_color=color.rgb(100, 0, 150))
                else:
                    enemy = Enemy(name, pos, hp, col, xp_value=xp)
                enemy.target = self.player
                self.enemies.append(enemy)
            
            # Dream mode bosses with 2x XP
            dream_bosses = [
                ("Terror Lord", (75, 0.75, 75), 800, color.rgb(150, 0, 150), 400),
                ("Nightmare King", (-75, 0.75, -75), 700, color.rgb(80, 0, 120), 360),
                ("Void Overlord", (-75, 0.75, 75), 900, color.rgb(50, 0, 100), 500),
                ("Shadow Tyrant", (75, 0.75, -75), 1000, color.rgb(30, 0, 60), 560),
            ]
            
            for name, pos, hp, col, xp in dream_bosses:
                boss = BossEnemy(name, pos, hp, col, xp_value=xp)
                boss.target = self.player
                self.enemies.append(boss)
            
            # ========== DREAM MODE BIOME BOSSES ==========
            # Volcanic Inferno Boss (North)
            volcanic_boss = BossEnemy("Inferno Overlord", (0, 0.75, 350), 3000, color.rgb(255, 50, 0), xp_value=1600)
            volcanic_boss.target = self.player
            volcanic_boss.can_fireball = True
            self.enemies.append(volcanic_boss)
            
            # Desert Boss
            desert_boss = BossEnemy("Sand Nightmare", (300, 0.75, 0), 3500, color.rgb(200, 150, 0), xp_value=1800)
            desert_boss.target = self.player
            self.enemies.append(desert_boss)
            
            # Swamp Boss
            swamp_boss = BossEnemy("Toxic Abomination", (0, 0.75, -350), 4000, color.rgb(100, 150, 0), xp_value=2000)
            swamp_boss.target = self.player
            swamp_boss.can_poison = True
            self.enemies.append(swamp_boss)
            
            # Volcanic Hellscape Boss (West)
            hellscape_boss = BossEnemy("Magma Demon Lord", (-300, 0.75, 0), 5000, color.rgb(255, 100, 0), xp_value=2500)
            hellscape_boss.target = self.player
            hellscape_boss.can_fireball = True
            hellscape_boss.can_magic = True
            self.enemies.append(hellscape_boss)
            
            # ========== TERROR LAND BOSS SPAWNS (Northeast) ==========
            terror_bosses = [
                ("Terror Guardian", (150, 0.75, 150), 2000, color.magenta),
                ("Nightmare Beast", (180, 0.75, 200), 2500, color.violet),
                ("Void Titan", (200, 0.75, 180), 3000, color.red),
                ("Shadow Colossus", (250, 0.75, 230), 3500, color.orange),
                ("Chaos Lord", (160, 0.75, 220), 2800, color.red),
                ("Dread Overlord", (220, 0.75, 160), 3200, color.orange),
                ("Annihilation Walker", (280, 0.75, 200), 4000, color.red),
                ("Oblivion Spawn", (200, 0.75, 280), 3800, color.orange),
                ("Doom Bringer", (240, 0.75, 280), 3600, color.violet),
                ("Apocalypse Fiend", (300, 0.75, 250), 5000, color.magenta),
            ]
            
            for name, pos, hp, col in terror_bosses:
                xp = hp // 2
                boss = BossEnemy(name, pos, hp, col, xp_value=xp)
                boss.target = self.player
                boss.base_speed = 1.5
                boss.can_magic = True
                boss.projectile_scale = 3.0
                self.enemies.append(boss)
            
            # Supreme Terror Lord
            supreme_boss = BossEnemy("Supreme Terror Lord", (300, 0.75, 300), 8000, color.red, xp_value=4000)
            supreme_boss.target = self.player
            supreme_boss.can_magic = True
            supreme_boss.can_fireball = True
            supreme_boss.can_poison = True
            supreme_boss.projectile_scale = 5.0
            supreme_boss.scale = (3, 3, 3)
            self.enemies.append(supreme_boss)
            
            # Don't spawn normal enemies in Dream Mode - only Dream enemies
            return
        
        # ========== NORMAL MODE ENEMIES ==========
        # ========== ORIGINAL AREA ENEMIES ==========
        spawns = [
            # Wolves (Northeast)
            ("Wolf", (60, 0.75, 60), 100, color.gray),
            ("Wolf", (70, 0.75, 55), 100, color.gray),
            ("Wolf", (65, 0.75, 70), 120, color.dark_gray),
            # Slimes (Southwest)
            ("Slime", (-60, 0.75, -60), 70, color.lime),
            ("Slime", (-70, 0.75, -55), 70, color.lime),
            ("Slime", (-65, 0.75, -70), 80, color.green),
            # Goblins (Northwest - melee only, archers separate)
            ("Goblin", (-60, 0.75, 60), 110, color.green),
            ("Goblin", (-70, 0.75, 55), 110, color.green),
            ("Goblin", (-65, 0.75, 70), 130, color.olive),
            # Skeletons (Southeast - melee only, archer separate)
            ("Skeleton", (60, 0.75, -60), 140, color.white),
            ("Skeleton", (70, 0.75, -55), 140, color.white),
        ]

        for name, pos, hp, col in spawns:
            enemy = Enemy(name, pos, hp, col)
            enemy.target = self.player
            self.enemies.append(enemy)

        # ========== STARTING AREA BOSSES ==========
        # Alpha Wolf Boss (Northeast)
        alpha_wolf = BossEnemy("Alpha Wolf", (75, 0.75, 75), 500, color.smoke, xp_value=200)
        alpha_wolf.target = self.player
        self.enemies.append(alpha_wolf)

        # King Slime Boss (Southwest)
        king_slime = BossEnemy("King Slime", (-75, 0.75, -75), 400, color.olive, xp_value=180)
        king_slime.target = self.player
        self.enemies.append(king_slime)

        # Goblin Warlord Boss (Northwest)
        goblin_boss = BossEnemy("Goblin Warlord", (-75, 0.75, 75), 600, color.orange, xp_value=250)
        goblin_boss.target = self.player
        self.enemies.append(goblin_boss)

        # Skeleton Lord Boss (Southeast)
        skeleton_boss = BossEnemy("Skeleton Lord", (75, 0.75, -75), 700, color.white, xp_value=280)
        skeleton_boss.target = self.player
        self.enemies.append(skeleton_boss)

        # ========== RANGED ENEMIES (fire projectiles) ==========
        ranged_spawns = [
            # Skeleton Archers
            ("Skeleton Archer", (65, 0.75, -70), 120, color.light_gray, color.white),
            ("Skeleton Archer", (80, 0.75, -65), 120, color.light_gray, color.white),
            # Goblin Archers
            ("Goblin Archer", (-65, 0.75, 80), 90, color.dark_gray, color.orange),
            ("Goblin Archer", (-80, 0.75, 65), 90, color.dark_gray, color.orange),
        ]

        for name, pos, hp, col, proj_col in ranged_spawns:
            enemy = RangedEnemy(name, pos, hp, col, xp_value=30, projectile_color=proj_col)
            enemy.target = self.player
            self.enemies.append(enemy)

        # ========== FROZEN TUNDRA ENEMIES (North z > 100) ==========
        tundra_spawns = [
            ("Frost Wolf", (50, 0.75, 150), 200, color.white),
            ("Frost Wolf", (-30, 0.75, 180), 200, color.white),
            ("Ice Golem", (0, 0.75, 200), 600, color.cyan),
            ("Ice Golem", (80, 0.75, 250), 600, color.cyan),
            ("Frost Giant", (-60, 0.75, 300), 800, color.azure),
            ("Snow Wraith", (100, 0.75, 180), 250, color.white),
            ("Snow Wraith", (-100, 0.75, 220), 250, color.white),
        ]

        for name, pos, hp, col in tundra_spawns:
            xp = hp // 4
            enemy = Enemy(name, pos, hp, col, xp_value=xp)
            enemy.target = self.player
            enemy.base_speed = 1.5 if 'Golem' in name else 2.5
            self.enemies.append(enemy)

        # Tundra ranged (Ice Mages)
        tundra_ranged = [
            ("Ice Mage", (30, 0.75, 170), 180, color.azure, color.cyan),
            ("Ice Mage", (-80, 0.75, 280), 180, color.azure, color.cyan),
        ]
        for name, pos, hp, col, proj_col in tundra_ranged:
            enemy = RangedEnemy(name, pos, hp, col, xp_value=60, projectile_color=proj_col)
            enemy.target = self.player
            self.enemies.append(enemy)

        # Tundra Boss
        frost_boss = BossEnemy("Frost King", (0, 0.75, 350), 2000, color.cyan, xp_value=800)
        frost_boss.target = self.player
        self.enemies.append(frost_boss)

        # ========== DESERT WASTELAND ENEMIES (East x > 100) ==========
        desert_spawns = [
            ("Sand Scorpion", (150, 0.75, 30), 180, color.yellow),
            ("Sand Scorpion", (180, 0.75, -50), 180, color.yellow),
            ("Sand Golem", (200, 0.75, 0), 550, color.gold),
            ("Sand Golem", (250, 0.75, 80), 550, color.gold),
            ("Mummy", (220, 0.75, -80), 350, color.white),
            ("Mummy", (280, 0.75, 50), 350, color.white),
            ("Desert Worm", (300, 0.75, -30), 700, color.brown),
        ]

        for name, pos, hp, col in desert_spawns:
            xp = hp // 4
            enemy = Enemy(name, pos, hp, col, xp_value=xp)
            enemy.target = self.player
            enemy.base_speed = 1.0 if 'Golem' in name or 'Worm' in name else 2.2
            self.enemies.append(enemy)

        # Desert ranged (Sand Archers)
        desert_ranged = [
            ("Desert Archer", (170, 0.75, 60), 150, color.yellow, color.orange),
            ("Desert Archer", (230, 0.75, -40), 150, color.yellow, color.orange),
        ]
        for name, pos, hp, col, proj_col in desert_ranged:
            enemy = RangedEnemy(name, pos, hp, col, xp_value=50, projectile_color=proj_col)
            enemy.target = self.player
            self.enemies.append(enemy)

        # Desert Boss
        pharaoh_boss = BossEnemy("Pharaoh Guardian", (300, 0.75, 0), 2500, color.gold, xp_value=1000)
        pharaoh_boss.target = self.player
        self.enemies.append(pharaoh_boss)

        # ========== DARK SWAMP ENEMIES (South z < -100) ==========
        swamp_spawns = [
            ("Swamp Creature", (30, 0.75, -150), 220, color.olive),
            ("Swamp Creature", (-50, 0.75, -180), 220, color.olive),
            ("Poison Toad", (0, 0.75, -200), 180, color.green),
            ("Poison Toad", (80, 0.75, -220), 180, color.green),
            ("Bog Golem", (-30, 0.75, -250), 500, color.brown),
            ("Bog Golem", (60, 0.75, -300), 500, color.brown),
            ("Swamp Witch", (-80, 0.75, -280), 300, color.violet),
        ]

        for name, pos, hp, col in swamp_spawns:
            xp = hp // 4
            enemy = Enemy(name, pos, hp, col, xp_value=xp)
            enemy.target = self.player
            enemy.base_speed = 1.2 if 'Golem' in name else 2.0
            self.enemies.append(enemy)

        # Swamp ranged (Witch shoots poison)
        swamp_ranged = [
            ("Swamp Witch", (50, 0.75, -170), 200, color.violet, color.green),
            ("Swamp Witch", (-60, 0.75, -320), 200, color.violet, color.green),
        ]
        for name, pos, hp, col, proj_col in swamp_ranged:
            enemy = RangedEnemy(name, pos, hp, col, xp_value=70, projectile_color=proj_col)
            enemy.target = self.player
            self.enemies.append(enemy)

        # Swamp Boss
        swamp_boss = BossEnemy("Swamp Hydra", (0, 0.75, -350), 3000, color.olive, xp_value=1200)
        swamp_boss.target = self.player
        self.enemies.append(swamp_boss)

        # ========== VOLCANIC HELLSCAPE ENEMIES (West x < -100) ==========
        volcanic_spawns = [
            ("Fire Imp", (-150, 0.75, 30), 150, color.orange),
            ("Fire Imp", (-180, 0.75, -40), 150, color.orange),
            ("Fire Imp", (-160, 0.75, 60), 150, color.orange),
            ("Lava Golem", (-200, 0.75, 0), 700, color.red),
            ("Lava Golem", (-250, 0.75, 70), 700, color.red),
            ("Magma Beast", (-220, 0.75, -60), 450, color.orange),
            ("Magma Beast", (-280, 0.75, 30), 450, color.orange),
            ("Fire Dragon", (-300, 0.75, -30), 1200, color.red),
        ]

        for name, pos, hp, col in volcanic_spawns:
            xp = hp // 3  # More XP in volcanic
            enemy = Enemy(name, pos, hp, col, xp_value=xp)
            enemy.target = self.player
            enemy.base_speed = 0.8 if 'Golem' in name else 3.0 if 'Imp' in name else 2.0
            self.enemies.append(enemy)

        # Volcanic ranged (Fire Mages)
        volcanic_ranged = [
            ("Fire Mage", (-170, 0.75, 50), 200, color.red, color.orange),
            ("Fire Mage", (-230, 0.75, -50), 200, color.red, color.orange),
            ("Flame Archer", (-260, 0.75, 80), 180, color.orange, color.red),
        ]
        for name, pos, hp, col, proj_col in volcanic_ranged:
            enemy = RangedEnemy(name, pos, hp, col, xp_value=80, projectile_color=proj_col)
            enemy.target = self.player
            self.enemies.append(enemy)

        # Volcanic Boss - Ancient Fire Dragon
        fire_boss = BossEnemy("Ancient Fire Dragon", (-300, 0.75, 0), 4000, color.red, xp_value=1500)
        fire_boss.target = self.player
        self.enemies.append(fire_boss)

        # ========== FANTASY LAND ENEMIES (Northeast x > 100, z > 100) ==========
        # In Dream Mode: TERROR LAND - All enemies are bosses that fire projectiles
        if self.dream_mode:
            # TERROR LAND: All boss-type enemies with projectiles - BRIGHT visible colors
            terror_bosses = [
                ("Terror Guardian", (150, 0.75, 150), 2000, color.magenta),
                ("Nightmare Beast", (180, 0.75, 200), 2500, color.violet),
                ("Void Titan", (200, 0.75, 180), 3000, color.red),
                ("Shadow Colossus", (250, 0.75, 230), 3500, color.orange),
                ("Chaos Lord", (160, 0.75, 220), 2800, color.red),
                ("Dread Overlord", (220, 0.75, 160), 3200, color.orange),
                ("Annihilation Walker", (280, 0.75, 200), 4000, color.red),
                ("Oblivion Spawn", (200, 0.75, 280), 3800, color.orange),
                ("Doom Bringer", (240, 0.75, 280), 3600, color.violet),
                ("Apocalypse Fiend", (300, 0.75, 250), 5000, color.magenta),
            ]
            
            for name, pos, hp, col in terror_bosses:
                xp = hp // 2  # Massive XP in Terror Land
                boss = BossEnemy(name, pos, hp, col, xp_value=xp)
                boss.target = self.player
                boss.base_speed = 1.5  # Slower but deadly
                # Enable magic attacks for all Terror Land bosses
                boss.can_magic = True
                boss.projectile_scale = 3.0  # 3x larger projectiles
                self.enemies.append(boss)
            
            # Supreme Terror Lord - Ultimate boss - GIANT and bright red
            supreme_boss = BossEnemy("Supreme Terror Lord", (300, 0.75, 300), 8000, color.red, xp_value=4000)
            supreme_boss.target = self.player
            supreme_boss.can_magic = True
            supreme_boss.can_fireball = True
            supreme_boss.can_poison = True
            supreme_boss.projectile_scale = 5.0  # 5x larger projectiles
            # Make Supreme boss GIANT
            supreme_boss.scale = (3, 3, 3)
            self.enemies.append(supreme_boss)
            
            # Fear Injector 1 - Blue final boss
            fear_injector1 = BossEnemy("fearinjector1", (320, 0.75, 280), 10000, color.blue, xp_value=5000)
            fear_injector1.target = self.player
            fear_injector1.can_terror_scream = True
            fear_injector1.can_iceball = True
            fear_injector1.can_magic = True
            fear_injector1.can_shadow_dash = True
            fear_injector1.can_shadow_bullet = True
            fear_injector1.projectile_scale = 4.0
            fear_injector1.scale = (2.5, 2.5, 2.5)
            self.enemies.append(fear_injector1)
            
            # Fear Injector 2 - Pink final boss
            fear_injector2 = BossEnemy("fearinjector2", (280, 0.75, 320), 10000, color.magenta, xp_value=5000)
            fear_injector2.target = self.player
            fear_injector2.can_terror_scream = True
            fear_injector2.can_poison = True
            fear_injector2.can_soul_drain = True
            fear_injector2.can_blood_rage = True
            fear_injector2.can_shadow_bullet = True
            fear_injector2.projectile_scale = 4.0
            fear_injector2.scale = (2.5, 2.5, 2.5)
            self.enemies.append(fear_injector2)
            
            # Link them as partners for avenge mechanic
            fear_injector1.partner_boss = fear_injector2
            fear_injector2.partner_boss = fear_injector1
            
        else:
            # Normal Fantasy Land
            fantasy_spawns = [
                ("Fairy Guardian", (150, 0.75, 150), 180, color.magenta),
                ("Fairy Guardian", (180, 0.75, 200), 180, color.magenta),
                ("Mushroom Golem", (200, 0.75, 180), 650, color.red),
                ("Mushroom Golem", (250, 0.75, 230), 650, color.red),
                ("Crystal Sprite", (160, 0.75, 220), 250, color.cyan),
                ("Crystal Sprite", (220, 0.75, 160), 250, color.cyan),
                ("Dream Walker", (280, 0.75, 200), 400, color.violet),
                ("Unicorn", (200, 0.75, 280), 500, color.white),
                ("Forest Spirit", (240, 0.75, 280), 350, color.lime),
                ("Ancient Treant", (300, 0.75, 250), 900, color.brown),
            ]

            for name, pos, hp, col in fantasy_spawns:
                xp = hp // 3  # Good XP in Fantasy Land
                enemy = Enemy(name, pos, hp, col, xp_value=xp)
                enemy.target = self.player
                enemy.base_speed = 0.6 if 'Golem' in name or 'Treant' in name else 2.5 if 'Sprite' in name else 2.0
                self.enemies.append(enemy)

            # Fantasy ranged (Magic casters)
            fantasy_ranged = [
                ("Pixie Mage", (170, 0.75, 180), 160, color.pink, color.magenta),
                ("Pixie Mage", (230, 0.75, 220), 160, color.pink, color.magenta),
                ("Moon Witch", (260, 0.75, 150), 280, color.violet, color.white),
                ("Starlight Archer", (190, 0.75, 260), 220, color.gold, color.yellow),
            ]
            for name, pos, hp, col, proj_col in fantasy_ranged:
                enemy = RangedEnemy(name, pos, hp, col, xp_value=90, projectile_color=proj_col)
                enemy.target = self.player
                self.enemies.append(enemy)

            # Fantasy Land Boss - The Fairy Queen
            fairy_boss = BossEnemy("Fairy Queen", (300, 0.75, 300), 3500, color.magenta, xp_value=1400)
            fairy_boss.target = self.player
            self.enemies.append(fairy_boss)

    def create_hud(self):
        """Create the in-game HUD."""
        race_name = config.RACES[self.character.race]['name']
        class_name = config.CLASSES[self.character.char_class]['name']

        self.hud_name = Text(
            text=f'{self.username} - Lv.{self.character.level} {race_name} {class_name}',
            position=(-0.85, 0.47),
            scale=1.2,
            color=color.cyan
        )

        # Health bar - bg has higher z (back), bar has lower z (front)
        self.hp_label = Text(text='HP', position=(-0.85, 0.42), scale=1.2, color=color.white)
        self.health_bar_bg = Entity(parent=camera.ui, model='quad', texture='white_cube',
                                     color=color.dark_gray, scale=(0.4, 0.025), position=(-0.82, 0.42, 0.01), origin=(-0.5, 0))
        self.health_bar = Entity(parent=camera.ui, model='quad', texture='white_cube',
                                  color=color.red, scale=(0.4, 0.025), position=(-0.82, 0.42, 0), origin=(-0.5, 0))
        self.hp_text = Text(text=f'{int(self.character.health)}/{int(self.character.max_health)}',
                            position=(-0.62, 0.42), origin=(0, 0), scale=0.8, color=color.white)

        # Mana bar - bg has higher z (back), bar has lower z (front)
        self.mp_label = Text(text='MP', position=(-0.85, 0.38), scale=1.2, color=color.white)
        self.mana_bar_bg = Entity(parent=camera.ui, model='quad', texture='white_cube',
                                   color=color.dark_gray, scale=(0.4, 0.02), position=(-0.82, 0.38, 0.01), origin=(-0.5, 0))
        self.mana_bar = Entity(parent=camera.ui, model='quad', texture='white_cube',
                                color=color.blue, scale=(0.4, 0.02), position=(-0.82, 0.38, 0), origin=(-0.5, 0))
        self.mp_text = Text(text=f'{int(self.character.mana)}/{int(self.character.max_mana)}',
                            position=(-0.62, 0.38), origin=(0, 0), scale=0.7, color=color.white)

        # XP bar - bg has higher z (back), bar has lower z (front)
        self.xp_label = Text(text='XP', position=(-0.85, 0.34), scale=1, color=color.yellow)
        self.xp_bar_bg = Entity(parent=camera.ui, model='quad', texture='white_cube',
                                 color=color.dark_gray, scale=(0.4, 0.015), position=(-0.82, 0.34, 0.01), origin=(-0.5, 0))
        self.xp_bar = Entity(parent=camera.ui, model='quad', texture='white_cube',
                              color=color.yellow, scale=(0.4, 0.015), position=(-0.82, 0.34, 0), origin=(-0.5, 0))

        # Hotbar
        self.hotbar_slots = []
        self.hotbar_slot_bgs = []
        self.hotbar_icons = []  # Icons for items in hotbar
        hotbar_start_x = -0.28

        for i in range(8):
            slot_border = Entity(parent=camera.ui, model='quad', texture='white_cube',
                                  color=color.yellow if i == self.selected_hotbar else color.dark_gray,
                                  scale=(0.075, 0.075), position=(hotbar_start_x + i * 0.08, -0.40), z=0.02)
            self.hotbar_slot_bgs.append(slot_border)

            slot_bg = Entity(parent=camera.ui, model='quad', texture='white_cube',
                              color=color.smoke, scale=(0.07, 0.07), position=(hotbar_start_x + i * 0.08, -0.40), z=0.01)
            self.hotbar_slots.append(slot_bg)

            Text(text=str(i + 1), position=(hotbar_start_x + i * 0.08 - 0.025, -0.365), scale=0.6, color=color.gray)

            # Create initial hotbar icons
            item_idx = self.hotbar[i]
            slot_x = hotbar_start_x + i * 0.08
            slot_y = -0.40
            if item_idx is not None and item_idx < len(self.inventory) and self.inventory[item_idx]:
                item = self.inventory[item_idx]
                icons = self.create_hotbar_icon(item, slot_x, slot_y, 0.065)
                self.hotbar_icons.append(icons)
            else:
                self.hotbar_icons.append([])

        # Instructions
        self.instructions = Text(
            text='WASD: Move | SPACE: Jump | Click: Attack | E: Interact | I: Inventory | 1-8: Hotbar',
            position=(0, -0.47), origin=(0, 0), scale=0.7, color=color.light_gray
        )

        # Area indicator
        self.area_text = Text(text='Village', position=(0, 0.45), origin=(0, 0), scale=1.2, color=color.yellow)

        # Update function
        def update_game():
            if self.game_active and self.character:
                self.character.regenerate(time.dt)

                health_ratio = max(0, min(1, self.character.health / self.character.max_health))
                self.health_bar.scale_x = 0.4 * health_ratio
                self.hp_text.text = f'{int(self.character.health)}/{int(self.character.max_health)}'

                mana_ratio = max(0, min(1, self.character.mana / self.character.max_mana))
                self.mana_bar.scale_x = 0.4 * mana_ratio
                self.mp_text.text = f'{int(self.character.mana)}/{int(self.character.max_mana)}'

                xp_ratio = max(0, min(1, self.character.experience / self.character.exp_to_next_level))
                self.xp_bar.scale_x = 0.4 * xp_ratio

                race_name = config.RACES[self.character.race]['name']
                class_name = config.CLASSES[self.character.char_class]['name']
                self.hud_name.text = f'{self.username} - Lv.{self.character.level} {race_name} {class_name}'

                if self.teach_active:
                    self.update_teach_minigame()

                # Check portal collision
                self.check_portal_interaction()

                # Update area text based on position
                if self.player:
                    px, pz = self.player.x, self.player.z
                    # Check biome zones first (larger areas)
                    if px > 100 and pz > 100:
                        self.area_text.text = 'Terror Land' if self.dream_mode else 'Fantasy Land'
                    elif pz > 100:
                        self.area_text.text = 'Volcanic Inferno' if self.dream_mode else 'Frozen Tundra'
                    elif pz < -100:
                        self.area_text.text = 'Dark Swamp'
                    elif px > 100:
                        self.area_text.text = 'Desert Wasteland'
                    elif px < -100:
                        self.area_text.text = 'Volcanic Hellscape'
                    # Check local areas
                    elif abs(px) < 35 and abs(pz) < 35:
                        self.area_text.text = 'Village'
                    elif px > 40 and pz > 40:
                        self.area_text.text = 'Wolf Den'
                    elif px < -40 and pz < -40:
                        self.area_text.text = 'Slime Swamp'
                    elif px < -40 and pz > 40:
                        self.area_text.text = 'Goblin Camp'
                    elif px > 40 and pz < -40:
                        self.area_text.text = 'Skeleton Ruins'
                    else:
                        self.area_text.text = 'Wilderness'

                # Fade old chat messages
                for msg in self.chat_messages[:]:
                    if time.time() - msg['time'] > 15:
                        self.chat_messages.remove(msg)
                        self.update_chat_display()

        Entity(update=update_game)

    def update_hotbar_selection(self):
        """Update hotbar visual selection."""
        for i, border in enumerate(self.hotbar_slot_bgs):
            border.color = color.yellow if i == self.selected_hotbar else color.dark_gray

    def use_hotbar_item(self, slot):
        """Use item in hotbar slot."""
        if slot >= len(self.hotbar):
            return

        item_idx = self.hotbar[slot]
        if item_idx is None or item_idx >= len(self.inventory):
            return

        item = self.inventory[item_idx]
        if not item:
            return

        if item['type'] == 'weapon':
            # Equip weapon
            self.equipped_weapon = item
            self.create_weapon_visual()
            weapon_type = item.get('weapon_type', 'weapon')
            extra_info = ""
            if weapon_type == 'bow':
                extra_info = f" Range: {item.get('range', 15)}"
            elif weapon_type == 'staff':
                extra_info = f" Mana+{item.get('mana_bonus', 0)}"
            elif weapon_type == 'healing_staff':
                extra_info = f" Heal: {item.get('heal_power', 0)}"

            # Apply special metal bonuses
            bonus_info = ""
            if item.get('health_bonus', 0) > 0:
                health_boost = item['health_bonus']
                self.character.max_health += health_boost
                self.character.health += health_boost
                bonus_info += f" +{health_boost} HP"
            if item.get('speed_bonus', 0) > 0:
                speed_boost = item['speed_bonus'] / 100  # Convert to speed multiplier
                self.player.speed += speed_boost
                bonus_info += f" +{item['speed_bonus']}% Speed"
            if item.get('attack_speed_mult', 1.0) > 1.0:
                bonus_info += f" {item['attack_speed_mult']}x Attack Speed"
            if item.get('poison_damage', 0) > 0:
                bonus_info += f" +{item['poison_damage']} Poison/sec"
            if item.get('slow_percent', 0) > 0:
                bonus_info += f" {item['slow_percent']}% Slow"
            if item.get('weaken_percent', 0) > 0:
                bonus_info += f" {item['weaken_percent']}% Weaken"
            if item.get('curse_percent', 0) > 0:
                bonus_info += f" {item['curse_percent']}% Curse"

            self.add_chat_message(f"Equipped: {item['name']} (DMG: {item.get('damage', 0)}{extra_info}{bonus_info})", color.yellow)

        elif item['type'] == 'armor':
            # Equip armor
            slot = item.get('slot')
            if slot and slot in self.equipped_armor:
                old_armor = self.equipped_armor[slot]
                self.equipped_armor[slot] = item
                defense = item.get('defense', 0)
                self.add_chat_message(f"Equipped: {item['name']} (DEF: {defense}) [{slot}]", color.azure)
                # Calculate total defense
                total_def = self.get_total_defense()
                self.add_chat_message(f"Total Defense: {total_def}", color.gray)

        elif item['type'] == 'consumable':
            if 'heal' in item:
                self.character.heal(item['heal'])
                self.add_chat_message(f"Used {item['name']}! +{item['heal']} HP", color.green)
            if 'mana' in item:
                self.character.mana = min(self.character.max_mana, self.character.mana + item['mana'])
                self.add_chat_message(f"Used {item['name']}! +{item['mana']} MP", color.azure)
            if 'stamina' in item:
                self.character.stamina = min(self.character.max_stamina, self.character.stamina + item['stamina'])
                self.add_chat_message(f"Used {item['name']}! +{item['stamina']} Stamina", color.green)
            self.inventory[item_idx] = None
            self.update_hotbar_display()

        elif item['type'] == 'spell':
            # Use spell scroll
            mana_cost = item.get('mana_cost', 10)
            if self.character.use_mana(mana_cost):
                self.add_chat_message(f"Cast {item['name']}! (DMG: {item.get('damage', 0)})", color.magenta)
                # Deal damage to nearby enemies
                for enemy in self.enemies[:]:
                    if enemy.health <= 0:
                        continue
                    if distance(self.player, enemy) < 8:
                        # Save enemy data before take_damage (which can destroy it)
                        enemy_name = enemy.enemy_name
                        enemy_pos = Vec3(enemy.position)
                        enemy_xp = enemy.xp_value
                        
                        enemy.take_damage(item.get('damage', 20))
                        if enemy.health <= 0:
                            self.character.gain_experience(enemy_xp)
                            self.drop_enemy_loot(enemy_name, enemy_pos)
                            if enemy in self.enemies:
                                self.enemies.remove(enemy)
                            self.add_chat_message(f"{enemy_name} defeated! +{enemy_xp} XP", color.yellow)
                        break
                # Consume scroll
                self.inventory[item_idx] = None
                self.update_hotbar_display()
            else:
                self.add_chat_message("Not enough mana!", color.red)

    def open_pet_book(self):
        """Open the pet selection book."""
        if self.pet:
            self.add_chat_message("You already have a pet!", color.red)
            return

        self.pet_book_open = True
        mouse.locked = False

        # Dark background
        bg = Entity(parent=camera.ui, model='quad', texture='white_cube',
                    color=color.black90, scale=(0.8, 0.6), position=(0, 0), z=0.1)
        self.pet_book_ui.append(bg)

        # Border
        border = Entity(parent=camera.ui, model='quad', texture='white_cube',
                        color=color.magenta, scale=(0.82, 0.62), position=(0, 0), z=0.2)
        self.pet_book_ui.append(border)

        title = Text(text='~ Choose Your Starter Pet ~', position=(0, 0.22), origin=(0, 0),
                     scale=2, color=color.magenta)
        self.pet_book_ui.append(title)

        for i, pet_name in enumerate(self.available_pets):
            pet_text = Text(text=f'{">" if i == self.pet_book_selection else " "} {pet_name}',
                            position=(0, 0.1 - i * 0.08), origin=(0, 0), scale=1.5,
                            color=color.yellow if i == self.pet_book_selection else color.white)
            self.pet_book_ui.append(pet_text)

        # Confirm button
        confirm_btn = Button(
            text='CONFIRM',
            scale=(0.2, 0.06),
            position=(0, -0.18),
            color=color.green,
            highlight_color=color.lime,
            text_color=color.white,
            on_click=self.select_pet
        )
        self.pet_book_ui.append(confirm_btn)

        inst = Text(text='[Left Click] to cycle pets | [ESC] to close',
                    position=(0, -0.26), origin=(0, 0), scale=1, color=color.light_gray)
        self.pet_book_ui.append(inst)

    def update_pet_book_display(self):
        self.close_pet_book()
        self.open_pet_book()

    def select_pet(self):
        if self.pet_book_selection < len(self.available_pets):
            pet_type = self.available_pets[self.pet_book_selection]
            self.pet = Pet(pet_type, self.player)
            self.add_chat_message(f"You chose {pet_type} as your companion!", color.lime)
            self.update_pet_ui()
            self.close_pet_book()

    def close_pet_book(self):
        self.pet_book_open = False
        mouse.locked = True
        for ui in self.pet_book_ui:
            destroy(ui)
        self.pet_book_ui = []

    def show_trainer_menu(self):
        if not self.pet:
            self.show_dialogue('Pet Trainer', [
                "You don't have a pet yet!",
                "Go use the Pet Book in the village center to choose one."
            ])
            return

        self.training_active = True
        self.training_npc = 'trainer'
        mouse.locked = False

        bg = Entity(parent=camera.ui, model='quad', texture='white_cube',
                    color=color.black90, scale=(0.6, 0.4), position=(0, 0), z=0.1)
        self.training_ui.append(bg)

        title = Text(text=f'Train {self.pet.pet_type}', position=(0, 0.15), origin=(0, 0),
                     scale=1.8, color=color.lime)
        self.training_ui.append(title)

        train_btn = Text(text='[1] TRAIN - Perform action to teach', position=(0, 0.05),
                         origin=(0, 0), scale=1.2, color=color.yellow)
        self.training_ui.append(train_btn)

        teach_btn = Text(text='[2] TEACH - Timing minigame', position=(0, -0.03),
                         origin=(0, 0), scale=1.2, color=color.cyan)
        self.training_ui.append(teach_btn)

        close_btn = Text(text='[ESC] Close', position=(0, -0.15), origin=(0, 0),
                         scale=1, color=color.light_gray)
        self.training_ui.append(close_btn)

    def close_trainer_menu(self):
        self.training_active = False
        self.training_npc = None
        mouse.locked = True
        for ui in self.training_ui:
            destroy(ui)
        self.training_ui = []

    def start_train_mode(self):
        self.close_trainer_menu()
        self.training_skill = 'pending'

        self.train_instruction = Text(
            text='TRAINING: Attack an enemy to teach "Attack"!\nJump to teach "Dodge"! Press ESC to cancel.',
            position=(0, 0.3), origin=(0, 0), scale=1.2, color=color.lime, background=True
        )

    def complete_training(self, skill_name):
        if self.pet and self.training_skill == 'pending':
            if self.pet.learn_skill(skill_name):
                self.add_chat_message(f"{self.pet.pet_type} learned {skill_name}!", color.lime)
                self.update_pet_ui()
            else:
                self.add_chat_message(f"{self.pet.pet_type} already knows this!", color.orange)
            self.training_skill = None
            if hasattr(self, 'train_instruction'):
                destroy(self.train_instruction)

    def start_teach_minigame(self):
        self.close_trainer_menu()
        self.teach_active = True
        self.teach_bar_pos = 0
        self.teach_bar_direction = 1
        self.teach_target_zone = random.uniform(0.3, 0.7)
        self.teach_skill = 'Power Strike'
        mouse.locked = False

        bg = Entity(parent=camera.ui, model='quad', texture='white_cube',
                    color=color.black90, scale=(0.8, 0.3), position=(0, 0), z=0.1)
        self.teach_ui.append(bg)

        title = Text(text=f'TEACH: {self.teach_skill}', position=(0, 0.1), origin=(0, 0),
                     scale=1.5, color=color.cyan)
        self.teach_ui.append(title)

        inst = Text(text='Press SPACE when the bar is in the green zone!', position=(0, 0.05),
                    origin=(0, 0), scale=1, color=color.white)
        self.teach_ui.append(inst)

        bar_bg = Entity(parent=camera.ui, model='quad', texture='white_cube',
                        color=color.dark_gray, scale=(0.6, 0.04), position=(0, -0.02))
        self.teach_ui.append(bar_bg)

        zone_width = 0.1
        zone_x = -0.3 + self.teach_target_zone * 0.6
        self.teach_zone = Entity(parent=camera.ui, model='quad', texture='white_cube',
                                  color=color.lime, scale=(zone_width, 0.04), position=(zone_x, -0.02))
        self.teach_ui.append(self.teach_zone)

        self.teach_indicator = Entity(parent=camera.ui, model='quad', texture='white_cube',
                                       color=color.white, scale=(0.02, 0.06), position=(-0.3, -0.02))
        self.teach_ui.append(self.teach_indicator)

    def update_teach_minigame(self):
        if not self.teach_active:
            return

        speed = 1.5
        self.teach_bar_pos += self.teach_bar_direction * speed * time.dt

        if self.teach_bar_pos >= 1:
            self.teach_bar_pos = 1
            self.teach_bar_direction = -1
        elif self.teach_bar_pos <= 0:
            self.teach_bar_pos = 0
            self.teach_bar_direction = 1

        self.teach_indicator.x = -0.3 + self.teach_bar_pos * 0.6

    def check_teach_timing(self):
        if not self.teach_active:
            return

        zone_start = self.teach_target_zone - 0.08
        zone_end = self.teach_target_zone + 0.08

        if zone_start <= self.teach_bar_pos <= zone_end:
            if self.pet:
                if self.pet.learn_skill(self.teach_skill):
                    self.add_chat_message(f"Perfect! {self.pet.pet_type} learned {self.teach_skill}!", color.lime)
                    self.update_pet_ui()
                else:
                    self.add_chat_message(f"{self.pet.pet_type} already knows this!", color.orange)
        else:
            self.add_chat_message("Missed! Try again.", color.red)

        self.close_teach_minigame()

    def close_teach_minigame(self):
        self.teach_active = False
        self.teach_skill = None
        mouse.locked = True
        for ui in self.teach_ui:
            destroy(ui)
        self.teach_ui = []

    def toggle_inventory(self):
        if self.inventory_open:
            self.close_inventory()
        else:
            self.open_inventory()

    def open_inventory(self):
        self.inventory_open = True
        self.dragging_item = None
        self.dragging_from = None
        mouse.locked = False

        # Background
        bg = Entity(parent=camera.ui, model='quad', texture='white_cube',
                    color=color.black90, scale=(0.9, 0.8), position=(0, 0.05), z=0.1)
        self.inventory_ui.append(bg)

        # Border
        border = Entity(parent=camera.ui, model='quad', texture='white_cube',
                        color=color.gray, scale=(0.92, 0.82), position=(0, 0.05), z=0.2)
        self.inventory_ui.append(border)

        title = Text(text='INVENTORY', position=(0, 0.38), origin=(0, 0), scale=2, color=color.white)
        self.inventory_ui.append(title)

        # Inventory grid
        slot_size = 0.09
        start_x = -0.22
        start_y = 0.25
        self.inv_slots = []

        for row in range(4):
            for col in range(4):
                idx = row * 4 + col
                slot_x = start_x + col * (slot_size + 0.025)
                slot_y = start_y - row * (slot_size + 0.025)

                # Slot button (clickable)
                slot_btn = Button(
                    scale=(slot_size, slot_size),
                    position=(slot_x, slot_y),
                    color=color.dark_gray,
                    highlight_color=color.gray,
                    on_click=Func(self.click_inventory_slot, idx)
                )
                self.inventory_ui.append(slot_btn)
                self.inv_slots.append({'btn': slot_btn, 'idx': idx, 'pos': (slot_x, slot_y)})

                if idx < len(self.inventory) and self.inventory[idx]:
                    item = self.inventory[idx]
                    self.create_item_icon(item, slot_x, slot_y, slot_size)

        # Hotbar section label
        hotbar_label = Text(text='HOTBAR (Click inventory item, then hotbar slot)',
                            position=(0, -0.18), origin=(0, 0), scale=0.9, color=color.yellow)
        self.inventory_ui.append(hotbar_label)

        # Hotbar slots in inventory view
        hotbar_start_x = -0.21
        hotbar_y = -0.28
        self.hotbar_inv_slots = []

        for i in range(8):
            hb_x = hotbar_start_x + i * (slot_size + 0.015)

            # Hotbar slot button
            hb_btn = Button(
                scale=(slot_size, slot_size),
                position=(hb_x, hotbar_y),
                color=color.olive if self.hotbar[i] is not None else color.dark_gray,
                highlight_color=color.yellow,
                on_click=Func(self.click_hotbar_slot, i)
            )
            self.inventory_ui.append(hb_btn)
            self.hotbar_inv_slots.append({'btn': hb_btn, 'idx': i, 'pos': (hb_x, hotbar_y)})

            # Hotbar number
            num_text = Text(text=str(i + 1), position=(hb_x, hotbar_y + slot_size/2 + 0.015),
                            origin=(0, 0), scale=0.7, color=color.white)
            self.inventory_ui.append(num_text)

            # Show item in hotbar slot
            item_idx = self.hotbar[i]
            if item_idx is not None and item_idx < len(self.inventory) and self.inventory[item_idx]:
                item = self.inventory[item_idx]
                self.create_item_icon(item, hb_x, hotbar_y, slot_size * 0.9)

        # Garbage slot (trash can)
        garbage_x = 0.35
        garbage_y = -0.28
        garbage_btn = Button(
            scale=(slot_size * 1.2, slot_size * 1.2),
            position=(garbage_x, garbage_y),
            color=color.rgb(150, 50, 50),
            highlight_color=color.red,
            on_click=Func(self.delete_selected_item)
        )
        self.inventory_ui.append(garbage_btn)
        
        # Trash icon text
        trash_icon = Text(text='🗑', position=(garbage_x, garbage_y), origin=(0, 0),
                         scale=3, color=color.white)
        self.inventory_ui.append(trash_icon)
        
        trash_label = Text(text='DELETE', position=(garbage_x, garbage_y - 0.07), origin=(0, 0),
                          scale=0.7, color=color.red)
        self.inventory_ui.append(trash_label)

        # Instructions
        close_text = Text(text='[I] Close | Click item then hotbar/trash to assign/delete',
                          position=(0, -0.38), origin=(0, 0), scale=0.9, color=color.light_gray)
        self.inventory_ui.append(close_text)

        # Selected item display
        self.selected_item_text = Text(text='', position=(0.25, 0.25), origin=(0, 0),
                                        scale=0.9, color=color.white)
        self.inventory_ui.append(self.selected_item_text)

    def create_item_icon(self, item, x, y, size):
        """Create a visual icon for an item."""
        item_type = item.get('type', 'misc')
        item_color = item.get('color', color.white)
        rarity = item.get('rarity', 'common')
        rarity_color = Item.RARITY_COLORS.get(rarity, color.white)
        weapon_type = item.get('weapon_type', None)

        # Rarity border
        rarity_border = Entity(parent=camera.ui, model='quad', texture='white_cube',
                               color=rarity_color, scale=(size * 0.95, size * 0.95),
                               position=(x, y), z=-0.01)
        self.inventory_ui.append(rarity_border)

        # Item background
        item_bg = Entity(parent=camera.ui, model='quad', texture='white_cube',
                         color=color.black66, scale=(size * 0.85, size * 0.85),
                         position=(x, y), z=-0.02)
        self.inventory_ui.append(item_bg)

        # Item icon based on type
        icon_size = size * 0.6

        if item_type == 'weapon':
            if weapon_type == 'sword':
                # Sword icon - vertical blade
                e1 = Entity(parent=camera.ui, model='quad', texture='white_cube',
                       color=item_color, scale=(icon_size * 0.2, icon_size * 0.9),
                       position=(x, y + icon_size * 0.1), z=-0.03)
                self.inventory_ui.append(e1)
                # Crossguard
                e2 = Entity(parent=camera.ui, model='quad', texture='white_cube',
                       color=color.brown, scale=(icon_size * 0.5, icon_size * 0.15),
                       position=(x, y - icon_size * 0.25), z=-0.04)
                self.inventory_ui.append(e2)
            elif weapon_type == 'dagger':
                e1 = Entity(parent=camera.ui, model='quad', texture='white_cube',
                       color=item_color, scale=(icon_size * 0.15, icon_size * 0.5),
                       position=(x, y + icon_size * 0.1), z=-0.03)
                self.inventory_ui.append(e1)
                e2 = Entity(parent=camera.ui, model='quad', texture='white_cube',
                       color=color.brown, scale=(icon_size * 0.3, icon_size * 0.15),
                       position=(x, y - icon_size * 0.2), z=-0.04)
                self.inventory_ui.append(e2)
            elif weapon_type == 'staff':
                e1 = Entity(parent=camera.ui, model='quad', texture='white_cube',
                       color=color.brown, scale=(icon_size * 0.12, icon_size * 0.8),
                       position=(x, y), z=-0.03)
                self.inventory_ui.append(e1)
                e2 = Entity(parent=camera.ui, model='quad', texture='white_cube',
                       color=item_color, scale=(icon_size * 0.3, icon_size * 0.3),
                       position=(x, y + icon_size * 0.35), z=-0.04)
                self.inventory_ui.append(e2)
            elif weapon_type == 'healing_staff':
                e1 = Entity(parent=camera.ui, model='quad', texture='white_cube',
                       color=color.white, scale=(icon_size * 0.1, icon_size * 0.7),
                       position=(x, y), z=-0.03)
                self.inventory_ui.append(e1)
                e2 = Entity(parent=camera.ui, model='quad', texture='white_cube',
                       color=color.lime, scale=(icon_size * 0.25, icon_size * 0.25),
                       position=(x, y + icon_size * 0.3), z=-0.04)
                self.inventory_ui.append(e2)
            elif weapon_type == 'bow':
                e1 = Entity(parent=camera.ui, model='quad', texture='white_cube',
                       color=item_color, scale=(icon_size * 0.1, icon_size * 0.7),
                       position=(x - icon_size * 0.1, y), z=-0.03)
                self.inventory_ui.append(e1)
                e2 = Entity(parent=camera.ui, model='quad', texture='white_cube',
                       color=color.white, scale=(icon_size * 0.03, icon_size * 0.6),
                       position=(x + icon_size * 0.05, y), z=-0.03)
                self.inventory_ui.append(e2)
                e3 = Entity(parent=camera.ui, model='quad', texture='white_cube',
                       color=color.brown, scale=(icon_size * 0.05, icon_size * 0.5),
                       position=(x, y), z=-0.04)
                self.inventory_ui.append(e3)
            else:
                e1 = Entity(parent=camera.ui, model='quad', texture='white_cube',
                       color=item_color, scale=(icon_size * 0.3, icon_size * 0.7),
                       position=(x, y), z=-0.03)
                self.inventory_ui.append(e1)

        elif item_type == 'armor':
            slot = item.get('slot', 'chest')
            if slot == 'chest':
                e1 = Entity(parent=camera.ui, model='quad', texture='white_cube',
                       color=item_color, scale=(icon_size * 0.6, icon_size * 0.7),
                       position=(x, y), z=-0.03)
                self.inventory_ui.append(e1)
            elif slot == 'head':
                e1 = Entity(parent=camera.ui, model='quad', texture='white_cube',
                       color=item_color, scale=(icon_size * 0.5, icon_size * 0.5),
                       position=(x, y + icon_size * 0.1), z=-0.03)
                self.inventory_ui.append(e1)
            elif slot == 'off_hand':
                e1 = Entity(parent=camera.ui, model='quad', texture='white_cube',
                       color=item_color, scale=(icon_size * 0.5, icon_size * 0.6),
                       position=(x, y), z=-0.03)
                self.inventory_ui.append(e1)
                e2 = Entity(parent=camera.ui, model='quad', texture='white_cube',
                       color=color.gold, scale=(icon_size * 0.15, icon_size * 0.15),
                       position=(x, y), z=-0.04)
                self.inventory_ui.append(e2)

        elif item_type == 'consumable':
            e1 = Entity(parent=camera.ui, model='quad', texture='white_cube',
                   color=item_color, scale=(icon_size * 0.35, icon_size * 0.5),
                   position=(x, y - icon_size * 0.1), z=-0.03)
            self.inventory_ui.append(e1)
            e2 = Entity(parent=camera.ui, model='quad', texture='white_cube',
                   color=color.light_gray, scale=(icon_size * 0.15, icon_size * 0.2),
                   position=(x, y + icon_size * 0.25), z=-0.03)
            self.inventory_ui.append(e2)

        elif item_type == 'spell':
            e1 = Entity(parent=camera.ui, model='quad', texture='white_cube',
                   color=color.white, scale=(icon_size * 0.5, icon_size * 0.6),
                   position=(x, y), z=-0.03)
            self.inventory_ui.append(e1)
            e2 = Entity(parent=camera.ui, model='quad', texture='white_cube',
                   color=item_color, scale=(icon_size * 0.3, icon_size * 0.3),
                   position=(x, y), z=-0.04)
            self.inventory_ui.append(e2)

        elif item_type == 'ammo':
            e1 = Entity(parent=camera.ui, model='quad', texture='white_cube',
                   color=color.brown, scale=(icon_size * 0.1, icon_size * 0.6),
                   position=(x, y), z=-0.03)
            self.inventory_ui.append(e1)
            e2 = Entity(parent=camera.ui, model='quad', texture='white_cube',
                   color=color.gray, scale=(icon_size * 0.15, icon_size * 0.15),
                   position=(x, y + icon_size * 0.25), z=-0.04)
            self.inventory_ui.append(e2)

        else:
            e1 = Entity(parent=camera.ui, model='quad', texture='white_cube',
                   color=item_color, scale=(icon_size * 0.5, icon_size * 0.5),
                   position=(x, y), z=-0.03)
            self.inventory_ui.append(e1)

        # Item name (short)
        name_text = Text(text=item['name'][:5], position=(x, y - size * 0.35),
                         origin=(0, 0), scale=0.55, color=color.white)
        self.inventory_ui.append(name_text)

    def create_hotbar_icon(self, item, x, y, size):
        """Create a visual icon for an item in the main HUD hotbar."""
        icons = []  # Keep track of all entities for this icon
        item_type = item.get('type', 'misc')
        item_color = item.get('color', color.white)
        rarity = item.get('rarity', 'common')
        rarity_color = Item.RARITY_COLORS.get(rarity, color.white)
        weapon_type = item.get('weapon_type', None)

        # Rarity border (thin) - negative z = in front
        rarity_border = Entity(parent=camera.ui, model='quad', texture='white_cube',
                               color=rarity_color, scale=(size * 0.95, size * 0.95),
                               position=(x, y), z=-0.01)
        icons.append(rarity_border)

        # Item background
        item_bg = Entity(parent=camera.ui, model='quad', texture='white_cube',
                         color=color.black66, scale=(size * 0.85, size * 0.85),
                         position=(x, y), z=-0.02)
        icons.append(item_bg)

        # Item icon based on type
        icon_size = size * 0.6

        if item_type == 'weapon':
            if weapon_type == 'sword':
                e1 = Entity(parent=camera.ui, model='quad', texture='white_cube',
                           color=item_color, scale=(icon_size * 0.2, icon_size * 0.9),
                           position=(x, y + icon_size * 0.1), z=-0.03)
                e2 = Entity(parent=camera.ui, model='quad', texture='white_cube',
                           color=color.brown, scale=(icon_size * 0.5, icon_size * 0.15),
                           position=(x, y - icon_size * 0.25), z=-0.04)
                icons.extend([e1, e2])
            elif weapon_type == 'dagger':
                e1 = Entity(parent=camera.ui, model='quad', texture='white_cube',
                           color=item_color, scale=(icon_size * 0.15, icon_size * 0.5),
                           position=(x, y + icon_size * 0.1), z=-0.03)
                e2 = Entity(parent=camera.ui, model='quad', texture='white_cube',
                           color=color.brown, scale=(icon_size * 0.3, icon_size * 0.15),
                           position=(x, y - icon_size * 0.2), z=-0.04)
                icons.extend([e1, e2])
            elif weapon_type == 'staff':
                e1 = Entity(parent=camera.ui, model='quad', texture='white_cube',
                           color=color.brown, scale=(icon_size * 0.12, icon_size * 0.8),
                           position=(x, y), z=-0.03)
                e2 = Entity(parent=camera.ui, model='quad', texture='white_cube',
                           color=item_color, scale=(icon_size * 0.3, icon_size * 0.3),
                           position=(x, y + icon_size * 0.35), z=-0.04)
                icons.extend([e1, e2])
            elif weapon_type == 'healing_staff':
                e1 = Entity(parent=camera.ui, model='quad', texture='white_cube',
                           color=color.white, scale=(icon_size * 0.1, icon_size * 0.7),
                           position=(x, y), z=-0.03)
                e2 = Entity(parent=camera.ui, model='quad', texture='white_cube',
                           color=color.lime, scale=(icon_size * 0.25, icon_size * 0.25),
                           position=(x, y + icon_size * 0.3), z=-0.04)
                icons.extend([e1, e2])
            elif weapon_type == 'bow':
                e1 = Entity(parent=camera.ui, model='quad', texture='white_cube',
                           color=item_color, scale=(icon_size * 0.1, icon_size * 0.7),
                           position=(x - icon_size * 0.1, y), z=-0.03)
                e2 = Entity(parent=camera.ui, model='quad', texture='white_cube',
                           color=color.white, scale=(icon_size * 0.03, icon_size * 0.6),
                           position=(x + icon_size * 0.05, y), z=-0.03)
                e3 = Entity(parent=camera.ui, model='quad', texture='white_cube',
                           color=color.brown, scale=(icon_size * 0.05, icon_size * 0.5),
                           position=(x, y), z=-0.04)
                icons.extend([e1, e2, e3])
            else:
                e1 = Entity(parent=camera.ui, model='quad', texture='white_cube',
                           color=item_color, scale=(icon_size * 0.3, icon_size * 0.7),
                           position=(x, y), z=-0.03)
                icons.append(e1)

        elif item_type == 'armor':
            slot = item.get('slot', 'chest')
            if slot == 'chest':
                e1 = Entity(parent=camera.ui, model='quad', texture='white_cube',
                           color=item_color, scale=(icon_size * 0.6, icon_size * 0.7),
                           position=(x, y), z=-0.03)
                icons.append(e1)
            elif slot == 'head':
                e1 = Entity(parent=camera.ui, model='quad', texture='white_cube',
                           color=item_color, scale=(icon_size * 0.5, icon_size * 0.5),
                           position=(x, y + icon_size * 0.1), z=-0.03)
                icons.append(e1)
            elif slot == 'off_hand':
                e1 = Entity(parent=camera.ui, model='quad', texture='white_cube',
                           color=item_color, scale=(icon_size * 0.5, icon_size * 0.6),
                           position=(x, y), z=-0.03)
                e2 = Entity(parent=camera.ui, model='quad', texture='white_cube',
                           color=color.gold, scale=(icon_size * 0.15, icon_size * 0.15),
                           position=(x, y), z=-0.04)
                icons.extend([e1, e2])

        elif item_type == 'consumable':
            e1 = Entity(parent=camera.ui, model='quad', texture='white_cube',
                       color=item_color, scale=(icon_size * 0.35, icon_size * 0.5),
                       position=(x, y - icon_size * 0.1), z=-0.03)
            e2 = Entity(parent=camera.ui, model='quad', texture='white_cube',
                       color=color.light_gray, scale=(icon_size * 0.15, icon_size * 0.2),
                       position=(x, y + icon_size * 0.25), z=-0.03)
            icons.extend([e1, e2])

        elif item_type == 'spell':
            e1 = Entity(parent=camera.ui, model='quad', texture='white_cube',
                       color=color.white, scale=(icon_size * 0.5, icon_size * 0.6),
                       position=(x, y), z=-0.03)
            e2 = Entity(parent=camera.ui, model='quad', texture='white_cube',
                       color=item_color, scale=(icon_size * 0.3, icon_size * 0.3),
                       position=(x, y), z=-0.04)
            icons.extend([e1, e2])

        elif item_type == 'ammo':
            e1 = Entity(parent=camera.ui, model='quad', texture='white_cube',
                       color=color.brown, scale=(icon_size * 0.1, icon_size * 0.6),
                       position=(x, y), z=-0.03)
            e2 = Entity(parent=camera.ui, model='quad', texture='white_cube',
                       color=color.gray, scale=(icon_size * 0.15, icon_size * 0.15),
                       position=(x, y + icon_size * 0.25), z=-0.04)
            icons.extend([e1, e2])

        else:
            e1 = Entity(parent=camera.ui, model='quad', texture='white_cube',
                       color=item_color, scale=(icon_size * 0.5, icon_size * 0.5),
                       position=(x, y), z=-0.03)
            icons.append(e1)

        return icons

    def click_inventory_slot(self, idx):
        """Handle clicking an inventory slot."""
        if idx < len(self.inventory) and self.inventory[idx]:
            self.dragging_item = idx
            item = self.inventory[idx]
            self.selected_item_text.text = f"Selected: {item['name']}\nClick hotbar slot to assign"
            self.selected_item_text.color = Item.RARITY_COLORS.get(item.get('rarity', 'common'), color.white)

    def click_hotbar_slot(self, slot_idx):
        """Handle clicking a hotbar slot to assign item."""
        if self.dragging_item is not None:
            # Check if this item is already in another hotbar slot - remove it first
            for i in range(len(self.hotbar)):
                if self.hotbar[i] == self.dragging_item:
                    self.hotbar[i] = None  # Remove from old slot

            # Assign the selected item to this hotbar slot
            self.hotbar[slot_idx] = self.dragging_item
            item = self.inventory[self.dragging_item]
            self.add_chat_message(f"Assigned {item['name']} to hotbar slot {slot_idx + 1}", color.yellow)

            # Update hotbar display
            self.update_hotbar_display()

            # Clear selection
            self.dragging_item = None
            self.selected_item_text.text = "Item assigned!"

            # Refresh inventory
            self.close_inventory()
            self.open_inventory()

    def delete_selected_item(self):
        """Delete the currently selected item from inventory."""
        if self.dragging_item is not None:
            item = self.inventory[self.dragging_item]
            item_name = item['name']
            
            # Remove from hotbar if it's there
            for i in range(len(self.hotbar)):
                if self.hotbar[i] == self.dragging_item:
                    self.hotbar[i] = None
            
            # Remove from inventory
            self.inventory[self.dragging_item] = None
            
            # Show message
            self.add_chat_message(f"Deleted: {item_name}", color.red)
            
            # Clear selection
            self.dragging_item = None
            self.selected_item_text.text = "Item deleted!"
            
            # Update hotbar display
            self.update_hotbar_display()
            
            # Refresh inventory
            self.close_inventory()
            self.open_inventory()
        else:
            self.selected_item_text.text = "Select an item first!"
            self.selected_item_text.color = color.red

    def update_hotbar_display(self):
        """Update the main game hotbar icons."""
        hotbar_start_x = -0.28
        hotbar_y = -0.40

        # Destroy old icons
        for icon_list in self.hotbar_icons:
            for icon in icon_list:
                destroy(icon)
        self.hotbar_icons = []

        # Create new icons
        for i in range(8):
            item_idx = self.hotbar[i]
            slot_x = hotbar_start_x + i * 0.08
            if item_idx is not None and item_idx < len(self.inventory) and self.inventory[item_idx]:
                item = self.inventory[item_idx]
                icons = self.create_hotbar_icon(item, slot_x, hotbar_y, 0.065)
                self.hotbar_icons.append(icons)
            else:
                self.hotbar_icons.append([])

    def close_inventory(self):
        self.inventory_open = False
        mouse.locked = True
        for ui in self.inventory_ui:
            destroy(ui)
        self.inventory_ui = []

    def open_smelting_ui(self):
        """Open the smelting interface to convert ores to ingots and breakdown items."""
        self.smelting_open = True
        mouse.locked = False
        self.smelting_ui = []

        # Background - larger to fit more sections
        bg = Entity(parent=camera.ui, model='quad', texture='white_cube',
                    color=color.black90, scale=(0.95, 0.88), position=(0, 0), z=0.1)
        self.smelting_ui.append(bg)

        # Border
        border = Entity(parent=camera.ui, model='quad', texture='white_cube',
                        color=color.orange, scale=(0.97, 0.90), position=(0, 0), z=0.2)
        self.smelting_ui.append(border)

        title = Text(text='SMELTING FURNACE', position=(0, 0.40), origin=(0, 0), scale=2, color=color.orange)
        self.smelting_ui.append(title)

        subtitle = Text(text='Smelt ores OR break down weapons/armor/flasks into materials',
                        position=(0, 0.34), origin=(0, 0), scale=0.8, color=color.white)
        self.smelting_ui.append(subtitle)

        slot_size = 0.055
        start_x = -0.38

        # === ORES SECTION (Left Column) ===
        ore_label = Text(text='ORES:', position=(-0.38, 0.26), origin=(0, 0),
                        scale=0.8, color=color.yellow)
        self.smelting_ui.append(ore_label)

        ores_found = []
        for idx, item in enumerate(self.inventory):
            if item and item.get('type') == 'ore':
                ores_found.append((idx, item))

        if not ores_found:
            no_ore_text = Text(text='None', position=(-0.30, 0.18), origin=(0, 0),
                               scale=0.7, color=color.red)
            self.smelting_ui.append(no_ore_text)
        else:
            for i, (idx, ore) in enumerate(ores_found[:8]):  # Max 8 ores shown
                slot_x = start_x + (i % 4) * (slot_size + 0.015)
                slot_y = 0.18 - (i // 4) * (slot_size + 0.02)

                ore_btn = Button(
                    scale=(slot_size, slot_size),
                    position=(slot_x, slot_y),
                    color=ore.get('color', color.gray),
                    highlight_color=color.orange,
                    on_click=Func(self.smelt_ore, idx)
                )
                self.smelting_ui.append(ore_btn)

                ore_name = Text(text=ore['name'][:6], position=(slot_x, slot_y - slot_size/2 - 0.01),
                               origin=(0, 0), scale=0.4, color=color.white)
                self.smelting_ui.append(ore_name)

        # === WEAPONS SECTION (Right Column Top) ===
        weapon_label = Text(text='WEAPONS:', position=(0.10, 0.26), origin=(0, 0),
                           scale=0.8, color=color.cyan)
        self.smelting_ui.append(weapon_label)

        weapons_found = []
        for idx, item in enumerate(self.inventory):
            if item and item.get('type') == 'weapon':
                weapons_found.append((idx, item))

        if not weapons_found:
            no_wpn_text = Text(text='None', position=(0.18, 0.18), origin=(0, 0),
                               scale=0.7, color=color.red)
            self.smelting_ui.append(no_wpn_text)
        else:
            wpn_start_x = 0.10
            for i, (idx, weapon) in enumerate(weapons_found[:8]):  # Max 8 weapons shown
                slot_x = wpn_start_x + (i % 4) * (slot_size + 0.015)
                slot_y = 0.18 - (i // 4) * (slot_size + 0.02)

                wpn_btn = Button(
                    scale=(slot_size, slot_size),
                    position=(slot_x, slot_y),
                    color=weapon.get('color', color.gray),
                    highlight_color=color.cyan,
                    on_click=Func(self.breakdown_weapon, idx)
                )
                self.smelting_ui.append(wpn_btn)

                wpn_name = Text(text=weapon['name'][:6], position=(slot_x, slot_y - slot_size/2 - 0.01),
                               origin=(0, 0), scale=0.4, color=color.white)
                self.smelting_ui.append(wpn_name)

        # === ARMOR SECTION (Left Column Bottom) ===
        armor_label = Text(text='ARMOR:', position=(-0.38, -0.02), origin=(0, 0),
                          scale=0.8, color=color.magenta)
        self.smelting_ui.append(armor_label)

        armor_found = []
        for idx, item in enumerate(self.inventory):
            if item and item.get('type') == 'armor':
                armor_found.append((idx, item))

        if not armor_found:
            no_armor_text = Text(text='None', position=(-0.30, -0.10), origin=(0, 0),
                                scale=0.7, color=color.red)
            self.smelting_ui.append(no_armor_text)
        else:
            for i, (idx, armor) in enumerate(armor_found[:8]):  # Max 8 armor shown
                slot_x = start_x + (i % 4) * (slot_size + 0.015)
                slot_y = -0.10 - (i // 4) * (slot_size + 0.02)

                armor_btn = Button(
                    scale=(slot_size, slot_size),
                    position=(slot_x, slot_y),
                    color=armor.get('color', color.gray),
                    highlight_color=color.magenta,
                    on_click=Func(self.breakdown_armor, idx)
                )
                self.smelting_ui.append(armor_btn)

                armor_name = Text(text=armor['name'][:6], position=(slot_x, slot_y - slot_size/2 - 0.01),
                                 origin=(0, 0), scale=0.4, color=color.white)
                self.smelting_ui.append(armor_name)

        # === FLASKS/POTIONS SECTION (Right Column Bottom) ===
        flask_label = Text(text='FLASKS:', position=(0.10, -0.02), origin=(0, 0),
                          scale=0.8, color=color.lime)
        self.smelting_ui.append(flask_label)

        flasks_found = []
        for idx, item in enumerate(self.inventory):
            if item and item.get('type') in ['potion', 'flask']:
                flasks_found.append((idx, item))

        if not flasks_found:
            no_flask_text = Text(text='None', position=(0.18, -0.10), origin=(0, 0),
                                scale=0.7, color=color.red)
            self.smelting_ui.append(no_flask_text)
        else:
            flask_start_x = 0.10
            for i, (idx, flask) in enumerate(flasks_found[:8]):  # Max 8 flasks shown
                slot_x = flask_start_x + (i % 4) * (slot_size + 0.015)
                slot_y = -0.10 - (i // 4) * (slot_size + 0.02)

                flask_btn = Button(
                    scale=(slot_size, slot_size),
                    position=(slot_x, slot_y),
                    color=flask.get('color', color.gray),
                    highlight_color=color.lime,
                    on_click=Func(self.breakdown_flask, idx)
                )
                self.smelting_ui.append(flask_btn)

                flask_name = Text(text=flask['name'][:6], position=(slot_x, slot_y - slot_size/2 - 0.01),
                                 origin=(0, 0), scale=0.4, color=color.white)
                self.smelting_ui.append(flask_name)

        # Results info
        result_info = Text(text='Breakdown items to get ingots based on rarity. Armor gives leather too!',
                          position=(0, -0.28), origin=(0, 0), scale=0.7, color=color.light_gray)
        self.smelting_ui.append(result_info)

        # Instructions
        close_text = Text(text='[ESC] Close',
                          position=(0, -0.38), origin=(0, 0), scale=0.9, color=color.light_gray)
        self.smelting_ui.append(close_text)

    def smelt_ore(self, inv_idx):
        """Smelt an ore into an ingot."""
        if inv_idx >= len(self.inventory) or not self.inventory[inv_idx]:
            return

        ore = self.inventory[inv_idx]
        if ore.get('type') != 'ore':
            return

        smelt_result = ore.get('smelt_result')
        if not smelt_result or smelt_result not in Item.ITEM_DATA:
            self.add_chat_message("Cannot smelt this ore!", color.red)
            return

        # Remove ore from inventory
        self.inventory[inv_idx] = None

        # Add ingot to inventory (3x in dream mode)
        ingot_count = 3 if self.dream_mode else 1
        
        for _ in range(ingot_count):
            ingot_data = Item.ITEM_DATA[smelt_result].copy()
            ingot_data['name'] = smelt_result
            
            # Find empty slot for ingot
            added = False
            for i in range(len(self.inventory)):
                if self.inventory[i] is None:
                    self.inventory[i] = ingot_data
                    added = True
                    break
            
            if not added:
                break  # Stop if inventory full
        
        if ingot_count > 1:
            self.add_chat_message(f"Smelted {ore['name']} into {ingot_count}x {smelt_result}! (Dream Mode Bonus)", color.magenta)
        else:
            self.add_chat_message(f"Smelted {ore['name']} into {smelt_result}!", color.orange)

        # Refresh smelting UI
        self.close_smelting_ui()
        self.open_smelting_ui()

    def close_smelting_ui(self):
        """Close the smelting interface."""
        self.smelting_open = False
        mouse.locked = True
        for ui in self.smelting_ui:
            destroy(ui)
        self.smelting_ui = []

    def breakdown_weapon(self, inv_idx):
        """Break down a weapon into ingots based on its rarity/damage."""
        if inv_idx >= len(self.inventory) or not self.inventory[inv_idx]:
            return

        weapon = self.inventory[inv_idx]
        if weapon.get('type') != 'weapon':
            return
        
        weapon_name = weapon['name']
        
        # Special case: tErRoR bOw melts into tErRoR ingot
        if weapon_name == 'tErRoR bOw':
            self.inventory[inv_idx] = None
            terror_ingot = {
                'name': 'tErRoR ingot',
                'type': 'ore',
                'rarity': 'legendary',
                'color': color.rgb(255, 0, 255)
            }
            for i in range(len(self.inventory)):
                if self.inventory[i] is None:
                    self.inventory[i] = terror_ingot
                    self.add_chat_message("Melted tErRoR bOw into tErRoR ingot!", color.rgb(255, 0, 255))
                    break
            self.close_smelting_ui()
            self.open_smelting_ui()
            return

        # Determine ingot type and amount based on weapon rarity and damage
        rarity = weapon.get('rarity', 'common')
        damage = weapon.get('damage', 10)

        # Map rarity to ingot type
        rarity_ingot_map = {
            'common': 'Iron Ingot',
            'uncommon': 'Silver Ingot',
            'rare': 'Mithril Ingot',
            'legendary': 'Shadow Ingot'
        }

        # Calculate ingot count based on damage
        if damage < 15:
            ingot_count = 1
        elif damage < 30:
            ingot_count = 2
        elif damage < 50:
            ingot_count = 3
        else:
            ingot_count = 4

        ingot_type = rarity_ingot_map.get(rarity, 'Iron Ingot')

        # Remove weapon from inventory
        weapon_name = weapon['name']
        self.inventory[inv_idx] = None

        # Add ingots to inventory
        added_count = 0
        for _ in range(ingot_count):
            if ingot_type in Item.ITEM_DATA:
                ingot_data = Item.ITEM_DATA[ingot_type].copy()
                ingot_data['name'] = ingot_type
                for i in range(len(self.inventory)):
                    if self.inventory[i] is None:
                        self.inventory[i] = ingot_data
                        added_count += 1
                        break

        if added_count > 0:
            self.add_chat_message(f"Broke down {weapon_name} into {added_count}x {ingot_type}!", color.cyan)
        else:
            self.add_chat_message("Inventory full! Materials lost.", color.red)

        # Refresh smelting UI
        self.close_smelting_ui()
        self.open_smelting_ui()

    def breakdown_armor(self, inv_idx):
        """Break down armor into ingots and leather based on rarity/defense."""
        if inv_idx >= len(self.inventory) or not self.inventory[inv_idx]:
            return

        armor = self.inventory[inv_idx]
        if armor.get('type') != 'armor':
            return

        # Determine ingot type and amount based on armor rarity and defense
        rarity = armor.get('rarity', 'common')
        defense = armor.get('defense', 5)

        # Map rarity to ingot type
        rarity_ingot_map = {
            'common': 'Iron Ingot',
            'uncommon': 'Silver Ingot',
            'rare': 'Mithril Ingot',
            'legendary': 'Shadow Ingot'
        }

        # Calculate ingot count based on defense value
        if defense < 10:
            ingot_count = 1
        elif defense < 25:
            ingot_count = 2
        elif defense < 50:
            ingot_count = 3
        else:
            ingot_count = 4

        ingot_type = rarity_ingot_map.get(rarity, 'Iron Ingot')
        leather_count = 1 if defense < 20 else 2  # Armor always gives some leather

        # Remove armor from inventory
        armor_name = armor['name']
        self.inventory[inv_idx] = None

        # Add ingots to inventory
        added_ingots = 0
        for _ in range(ingot_count):
            if ingot_type in Item.ITEM_DATA:
                ingot_data = Item.ITEM_DATA[ingot_type].copy()
                ingot_data['name'] = ingot_type
                for i in range(len(self.inventory)):
                    if self.inventory[i] is None:
                        self.inventory[i] = ingot_data
                        added_ingots += 1
                        break

        # Add leather to inventory
        added_leather = 0
        for _ in range(leather_count):
            if 'Leather' in Item.ITEM_DATA:
                leather_data = Item.ITEM_DATA['Leather'].copy()
                leather_data['name'] = 'Leather'
                for i in range(len(self.inventory)):
                    if self.inventory[i] is None:
                        self.inventory[i] = leather_data
                        added_leather += 1
                        break

        if added_ingots > 0 or added_leather > 0:
            self.add_chat_message(f"Broke down {armor_name}: {added_ingots}x {ingot_type}, {added_leather}x Leather!", color.magenta)
        else:
            self.add_chat_message("Inventory full! Materials lost.", color.red)

        # Refresh smelting UI
        self.close_smelting_ui()
        self.open_smelting_ui()

    def breakdown_flask(self, inv_idx):
        """Break down potions/flasks into magic crystals or special materials."""
        if inv_idx >= len(self.inventory) or not self.inventory[inv_idx]:
            return

        flask = self.inventory[inv_idx]
        if flask.get('type') not in ['potion', 'flask']:
            return

        # Determine result based on potion rarity
        rarity = flask.get('rarity', 'common')
        flask_name = flask['name']

        # Map rarity to material type
        rarity_material_map = {
            'common': 'Magic Crystal',
            'uncommon': 'Magic Crystal',
            'rare': 'Void Essence',
            'legendary': 'Swift Essence'  # Special dungeon metal!
        }

        # Greater potions give more
        is_greater = 'Greater' in flask_name or 'Super' in flask_name
        material_count = 2 if is_greater else 1

        # Legendary flasks can give special metals
        if rarity == 'legendary':
            # 50% chance for special metal
            if random.random() < 0.5:
                material_type = random.choice(['Void Metal', 'Life Crystal', 'Swift Essence'])
            else:
                material_type = 'Void Essence'
        else:
            material_type = rarity_material_map.get(rarity, 'Magic Crystal')

        # Remove flask from inventory
        self.inventory[inv_idx] = None

        # Add materials to inventory
        added_count = 0
        for _ in range(material_count):
            if material_type in Item.ITEM_DATA:
                mat_data = Item.ITEM_DATA[material_type].copy()
                mat_data['name'] = material_type
                for i in range(len(self.inventory)):
                    if self.inventory[i] is None:
                        self.inventory[i] = mat_data
                        added_count += 1
                        break

        if added_count > 0:
            self.add_chat_message(f"Broke down {flask_name} into {added_count}x {material_type}!", color.lime)
        else:
            self.add_chat_message("Inventory full! Materials lost.", color.red)

        # Refresh smelting UI
        self.close_smelting_ui()
        self.open_smelting_ui()

    def open_secret_anvil_crafting(self):
        """Open special secret base anvil for arrows and level 2 weapons."""
        self.crafting_open = True
        mouse.locked = False
        self.crafting_ui = []

        # Background
        bg = Entity(parent=camera.ui, model='quad', texture='white_cube',
                    color=color.black90, scale=(0.8, 0.7), position=(0, 0.02), z=0.1)
        self.crafting_ui.append(bg)

        # Border
        border = Entity(parent=camera.ui, model='quad', texture='white_cube',
                        color=color.gold, scale=(0.82, 0.72), position=(0, 0.02), z=0.2)
        self.crafting_ui.append(border)

        title = Text(text='SECRET ANVIL', position=(0, 0.32), origin=(0, 0), scale=2.2, color=color.gold)
        self.crafting_ui.append(title)

        subtitle = Text(text='Craft powerful arrows and Level 2 weapons!',
                        position=(0, 0.25), origin=(0, 0), scale=0.9, color=color.yellow)
        self.crafting_ui.append(subtitle)

        # Crafting recipes
        recipes = [
            # Arrows
            {'name': 'Basic Arrows (x10)', 'materials': '5 Wood', 'item': 'Arrow'},
            {'name': 'Fire Arrows (x5)', 'materials': '3 Wood + 2 Coal', 'item': 'Fire Arrow'},
            {'name': 'Ice Arrows (x5)', 'materials': '3 Wood + 2 Ice Shard', 'item': 'Ice Arrow'},
            
            # Level 2 Weapons
            {'name': 'Steel Sword II', 'materials': '3 Iron + 2 Steel', 'item': 'Steel Sword II'},
            {'name': 'Steel Bow II', 'materials': '2 Iron + 3 Wood + 1 Steel', 'item': 'Steel Bow II'},
            {'name': 'Steel Dagger II', 'materials': '2 Iron + 1 Steel', 'item': 'Steel Dagger II'},
            {'name': 'Steel Staff II', 'materials': '2 Iron + 2 Wood + 1 Crystal', 'item': 'Steel Staff II'},
        ]

        start_y = 0.15
        for i, recipe in enumerate(recipes):
            y_pos = start_y - i * 0.08
            
            # Recipe name
            Text(text=recipe['name'], position=(-0.3, y_pos), origin=(0, 0),
                 scale=0.85, color=color.white, parent=camera.ui).background = True
            self.crafting_ui.append(self.crafting_ui[-1] if self.crafting_ui else None)
            
            # Materials needed
            Text(text=recipe['materials'], position=(0.1, y_pos), origin=(0, 0),
                 scale=0.7, color=color.light_gray, parent=camera.ui).background = True
            self.crafting_ui.append(self.crafting_ui[-1] if self.crafting_ui else None)
            
            # Craft button
            craft_btn = Button(
                text='CRAFT',
                scale=(0.1, 0.04),
                position=(0.32, y_pos),
                color=color.green,
                highlight_color=color.lime,
                on_click=Func(self.craft_secret_item, recipe['item'])
            )
            self.crafting_ui.append(craft_btn)

        # Close button
        close_btn = Button(
            text='CLOSE [ESC]',
            scale=(0.2, 0.05),
            position=(0, -0.28),
            color=color.red,
            highlight_color=color.orange,
            on_click=self.close_crafting_ui
        )
        self.crafting_ui.append(close_btn)

    def open_secret_anvil_crafting(self):
        """Open special secret base anvil for arrows and level 2 weapons."""
        self.crafting_open = True
        mouse.locked = False
        self.crafting_ui = []
        self.craft_slots = [None, None, None, None, None]  # 5 slots
        self.selected_craft_material = None  # Initialize selected material

        # Weapon type selection (default to sword)
        if not hasattr(self, 'selected_weapon_type'):
            self.selected_weapon_type = 'sword'

        # Background
        bg = Entity(parent=camera.ui, model='quad', texture='white_cube',
                    color=color.black90, scale=(0.95, 0.8), position=(0, 0.02), z=0.1)
        self.crafting_ui.append(bg)

        # Border (gold for secret anvil)
        border = Entity(parent=camera.ui, model='quad', texture='white_cube',
                        color=color.gold, scale=(0.97, 0.82), position=(0, 0.02), z=0.2)
        self.crafting_ui.append(border)

        title = Text(text='SECRET ANVIL', position=(0, 0.35), origin=(0, 0), scale=2, color=color.gold)
        self.crafting_ui.append(title)

        subtitle = Text(text='Place materials in slots, then craft! AI determines the result.',
                        position=(0, 0.28), origin=(0, 0), scale=0.85, color=color.yellow)
        self.crafting_ui.append(subtitle)

        # Crafting slots (5 material slots)
        self.craft_slot_btns = []
        slot_size = 0.085
        slot_start_x = -0.24

        craft_label = Text(text='Material Slots:', position=(-0.35, 0.18), origin=(0, 0),
                           scale=0.9, color=color.yellow)
        self.crafting_ui.append(craft_label)

        for i in range(5):
            slot_x = slot_start_x + i * (slot_size + 0.025)
            slot_btn = Button(
                scale=(slot_size, slot_size),
                position=(slot_x, 0.08),
                color=color.dark_gray,
                highlight_color=color.gray,
                on_click=Func(self.click_craft_slot, i)
            )
            self.crafting_ui.append(slot_btn)
            self.craft_slot_btns.append({'btn': slot_btn, 'pos': (slot_x, 0.08)})

            slot_num = Text(text=str(i + 1), position=(slot_x, 0.08 + slot_size/2 + 0.02),
                           origin=(0, 0), scale=0.7, color=color.white)
            self.crafting_ui.append(slot_num)

        # Weapon type selection buttons
        weapon_label = Text(text='Weapon Type:', position=(-0.35, -0.02), origin=(0, 0),
                           scale=0.9, color=color.yellow)
        self.crafting_ui.append(weapon_label)

        weapon_types = ['sword', 'bow', 'dagger', 'staff']
        weapon_start_x = -0.22
        for i, wtype in enumerate(weapon_types):
            wtype_x = weapon_start_x + i * 0.11
            wtype_btn = Button(
                text=wtype.upper(),
                scale=(0.10, 0.04),
                position=(wtype_x, -0.02),
                color=color.azure if self.selected_weapon_type == wtype else color.dark_gray,
                highlight_color=color.cyan,
                on_click=Func(self.select_weapon_type, wtype)
            )
            self.crafting_ui.append(wtype_btn)

        # Craft button
        craft_btn = Button(
            text='CRAFT',
            scale=(0.2, 0.07),
            position=(0, -0.12),
            color=color.green,
            highlight_color=color.lime,
            on_click=self.craft_secret_item_with_ai
        )
        self.crafting_ui.append(craft_btn)

        # Info text
        info = Text(text='Secret Anvil uses AI crafting - Same as village anvil!',
                    position=(0, -0.22), origin=(0, 0), scale=0.75, color=color.light_gray)
        self.crafting_ui.append(info)

        # Close button
        close_btn = Button(
            text='CLOSE [ESC]',
            scale=(0.2, 0.05),
            position=(0, -0.30),
            color=color.red,
            highlight_color=color.orange,
            on_click=self.close_crafting_ui
        )
        self.crafting_ui.append(close_btn)

        # Display items in slots
        self.update_craft_slot_display()

    def craft_secret_item_with_ai(self):
        """Use AI to craft items from secret anvil based on materials."""
        # Check if any materials placed
        if all(slot is None for slot in self.craft_slots):
            self.add_chat_message("Place materials in slots first!", color.red)
            return

        # Gather material names
        materials = []
        material_indices = []
        for i, slot in enumerate(self.craft_slots):
            if slot is not None:
                materials.append(slot['name'])
                material_indices.append(i)

        if not materials:
            self.add_chat_message("No materials in slots!", color.red)
            return

        # Use the same AI crafting system as the regular anvil
        new_item = self.create_ai_crafted_item(materials)

        # Remove materials from slots
        for i in material_indices:
            # Find and remove the item from inventory
            for inv_idx, inv_item in enumerate(self.inventory):
                if inv_item and inv_item['name'] == self.craft_slots[i]['name']:
                    self.inventory[inv_idx] = None
                    break

        # Add crafted item to inventory
        added = False
        for i in range(len(self.inventory)):
            if self.inventory[i] is None:
                self.inventory[i] = new_item
                added = True
                break

        if added:
            self.add_chat_message(f"Crafted: {new_item['name']}!", color.gold)
            self.update_hotbar_display()
            self.craft_slots = [None, None, None, None, None]
            self.update_craft_slot_display()
        else:
            self.add_chat_message("Inventory full!", color.red)

    def craft_secret_item(self, item_name):
        """Craft an item from the secret anvil."""
        # For now, just add the item if there's space
        # TODO: Check for materials in inventory
        created_item = Item.create(item_name)
        if created_item:
            added = False
            for i in range(len(self.inventory)):
                if self.inventory[i] is None:
                    self.inventory[i] = created_item
                    added = True
                    break
            
            if added:
                self.add_chat_message(f"Crafted {item_name}!", color.gold)
                self.update_hotbar_display()
            else:
                self.add_chat_message("Inventory full!", color.red)
        else:
            self.add_chat_message(f"Cannot craft {item_name}", color.red)

    def open_crafting_ui(self):
        """Open the crafting interface with AI-based item creation."""
        self.crafting_open = True
        mouse.locked = False
        self.crafting_ui = []
        self.craft_slots = [None, None, None, None, None]  # 5 slots
        self.selected_craft_material = None  # Initialize selected material

        # Weapon type selection (default to sword)
        if not hasattr(self, 'selected_weapon_type'):
            self.selected_weapon_type = 'sword'

        # Background
        bg = Entity(parent=camera.ui, model='quad', texture='white_cube',
                    color=color.black90, scale=(0.95, 0.8), position=(0, 0.02), z=0.1)
        self.crafting_ui.append(bg)

        # Border
        border = Entity(parent=camera.ui, model='quad', texture='white_cube',
                        color=color.cyan, scale=(0.97, 0.82), position=(0, 0.02), z=0.2)
        self.crafting_ui.append(border)

        title = Text(text='CRAFTING ANVIL', position=(0, 0.35), origin=(0, 0), scale=2, color=color.cyan)
        self.crafting_ui.append(title)

        subtitle = Text(text='Place materials in slots, then craft! AI determines the result.',
                        position=(0, 0.28), origin=(0, 0), scale=0.85, color=color.white)
        self.crafting_ui.append(subtitle)

        # Crafting slots (5 material slots)
        self.craft_slot_btns = []
        slot_size = 0.085
        slot_start_x = -0.24

        craft_label = Text(text='Material Slots:', position=(-0.35, 0.18), origin=(0, 0),
                           scale=0.9, color=color.yellow)
        self.crafting_ui.append(craft_label)

        for i in range(5):
            slot_x = slot_start_x + i * (slot_size + 0.025)
            slot_btn = Button(
                scale=(slot_size, slot_size),
                position=(slot_x, 0.08),
                color=color.dark_gray,
                highlight_color=color.gray,
                on_click=Func(self.click_craft_slot, i)
            )
            self.crafting_ui.append(slot_btn)
            self.craft_slot_btns.append({'btn': slot_btn, 'pos': (slot_x, 0.08)})

            slot_num = Text(text=str(i + 1), position=(slot_x, 0.08 + slot_size/2 + 0.02),
                           origin=(0, 0), scale=0.7, color=color.white)
            self.crafting_ui.append(slot_num)

        # Weapon type selection buttons
        weapon_label = Text(text='Weapon Type:', position=(-0.35, -0.02), origin=(0, 0),
                           scale=0.9, color=color.yellow)
        self.crafting_ui.append(weapon_label)

        weapon_types = ['sword', 'bow', 'dagger', 'staff']
        weapon_start_x = -0.22
        for i, wtype in enumerate(weapon_types):
            wtype_x = weapon_start_x + i * 0.11
            wtype_btn = Button(
                text=wtype.upper(),
                scale=(0.10, 0.04),
                position=(wtype_x, -0.02),
                color=color.azure if self.selected_weapon_type == wtype else color.dark_gray,
                highlight_color=color.cyan,
                on_click=Func(self.select_weapon_type, wtype)
            )
            self.crafting_ui.append(wtype_btn)

        # Result preview area
        result_label = Text(text='Result:', position=(0.32, 0.08), origin=(0, 0),
                            scale=0.9, color=color.yellow)
        self.crafting_ui.append(result_label)

        self.craft_result_text = Text(text='???', position=(0.32, 0.01), origin=(0, 0),
                                       scale=1.0, color=color.light_gray)
        self.crafting_ui.append(self.craft_result_text)

        # Craft button
        craft_btn = Button(text='CRAFT', scale=(0.15, 0.06), position=(0, -0.10),
                           color=color.green, on_click=self.do_craft)
        self.crafting_ui.append(craft_btn)

        # Inventory section for selecting materials
        inv_label = Text(text='Your Materials (click to add to slot):', position=(0, -0.19),
                         origin=(0, 0), scale=0.9, color=color.yellow)
        self.crafting_ui.append(inv_label)

        # Show craftable materials from inventory (ingots, ores, special metals, materials)
        mat_size = 0.065
        start_x = -0.35
        mat_y = -0.32

        self.mat_buttons = []
        mat_count = 0
        for idx, item in enumerate(self.inventory):
            # Check if item is craftable material
            item_type = item.get('type', '') if item else ''
            is_craftable = item_type in ['ingot', 'material', 'ore', 'special_metal'] if item else False
            
            if is_craftable:
                mat_x = start_x + (mat_count % 10) * (mat_size + 0.015)
                mat_row_y = mat_y - (mat_count // 10) * (mat_size + 0.015)

                mat_btn = Button(
                    scale=(mat_size, mat_size),
                    position=(mat_x, mat_row_y),
                    color=item.get('color', color.white),
                    highlight_color=color.cyan,
                    on_click=Func(self.select_material_for_craft, idx)
                )
                self.crafting_ui.append(mat_btn)
                self.mat_buttons.append({'btn': mat_btn, 'idx': idx, 'item': item})

                # Small name label
                short_name = item['name'][:6]
                name_lbl = Text(text=short_name, position=(mat_x, mat_row_y - mat_size/2 - 0.01),
                               origin=(0, 0), scale=0.45, color=color.white)
                self.crafting_ui.append(name_lbl)

                mat_count += 1

        if mat_count == 0:
            no_mat = Text(text='No materials in inventory!', position=(0, -0.30),
                         origin=(0, 0), scale=1.0, color=color.red)
            self.crafting_ui.append(no_mat)

        # Instructions
        close_text = Text(text='[ESC] Close | Click material then click slot to place',
                          position=(0, -0.35), origin=(0, 0), scale=0.8, color=color.light_gray)
        self.crafting_ui.append(close_text)

        # Currently selected material for placing
        self.selected_craft_material = None

    def select_material_for_craft(self, inv_idx):
        """Select a material from inventory to place in craft slot."""
        if inv_idx >= len(self.inventory) or not self.inventory[inv_idx]:
            return
        self.selected_craft_material = inv_idx
        self.add_chat_message(f"Selected {self.inventory[inv_idx]['name']} - click a slot to place", color.cyan)

    def click_craft_slot(self, slot_idx):
        """Place selected material in craft slot or remove existing."""
        if self.selected_craft_material is not None:
            # Place material in slot
            if self.selected_craft_material < len(self.inventory) and self.inventory[self.selected_craft_material]:
                self.craft_slots[slot_idx] = self.selected_craft_material
                self.update_craft_slot_display()
                self.update_craft_preview()
                self.selected_craft_material = None
        else:
            # Clear slot if clicked without selection
            if self.craft_slots[slot_idx] is not None:
                self.craft_slots[slot_idx] = None
                self.update_craft_slot_display()
                self.update_craft_preview()

    def update_craft_slot_display(self):
        """Update the visual display of craft slots."""
        for i, slot_data in enumerate(self.craft_slot_btns):
            inv_idx = self.craft_slots[i]
            if inv_idx is not None and inv_idx < len(self.inventory) and self.inventory[inv_idx]:
                slot_data['btn'].color = self.inventory[inv_idx].get('color', color.white)
            else:
                slot_data['btn'].color = color.dark_gray

    def update_craft_preview(self):
        """Preview what item would be crafted based on materials."""
        # Get material names in slots
        materials = []
        for inv_idx in self.craft_slots:
            if inv_idx is not None and inv_idx < len(self.inventory) and self.inventory[inv_idx]:
                materials.append(self.inventory[inv_idx]['name'])

        if not materials:
            self.craft_result_text.text = '???'
            self.craft_result_text.color = color.light_gray
            return

        # Sort materials for recipe matching
        materials_sorted = tuple(sorted(materials))

        # Check exact recipe match first
        result = None
        bonus = 0
        for recipe_mats, recipe_data in Item.CRAFTING_RECIPES.items():
            if tuple(sorted(recipe_mats)) == materials_sorted:
                result = recipe_data['result']
                bonus = recipe_data.get('bonus_damage', 0)
                break

        # Check for special metal bonuses (4x damage + effects!)
        special_metals = ['Void Metal', 'Life Crystal', 'Swift Essence', 'Vitality Core', 'Chrono Shard',
                          'Venom Core', 'Plague Essence', 'Frost Shard', 'Weakness Crystal', 'Curse Stone', 'tErRoR ingot']
        has_special = any(m in special_metals for m in materials)
        special_bonus_text = " [4x DMG!]" if has_special else ""

        if result:
            self.craft_result_text.text = f"{result}" + (f" (+{bonus} dmg)" if bonus > 0 else "") + special_bonus_text
            self.craft_result_text.color = color.green
        else:
            # AI-generated item based on materials
            self.craft_result_text.text = self.generate_ai_item_name(materials) + special_bonus_text
            self.craft_result_text.color = color.magenta if has_special else color.yellow

    def generate_ai_item_name(self, materials):
        """Generate an item name based on materials (AI-like system)."""
        if not materials:
            return "???"

        # Material tier calculation
        tier_values = {
            'Copper Ingot': 1, 'Iron Ingot': 2, 'Silver Ingot': 3, 'Gold Ingot': 4,
            'Mithril Ingot': 5, 'Adamantite Ingot': 6, 'Shadow Ingot': 7, 'Dragon Ingot': 8,
            'Wood': 1, 'Leather': 2, 'Magic Crystal': 5, 'Dragon Scale': 7, 'Void Essence': 8
        }

        # Prefixes based on highest tier material
        prefixes = {
            1: '', 2: 'Sturdy ', 3: 'Fine ', 4: 'Gilded ',
            5: 'Mystic ', 6: 'Adamant ', 7: 'Shadow ', 8: 'Dragon '
        }

        # Determine weapon type based on material count
        has_wood = any('Wood' in m for m in materials)
        has_crystal = any('Crystal' in m for m in materials)

        if has_crystal:
            weapon = 'Staff'
        elif has_wood and len(materials) == 2:
            weapon = 'Bow'
        elif len(materials) >= 3:
            weapon = 'Sword'
        elif len(materials) == 2:
            weapon = 'Dagger'
        else:
            weapon = 'Blade'

        # Get highest tier
        max_tier = 1
        for mat in materials:
            tier = tier_values.get(mat, 1)
            if tier > max_tier:
                max_tier = tier

        prefix = prefixes.get(max_tier, '')
        return f"{prefix}{weapon} (Custom)"

    def do_craft(self):
        """Execute the crafting."""
        # Get materials from slots
        materials = []
        material_indices = []
        for inv_idx in self.craft_slots:
            if inv_idx is not None and inv_idx < len(self.inventory) and self.inventory[inv_idx]:
                materials.append(self.inventory[inv_idx]['name'])
                material_indices.append(inv_idx)

        if not materials:
            self.add_chat_message("No materials in slots!", color.red)
            return

        # Check for exact recipe
        materials_sorted = tuple(sorted(materials))
        result_name = None
        bonus_damage = 0

        for recipe_mats, recipe_data in Item.CRAFTING_RECIPES.items():
            if tuple(sorted(recipe_mats)) == materials_sorted:
                result_name = recipe_data['result']
                bonus_damage = recipe_data.get('bonus_damage', 0)
                break

        if result_name and result_name in Item.ITEM_DATA:
            # Known recipe - create the item
            new_item = Item.ITEM_DATA[result_name].copy()
            new_item['name'] = result_name
            if bonus_damage > 0:
                new_item['damage'] = new_item.get('damage', 0) + bonus_damage
        else:
            # AI-generated custom item
            new_item = self.create_ai_crafted_item(materials)

        # Remove materials from inventory
        for idx in material_indices:
            self.inventory[idx] = None

        # Add crafted item to inventory
        added = False
        for i in range(len(self.inventory)):
            if self.inventory[i] is None:
                self.inventory[i] = new_item
                added = True
                break
        
        if added:
            self.add_chat_message(f"Crafted: {new_item['name']}!", color.cyan)
        else:
            self.add_chat_message("Inventory full! Item lost.", color.red)

        # Reset and refresh
        self.craft_slots = [None, None, None]
        self.close_crafting_ui()
        self.open_crafting_ui()

    def select_weapon_type(self, weapon_type):
        """Select weapon type for crafting."""
        self.selected_weapon_type = weapon_type
        self.close_crafting_ui()
        self.open_crafting_ui()

    def create_ai_crafted_item(self, materials):
        """Create a custom item based on materials placed."""
        tier_values = {
            'Copper Ingot': 1, 'Iron Ingot': 2, 'Silver Ingot': 3, 'Gold Ingot': 4,
            'Mithril Ingot': 5, 'Adamantite Ingot': 6, 'Shadow Ingot': 7, 'Dragon Ingot': 8,
            'Wood': 1, 'Leather': 2, 'Magic Crystal': 5, 'Dragon Scale': 7, 'Void Essence': 8,
            'Copper Ore': 0, 'Iron Ore': 1, 'Silver Ore': 2, 'Gold Ore': 3,
            'Mithril Ore': 4, 'Adamantite Ore': 5, 'Shadow Ore': 6, 'Dragon Ore': 7
        }

        tier_colors = {
            1: color.brown, 2: color.gray, 3: color.light_gray, 4: color.gold,
            5: color.cyan, 6: color.violet, 7: color.black, 8: color.red
        }

        tier_rarities = {
            1: 'common', 2: 'common', 3: 'uncommon', 4: 'uncommon',
            5: 'rare', 6: 'rare', 7: 'legendary', 8: 'legendary'
        }

        prefixes = {
            1: 'Crude', 2: 'Sturdy', 3: 'Fine', 4: 'Gilded',
            5: 'Mystic', 6: 'Adamant', 7: 'Shadow', 8: 'Dragon'
        }

        # Special metal bonuses (from dungeon 7+) - all grant 4x damage!
        special_metal_bonuses = {
            'Void Metal': {'type': 'speed', 'value': 10, 'damage_mult': 4},
            'Life Crystal': {'type': 'health', 'value': 25, 'damage_mult': 4},
            'Swift Essence': {'type': 'speed', 'value': 15, 'damage_mult': 4},
            'Vitality Core': {'type': 'health', 'value': 50, 'damage_mult': 4},
            'Chrono Shard': {'type': 'attack_speed', 'value': 2.0, 'damage_mult': 4},  # 2x attack speed, stacks!
            'Venom Core': {'type': 'poison', 'value': 15, 'damage_mult': 4},
            'Plague Essence': {'type': 'poison', 'value': 25, 'damage_mult': 4},
            'Frost Shard': {'type': 'slow', 'value': 50, 'damage_mult': 4},
            'Weakness Crystal': {'type': 'weaken', 'value': 30, 'damage_mult': 4},
            'Curse Stone': {'type': 'curse', 'value': 20, 'damage_mult': 4},
            'tErRoR ingot': {'type': 'xp', 'value': 4.0, 'attack_speed_value': 3.0, 'damage_mult': 4}  # 4x XP, 3x attack speed, 4x dmg!
        }

        # Calculate total tier value and check for special metals
        total_tier = 0
        max_tier = 1
        health_bonus = 0
        speed_bonus = 0
        attack_speed_mult = 1.0  # Base attack speed multiplier
        damage_multiplier = 1  # Base damage multiplier
        xp_multiplier = 1.0  # Base XP multiplier
        poison_damage = 0
        slow_percent = 0
        weaken_percent = 0
        curse_percent = 0
        has_special_metal = False

        for mat in materials:
            tier = tier_values.get(mat, 1)
            total_tier += tier
            if tier > max_tier:
                max_tier = tier

            # Check for special metal bonuses
            if mat in special_metal_bonuses:
                has_special_metal = True
                bonus = special_metal_bonuses[mat]
                damage_multiplier = max(damage_multiplier, bonus.get('damage_mult', 1))  # 4x damage from special metals
                if bonus['type'] == 'health':
                    health_bonus += bonus['value']
                elif bonus['type'] == 'speed':
                    speed_bonus += bonus['value']
                elif bonus['type'] == 'attack_speed':
                    attack_speed_mult *= bonus['value']  # Stacks multiplicatively (2x * 2x = 4x)
                elif bonus['type'] == 'xp':
                    xp_multiplier = bonus['value']  # 4x XP gain
                    if 'attack_speed_value' in bonus:
                        attack_speed_mult *= bonus['attack_speed_value']  # 3x attack speed for tErRoR ingot
                elif bonus['type'] == 'poison':
                    poison_damage += bonus['value']
                elif bonus['type'] == 'slow':
                    slow_percent += bonus['value']
                elif bonus['type'] == 'weaken':
                    weaken_percent += bonus['value']
                elif bonus['type'] == 'curse':
                    curse_percent += bonus['value']

        # Determine weapon type based on selection
        weapon_type = getattr(self, 'selected_weapon_type', 'sword')

        if weapon_type == 'bow':
            base_damage = 10 + total_tier * 4
            attack_range = 15 + total_tier * 2
        elif weapon_type == 'dagger':
            base_damage = 8 + total_tier * 3
        elif weapon_type == 'staff':
            base_damage = 12 + total_tier * 4
        else:  # sword
            base_damage = 15 + total_tier * 5

        # Apply 4x damage multiplier from special metals
        base_damage = int(base_damage * damage_multiplier)
        
        # Dream mode: 3x weapon damage
        if self.dream_mode:
            base_damage = int(base_damage * 3)

        prefix = prefixes.get(max_tier, 'Crude')
        weapon_name = weapon_type.capitalize()

        # Add special prefix if special metals were used
        if has_special_metal:
            if xp_multiplier > 1.0:
                prefix = "tErRoR " + prefix
            elif poison_damage > 0:
                prefix = "Venomous " + prefix
            elif slow_percent > 0:
                prefix = "Frozen " + prefix
            elif weaken_percent > 0:
                prefix = "Crippling " + prefix
            elif curse_percent > 0:
                prefix = "Cursed " + prefix
            elif attack_speed_mult > 1.0:
                prefix = "Chrono " + prefix
            elif health_bonus > 0 and speed_bonus > 0:
                prefix = "Empowered " + prefix
            elif health_bonus > 0:
                prefix = "Vital " + prefix
            elif speed_bonus > 0:
                prefix = "Swift " + prefix

        new_item = {
            'name': f"{prefix} {weapon_name}",
            'type': 'weapon',
            'weapon_type': weapon_type,
            'damage': base_damage,
            'rarity': tier_rarities.get(max_tier, 'common'),
            'color': tier_colors.get(max_tier, color.gray),
            'crafted': True
        }

        # Apply special metal bonuses
        if has_special_metal:
            new_item['rarity'] = 'legendary'  # Upgrade rarity if special metals used

        if health_bonus > 0:
            new_item['health_bonus'] = health_bonus
        if speed_bonus > 0:
            new_item['speed_bonus'] = speed_bonus
        if attack_speed_mult > 1.0:
            new_item['attack_speed_mult'] = attack_speed_mult  # Stacks! 2x * 2x = 4x
        if xp_multiplier > 1.0:
            new_item['xp_multiplier'] = xp_multiplier  # 4x XP from tErRoR ingot!
        if poison_damage > 0:
            new_item['poison_damage'] = poison_damage  # Damage per second
        if slow_percent > 0:
            new_item['slow_percent'] = slow_percent  # Slows enemy movement
        if weaken_percent > 0:
            new_item['weaken_percent'] = weaken_percent  # Reduces enemy damage
        if curse_percent > 0:
            new_item['curse_percent'] = curse_percent  # Enemy takes more damage

        if weapon_type == 'bow':
            new_item['range'] = 15 + total_tier * 2

        return new_item

    def close_crafting_ui(self):
        """Close the crafting interface."""
        self.crafting_open = False
        mouse.locked = True
        for ui in self.crafting_ui:
            destroy(ui)
        self.crafting_ui = []
        self.craft_slots = [None, None, None, None, None]

    def show_dialogue(self, npc_name, dialogue_lines):
        """Show dialogue UI."""
        self.dialogue_open = True
        self.dialogue_ui = []
        self.dialogue_lines = dialogue_lines
        self.dialogue_index = 0
        mouse.locked = False

        bg = Entity(parent=camera.ui, model='quad', texture='white_cube',
                    color=color.black90, scale=(1.4, 0.35), position=(0, -0.25), z=0.1)
        self.dialogue_ui.append(bg)

        # NPC portrait placeholder
        portrait = Entity(parent=camera.ui, model='quad', texture='white_cube',
                          color=color.dark_gray, scale=(0.15, 0.25), position=(-0.55, -0.25))
        self.dialogue_ui.append(portrait)

        name_text = Text(text=npc_name, position=(-0.4, -0.10), scale=1.8, color=color.yellow)
        self.dialogue_ui.append(name_text)

        self.dialogue_text = Text(text=dialogue_lines[0], position=(-0.4, -0.20),
                                   scale=1.1, color=color.white, wordwrap=50)
        self.dialogue_ui.append(self.dialogue_text)

        self.continue_prompt = Text(text='[SPACE] Continue | [ESC] Close',
                                     position=(0.4, -0.38), scale=0.9, color=color.light_gray)
        self.dialogue_ui.append(self.continue_prompt)

    def advance_dialogue(self):
        self.dialogue_index += 1
        if self.dialogue_index >= len(self.dialogue_lines):
            self.close_dialogue()
        else:
            self.dialogue_text.text = self.dialogue_lines[self.dialogue_index]

    def close_dialogue(self):
        self.dialogue_open = False
        mouse.locked = True
        for ui in self.dialogue_ui:
            destroy(ui)
        self.dialogue_ui = []

    def interact_with_npc(self):
        if not self.player:
            return

        # Check for chest first
        if self.interact_with_chest():
            return

        if hasattr(self, 'village_elder') and distance(self.player, self.village_elder) < 4:
            self.show_dialogue('Village Elder', [
                "Welcome to our village, adventurer!",
                "The wilderness beyond these walls is dangerous.",
                "Use the portals near the walls to travel to different areas.",
                "Wolves roam the northeast, Slimes infest the southwest.",
                "Goblins lurk in the northwest, and Skeletons haunt the southeast.",
                "Choose a pet from the book and train it well!"
            ])
            return

        if hasattr(self, 'merchant') and distance(self.player, self.merchant) < 4:
            self.show_dialogue('Merchant', [
                "Welcome to my shop!",
                "I sell potions, weapons, and armor.",
                "(Shop system coming soon!)"
            ])
            return

        if hasattr(self, 'pet_trainer') and distance(self.player, self.pet_trainer) < 4:
            self.show_trainer_menu()
            return

        if hasattr(self, 'blacksmith') and distance(self.player, self.blacksmith) < 4:
            self.show_dialogue('Blacksmith', [
                "Need something forged?",
                "Use the Smelting Furnace to smelt ores into ingots.",
                "Then use the Crafting Anvil to forge your weapons!"
            ])
            return

        # Smelting station interaction
        if hasattr(self, 'smelting_station') and distance(self.player, self.smelting_station) < 4:
            self.open_smelting_ui()
            return

        # Crafting station interaction
        if hasattr(self, 'crafting_station') and distance(self.player, self.crafting_station) < 4:
            self.open_crafting_ui()
            return

        # Dream mode portal interaction - escape back to normal world
        if self.dream_mode and hasattr(self, 'dream_portal') and self.dream_portal and distance(self.player, self.dream_portal) < 5:
            self.add_chat_message("You found the hidden portal! It whispers of escape...", color.rgb(150, 0, 200))
            self.add_chat_message("Press E again to return to the light...", color.rgb(100, 0, 150))
            self.add_chat_message("(This would reload the game in normal mode)", color.gray)
            return

        if hasattr(self, 'guard') and distance(self.player, self.guard) < 4:
            self.show_dialogue('Guard', [
                "Halt! Beyond this gate lies danger.",
                "Use the portals to travel safely to different regions.",
                "Each area has different enemies - be prepared!"
            ])
            return

    def load_game(self):
        print("Save system not yet implemented, starting new game...")
        self.show_character_creator()

    def quit_game(self):
        application.quit()

    def run(self):
        self.app.run()


# Global game instance
game_instance = None


def update():
    global game_instance
    if not game_instance or not game_instance.game_active:
        return

    # Update attack cooldown
    if game_instance.attack_cooldown > 0:
        game_instance.attack_cooldown -= time.dt

    # Check dungeon waves
    game_instance.check_dungeon_wave()
    
    # Check enemy respawn outside dungeons
    game_instance.check_enemy_respawn()
    
    # ERROR 404 MODE: Error debuff - teleport enemies away when too close
    if game_instance.error404_mode and game_instance.player:
        game_instance.error_debuff_cooldown -= time.dt
        if game_instance.error_debuff_cooldown <= 0:
            for enemy in game_instance.enemies[:]:
                if enemy.health <= 0:
                    continue
                dist = distance(game_instance.player, enemy)
                if dist < 10:  # Enemy too close
                    # Teleport enemy away randomly
                    import random
                    angle = random.uniform(0, 360)
                    teleport_dist = random.uniform(30, 50)
                    import math
                    new_x = game_instance.player.x + teleport_dist * math.cos(math.radians(angle))
                    new_z = game_instance.player.z + teleport_dist * math.sin(math.radians(angle))
                    enemy.position = Vec3(new_x, 0.75, new_z)
                    
                    # Apply 100 damage to player
                    game_instance.character.health -= 100
                    game_instance.add_chat_message("ERROR DEBUFF: -100 HP! Enemy teleported!", color.rgb(255, 0, 255))
                    
                    # Reset cooldown
                    game_instance.error_debuff_cooldown = 2.0  # 2 second cooldown between teleports
                    break

    if held_keys['left mouse'] and game_instance.player:
        # Pet book interaction
        if hasattr(game_instance, 'pet_book') and not game_instance.pet:
            if distance(game_instance.player, game_instance.pet_book) < 3:
                if not game_instance.pet_book_open:
                    game_instance.open_pet_book()
                return

        # Training mode
        if game_instance.training_skill == 'pending':
            for enemy in game_instance.enemies[:]:
                if enemy.health <= 0:
                    continue
                if distance(game_instance.player, enemy) < 4:
                    game_instance.complete_training('Attack')
                    break

        # Combat with weapon swing
        if game_instance.attack_cooldown <= 0:
            weapon_type = None
            if game_instance.equipped_weapon:
                weapon_type = game_instance.equipped_weapon.get('weapon_type')

            # Bow - ranged attack
            if weapon_type == 'bow':
                game_instance.shoot_arrow()
            # Staff - fire piercing projectile
            elif weapon_type == 'staff':
                game_instance.shoot_staff_projectile()
            else:
                # Melee attack
                attack_range = 3
                if weapon_type == 'dagger':
                    attack_range = 2.5  # Shorter range
                elif weapon_type == 'staff' or weapon_type == 'healing_staff':
                    attack_range = 3.5  # Slightly longer

                # Swing weapon animation first
                game_instance.swing_weapon()
                
                # ERROR 404 mode: Release terror bullets on attack
                if game_instance.error404_mode:
                    game_instance.shoot_terror_bullets()

                hit_enemy = False
                for enemy in game_instance.enemies[:]:
                    if enemy.health <= 0:
                        continue
                    if distance(game_instance.player, enemy) < attack_range:
                        # Save enemy data before take_damage (which can destroy it)
                        enemy_name = enemy.enemy_name
                        enemy_pos = Vec3(enemy.position)
                        enemy_xp = enemy.xp_value
                        
                        # Calculate damage from character + weapon
                        base_damage = game_instance.character.get_attack_power()
                        weapon_damage = 0
                        if game_instance.equipped_weapon:
                            weapon_damage = game_instance.equipped_weapon.get('damage', 0)
                        total_damage = base_damage + weapon_damage
                        
                        # ERROR 404 mode: 5x damage bonus
                        if game_instance.error404_mode:
                            total_damage *= 5.0

                        enemy.take_damage(total_damage)
                        game_instance.add_chat_message(f"Hit {enemy_name}! (-{int(total_damage)} HP)", color.orange)
                        hit_enemy = True

                        # Apply weapon debuffs from special metals
                        if game_instance.equipped_weapon:
                            poison_dmg = game_instance.equipped_weapon.get('poison_damage', 0)
                            slow_pct = game_instance.equipped_weapon.get('slow_percent', 0)
                            weaken_pct = game_instance.equipped_weapon.get('weaken_percent', 0)
                            curse_pct = game_instance.equipped_weapon.get('curse_percent', 0)
                            if poison_dmg or slow_pct or weaken_pct or curse_pct:
                                if enemy.health > 0:  # Only apply if enemy still alive
                                    enemy.apply_debuffs(poison=poison_dmg, slow=slow_pct, weaken=weaken_pct, curse=curse_pct, duration=5)
                                    debuff_msg = []
                                    if poison_dmg: debuff_msg.append("Poisoned")
                                    if slow_pct: debuff_msg.append("Slowed")
                                    if weaken_pct: debuff_msg.append("Weakened")
                                    if curse_pct: debuff_msg.append("Cursed")
                                    game_instance.add_chat_message(f"{enemy_name} {', '.join(debuff_msg)}!", color.magenta)

                        if enemy.health <= 0:
                            game_instance.character.gain_experience(enemy_xp)
                            game_instance.drop_enemy_loot(enemy_name, enemy_pos)
                            if enemy in game_instance.enemies:
                                game_instance.enemies.remove(enemy)
                            game_instance.add_chat_message(f"{enemy_name} defeated! +{enemy_xp} XP", color.yellow)
                        break  # Only hit one enemy per attack


def input(key):
    global game_instance
    if not game_instance:
        return

    # Teach minigame
    if game_instance.teach_active:
        if key == 'space':
            game_instance.check_teach_timing()
        elif key == 'escape':
            game_instance.close_teach_minigame()
        return

    # Pet book
    if game_instance.pet_book_open:
        if key == 'left mouse':
            game_instance.pet_book_selection = (game_instance.pet_book_selection + 1) % len(game_instance.available_pets)
            game_instance.update_pet_book_display()
        elif key == 'right mouse':
            game_instance.select_pet()
        elif key == 'escape':
            game_instance.close_pet_book()
        return

    # Training menu
    if game_instance.training_active:
        if key == '1':
            game_instance.start_train_mode()
        elif key == '2':
            game_instance.start_teach_minigame()
        elif key == 'escape':
            game_instance.close_trainer_menu()
        return

    # Training mode
    if game_instance.training_skill == 'pending':
        if key == 'escape':
            game_instance.training_skill = None
            if hasattr(game_instance, 'train_instruction'):
                destroy(game_instance.train_instruction)
        elif key == 'space':
            game_instance.complete_training('Dodge')
        return

    # Dialogue
    if game_instance.game_active and game_instance.dialogue_open:
        if key == 'space':
            game_instance.advance_dialogue()
        elif key == 'escape':
            game_instance.close_dialogue()
        return

    # Inventory
    if key == 'i' and game_instance.game_active:
        game_instance.toggle_inventory()
        return

    if game_instance.game_active and game_instance.inventory_open:
        if key == 'escape':
            game_instance.close_inventory()
        return

    # Smelting UI
    if game_instance.game_active and game_instance.smelting_open:
        if key == 'escape':
            game_instance.close_smelting_ui()
        return

    # Crafting UI
    if game_instance.game_active and game_instance.crafting_open:
        if key == 'escape':
            game_instance.close_crafting_ui()
        return

    # ESC
    if key == 'escape':
        # Exit dungeon if in one
        if game_instance.in_dungeon:
            game_instance.exit_dungeon()
            mouse.locked = True
        elif mouse.locked:
            mouse.locked = False
        else:
            if game_instance.game_active:
                mouse.locked = True

    # Interact
    if key == 'e' and game_instance.game_active:
        # Check for secret base return portal
        if game_instance.in_secret_dungeon and hasattr(game_instance, 'secret_base_portal') and game_instance.secret_base_portal:
            if distance(game_instance.player, game_instance.secret_base_portal) < 4:
                game_instance.return_to_secret_dungeon()
                return
        
        # Check for secret base return portal
        if game_instance.in_secret_dungeon and hasattr(game_instance, 'secret_base_portal') and game_instance.secret_base_portal:
            if distance(game_instance.player, game_instance.secret_base_portal) < 4:
                game_instance.return_to_secret_dungeon()
                return
        
        # Check for nearby regular portal first
        nearby_portal = game_instance.check_portal_interaction()
        if nearby_portal and nearby_portal.cooldown <= 0:
            nearby_portal.cooldown = 1.0  # Prevent spam
            game_instance.enter_dungeon(nearby_portal.dungeon_level)
        else:
            # Check for secret dungeon portal
            secret_portal = game_instance.check_secret_portal_interaction()
            if secret_portal and secret_portal.cooldown <= 0:
                secret_portal.cooldown = 1.0
                game_instance.enter_secret_dungeon(secret_portal.biome_name, secret_portal.difficulty)
            else:
                game_instance.interact_with_npc()
    
    # F key - Secret base anvil interaction
    if key == 'f' and game_instance.game_active:
        if game_instance.in_secret_dungeon and hasattr(game_instance, 'secret_base_anvil') and game_instance.secret_base_anvil:
            if distance(game_instance.player, game_instance.secret_base_anvil) < 4:
                game_instance.open_secret_anvil_crafting()

    # Right click - healing staff heal self
    if key == 'right mouse' and game_instance.game_active:
        if game_instance.equipped_weapon:
            weapon_type = game_instance.equipped_weapon.get('weapon_type')
            if weapon_type == 'healing_staff':
                game_instance.use_healing_staff()

    # Hotbar
    if game_instance.game_active:
        for i in range(8):
            if key == str(i + 1):
                game_instance.selected_hotbar = i
                game_instance.update_hotbar_selection()
                game_instance.use_hotbar_item(i)


if __name__ == '__main__':
    game_instance = Game()
    game_instance.run()
