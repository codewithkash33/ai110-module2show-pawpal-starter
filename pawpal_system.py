"""PawPal+ System — Logic layer with all backend classes."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import List


# ---------------------------------------------------------------------------
# Task
# ---------------------------------------------------------------------------

@dataclass
class Task:
    """Represents a single pet-care activity."""
    title: str
    duration_minutes: int
    priority: str = "medium"  # "low", "medium", "high"
    category: str = "general"  # e.g. "walk", "feeding", "meds", "grooming", "enrichment"
    completed: bool = False

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.completed = True

    def mark_incomplete(self) -> None:
        """Reset this task to incomplete."""
        self.completed = False

    def __str__(self) -> str:
        """Return a readable string representation."""
        status = "done" if self.completed else "pending"
        return (f"{self.title} [{self.category}] — {self.duration_minutes} min, "
                f"priority: {self.priority}, status: {status}")


# ---------------------------------------------------------------------------
# Pet
# ---------------------------------------------------------------------------

class Pet:
    """Stores pet details and manages a list of tasks for this pet."""

    def __init__(self, name: str, species: str, age: int = 0, breed: str = "") -> None:
        self.name = name
        self.species = species
        self.age = age
        self.breed = breed
        self._tasks: List[Task] = []

    def add_task(self, task: Task) -> None:
        """Add a care task for this pet."""
        self._tasks.append(task)

    def remove_task(self, title: str) -> bool:
        """Remove a task by title. Returns True if found and removed."""
        for i, t in enumerate(self._tasks):
            if t.title == title:
                self._tasks.pop(i)
                return True
        return False

    def get_tasks(self) -> List[Task]:
        """Return all tasks assigned to this pet."""
        return list(self._tasks)

    def get_pending_tasks(self) -> List[Task]:
        """Return only incomplete tasks."""
        return [t for t in self._tasks if not t.completed]

    @property
    def task_count(self) -> int:
        """Return the number of tasks for this pet."""
        return len(self._tasks)

    def __str__(self) -> str:
        """Return a readable string representation."""
        return f"{self.name} ({self.species}, age {self.age}) — {self.task_count} task(s)"


# ---------------------------------------------------------------------------
# Owner
# ---------------------------------------------------------------------------

class Owner:
    """Manages multiple pets and provides access to all their tasks."""

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

    def get_all_tasks(self) -> List[Task]:
        """Retrieve every task across all pets."""
        tasks: List[Task] = []
        for pet in self._pets:
            tasks.extend(pet.get_tasks())
        return tasks

    def get_all_pending_tasks(self) -> List[Task]:
        """Retrieve only incomplete tasks across all pets."""
        tasks: List[Task] = []
        for pet in self._pets:
            tasks.extend(pet.get_pending_tasks())
        return tasks


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
            lines.append(f"  {idx}. {task}")
        lines.append("")
        lines.append(f"Total duration: {self.total_duration} minutes")
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Scheduler
# ---------------------------------------------------------------------------

class Scheduler:
    """The 'brain' that retrieves, organises, and schedules tasks across pets."""

    PRIORITY_WEIGHT = {"high": 3, "medium": 2, "low": 1}

    def __init__(self, owner: Owner) -> None:
        self.owner = owner
        self.time_budget: int = owner.available_time_minutes

    def _collect_tasks(self) -> List[Task]:
        """Pull all pending tasks from the owner's pets."""
        return self.owner.get_all_pending_tasks()

    def generate_schedule(self) -> DailyPlan:
        """Build and return a DailyPlan respecting the time budget."""
        plan = DailyPlan(plan_date=str(date.today()))
        tasks = self._collect_tasks()

        # Sort by priority (high first), then shortest duration for ties
        sorted_tasks = sorted(
            tasks,
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

        all_tasks = self._collect_tasks()

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

        skipped = [t for t in all_tasks if t not in plan.scheduled_tasks]
        if skipped:
            lines.append("Skipped tasks (did not fit):")
            for t in skipped:
                lines.append(f"  - {t}")

        return "\n".join(lines)
