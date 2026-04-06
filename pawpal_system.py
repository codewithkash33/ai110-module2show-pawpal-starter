"""PawPal+ System — Logic layer with all backend classes."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import List


# ---------------------------------------------------------------------------
# Task
# ---------------------------------------------------------------------------

@dataclass
class Task:
    """Represents a single pet-care activity."""
    title: str
    duration_minutes: int
    priority: str = "medium"        # "low", "medium", "high"
    category: str = "general"       # e.g. "walk", "feeding", "meds", "grooming", "enrichment"
    scheduled_time: str = ""        # "HH:MM" format, e.g. "08:30"
    frequency: str = "once"         # "once", "daily", "weekly"
    completed: bool = False
    pet_name: str = ""              # which pet this task belongs to

    def mark_complete(self) -> Task | None:
        """Mark this task as completed. Returns a new Task for the next occurrence if recurring."""
        self.completed = True
        if self.frequency in ("daily", "weekly"):
            return self._create_next_occurrence()
        return None

    def mark_incomplete(self) -> None:
        """Reset this task to incomplete."""
        self.completed = False

    def _create_next_occurrence(self) -> Task:
        """Create the next occurrence of a recurring task."""
        delta = timedelta(days=1) if self.frequency == "daily" else timedelta(weeks=1)
        next_date = date.today() + delta
        return Task(
            title=f"{self.title}",
            duration_minutes=self.duration_minutes,
            priority=self.priority,
            category=self.category,
            scheduled_time=self.scheduled_time,
            frequency=self.frequency,
            completed=False,
            pet_name=self.pet_name,
        )

    @property
    def _time_sort_key(self) -> tuple:
        """Return a sortable key from the scheduled_time string."""
        if self.scheduled_time:
            parts = self.scheduled_time.split(":")
            return (int(parts[0]), int(parts[1]))
        return (99, 99)  # unscheduled tasks sort to the end

    def __str__(self) -> str:
        """Return a readable string representation."""
        status = "done" if self.completed else "pending"
        time_str = f" @ {self.scheduled_time}" if self.scheduled_time else ""
        freq_str = f" [{self.frequency}]" if self.frequency != "once" else ""
        return (f"{self.title} [{self.category}]{time_str}{freq_str} — "
                f"{self.duration_minutes} min, priority: {self.priority}, status: {status}")


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
        """Add a care task for this pet and tag it with the pet's name."""
        task.pet_name = self.name
        self._tasks.append(task)

    def remove_task(self, title: str) -> bool:
        """Remove a task by title. Returns True if found and removed."""
        for i, t in enumerate(self._tasks):
            if t.title == title:
                self._tasks.pop(i)
                return True
        return False

    def complete_task(self, title: str) -> str | None:
        """Mark a task complete; if recurring, auto-create the next occurrence. Returns a message if recurring."""
        for t in self._tasks:
            if t.title == title and not t.completed:
                next_task = t.mark_complete()
                if next_task is not None:
                    self.add_task(next_task)
                    return f"Recurring task '{title}' completed — next occurrence added."
                return None
        return None

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

    # ── Collect ────────────────────────────────────────────────

    def _collect_tasks(self) -> List[Task]:
        """Pull all pending tasks from the owner's pets."""
        return self.owner.get_all_pending_tasks()

    # ── Sorting ────────────────────────────────────────────────

    def sort_by_time(self, tasks: List[Task] | None = None) -> List[Task]:
        """Sort tasks by their scheduled_time (HH:MM). Unscheduled tasks go last."""
        source = tasks if tasks is not None else self._collect_tasks()
        return sorted(source, key=lambda t: t._time_sort_key)

    def sort_by_priority(self, tasks: List[Task] | None = None) -> List[Task]:
        """Sort tasks by priority (high → low), then shortest duration."""
        source = tasks if tasks is not None else self._collect_tasks()
        return sorted(
            source,
            key=lambda t: (-self.PRIORITY_WEIGHT.get(t.priority, 0), t.duration_minutes),
        )

    # ── Filtering ──────────────────────────────────────────────

    def filter_by_status(self, completed: bool, tasks: List[Task] | None = None) -> List[Task]:
        """Filter tasks by completion status."""
        source = tasks if tasks is not None else self.owner.get_all_tasks()
        return [t for t in source if t.completed == completed]

    def filter_by_pet(self, pet_name: str, tasks: List[Task] | None = None) -> List[Task]:
        """Filter tasks belonging to a specific pet."""
        source = tasks if tasks is not None else self.owner.get_all_tasks()
        return [t for t in source if t.pet_name == pet_name]

    def filter_by_category(self, category: str, tasks: List[Task] | None = None) -> List[Task]:
        """Filter tasks by category."""
        source = tasks if tasks is not None else self.owner.get_all_tasks()
        return [t for t in source if t.category == category]

    # ── Conflict Detection ─────────────────────────────────────

    def detect_conflicts(self, tasks: List[Task] | None = None) -> List[str]:
        """Detect tasks that overlap in time. Returns a list of warning messages."""
        source = tasks if tasks is not None else self._collect_tasks()
        # Only check tasks that have a scheduled_time
        timed = [t for t in source if t.scheduled_time]
        timed_sorted = sorted(timed, key=lambda t: t._time_sort_key)

        warnings: List[str] = []
        for i in range(len(timed_sorted)):
            for j in range(i + 1, len(timed_sorted)):
                a, b = timed_sorted[i], timed_sorted[j]
                # Calculate end time of task a
                a_start_h, a_start_m = a._time_sort_key
                a_end_total = a_start_h * 60 + a_start_m + a.duration_minutes
                b_start_h, b_start_m = b._time_sort_key
                b_start_total = b_start_h * 60 + b_start_m
                if b_start_total < a_end_total:
                    warnings.append(
                        f"⚠ Conflict: '{a.title}' ({a.scheduled_time}, {a.duration_minutes} min) "
                        f"overlaps with '{b.title}' ({b.scheduled_time}, {b.duration_minutes} min)"
                    )
        return warnings

    # ── Schedule Generation ────────────────────────────────────

    def generate_schedule(self) -> DailyPlan:
        """Build and return a DailyPlan respecting the time budget."""
        plan = DailyPlan(plan_date=str(date.today()))
        tasks = self._collect_tasks()

        # Sort by priority (high first), then shortest duration for ties
        sorted_tasks = self.sort_by_priority(tasks)

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

        # Conflict warnings
        conflicts = self.detect_conflicts(plan.scheduled_tasks)
        if conflicts:
            lines.append("")
            lines.append("Conflicts detected:")
            lines.extend(f"  {w}" for w in conflicts)

        return "\n".join(lines)
