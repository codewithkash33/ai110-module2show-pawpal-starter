"""PawPal+ System — Logic layer with all backend classes."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import List


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class Pet:
    """Represents a pet with basic profile information."""
    name: str
    species: str  # e.g. "dog", "cat", "other"
    age: int = 0
    breed: str = ""


@dataclass
class Task:
    """A single pet-care task (walk, feeding, meds, etc.)."""
    title: str
    duration_minutes: int
    priority: str = "medium"  # "low", "medium", "high"
    category: str = "general"  # e.g. "walk", "feeding", "meds", "grooming", "enrichment"
    pet_name: str = ""


# ---------------------------------------------------------------------------
# Owner
# ---------------------------------------------------------------------------

class Owner:
    """Represents the pet owner, holds pets and preferences."""

    def __init__(self, name: str, available_time_minutes: int = 120,
                 preferences: List[str] | None = None) -> None:
        self.name = name
        self.available_time_minutes = available_time_minutes
        self.preferences: List[str] = preferences or []
        self._pets: List[Pet] = []

    def add_pet(self, pet: Pet) -> None:
        """Register a pet under this owner."""
        self._pets.append(pet)

    def remove_pet(self, pet_name: str) -> bool:
        """Remove a pet by name. Returns True if found and removed."""
        for i, p in enumerate(self._pets):
            if p.name == pet_name:
                self._pets.pop(i)
                return True
        return False

    def get_pets(self) -> List[Pet]:
        """Return the list of owner's pets."""
        return list(self._pets)


# ---------------------------------------------------------------------------
# Daily Plan
# ---------------------------------------------------------------------------

@dataclass
class DailyPlan:
    """The output of the scheduler — an ordered list of tasks for a day."""
    plan_date: str = ""
    scheduled_tasks: List[Task] = field(default_factory=list)
    total_duration: int = 0

    def add_task(self, task: Task) -> None:
        """Append a task to the plan and update total duration."""
        self.scheduled_tasks.append(task)
        self.total_duration += task.duration_minutes

    def get_explanation(self) -> str:
        """Return a human-readable explanation of the plan."""
        if not self.scheduled_tasks:
            return "No tasks scheduled for today."

        lines = [f"Daily Plan for {self.plan_date}:", ""]
        for idx, task in enumerate(self.scheduled_tasks, start=1):
            lines.append(
                f"  {idx}. {task.title} ({task.duration_minutes} min, "
                f"priority: {task.priority}, category: {task.category})"
            )
        lines.append("")
        lines.append(f"Total duration: {self.total_duration} minutes")
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Scheduler
# ---------------------------------------------------------------------------

class Scheduler:
    """Generates a daily care plan based on tasks, time budget, and priorities."""

    PRIORITY_WEIGHT = {"high": 3, "medium": 2, "low": 1}

    def __init__(self, owner: Owner, tasks: List[Task] | None = None) -> None:
        self.owner = owner
        self.tasks: List[Task] = tasks or []
        self.time_budget: int = owner.available_time_minutes

    def generate_schedule(self) -> DailyPlan:
        """Build and return a DailyPlan respecting the time budget."""
        plan = DailyPlan(plan_date=str(date.today()))

        # Sort tasks by priority (high first), then shortest duration for ties
        sorted_tasks = sorted(
            self.tasks,
            key=lambda t: (-self.PRIORITY_WEIGHT.get(t.priority, 0), t.duration_minutes),
        )

        remaining = self.time_budget
        for task in sorted_tasks:
            if task.duration_minutes <= remaining:
                plan.add_task(task)
                remaining -= task.duration_minutes

        return plan

    def explain_plan(self, plan: DailyPlan) -> str:
        """Provide reasoning for why tasks were chosen and ordered."""
        if not plan.scheduled_tasks:
            return "No tasks could fit within the available time budget."

        lines = ["Schedule explanation:", ""]
        lines.append(
            f"Time budget: {self.time_budget} minutes  |  "
            f"Used: {plan.total_duration} minutes  |  "
            f"Remaining: {self.time_budget - plan.total_duration} minutes"
        )
        lines.append("")
        lines.append("Tasks were sorted by priority (high → medium → low), "
                      "then by shortest duration to maximise the number of tasks that fit.")
        lines.append("")

        skipped = [t for t in self.tasks if t not in plan.scheduled_tasks]
        if skipped:
            lines.append("Skipped tasks (did not fit):")
            for t in skipped:
                lines.append(f"  - {t.title} ({t.duration_minutes} min, {t.priority})")

        return "\n".join(lines)
