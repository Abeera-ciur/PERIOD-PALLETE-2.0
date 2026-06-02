"""Period Pallete  · main.py — entry point"""
import streamlit as st

st.set_page_config(
    page_title="Period Pallete – understand. care. thrive.",
    page_icon="🌸",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Route based on auth state
if st.session_state.get("user"):
    st.switch_page("pages/Dashboard.py")
else:
    st.switch_page("pages/Auth.py")
