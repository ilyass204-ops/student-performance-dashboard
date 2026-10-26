
import pandas as pd

REQUIRED_COLUMNS = [
    "student_id",
    "name",
    "math_score",
    "programming_score",
    "attendance",
    "study_hours",
]

NUMERIC_COLUMNS = [
    "math_score",
    "programming_score",
    "attendance",
    "study_hours",
]


def validate_columns(data):
    """Check whether all required columns exist."""
    missing = [
        column for column in REQUIRED_COLUMNS
        if column not in data.columns
    ]

    if missing:
        raise ValueError(
            f"Missing required columns: {missing}"
        )


def clean_data(data):
    """Validate and return usable student records."""
    validate_columns(data)

    data = data[REQUIRED_COLUMNS].copy()

    for column in ["student_id", "name"]:
        data[column] = data[column].astype("string").str.strip()
        data[column] = data[column].replace("", pd.NA)

    for column in NUMERIC_COLUMNS:
        data[column] = pd.to_numeric(
            data[column], errors="coerce"
        )

    invalid = (
        data[["student_id", "name"]].isna().any(axis=1)
        | data[NUMERIC_COLUMNS].isna().any(axis=1)
        | ~data["math_score"].between(0, 100)
        | ~data["programming_score"].between(0, 100)
        | ~data["attendance"].between(0, 100)
        | (data["study_hours"] < 0)
        | data["student_id"].duplicated(keep=False)
    )

    return data.loc[~invalid].copy()


def add_performance(data):
    """Calculate average scores and performance categories."""
    result = data.copy()

    result["average_score"] = result[
        ["math_score", "programming_score"]
    ].mean(axis=1)

    result["performance"] = result["average_score"].apply(
        get_performance
    )

    return result


def get_performance(score):
    """Classify a student's average score."""
    if score >= 85:
        return "Excellent"
    elif score >= 70:
        return "Good"
    elif score >= 60:
        return "Pass"
    else:
        return "Needs Improvement"
