"""
UI de Inputs - PcComponentes Content Generator
Versión 4.1.1
"""

import streamlit as st
from typing import Dict, Tuple, List, Optional

from config.archetipos import list_arquetipos, get_arquetipo
from config.settings import (
    MIN_CONTENT_LENGTH,
    MAX_CONTENT_LENGTH,
    DEFAULT_CONTENT_LENGTH,
    MAX_KEYWORDS,
    MAX_SECONDARY_LINKS
)

from core.scraper import scrape_pdp_data


def render_content_inputs() -> Tuple[bool, Dict]:
    """
    Renderiza todos los inputs necesarios para crear contenido nuevo.
    """
    
    config = {}
    
    # Paso 1: Arquetipo
    st.markdown("### 📚 Paso 1: Seleccionar Arquetipo")
    arquetipo_code, campos_arquetipo = render_arquetipo_section()
    config['arquetipo_codigo'] = arquetipo_code
    config['campos_arquetipo'] = campos_arquetipo
    
    if not arquetipo_code:
        st.info("👆 Selecciona un arquetipo para continuar")
        return False, {}
    
    arquetipo = get_arquetipo(arquetipo_code)
    
    # Paso 2: Producto
    st.markdown("---")
    st.markdown("### 🛒 Paso 2: Producto (Opcional)")
    pdp_data = render_product_section()
    config['pdp_data'] = pdp_data
    
    # Paso 3: Keywords
    st.markdown("---")
    st.markdown("### 🔑 Paso 3: Keywords y SEO")
    keywords, objetivo = render_keywords_section()
    config['keywords'] = keywords
    config['objetivo'] = objetivo
    
    # Verificación GSC (OPCIONAL - con manejo de errores)
    config['gsc_analysis'] = None
    if keywords and len(keywords) > 0:
        try:
            from config.settings import GSC_VERIFICATION_ENABLED
            if GSC_VERIFICATION_ENABLED:
                try:
                    from ui.gsc_section import render_gsc_verification_section
                    st.markdown("---")
                    gsc_analysis = render_gsc_verification_section(
                        keyword=keywords[0],
                        show_disclaimer=True
                    )
                    config['gsc_analysis'] = gsc_analysis
                except Exception as e:
                    # GSC falló, continuar sin verificación
                    pass
        except:
            # GSC no configurado, continuar
            pass
    
    # Paso 4: Configuración
    st.markdown("---")
    st.markdown("### ⚙️ Paso 4: Configuración del Contenido")
    target_length, context = render_content_config_section(arquetipo)
    config['target_length'] = target_length
    config['context'] = context
    
    # Paso 5: Enlaces
    st.markdown("---")
    st.markdown("### 🔗 Paso 5: Enlaces")
    links = render_links_section()
    config['links'] = links
    
    # Paso 6: Extras
    st.markdown("---")
    st.markdown("### 🎯 Paso 6: Extras (Opcional)")
    producto_alternativo, casos_uso = render_extras_section()
    config['producto_alternativo'] = producto_alternativo
    config['casos_uso'] = casos_uso
    
    # Validar
    st.markdown("---")
    is_valid, validation_messages = validate_inputs(config)
    
    if not is_valid:
        st.warning("⚠️ **Completa los campos obligatorios:**\n\n" + "\n".join(validation_messages))
        return False, {}
    
    render_generation_summary(config, arquetipo)
    
    # Botón
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        should_generate = st.button(
            "🚀 Generar Contenido",
            type="primary",
            use_container_width=True
        )
    
    return should_generate, config


# ============================================================================
# RESTO DE FUNCIONES (igual que antes)
# ============================================================================

def render_arquetipo_section() -> Tuple[Optional[str], Dict]:
    st.info("Los **arquetipos** son plantillas predefinidas.")
    arquetipos = list_arquetipos()
    arquetipo_options = {f"{arq['code']} - {arq['name']}": arq['code'] for arq in arquetipos}
    
    selected_display = st.selectbox(
        "Seleccionar arquetipo *",
        options=list(arquetipo_options.keys()),
        help="Elige el tipo de contenido"
    )
    
    if not selected_display:
        return None, {}
    
    arquetipo_code = arquetipo_options[selected_display]
    arquetipo = get_arquetipo(arquetipo_code)
    
    with st.expander("ℹ️ Información del Arquetipo", expanded=False):
        st.markdown(f"**{arquetipo['name']}**")
        st.caption(arquetipo['description'])
    
    campos_valores = {}
    campos_especificos = arquetipo.get('campos_especificos', [])
    
    if campos_especificos:
        st.markdown("#### 📝 Campos Específicos")
        for campo in campos_especificos:
            label = campo['label'] + (" *" if campo.get('required') else "")
            if campo['type'] == 'text':
                campos_valores[campo['key']] = st.text_input(label, placeholder=campo.get('placeholder', ''))
            elif campo['type'] == 'textarea':
                campos_valores[campo['key']] = st.text_area(label, placeholder=campo.get('placeholder', ''), height=100)
    
    return arquetipo_code, campos_valores


def render_product_section() -> Optional[Dict]:
    st.info("Introduce la URL del producto para scrapear datos automáticamente.")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        product_url = st.text_input("URL del Producto (opcional)", placeholder="https://www.pccomponentes.com/...")
    with col2:
        scrape_button = st.button("🔍 Scrapear", disabled=not product_url or len(product_url.strip()) < 10, use_container_width=True)
    
    if scrape_button and product_url:
        with st.spinner("Scrapeando..."):
            pdp_data = scrape_pdp_data(product_url)
            if pdp_data:
                st.success("✅ Producto scrapeado")
                st.session_state['scraped_pdp_data'] = pdp_data
                return pdp_data
            else:
                st.error("❌ Error al scrapear")
    
    return st.session_state.get('scraped_pdp_data')


def render_keywords_section() -> Tuple[List[str], str]:
    keyword_principal = st.text_input("Keyword Principal *", placeholder="Ej: mejor portátil gaming 2025")
    keywords_secundarias_input = st.text_area("Keywords Secundarias", placeholder="keyword 1\nkeyword 2", height=100)
    
    keywords = []
    if keyword_principal:
        keywords.append(keyword_principal.strip())
    if keywords_secundarias_input:
        secundarias = [k.strip() for k in keywords_secundarias_input.split('\n') if k.strip() and k.strip() != keyword_principal]
        keywords.extend(secundarias[:MAX_KEYWORDS-1])
    
    objetivo = st.text_area("Objetivo del Contenido *", placeholder="¿Qué quieres lograr?", height=100)
    
    return keywords, objetivo


def render_content_config_section(arquetipo: Dict) -> Tuple[int, str]:
    col1, col2 = st.columns(2)
    
    with col1:
        default_length = arquetipo.get('default_length', DEFAULT_CONTENT_LENGTH)
        target_length = st.number_input(
            "Longitud Objetivo (palabras) *",
            min_value=MIN_CONTENT_LENGTH,
            max_value=MAX_CONTENT_LENGTH,
            value=default_length,
            step=100
        )
    
    with col2:
        st.info(f"💡 Sugerencia: ~{default_length} palabras")
    
    context = st.text_area("Contexto Adicional (opcional)", placeholder="Información adicional...", height=100)
    
    return target_length, context


def render_links_section() -> Dict:
    st.markdown("#### 🔗 Enlace Principal")
    
    col1, col2 = st.columns(2)
    with col1:
        link_url = st.text_input("URL del enlace principal", placeholder="https://...")
    with col2:
        link_text = st.text_input("Texto anchor", placeholder="texto del enlace")
    
    return {
        'principal': {'url': link_url, 'text': link_text},
        'secundarios': []
    }


def render_extras_section() -> Tuple[Dict, List[str]]:
    st.markdown("#### 🎯 Producto Alternativo")
    
    col1, col2 = st.columns(2)
    with col1:
        alt_url = st.text_input("URL producto alternativo", placeholder="https://...")
    with col2:
        alt_text = st.text_input("Nombre del producto", placeholder="Nombre...")
    
    return {'url': alt_url, 'text': alt_text}, []


def validate_inputs(config: Dict) -> Tuple[bool, List[str]]:
    errors = []
    
    if not config.get('arquetipo_codigo'):
        errors.append("❌ Selecciona un arquetipo")
    if not config.get('keywords') or len(config['keywords']) == 0:
        errors.append("❌ Keyword principal requerida")
    if not config.get('objetivo') or len(config['objetivo'].strip()) < 10:
        errors.append("❌ Describe el objetivo")
    if not config.get('target_length') or config['target_length'] < MIN_CONTENT_LENGTH:
        errors.append(f"❌ Longitud mínima: {MIN_CONTENT_LENGTH} palabras")
    
    return len(errors) == 0, errors


def render_generation_summary(config: Dict, arquetipo: Dict) -> None:
    st.markdown("### 📋 Resumen")
    st.info("✅ Todo listo. El proceso tomará 3-5 minutos.")


__version__ = "4.1.1"
