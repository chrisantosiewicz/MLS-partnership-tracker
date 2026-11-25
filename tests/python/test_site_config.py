"""The site loads Plotly.js from a CDN at a pinned version. It must match the
version the installed plotly Python package writes figures for, or charts can
break silently on the published page."""

import re
from pathlib import Path

import plotly.offline

QUARTO_YML = Path(__file__).resolve().parents[2] / "site" / "_quarto.yml"


def test_plotly_js_cdn_version_matches_python_package():
    text = QUARTO_YML.read_text()
    pinned = re.findall(r"plotly\.js-dist-min@([\d.]+)/", text)
    assert pinned, "No pinned Plotly.js script found in site/_quarto.yml"
    assert set(pinned) == {plotly.offline.get_plotlyjs_version()}
