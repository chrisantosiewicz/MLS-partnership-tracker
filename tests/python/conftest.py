"""Let the tests import the modules in python/ (e.g. `import wiki_pageviews`)."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "python"))
