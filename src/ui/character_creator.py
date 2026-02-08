"""Character creation UI screen."""

from ursina import *
import config


class CharacterCreator(Entity):
    """Character creation screen for new games."""

    def __init__(self, username, on_complete_callback):
        super().__init__()
        self.username = username
        self.on_complete_callback = on_complete_callback

        # Selected options
        self.selected_race = 'human'
        self.selected_class = 'warrior'

        # Title
        self.title = Text(
            text='CREATE YOUR CHARACTER',
            scale=2,
            origin=(0, 0),
            y=0.4,
            color=color.cyan
        )

        # Character name display
        self.name_display = Text(
            text=f'Name: {username}',
            scale=1.5,
            origin=(0, 0),
            y=0.32,
            color=color.white
        )

        # === RACE SELECTION ===
        self.race_label = Text(
            text='Choose Race:',
            scale=1.2,
            origin=(0, 0),
            y=0.22,
            color=color.light_gray
        )

        self.race_buttons = {}
        races = list(config.RACES.keys())
        start_x = -0.3
        for i, race_key in enumerate(races):
            race = config.RACES[race_key]
            is_selected = race_key == self.selected_race
            btn = Button(
                text=race['name'],
                scale=(0.15, 0.05),
                x=start_x + (i * 0.2),
                y=0.14,
                color=color.green if is_selected else color.dark_gray,
                on_click=Func(self.select_race, race_key)
            )
            self.race_buttons[race_key] = btn

        # Race description
        self.race_desc = Text(
            text=config.RACES[self.selected_race]['description'],
            scale=1,
            origin=(0, 0),
            y=0.06,
            color=color.light_gray
        )

        # Race stat bonuses
        self.race_stats = Text(
            text=self._get_race_stats_text(),
            scale=0.9,
            origin=(0, 0),
            y=0.0,
            color=color.lime
        )

        # === CLASS SELECTION ===
        self.class_label = Text(
            text='Choose Class:',
            scale=1.2,
            origin=(0, 0),
            y=-0.08,
            color=color.light_gray
        )

        self.class_buttons = {}
        classes = list(config.CLASSES.keys())
        for i, class_key in enumerate(classes):
            char_class = config.CLASSES[class_key]
            is_selected = class_key == self.selected_class
            btn = Button(
                text=char_class['name'],
                scale=(0.15, 0.05),
                x=start_x + (i * 0.2),
                y=-0.16,
                color=color.azure if is_selected else color.dark_gray,
                on_click=Func(self.select_class, class_key)
            )
            self.class_buttons[class_key] = btn

        # Class description
        self.class_desc = Text(
            text=config.CLASSES[self.selected_class]['description'],
            scale=1,
            origin=(0, 0),
            y=-0.24,
            color=color.light_gray
        )

        # Class stats preview
        self.class_stats = Text(
            text=self._get_class_stats_text(),
            scale=0.8,
            origin=(0, 0),
            y=-0.30,
            color=color.cyan
        )

        # Start button
        self.start_button = Button(
            text='BEGIN ADVENTURE',
            scale=(0.3, 0.07),
            y=-0.42,
            color=color.green,
            on_click=self.create_character
        )

    def select_race(self, race_key):
        """Select a race."""
        for key, btn in self.race_buttons.items():
            btn.color = color.green if key == race_key else color.dark_gray

        self.selected_race = race_key
        self.race_desc.text = config.RACES[race_key]['description']
        self.race_stats.text = self._get_race_stats_text()

    def select_class(self, class_key):
        """Select a class."""
        for key, btn in self.class_buttons.items():
            btn.color = color.azure if key == class_key else color.dark_gray

        self.selected_class = class_key
        self.class_desc.text = config.CLASSES[class_key]['description']
        self.class_stats.text = self._get_class_stats_text()

    def _get_race_stats_text(self):
        """Get formatted race stat bonuses."""
        bonuses = config.RACES[self.selected_race]['stat_bonuses']
        parts = []
        for stat, value in bonuses.items():
            if value > 0:
                parts.append(f"+{value} {stat.upper()}")
            elif value < 0:
                parts.append(f"{value} {stat.upper()}")
        return "  ".join(parts) if parts else "Balanced stats"

    def _get_class_stats_text(self):
        """Get formatted class base stats."""
        stats = config.CLASSES[self.selected_class]['base_stats']
        parts = [f"{stat[:3].upper()}: {value}" for stat, value in stats.items()]
        return "  ".join(parts)

    def create_character(self):
        """Create the character and start the game."""
        callback = self.on_complete_callback
        race = self.selected_race
        char_class = self.selected_class
        self.cleanup()
        callback(race, char_class)

    def cleanup(self):
        """Clean up all UI elements."""
        destroy(self.title)
        destroy(self.name_display)
        destroy(self.race_label)
        for btn in self.race_buttons.values():
            destroy(btn)
        destroy(self.race_desc)
        destroy(self.race_stats)
        destroy(self.class_label)
        for btn in self.class_buttons.values():
            destroy(btn)
        destroy(self.class_desc)
        destroy(self.class_stats)
        destroy(self.start_button)
        destroy(self)
