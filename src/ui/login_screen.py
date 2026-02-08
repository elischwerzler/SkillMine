from ursina import *


class LoginScreen(Entity):
    """Username input screen that appears before the main game."""

    def __init__(self, on_login_callback):
        super().__init__()
        self.on_login_callback = on_login_callback
        self.username = ""
        self.cursor_visible = True
        self.cursor_timer = 0
        self.active = True

        # Title
        self.title = Text(
            text='SKILLMINE',
            scale=3,
            origin=(0, 0),
            y=0.3,
            color=color.cyan
        )

        # Subtitle
        self.subtitle = Text(
            text='Enter the realm of adventure',
            scale=1.2,
            origin=(0, 0),
            y=0.2,
            color=color.light_gray
        )

        # Username prompt
        self.prompt = Text(
            text="What's your username?",
            scale=1.5,
            origin=(0, 0),
            y=0.05,
            color=color.white
        )

        # Input display
        self.input_display = Text(
            text='_',
            scale=2,
            origin=(0, 0),
            y=-0.05,
            color=color.white
        )

        # Enter button
        self.enter_button = Button(
            text='ENTER',
            scale=(0.2, 0.06),
            y=-0.18,
            color=color.azure,
            on_click=self.submit_username
        )

        # Error message
        self.error_text = Text(
            text='',
            scale=1,
            origin=(0, 0),
            y=-0.28,
            color=color.red
        )

    def update(self):
        self.cursor_timer += time.dt
        if self.cursor_timer >= 0.5:
            self.cursor_timer = 0
            self.cursor_visible = not self.cursor_visible
            self._update_display()

    def _update_display(self):
        if not self.active:
            return
        cursor = '_' if self.cursor_visible else ' '
        display_text = self.username + cursor if self.username else cursor
        self.input_display.text = display_text

    def input(self, key):
        if not self.active:
            return
        if key == 'backspace' and len(self.username) > 0:
            self.username = self.username[:-1]
            self.error_text.text = ''
        elif key == 'enter':
            self.submit_username()
        elif key == 'space':
            pass  # Ignore spaces
        elif len(key) == 1 and len(self.username) < 20:
            # Accept letters, numbers, underscore, hyphen
            if key.isalnum() or key == '-':
                self.username += key
                self.error_text.text = ''

        self._update_display()

    def submit_username(self):
        if len(self.username) < 3:
            self.error_text.text = 'Username must be at least 3 characters!'
            return

        # Success
        callback = self.on_login_callback
        username = self.username
        self.cleanup()
        callback(username)

    def cleanup(self):
        self.active = False
        destroy(self.title)
        destroy(self.subtitle)
        destroy(self.prompt)
        destroy(self.input_display)
        destroy(self.enter_button)
        destroy(self.error_text)
        destroy(self)
