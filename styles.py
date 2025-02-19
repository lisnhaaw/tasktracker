import streamlit as st

def apply_custom_styles():
    st.markdown("""
        <style>
        .stButton > button {
            width: 100%;
            border-radius: 5px;
            height: 3em;
            background-color: #FF4B4B;
            color: white;
        }
        
        .stTextInput > div > div > input {
            border-radius: 5px;
        }
        
        .habit-card {
            padding: 1rem;
            border-radius: 10px;
            background-color: #F0F2F6;
            margin-bottom: 1rem;
        }
        
        .streak-number {
            font-size: 2rem;
            font-weight: bold;
            color: #FF4B4B;
        }
        
        .habit-title {
            font-size: 1.2rem;
            font-weight: bold;
            margin-bottom: 0.5rem;
        }
        
        .completion-rate {
            font-size: 1.1rem;
            color: #666;
        }
        
        </style>
    """, unsafe_allow_html=True)
