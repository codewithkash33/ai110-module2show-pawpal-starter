# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## Smarter Scheduling

The Scheduler class includes several algorithmic features beyond simple list management:

- **Sort by time** — `sort_by_time()` orders tasks by their `HH:MM` scheduled time using a lambda key, placing unscheduled tasks at the end.
- **Sort by priority** — `sort_by_priority()` ranks tasks high → medium → low, breaking ties by shortest duration.
- **Filter by pet / status / category** — `filter_by_pet()`, `filter_by_status()`, and `filter_by_category()` let you slice the task list by any dimension.
- **Recurring tasks** — Tasks with `frequency="daily"` or `"weekly"` automatically create a new pending occurrence when marked complete, using `timedelta` for date arithmetic.
- **Conflict detection** — `detect_conflicts()` compares every pair of timed tasks and flags overlapping windows (start-time + duration overlap) with a warning message instead of crashing.
