"""Inventory system for managing items."""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from enum import Enum


class ItemType(Enum):
    WEAPON = "weapon"
    ARMOR = "armor"
    CONSUMABLE = "consumable"
    MATERIAL = "material"
    QUEST = "quest"
    MISC = "misc"


class ItemRarity(Enum):
    COMMON = ("common", (200, 200, 200))
    UNCOMMON = ("uncommon", (100, 255, 100))
    RARE = ("rare", (100, 150, 255))
    EPIC = ("epic", (200, 100, 255))
    LEGENDARY = ("legendary", (255, 200, 50))


@dataclass
class Item:
    """Base item class."""
    id: str
    name: str
    description: str
    item_type: ItemType
    rarity: ItemRarity = ItemRarity.COMMON
    stack_size: int = 1
    max_stack: int = 99
    value: int = 0  # Gold value
    icon: str = "default"

    # Equipment stats (for weapons/armor)
    attack: int = 0
    defense: int = 0
    stat_bonuses: Dict[str, int] = field(default_factory=dict)

    # Consumable effects
    heal_amount: int = 0
    mana_restore: int = 0
    buff_type: str = ""
    buff_duration: float = 0

    def is_equipment(self) -> bool:
        return self.item_type in [ItemType.WEAPON, ItemType.ARMOR]

    def is_consumable(self) -> bool:
        return self.item_type == ItemType.CONSUMABLE

    def is_stackable(self) -> bool:
        return self.max_stack > 1


# Item definitions
ITEMS = {
    # === WEAPONS ===
    'rusty_sword': Item(
        id='rusty_sword',
        name='Rusty Sword',
        description='An old, rusty sword. Better than nothing.',
        item_type=ItemType.WEAPON,
        rarity=ItemRarity.COMMON,
        max_stack=1,
        value=5,
        attack=5
    ),
    'old_sword': Item(
        id='old_sword',
        name='Old Sword',
        description='A well-used sword that still has some fight in it.',
        item_type=ItemType.WEAPON,
        rarity=ItemRarity.COMMON,
        max_stack=1,
        value=15,
        attack=8
    ),
    'iron_sword': Item(
        id='iron_sword',
        name='Iron Sword',
        description='A reliable iron sword.',
        item_type=ItemType.WEAPON,
        rarity=ItemRarity.UNCOMMON,
        max_stack=1,
        value=50,
        attack=15
    ),
    'steel_sword': Item(
        id='steel_sword',
        name='Steel Sword',
        description='A finely crafted steel blade.',
        item_type=ItemType.WEAPON,
        rarity=ItemRarity.RARE,
        max_stack=1,
        value=150,
        attack=25,
        stat_bonuses={'strength': 2}
    ),
    'flame_blade': Item(
        id='flame_blade',
        name='Flame Blade',
        description='A sword imbued with the power of fire.',
        item_type=ItemType.WEAPON,
        rarity=ItemRarity.EPIC,
        max_stack=1,
        value=500,
        attack=35,
        stat_bonuses={'strength': 3, 'intelligence': 2}
    ),

    # === ARMOR ===
    'cloth_armor': Item(
        id='cloth_armor',
        name='Cloth Armor',
        description='Basic cloth protection.',
        item_type=ItemType.ARMOR,
        rarity=ItemRarity.COMMON,
        max_stack=1,
        value=10,
        defense=3
    ),
    'leather_armor': Item(
        id='leather_armor',
        name='Leather Armor',
        description='Sturdy leather armor.',
        item_type=ItemType.ARMOR,
        rarity=ItemRarity.UNCOMMON,
        max_stack=1,
        value=40,
        defense=8
    ),
    'chainmail': Item(
        id='chainmail',
        name='Chainmail',
        description='Linked metal rings provide good protection.',
        item_type=ItemType.ARMOR,
        rarity=ItemRarity.RARE,
        max_stack=1,
        value=120,
        defense=15,
        stat_bonuses={'vitality': 2}
    ),

    # === CONSUMABLES ===
    'health_potion': Item(
        id='health_potion',
        name='Health Potion',
        description='Restores 50 health.',
        item_type=ItemType.CONSUMABLE,
        rarity=ItemRarity.COMMON,
        max_stack=20,
        value=25,
        heal_amount=50
    ),
    'greater_health_potion': Item(
        id='greater_health_potion',
        name='Greater Health Potion',
        description='Restores 150 health.',
        item_type=ItemType.CONSUMABLE,
        rarity=ItemRarity.UNCOMMON,
        max_stack=10,
        value=75,
        heal_amount=150
    ),
    'mana_potion': Item(
        id='mana_potion',
        name='Mana Potion',
        description='Restores 30 mana.',
        item_type=ItemType.CONSUMABLE,
        rarity=ItemRarity.COMMON,
        max_stack=20,
        value=30,
        mana_restore=30
    ),
    'stamina_elixir': Item(
        id='stamina_elixir',
        name='Stamina Elixir',
        description='Restores stamina and boosts regeneration.',
        item_type=ItemType.CONSUMABLE,
        rarity=ItemRarity.UNCOMMON,
        max_stack=10,
        value=40,
        buff_type='stamina_regen',
        buff_duration=60
    ),

    # === MATERIALS ===
    'wolf_pelt': Item(
        id='wolf_pelt',
        name='Wolf Pelt',
        description='A pelt from a wild wolf.',
        item_type=ItemType.MATERIAL,
        rarity=ItemRarity.COMMON,
        max_stack=50,
        value=5
    ),
    'wolf_fang': Item(
        id='wolf_fang',
        name='Wolf Fang',
        description='A sharp wolf fang.',
        item_type=ItemType.MATERIAL,
        rarity=ItemRarity.COMMON,
        max_stack=50,
        value=3
    ),
    'slime_gel': Item(
        id='slime_gel',
        name='Slime Gel',
        description='Gooey substance from a slime.',
        item_type=ItemType.MATERIAL,
        rarity=ItemRarity.COMMON,
        max_stack=50,
        value=2
    ),
    'healing_herb': Item(
        id='healing_herb',
        name='Healing Herb',
        description='A medicinal herb.',
        item_type=ItemType.MATERIAL,
        rarity=ItemRarity.COMMON,
        max_stack=50,
        value=3
    ),
    'bone': Item(
        id='bone',
        name='Bone',
        description='An old bone.',
        item_type=ItemType.MATERIAL,
        rarity=ItemRarity.COMMON,
        max_stack=50,
        value=2
    ),
    'ancient_coin': Item(
        id='ancient_coin',
        name='Ancient Coin',
        description='A coin from a forgotten era.',
        item_type=ItemType.MATERIAL,
        rarity=ItemRarity.RARE,
        max_stack=99,
        value=25
    ),

    # === QUEST ITEMS ===
    'elder_letter': Item(
        id='elder_letter',
        name="Elder's Letter",
        description='A sealed letter from the Village Elder.',
        item_type=ItemType.QUEST,
        rarity=ItemRarity.COMMON,
        max_stack=1,
        value=0
    ),
}


@dataclass
class InventorySlot:
    """A slot in the inventory containing an item and quantity."""
    item: Optional[Item] = None
    quantity: int = 0

    def is_empty(self) -> bool:
        return self.item is None or self.quantity <= 0

    def can_add(self, item: Item, amount: int = 1) -> bool:
        if self.is_empty():
            return True
        if self.item.id == item.id and item.is_stackable():
            return self.quantity + amount <= item.max_stack
        return False

    def add(self, item: Item, amount: int = 1) -> int:
        """Add items to slot. Returns overflow amount."""
        if self.is_empty():
            self.item = item
            self.quantity = min(amount, item.max_stack)
            return max(0, amount - item.max_stack)
        elif self.item.id == item.id and item.is_stackable():
            can_add = item.max_stack - self.quantity
            to_add = min(amount, can_add)
            self.quantity += to_add
            return amount - to_add
        return amount

    def remove(self, amount: int = 1) -> int:
        """Remove items from slot. Returns amount actually removed."""
        if self.is_empty():
            return 0
        removed = min(amount, self.quantity)
        self.quantity -= removed
        if self.quantity <= 0:
            self.item = None
            self.quantity = 0
        return removed


class Inventory:
    """Player inventory system."""

    def __init__(self, size: int = 30):
        self.size = size
        self.slots: List[InventorySlot] = [InventorySlot() for _ in range(size)]
        self.gold = 0

        # Equipment slots
        self.equipment: Dict[str, InventorySlot] = {
            'weapon': InventorySlot(),
            'armor': InventorySlot(),
            'helmet': InventorySlot(),
            'boots': InventorySlot(),
            'accessory': InventorySlot(),
        }

    def add_item(self, item_id: str, quantity: int = 1) -> bool:
        """Add an item to inventory by ID."""
        if item_id not in ITEMS:
            print(f"Unknown item: {item_id}")
            return False

        item = ITEMS[item_id]
        return self.add_item_object(item, quantity)

    def add_item_object(self, item: Item, quantity: int = 1) -> bool:
        """Add an item object to inventory."""
        remaining = quantity

        # Try to stack with existing items first
        if item.is_stackable():
            for slot in self.slots:
                if not slot.is_empty() and slot.item.id == item.id:
                    remaining = slot.add(item, remaining)
                    if remaining <= 0:
                        print(f"Added {quantity}x {item.name}")
                        return True

        # Find empty slots for remaining items
        while remaining > 0:
            empty_slot = self._find_empty_slot()
            if empty_slot is None:
                print(f"Inventory full! Could not add {remaining}x {item.name}")
                return False
            remaining = empty_slot.add(item, remaining)

        print(f"Added {quantity}x {item.name}")
        return True

    def remove_item(self, item_id: str, quantity: int = 1) -> bool:
        """Remove an item from inventory."""
        count = self.count_item(item_id)
        if count < quantity:
            return False

        remaining = quantity
        for slot in self.slots:
            if not slot.is_empty() and slot.item.id == item_id:
                removed = slot.remove(remaining)
                remaining -= removed
                if remaining <= 0:
                    break

        return True

    def count_item(self, item_id: str) -> int:
        """Count total quantity of an item in inventory."""
        total = 0
        for slot in self.slots:
            if not slot.is_empty() and slot.item.id == item_id:
                total += slot.quantity
        return total

    def has_item(self, item_id: str, quantity: int = 1) -> bool:
        """Check if inventory has enough of an item."""
        return self.count_item(item_id) >= quantity

    def _find_empty_slot(self) -> Optional[InventorySlot]:
        """Find first empty slot."""
        for slot in self.slots:
            if slot.is_empty():
                return slot
        return None

    def equip_item(self, slot_index: int) -> bool:
        """Equip an item from inventory."""
        if slot_index < 0 or slot_index >= len(self.slots):
            return False

        slot = self.slots[slot_index]
        if slot.is_empty():
            return False

        item = slot.item
        if not item.is_equipment():
            return False

        # Determine equipment slot
        equip_slot = 'weapon' if item.item_type == ItemType.WEAPON else 'armor'

        # Swap with currently equipped
        old_equip = self.equipment[equip_slot]
        self.equipment[equip_slot] = InventorySlot(item, 1)
        slot.remove(1)

        # Put old equipment back in inventory
        if not old_equip.is_empty():
            self.add_item_object(old_equip.item, 1)

        print(f"Equipped {item.name}")
        return True

    def unequip_item(self, equip_slot: str) -> bool:
        """Unequip an item to inventory."""
        if equip_slot not in self.equipment:
            return False

        slot = self.equipment[equip_slot]
        if slot.is_empty():
            return False

        if self._find_empty_slot() is None:
            print("Inventory full, cannot unequip!")
            return False

        self.add_item_object(slot.item, 1)
        self.equipment[equip_slot] = InventorySlot()
        return True

    def use_item(self, slot_index: int, character) -> bool:
        """Use an item from inventory."""
        if slot_index < 0 or slot_index >= len(self.slots):
            return False

        slot = self.slots[slot_index]
        if slot.is_empty():
            return False

        item = slot.item
        if not item.is_consumable():
            return False

        # Apply effects
        if item.heal_amount > 0:
            character.heal(item.heal_amount)
            print(f"Restored {item.heal_amount} health!")

        if item.mana_restore > 0:
            character.mana = min(character.max_mana, character.mana + item.mana_restore)
            print(f"Restored {item.mana_restore} mana!")

        # Remove item
        slot.remove(1)
        return True

    def add_gold(self, amount: int):
        """Add gold."""
        self.gold += amount
        print(f"+{amount} gold (Total: {self.gold})")

    def remove_gold(self, amount: int) -> bool:
        """Remove gold. Returns False if not enough."""
        if self.gold < amount:
            return False
        self.gold -= amount
        return True

    def get_equipped_stats(self) -> Dict[str, int]:
        """Get total stats from equipped items."""
        stats = {'attack': 0, 'defense': 0}
        stat_bonuses = {}

        for slot in self.equipment.values():
            if not slot.is_empty():
                stats['attack'] += slot.item.attack
                stats['defense'] += slot.item.defense
                for stat, bonus in slot.item.stat_bonuses.items():
                    stat_bonuses[stat] = stat_bonuses.get(stat, 0) + bonus

        return {**stats, 'bonuses': stat_bonuses}

    def get_items_by_type(self, item_type: ItemType) -> List[InventorySlot]:
        """Get all items of a specific type."""
        return [slot for slot in self.slots
                if not slot.is_empty() and slot.item.item_type == item_type]

    def to_dict(self) -> Dict:
        """Serialize inventory for saving."""
        slots_data = []
        for slot in self.slots:
            if slot.is_empty():
                slots_data.append(None)
            else:
                slots_data.append({
                    'item_id': slot.item.id,
                    'quantity': slot.quantity
                })

        equip_data = {}
        for slot_name, slot in self.equipment.items():
            if not slot.is_empty():
                equip_data[slot_name] = {
                    'item_id': slot.item.id,
                    'quantity': slot.quantity
                }

        return {
            'slots': slots_data,
            'equipment': equip_data,
            'gold': self.gold
        }

    def from_dict(self, data: Dict):
        """Restore inventory from saved data."""
        self.gold = data.get('gold', 0)

        for i, slot_data in enumerate(data.get('slots', [])):
            if i >= len(self.slots):
                break
            if slot_data and slot_data['item_id'] in ITEMS:
                self.slots[i] = InventorySlot(
                    ITEMS[slot_data['item_id']],
                    slot_data['quantity']
                )

        for slot_name, equip_data in data.get('equipment', {}).items():
            if slot_name in self.equipment and equip_data['item_id'] in ITEMS:
                self.equipment[slot_name] = InventorySlot(
                    ITEMS[equip_data['item_id']],
                    equip_data['quantity']
                )
