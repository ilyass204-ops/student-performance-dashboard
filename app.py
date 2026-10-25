
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

st.set_page_config(
    page_title="Student Performance Dashboard",
    page_icon="📊",
    layout="wide"
)

st.title("Student Performance Analytics Dashboard")
st.write("Explore student grades, attendance, and study habits.")

# Load data
data = pd.read_csv("students.csv")

# Check required columns
required_columns = [
    "student_id",
    "name",
    "math_score",
    "programming_score",
    "attendance",
    "study_hours"
]

missing_columns = [
    column for column in required_columns
    if column not in data.columns
]

if missing_columns:
    st.error(f"Missing columns: {missing_columns}")
    st.stop()

# Calculate average score and performance category
data["average_score"] = data[
    ["math_score", "programming_score"]
].mean(axis=1)

def get_performance(score):
    if score >= 85:
        return "Excellent"
    elif score >= 70:
        return "Good"
    elif score >= 60:
        return "Pass"
    else:
        return "Needs Improvement"

data["performance"] = data["average_score"].apply(
    get_performance
)

# Sidebar filters
st.sidebar.header("Filter Students")

search_name = st.sidebar.text_input(
    "Search by name or student ID"
)

categories = [
    "Excellent",
    "Good",
    "Pass",
    "Needs Improvement"
]

selected_categories = st.sidebar.multiselect(
    "Performance category",
    categories,
    default=categories
)

minimum_score = st.sidebar.slider(
    "Minimum average score",
    min_value=0,
    max_value=100,
    value=0
)

maximum_score = st.sidebar.slider(
    "Maximum average score",
    min_value=0,
    max_value=100,
    value=100
)

# Filter the dataset
filtered_data = data.copy()

if search_name:
    search_text = search_name.lower()

    filtered_data = filtered_data[
        filtered_data["name"].str.lower().str.contains(
            search_text, na=False
        )
        |
        filtered_data["student_id"].str.lower().str.contains(
            search_text, na=False
        )
    ]

filtered_data = filtered_data[
    filtered_data["performance"].isin(selected_categories)
]

filtered_data = filtered_data[
    (filtered_data["average_score"] >= minimum_score)
    &
    (filtered_data["average_score"] <= maximum_score)
]

# Summary metrics
st.header("Overview")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Students Found", len(filtered_data))

if not filtered_data.empty:
    col2.metric(
        "Average Score",
        f"{filtered_data['average_score'].mean():.2f}"
    )
    col3.metric(
        "Average Attendance",
        f"{filtered_data['attendance'].mean():.1f}%"
    )
    col4.metric(
        "Average Study Hours",
        f"{filtered_data['study_hours'].mean():.1f}"
    )
else:
    col2.metric("Average Score", "N/A")
    col3.metric("Average Attendance", "N/A")
    col4.metric("Average Study Hours", "N/A")
    st.warning("No students match these filters.")

# Filtered table
st.header("Student Records")
st.dataframe(filtered_data, use_container_width=True)

# Charts based on filtered data
if not filtered_data.empty:
    st.header("Student Performance Comparison")

    chart_data = filtered_data.sort_values(
        "average_score", ascending=False
    )

    fig1, ax1 = plt.subplots(figsize=(10, 5))
    ax1.bar(
        chart_data["name"],
        chart_data["average_score"]
    )
    ax1.set_xlabel("Student")
    ax1.set_ylabel("Average Score")
    ax1.set_ylim(0, 100)
    ax1.tick_params(axis="x", rotation=45)
    ax1.set_title("Average Score by Student")
    plt.tight_layout()
    st.pyplot(fig1)
    plt.close(fig1)

    st.header("Study Hours vs Academic Performance")

    fig2, ax2 = plt.subplots(figsize=(8, 5))
    ax2.scatter(
        filtered_data["study_hours"],
        filtered_data["average_score"]
    )
    ax2.set_xlabel("Weekly Study Hours")
    ax2.set_ylabel("Average Score")
    ax2.set_ylim(0, 100)
    ax2.set_title("Study Hours vs Average Score")
    plt.tight_layout()
    st.pyplot(fig2)
    plt.close(fig2)

    # Select an individual student
    st.header("Individual Student Analysis")

    student_options = (
        filtered_data["student_id"]
        + " - "
        + filtered_data["name"]
    ).tolist()

    selected_student = st.selectbox(
        "Select a student",
        student_options
    )

    student_id = selected_student.split(" - ")[0]

    student = filtered_data[
        filtered_data["student_id"] == student_id
    ].iloc[0]

    a, b, c, d = st.columns(4)

    a.metric("Average Score", f"{student['average_score']:.1f}")
    b.metric("Math Score", int(student["math_score"]))
    c.metric(
        "Programming Score",
        int(student["programming_score"])
    )
    d.metric("Attendance", f"{student['attendance']}%")

    st.write(
        f"**Performance category:** {student['performance']}"
    )
    st.write(
        f"**Weekly study hours:** {student['study_hours']}"
    )

# Footer
st.caption(
    "Demonstration project using fictional student data. "
    "Performance categories are illustrative, not official grades."
)
