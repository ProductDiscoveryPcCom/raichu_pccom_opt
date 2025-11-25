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
                except Exception:
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
# SECCIONES DE INPUT
# ============================================================================

def render_arquetipo_section() -> Tuple[Optional[str], Dict]:
    """Renderiza sección de selección de arquetipo"""
    st.info("Los **arquetipos** son plantillas predefinidas.")
    
    # ✅ CORRECCIÓN: Obtener códigos y luego convertir a dicts
    arquetipos_codes = list_arquetipos()
    arquetipos = [get_arquetipo(code) for code in arquetipos_codes]
    
    # ✅ Ahora sí podemos acceder a arq['code'] y arq['name']
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
        st.caption(f"📊 Embudo: {arquetipo['funnel']} | 📝 Longitud sugerida: {arquetipo['default_length']} palabras")
    
    # ✅ CORRECCIÓN: campos_especificos es un DICT, no una lista
    campos_valores = {}
    campos_especificos = arquetipo.get('campos_especificos', {})
    
    if campos_especificos:
        st.markdown("#### 📝 Campos Específicos del Arquetipo")
        st.caption("Completa la información relevante para este tipo de contenido")
        
        for campo_key, campo_info in campos_especificos.items():
            label = campo_info['label']
            if campo_info.get('required', False):
                label += " *"
            
            if campo_info['type'] == 'text':
                campos_valores[campo_key] = st.text_input(
                    label, 
                    placeholder=campo_info.get('placeholder', ''),
                    help=campo_info.get('help', ''),
                    key=f"campo_{campo_key}"
                )
            elif campo_info['type'] == 'textarea':
                campos_valores[campo_key] = st.text_area(
                    label, 
                    placeholder=campo_info.get('placeholder', ''),
                    help=campo_info.get('help', ''),
                    height=100,
                    key=f"campo_{campo_key}"
                )
    
    return arquetipo_code, campos_valores


def render_product_section() -> Optional[Dict]:
    """Renderiza sección de producto"""
    st.info("Introduce la URL del producto para scrapear datos automáticamente.")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        product_url = st.text_input(
            "URL del Producto (opcional)", 
            placeholder="https://www.pccomponentes.com/..."
        )
    with col2:
        scrape_button = st.button(
            "🔍 Scrapear", 
            disabled=not product_url or len(product_url.strip()) < 10, 
            use_container_width=True
        )
    
    if scrape_button and product_url:
        with st.spinner("Scrapeando producto..."):
            pdp_data = scrape_pdp_data(product_url)
            if pdp_data:
                st.success("✅ Producto scrapeado correctamente")
                st.session_state['scraped_pdp_data'] = pdp_data
                
                # Mostrar preview
                with st.expander("👀 Preview de datos scrapeados", expanded=False):
                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.markdown(f"**Nombre:** {pdp_data.get('name', 'N/A')}")
                        st.markdown(f"**Precio:** {pdp_data.get('price', 'N/A')} €")
                    with col_b:
                        st.markdown(f"**Marca:** {pdp_data.get('brand', 'N/A')}")
                        st.markdown(f"**Disponibilidad:** {pdp_data.get('availability', 'N/A')}")
                
                return pdp_data
            else:
                st.error("❌ Error al scrapear el producto")
    
    # Retornar datos previamente scrapeados si existen
    return st.session_state.get('scraped_pdp_data')


def render_keywords_section() -> Tuple[List[str], str]:
    """Renderiza sección de keywords"""
    keyword_principal = st.text_input(
        "Keyword Principal *", 
        placeholder="Ej: mejor portátil gaming 2025"
    )
    
    keywords_secundarias_input = st.text_area(
        "Keywords Secundarias (una por línea)", 
        placeholder="keyword secundaria 1\nkeyword secundaria 2\nkeyword secundaria 3",
        height=100
    )
    
    keywords = []
    if keyword_principal:
        keywords.append(keyword_principal.strip())
    
    if keywords_secundarias_input:
        secundarias = [
            k.strip() for k in keywords_secundarias_input.split('\n') 
            if k.strip() and k.strip() != keyword_principal
        ]
        keywords.extend(secundarias[:MAX_KEYWORDS-1])
    
    objetivo = st.text_area(
        "Objetivo del Contenido *", 
        placeholder="¿Qué quieres lograr con este contenido?",
        height=100
    )
    
    return keywords, objetivo


def render_content_config_section(arquetipo: Dict) -> Tuple[int, str]:
    """Renderiza configuración del contenido"""
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
        st.info(f"💡 Sugerencia del arquetipo: ~{default_length} palabras")
    
    context = st.text_area(
        "Contexto Adicional (opcional)", 
        placeholder="Información adicional, datos internos, perspectiva única...",
        height=100
    )
    
    return target_length, context


def render_links_section() -> Dict:
    """Renderiza sección de enlaces"""
    st.markdown("#### 🔗 Enlace Principal (Recomendado)")
    
    col1, col2 = st.columns(2)
    with col1:
        link_url = st.text_input(
            "URL del enlace principal", 
            placeholder="https://www.pccomponentes.com/categoria"
        )
    with col2:
        link_text = st.text_input(
            "Texto anchor del enlace", 
            placeholder="Ej: portátiles gaming"
        )
    
    return {
        'principal': {'url': link_url, 'text': link_text},
        'secundarios': []
    }


def render_extras_section() -> Tuple[Dict, List[str]]:
    """Renderiza sección de extras"""
    st.markdown("#### 🎯 Producto Alternativo (Opcional)")
    st.caption("Para incluir en el veredicto final como alternativa")
    
    col1, col2 = st.columns(2)
    with col1:
        alt_url = st.text_input(
            "URL del producto alternativo", 
            placeholder="https://www.pccomponentes.com/producto"
        )
    with col2:
        alt_text = st.text_input(
            "Nombre del producto alternativo", 
            placeholder="Nombre del producto"
        )
    
    return {'url': alt_url, 'text': alt_text}, []


# ============================================================================
# VALIDACIÓN Y RESUMEN
# ============================================================================

def validate_inputs(config: Dict) -> Tuple[bool, List[str]]:
    """Valida que todos los inputs obligatorios estén completos"""
    errors = []
    
    if not config.get('arquetipo_codigo'):
        errors.append("❌ Selecciona un arquetipo")
    
    if not config.get('keywords') or len(config['keywords']) == 0:
        errors.append("❌ Introduce al menos una keyword principal")
    
    if not config.get('objetivo') or len(config['objetivo'].strip()) < 10:
        errors.append("❌ Describe el objetivo del contenido (mínimo 10 caracteres)")
    
    if not config.get('target_length') or config['target_length'] < MIN_CONTENT_LENGTH:
        errors.append(f"❌ La longitud mínima es {MIN_CONTENT_LENGTH} palabras")
    
    return len(errors) == 0, errors


def render_generation_summary(config: Dict, arquetipo: Dict) -> None:
    """Renderiza resumen antes de generar"""
    st.markdown("### 📋 Resumen de Configuración")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Contenido:**")
        st.markdown(f"- 📚 Arquetipo: {arquetipo['name']}")
        st.markdown(f"- 📝 Longitud: {config['target_length']:,} palabras")
        st.markdown(f"- 🔑 Keywords: {len(config['keywords'])} configuradas")
    
    with col2:
        st.markdown("**Extras:**")
        pdp = "✅ Sí" if config.get('pdp_data') else "❌ No"
        st.markdown(f"- 🛒 Producto scrapeado: {pdp}")
        
        links = "✅ Sí" if config['links']['principal'].get('url') else "❌ No"
        st.markdown(f"- 🔗 Enlaces configurados: {links}")
    
    st.info("✅ Todo listo. El proceso de generación tomará aproximadamente 3-5 minutos.")


__version__ = "4.1.1"
