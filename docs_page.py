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
    # 1. Configuración de página SIEMPRE primero en producción
    st.set_page_config(page_title=title, page_icon=icon, layout="wide")

    # 2. Inicializar selector
    init_language_selector()
    lang = st.session_state.selected_lang

    # 3. Asegurar la raíz del proyecto
    project_root = Path(__file__).resolve().parent

    # Limpiamos el md_filename por si acaso le quedó un "docs/" adentro del string anterior
    clean_filename = Path(md_filename).name

    # Construimos el path de forma ultra segura
    path = project_root / "docs" / lang / clean_filename

    if not path.exists():
        # Usamos path absoluto en el error interno de desarrollo para saber EXACTAMENTE dónde buscó el servidor
        st.error("No se encontró el archivo de documentación en el servidor.")
        st.code(f"Buscado en: {path}")
        return

    st.markdown(path.read_text(encoding="utf-8"))
