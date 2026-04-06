"""Tests for the PawPal+ logic layer."""

from pawpal_system import Task, Pet, Owner, Scheduler


# ── Task completion ───────────────────────────────────────────

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


# ── Task addition to Pet ──────────────────────────────────────

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


# ── Owner aggregation ────────────────────────────────────────

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


# ── Scheduler ────────────────────────────────────────────────

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


# ── Sorting ──────────────────────────────────────────────────

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


# ── Filtering ────────────────────────────────────────────────

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


# ── Recurring tasks ──────────────────────────────────────────

def test_recurring_daily_task_creates_next():
    """Completing a daily task should auto-create the next occurrence."""
    pet = Pet(name="Rex", species="dog")
    pet.add_task(Task(title="Walk", duration_minutes=30, frequency="daily"))
    assert pet.task_count == 1

    msg = pet.complete_task("Walk")
    assert msg is not None
    assert pet.task_count == 2
    # Original is done, new one is pending
    assert pet.get_tasks()[0].completed is True
    assert pet.get_tasks()[1].completed is False


def test_one_time_task_no_recurrence():
    """Completing a one-time task should NOT create a new occurrence."""
    pet = Pet(name="Rex", species="dog")
    pet.add_task(Task(title="Vet visit", duration_minutes=60, frequency="once"))
    pet.complete_task("Vet visit")
    assert pet.task_count == 1


# ── Conflict detection ───────────────────────────────────────

def test_detect_conflicts_overlapping():
    """Two tasks at the same time should produce a conflict warning."""
    owner = Owner(name="Jordan")
    pet = Pet(name="Rex", species="dog")
    pet.add_task(Task(title="Walk", duration_minutes=30, scheduled_time="07:00"))
    pet.add_task(Task(title="Vet", duration_minutes=60, scheduled_time="07:00"))
    owner.add_pet(pet)

    warnings = Scheduler(owner).detect_conflicts()
    assert len(warnings) == 1
    assert "Walk" in warnings[0]
    assert "Vet" in warnings[0]


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
