"""
Smoke tests for AeroSense AI Streamlit pages using streamlit.testing.v1.AppTest
Verifies that app.py and all 10 pages import and render without uncaught exceptions.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest
from streamlit.testing.v1 import AppTest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PAGE_FILES = [PROJECT_ROOT / "app.py"] + sorted((PROJECT_ROOT / "pages").glob("*.py"))

@pytest.mark.parametrize("page_path", PAGE_FILES, ids=lambda p: p.name)
def test_streamlit_page_renders_without_exception(page_path: Path):
    at = AppTest.from_file(str(page_path), default_timeout=30)
    at.run()
    assert not at.exception, f"Uncaught Streamlit exception in {page_path.name}: {at.exception}"
