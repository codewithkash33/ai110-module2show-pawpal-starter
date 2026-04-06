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

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

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

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
