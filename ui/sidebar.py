"""
Sidebar de la aplicación
"""
import streamlit as st

def render_sidebar():
    """Renderiza el sidebar con información de la app"""
    with st.sidebar:
        st.markdown("## Content Generator")
        st.markdown("**PcComponentes**")
        st.markdown("---")
        
        st.markdown("### 🆕 V4.1 - Notas de la versión")
        features = [
            "18 arquetipos completos",
            "Campos específicos por arquetipo",
            "Verificación GSC",
            "Flujo 3 etapas",
            "CSS compatible con CMS",
            "Modo Reescritura",
            "Análisis Competitivo",
            "Scraping Competidores",
            "**NUEVO: Notas Usuario**"
        ]
        for feature in features:
            st.markdown(f"✅ {feature}")
        
        st.markdown("---")
        st.markdown("### Info")
        st.markdown("Versión 4.1")
        st.markdown("© 2025 PcComponentes")
