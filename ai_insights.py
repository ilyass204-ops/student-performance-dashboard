
import json
import os
import warnings

import pandas as pd
import streamlit as st
from streamlit.errors import StreamlitSecretNotFoundError

with warnings.catch_warnings():
    warnings.filterwarnings(
        "ignore",
        message=r"'_UnionGenericAlias' is deprecated and slated for removal in Python 3\.17",
        category=DeprecationWarning,
        module=r"google\.genai\.types",
    )
    from google.genai.errors import APIError


def build_ai_summary(summary, support_data):
    """Prepare anonymous class statistics for the AI."""

    support_reasons = {}

    if not support_data.empty:
        support_reasons = (
            support_data["reasons"]
            .value_counts()
            .to_dict()
        )

    return {
        "student_count": summary["student_count"],
        "average_score": round(
            float(summary["average_score"]), 2
        ),
        "average_attendance": round(
            float(summary["average_attendance"]), 2
        ),
        "weakest_subject": summary["weakest_subject"],
        "support_flag_count": len(support_data),
        "support_reason_counts": support_reasons,
    }


def generate_ai_insights(summary, support_data):
    """Generate a teacher-focused report using Gemini."""

    try:
        api_key = (
            st.secrets.get("GEMINI_API_KEY")
            or st.secrets.get("GOOGLE_API_KEY")
        )
    except StreamlitSecretNotFoundError:
        api_key = None

    api_key = (
        api_key
        or os.getenv("GEMINI_API_KEY")
        or os.getenv("GOOGLE_API_KEY")
    )

    if not api_key:
        return None

    from google import genai
    anonymous_summary = build_ai_summary(
        summary, support_data
    )

    prompt = f"""
You are an academic analytics assistant helping a teacher.

Analyze these anonymous class statistics:
{json.dumps(anonymous_summary, indent=2)}

Write a concise report in clear, professional English.

Use these headings:
1. Class Overview
2. Main Areas for Attention
3. Three Practical Teaching Recommendations
4. Limitations of This Analysis

Rules:
- Use only the statistics provided.
- Do not invent facts or claim that one factor caused another.
- Explain that support flags are screening indicators, not diagnoses.
- Do not recommend automatic grading or punishment.
- Make recommendations practical and respectful.
- If the class is empty, say that there is not enough data.
"""

    client = genai.Client(api_key=api_key)

    try:
        model = (
            st.secrets.get("GEMINI_MODEL")
            or os.getenv("GEMINI_MODEL")
            or "gemini-3.5-flash-lite"
        )
    except StreamlitSecretNotFoundError:
        model = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")

    fallback_models = [
        os.getenv("GEMINI_FALLBACK_MODEL", "gemini-3.1-flash-lite"),
        "gemini-3.1-flash-lite",
        "gemini-3.8-flash",
    ]
    models_to_try = list(dict.fromkeys(
        candidate for candidate in [model, *fallback_models]
        if candidate
    ))

    last_unavailable_error = None
    for candidate in models_to_try:
        try:
            response = client.models.generate_content(
                model=candidate,
                contents=prompt,
            )
            break
        except APIError as exc:
            if exc.code != 503:
                raise
            last_unavailable_error = exc
    else:
        raise last_unavailable_error

    if not response.text:
        raise RuntimeError("Gemini returned an empty response.")

    return response.text
