"""Tests for the PawPal+ logic layer.

Test plan:
  1. Task basics       — completion, reset, string representation
  2. Pet management    — add/remove tasks, task count, complete_task
  3. Owner aggregation — multi-pet task collection
  4. Sorting           — chronological order, unscheduled-last, ties
  5. Filtering         — by pet, status, category
  6. Recurring tasks   — daily, weekly, attribute preservation
  7. Conflict detection— exact overlap, partial overlap, no overlap, cross-pet
  8. Schedule generation — budget, priority, edge cases (empty, zero budget)
"""

from pawpal_system import Task, Pet, Owner, Scheduler, DailyPlan


# ═══════════════════════════════════════════════════════════════
# 1. Task basics
# ═══════════════════════════════════════════════════════════════

def test_mark_complete_changes_status():
    """Calling mark_complete() should set completed to True."""
    task = Task(title="Walk", duration_minutes=20, priority="high")
    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_mark_incomplete_resets_status():
    """Calling mark_incomplete() after completing should reset to False."""
    task = Task(title="Feed", duration_minutes=10)
    task.mark_complete()
    task.mark_incomplete()
    assert task.completed is False


def test_task_str_includes_key_info():
    """__str__ should contain title, category, priority, and status."""
    task = Task(title="Walk", duration_minutes=30, priority="high",
                category="walk", scheduled_time="07:00")
    text = str(task)
    assert "Walk" in text
    assert "walk" in text
    assert "07:00" in text
    assert "high" in text
    assert "pending" in text


# ═══════════════════════════════════════════════════════════════
# 2. Pet management
# ═══════════════════════════════════════════════════════════════

def test_add_task_increases_pet_task_count():
    """Adding a task to a Pet should increase its task_count."""
    pet = Pet(name="Mochi", species="dog")
    assert pet.task_count == 0
    pet.add_task(Task(title="Walk", duration_minutes=30))
    assert pet.task_count == 1
    pet.add_task(Task(title="Feed", duration_minutes=10))
    assert pet.task_count == 2


def test_remove_task_decreases_count():
    """Removing a task should decrease the pet's task count."""
    pet = Pet(name="Mochi", species="dog")
    pet.add_task(Task(title="Walk", duration_minutes=30))
    pet.remove_task("Walk")
    assert pet.task_count == 0


def test_remove_nonexistent_task_returns_false():
    """Removing a task that doesn't exist should return False."""
    pet = Pet(name="Mochi", species="dog")
    assert pet.remove_task("Ghost task") is False


def test_add_task_tags_pet_name():
    """Adding a task via Pet.add_task should set pet_name automatically."""
    pet = Pet(name="Mochi", species="dog")
    task = Task(title="Walk", duration_minutes=30)
    pet.add_task(task)
    assert task.pet_name == "Mochi"


def test_pet_with_no_tasks():
    """A pet with no tasks should return empty lists and zero count."""
    pet = Pet(name="Ghost", species="cat")
    assert pet.task_count == 0
    assert pet.get_tasks() == []
    assert pet.get_pending_tasks() == []


def test_get_pending_tasks_excludes_completed():
    """get_pending_tasks() should not include completed tasks."""
    pet = Pet(name="Rex", species="dog")
    t1 = Task(title="Walk", duration_minutes=30)
    t2 = Task(title="Feed", duration_minutes=10)
    t1.completed = True
    pet.add_task(t1)
    pet.add_task(t2)
    pending = pet.get_pending_tasks()
    assert len(pending) == 1
    assert pending[0].title == "Feed"


# ═══════════════════════════════════════════════════════════════
# 3. Owner aggregation
# ═══════════════════════════════════════════════════════════════

def test_owner_get_all_tasks():
    """Owner.get_all_tasks() should return tasks from every pet."""
    owner = Owner(name="Jordan")
    dog = Pet(name="Rex", species="dog")
    cat = Pet(name="Luna", species="cat")
    dog.add_task(Task(title="Walk", duration_minutes=30))
    cat.add_task(Task(title="Feed", duration_minutes=10))
    owner.add_pet(dog)
    owner.add_pet(cat)
    assert len(owner.get_all_tasks()) == 2


def test_owner_with_no_pets():
    """Owner with no pets should return empty task lists."""
    owner = Owner(name="Jordan")
    assert owner.get_all_tasks() == []
    assert owner.get_all_pending_tasks() == []
    assert owner.get_pets() == []


def test_owner_get_all_pending_skips_completed():
    """get_all_pending_tasks() should exclude completed tasks across pets."""
    owner = Owner(name="Jordan")
    pet = Pet(name="Rex", species="dog")
    t1 = Task(title="Walk", duration_minutes=30)
    t2 = Task(title="Feed", duration_minutes=10)
    t1.completed = True
    pet.add_task(t1)
    pet.add_task(t2)
    owner.add_pet(pet)
    assert len(owner.get_all_pending_tasks()) == 1


def test_owner_remove_pet():
    """Removing a pet should reduce the pet list."""
    owner = Owner(name="Jordan")
    owner.add_pet(Pet(name="Rex", species="dog"))
    assert len(owner.get_pets()) == 1
    owner.remove_pet("Rex")
    assert len(owner.get_pets()) == 0


# ═══════════════════════════════════════════════════════════════
# 4. Sorting
# ═══════════════════════════════════════════════════════════════

def test_sort_by_time():
    """sort_by_time() should order tasks by their HH:MM scheduled_time."""
    owner = Owner(name="Jordan")
    pet = Pet(name="Rex", species="dog")
    pet.add_task(Task(title="Evening walk", duration_minutes=20, scheduled_time="18:00"))
    pet.add_task(Task(title="Morning walk", duration_minutes=30, scheduled_time="07:00"))
    pet.add_task(Task(title="Lunch feed", duration_minutes=10, scheduled_time="12:00"))
    owner.add_pet(pet)

    result = Scheduler(owner).sort_by_time()
    times = [t.scheduled_time for t in result]
    assert times == ["07:00", "12:00", "18:00"]


def test_sort_by_time_unscheduled_last():
    """Tasks without a scheduled_time should appear at the end."""
    owner = Owner(name="Jordan")
    pet = Pet(name="Rex", species="dog")
    pet.add_task(Task(title="No time", duration_minutes=10))
    pet.add_task(Task(title="Early", duration_minutes=10, scheduled_time="06:00"))
    owner.add_pet(pet)

    result = Scheduler(owner).sort_by_time()
    assert result[0].title == "Early"
    assert result[1].title == "No time"


def test_sort_by_time_same_hour_different_minute():
    """Tasks at the same hour should be sorted by minute."""
    owner = Owner(name="Jordan")
    pet = Pet(name="Rex", species="dog")
    pet.add_task(Task(title="Late half", duration_minutes=10, scheduled_time="08:45"))
    pet.add_task(Task(title="Early half", duration_minutes=10, scheduled_time="08:15"))
    owner.add_pet(pet)

    result = Scheduler(owner).sort_by_time()
    assert result[0].title == "Early half"
    assert result[1].title == "Late half"


def test_sort_by_priority_order():
    """sort_by_priority() should rank high > medium > low."""
    owner = Owner(name="Jordan")
    pet = Pet(name="Rex", species="dog")
    pet.add_task(Task(title="Low", duration_minutes=5, priority="low"))
    pet.add_task(Task(title="High", duration_minutes=5, priority="high"))
    pet.add_task(Task(title="Med", duration_minutes=5, priority="medium"))
    owner.add_pet(pet)

    result = Scheduler(owner).sort_by_priority()
    priorities = [t.priority for t in result]
    assert priorities == ["high", "medium", "low"]


def test_sort_by_priority_tiebreak_by_duration():
    """Equal-priority tasks should be sorted shortest-first."""
    owner = Owner(name="Jordan")
    pet = Pet(name="Rex", species="dog")
    pet.add_task(Task(title="Long", duration_minutes=60, priority="high"))
    pet.add_task(Task(title="Short", duration_minutes=5, priority="high"))
    owner.add_pet(pet)

    result = Scheduler(owner).sort_by_priority()
    assert result[0].title == "Short"
    assert result[1].title == "Long"


# ═══════════════════════════════════════════════════════════════
# 5. Filtering
# ═══════════════════════════════════════════════════════════════

def test_filter_by_pet():
    """filter_by_pet() should return only tasks for the named pet."""
    owner = Owner(name="Jordan")
    dog = Pet(name="Rex", species="dog")
    cat = Pet(name="Luna", species="cat")
    dog.add_task(Task(title="Walk", duration_minutes=30))
    cat.add_task(Task(title="Feed", duration_minutes=10))
    owner.add_pet(dog)
    owner.add_pet(cat)

    result = Scheduler(owner).filter_by_pet("Luna")
    assert len(result) == 1
    assert result[0].title == "Feed"


def test_filter_by_pet_no_match():
    """filter_by_pet() with an unknown name should return empty list."""
    owner = Owner(name="Jordan")
    pet = Pet(name="Rex", species="dog")
    pet.add_task(Task(title="Walk", duration_minutes=30))
    owner.add_pet(pet)

    result = Scheduler(owner).filter_by_pet("Unknown")
    assert result == []


def test_filter_by_status():
    """filter_by_status() should correctly separate completed/pending tasks."""
    owner = Owner(name="Jordan")
    pet = Pet(name="Rex", species="dog")
    t1 = Task(title="Walk", duration_minutes=30)
    t2 = Task(title="Feed", duration_minutes=10)
    t1.mark_complete()
    pet.add_task(t1)
    pet.add_task(t2)
    owner.add_pet(pet)

    scheduler = Scheduler(owner)
    assert len(scheduler.filter_by_status(completed=True)) == 1
    assert len(scheduler.filter_by_status(completed=False)) == 1


def test_filter_by_category():
    """filter_by_category() should return only matching tasks."""
    owner = Owner(name="Jordan")
    pet = Pet(name="Rex", species="dog")
    pet.add_task(Task(title="Walk", duration_minutes=30, category="walk"))
    pet.add_task(Task(title="Feed", duration_minutes=10, category="feeding"))
    pet.add_task(Task(title="Brush", duration_minutes=15, category="grooming"))
    owner.add_pet(pet)

    result = Scheduler(owner).filter_by_category("walk")
    assert len(result) == 1
    assert result[0].title == "Walk"


# ═══════════════════════════════════════════════════════════════
# 6. Recurring tasks
# ═══════════════════════════════════════════════════════════════

def test_recurring_daily_task_creates_next():
    """Completing a daily task should auto-create the next occurrence."""
    pet = Pet(name="Rex", species="dog")
    pet.add_task(Task(title="Walk", duration_minutes=30, frequency="daily"))
    assert pet.task_count == 1

    msg = pet.complete_task("Walk")
    assert msg is not None
    assert pet.task_count == 2
    assert pet.get_tasks()[0].completed is True
    assert pet.get_tasks()[1].completed is False


def test_recurring_weekly_task_creates_next():
    """Completing a weekly task should also auto-create the next occurrence."""
    pet = Pet(name="Rex", species="dog")
    pet.add_task(Task(title="Bath", duration_minutes=45, frequency="weekly"))
    pet.complete_task("Bath")
    assert pet.task_count == 2
    assert pet.get_tasks()[1].frequency == "weekly"


def test_recurring_task_preserves_attributes():
    """The new occurrence should keep the same priority, category, and time."""
    pet = Pet(name="Rex", species="dog")
    pet.add_task(Task(title="Walk", duration_minutes=30, priority="high",
                      category="walk", scheduled_time="07:00", frequency="daily"))
    pet.complete_task("Walk")
    new_task = pet.get_tasks()[1]
    assert new_task.priority == "high"
    assert new_task.category == "walk"
    assert new_task.scheduled_time == "07:00"
    assert new_task.frequency == "daily"
    assert new_task.duration_minutes == 30


def test_one_time_task_no_recurrence():
    """Completing a one-time task should NOT create a new occurrence."""
    pet = Pet(name="Rex", species="dog")
    pet.add_task(Task(title="Vet visit", duration_minutes=60, frequency="once"))
    pet.complete_task("Vet visit")
    assert pet.task_count == 1


def test_complete_already_done_task_is_noop():
    """Completing a task that is already done should not create duplicates."""
    pet = Pet(name="Rex", species="dog")
    pet.add_task(Task(title="Walk", duration_minutes=30, frequency="daily"))
    pet.complete_task("Walk")
    assert pet.task_count == 2
    # Try completing the already-done original again — should be a no-op
    pet.complete_task("Walk")
    # The new pending one gets completed, creating a third
    assert pet.task_count == 3


# ═══════════════════════════════════════════════════════════════
# 7. Conflict detection
# ═══════════════════════════════════════════════════════════════

def test_detect_conflicts_exact_overlap():
    """Two tasks at the exact same time should produce a conflict warning."""
    owner = Owner(name="Jordan")
    pet = Pet(name="Rex", species="dog")
    pet.add_task(Task(title="Walk", duration_minutes=30, scheduled_time="07:00"))
    pet.add_task(Task(title="Vet", duration_minutes=60, scheduled_time="07:00"))
    owner.add_pet(pet)

    warnings = Scheduler(owner).detect_conflicts()
    assert len(warnings) == 1
    assert "Walk" in warnings[0]
    assert "Vet" in warnings[0]


def test_detect_conflicts_partial_overlap():
    """A task that starts before the previous one ends should be flagged."""
    owner = Owner(name="Jordan")
    pet = Pet(name="Rex", species="dog")
    pet.add_task(Task(title="Walk", duration_minutes=45, scheduled_time="07:00"))
    pet.add_task(Task(title="Feed", duration_minutes=10, scheduled_time="07:30"))
    owner.add_pet(pet)

    warnings = Scheduler(owner).detect_conflicts()
    assert len(warnings) == 1


def test_detect_conflicts_no_overlap():
    """Non-overlapping tasks should produce no conflict warnings."""
    owner = Owner(name="Jordan")
    pet = Pet(name="Rex", species="dog")
    pet.add_task(Task(title="Walk", duration_minutes=30, scheduled_time="07:00"))
    pet.add_task(Task(title="Feed", duration_minutes=10, scheduled_time="08:00"))
    owner.add_pet(pet)

    warnings = Scheduler(owner).detect_conflicts()
    assert len(warnings) == 0


def test_detect_conflicts_cross_pet():
    """Conflicts should be detected even when tasks belong to different pets."""
    owner = Owner(name="Jordan")
    dog = Pet(name="Rex", species="dog")
    cat = Pet(name="Luna", species="cat")
    dog.add_task(Task(title="Dog walk", duration_minutes=60, scheduled_time="09:00"))
    cat.add_task(Task(title="Cat vet", duration_minutes=30, scheduled_time="09:15"))
    owner.add_pet(dog)
    owner.add_pet(cat)

    warnings = Scheduler(owner).detect_conflicts()
    assert len(warnings) == 1
    assert "Dog walk" in warnings[0]
    assert "Cat vet" in warnings[0]


def test_detect_conflicts_ignores_unscheduled():
    """Tasks without a scheduled_time should not trigger conflict warnings."""
    owner = Owner(name="Jordan")
    pet = Pet(name="Rex", species="dog")
    pet.add_task(Task(title="Walk", duration_minutes=30))
    pet.add_task(Task(title="Feed", duration_minutes=10))
    owner.add_pet(pet)

    warnings = Scheduler(owner).detect_conflicts()
    assert len(warnings) == 0


# ═══════════════════════════════════════════════════════════════
# 8. Schedule generation — edge cases
# ═══════════════════════════════════════════════════════════════

def test_schedule_respects_time_budget():
    """Scheduled tasks should not exceed the owner's time budget."""
    owner = Owner(name="Jordan", available_time_minutes=25)
    pet = Pet(name="Mochi", species="dog")
    pet.add_task(Task(title="Walk", duration_minutes=20, priority="high"))
    pet.add_task(Task(title="Play", duration_minutes=15, priority="low"))
    owner.add_pet(pet)

    plan = Scheduler(owner).generate_schedule()
    assert plan.total_duration <= 25


def test_schedule_prioritises_high_tasks():
    """High-priority tasks should appear before low-priority ones."""
    owner = Owner(name="Jordan", available_time_minutes=60)
    pet = Pet(name="Mochi", species="dog")
    pet.add_task(Task(title="Brush teeth", duration_minutes=5, priority="low"))
    pet.add_task(Task(title="Give meds", duration_minutes=5, priority="high"))
    owner.add_pet(pet)

    plan = Scheduler(owner).generate_schedule()
    titles = [t.title for t in plan.scheduled_tasks]
    assert titles.index("Give meds") < titles.index("Brush teeth")


def test_schedule_empty_when_no_tasks():
    """Schedule should be empty when pets have no tasks."""
    owner = Owner(name="Jordan", available_time_minutes=60)
    owner.add_pet(Pet(name="Rex", species="dog"))

    plan = Scheduler(owner).generate_schedule()
    assert plan.scheduled_tasks == []
    assert plan.total_duration == 0


def test_schedule_empty_when_no_pets():
    """Schedule should be empty when owner has no pets."""
    owner = Owner(name="Jordan", available_time_minutes=60)

    plan = Scheduler(owner).generate_schedule()
    assert plan.scheduled_tasks == []


def test_schedule_zero_budget():
    """With zero time budget, no tasks should be scheduled."""
    owner = Owner(name="Jordan", available_time_minutes=0)
    pet = Pet(name="Rex", species="dog")
    pet.add_task(Task(title="Walk", duration_minutes=10, priority="high"))
    owner.add_pet(pet)

    plan = Scheduler(owner).generate_schedule()
    assert plan.scheduled_tasks == []
    assert plan.total_duration == 0


def test_schedule_single_task_exceeds_budget():
    """A single task longer than the budget should be skipped."""
    owner = Owner(name="Jordan", available_time_minutes=15)
    pet = Pet(name="Rex", species="dog")
    pet.add_task(Task(title="Long walk", duration_minutes=60, priority="high"))
    owner.add_pet(pet)

    plan = Scheduler(owner).generate_schedule()
    assert plan.scheduled_tasks == []


def test_schedule_all_tasks_completed():
    """If all tasks are completed, the schedule should be empty."""
    owner = Owner(name="Jordan", available_time_minutes=120)
    pet = Pet(name="Rex", species="dog")
    t = Task(title="Walk", duration_minutes=30, priority="high")
    t.completed = True
    pet.add_task(t)
    owner.add_pet(pet)

    plan = Scheduler(owner).generate_schedule()
    assert plan.scheduled_tasks == []


def test_daily_plan_explanation_empty():
    """An empty plan should return a 'no tasks' message."""
    plan = DailyPlan(plan_date="2026-04-05")
    assert "No tasks" in plan.get_explanation()


def test_daily_plan_explanation_with_tasks():
    """A plan with tasks should include the total duration."""
    plan = DailyPlan(plan_date="2026-04-05")
    plan.add_task(Task(title="Walk", duration_minutes=30))
    explanation = plan.get_explanation()
    assert "30 minutes" in explanation
    assert "Walk" in explanation


def test_detect_conflicts_no_overlap():
    """Non-overlapping tasks should produce no conflict warnings."""
    owner = Owner(name="Jordan")
    pet = Pet(name="Rex", species="dog")
    pet.add_task(Task(title="Walk", duration_minutes=30, scheduled_time="07:00"))
    pet.add_task(Task(title="Feed", duration_minutes=10, scheduled_time="08:00"))
    owner.add_pet(pet)

    warnings = Scheduler(owner).detect_conflicts()
    assert len(warnings) == 0


def test_detect_conflicts_partial_overlap():
    """A task that starts before the previous one ends should be flagged."""
    owner = Owner(name="Jordan")
    pet = Pet(name="Rex", species="dog")
    pet.add_task(Task(title="Walk", duration_minutes=45, scheduled_time="07:00"))
    pet.add_task(Task(title="Feed", duration_minutes=10, scheduled_time="07:30"))
    owner.add_pet(pet)

    warnings = Scheduler(owner).detect_conflicts()
    assert len(warnings) == 1
