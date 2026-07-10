import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from docs_page import render_doc_page

# Pasamos solo el nombre del archivo, la carpeta "docs" y el idioma se manejan internamente
render_doc_page("snowmaking.md", title="Snowmaking", icon="❄️")
