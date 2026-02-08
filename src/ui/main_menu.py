from ursina import *


class MainMenu(Entity):
    """Main menu shown after login."""

    def __init__(self, username, on_play_callback, on_quit_callback):
        super().__init__()
        self.username = username
        self.on_play_callback = on_play_callback
        self.on_quit_callback = on_quit_callback

        # Title
        self.title = Text(
            text='SKILLMINE',
            scale=3,
            origin=(0, 0),
            y=0.35,
            color=color.cyan
        )

        # Welcome message
        self.welcome = Text(
            text=f'Welcome, {username}!',
            scale=1.5,
            origin=(0, 0),
            y=0.2,
            color=color.white
        )

        # Menu buttons
        button_y_start = 0.05
        button_spacing = 0.1

        self.play_button = Button(
            text='NEW GAME',
            scale=(0.3, 0.07),
            y=button_y_start,
            color=color.green,
            on_click=self.start_game
        )

        self.continue_button = Button(
            text='CONTINUE',
            scale=(0.3, 0.07),
            y=button_y_start - button_spacing,
            color=color.azure,
            on_click=self.continue_game
        )

        self.settings_button = Button(
            text='SETTINGS',
            scale=(0.3, 0.07),
            y=button_y_start - button_spacing * 2,
            color=color.gray,
            on_click=self.open_settings
        )

        self.quit_button = Button(
            text='QUIT',
            scale=(0.3, 0.07),
            y=button_y_start - button_spacing * 3,
            color=color.red,
            on_click=self.quit_game
        )

        # Version text
        self.version = Text(
            text='v0.1.0 Alpha',
            scale=1,
            origin=(0, 0),
            y=-0.45,
            color=color.light_gray
        )

    def start_game(self):
        callback = self.on_play_callback
        self.cleanup()
        callback(new_game=True)

    def continue_game(self):
        callback = self.on_play_callback
        self.cleanup()
        callback(new_game=False)

    def open_settings(self):
        print("Settings not yet implemented")

    def quit_game(self):
        self.on_quit_callback()

    def cleanup(self):
        destroy(self.title)
        destroy(self.welcome)
        destroy(self.play_button)
        destroy(self.continue_button)
        destroy(self.settings_button)
        destroy(self.quit_button)
        destroy(self.version)
        destroy(self)
