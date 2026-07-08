import streamlit as st
from pathlib import Path


def render_doc_page(md_path: str, title: str, icon: str = "📄"):
    st.set_page_config(page_title=title, page_icon=icon, layout="wide")

    # Resuelve la ruta relativa a la raíz del proyecto (donde vive este archivo),
    # sin importar desde qué carpeta se ejecutó `streamlit run`.
    project_root = Path(__file__).resolve().parent
    path = project_root / md_path

    if not path.exists():
        st.error(f"No se encontró el archivo de documentación: {path}")
        return

    st.markdown(path.read_text(encoding="utf-8"))
