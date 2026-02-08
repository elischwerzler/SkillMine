"""Quest system for tracking and completing quests."""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Callable
from enum import Enum
import json


class QuestStatus(Enum):
    AVAILABLE = "available"
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"
    TURNED_IN = "turned_in"


class ObjectiveType(Enum):
    KILL = "kill"           # Kill X enemies of type Y
    COLLECT = "collect"     # Collect X items of type Y
    TALK = "talk"           # Talk to NPC
    EXPLORE = "explore"     # Reach location
    ESCORT = "escort"       # Escort NPC to location
    INTERACT = "interact"   # Interact with object
    SURVIVE = "survive"     # Survive for X seconds


@dataclass
class QuestObjective:
    """A single objective within a quest."""
    id: str
    description: str
    objective_type: ObjectiveType
    target: str  # Enemy type, item type, NPC name, location, etc.
    required_count: int = 1
    current_count: int = 0
    is_optional: bool = False
    is_hidden: bool = False  # Hidden until previous objective complete

    def is_complete(self) -> bool:
        return self.current_count >= self.required_count

    def progress(self, amount: int = 1) -> bool:
        """Add progress to objective. Returns True if just completed."""
        was_complete = self.is_complete()
        self.current_count = min(self.required_count, self.current_count + amount)
        return not was_complete and self.is_complete()


@dataclass
class QuestReward:
    """Rewards for completing a quest."""
    experience: int = 0
    gold: int = 0
    items: List[str] = field(default_factory=list)
    reputation: Dict[str, int] = field(default_factory=dict)
    unlock_quest: Optional[str] = None
    unlock_ability: Optional[str] = None


@dataclass
class Quest:
    """A complete quest with objectives and rewards."""
    id: str
    name: str
    description: str
    giver_npc: str
    level_requirement: int = 1
    objectives: List[QuestObjective] = field(default_factory=list)
    rewards: QuestReward = field(default_factory=QuestReward)
    status: QuestStatus = QuestStatus.AVAILABLE

    # Quest chain
    prerequisite_quests: List[str] = field(default_factory=list)
    is_main_quest: bool = False
    is_daily: bool = False
    is_repeatable: bool = False

    # Dialogue
    accept_dialogue: str = ""
    progress_dialogue: str = ""
    complete_dialogue: str = ""

    def is_complete(self) -> bool:
        """Check if all required objectives are complete."""
        for obj in self.objectives:
            if not obj.is_optional and not obj.is_complete():
                return False
        return True

    def get_active_objectives(self) -> List[QuestObjective]:
        """Get currently active (visible) objectives."""
        active = []
        for i, obj in enumerate(self.objectives):
            if obj.is_hidden:
                # Check if previous objective is complete
                if i > 0 and self.objectives[i - 1].is_complete():
                    active.append(obj)
            else:
                active.append(obj)
        return active


class QuestManager:
    """Manages all quests and quest progress."""

    def __init__(self):
        self.all_quests: Dict[str, Quest] = {}
        self.active_quests: List[Quest] = []
        self.completed_quests: List[str] = []
        self.failed_quests: List[str] = []

        # Player state reference
        self.player_level = 1
        self.player_reputation: Dict[str, int] = {}

        # Callbacks
        self.on_quest_accepted: Optional[Callable] = None
        self.on_quest_completed: Optional[Callable] = None
        self.on_objective_progress: Optional[Callable] = None
        self.on_objective_completed: Optional[Callable] = None

        # Load default quests
        self._load_default_quests()

    def _load_default_quests(self):
        """Load the default quests."""
        # Main story quest 1
        self.register_quest(Quest(
            id="main_01_investigate_forest",
            name="Strange Happenings",
            description="The Village Elder has asked you to investigate strange occurrences in the forest.",
            giver_npc="Village Elder",
            level_requirement=1,
            is_main_quest=True,
            objectives=[
                QuestObjective(
                    id="travel_to_forest",
                    description="Travel to the Dark Forest",
                    objective_type=ObjectiveType.EXPLORE,
                    target="dark_forest"
                ),
                QuestObjective(
                    id="kill_corrupted",
                    description="Defeat corrupted creatures",
                    objective_type=ObjectiveType.KILL,
                    target="corrupted",
                    required_count=5
                ),
                QuestObjective(
                    id="find_source",
                    description="Find the source of corruption",
                    objective_type=ObjectiveType.EXPLORE,
                    target="corruption_source",
                    is_hidden=True
                ),
            ],
            rewards=QuestReward(
                experience=100,
                gold=50,
                items=["health_potion", "old_sword"],
                unlock_quest="main_02_corruption"
            ),
            accept_dialogue="Thank you, brave adventurer. Head east into the forest and be careful!",
            progress_dialogue="Have you found anything in the forest yet?",
            complete_dialogue="By the gods! This is worse than I feared. Thank you for your bravery."
        ))

        # Side quest - hunting
        self.register_quest(Quest(
            id="side_wolf_pelts",
            name="Wolf Hunter",
            description="The tanner needs wolf pelts for his leather work.",
            giver_npc="Tanner",
            level_requirement=1,
            objectives=[
                QuestObjective(
                    id="collect_pelts",
                    description="Collect Wolf Pelts",
                    objective_type=ObjectiveType.COLLECT,
                    target="wolf_pelt",
                    required_count=5
                ),
            ],
            rewards=QuestReward(
                experience=40,
                gold=25,
                items=["leather_armor"]
            ),
            is_repeatable=True,
            accept_dialogue="I need wolf pelts for my work. Bring me 5 and I'll reward you well.",
            complete_dialogue="Excellent pelts! Here's your reward."
        ))

        # Side quest - gathering
        self.register_quest(Quest(
            id="side_herb_gathering",
            name="Healing Herbs",
            description="The healer needs medicinal herbs.",
            giver_npc="Village Healer",
            level_requirement=1,
            objectives=[
                QuestObjective(
                    id="gather_herbs",
                    description="Gather Healing Herbs",
                    objective_type=ObjectiveType.COLLECT,
                    target="healing_herb",
                    required_count=10
                ),
            ],
            rewards=QuestReward(
                experience=30,
                gold=15,
                items=["health_potion", "health_potion", "health_potion"]
            ),
            accept_dialogue="I'm running low on herbs. Could you gather some from the meadow?",
            complete_dialogue="These are perfect! Take these potions as thanks."
        ))

        # Side quest - escort
        self.register_quest(Quest(
            id="side_escort_merchant",
            name="Safe Passage",
            description="Escort the merchant safely to the next town.",
            giver_npc="Traveling Merchant",
            level_requirement=3,
            objectives=[
                QuestObjective(
                    id="escort_merchant",
                    description="Escort the merchant to Riverside",
                    objective_type=ObjectiveType.ESCORT,
                    target="merchant_to_riverside"
                ),
                QuestObjective(
                    id="defeat_bandits",
                    description="Defeat any bandits that attack",
                    objective_type=ObjectiveType.KILL,
                    target="bandit",
                    required_count=3,
                    is_optional=True
                ),
            ],
            rewards=QuestReward(
                experience=75,
                gold=100,
                reputation={"merchants_guild": 10}
            ),
            accept_dialogue="The roads aren't safe anymore. Will you protect me on my journey?",
            complete_dialogue="We made it! Thank you, here's your payment."
        ))

        # Daily quest
        self.register_quest(Quest(
            id="daily_monster_hunt",
            name="Daily Hunt",
            description="Help keep the village safe by hunting monsters.",
            giver_npc="Guard Captain",
            level_requirement=1,
            is_daily=True,
            is_repeatable=True,
            objectives=[
                QuestObjective(
                    id="kill_monsters",
                    description="Defeat any monsters",
                    objective_type=ObjectiveType.KILL,
                    target="any_monster",
                    required_count=10
                ),
            ],
            rewards=QuestReward(
                experience=50,
                gold=30
            ),
            accept_dialogue="Keep the roads safe today, adventurer!",
            complete_dialogue="Well done! Come back tomorrow for more work."
        ))

    def register_quest(self, quest: Quest):
        """Register a quest in the system."""
        self.all_quests[quest.id] = quest

    def get_available_quests(self, npc_name: str = None) -> List[Quest]:
        """Get all available quests, optionally filtered by NPC."""
        available = []
        for quest in self.all_quests.values():
            if quest.status != QuestStatus.AVAILABLE:
                if not (quest.is_repeatable and quest.status == QuestStatus.TURNED_IN):
                    continue

            # Check level requirement
            if quest.level_requirement > self.player_level:
                continue

            # Check prerequisites
            if quest.prerequisite_quests:
                if not all(q in self.completed_quests for q in quest.prerequisite_quests):
                    continue

            # Filter by NPC if specified
            if npc_name and quest.giver_npc != npc_name:
                continue

            available.append(quest)

        return available

    def accept_quest(self, quest_id: str) -> bool:
        """Accept a quest."""
        if quest_id not in self.all_quests:
            return False

        quest = self.all_quests[quest_id]

        if quest.status != QuestStatus.AVAILABLE:
            if not (quest.is_repeatable and quest.status == QuestStatus.TURNED_IN):
                return False

        # Reset objectives for repeatable quests
        if quest.is_repeatable:
            for obj in quest.objectives:
                obj.current_count = 0

        quest.status = QuestStatus.ACTIVE
        if quest not in self.active_quests:
            self.active_quests.append(quest)

        print(f"Quest accepted: {quest.name}")

        if self.on_quest_accepted:
            self.on_quest_accepted(quest)

        return True

    def update_objective(self, objective_type: ObjectiveType, target: str, amount: int = 1):
        """Update progress on matching objectives across all active quests."""
        for quest in self.active_quests:
            if quest.status != QuestStatus.ACTIVE:
                continue

            for objective in quest.objectives:
                if objective.objective_type == objective_type and objective.target == target:
                    if objective.progress(amount):
                        # Objective completed
                        print(f"Objective complete: {objective.description}")
                        if self.on_objective_completed:
                            self.on_objective_completed(quest, objective)
                    else:
                        # Progress made
                        if self.on_objective_progress:
                            self.on_objective_progress(quest, objective)

                    # Check if quest is now complete
                    if quest.is_complete():
                        self._mark_quest_ready(quest)

    def _mark_quest_ready(self, quest: Quest):
        """Mark quest as ready to turn in."""
        print(f"Quest complete: {quest.name} - Return to {quest.giver_npc}")

    def turn_in_quest(self, quest_id: str) -> Optional[QuestReward]:
        """Turn in a completed quest and receive rewards."""
        if quest_id not in self.all_quests:
            return None

        quest = self.all_quests[quest_id]

        if quest.status != QuestStatus.ACTIVE or not quest.is_complete():
            return None

        # Mark as turned in
        quest.status = QuestStatus.TURNED_IN
        if quest_id not in self.completed_quests:
            self.completed_quests.append(quest_id)

        # Remove from active
        if quest in self.active_quests:
            self.active_quests.remove(quest)

        # Apply rewards
        rewards = quest.rewards
        print(f"\n=== Quest Complete: {quest.name} ===")
        print(f"Experience: +{rewards.experience}")
        print(f"Gold: +{rewards.gold}")
        if rewards.items:
            print(f"Items: {', '.join(rewards.items)}")
        if rewards.reputation:
            for faction, rep in rewards.reputation.items():
                print(f"Reputation ({faction}): {'+' if rep > 0 else ''}{rep}")
        print("================================\n")

        if self.on_quest_completed:
            self.on_quest_completed(quest)

        # Unlock follow-up quest
        if rewards.unlock_quest:
            if rewards.unlock_quest in self.all_quests:
                self.all_quests[rewards.unlock_quest].status = QuestStatus.AVAILABLE

        return rewards

    def abandon_quest(self, quest_id: str) -> bool:
        """Abandon an active quest."""
        if quest_id not in self.all_quests:
            return False

        quest = self.all_quests[quest_id]

        if quest.status != QuestStatus.ACTIVE:
            return False

        quest.status = QuestStatus.AVAILABLE
        if quest in self.active_quests:
            self.active_quests.remove(quest)

        # Reset progress
        for obj in quest.objectives:
            obj.current_count = 0

        print(f"Quest abandoned: {quest.name}")
        return True

    def fail_quest(self, quest_id: str):
        """Mark a quest as failed."""
        if quest_id not in self.all_quests:
            return

        quest = self.all_quests[quest_id]
        quest.status = QuestStatus.FAILED
        self.failed_quests.append(quest_id)

        if quest in self.active_quests:
            self.active_quests.remove(quest)

        print(f"Quest failed: {quest.name}")

    def get_quest_log_text(self) -> str:
        """Get formatted quest log text."""
        if not self.active_quests:
            return "No active quests."

        lines = ["=== QUEST LOG ===\n"]

        for quest in self.active_quests:
            status = "[COMPLETE]" if quest.is_complete() else ""
            quest_type = "[MAIN]" if quest.is_main_quest else "[SIDE]"
            lines.append(f"{quest_type} {quest.name} {status}")
            lines.append(f"  {quest.description}")

            for obj in quest.get_active_objectives():
                check = "[x]" if obj.is_complete() else "[ ]"
                optional = "(Optional) " if obj.is_optional else ""
                lines.append(f"  {check} {optional}{obj.description}: {obj.current_count}/{obj.required_count}")

            lines.append("")

        return "\n".join(lines)

    def to_dict(self) -> Dict:
        """Serialize quest state for saving."""
        active_data = []
        for quest in self.active_quests:
            quest_data = {
                'id': quest.id,
                'objectives': [
                    {'id': obj.id, 'current_count': obj.current_count}
                    for obj in quest.objectives
                ]
            }
            active_data.append(quest_data)

        return {
            'active_quests': active_data,
            'completed_quests': self.completed_quests,
            'failed_quests': self.failed_quests,
        }

    def from_dict(self, data: Dict):
        """Restore quest state from saved data."""
        self.completed_quests = data.get('completed_quests', [])
        self.failed_quests = data.get('failed_quests', [])

        # Mark completed quests
        for quest_id in self.completed_quests:
            if quest_id in self.all_quests:
                self.all_quests[quest_id].status = QuestStatus.TURNED_IN

        # Restore active quests
        for quest_data in data.get('active_quests', []):
            quest_id = quest_data['id']
            if quest_id in self.all_quests:
                quest = self.all_quests[quest_id]
                quest.status = QuestStatus.ACTIVE
                self.active_quests.append(quest)

                # Restore objective progress
                for obj_data in quest_data['objectives']:
                    for obj in quest.objectives:
                        if obj.id == obj_data['id']:
                            obj.current_count = obj_data['current_count']
                            break
