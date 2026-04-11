"""
OzZoo Mission System
Provides gameplay objectives and rewards for players.
"""

from __future__ import annotations
from enum import Enum
from typing import TYPE_CHECKING, Optional, Dict, Any, Set
from dataclasses import dataclass
import random

if TYPE_CHECKING:
    from .zoo import Zoo


class MissionType(Enum):
    """Types of missions available."""
    KEEP_HAPPY = "keep_happy"          # Keep N animals happy for X days
    BREED_ANIMALS = "breed_animals"     # Breed N animals successfully
    VISITOR_COUNT = "visitor_count"     # Attract X visitors in Y days
    PROFIT_TARGET = "profit_target"     # Earn $X profit
    BUILD_ENCLOSURES = "build_enclosures"  # Build N enclosures


@dataclass
class MissionReward:
    """Rewards for completing a mission."""
    money: float = 0.0
    reputation: int = 0
    description: str = ""


class Mission:
    """
    Represents a gameplay mission/objective.
    
    Attributes:
        mission_id: Unique identifier
        mission_type: Type of mission (MissionType enum)
        title: Display title for the mission
        description: Detailed description
        target_value: Goal value (e.g., 5 koalas, $10000 profit)
        current_progress: Current progress toward goal
        duration_days: Number of days to complete (0 = no time limit)
        days_remaining: Days left to complete
        target_animal: Specific animal type for animal-based missions
        reward: MissionReward for completion
        is_complete: Whether mission is completed
        is_failed: Whether mission has failed
    """
    
    def __init__(
        self,
        mission_id: str,
        mission_type: MissionType,
        title: str,
        description: str,
        target_value: int,
        duration_days: int = 0,
        target_animal: Optional[str] = None,
        reward: Optional[MissionReward] = None,
        custom_data: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize a mission.
        
        Args:
            mission_id: Unique identifier for the mission
            mission_type: Type of mission
            title: Display title
            description: Detailed description
            target_value: Goal to reach
            duration_days: Days allowed (0 for unlimited)
            target_animal: Specific animal for animal-based missions
            reward: Reward for completion
            custom_data: Extra mission-specific metadata
        """
        self.mission_id = mission_id
        self.mission_type = mission_type
        self.title = title
        self.description = description
        self.target_value = target_value
        self.current_progress = 0
        self.duration_days = duration_days
        self.days_remaining = duration_days
        self.target_animal = target_animal
        self.reward = reward or MissionReward(money=5000, reputation=10)
        self.is_complete = False
        self.is_failed = False
        self.custom_data: Dict[str, Any] = custom_data.copy() if custom_data else {}
    
    def update_progress(self, amount: int) -> None:
        """
        Update mission progress.
        
        Args:
            amount: Amount to add to current progress
        
        Note: For KEEP_HAPPY missions, completion is checked against required_days,
              not target_value. Completion check is handled by Zoo.update_mission_progress().
        """
        if not self.is_complete and not self.is_failed:
            self.current_progress += amount
            # Don't auto-complete here for KEEP_HAPPY - let Zoo handle it
            # For other mission types, check against target_value
            if self.mission_type != MissionType.KEEP_HAPPY:
                if self.current_progress >= self.target_value:
                    self.is_complete = True
    
    def set_progress(self, value: int) -> None:
        """
        Set mission progress to a specific value.
        
        Args:
            value: Progress value to set
        """
        if not self.is_complete and not self.is_failed:
            self.current_progress = value
            # Don't auto-complete here for KEEP_HAPPY - let Zoo handle it
            if self.mission_type != MissionType.KEEP_HAPPY:
                if self.current_progress >= self.target_value:
                    self.is_complete = True
    
    def tick_day(self) -> None:
        """
        Process daily update for mission.
        Decrements days_remaining and checks for failure.
        """
        if self.is_complete or self.is_failed:
            return
        
        if self.duration_days > 0:
            self.days_remaining -= 1
            if self.days_remaining <= 0 and not self.is_complete:
                self.is_failed = True
    
    def get_progress_percentage(self) -> float:
        """
        Get mission completion percentage.
        
        Returns:
            Percentage complete (0-100)
        """
        # For KEEP_HAPPY missions, progress is measured against required_days
        if self.mission_type == MissionType.KEEP_HAPPY:
            required_days = int(
                self.custom_data.get(
                    "required_days",
                    getattr(self, "required_days", self.target_value),
                )
            )
            if required_days == 0:
                return 100.0
            return min(100.0, (self.current_progress / required_days) * 100)
        
        # For other missions, progress is measured against target_value
        if self.target_value == 0:
            return 100.0
        return min(100.0, (self.current_progress / self.target_value) * 100)
    
    def get_status_text(self) -> str:
        """
        Get human-readable status text.
        
        Returns:
            Status string (e.g., "3/5 consecutive days")
        """
        if self.is_complete:
            return "✓ Complete!"
        if self.is_failed:
            return "✗ Failed"
        
        # For KEEP_HAPPY missions, show consecutive days progress
        if self.mission_type == MissionType.KEEP_HAPPY:
            required_days = int(
                self.custom_data.get(
                    "required_days",
                    getattr(self, "required_days", self.target_value),
                )
            )
            progress_text = f"{self.current_progress}/{required_days} consecutive days"
        else:
            progress_text = f"{self.current_progress}/{self.target_value}"
        
        if self.duration_days > 0:
            progress_text += f" ({self.days_remaining} days left)"
        return progress_text
    
    def to_dict(self) -> dict:
        """
        Serialize to dictionary for JSON save.
        
        Returns:
            Dictionary representation
        """
        data = {
            "mission_id": self.mission_id,
            "mission_type": self.mission_type.value,
            "title": self.title,
            "description": self.description,
            "target_value": self.target_value,
            "current_progress": self.current_progress,
            "duration_days": self.duration_days,
            "days_remaining": self.days_remaining,
            "target_animal": self.target_animal,
            "reward": {
                "money": self.reward.money,
                "reputation": self.reward.reputation,
                "description": self.reward.description
            },
            "is_complete": self.is_complete,
            "is_failed": self.is_failed,
            "custom_data": self.custom_data.copy(),
        }
        
        # Include required_days if it exists (for KEEP_HAPPY missions)
        if hasattr(self, "required_days"):
            data["required_days"] = self.required_days
            data["custom_data"]["required_days"] = self.required_days
        
        return data
    
    @classmethod
    def from_dict(cls, data: dict) -> Mission:
        """
        Deserialize from dictionary.
        
        Args:
            data: Dictionary containing mission data
            
        Returns:
            New Mission instance
        """
        reward_data = data.get("reward", {})
        reward = MissionReward(
            money=reward_data.get("money", 0.0),
            reputation=reward_data.get("reputation", 0),
            description=reward_data.get("description", "")
        )
        
        mission = cls(
            mission_id=data["mission_id"],
            mission_type=MissionType(data["mission_type"]),
            title=data["title"],
            description=data["description"],
            target_value=data["target_value"],
            duration_days=data["duration_days"],
            target_animal=data.get("target_animal"),
            reward=reward,
            custom_data=data.get("custom_data", {}),
        )
        
        mission.current_progress = data.get("current_progress", 0)
        mission.days_remaining = data.get("days_remaining", mission.duration_days)
        mission.is_complete = data.get("is_complete", False)
        mission.is_failed = data.get("is_failed", False)
        
        # Restore required_days if present
        if "required_days" in data:
            mission.required_days = data["required_days"]
            mission.custom_data["required_days"] = data["required_days"]
        elif "required_days" in mission.custom_data:
            mission.required_days = mission.custom_data["required_days"]
        
        return mission
    
    def __str__(self) -> str:
        """Human-readable representation."""
        return f"{self.title}: {self.get_status_text()}"


# Mission templates for generation
MISSION_TEMPLATES = {
    MissionType.KEEP_HAPPY: {
        "animals": {
            "Koala": {
                "title": "Happy Koalas",
                "desc": "Keep {count} koala(s) happy (70+ happiness) for {days} consecutive days",
                "habitat": "eucalyptus_grove",
                "reward_money": 3000,
                "reward_rep": 15
            },
            "Kangaroo": {
                "title": "Bouncing Roos",
                "desc": "Keep {count} kangaroo(s) happy (70+ happiness) for {days} consecutive days",
                "habitat": "outback_savanna",
                "reward_money": 3500,
                "reward_rep": 15
            },
            "Emu": {
                "title": "Happy Emus",
                "desc": "Keep {count} emu(s) happy (70+ happiness) for {days} consecutive days",
                "habitat": "rainforest_aviary",
                "reward_money": 2500,
                "reward_rep": 12
            },
            "SaltwaterCroc": {
                "title": "Content Crocs",
                "desc": "Keep {count} saltwater crocodile(s) happy (70+ happiness) for {days} consecutive days",
                "habitat": "billabong",
                "reward_money": 4000,
                "reward_rep": 18
            },
            "Wombat": {
                "title": "Wombat Welfare",
                "desc": "Keep {count} wombat(s) happy (70+ happiness) for {days} consecutive days",
                "habitat": "outback_savanna",
                "reward_money": 3200,
                "reward_rep": 14
            },
            "Kookaburra": {
                "title": "Laughing Kookaburras",
                "desc": "Keep {count} kookaburra(s) happy (70+ happiness) for {days} consecutive days",
                "habitat": "rainforest_aviary",
                "reward_money": 2800,
                "reward_rep": 13
            },
            "Platypus": {
                "title": "Happy Platypuses",
                "desc": "Keep {count} platypus(es) happy (70+ happiness) for {days} consecutive days",
                "habitat": "billabong",
                "reward_money": 3500,
                "reward_rep": 16
            }
        }
    }
}


def _generate_keep_happy_mission(difficulty: str = "easy", mission_prefix: str = "starter") -> Mission:
    """Generate a KEEP_HAPPY mission."""
    mission_type = MissionType.KEEP_HAPPY

    # Select random animal
    animals = list(MISSION_TEMPLATES[mission_type]["animals"].keys())
    animal_type = random.choice(animals)
    template = MISSION_TEMPLATES[mission_type]["animals"][animal_type]

    # Set difficulty parameters
    if difficulty == "easy":
        count = random.randint(2, 3)
        days = random.randint(5, 7)
    elif difficulty == "medium":
        count = random.randint(3, 5)
        days = random.randint(7, 10)
    else:  # hard
        count = random.randint(5, 8)
        days = random.randint(10, 15)

    # Create mission
    title = template["title"]
    description = template["desc"].format(count=count, days=days)

    reward = MissionReward(
        money=template["reward_money"] * count,
        reputation=template["reward_rep"],
        description=f"${template['reward_money'] * count:,} and {template['reward_rep']} reputation points",
    )

    mission = Mission(
        mission_id=f"mission_{mission_prefix}_{animal_type}_{random.randint(1000, 9999)}",
        mission_type=mission_type,
        title=title,
        description=description,
        target_value=count,  # Number of animals that must complete the days requirement
        duration_days=days + 3,  # Give a few extra days buffer
        target_animal=animal_type,
        reward=reward,
        custom_data={"required_days": days},
    )

    # Keep attribute for compatibility with existing UI code paths
    mission.required_days = days
    return mission


def generate_starter_mission(difficulty: str = "easy") -> Mission:
    """
    Generate a random starter mission for a new game.
    
    Args:
        difficulty: Mission difficulty ("easy", "medium", "hard")
        
    Returns:
        Generated Mission instance
    """
    return _generate_keep_happy_mission(difficulty=difficulty, mission_prefix="starter")


def generate_random_mission(
    difficulty: str = "easy",
    zoo: Optional["Zoo"] = None,
    exclude_types: Optional[Set[MissionType]] = None,
) -> Mission:
    """
    Generate a random mission from a weighted mission pool.

    If possible, excludes mission types that are already active.
    """
    weighted_types = [
        (MissionType.KEEP_HAPPY, 0.35),
        (MissionType.VISITOR_COUNT, 0.20),
        (MissionType.PROFIT_TARGET, 0.20),
        (MissionType.BUILD_ENCLOSURES, 0.15),
        (MissionType.BREED_ANIMALS, 0.10),
    ]
    blocked = set(exclude_types or set())
    available = [(m_type, weight) for m_type, weight in weighted_types if m_type not in blocked]
    if not available:
        available = weighted_types

    mission_types = [m_type for m_type, _ in available]
    mission_weights = [weight for _, weight in available]
    selected_type = random.choices(mission_types, weights=mission_weights, k=1)[0]
    mission_id = f"mission_{selected_type.value}_{random.randint(1000, 9999)}"

    if selected_type == MissionType.KEEP_HAPPY:
        return _generate_keep_happy_mission(difficulty=difficulty, mission_prefix="auto")

    if selected_type == MissionType.VISITOR_COUNT:
        if difficulty == "easy":
            target, duration = random.randint(60, 90), random.randint(7, 9)
        elif difficulty == "medium":
            target, duration = random.randint(120, 180), random.randint(9, 11)
        else:
            target, duration = random.randint(220, 300), random.randint(11, 14)
        baseline_visitors = int(getattr(zoo, "_total_visitors_served", 0))
        return Mission(
            mission_id=mission_id,
            mission_type=selected_type,
            title="Visitor Boom",
            description=f"Attract {target} visitors within {duration} days.",
            target_value=target,
            duration_days=duration,
            reward=MissionReward(
                money=float(target * 28),
                reputation=12,
                description=f"${target * 28:,} and 12 reputation points",
            ),
            custom_data={"baseline_visitors": baseline_visitors},
        )

    if selected_type == MissionType.PROFIT_TARGET:
        if difficulty == "easy":
            target, duration = random.randint(1500, 2500), random.randint(8, 10)
        elif difficulty == "medium":
            target, duration = random.randint(3000, 5000), random.randint(10, 12)
        else:
            target, duration = random.randint(6000, 9000), random.randint(12, 15)
        baseline_profit = float(getattr(zoo, "_total_revenue", 0.0) - getattr(zoo, "_total_expenses", 0.0))
        return Mission(
            mission_id=mission_id,
            mission_type=selected_type,
            title="Profit Target",
            description=f"Earn ${target:,} profit within {duration} days.",
            target_value=target,
            duration_days=duration,
            reward=MissionReward(
                money=float(int(target * 0.45)),
                reputation=15,
                description=f"${int(target * 0.45):,} and 15 reputation points",
            ),
            custom_data={"baseline_profit": baseline_profit},
        )

    if selected_type == MissionType.BUILD_ENCLOSURES:
        if difficulty == "easy":
            target, duration = random.randint(1, 2), random.randint(8, 10)
        elif difficulty == "medium":
            target, duration = random.randint(2, 3), random.randint(10, 12)
        else:
            target, duration = random.randint(3, 4), random.randint(12, 15)
        baseline_enclosures = int(len(getattr(zoo, "enclosures", {}))) if zoo else 0
        return Mission(
            mission_id=mission_id,
            mission_type=selected_type,
            title="Expand the Park",
            description=f"Build {target} new enclosure(s) within {duration} days.",
            target_value=target,
            duration_days=duration,
            reward=MissionReward(
                money=float(target * 2200),
                reputation=10 + target,
                description=f"${target * 2200:,} and {10 + target} reputation points",
            ),
            custom_data={"baseline_enclosures": baseline_enclosures},
        )

    # MissionType.BREED_ANIMALS
    if difficulty == "easy":
        target, duration = random.randint(1, 2), random.randint(10, 12)
    elif difficulty == "medium":
        target, duration = random.randint(2, 3), random.randint(12, 14)
    else:
        target, duration = random.randint(3, 4), random.randint(14, 16)
    baseline_births = int(getattr(zoo, "_animals_born", 0))
    return Mission(
        mission_id=mission_id,
        mission_type=selected_type,
        title="Baby Boom",
        description=f"Welcome {target} newborn animal(s) within {duration} days.",
        target_value=target,
        duration_days=duration,
        reward=MissionReward(
            money=float(target * 2600),
            reputation=14 + target,
            description=f"${target * 2600:,} and {14 + target} reputation points",
        ),
        custom_data={"baseline_births": baseline_births},
    )


def get_mission_animal_habitat(mission: Mission) -> Optional[str]:
    """
    Get the required habitat type for a mission's target animal.
    
    Args:
        mission: Mission to check
        
    Returns:
        Habitat type string or None
    """
    if mission.mission_type == MissionType.KEEP_HAPPY and mission.target_animal:
        templates = MISSION_TEMPLATES[MissionType.KEEP_HAPPY]["animals"]
        if mission.target_animal in templates:
            return templates[mission.target_animal]["habitat"]
    return None
