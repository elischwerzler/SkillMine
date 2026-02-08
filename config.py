# Game Configuration
GAME_TITLE = "SkillMine"
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
FULLSCREEN = False

# Player Settings
PLAYER_SPEED = 5
PLAYER_SPRINT_MULTIPLIER = 1.8
PLAYER_JUMP_HEIGHT = 2
MOUSE_SENSITIVITY = 40

# Combat Settings
BASE_HEALTH = 50  # Lower for more dangerous combat
BASE_MANA = 50
BASE_STAMINA = 100
ATTACK_COOLDOWN = 0.5

# World Settings
DAY_CYCLE_DURATION = 300  # seconds for full day/night cycle
GRAVITY = 1

# Character Classes
CLASSES = {
    'warrior': {
        'name': 'Warrior',
        'description': 'A mighty fighter skilled in melee combat',
        'base_stats': {'strength': 15, 'agility': 10, 'intelligence': 5, 'vitality': 12},
        'abilities': ['power_strike', 'shield_bash', 'battle_cry']
    },
    'mage': {
        'name': 'Mage',
        'description': 'A master of arcane arts and elemental magic',
        'base_stats': {'strength': 5, 'agility': 8, 'intelligence': 18, 'vitality': 8},
        'abilities': ['fireball', 'ice_shard', 'arcane_shield']
    },
    'ranger': {
        'name': 'Ranger',
        'description': 'A swift hunter with deadly precision',
        'base_stats': {'strength': 10, 'agility': 16, 'intelligence': 8, 'vitality': 10},
        'abilities': ['precise_shot', 'evasive_roll', 'trap']
    },
    'healer': {
        'name': 'Healer',
        'description': 'A devoted support who mends wounds and protects allies',
        'base_stats': {'strength': 6, 'agility': 8, 'intelligence': 14, 'vitality': 14},
        'abilities': ['heal', 'blessing', 'purify']
    }
}

# Races
RACES = {
    'human': {
        'name': 'Human',
        'description': 'Versatile and adaptable',
        'stat_bonuses': {'strength': 1, 'agility': 1, 'intelligence': 1, 'vitality': 1}
    },
    'elf': {
        'name': 'Elf',
        'description': 'Graceful and magically attuned',
        'stat_bonuses': {'strength': 0, 'agility': 2, 'intelligence': 2, 'vitality': 0}
    },
    'dwarf': {
        'name': 'Dwarf',
        'description': 'Sturdy and resilient',
        'stat_bonuses': {'strength': 2, 'agility': 0, 'intelligence': 0, 'vitality': 2}
    },
    'orc': {
        'name': 'Orc',
        'description': 'Powerful and fierce',
        'stat_bonuses': {'strength': 3, 'agility': 1, 'intelligence': -1, 'vitality': 1}
    }
}

# Starter Pets
STARTER_PETS = {
    'wolf': {
        'name': 'Shadow Wolf',
        'description': 'A loyal wolf companion that excels in combat',
        'type': 'combat',
        'base_stats': {'attack': 10, 'defense': 5, 'speed': 12},
        'abilities': ['bite', 'howl']
    },
    'owl': {
        'name': 'Mystic Owl',
        'description': 'A wise owl that reveals hidden secrets',
        'type': 'utility',
        'base_stats': {'attack': 5, 'defense': 3, 'speed': 15},
        'abilities': ['scout', 'detect_treasure']
    },
    'turtle': {
        'name': 'Guardian Turtle',
        'description': 'A sturdy turtle that provides protection',
        'type': 'defense',
        'base_stats': {'attack': 3, 'defense': 15, 'speed': 5},
        'abilities': ['shield', 'taunt']
    }
}
