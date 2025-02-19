import streamlit as st
import pandas as pd
from datetime import datetime
from data_handler import TaskTracker
from visualizations import (
    create_streak_chart, create_heatmap, 
    create_completion_chart, render_calendar
)
from styles import apply_custom_styles

def main():
    st.set_page_config(
        page_title="Task Tracker",
        page_icon="📅",
        layout="wide"
    )

    apply_custom_styles()

    st.title("📅 Task Tracker")

    tracker = TaskTracker()

    # Sidebar for adding new tasks
    with st.sidebar:
        st.header("Add New Task")
        new_task = st.text_input("Task Name")
        task_description = st.text_area("Description (optional)")

        # Date selection
        task_date = st.date_input(
            "Task Date",
            datetime.now(),
            min_value=datetime.now()
        )

        # Repetition options
        repeat_type = st.selectbox(
            "Repeat Task",
            options=[
                "none",
                "same_date_monthly",
                "first_monday_monthly"
            ],
            format_func=lambda x: {
                "none": "No Repetition",
                "same_date_monthly": "Monthly (Same Date)",
                "first_monday_monthly": "Monthly (First Monday)"
            }[x]
        )

        if st.button("Add Task"):
            if new_task:
                if tracker.add_task(new_task, task_date.strftime('%Y-%m-%d'), repeat_type, task_description):
                    st.success(f"Added new task: {new_task}")
                else:
                    st.error("This task already exists!")

        st.markdown("---")

        if st.button("Export Data"):
            st.download_button(
                label="Download CSV",
                data=tracker.export_data(),
                file_name="task_data.csv",
                mime="text/csv"
            )

    # Main content area
    if not st.session_state.tasks:
        st.info("Start by adding a task in the sidebar!")
        return

    # Calendar View
    st.header("Calendar View")
    render_calendar(st.session_state.task_data)

    # Daily Check-in Section
    st.header("Today's Tasks")
    cols = st.columns(len(st.session_state.tasks))

    today = datetime.now().strftime('%Y-%m-%d')
    for idx, (task_name, task_info) in enumerate(st.session_state.tasks.items()):
        with cols[idx]:
            st.markdown(f"<div class='habit-card'>", unsafe_allow_html=True)
            st.markdown(f"<div class='habit-title'>{task_name}</div>", unsafe_allow_html=True)

            # Only show completion checkbox for today's tasks
            today_task = st.session_state.task_data[
                (st.session_state.task_data.task == task_name) &
                (st.session_state.task_data.date == today)
            ]

            if not today_task.empty:
                completed = st.checkbox(
                    "Completed Today",
                    key=f"check_{task_name}",
                    value=bool(today_task.iloc[0]['completed'])
                )
                if completed:
                    tracker.log_task(task_name, today, True)
                else:
                    tracker.log_task(task_name, today, False)

            streak = tracker.get_streak(task_name)
            st.markdown(f"<div class='streak-number'>{streak} 🔥</div>", unsafe_allow_html=True)

            completion_rate = tracker.get_completion_rate(task_name)
            st.markdown(
                f"<div class='completion-rate'>{completion_rate:.1f}% completed</div>",
                unsafe_allow_html=True
            )

            # Show repetition info
            repeat_type = task_info.get('repeat_type', 'none')
            if repeat_type != 'none':
                repeat_text = {
                    'same_date_monthly': 'Repeats monthly on same date',
                    'first_monday_monthly': 'Repeats on first Monday of month'
                }[repeat_type]
                st.markdown(f"<div style='color: #666;'>{repeat_text}</div>", unsafe_allow_html=True)

            if st.button("Remove", key=f"remove_{task_name}"):
                tracker.remove_task(task_name)
                st.experimental_rerun()

            st.markdown("</div>", unsafe_allow_html=True)

    # Additional Visualizations
    with st.expander("Show Detailed Analytics", expanded=False):
        st.header("Detailed Analytics")

        # Individual task visualizations
        for task_name in st.session_state.tasks:
            st.subheader(task_name)

            col1, col2 = st.columns(2)

            with col1:
                streak_chart = create_streak_chart(st.session_state.task_data, task_name)
                if streak_chart:
                    st.plotly_chart(streak_chart, use_container_width=True)

            with col2:
                heatmap = create_heatmap(st.session_state.task_data, task_name)
                if heatmap:
                    st.plotly_chart(heatmap, use_container_width=True)

        # Overall completion rates
        completion_chart = create_completion_chart(st.session_state.task_data)
        if completion_chart:
            st.plotly_chart(completion_chart, use_container_width=True)

if __name__ == "__main__":
    main()