import streamlit as st
from pathlib import Path


def init_language_selector():
    languages = {"🇪🇸 Español": "es", "🇺🇸 English": "en", "🇨🇦 Català": "ca"}

    # Inicializar el estado si no existe
    if "selected_lang" not in st.session_state:
        st.session_state.selected_lang = "es"

    # Encontrar el índice actual para que el selectbox no se resetee al cambiar de página
    current_index = list(languages.values()).index(st.session_state.selected_lang)

    # Renderizar el selector arriba de todo en el sidebar
    selected_label = st.sidebar.selectbox(
        "Language / Idioma",
        options=list(languages.keys()),
        index=current_index,
        key="lang_selector_ui",
    )

    st.session_state.selected_lang = languages[selected_label]


def render_doc_page(md_filename: str, title: str, icon: str = "📄"):
    init_language_selector()
    st.set_page_config(page_title=title, page_icon=icon, layout="wide")

    lang = st.session_state.selected_lang

    project_root = Path(__file__).resolve().parent
    path = project_root / "docs" / lang / md_filename

    if not path.exists():
        st.error(
            f"No se encontró el archivo de documentación: {path.relative_to(project_root)}"
        )
        return

    st.markdown(path.read_text(encoding="utf-8"))
