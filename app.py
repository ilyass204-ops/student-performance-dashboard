
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

st.set_page_config(
    page_title="Student Performance Dashboard",
    page_icon="📊",
    layout="wide"
)

st.title("Student Performance Analytics Dashboard")
st.write(
    "Upload, analyze, filter, and export student performance data."
)

# Required dataset columns
REQUIRED_COLUMNS = [
    "student_id",
    "name",
    "math_score",
    "programming_score",
    "attendance",
    "study_hours"
]

NUMERIC_COLUMNS = [
    "math_score",
    "programming_score",
    "attendance",
    "study_hours"
]

# Upload a CSV file
st.sidebar.header("Dataset")

uploaded_file = st.sidebar.file_uploader(
    "Upload student data (CSV)",
    type=["csv"]
)

# Use uploaded data, or the sample dataset
if uploaded_file is not None:
    try:
        raw_data = pd.read_csv(uploaded_file)
        source_name = uploaded_file.name
    except Exception:
        st.error("Could not read this file as a CSV.")
        st.stop()
else:
    try:
        raw_data = pd.read_csv("students.csv")
        source_name = "students.csv"
    except FileNotFoundError:
        st.error(
            "students.csv was not found. "
            "Upload a valid CSV file to continue."
        )
        st.stop()
    except Exception:
        st.error("Could not read students.csv.")
        st.stop()

st.caption(f"Current dataset: {source_name}")

# Validate required columns
missing_columns = [
    column for column in REQUIRED_COLUMNS
    if column not in raw_data.columns
]

if missing_columns:
    st.error(f"Missing required columns: {missing_columns}")
    st.info(
        "Required columns: "
        + ", ".join(REQUIRED_COLUMNS)
    )
    st.stop()

# Keep only the required columns
data = raw_data[REQUIRED_COLUMNS].copy()

# Clean text fields
for column in ["student_id", "name"]:
    data[column] = data[column].astype("string").str.strip()
    data[column] = data[column].replace("", pd.NA)

# Convert numeric columns and detect invalid values
for column in NUMERIC_COLUMNS:
    data[column] = pd.to_numeric(
        data[column], errors="coerce"
    )

# Validate required values
missing_values = data.isna().sum()
invalid_numeric_rows = data[NUMERIC_COLUMNS].isna().any(axis=1)

# Validate allowed numeric ranges
invalid_score_rows = (
    (data["math_score"] < 0)
    | (data["math_score"] > 100)
    | (data["programming_score"] < 0)
    | (data["programming_score"] > 100)
)

invalid_attendance_rows = (
    (data["attendance"] < 0)
    | (data["attendance"] > 100)
)

invalid_study_rows = data["study_hours"] < 0

# Detect duplicate student IDs
duplicate_id_rows = (
    data["student_id"].notna()
    & data["student_id"].duplicated(keep=False)
)

# Show data quality report
st.header("Data Quality Report")

q1, q2, q3, q4 = st.columns(4)

q1.metric("Rows Uploaded", len(data))
q2.metric("Rows with Missing/Invalid Numbers", int(invalid_numeric_rows.sum()))
q3.metric("Invalid Score Rows", int(invalid_score_rows.sum()))
q4.metric("Duplicate ID Rows", int(duplicate_id_rows.sum()))

with st.expander("View missing values by column"):
    st.dataframe(
        missing_values.rename("Missing Values"),
        use_container_width=True
    )

# Remove rows that cannot be analyzed reliably
invalid_rows = (
    data[["student_id", "name"]].isna().any(axis=1)
    | invalid_numeric_rows
    | invalid_score_rows
    | invalid_attendance_rows
    | invalid_study_rows
    | duplicate_id_rows
)

clean_data = data.loc[~invalid_rows].copy()

st.write(f"Valid rows available for analysis: {len(clean_data)}")

if clean_data.empty:
    st.error(
        "No valid student records were found. "
        "Please upload a corrected CSV file."
    )
    st.stop()

# Calculate average score and performance category
clean_data["average_score"] = clean_data[
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

clean_data["performance"] = clean_data[
    "average_score"
].apply(get_performance)

# Sidebar filters
st.sidebar.header("Filter Students")

search_text = st.sidebar.text_input(
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

minimum_score, maximum_score = st.sidebar.slider(
    "Average score range",
    min_value=0,
    max_value=100,
    value=(0, 100)
)

filtered_data = clean_data.copy()

if search_text:
    search = search_text.strip().lower()

    matches_name = filtered_data["name"].str.lower().str.contains(
        search, na=False
    )

    matches_id = filtered_data["student_id"].str.lower().str.contains(
        search, na=False
    )

    filtered_data = filtered_data[
        matches_name | matches_id
    ]

filtered_data = filtered_data[
    filtered_data["performance"].isin(selected_categories)
]

filtered_data = filtered_data[
    filtered_data["average_score"].between(
        minimum_score, maximum_score
    )
]

# Dashboard metrics
st.header("Performance Overview")

c1, c2, c3, c4 = st.columns(4)

c1.metric("Students Found", len(filtered_data))

if not filtered_data.empty:
    c2.metric(
        "Average Score",
        f"{filtered_data['average_score'].mean():.2f}"
    )
    c3.metric(
        "Average Attendance",
        f"{filtered_data['attendance'].mean():.1f}%"
    )
    c4.metric(
        "Average Study Hours",
        f"{filtered_data['study_hours'].mean():.1f}"
    )
else:
    c2.metric("Average Score", "N/A")
    c3.metric("Average Attendance", "N/A")
    c4.metric("Average Study Hours", "N/A")
    st.warning("No students match the selected filters.")

# Display filtered records
st.header("Student Records")
st.dataframe(filtered_data, use_container_width=True)

# Download filtered results
st.subheader("Export Results")

csv_data = filtered_data.to_csv(index=False).encode("utf-8")

st.download_button(
    label="Download filtered results as CSV",
    data=csv_data,
    file_name="student_performance_results.csv",
    mime="text/csv"
)

# Charts
if not filtered_data.empty:
    st.header("Student Performance Comparison")

    chart_data = filtered_data.sort_values(
        "average_score", ascending=False
    )

    fig1, ax1 = plt.subplots(figsize=(10, 5))
    ax1.bar(chart_data["name"], chart_data["average_score"])
    ax1.set_xlabel("Student")
    ax1.set_ylabel("Average Score")
    ax1.set_ylim(0, 100)
    ax1.set_title("Average Score by Student")
    ax1.tick_params(axis="x", rotation=45)
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

    selected_id = selected_student.split(" - ")[0]

    student = filtered_data[
        filtered_data["student_id"] == selected_id
    ].iloc[0]

    s1, s2, s3, s4 = st.columns(4)

    s1.metric("Average Score", f"{student['average_score']:.1f}")
    s2.metric("Math Score", f"{student['math_score']:.0f}")
    s3.metric(
        "Programming Score",
        f"{student['programming_score']:.0f}"
    )
    s4.metric("Attendance", f"{student['attendance']:.1f}%")

    st.write(f"**Name:** {student['name']}")
    st.write(f"**Performance:** {student['performance']}")
    st.write(f"**Weekly Study Hours:** {student['study_hours']:.1f}")

st.caption(
    "This project uses fictional demonstration data. "
    "Performance categories are illustrative, not official grades."
)
