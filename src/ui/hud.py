"""HUD (Heads-Up Display) for in-game UI."""

from ursina import *
from typing import Optional

from ..player.inventory import Inventory, ItemRarity


class GameHUD(Entity):
    """Main game HUD with all UI elements."""

    def __init__(self, character, inventory: Inventory):
        super().__init__(parent=camera.ui)
        self.character = character
        self.inventory = inventory

        # Create all HUD elements
        self._create_player_panel()
        self._create_resource_bars()
        self._create_exp_bar()
        self._create_minimap()
        self._create_hotbar()
        self._create_quest_tracker()
        self._create_combat_log()
        self._create_instructions()

    def _create_player_panel(self):
        """Create player info panel."""
        # Background
        self.player_panel_bg = Entity(
            parent=self,
            model='quad',
            color=color.rgba(0, 0, 0, 180),
            scale=(0.35, 0.14),
            position=(-0.72, 0.42)
        )

        # Name
        self.player_name = Text(
            parent=self,
            text=self.character.name,
            position=(-0.88, 0.47),
            scale=1.5,
            color=color.rgb(100, 200, 255)
        )

        # Level and class
        self.player_level = Text(
            parent=self,
            text=f'Lv.{self.character.level}',
            position=(-0.88, 0.44),
            scale=1,
            color=color.rgb(255, 220, 100)
        )

    def _create_resource_bars(self):
        """Create health, mana, and stamina bars."""
        bar_width = 0.28
        bar_start_x = -0.73
        bar_start_y = 0.40

        # Health bar
        self.health_bar_bg = Entity(
            parent=self,
            model='quad',
            color=color.rgb(60, 20, 20),
            scale=(bar_width, 0.022),
            position=(bar_start_x, bar_start_y)
        )
        self.health_bar = Entity(
            parent=self,
            model='quad',
            color=color.rgb(200, 50, 50),
            scale=(bar_width, 0.022),
            position=(bar_start_x, bar_start_y),
            origin=(-0.5, 0)
        )
        self.health_text = Text(
            parent=self,
            text='100/100',
            position=(bar_start_x, bar_start_y),
            origin=(0, 0),
            scale=0.7,
            color=color.white
        )

        # Mana bar
        self.mana_bar_bg = Entity(
            parent=self,
            model='quad',
            color=color.rgb(20, 20, 60),
            scale=(bar_width, 0.018),
            position=(bar_start_x, bar_start_y - 0.028)
        )
        self.mana_bar = Entity(
            parent=self,
            model='quad',
            color=color.rgb(50, 100, 200),
            scale=(bar_width, 0.018),
            position=(bar_start_x, bar_start_y - 0.028),
            origin=(-0.5, 0)
        )
        self.mana_text = Text(
            parent=self,
            text='50/50',
            position=(bar_start_x, bar_start_y - 0.028),
            origin=(0, 0),
            scale=0.6,
            color=color.white
        )

        # Stamina bar
        self.stamina_bar_bg = Entity(
            parent=self,
            model='quad',
            color=color.rgb(40, 40, 20),
            scale=(bar_width, 0.012),
            position=(bar_start_x, bar_start_y - 0.05)
        )
        self.stamina_bar = Entity(
            parent=self,
            model='quad',
            color=color.rgb(200, 180, 50),
            scale=(bar_width, 0.012),
            position=(bar_start_x, bar_start_y - 0.05),
            origin=(-0.5, 0)
        )

    def _create_exp_bar(self):
        """Create experience bar at bottom of screen."""
        self.exp_bar_bg = Entity(
            parent=self,
            model='quad',
            color=color.rgb(30, 30, 30),
            scale=(0.6, 0.012),
            position=(0, -0.47)
        )
        self.exp_bar = Entity(
            parent=self,
            model='quad',
            color=color.rgb(100, 50, 200),
            scale=(0, 0.012),
            position=(0, -0.47),
            origin=(-0.5, 0)
        )
        self.exp_text = Text(
            parent=self,
            text='0%',
            position=(0.32, -0.47),
            origin=(0, 0),
            scale=0.6,
            color=color.rgb(150, 100, 255)
        )

    def _create_minimap(self):
        """Create minimap in top-right corner."""
        # Minimap background
        self.minimap_bg = Entity(
            parent=self,
            model='quad',
            color=color.rgba(0, 0, 0, 180),
            scale=(0.2, 0.2),
            position=(0.78, 0.38)
        )

        # Minimap border
        self.minimap_border = Entity(
            parent=self,
            model='quad',
            color=color.rgb(80, 80, 100),
            scale=(0.21, 0.21),
            position=(0.78, 0.38),
            z=0.01
        )

        # Player marker
        self.minimap_player = Entity(
            parent=self,
            model='quad',
            color=color.rgb(100, 200, 255),
            scale=(0.015, 0.015),
            position=(0.78, 0.38)
        )

        # Compass directions
        Text(parent=self, text='N', position=(0.78, 0.49), origin=(0, 0), scale=0.7, color=color.white)
        Text(parent=self, text='S', position=(0.78, 0.27), origin=(0, 0), scale=0.7, color=color.white)
        Text(parent=self, text='E', position=(0.89, 0.38), origin=(0, 0), scale=0.7, color=color.white)
        Text(parent=self, text='W', position=(0.67, 0.38), origin=(0, 0), scale=0.7, color=color.white)

    def _create_hotbar(self):
        """Create ability/item hotbar."""
        self.hotbar_slots = []
        slot_size = 0.06
        start_x = -0.18
        y = -0.38

        for i in range(6):
            # Slot background
            slot_bg = Entity(
                parent=self,
                model='quad',
                color=color.rgb(40, 40, 50),
                scale=(slot_size, slot_size),
                position=(start_x + (i * (slot_size + 0.01)), y)
            )

            # Slot border
            slot_border = Entity(
                parent=self,
                model='quad',
                color=color.rgb(80, 80, 100),
                scale=(slot_size + 0.005, slot_size + 0.005),
                position=(start_x + (i * (slot_size + 0.01)), y),
                z=0.01
            )

            # Slot key number
            slot_key = Text(
                parent=self,
                text=str(i + 1),
                position=(start_x + (i * (slot_size + 0.01)) - 0.025, y + 0.025),
                scale=0.6,
                color=color.rgb(150, 150, 150)
            )

            self.hotbar_slots.append({
                'bg': slot_bg,
                'border': slot_border,
                'key': slot_key,
                'content': None
            })

    def _create_quest_tracker(self):
        """Create quest tracker panel."""
        # Background
        self.quest_tracker_bg = Entity(
            parent=self,
            model='quad',
            color=color.rgba(0, 0, 0, 150),
            scale=(0.3, 0.2),
            position=(0.72, 0.1)
        )

        # Title
        self.quest_tracker_title = Text(
            parent=self,
            text='Active Quests',
            position=(0.58, 0.18),
            scale=1,
            color=color.rgb(255, 220, 100)
        )

        # Quest entries (up to 3)
        self.quest_entries = []
        for i in range(3):
            entry = Text(
                parent=self,
                text='',
                position=(0.58, 0.12 - (i * 0.06)),
                scale=0.8,
                color=color.white,
                wordwrap=25
            )
            self.quest_entries.append(entry)

    def _create_combat_log(self):
        """Create combat log panel."""
        # Background
        self.combat_log_bg = Entity(
            parent=self,
            model='quad',
            color=color.rgba(0, 0, 0, 100),
            scale=(0.35, 0.15),
            position=(-0.72, -0.1),
            visible=False
        )

        # Log entries
        self.combat_log_entries = []
        for i in range(5):
            entry = Text(
                parent=self,
                text='',
                position=(-0.88, -0.03 - (i * 0.025)),
                scale=0.7,
                color=color.rgb(200, 200, 200),
                visible=False
            )
            self.combat_log_entries.append(entry)

    def _create_instructions(self):
        """Create control instructions."""
        self.instructions = Text(
            parent=self,
            text='WASD: Move | SPACE: Jump | SHIFT: Sprint | V: Camera | E: Interact | I: Inventory | Q: Quests | TAB: Stats',
            position=(0, -0.43),
            origin=(0, 0),
            scale=0.7,
            color=color.rgb(150, 150, 150)
        )

    def update(self):
        """Update HUD values."""
        # Update health bar
        health_ratio = self.character.health / self.character.max_health
        self.health_bar.scale_x = 0.28 * health_ratio
        self.health_text.text = f'{int(self.character.health)}/{int(self.character.max_health)}'

        # Update mana bar
        mana_ratio = self.character.mana / self.character.max_mana
        self.mana_bar.scale_x = 0.28 * mana_ratio
        self.mana_text.text = f'{int(self.character.mana)}/{int(self.character.max_mana)}'

        # Update stamina bar
        stamina_ratio = self.character.stamina / self.character.max_stamina
        self.stamina_bar.scale_x = 0.28 * stamina_ratio

        # Update exp bar
        exp_ratio = self.character.experience / self.character.exp_to_next_level
        self.exp_bar.scale_x = 0.6 * exp_ratio
        self.exp_text.text = f'{int(exp_ratio * 100)}%'

        # Update level display
        self.player_level.text = f'Lv.{self.character.level}'

    def update_quest_tracker(self, quests):
        """Update quest tracker with active quests."""
        for i, entry in enumerate(self.quest_entries):
            if i < len(quests):
                quest = quests[i]
                # Show first incomplete objective
                for obj in quest.objectives:
                    if not obj.is_complete():
                        entry.text = f"• {quest.name}\n  {obj.description}: {obj.current_count}/{obj.required_count}"
                        break
            else:
                entry.text = ''

    def add_combat_log(self, message: str):
        """Add message to combat log."""
        self.combat_log_bg.visible = True

        # Shift existing entries up
        for i in range(len(self.combat_log_entries) - 1, 0, -1):
            self.combat_log_entries[i].text = self.combat_log_entries[i - 1].text

        self.combat_log_entries[0].text = message
        self.combat_log_entries[0].visible = True

        # Hide after 5 seconds of no new messages
        invoke(self._fade_combat_log, delay=5.0)

    def _fade_combat_log(self):
        """Fade out combat log."""
        # Check if any recent messages
        self.combat_log_bg.visible = False
        for entry in self.combat_log_entries:
            entry.visible = False

    def show_damage_number(self, position, amount, is_crit=False):
        """Show floating damage number."""
        damage_text = Text(
            text=str(int(amount)),
            position=position,
            scale=1.5 if is_crit else 1,
            color=color.rgb(255, 100, 100) if is_crit else color.rgb(255, 200, 200),
            origin=(0, 0)
        )

        # Animate and destroy
        damage_text.animate_y(damage_text.y + 0.1, duration=0.5)
        damage_text.animate_color(color.rgba(255, 255, 255, 0), duration=0.5)
        destroy(damage_text, delay=0.5)


class InventoryUI(Entity):
    """Inventory screen UI."""

    def __init__(self, inventory: Inventory, character, on_close):
        super().__init__(parent=camera.ui)
        self.inventory = inventory
        self.character = character
        self.on_close = on_close
        self.selected_slot = None

        self._create_ui()

    def _create_ui(self):
        """Create inventory UI."""
        # Background overlay
        self.overlay = Entity(
            parent=self,
            model='quad',
            color=color.rgba(0, 0, 0, 200),
            scale=(2, 2)
        )

        # Main panel
        self.panel = Entity(
            parent=self,
            model='quad',
            color=color.rgb(40, 40, 50),
            scale=(0.8, 0.7)
        )

        # Title
        self.title = Text(
            parent=self,
            text='INVENTORY',
            position=(0, 0.3),
            origin=(0, 0),
            scale=2,
            color=color.rgb(255, 220, 100)
        )

        # Gold display
        self.gold_text = Text(
            parent=self,
            text=f'Gold: {self.inventory.gold}',
            position=(-0.35, 0.25),
            scale=1.2,
            color=color.rgb(255, 215, 0)
        )

        # Equipment panel
        self._create_equipment_panel()

        # Inventory grid
        self._create_inventory_grid()

        # Item info panel
        self._create_info_panel()

        # Close button
        self.close_btn = Button(
            parent=self,
            text='X',
            scale=(0.05, 0.05),
            position=(0.37, 0.32),
            color=color.rgb(150, 50, 50),
            on_click=self.close
        )

    def _create_equipment_panel(self):
        """Create equipment slots panel."""
        equip_x = -0.3
        equip_y = 0.1

        Text(parent=self, text='Equipment', position=(equip_x, equip_y + 0.1),
             scale=1, color=color.rgb(200, 200, 200))

        self.equip_slots = {}
        slot_labels = ['Weapon', 'Armor', 'Helmet', 'Boots', 'Accessory']
        slot_keys = ['weapon', 'armor', 'helmet', 'boots', 'accessory']

        for i, (label, key) in enumerate(zip(slot_labels, slot_keys)):
            y_offset = equip_y - (i * 0.08)

            # Label
            Text(parent=self, text=label + ':', position=(equip_x - 0.05, y_offset),
                 scale=0.8, color=color.rgb(150, 150, 150))

            # Slot
            slot = Button(
                parent=self,
                scale=(0.12, 0.05),
                position=(equip_x + 0.1, y_offset),
                color=color.rgb(60, 60, 70),
                on_click=Func(self.select_equipment, key)
            )

            # Update slot text
            equip = self.inventory.equipment[key]
            if not equip.is_empty():
                slot.text = equip.item.name
                slot.text_entity.scale = 0.6

            self.equip_slots[key] = slot

    def _create_inventory_grid(self):
        """Create inventory slot grid."""
        self.slots = []
        cols = 6
        rows = 5
        slot_size = 0.07
        start_x = 0.05
        start_y = 0.15

        for i in range(len(self.inventory.slots)):
            row = i // cols
            col = i % cols

            x = start_x + (col * (slot_size + 0.01))
            y = start_y - (row * (slot_size + 0.01))

            slot = Button(
                parent=self,
                scale=(slot_size, slot_size),
                position=(x, y),
                color=color.rgb(50, 50, 60),
                on_click=Func(self.select_slot, i)
            )

            inv_slot = self.inventory.slots[i]
            if not inv_slot.is_empty():
                slot.text = str(inv_slot.quantity) if inv_slot.quantity > 1 else ''
                slot.text_entity.scale = 0.5
                # Color by rarity
                r, g, b = inv_slot.item.rarity.value[1]
                slot.color = color.rgb(r // 3, g // 3, b // 3)

            self.slots.append(slot)

    def _create_info_panel(self):
        """Create item info panel."""
        self.info_panel = Entity(
            parent=self,
            model='quad',
            color=color.rgb(30, 30, 40),
            scale=(0.25, 0.25),
            position=(0.25, -0.15),
            visible=False
        )

        self.info_name = Text(
            parent=self,
            text='',
            position=(0.14, -0.05),
            scale=1,
            color=color.white,
            visible=False
        )

        self.info_desc = Text(
            parent=self,
            text='',
            position=(0.14, -0.1),
            scale=0.7,
            color=color.rgb(180, 180, 180),
            visible=False,
            wordwrap=20
        )

        self.info_stats = Text(
            parent=self,
            text='',
            position=(0.14, -0.2),
            scale=0.8,
            color=color.rgb(100, 200, 100),
            visible=False
        )

        # Action buttons
        self.use_btn = Button(
            parent=self,
            text='Use',
            scale=(0.08, 0.04),
            position=(0.18, -0.28),
            color=color.rgb(60, 100, 60),
            on_click=self.use_selected,
            visible=False
        )

        self.equip_btn = Button(
            parent=self,
            text='Equip',
            scale=(0.08, 0.04),
            position=(0.28, -0.28),
            color=color.rgb(60, 60, 100),
            on_click=self.equip_selected,
            visible=False
        )

    def select_slot(self, index):
        """Select an inventory slot."""
        slot = self.inventory.slots[index]
        if slot.is_empty():
            self._hide_info()
            return

        self.selected_slot = index
        item = slot.item

        # Show info
        self.info_panel.visible = True
        self.info_name.visible = True
        self.info_desc.visible = True
        self.info_stats.visible = True

        r, g, b = item.rarity.value[1]
        self.info_name.text = item.name
        self.info_name.color = color.rgb(r, g, b)
        self.info_desc.text = item.description

        # Stats
        stats = []
        if item.attack:
            stats.append(f"Attack: +{item.attack}")
        if item.defense:
            stats.append(f"Defense: +{item.defense}")
        if item.heal_amount:
            stats.append(f"Heals: {item.heal_amount}")
        if item.mana_restore:
            stats.append(f"Mana: +{item.mana_restore}")
        self.info_stats.text = '\n'.join(stats)

        # Show appropriate buttons
        self.use_btn.visible = item.is_consumable()
        self.equip_btn.visible = item.is_equipment()

    def select_equipment(self, slot_key):
        """Select an equipment slot."""
        equip = self.inventory.equipment[slot_key]
        if equip.is_empty():
            return

        # Could show unequip option here

    def _hide_info(self):
        """Hide item info panel."""
        self.info_panel.visible = False
        self.info_name.visible = False
        self.info_desc.visible = False
        self.info_stats.visible = False
        self.use_btn.visible = False
        self.equip_btn.visible = False
        self.selected_slot = None

    def use_selected(self):
        """Use selected item."""
        if self.selected_slot is not None:
            self.inventory.use_item(self.selected_slot, self.character)
            self._refresh()

    def equip_selected(self):
        """Equip selected item."""
        if self.selected_slot is not None:
            self.inventory.equip_item(self.selected_slot)
            self._refresh()

    def _refresh(self):
        """Refresh inventory display."""
        # Update gold
        self.gold_text.text = f'Gold: {self.inventory.gold}'

        # Update slots
        for i, slot in enumerate(self.slots):
            inv_slot = self.inventory.slots[i]
            if inv_slot.is_empty():
                slot.text = ''
                slot.color = color.rgb(50, 50, 60)
            else:
                slot.text = str(inv_slot.quantity) if inv_slot.quantity > 1 else ''
                r, g, b = inv_slot.item.rarity.value[1]
                slot.color = color.rgb(r // 3, g // 3, b // 3)

        # Update equipment
        for key, slot in self.equip_slots.items():
            equip = self.inventory.equipment[key]
            if equip.is_empty():
                slot.text = ''
            else:
                slot.text = equip.item.name

        self._hide_info()

    def close(self):
        """Close inventory."""
        destroy(self)
        self.on_close()

    def input(self, key):
        if key == 'escape' or key == 'i':
            self.close()
