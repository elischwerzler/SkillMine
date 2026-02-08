"""Dialogue system for NPC conversations."""

import json
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Callable


@dataclass
class DialogueChoice:
    """A choice the player can make in dialogue."""
    text: str
    next_node: str
    conditions: Dict = field(default_factory=dict)
    effects: Dict = field(default_factory=dict)


@dataclass
class DialogueNode:
    """A single node in a dialogue tree."""
    id: str
    speaker: str
    text: str
    choices: List[DialogueChoice] = field(default_factory=list)
    is_end: bool = False
    on_enter_effects: Dict = field(default_factory=dict)


class DialogueTree:
    """A complete dialogue conversation tree."""

    def __init__(self, tree_id: str, npc_name: str):
        self.tree_id = tree_id
        self.npc_name = npc_name
        self.nodes: Dict[str, DialogueNode] = {}
        self.start_node: str = "start"
        self.current_node: Optional[DialogueNode] = None

    def add_node(self, node: DialogueNode):
        """Add a node to the dialogue tree."""
        self.nodes[node.id] = node

    def start(self) -> DialogueNode:
        """Start the dialogue from the beginning."""
        self.current_node = self.nodes.get(self.start_node)
        return self.current_node

    def select_choice(self, choice_index: int) -> Optional[DialogueNode]:
        """Select a choice and move to the next node."""
        if not self.current_node or not self.current_node.choices:
            return None

        if 0 <= choice_index < len(self.current_node.choices):
            choice = self.current_node.choices[choice_index]
            next_node_id = choice.next_node

            if next_node_id == "end":
                self.current_node = None
                return None

            self.current_node = self.nodes.get(next_node_id)
            return self.current_node

        return self.current_node

    def is_active(self) -> bool:
        """Check if dialogue is currently active."""
        return self.current_node is not None

    @classmethod
    def from_dict(cls, data: Dict) -> 'DialogueTree':
        """Create a dialogue tree from dictionary data."""
        tree = cls(data['id'], data['npc_name'])
        tree.start_node = data.get('start_node', 'start')

        for node_data in data.get('nodes', []):
            choices = []
            for choice_data in node_data.get('choices', []):
                choice = DialogueChoice(
                    text=choice_data['text'],
                    next_node=choice_data['next_node'],
                    conditions=choice_data.get('conditions', {}),
                    effects=choice_data.get('effects', {})
                )
                choices.append(choice)

            node = DialogueNode(
                id=node_data['id'],
                speaker=node_data.get('speaker', tree.npc_name),
                text=node_data['text'],
                choices=choices,
                is_end=node_data.get('is_end', False),
                on_enter_effects=node_data.get('effects', {})
            )
            tree.add_node(node)

        return tree


class DialogueManager:
    """Manages all dialogue trees and current conversation state."""

    def __init__(self):
        self.dialogue_trees: Dict[str, DialogueTree] = {}
        self.current_dialogue: Optional[DialogueTree] = None
        self.conversation_history: List[Dict] = []

        # Callbacks
        self.on_dialogue_start: Optional[Callable] = None
        self.on_dialogue_end: Optional[Callable] = None
        self.on_node_change: Optional[Callable] = None

        # Player state reference (for conditions)
        self.player_state: Dict = {}

    def load_dialogue(self, dialogue_data: Dict):
        """Load a dialogue tree from data."""
        tree = DialogueTree.from_dict(dialogue_data)
        self.dialogue_trees[tree.tree_id] = tree

    def load_dialogue_file(self, filepath: str):
        """Load dialogue from a JSON file."""
        with open(filepath, 'r') as f:
            data = json.load(f)
            self.load_dialogue(data)

    def start_dialogue(self, tree_id: str) -> Optional[DialogueNode]:
        """Start a dialogue conversation."""
        if tree_id not in self.dialogue_trees:
            print(f"Dialogue tree '{tree_id}' not found")
            return None

        self.current_dialogue = self.dialogue_trees[tree_id]
        node = self.current_dialogue.start()

        if self.on_dialogue_start:
            self.on_dialogue_start(self.current_dialogue)

        if node and self.on_node_change:
            self.on_node_change(node)

        return node

    def select_choice(self, choice_index: int) -> Optional[DialogueNode]:
        """Select a dialogue choice."""
        if not self.current_dialogue:
            return None

        # Get the choice before moving
        current_node = self.current_dialogue.current_node
        if current_node and 0 <= choice_index < len(current_node.choices):
            choice = current_node.choices[choice_index]
            self.apply_effects(choice.effects)

        node = self.current_dialogue.select_choice(choice_index)

        if node:
            self.apply_effects(node.on_enter_effects)
            if self.on_node_change:
                self.on_node_change(node)
        else:
            self.end_dialogue()

        return node

    def apply_effects(self, effects: Dict):
        """Apply dialogue effects (give items, change reputation, etc.)."""
        if not effects:
            return

        if 'give_xp' in effects:
            print(f"Gained {effects['give_xp']} XP!")

        if 'give_gold' in effects:
            print(f"Gained {effects['give_gold']} gold!")

        if 'give_item' in effects:
            print(f"Received item: {effects['give_item']}")

        if 'start_quest' in effects:
            print(f"Quest started: {effects['start_quest']}")

        if 'reputation' in effects:
            for faction, amount in effects['reputation'].items():
                print(f"Reputation with {faction}: {'+' if amount > 0 else ''}{amount}")

    def check_conditions(self, conditions: Dict) -> bool:
        """Check if dialogue conditions are met."""
        if not conditions:
            return True

        if 'min_level' in conditions:
            player_level = self.player_state.get('level', 1)
            if player_level < conditions['min_level']:
                return False

        if 'has_item' in conditions:
            inventory = self.player_state.get('inventory', [])
            if conditions['has_item'] not in inventory:
                return False

        if 'quest_complete' in conditions:
            completed_quests = self.player_state.get('completed_quests', [])
            if conditions['quest_complete'] not in completed_quests:
                return False

        if 'min_reputation' in conditions:
            for faction, min_rep in conditions['min_reputation'].items():
                current_rep = self.player_state.get('reputation', {}).get(faction, 0)
                if current_rep < min_rep:
                    return False

        return True

    def get_available_choices(self) -> List[DialogueChoice]:
        """Get choices that meet their conditions."""
        if not self.current_dialogue or not self.current_dialogue.current_node:
            return []

        available = []
        for choice in self.current_dialogue.current_node.choices:
            if self.check_conditions(choice.conditions):
                available.append(choice)

        return available

    def end_dialogue(self):
        """End the current dialogue."""
        if self.on_dialogue_end:
            self.on_dialogue_end(self.current_dialogue)

        self.current_dialogue = None

    def is_in_dialogue(self) -> bool:
        """Check if currently in a dialogue."""
        return self.current_dialogue is not None and self.current_dialogue.is_active()


# Sample dialogue data for testing
SAMPLE_DIALOGUE = {
    "id": "village_elder",
    "npc_name": "Village Elder",
    "start_node": "greeting",
    "nodes": [
        {
            "id": "greeting",
            "speaker": "Village Elder",
            "text": "Ah, a new adventurer! Welcome to our humble village. What brings you to these parts?",
            "choices": [
                {"text": "I'm looking for adventure!", "next_node": "adventure"},
                {"text": "I need help with something.", "next_node": "help"},
                {"text": "Just passing through.", "next_node": "passing"},
                {"text": "Goodbye.", "next_node": "end"}
            ]
        },
        {
            "id": "adventure",
            "speaker": "Village Elder",
            "text": "Adventure, you say? Well, there's been strange happenings in the forest lately. Creatures have been more aggressive. Perhaps you could investigate?",
            "choices": [
                {"text": "I'll check it out!", "next_node": "accept_quest", "effects": {"start_quest": "forest_investigation"}},
                {"text": "Sounds dangerous... any reward?", "next_node": "reward_question"},
                {"text": "Maybe later.", "next_node": "greeting"}
            ]
        },
        {
            "id": "reward_question",
            "speaker": "Village Elder",
            "text": "Of course! The village will pay you 50 gold and I have an old sword that might serve you well.",
            "choices": [
                {"text": "Deal! I'll do it.", "next_node": "accept_quest", "effects": {"start_quest": "forest_investigation"}},
                {"text": "I need to prepare first.", "next_node": "greeting"}
            ]
        },
        {
            "id": "accept_quest",
            "speaker": "Village Elder",
            "text": "Excellent! Head east into the forest and see what you can find. Be careful, young one.",
            "effects": {"give_xp": 10},
            "choices": [
                {"text": "I won't let you down!", "next_node": "end"},
                {"text": "Any tips?", "next_node": "tips"}
            ]
        },
        {
            "id": "tips",
            "speaker": "Village Elder",
            "text": "Watch for glowing eyes in the darkness - that's usually a sign of corrupted creatures. And don't venture too deep alone.",
            "choices": [
                {"text": "Thanks for the advice!", "next_node": "end"}
            ]
        },
        {
            "id": "help",
            "speaker": "Village Elder",
            "text": "Help? What kind of help do you need? I know much about this land.",
            "choices": [
                {"text": "Where can I find equipment?", "next_node": "equipment"},
                {"text": "Tell me about this village.", "next_node": "village_info"},
                {"text": "Never mind.", "next_node": "greeting"}
            ]
        },
        {
            "id": "equipment",
            "speaker": "Village Elder",
            "text": "The blacksmith to the north has weapons and armor. The general store has supplies. Tell them I sent you for a discount!",
            "effects": {"reputation": {"village": 5}},
            "choices": [
                {"text": "Thanks!", "next_node": "greeting"},
                {"text": "Goodbye.", "next_node": "end"}
            ]
        },
        {
            "id": "village_info",
            "speaker": "Village Elder",
            "text": "This is Millbrook Village, founded over a hundred years ago. We're peaceful folk - farmers mostly. Though lately, troubles have found us...",
            "choices": [
                {"text": "What kind of troubles?", "next_node": "adventure"},
                {"text": "Interesting. Thanks.", "next_node": "greeting"}
            ]
        },
        {
            "id": "passing",
            "speaker": "Village Elder",
            "text": "I see. Well, you're welcome to rest at the inn. Safe travels, stranger.",
            "choices": [
                {"text": "Actually, wait...", "next_node": "greeting"},
                {"text": "Thanks. Goodbye.", "next_node": "end"}
            ]
        }
    ]
}
