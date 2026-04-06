"""PawPal+ Demo Script — verifies the logic layer in the terminal."""

from pawpal_system import Owner, Pet, Task, Scheduler


def main() -> None:
    # ── Owner ──────────────────────────────────────────────────
    owner = Owner(name="Jordan", available_time_minutes=90)

    # ── Pets ───────────────────────────────────────────────────
    mochi = Pet(name="Mochi", species="dog", age=3, breed="Shiba Inu")
    whiskers = Pet(name="Whiskers", species="cat", age=5, breed="Tabby")

    owner.add_pet(mochi)
    owner.add_pet(whiskers)

    # ── Tasks for Mochi ────────────────────────────────────────
    mochi.add_task(Task(title="Morning walk", duration_minutes=30, priority="high", category="walk"))
    mochi.add_task(Task(title="Feed breakfast", duration_minutes=10, priority="high", category="feeding"))
    mochi.add_task(Task(title="Play fetch", duration_minutes=20, priority="medium", category="enrichment"))

    # ── Tasks for Whiskers ─────────────────────────────────────
    whiskers.add_task(Task(title="Clean litter box", duration_minutes=10, priority="high", category="grooming"))
    whiskers.add_task(Task(title="Feed wet food", duration_minutes=5, priority="high", category="feeding"))
    whiskers.add_task(Task(title="Brush fur", duration_minutes=15, priority="low", category="grooming"))

    # ── Print owner & pet summary ──────────────────────────────
    print("=" * 55)
    print(f"  Owner: {owner.name}  |  Time budget: {owner.available_time_minutes} min")
    print("=" * 55)
    for pet in owner.get_pets():
        print(f"\n  🐾 {pet}")
        for task in pet.get_tasks():
            print(f"     • {task}")

    # ── Generate schedule ──────────────────────────────────────
    scheduler = Scheduler(owner)
    plan = scheduler.generate_schedule()

    print("\n" + "=" * 55)
    print("  📋 Today's Schedule")
    print("=" * 55)
    print(plan.get_explanation())

    print()
    print(scheduler.explain_plan(plan))
    print()


if __name__ == "__main__":
    main()
