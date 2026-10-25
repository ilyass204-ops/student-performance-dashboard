
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Student Performance Dashboard",
    page_icon="📊",
    layout="wide"
)

st.title("Student Performance Analytics Dashboard")
st.write("Explore student grades, attendance, and study habits.")

data = pd.read_csv("students.csv")

st.subheader("Student Data")
st.dataframe(data, use_container_width=True)

st.subheader("Basic Statistics")

col1, col2, col3 = st.columns(3)

col1.metric("Total Students", len(data))
col2.metric(
    "Average Math Score",
    round(data["math_score"].mean(), 2)
)
col3.metric(
    "Average Programming Score",
    round(data["programming_score"].mean(), 2)
)
