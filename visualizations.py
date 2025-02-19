import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import datetime, timedelta
import streamlit as st
from streamlit_calendar import calendar
import json

def create_streak_chart(task_data, task_name):
    fig = go.Figure()

    task_entries = task_data[task_data.task == task_name].sort_values('date')
    if not task_entries.empty:
        fig.add_trace(go.Scatter(
            x=task_entries['date'],
            y=task_entries['completed'].astype(int),
            mode='lines+markers',
            name='Completion',
            line=dict(color='#FF4B4B'),
            marker=dict(size=8)
        ))

    fig.update_layout(
        title=f'{task_name} Completion Streak',
        xaxis_title='Date',
        yaxis_title='Completed',
        yaxis=dict(tickmode='array', tickvals=[0, 1], ticktext=['No', 'Yes']),
        showlegend=False,
        height=300,
        margin=dict(l=20, r=20, t=40, b=20)
    )

    return fig

def create_calendar_events(task_data):
    events = []
    for task_name in task_data['task'].unique():
        task_entries = task_data[task_data.task == task_name]
        for _, entry in task_entries.iterrows():
            color = '#4CAF50' if entry['completed'] else '#FF4B4B'
            events.append({
                'title': task_name,
                'start': entry['date'],
                'end': entry['date'],
                'backgroundColor': color,
                'textColor': '#FFFFFF'
            })
    return events

def render_calendar(task_data):
    events = create_calendar_events(task_data)
    calendar_options = {
        'headerToolbar': {
            'left': 'prev,next today',
            'center': 'title',
            'right': 'dayGridMonth,timeGridWeek'
        },
        'initialView': 'dayGridMonth',
        'selectable': True,
        'events': events,
        'height': 600
    }

    calendar(events=events, options=calendar_options)

def create_heatmap(task_data, task_name):
    dates = pd.date_range(
        start=(datetime.now() - timedelta(days=180)).strftime('%Y-%m-%d'),
        end=datetime.now().strftime('%Y-%m-%d')
    )

    task_entries = task_data[task_data.task == task_name]
    completion_dict = dict(zip(task_entries['date'], task_entries['completed']))

    values = [int(completion_dict.get(date.strftime('%Y-%m-%d'), 0)) for date in dates]

    fig = go.Figure(data=go.Heatmap(
        z=[values],
        x=dates,
        y=['Completion'],
        colorscale=[[0, '#F0F2F6'], [1, '#FF4B4B']],
        showscale=False
    ))

    fig.update_layout(
        title=f'{task_name} Activity Heatmap',
        height=200,
        margin=dict(l=20, r=20, t=40, b=20)
    )

    return fig

def create_completion_chart(task_data):
    if task_data.empty:
        return None

    tasks = task_data['task'].unique()
    completion_rates = []

    for task in tasks:
        completed = len(task_data[(task_data.task == task) & (task_data.completed)])
        total = len(task_data[task_data.task == task])
        rate = (completed / total * 100) if total > 0 else 0
        completion_rates.append({'task': task, 'rate': rate})

    df = pd.DataFrame(completion_rates)

    if not df.empty:
        fig = px.bar(
            df,
            x='task',
            y='rate',
            title='Task Completion Rates',
            labels={'task': 'Task', 'rate': 'Completion Rate (%)'}
        )

        fig.update_layout(
            height=300,
            margin=dict(l=20, r=20, t=40, b=20)
        )

        return fig
    return None