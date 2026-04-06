import streamlit as st
from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    "A smart pet care planning assistant. Register pets, create tasks, "
    "sort & filter, detect conflicts, and generate an optimised daily schedule."
)

# ── Session State Initialisation ──────────────────────────────
if "owner" not in st.session_state:
    st.session_state.owner = None

# ── Owner Setup ───────────────────────────────────────────────
st.subheader("👤 Owner Setup")

col_name, col_time = st.columns(2)
with col_name:
    owner_name = st.text_input("Owner name", value="Jordan")
with col_time:
    available_time = st.number_input(
        "Available time (minutes)", min_value=10, max_value=480, value=120
    )

if st.button("Save Owner"):
    st.session_state.owner = Owner(
        name=owner_name, available_time_minutes=int(available_time)
    )
    st.success(f"Owner **{owner_name}** saved with {available_time} min budget.")

if st.session_state.owner is None:
    st.info("Set up an owner above to get started.")
    st.stop()

owner: Owner = st.session_state.owner

st.divider()

# ── Add a Pet ─────────────────────────────────────────────────
st.subheader("🐾 Add a Pet")

col_pname, col_species, col_age, col_breed = st.columns(4)
with col_pname:
    pet_name = st.text_input("Pet name", value="Mochi")
with col_species:
    species = st.selectbox("Species", ["dog", "cat", "other"])
with col_age:
    pet_age = st.number_input("Age", min_value=0, max_value=30, value=3)
with col_breed:
    breed = st.text_input("Breed", value="")

if st.button("Add Pet"):
    new_pet = Pet(name=pet_name, species=species, age=int(pet_age), breed=breed)
    owner.add_pet(new_pet)
    st.success(f"Added **{pet_name}** the {species}!")

pets = owner.get_pets()
if pets:
    st.markdown("**Registered pets:**")
    for p in pets:
        st.write(f"  • {p}")
else:
    st.info("No pets yet. Add one above.")

st.divider()

# ── Add Tasks to a Pet ────────────────────────────────────────
st.subheader("📝 Add a Task")

if not pets:
    st.info("Add a pet first before creating tasks.")
else:
    pet_options = [p.name for p in pets]
    selected_pet_name = st.selectbox("Assign to pet", pet_options)

    col_t1, col_t2 = st.columns(2)
    with col_t1:
        task_title = st.text_input("Task title", value="Morning walk")
    with col_t2:
        duration = st.number_input("Duration (min)", min_value=1, max_value=240, value=20)

    col_t3, col_t4, col_t5, col_t6 = st.columns(4)
    with col_t3:
        priority = st.selectbox("Priority", ["high", "medium", "low"], index=0)
    with col_t4:
        category = st.selectbox(
            "Category", ["walk", "feeding", "meds", "grooming", "enrichment", "general"]
        )
    with col_t5:
        scheduled_time = st.text_input("Time (HH:MM)", value="", placeholder="e.g. 08:30")
    with col_t6:
        frequency = st.selectbox("Frequency", ["once", "daily", "weekly"], index=0)

    if st.button("Add Task"):
        target_pet = next(p for p in pets if p.name == selected_pet_name)
        new_task = Task(
            title=task_title,
            duration_minutes=int(duration),
            priority=priority,
            category=category,
            scheduled_time=scheduled_time,
            frequency=frequency,
        )
        target_pet.add_task(new_task)
        st.success(f"Task **{task_title}** added to {selected_pet_name}.")

    # ── Task display per pet with complete button ─────────────
    for p in pets:
        tasks_list = p.get_tasks()
        if tasks_list:
            st.markdown(f"**{p.name}'s tasks:**")
            task_data = [
                {
                    "Title": t.title,
                    "Time": t.scheduled_time or "—",
                    "Duration": f"{t.duration_minutes} min",
                    "Priority": t.priority,
                    "Category": t.category,
                    "Frequency": t.frequency,
                    "Status": "✅" if t.completed else "⏳",
                }
                for t in tasks_list
            ]
            st.table(task_data)

            # Complete task buttons
            pending = p.get_pending_tasks()
            if pending:
                task_to_complete = st.selectbox(
                    f"Mark complete ({p.name})",
                    [t.title for t in pending],
                    key=f"complete_{p.name}",
                )
                if st.button(f"Complete task", key=f"btn_complete_{p.name}"):
                    msg = p.complete_task(task_to_complete)
                    st.success(f"**{task_to_complete}** marked complete!")
                    if msg:
                        st.info(msg)
                    st.rerun()

st.divider()

# ── Sorting & Filtering ──────────────────────────────────────
st.subheader("🔍 Sort & Filter Tasks")

all_tasks = owner.get_all_tasks()
if not all_tasks:
    st.info("No tasks to sort or filter yet.")
else:
    scheduler = Scheduler(owner)

    col_sort, col_filter = st.columns(2)
    with col_sort:
        sort_mode = st.radio("Sort by", ["Priority", "Scheduled time"], horizontal=True)
    with col_filter:
        filter_options = ["All"] + [p.name for p in pets]
        filter_pet = st.selectbox("Filter by pet", filter_options)

    # Apply filter
    if filter_pet == "All":
        filtered = all_tasks
    else:
        filtered = scheduler.filter_by_pet(filter_pet, all_tasks)

    # Apply sort
    if sort_mode == "Priority":
        display_tasks = scheduler.sort_by_priority(filtered)
    else:
        display_tasks = scheduler.sort_by_time(filtered)

    if display_tasks:
        sorted_data = [
            {
                "Title": t.title,
                "Pet": t.pet_name,
                "Time": t.scheduled_time or "—",
                "Duration": f"{t.duration_minutes} min",
                "Priority": t.priority,
                "Category": t.category,
                "Status": "✅" if t.completed else "⏳",
            }
            for t in display_tasks
        ]
        st.table(sorted_data)
    else:
        st.info("No tasks match the current filter.")

    # ── Conflict Detection ────────────────────────────────────
    conflicts = scheduler.detect_conflicts()
    if conflicts:
        st.subheader("⚠️ Schedule Conflicts")
        for warning in conflicts:
            st.warning(warning)
    else:
        if any(t.scheduled_time for t in all_tasks):
            st.success("No scheduling conflicts detected.")

st.divider()

# ── Generate Schedule ─────────────────────────────────────────
st.subheader("📋 Generate Daily Schedule")
st.caption(
    f"Time budget: **{owner.available_time_minutes} min** — "
    "tasks are selected by priority, then shortest duration."
)

if st.button("Generate Schedule"):
    pending_tasks = owner.get_all_pending_tasks()
    if not pending_tasks:
        st.warning("No pending tasks. Add tasks to your pets first.")
    else:
        scheduler = Scheduler(owner)
        plan = scheduler.generate_schedule()
        explanation = scheduler.explain_plan(plan)

        # Show the plan as a clean table
        st.markdown(f"### 📅 {plan.plan_date}")

        if plan.scheduled_tasks:
            plan_data = [
                {
                    "#": idx,
                    "Task": t.title,
                    "Pet": t.pet_name,
                    "Time": t.scheduled_time or "—",
                    "Duration": f"{t.duration_minutes} min",
                    "Priority": t.priority,
                }
                for idx, t in enumerate(plan.scheduled_tasks, 1)
            ]
            st.table(plan_data)

            # Summary metrics
            col_m1, col_m2, col_m3 = st.columns(3)
            col_m1.metric("Tasks scheduled", len(plan.scheduled_tasks))
            col_m2.metric("Time used", f"{plan.total_duration} min")
            col_m3.metric("Time remaining",
                          f"{owner.available_time_minutes - plan.total_duration} min")

            # Conflict warnings inside the plan
            conflicts = scheduler.detect_conflicts(plan.scheduled_tasks)
            if conflicts:
                for w in conflicts:
                    st.warning(w)

            # Explanation expander
            with st.expander("💡 Why this plan?"):
                st.text(explanation)
        else:
            st.warning("No tasks could fit within the available time budget.")
