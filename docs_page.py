import streamlit as st
from pathlib import Path


def init_language_selector():
    languages = {"🇺🇸 English": "en", "🇪🇸 Español": "es", "🇨🇦 Català": "ca"}

    # Initialize state if missing — defaults to English to match the
    # rest of the app on first load. The selector still lets the user
    # switch to any of the translated docs at any time.
    if "selected_lang" not in st.session_state:
        st.session_state.selected_lang = "en"

    # Find the current index so the selectbox doesn't reset on page change
    current_index = list(languages.values()).index(st.session_state.selected_lang)

    # Render the selector at the very top of the sidebar
    selected_label = st.sidebar.selectbox(
        "Language / Idioma",
        options=list(languages.keys()),
        index=current_index,
        key="lang_selector_ui",
    )

    st.session_state.selected_lang = languages[selected_label]


def render_doc_page(md_filename: str, title: str, icon: str = "📄"):
    # 1. Page config ALWAYS first in production
    st.set_page_config(page_title=title, page_icon=icon, layout="wide")

    # 2. Initialize selector
    init_language_selector()
    lang = st.session_state.selected_lang

    # 3. Resolve the project root
    project_root = Path(__file__).resolve().parent

    # Strip any accidental "docs/" left over in the filename string
    clean_filename = Path(md_filename).name

    # Build the path safely
    path = project_root / "docs" / lang / clean_filename

    if not path.exists():
        # Show the absolute path in dev to know exactly where the server looked
        st.error("Documentation file not found on the server.")
        st.code(f"Looked in: {path}")
        return

    st.markdown(path.read_text(encoding="utf-8"))
