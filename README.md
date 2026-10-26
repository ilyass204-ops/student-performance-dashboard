# Student Performance Intelligence Dashboard

An interactive Python dashboard for analyzing student academic performance, attendance, and study habits. Built with Streamlit, pandas, and Matplotlib, with optional AI-generated class insights.

## Features

- Explore student academic records through an interactive dashboard
- Analyze average scores and performance categories
- Visualize academic performance and study habits
- Upload and validate student datasets
- Identify students who may need additional academic support
- Generate teacher-focused AI insights from aggregated class statistics
- Fall back to rule-based insights when AI is unavailable
- Run automated tests for data processing, analysis, and AI insight logic

## Technology Stack

- Python
- Streamlit
- pandas
- Matplotlib
- Google Gemini API (`google-genai`)
- pytest

## Getting Started

### 1. Set up the environment

Install Python, then create and activate a virtual environment if you do not already have one.

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 2. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 3. Configure optional AI insights

Set `GEMINI_API_KEY` as an environment variable or configure it in `.streamlit/secrets.toml`.

Example secrets configuration:

```toml
GEMINI_API_KEY = "your-api-key-here"
```

Never commit API keys or other secrets to version control.

AI insights are optional. Without a configured key, the dashboard can provide rule-based insights. The default model is `gemini-3.5-flash-lite`; `GEMINI_MODEL` can be used to select another model supported by your code.

### 4. Run the dashboard

```bash
python -m streamlit run app.py
```

Streamlit will display a local URL in your terminal. Open that URL in your browser.

## Testing

Run the automated test suite:

```bash
python -m pytest -v
```

The current test suite contains 17 tests covering data validation, analysis utilities, and AI insight behavior.

## Dataset and Privacy

Use fictional or appropriately anonymized student data for demonstrations. The local `students.csv` file is excluded from version control; provide a suitable dataset through the application's supported data-loading workflow.

AI insights are designed to use aggregated class statistics rather than student names or IDs.

## Future Improvements

- Expand dashboard usability and accessibility testing
- Add more robust data-quality reporting
- Improve documentation and deployment instructions