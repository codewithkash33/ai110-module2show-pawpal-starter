"""PawPal+ Demo Script — verifies the logic layer in the terminal."""

from pawpal_system import Owner, Pet, Task, Scheduler


def section(title: str) -> None:
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print("=" * 60)


def main() -> None:
    # ── Owner ──────────────────────────────────────────────────
    owner = Owner(name="Jordan", available_time_minutes=90)

    # ── Pets ───────────────────────────────────────────────────
    mochi = Pet(name="Mochi", species="dog", age=3, breed="Shiba Inu")
    whiskers = Pet(name="Whiskers", species="cat", age=5, breed="Tabby")

    owner.add_pet(mochi)
    owner.add_pet(whiskers)

    # ── Tasks (added deliberately out of time-order) ──────────
    mochi.add_task(Task(title="Play fetch", duration_minutes=20, priority="medium",
                        category="enrichment", scheduled_time="10:00"))
    mochi.add_task(Task(title="Morning walk", duration_minutes=30, priority="high",
                        category="walk", scheduled_time="07:00", frequency="daily"))
    mochi.add_task(Task(title="Feed breakfast", duration_minutes=10, priority="high",
                        category="feeding", scheduled_time="07:30"))

    whiskers.add_task(Task(title="Feed wet food", duration_minutes=5, priority="high",
                           category="feeding", scheduled_time="07:30"))
    whiskers.add_task(Task(title="Clean litter box", duration_minutes=10, priority="high",
                           category="grooming", scheduled_time="09:00", frequency="daily"))
    whiskers.add_task(Task(title="Brush fur", duration_minutes=15, priority="low",
                           category="grooming", scheduled_time="11:00"))

    # ── Intentional conflict: two tasks at the same time ──────
    mochi.add_task(Task(title="Vet visit", duration_minutes=60, priority="high",
                        category="meds", scheduled_time="07:00"))

    # ── Owner & Pet summary ───────────────────────────────────
    section(f"Owner: {owner.name}  |  Budget: {owner.available_time_minutes} min")
    for pet in owner.get_pets():
        print(f"\n  🐾 {pet}")
        for task in pet.get_tasks():
            print(f"     • {task}")

    # ── Sorting by time ───────────────────────────────────────
    scheduler = Scheduler(owner)

    section("Tasks sorted by scheduled time")
    for t in scheduler.sort_by_time():
        print(f"  {t}")

    # ── Sorting by priority ───────────────────────────────────
    section("Tasks sorted by priority")
    for t in scheduler.sort_by_priority():
        print(f"  {t}")

    # ── Filtering by pet ──────────────────────────────────────
    section("Filter: Whiskers' tasks only")
    for t in scheduler.filter_by_pet("Whiskers"):
        print(f"  {t}")

    # ── Filtering by category ─────────────────────────────────
    section("Filter: feeding tasks only")
    for t in scheduler.filter_by_category("feeding"):
        print(f"  {t}")

    # ── Conflict detection ────────────────────────────────────
    section("Conflict detection")
    conflicts = scheduler.detect_conflicts()
    if conflicts:
        for w in conflicts:
            print(f"  {w}")
    else:
        print("  No conflicts found.")

    # ── Generate schedule ─────────────────────────────────────
    section("📋 Today's Schedule")
    plan = scheduler.generate_schedule()
    print(plan.get_explanation())
    print()
    print(scheduler.explain_plan(plan))

    # ── Recurring task demo ───────────────────────────────────
    section("Recurring task: complete 'Morning walk'")
    msg = mochi.complete_task("Morning walk")
    if msg:
        print(f"  {msg}")
    print(f"  Mochi now has {mochi.task_count} task(s):")
    for t in mochi.get_tasks():
        print(f"     • {t}")

    # ── Filter by status after completing ─────────────────────
    section("Filter: pending tasks only (after completing walk)")
    for t in scheduler.filter_by_status(completed=False):
        print(f"  {t}")

    print()


if __name__ == "__main__":
    main()
