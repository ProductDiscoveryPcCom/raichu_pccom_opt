"""
Componentes de input de la UI
"""
import streamlit as st
from typing import Dict, List

from config.archetipos import ARQUETIPOS
from utils.state_manager import StateManager


def render_arquetipo_selector() -> tuple:
    """
    Renderiza selector de arquetipo
    
    Returns:
        Tuple de (arquetipo_code, arquetipo_dict, content_length)
    """
    col1, col2 = st.columns(2)
    
    with col1:
        arquetipo_code = st.selectbox(
            "Arquetipo",
            options=list(ARQUETIPOS.keys()),
            format_func=lambda x: f"{ARQUETIPOS[x]['name']}"
        )
        arquetipo = ARQUETIPOS[arquetipo_code]
        
        st.info(f"**{arquetipo['name']}**\n\n"
                f"{arquetipo['description']}\n\n"
                f"*Uso:* {arquetipo['use_case']}")
    
    with col2:
        content_length = st.slider(
            "Longitud (palabras)",
            min_value=800,
            max_value=3000,
            value=arquetipo['default_length'],
            step=100
        )
    
    return arquetipo_code, arquetipo, content_length


def render_campos_especificos(arquetipo_data: dict) -> dict:
    """
    Renderiza campos de input específicos del arquetipo
    
    Args:
        arquetipo_data: Dict con datos del arquetipo
        
    Returns:
        Dict con valores de los campos
    """
    campos_especificos = arquetipo_data.get('campos_especificos', {})
    
    if not campos_especificos:
        return {}
    
    st.markdown("### 📝 Información Específica del Arquetipo")
    st.caption(f"Completa estos campos para optimizar el contenido tipo "
               f"'{arquetipo_data['name']}'")
    
    valores = {}
    
    for campo_key, campo_config in campos_especificos.items():
        label = campo_config['label']
        tipo = campo_config['type']
        placeholder = campo_config.get('placeholder', '')
        help_text = campo_config.get('help', '')
        
        if tipo == 'text':
            valores[campo_key] = st.text_input(
                label,
                placeholder=placeholder,
                help=help_text,
                key=f"campo_{campo_key}"
            )
        elif tipo == 'textarea':
            valores[campo_key] = st.text_area(
                label,
                placeholder=placeholder,
                help=help_text,
                height=100,
                key=f"campo_{campo_key}"
            )
    
    return valores


def render_keywords_input() -> tuple:
    """
    Renderiza inputs de keywords
    
    Returns:
        Tuple de (keyword_principal, keywords_secundarias, keywords_list)
    """
    st.markdown("### 🔍 Keywords SEO")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        keyword_principal = st.text_input(
            "Keyword Principal (obligatoria)",
            placeholder="robot aspirador xiaomi",
            help="Se verificará si ya existe contenido rankeando para esta keyword"
        )
    
    with col2:
        keywords_secundarias = st.text_input(
            "Keywords secundarias / Variaciones (separadas por comas)",
            placeholder="aspirador inteligente, robot friegasuelos",
            help="Keywords adicionales para optimización SEO"
        )
    
    keywords_list = []
    if keyword_principal:
        keywords_list.append(keyword_principal)
    if keywords_secundarias:
        keywords_list.extend([k.strip() for k in keywords_secundarias.split(',')])
    
    return keyword_principal, keywords_secundarias, keywords_list


def render_links_input() -> dict:
    """
    Renderiza inputs de enlaces internos
    
    Returns:
        Dict con estructura de enlaces
    """
    st.markdown("### 🔗 Enlace Principal")
    col1, col2 = st.columns(2)
    with col1:
        link_principal_url = st.text_input(
            "URL enlace principal",
            placeholder="https://www.pccomponentes.com/black-friday"
        )
    with col2:
        link_principal_text = st.text_input(
            "Texto anchor principal",
            placeholder="ofertas Black Friday"
        )
    
    st.markdown("### 🔗 Enlaces Secundarios (hasta 3)")
    links_secundarios = []
    for i in range(3):
        col1, col2 = st.columns(2)
        with col1:
            url = st.text_input(f"URL secundario {i+1}", key=f"sec_url_{i}")
        with col2:
            text = st.text_input(f"Texto anchor {i+1}", key=f"sec_text_{i}")
        
        if url and text:
            links_secundarios.append({"url": url, "text": text})
    
    return {
        "principal": {
            "url": link_principal_url, 
            "text": link_principal_text
        } if link_principal_url else {},
        "secundarios": links_secundarios
    }
