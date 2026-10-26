
import pandas as pd
import pytest

from data_utils import (
    validate_columns,
    clean_data,
    add_performance,
    get_performance,
)


def sample_data():
    return pd.DataFrame({
        "student_id": ["A01", "A02"],
        "name": ["Amina", "Omar"],
        "math_score": [90, 50],
        "programming_score": [80, 60],
        "attendance": [95, 70],
        "study_hours": [12, 4],
    })


def test_valid_columns():
    validate_columns(sample_data())


def test_missing_column():
    data = sample_data().drop(columns=["math_score"])

    with pytest.raises(ValueError):
        validate_columns(data)


def test_clean_data_keeps_valid_rows():
    data = sample_data()
    result = clean_data(data)

    assert len(result) == 2


def test_invalid_score_is_removed():
    data = sample_data()
    data.loc[0, "math_score"] = 150

    result = clean_data(data)

    assert len(result) == 1
    assert result.iloc[0]["student_id"] == "A02"


def test_duplicate_ids_are_removed():
    data = sample_data()
    data.loc[1, "student_id"] = "A01"

    result = clean_data(data)

    assert len(result) == 0


def test_average_score():
    result = add_performance(sample_data())

    assert result.iloc[0]["average_score"] == 85
    assert result.iloc[1]["average_score"] == 55


def test_performance_categories():
    assert get_performance(90) == "Excellent"
    assert get_performance(75) == "Good"
    assert get_performance(65) == "Pass"
    assert get_performance(55) == "Needs Improvement"
