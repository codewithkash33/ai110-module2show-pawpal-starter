# PawPal+ Project Reflection

## 1. System Design

### Core Actions

A user of PawPal+ should be able to:

1. **Add a pet and owner profile** — enter pet details (name, species, age, breed) and owner info (name, available time, preferences).
2. **Add / edit care tasks** — create tasks like walks, feeding, meds, grooming, and enrichment with a duration and priority level.
3. **Generate a daily schedule** — produce an optimised daily plan that fits tasks into the owner's available time, ordered by priority, along with an explanation of why each task was chosen.

### Building Blocks

| Object | Attributes | Methods |
|---|---|---|
| **Pet** (dataclass) | name, species, age, breed | — (data holder) |
| **Task** (dataclass) | title, duration_minutes, priority, category, pet_name | — (data holder) |
| **Owner** | name, available_time_minutes, preferences, _pets | add_pet(), remove_pet(), get_pets() |
| **DailyPlan** (dataclass) | plan_date, scheduled_tasks, total_duration | add_task(), get_explanation() |
| **Scheduler** | owner, tasks, time_budget | generate_schedule(), explain_plan() |

### Relationships

- Owner **1 → *** Pet (an owner owns one or more pets)
- Owner **1 → *** Task (an owner manages tasks)
- Task *** → 1** Pet (each task is for a specific pet)
- Scheduler → Owner (uses owner info), Scheduler → DailyPlan (produces a plan)
- DailyPlan *** → *** Task (a plan contains multiple tasks)

**a. Initial design**

The UML design contains five classes: **Pet**, **Task**, **Owner**, **DailyPlan**, and **Scheduler**.

- **Pet** and **Task** are Python `dataclass` objects — they hold data with minimal behaviour, keeping the code clean and declarative.
- **Owner** manages the list of pets and stores the time budget and preferences that constrain scheduling.
- **DailyPlan** is the output object — it accumulates scheduled tasks and can produce a human-readable explanation.
- **Scheduler** is the core engine. It takes an Owner and a list of Tasks, sorts them by priority (high → medium → low) and duration, then greedily fills the time budget to produce a DailyPlan. It also explains which tasks were skipped and why.

**b. Design changes**

After reviewing the initial skeleton with Copilot, one change was made:

- **Added a `DailyPlan` class** — the original brainstorm only had Owner, Pet, Task, and Scheduler. Copilot pointed out that the schedule output deserved its own class so it could carry metadata (date, total duration) and provide a `get_explanation()` method, rather than returning a raw list of tasks from the Scheduler. This improved separation of concerns and made the UI layer simpler to implement.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

The scheduler considers three constraints when building a daily plan:

1. **Time budget** — the owner's total available minutes per day. Tasks are only added if they fit within the remaining budget.
2. **Priority** — tasks are sorted high → medium → low so the most important care activities are scheduled first.
3. **Duration** — among tasks of equal priority, shorter tasks are scheduled first to maximise the number of tasks that fit.

Time and priority were chosen as the primary constraints because a busy pet owner's biggest challenge is fitting essential tasks (meds, feeding) into a limited window before lower-priority activities (enrichment, grooming).

**b. Tradeoffs**

The conflict detection algorithm checks whether any task's time window overlaps with another's using start-time + duration arithmetic. However, it only flags overlaps among tasks that have a `scheduled_time` — **tasks without a time are silently ignored** and placed at the end of the sorted list.

This tradeoff is reasonable because many pet-care tasks (e.g. "brush fur") don't need a specific time slot. Forcing the user to assign times to every task would add friction without improving the schedule. By checking only timed tasks, the system stays lightweight while still catching real conflicts like a vet visit overlapping with a morning walk.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

The test suite (41 tests) covers eight categories of behaviour:

1. **Task basics** — marking complete/incomplete, string representation
2. **Pet management** — add/remove tasks, auto-tagging pet_name, empty-pet edge case, pending-only filtering
3. **Owner aggregation** — multi-pet task collection, no-pets edge case, removing pets
4. **Sorting** — chronological order (HH:MM), unscheduled-last, same-hour ties, priority ordering with duration tiebreak
5. **Filtering** — by pet name (including no-match), by completion status, by category
6. **Recurring tasks** — daily and weekly auto-creation, attribute preservation, one-time no-recurrence, double-complete idempotency
7. **Conflict detection** — exact overlap, partial overlap, no overlap, cross-pet conflicts, unscheduled tasks ignored
8. **Schedule generation edge cases** — time budget enforcement, priority ordering, empty task list, no pets, zero budget, single task exceeding budget, all tasks completed, DailyPlan explanation output

These tests are important because they verify both the "happy path" (normal usage) and critical edge cases (empty data, zero budget, already-completed tasks) that could silently break the scheduler.

**b. Confidence**

Confidence level: ⭐⭐⭐⭐ (4/5)

The scheduler works correctly for all tested scenarios. Edge cases I would test next with more time:
- Tasks with invalid scheduled_time formats (e.g. "25:99", "abc")
- Very large task lists (performance / stress testing)
- Concurrent recurring tasks where multiple daily tasks complete simultaneously
- Boundary condition: a task whose duration exactly equals the remaining budget

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
