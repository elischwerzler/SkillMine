"""Character stats and customization system."""

import config


class Character:
    """Represents a player character with stats, class, and race."""

    def __init__(self, name, race='human', char_class='warrior', dream_mode=False):
        self.name = name
        self.race = race
        self.char_class = char_class
        self.dream_mode = dream_mode

        # Level and experience
        self.level = 1
        self.experience = 0
        self.exp_to_next_level = 100

        # Calculate base stats from race and class
        self.base_stats = self._calculate_base_stats()

        # Current stats (modified by equipment, buffs, etc.)
        self.stats = self.base_stats.copy()

        # Derived stats
        self.max_health = config.BASE_HEALTH + (self.stats['vitality'] * 5)  # 5 HP per vitality
        self.max_mana = config.BASE_MANA + (self.stats['intelligence'] * 5)
        self.max_stamina = config.BASE_STAMINA + (self.stats['agility'] * 3)

        # Current values
        self.health = self.max_health
        self.mana = self.max_mana
        self.stamina = self.max_stamina

        # Abilities
        self.abilities = self._get_class_abilities()
        self.unlocked_abilities = [self.abilities[0]] if self.abilities else []

        # Skill points for leveling
        self.skill_points = 0
        self.stat_points = 0

        # Equipment slots
        self.equipment = {
            'head': None,
            'chest': None,
            'legs': None,
            'feet': None,
            'main_hand': None,
            'off_hand': None,
            'accessory': None
        }

        # Inventory
        self.inventory = []
        self.max_inventory_size = 20
        self.gold = 0

    def _calculate_base_stats(self):
        """Calculate base stats from race and class."""
        stats = {'strength': 10, 'agility': 10, 'intelligence': 10, 'vitality': 10}

        # Add class base stats
        if self.char_class in config.CLASSES:
            class_stats = config.CLASSES[self.char_class]['base_stats']
            for stat, value in class_stats.items():
                stats[stat] = value

        # Add race bonuses
        if self.race in config.RACES:
            race_bonuses = config.RACES[self.race]['stat_bonuses']
            for stat, bonus in race_bonuses.items():
                stats[stat] += bonus
        
        # Dream Mode bonus: +4 to all stats
        if self.dream_mode:
            for stat in stats:
                stats[stat] += 4

        return stats

    def _get_class_abilities(self):
        """Get abilities for the character's class."""
        if self.char_class in config.CLASSES:
            return config.CLASSES[self.char_class]['abilities']
        return []

    def gain_experience(self, amount):
        """Add experience and handle leveling up."""
        self.experience += amount
        leveled_up = False

        while self.experience >= self.exp_to_next_level:
            self.experience -= self.exp_to_next_level
            self.level_up()
            leveled_up = True

        return leveled_up

    def level_up(self):
        """Level up the character."""
        self.level += 1
        self.exp_to_next_level = int(self.exp_to_next_level * 1.5)

        # Grant stat and skill points
        self.stat_points += 3
        self.skill_points += 1

        # Add +2 to every stat on level up
        for stat in self.stats:
            self.stats[stat] += 2
            self.base_stats[stat] += 2

        # Increase max values (also scales with new vitality/intelligence/agility)
        self.max_health += 10 + 10  # Extra from +2 vitality
        self.max_mana += 5 + 10     # Extra from +2 intelligence
        self.max_stamina += 5 + 6   # Extra from +2 agility

        # Restore to full
        self.health = self.max_health
        self.mana = self.max_mana
        self.stamina = self.max_stamina

        # Unlock new ability every 3 levels
        if self.level % 3 == 0:
            ability_index = self.level // 3
            if ability_index < len(self.abilities):
                self.unlocked_abilities.append(self.abilities[ability_index])

        print(f"{self.name} reached level {self.level}!")

    def allocate_stat_point(self, stat_name):
        """Allocate a stat point to a specific stat."""
        if self.stat_points > 0 and stat_name in self.stats:
            self.stats[stat_name] += 1
            self.stat_points -= 1
            self._recalculate_derived_stats()
            return True
        return False

    def _recalculate_derived_stats(self):
        """Recalculate derived stats based on current stats."""
        self.max_health = config.BASE_HEALTH + (self.stats['vitality'] * 5) + (self.level * 5)
        self.max_mana = config.BASE_MANA + (self.stats['intelligence'] * 5) + (self.level * 5)
        self.max_stamina = config.BASE_STAMINA + (self.stats['agility'] * 3) + (self.level * 5)

    def take_damage(self, amount):
        """Take damage, returns True if character dies."""
        # Calculate damage reduction from stats
        damage_reduction = self.stats['vitality'] * 0.5
        actual_damage = max(1, amount - damage_reduction)

        self.health -= actual_damage

        if self.health <= 0:
            self.health = 0
            return True
        return False

    def heal(self, amount):
        """Heal the character."""
        self.health = min(self.max_health, self.health + amount)

    def use_mana(self, amount):
        """Use mana, returns False if not enough mana."""
        if self.mana >= amount:
            self.mana -= amount
            return True
        return False

    def use_stamina(self, amount):
        """Use stamina, returns False if not enough stamina."""
        if self.stamina >= amount:
            self.stamina -= amount
            return True
        return False

    def regenerate(self, dt):
        """Regenerate health, mana, and stamina over time."""
        # Stamina regenerates fastest
        self.stamina = min(self.max_stamina, self.stamina + (5 * dt))

        # Mana regenerates based on intelligence
        mana_regen = (1 + self.stats['intelligence'] * 0.1) * dt
        self.mana = min(self.max_mana, self.mana + mana_regen)

        # Health regenerates very slowly - only out of combat really matters
        health_regen = (0.1 + self.stats['vitality'] * 0.01) * dt
        self.health = min(self.max_health, self.health + health_regen)

    def add_to_inventory(self, item):
        """Add an item to inventory."""
        if len(self.inventory) < self.max_inventory_size:
            self.inventory.append(item)
            return True
        return False

    def remove_from_inventory(self, item):
        """Remove an item from inventory."""
        if item in self.inventory:
            self.inventory.remove(item)
            return True
        return False

    def equip_item(self, item, slot):
        """Equip an item to a slot."""
        if slot in self.equipment:
            # Unequip current item if any
            old_item = self.equipment[slot]
            if old_item:
                self.add_to_inventory(old_item)

            self.equipment[slot] = item
            self.remove_from_inventory(item)
            return True
        return False

    def get_attack_power(self):
        """Calculate total attack power."""
        base_attack = self.stats['strength'] * 2

        # Add weapon damage if equipped
        weapon = self.equipment.get('main_hand')
        if weapon and hasattr(weapon, 'damage'):
            base_attack += weapon.damage

        return base_attack

    def get_magic_power(self):
        """Calculate total magic power."""
        return self.stats['intelligence'] * 3

    def get_defense(self):
        """Calculate total defense."""
        base_defense = self.stats['vitality']

        # Add armor defense
        for slot in ['head', 'chest', 'legs', 'feet']:
            armor = self.equipment.get(slot)
            if armor and hasattr(armor, 'defense'):
                base_defense += armor.defense

        return base_defense

    def to_dict(self):
        """Convert character to dictionary for saving."""
        return {
            'name': self.name,
            'race': self.race,
            'char_class': self.char_class,
            'level': self.level,
            'experience': self.experience,
            'stats': self.stats,
            'health': self.health,
            'mana': self.mana,
            'stamina': self.stamina,
            'skill_points': self.skill_points,
            'stat_points': self.stat_points,
            'gold': self.gold,
            'unlocked_abilities': self.unlocked_abilities
        }

    @classmethod
    def from_dict(cls, data):
        """Create character from saved dictionary."""
        char = cls(data['name'], data['race'], data['char_class'])
        char.level = data['level']
        char.experience = data['experience']
        char.stats = data['stats']
        char.health = data['health']
        char.mana = data['mana']
        char.stamina = data['stamina']
        char.skill_points = data['skill_points']
        char.stat_points = data['stat_points']
        char.gold = data['gold']
        char.unlocked_abilities = data['unlocked_abilities']
        char._recalculate_derived_stats()
        return char
