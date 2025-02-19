import pandas as pd
from datetime import datetime, timedelta
import json
import streamlit as st

class TaskTracker:
    def __init__(self):
        if 'tasks' not in st.session_state:
            st.session_state.tasks = {}
        if 'task_data' not in st.session_state:
            st.session_state.task_data = pd.DataFrame(
                columns=['task', 'date', 'completed', 'repeat_type']
            )

    def add_task(self, task_name, date, repeat_type="none", description=""):
        if task_name not in st.session_state.tasks:
            st.session_state.tasks[task_name] = {
                'description': description,
                'created_at': datetime.now().strftime('%Y-%m-%d'),
                'repeat_type': repeat_type
            }
            # Add initial task entry
            new_entry = pd.DataFrame({
                'task': [task_name],
                'date': [date],
                'completed': [False],
                'repeat_type': [repeat_type]
            })
            st.session_state.task_data = pd.concat([st.session_state.task_data, new_entry])

            # Create future occurrences if it's a repeating task
            if repeat_type != "none":
                self._create_next_occurrence(task_name, date)
            return True
        return False

    def remove_task(self, task_name):
        if task_name in st.session_state.tasks:
            del st.session_state.tasks[task_name]
            st.session_state.task_data = st.session_state.task_data[
                st.session_state.task_data.task != task_name
            ]

    def log_task(self, task_name, date, completed=True):
        new_entry = pd.DataFrame({
            'task': [task_name],
            'date': [date],
            'completed': [completed],
            'repeat_type': [st.session_state.tasks[task_name]['repeat_type']]
        })

        # Remove any existing entry for the same task and date
        st.session_state.task_data = st.session_state.task_data[
            ~((st.session_state.task_data.task == task_name) & 
              (st.session_state.task_data.date == date))
        ]
        st.session_state.task_data = pd.concat([st.session_state.task_data, new_entry])

        # Handle task repetition
        if completed and st.session_state.tasks[task_name]['repeat_type'] != "none":
            self._create_next_occurrence(task_name, date)

    def _create_next_occurrence(self, task_name, current_date):
        current_date = datetime.strptime(current_date, '%Y-%m-%d')
        repeat_type = st.session_state.tasks[task_name]['repeat_type']

        if repeat_type == "same_date_monthly":
            # Next month, same date
            next_date = (current_date.replace(day=1) + timedelta(days=32)).replace(day=current_date.day)
        elif repeat_type == "first_monday_monthly":
            # First Monday of next month
            next_month = (current_date.replace(day=1) + timedelta(days=32)).replace(day=1)
            days_ahead = 7 - next_month.weekday()  # weekday() is 0 for Monday
            if days_ahead <= 0:  # If we're already past Monday
                days_ahead += 7
            next_date = next_month + timedelta(days=days_ahead - 1)
        else:
            return

        # Add the next occurrence to task data
        new_entry = pd.DataFrame({
            'task': [task_name],
            'date': [next_date.strftime('%Y-%m-%d')],
            'completed': [False],
            'repeat_type': [repeat_type]
        })
        st.session_state.task_data = pd.concat([st.session_state.task_data, new_entry])

    def get_streak(self, task_name):
        if task_name not in st.session_state.tasks:
            return 0

        task_data = st.session_state.task_data[
            (st.session_state.task_data.task == task_name) &
            (st.session_state.task_data.completed == True)
        ]
        if task_data.empty:
            return 0

        task_data = task_data.sort_values('date', ascending=False)
        current_date = datetime.now().date()
        streak = 0

        for _, row in task_data.iterrows():
            date = datetime.strptime(row['date'], '%Y-%m-%d').date()
            if date == current_date - timedelta(days=streak):
                streak += 1
            else:
                break

        return streak

    def get_completion_rate(self, task_name, days=30):
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)

        task_data = st.session_state.task_data[
            (st.session_state.task_data.task == task_name) &
            (st.session_state.task_data.date >= start_date.strftime('%Y-%m-%d'))
        ]

        total_days = (end_date - start_date).days + 1
        completed_days = len(task_data[task_data.completed == True])

        return (completed_days / total_days) * 100 if total_days > 0 else 0

    def export_data(self):
        return st.session_state.task_data.to_csv(index=False)