"""Dialogue UI for displaying conversations."""

from ursina import *
from .system import DialogueManager, DialogueNode, SAMPLE_DIALOGUE


class DialogueUI(Entity):
    """UI for displaying dialogue conversations."""

    def __init__(self, dialogue_manager: DialogueManager):
        super().__init__(parent=camera.ui)
        self.dialogue_manager = dialogue_manager
        self.visible = False

        # Set up callbacks
        self.dialogue_manager.on_dialogue_start = self.on_dialogue_start
        self.dialogue_manager.on_dialogue_end = self.on_dialogue_end
        self.dialogue_manager.on_node_change = self.on_node_change

        # Create UI elements (hidden by default)
        self.create_ui()
        self.hide()

    def create_ui(self):
        """Create the dialogue UI elements."""
        # Dark background panel
        self.panel = Entity(
            parent=self,
            model='quad',
            color=color.rgba(0, 0, 0, 200),
            scale=(1.4, 0.45),
            y=-0.25
        )

        # Border
        self.border = Entity(
            parent=self,
            model='quad',
            color=color.rgb(80, 80, 100),
            scale=(1.42, 0.47),
            y=-0.25,
            z=0.01
        )

        # Speaker name background
        self.speaker_bg = Entity(
            parent=self,
            model='quad',
            color=color.rgb(60, 60, 80),
            scale=(0.3, 0.06),
            position=(-0.55, -0.05)
        )

        # Speaker name
        self.speaker_text = Text(
            parent=self,
            text='',
            scale=1.5,
            position=(-0.55, -0.05),
            origin=(0, 0),
            color=color.rgb(100, 200, 255)
        )

        # Dialogue text
        self.dialogue_text = Text(
            parent=self,
            text='',
            scale=1.2,
            position=(-0.65, -0.15),
            origin=(-0.5, 0.5),
            color=color.white,
            wordwrap=60
        )

        # Choice buttons (up to 4)
        self.choice_buttons = []
        for i in range(4):
            btn = Button(
                parent=self,
                text='',
                scale=(1.3, 0.055),
                position=(0, -0.32 - (i * 0.065)),
                color=color.rgb(50, 50, 70),
                highlight_color=color.rgb(70, 100, 130),
                text_color=color.white,
                visible=False
            )
            btn.text_entity.scale = 0.8
            self.choice_buttons.append(btn)

        # Continue prompt (for dialogue without choices)
        self.continue_text = Text(
            parent=self,
            text='[Press SPACE to continue]',
            scale=1,
            position=(0, -0.42),
            origin=(0, 0),
            color=color.rgb(150, 150, 170),
            visible=False
        )

    def show(self):
        """Show the dialogue UI."""
        self.visible = True
        self.panel.visible = True
        self.border.visible = True
        self.speaker_bg.visible = True
        self.speaker_text.visible = True
        self.dialogue_text.visible = True
        mouse.locked = False

    def hide(self):
        """Hide the dialogue UI."""
        self.visible = False
        self.panel.visible = False
        self.border.visible = False
        self.speaker_bg.visible = False
        self.speaker_text.visible = False
        self.dialogue_text.visible = False
        self.continue_text.visible = False
        for btn in self.choice_buttons:
            btn.visible = False

    def on_dialogue_start(self, dialogue_tree):
        """Called when dialogue starts."""
        self.show()

    def on_dialogue_end(self, dialogue_tree):
        """Called when dialogue ends."""
        self.hide()
        mouse.locked = True

    def on_node_change(self, node: DialogueNode):
        """Called when dialogue node changes."""
        self.speaker_text.text = node.speaker
        self.dialogue_text.text = node.text

        # Hide all choice buttons first
        for btn in self.choice_buttons:
            btn.visible = False
        self.continue_text.visible = False

        # Get available choices
        available_choices = self.dialogue_manager.get_available_choices()

        if available_choices:
            # Show choice buttons
            for i, choice in enumerate(available_choices):
                if i < len(self.choice_buttons):
                    btn = self.choice_buttons[i]
                    btn.text = f"{i + 1}. {choice.text}"
                    btn.visible = True
                    btn.on_click = Func(self.select_choice, i)
        elif node.is_end:
            # End node - show continue to exit
            self.continue_text.text = '[Press SPACE to close]'
            self.continue_text.visible = True
        else:
            # No choices but not end - auto continue
            self.continue_text.text = '[Press SPACE to continue]'
            self.continue_text.visible = True

    def select_choice(self, index: int):
        """Select a dialogue choice."""
        self.dialogue_manager.select_choice(index)

    def input(self, key):
        """Handle input for dialogue."""
        if not self.visible:
            return

        # Number keys for choices
        if key in ['1', '2', '3', '4']:
            choice_index = int(key) - 1
            available = self.dialogue_manager.get_available_choices()
            if choice_index < len(available):
                self.select_choice(choice_index)

        # Space to continue or end
        if key == 'space':
            if self.continue_text.visible:
                current = self.dialogue_manager.current_dialogue
                if current and current.current_node:
                    if current.current_node.is_end:
                        self.dialogue_manager.end_dialogue()
                    elif not current.current_node.choices:
                        # Auto-advance to next node if defined
                        self.dialogue_manager.end_dialogue()

        # Escape to close dialogue
        if key == 'escape':
            self.dialogue_manager.end_dialogue()


class NPCDialogue:
    """Mixin class for NPCs with dialogue capability."""

    def __init__(self, npc_entity, dialogue_tree_id: str, dialogue_manager: DialogueManager):
        self.entity = npc_entity
        self.dialogue_tree_id = dialogue_tree_id
        self.dialogue_manager = dialogue_manager
        self.interaction_distance = 3.0

    def can_interact(self, player_position) -> bool:
        """Check if player is close enough to interact."""
        distance = (self.entity.position - player_position).length()
        return distance <= self.interaction_distance

    def interact(self):
        """Start dialogue with this NPC."""
        self.dialogue_manager.start_dialogue(self.dialogue_tree_id)
