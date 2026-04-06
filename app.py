import streamlit as st
from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    "A pet care planning assistant. Add your info, register pets, "
    "create tasks, and generate a daily schedule."
)

# ── Session State Initialisation ──────────────────────────────
# Streamlit reruns the script on every interaction, so we persist
# the Owner object in session_state so data survives across clicks.
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

# Show current pets
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

    col_t1, col_t2, col_t3, col_t4 = st.columns(4)
    with col_t1:
        task_title = st.text_input("Task title", value="Morning walk")
    with col_t2:
        duration = st.number_input("Duration (min)", min_value=1, max_value=240, value=20)
    with col_t3:
        priority = st.selectbox("Priority", ["high", "medium", "low"], index=0)
    with col_t4:
        category = st.selectbox(
            "Category", ["walk", "feeding", "meds", "grooming", "enrichment", "general"]
        )

    if st.button("Add Task"):
        target_pet = next(p for p in pets if p.name == selected_pet_name)
        new_task = Task(
            title=task_title,
            duration_minutes=int(duration),
            priority=priority,
            category=category,
        )
        target_pet.add_task(new_task)
        st.success(f"Task **{task_title}** added to {selected_pet_name}.")

    # Show all tasks per pet
    for p in pets:
        tasks_list = p.get_tasks()
        if tasks_list:
            st.markdown(f"**{p.name}'s tasks:**")
            task_data = [
                {
                    "Title": t.title,
                    "Duration": f"{t.duration_minutes} min",
                    "Priority": t.priority,
                    "Category": t.category,
                    "Status": "✅" if t.completed else "⏳",
                }
                for t in tasks_list
            ]
            st.table(task_data)

st.divider()

# ── Generate Schedule ─────────────────────────────────────────
st.subheader("📋 Generate Daily Schedule")
st.caption(
    f"Time budget: **{owner.available_time_minutes} min** — "
    "tasks are selected by priority, then shortest duration."
)

if st.button("Generate Schedule"):
    all_tasks = owner.get_all_pending_tasks()
    if not all_tasks:
        st.warning("No pending tasks. Add tasks to your pets first.")
    else:
        scheduler = Scheduler(owner)
        plan = scheduler.generate_schedule()
        explanation = scheduler.explain_plan(plan)

        st.markdown("### Today's Plan")
        st.text(plan.get_explanation())
        with st.expander("Why this plan?"):
            st.text(explanation)
