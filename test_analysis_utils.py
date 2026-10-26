
import pandas as pd

from analysis_utils import (
    summarize_class,
    identify_students_needing_support,
)


def sample_data():
    return pd.DataFrame({
        "student_id": ["S01", "S02", "S03"],
        "name": ["Amina", "Omar", "Sara"],
        "math_score": [80, 45, 70],
        "programming_score": [70, 50, 90],
        "attendance": [90, 65, 85],
        "study_hours": [10, 4, 12],
    })


def test_class_summary():
    result = summarize_class(sample_data())

    assert result["student_count"] == 3
    assert round(result["average_score"], 2) == 67.5
    assert round(result["average_attendance"], 2) == 80
    assert result["weakest_subject"] == "Mathematics"


def test_identifies_students_needing_support():
    result = identify_students_needing_support(sample_data())

    assert set(result["student_id"]) == {"S02"}
    assert "Average score below 60" in result.iloc[0]["reasons"]
    assert "Attendance below 75%" in result.iloc[0]["reasons"]


def test_no_students_need_support():
    data = sample_data()
    data["math_score"] = [80, 85, 90]
    data["programming_score"] = [80, 85, 90]
    data["attendance"] = [90, 95, 85]

    result = identify_students_needing_support(data)

    assert result.empty


def test_empty_class_summary():
    data = sample_data().iloc[0:0]

    result = summarize_class(data)

    assert result["student_count"] == 0
    assert result["weakest_subject"] == "N/A"


def test_empty_support_results():
    data = sample_data().iloc[0:0]

    result = identify_students_needing_support(data)

    assert result.empty
