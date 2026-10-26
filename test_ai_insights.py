
from unittest.mock import patch
from types import SimpleNamespace

import pandas as pd
import pytest

from ai_insights import APIError, build_ai_summary, generate_ai_insights


def test_summary_does_not_include_student_names_or_ids():
    summary = {
        "student_count": 2,
        "average_score": 72.5,
        "average_attendance": 80.0,
        "weakest_subject": "Mathematics",
    }

    support_data = pd.DataFrame({
        "student_id": ["S01"],
        "name": ["Amina"],
        "average_score": [55.0],
        "attendance": [60.0],
        "reasons": ["Average score below 60"],
    })

    result = build_ai_summary(summary, support_data)

    assert result["student_count"] == 2
    assert result["support_flag_count"] == 1
    assert "name" not in result
    assert "student_id" not in result
    assert "Amina" not in str(result)
    assert "S01" not in str(result)


def test_summary_handles_no_support_flags():
    summary = {
        "student_count": 2,
        "average_score": 80.0,
        "average_attendance": 90.0,
        "weakest_subject": "Programming",
    }

    support_data = pd.DataFrame(
        columns=[
            "student_id",
            "name",
            "average_score",
            "attendance",
            "reasons",
        ]
    )

    result = build_ai_summary(summary, support_data)

    assert result["support_flag_count"] == 0
    assert result["support_reason_counts"] == {}


def test_generate_ai_insights_uses_fallback_model_on_503(monkeypatch):
    import ai_insights

    monkeypatch.setattr(ai_insights.st, "secrets", {
        "GEMINI_API_KEY": "test-key",
    })
    monkeypatch.delenv("GEMINI_MODEL", raising=False)
    monkeypatch.delenv("GEMINI_FALLBACK_MODEL", raising=False)

    support_data = pd.DataFrame(
        columns=[
            "student_id",
            "name",
            "average_score",
            "attendance",
            "reasons",
        ]
    )
    summary = {
        "student_count": 1,
        "average_score": 80.0,
        "average_attendance": 90.0,
        "weakest_subject": "Mathematics",
    }
    overloaded = APIError(
        503,
        {"error": {"code": 503, "message": "Model busy"}},
    )

    with patch("google.genai.Client") as client_factory:
        generate_content = (
            client_factory.return_value.models.generate_content
        )
        generate_content.side_effect = [
            overloaded,
            SimpleNamespace(text="Fallback report"),
        ]

        result = generate_ai_insights(summary, support_data)

    assert result == "Fallback report"
    assert [
        call.kwargs["model"] for call in generate_content.call_args_list
    ] == ["gemini-3.5-flash-lite", "gemini-3.1-flash-lite"]


def test_generate_ai_insights_raises_after_all_models_are_unavailable(
    monkeypatch,
):
    import ai_insights

    monkeypatch.setattr(ai_insights.st, "secrets", {
        "GEMINI_API_KEY": "test-key",
    })
    monkeypatch.delenv("GEMINI_MODEL", raising=False)
    monkeypatch.delenv("GEMINI_FALLBACK_MODEL", raising=False)

    support_data = pd.DataFrame(
        columns=[
            "student_id",
            "name",
            "average_score",
            "attendance",
            "reasons",
        ]
    )
    summary = {
        "student_count": 1,
        "average_score": 80.0,
        "average_attendance": 90.0,
        "weakest_subject": "Mathematics",
    }
    overloaded = APIError(
        503,
        {"error": {"code": 503, "message": "Model busy"}},
    )

    with patch("google.genai.Client") as client_factory:
        generate_content = (
            client_factory.return_value.models.generate_content
        )
        generate_content.side_effect = overloaded

        with pytest.raises(APIError):
            generate_ai_insights(summary, support_data)

    assert generate_content.call_count == 3
