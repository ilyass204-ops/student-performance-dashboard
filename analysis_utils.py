
import pandas as pd


def summarize_class(data):
    """Calculate summary statistics for a class."""

    if data.empty:
        return {
            "student_count": 0,
            "average_score": 0.0,
            "average_attendance": 0.0,
            "weakest_subject": "N/A",
        }

    math_average = data["math_score"].mean()
    programming_average = data["programming_score"].mean()

    if math_average < programming_average:
        weakest_subject = "Mathematics"
    elif programming_average < math_average:
        weakest_subject = "Programming"
    else:
        weakest_subject = "Equal performance"

    return {
        "student_count": len(data),
        "average_score": data[
            ["math_score", "programming_score"]
        ].mean(axis=1).mean(),
        "average_attendance": data["attendance"].mean(),
        "weakest_subject": weakest_subject,
    }


def identify_students_needing_support(data):
    """Identify students who may benefit from extra support."""

    results = []

    for _, student in data.iterrows():
        reasons = []

        average_score = (
            student["math_score"] + student["programming_score"]
        ) / 2

        if average_score < 60:
            reasons.append("Average score below 60")

        if student["attendance"] < 75:
            reasons.append("Attendance below 75%")

        if reasons:
            results.append({
                "student_id": student["student_id"],
                "name": student["name"],
                "average_score": round(average_score, 2),
                "attendance": student["attendance"],
                "reasons": "; ".join(reasons),
            })

    return pd.DataFrame(
        results,
        columns=[
            "student_id",
            "name",
            "average_score",
            "attendance",
            "reasons",
        ],
    )
