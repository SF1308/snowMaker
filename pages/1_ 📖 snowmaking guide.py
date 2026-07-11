import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from docs_page import render_doc_page

# The filename (icon + "Snowmaking_Guide") controls how this entry
# looks in the sidebar nav: "📖 Snowmaking Guide".
render_doc_page("snowmaking.md", title="Snowmaking — Docs", icon="📖")
