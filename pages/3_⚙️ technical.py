import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from docs_page import render_doc_page

render_doc_page("technical.md", title="Technical — Docs", icon="⚙️")
