from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
from httpx import HTTPError
from ai_insights import APIError, generate_ai_insights
from data_utils import add_performance
from analysis_utils import (
    summarize_class,
    identify_students_needing_support,
)

st.set_page_config(
    page_title="Student Performance Dashboard",
    page_icon="📊",
    layout="wide"
)

# Professional, accessible light theme
st.markdown("""
<style>
:root {
    color-scheme: light;
    --app-bg: #F6F5F0;
    --surface: #FFFDF9;
    --surface-muted: #F0EFE8;
    --text-primary: #293A38;
    --text-secondary: #5D6D68;
    --border: #E1E0D8;
    --brand: #5D786D;
    --brand-hover: #4E685E;
    --teal: #78968B;
    --success-bg: #EAF1E9;
    --success-text: #3F604B;
    --warning-bg: #F5EFE1;
    --warning-text: #765E38;
    --error-bg: #F5E9E6;
    --error-text: #80534B;
    --info-bg: #EAF0EF;
    --info-text: #415D59;
}

html, body, [data-testid="stAppViewContainer"], .stApp {
    background:
        radial-gradient(ellipse at 88% 0%, rgba(190, 177, 145, .11), transparent 35%),
        var(--app-bg) !important;
    color: var(--text-primary) !important;
    font-family: "Segoe UI", Inter, Arial, sans-serif;
}

[data-testid="stHeader"] {
    background: rgba(246, 245, 240, .92) !important;
    backdrop-filter: blur(10px);
}
[data-testid="stToolbar"] { right: 1rem; }
.block-container {
    max-width: 1480px;
    padding-top: 2.2rem;
    padding-bottom: 3.5rem;
    animation: dashboard-fade-in .7s ease-out both;
}

@keyframes dashboard-fade-in {
    from { opacity: 0; transform: translateY(6px); }
    to { opacity: 1; transform: translateY(0); }
}

@keyframes chart-draw-in {
    from { clip-path: inset(100% 0 0 0); }
    to { clip-path: inset(0 0 0 0); }
}

/* Typography: one predictable high-contrast text color */
h1, h2, h3, h4, h5, h6,
[data-testid="stMarkdownContainer"],
[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] li,
[data-testid="stCaptionContainer"], label,
[data-testid="stWidgetLabel"] p {
    color: var(--text-primary) !important;
}
h1 { font-size: clamp(1.9rem, 3vw, 2.55rem) !important; font-weight: 730 !important; letter-spacing: -0.04em; }
h1::after {
    content: "";
    display: block;
    width: 3.4rem;
    height: 2px;
    margin-top: .65rem;
    border-radius: 4px;
    background: var(--teal);
}
h2 { font-size: 1.4rem !important; font-weight: 700 !important; margin-top: 1.55rem !important; padding-bottom: .6rem; border-bottom: 1px solid var(--border); }
h3 { font-size: 1.12rem !important; font-weight: 700 !important; }
p, li { line-height: 1.7; }
[data-testid="stCaptionContainer"] { color: var(--text-secondary) !important; }
hr { border-color: var(--border) !important; }

/* Sidebar and controls */
section[data-testid="stSidebar"] {
    background: linear-gradient(165deg, #FBFAF6 0%, #F0EFE8 100%) !important;
    border-right: 1px solid var(--border);
    box-shadow: 8px 0 24px rgba(52, 63, 55, .035);
}
section[data-testid="stSidebar"] * { color: var(--text-primary); }
section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p { color: var(--text-primary) !important; }
section[data-testid="stSidebar"] [data-testid="stWidgetLabel"] p { color: var(--text-primary) !important; }

/* Inputs and selection controls */
.stTextInput input, .stNumberInput input, .stDateInput input,
[data-baseweb="input"] input, [data-baseweb="textarea"] textarea {
    color: var(--text-primary) !important;
    background: var(--surface) !important;
    -webkit-text-fill-color: var(--text-primary) !important;
    border-color: #CBCFC5 !important;
    border-radius: 10px !important;
}
input::placeholder, textarea::placeholder { color: #75817B !important; opacity: 1 !important; }
[data-baseweb="select"] > div {
    color: var(--text-primary) !important;
    background: var(--surface) !important;
    border-color: #CBCFC5 !important;
    border-radius: 10px !important;
}
[data-baseweb="select"] *, [role="listbox"], [role="option"] {
    color: var(--text-primary) !important;
}
[role="listbox"], [role="option"] { background: var(--surface) !important; }
[role="option"]:hover { background: #EEF1EA !important; }
[data-baseweb="tag"] {
    color: #415D53 !important;
    background: #E8EEE8 !important;
    border: 1px solid #D2DED3 !important;
    border-radius: 8px !important;
}
[data-baseweb="tag"] * { color: #415D53 !important; }
input[type="checkbox"] { accent-color: var(--brand); }

/* Buttons: readable at rest, hover, focus and disabled states */
.stButton > button, .stDownloadButton > button,
[data-testid="stFormSubmitButton"] button,
[data-testid="stFileUploader"] button {
    color: #FFFFFF !important;
    background: var(--brand) !important;
    border: 1px solid var(--brand) !important;
    border-radius: 11px !important;
    min-height: 2.55rem;
    padding: .55rem 1rem;
    font-weight: 650 !important;
    box-shadow: 0 3px 9px rgba(57, 78, 65, .12);
    transition: transform .24s ease, box-shadow .24s ease, background-color .24s ease;
}
.stButton > button *, .stDownloadButton > button *,
[data-testid="stFormSubmitButton"] button *,
[data-testid="stFileUploader"] button * { color: #FFFFFF !important; }
.stButton > button:hover, .stDownloadButton > button:hover,
[data-testid="stFormSubmitButton"] button:hover,
[data-testid="stFileUploader"] button:hover {
    color: #FFFFFF !important;
    background: var(--brand-hover) !important;
    border-color: var(--brand-hover) !important;
    box-shadow: 0 5px 13px rgba(57, 78, 65, .17);
    transform: translateY(-1px);
}
.stButton > button:focus-visible, .stDownloadButton > button:focus-visible,
[data-testid="stFormSubmitButton"] button:focus-visible,
[data-testid="stFileUploader"] button:focus-visible {
    outline: 3px solid #A9BCAF !important; outline-offset: 3px;
}
.stButton > button:active, .stDownloadButton > button:active,
[data-testid="stFormSubmitButton"] button:active { transform: translateY(0) scale(.985); }
.stButton > button:disabled, .stDownloadButton > button:disabled { background: #E2E8F0 !important; color: #64748B !important; border-color: #CBD5E1 !important; }

/* KPI cards */
div[data-testid="stMetric"] {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-left: 3px solid #8FA69A !important;
    border-radius: 15px !important;
    padding: 1.1rem 1.2rem !important;
    box-shadow: 0 4px 15px rgba(53, 62, 51, .045);
    min-height: 105px;
    transition: transform .28s ease, box-shadow .28s ease, border-color .28s ease;
}
div[data-testid="stMetric"]:hover {
    transform: translateY(-2px);
    border-color: #C8CEC2 !important;
    box-shadow: 0 8px 19px rgba(53, 62, 51, .085);
}
div[data-testid="stMetricLabel"], div[data-testid="stMetricLabel"] * { color: var(--text-secondary) !important; font-weight: 650 !important; }
div[data-testid="stMetricValue"], div[data-testid="stMetricValue"] * { color: var(--text-primary) !important; font-weight: 760 !important; }
div[data-testid="stMetricDelta"] { color: var(--text-secondary) !important; }

/* Expanders: keep both closed and open states readable */
details[data-testid="stExpander"] {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 14px !important;
    overflow: hidden;
}
details[data-testid="stExpander"] summary,
details[data-testid="stExpander"] summary * {
    color: var(--text-primary) !important;
    background: var(--surface) !important;
    font-weight: 650 !important;
}
details[data-testid="stExpander"] summary:hover { background: #F4F3ED !important; }
details[data-testid="stExpander"] > div { background: var(--surface) !important; color: var(--text-primary) !important; }

/* Alerts use distinct semantic backgrounds with matching readable text */
div[data-testid="stAlert"] { border-radius: 13px !important; border: 1px solid var(--border) !important; }
div[data-testid="stAlert"][kind="info"] { background: var(--info-bg) !important; }
div[data-testid="stAlert"][kind="success"] { background: var(--success-bg) !important; }
div[data-testid="stAlert"][kind="warning"] { background: var(--warning-bg) !important; }
div[data-testid="stAlert"][kind="error"] { background: var(--error-bg) !important; }
div[data-testid="stAlert"] [data-testid="stMarkdownContainer"],
div[data-testid="stAlert"] [data-testid="stMarkdownContainer"] p,
div[data-testid="stAlert"] [data-testid="stMarkdownContainer"] li { color: var(--text-primary) !important; font-weight: 550 !important; }
div[data-testid="stAlert"] svg { color: currentColor !important; }

/* Tables and dataframe wrappers */
div[data-testid="stDataFrame"], div[data-testid="stTable"] {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 14px !important;
    overflow: hidden;
    box-shadow: 0 4px 14px rgba(53, 62, 51, .04);
}
div[data-testid="stTable"] table { background: var(--surface) !important; color: var(--text-primary) !important; }
div[data-testid="stTable"] th { background: #EFEEE7 !important; color: var(--text-primary) !important; }
div[data-testid="stTable"] td { background: var(--surface) !important; color: var(--text-primary) !important; }

/* Tabs, charts, code and other content containers */
button[data-baseweb="tab"] { color: var(--text-secondary) !important; }
button[data-baseweb="tab"][aria-selected="true"] { color: var(--brand) !important; }
[data-testid="stPlotlyChart"], [data-testid="stVegaLiteChart"] { background: var(--surface) !important; border-radius: 14px; }
[data-testid="stImage"] img {
    border-radius: 14px;
    animation: chart-draw-in 1.35s cubic-bezier(.22, .61, .36, 1) .18s both;
}
[data-testid="stCodeBlock"] { border: 1px solid var(--border); border-radius: 8px; }

/* Keep focus visible for keyboard users */
*:focus-visible { outline-color: #789287; }

@media (max-width: 768px) {
    .block-container { padding: 1rem .85rem 2rem; }
    h1 { font-size: 1.75rem !important; }
    h2 { font-size: 1.25rem !important; }
    div[data-testid="stMetric"] { padding: .8rem !important; }
}

@media (prefers-reduced-motion: reduce) {
    *, *::before, *::after {
        scroll-behavior: auto !important;
        transition-duration: .01ms !important;
        animation-duration: .01ms !important;
        animation-iteration-count: 1 !important;
    }
}
</style>
""", unsafe_allow_html=True)


st.title("🎓 Student Performance Intelligence")

st.markdown(
    """
    Upload student data, explore academic performance, and discover
    where additional learning support may be useful.
    """
)

st.caption("ACADEMIC ANALYTICS  /  PERFORMANCE INSIGHTS  /  DATA-DRIVEN SUPPORT")
st.divider()

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
    except (
        OSError,
        UnicodeDecodeError,
        pd.errors.EmptyDataError,
        pd.errors.ParserError,
    ) as exc:
        st.error(f"Could not read the uploaded CSV: {exc}")
        st.stop()
else:
    try:
        sample_data_path = Path(__file__).resolve().with_name("sample_students.csv")
        raw_data = pd.read_csv(sample_data_path)
        source_name = "students.csv"
    except FileNotFoundError:
        st.error(
            "students.csv was not found. "
            "Upload a valid CSV file to continue."
        )
        st.stop()
    except (
        OSError,
        UnicodeDecodeError,
        pd.errors.EmptyDataError,
        pd.errors.ParserError,
    ) as exc:
        st.error(f"Could not read students.csv: {exc}")
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
invalid_numeric_rows |= data[NUMERIC_COLUMNS].isin(
    [float("inf"), float("-inf")]
).any(axis=1)

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
    # A static table avoids the embedded dataframe's theme-dependent
    # rendering, which can make text unreadable in some browser themes.
    missing_values_table = missing_values.rename("Missing Values").rename_axis(
        "Column"
    ).reset_index()
    st.table(missing_values_table)

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
clean_data = add_performance(clean_data)

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
        search, na=False, regex=False
    )

    matches_id = filtered_data["student_id"].str.lower().str.contains(
        search, na=False, regex=False
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
st.dataframe(
    filtered_data,
    width="stretch",
    alt="Student records matching the selected filters",
)

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

    fig1, ax1 = plt.subplots(figsize=(10, 5), facecolor="#FFFDF9")
    ax1.set_facecolor("#FFFDF9")
    ax1.bar(chart_data["name"], chart_data["average_score"], color="#80988D", width=0.72)
    ax1.set_xlabel("Student")
    ax1.set_ylabel("Average Score")
    ax1.set_ylim(0, 100)
    ax1.set_title("Average Score by Student", color="#344640", pad=14, fontweight="bold")
    ax1.tick_params(axis="x", rotation=45, colors="#687770")
    ax1.tick_params(axis="y", colors="#687770")
    ax1.grid(axis="y", color="#E7E5DC", linewidth=0.8)
    ax1.set_axisbelow(True)
    for spine in ax1.spines.values():
        spine.set_color("#E1E0D8")
    plt.tight_layout()
    st.pyplot(fig1, alt="")
    plt.close(fig1)

    st.header("Study Hours vs Academic Performance")

    fig2, ax2 = plt.subplots(figsize=(8, 5), facecolor="#FFFDF9")
    ax2.set_facecolor("#FFFDF9")
    ax2.scatter(
        filtered_data["study_hours"],
        filtered_data["average_score"],
        color="#B18B70", edgecolors="#FFFDF9", linewidths=0.7, s=70
    )
    ax2.set_xlabel("Weekly Study Hours")
    ax2.set_ylabel("Average Score")
    ax2.set_ylim(0, 100)
    ax2.set_title("Study Hours vs Average Score", color="#344640", pad=14, fontweight="bold")
    ax2.tick_params(axis="x", colors="#687770")
    ax2.tick_params(axis="y", colors="#687770")
    ax2.grid(color="#E7E5DC", linewidth=0.8)
    ax2.set_axisbelow(True)
    for spine in ax2.spines.values():
        spine.set_color("#E1E0D8")
    plt.tight_layout()
    st.pyplot(fig2, alt="")
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

    selected_id = filtered_data.iloc[student_options.index(selected_student)]["student_id"]

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

# Academic Insights
st.header("Academic Insights")

if filtered_data.empty:
    st.info("Apply different filters to analyze student performance.")
else:
    summary = summarize_class(filtered_data)

    st.subheader("Class Summary")

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Students Analyzed",
        summary["student_count"]
    )

    col2.metric(
        "Class Average",
        f"{summary['average_score']:.2f}"
    )

    col3.metric(
        "Average Attendance",
        f"{summary['average_attendance']:.1f}%"
    )

    st.write(
        f"**Area needing the most attention:** "
        f"{summary['weakest_subject']}"
    )

    st.subheader("Students Who May Need Support")

    support_data = identify_students_needing_support(
        filtered_data
    )

    if support_data.empty:
        st.success(
            "No students meet the current support-flagging rules."
        )
    else:
        st.warning(
            f"{len(support_data)} student(s) may benefit "
            "from additional support."
        )

        st.dataframe(
            support_data,
            width="stretch",
            hide_index=True,
            alt="Students flagged as potentially needing additional support",
        )

    st.caption(
        "Support flags use illustrative score and attendance "
        "thresholds. They indicate possible support needs, "
        "not definitive judgments about students."
    )

    st.divider()
    st.subheader("AI Academic Insights Assistant")
    st.write(
        "Generate a teacher-focused report from the current "
        "class statistics."
    )

    if st.button("Generate AI Report", type="primary"):
        with st.spinner("Analyzing class statistics..."):
            ai_api_error = False
            try:
                ai_report = generate_ai_insights(summary, support_data)
            except APIError as exc:
                ai_api_error = True
                ai_report = None
                if exc.code == 503:
                    st.warning(
                        "The AI provider is temporarily unavailable "
                        f"(503: {exc.message}). Showing preliminary "
                        "rule-based insights instead."
                    )
                elif exc.code == 429:
                    st.warning(
                        "The AI provider rate limit has been reached "
                        f"({exc.code}: {exc.message}). Showing "
                        "preliminary rule-based insights instead."
                    )
                else:
                    st.error(
                        "The AI report could not be generated "
                        f"({exc.code}: {exc.message}). Showing "
                        "preliminary rule-based insights instead."
                    )
            except HTTPError:
                ai_api_error = True
                ai_report = None
                st.warning(
                    "The AI provider could not be reached. Check your "
                    "internet connection and try again. Showing "
                    "preliminary rule-based insights instead."
                )

            if ai_report:
                st.markdown(ai_report)
            else:
                if not ai_api_error:
                    st.info(
                        "AI is not configured yet. "
                        "Set GEMINI_API_KEY to enable the AI report."
                    )
                st.markdown("### Preliminary rule-based insights")
                st.write(
                    f"The current class average is "
                    f"{summary['average_score']:.1f}."
                )
                st.write(
                    f"The weakest subject by average score is "
                    f"{summary['weakest_subject']}."
                )
                st.write(
                    f"{len(support_data)} student(s) meet "
                    "the current support-flagging rules."
                )
                st.write(
                    "Consider reviewing the weaker subject, "
                    "offering additional practice, and checking "
                    "whether attendance support is needed."
                )

st.caption(
    "This project uses fictional demonstration data. "
    "Performance categories are illustrative, not official grades."
)

