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
