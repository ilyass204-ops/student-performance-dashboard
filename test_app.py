from pathlib import Path
from streamlit.testing.v1 import AppTest


def test_demo_and_literal_search():
    app = AppTest.from_file(str(Path(__file__).with_name("app.py"))).run()
    assert not app.exception
    assert not app.error
    app.text_input[0].set_value("[").run()
    assert not app.exception
