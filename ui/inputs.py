"""
UI de Inputs - PcComponentes Content Generator
Versión 4.1.1

Componente de interfaz para la entrada de datos en modo "Crear Nuevo".
Incluye selección de arquetipo, producto, keywords, enlaces, y verificación GSC.

Autor: PcComponentes - Product Discovery & Content
"""

import streamlit as st
from typing import Dict, Tuple, List, Optional

# Importar configuración y arquetipos
from config.archetipos import list_arquetipos, get_arquetipo
from config.settings import (
    MIN_CONTENT_LENGTH,
    MAX_CONTENT_LENGTH,
    DEFAULT_CONTENT_LENGTH,
    MAX_KEYWORDS,
    MAX_SECONDARY_LINKS,
    GSC_VERIFICATION_ENABLED
)

# Importar scraper
from core.scraper import scrape_pdp_data

# Importar sección GSC
from ui.gsc_section import render_gsc_verification_section


# ============================================================================
# FUNCIÓN PRINCIPAL
# ============================================================================

def render_content_inputs() -> Tuple[bool, Dict]:
    """
    Renderiza todos los inputs necesarios para crear contenido nuevo.
    
    Returns:
        Tuple[bool, Dict]: (should_generate, config_dict)
        - should_generate: True si el usuario quiere iniciar generación
        - config_dict: Diccionario con toda la configuración
        
    Notes:
        - Organiza inputs en secciones lógicas
        - Valida inputs antes de permitir generación
        - Incluye verificación GSC si está habilitada
    """
    
    # Inicializar configuración
    config = {}
    
    # Sección 1: Arquetipo
    st.markdown("### 📚 Paso 1: Seleccionar Arquetipo")
    arquetipo_code, campos_arquetipo = render_arquetipo_section()
    config['arquetipo_codigo'] = arquetipo_code
    config['campos_arquetipo'] = campos_arquetipo
    
    if not arquetipo_code:
        st.info("👆 Selecciona un arquetipo para continuar")
        return False, {}
    
    # Obtener info del arquetipo
    arquetipo = get_arquetipo(arquetipo_code)
    
    # Sección 2: Producto (opcional)
    st.markdown("---")
    st.markdown("### 🛒 Paso 2: Producto (Opcional)")
    pdp_data = render_product_section()
    config['pdp_data'] = pdp_data
    
    # Sección 3: Keywords y SEO
    st.markdown("---")
    st.markdown("### 🔑 Paso 3: Keywords y SEO")
    keywords, objetivo = render_keywords_section()
    config['keywords'] = keywords
    config['objetivo'] = objetivo
    
    # Verificación GSC (si está habilitada y hay keyword principal)
    gsc_analysis = None
    if GSC_VERIFICATION_ENABLED and keywords:
        st.markdown("---")
        gsc_analysis = render_gsc_verification_section(
            keyword=keywords[0],
            show_disclaimer=True
        )
        config['gsc_analysis'] = gsc_analysis
    
    # Sección 4: Configuración de contenido
    st.markdown("---")
    st.markdown("### ⚙️ Paso 4: Configuración del Contenido")
    target_length, context = render_content_config_section(arquetipo)
    config['target_length'] = target_length
    config['context'] = context
    
    # Sección 5: Enlaces
    st.markdown("---")
    st.markdown("### 🔗 Paso 5: Enlaces")
    links = render_links_section()
    config['links'] = links
    
    # Sección 6: Producto alternativo y casos de uso
    st.markdown("---")
    st.markdown("### 🎯 Paso 6: Extras (Opcional)")
    producto_alternativo, casos_uso = render_extras_section()
    config['producto_alternativo'] = producto_alternativo
    config['casos_uso'] = casos_uso
    
    # Validar inputs
    st.markdown("---")
    is_valid, validation_messages = validate_inputs(config, gsc_analysis)
    
    if not is_valid:
        st.warning("⚠️ **Completa los campos obligatorios:**\n\n" + "\n".join(validation_messages))
        return False, {}
    
    # Mostrar resumen
    render_generation_summary(config, arquetipo)
    
    # Botón de generación
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        should_generate = st.button(
            "🚀 Generar Contenido",
            type="primary",
            use_container_width=True
        )
    
    return should_generate, config


# ============================================================================
# SECCIÓN: ARQUETIPO
# ============================================================================

def render_arquetipo_section() -> Tuple[Optional[str], Dict]:
    """
    Renderiza la sección de selección de arquetipo.
    
    Returns:
        Tuple[Optional[str], Dict]: (arquetipo_code, campos_valores)
    """
    
    st.info("""
    Los **arquetipos** son plantillas predefinidas que estructuran el contenido
    según su propósito (review, guía, comparativa, etc.).
    """)
    
    # Obtener lista de arquetipos
    arquetipos = list_arquetipos()
    
    # Crear opciones formateadas
    arquetipo_options = {
        f"{arq['code']} - {arq['name']}": arq['code']
        for arq in arquetipos
    }
    
    # Selectbox de arquetipos
    selected_display = st.selectbox(
        "Seleccionar arquetipo *",
        options=list(arquetipo_options.keys()),
        help="Elige el tipo de contenido que quieres crear"
    )
    
    if not selected_display:
        return None, {}
    
    arquetipo_code = arquetipo_options[selected_display]
    arquetipo = get_arquetipo(arquetipo_code)
    
    # Mostrar info del arquetipo
    with st.expander("ℹ️ Información del Arquetipo", expanded=False):
        st.markdown(f"**{arquetipo['name']}**")
        st.caption(arquetipo['description'])
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Longitud", f"{arquetipo['default_length']} palabras")
        with col2:
            st.metric("Embudo", arquetipo['funnel'])
        with col3:
            st.metric("Caso de uso", arquetipo['use_case'])
    
    # Campos específicos del arquetipo
    campos_valores = render_arquetipo_specific_fields(arquetipo)
    
    return arquetipo_code, campos_valores


def render_arquetipo_specific_fields(arquetipo: Dict) -> Dict:
    """
    Renderiza campos específicos del arquetipo seleccionado.
    
    Args:
        arquetipo: Dict con información del arquetipo
        
    Returns:
        Dict con valores de los campos específicos
    """
    
    campos_especificos = arquetipo.get('campos_especificos', [])
    
    if not campos_especificos:
        return {}
    
    st.markdown("#### 📝 Campos Específicos del Arquetipo")
    
    valores = {}
    
    for campo in campos_especificos:
        label = campo['label']
        tipo = campo['type']
        requerido = campo.get('required', False)
        help_text = campo.get('help', '')
        
        # Añadir asterisco si es requerido
        if requerido:
            label += " *"
        
        # Renderizar según tipo
        if tipo == 'text':
            valores[campo['key']] = st.text_input(
                label,
                placeholder=campo.get('placeholder', ''),
                help=help_text
            )
        
        elif tipo == 'textarea':
            valores[campo['key']] = st.text_area(
                label,
                placeholder=campo.get('placeholder', ''),
                help=help_text,
                height=100
            )
        
        elif tipo == 'number':
            valores[campo['key']] = st.number_input(
                label,
                min_value=campo.get('min', 0),
                max_value=campo.get('max', 100),
                value=campo.get('default', 0),
                help=help_text
            )
        
        elif tipo == 'select':
            valores[campo['key']] = st.selectbox(
                label,
                options=campo.get('options', []),
                help=help_text
            )
        
        elif tipo == 'multiselect':
            valores[campo['key']] = st.multiselect(
                label,
                options=campo.get('options', []),
                help=help_text
            )
    
    return valores


# ============================================================================
# SECCIÓN: PRODUCTO
# ============================================================================

def render_product_section() -> Optional[Dict]:
    """
    Renderiza la sección de producto (scraping de PDP).
    
    Returns:
        Dict con datos del producto o None
    """
    
    st.info("""
    Si tu contenido está centrado en un producto específico, introduce su URL.
    Scrapearemos automáticamente la información del producto.
    """)
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        product_url = st.text_input(
            "URL del Producto (opcional)",
            placeholder="https://www.pccomponentes.com/...",
            help="URL de la página de producto en PcComponentes"
        )
    
    with col2:
        scrape_button = st.button(
            "🔍 Scrapear",
            disabled=not product_url or len(product_url.strip()) < 10,
            use_container_width=True
        )
    
    # Si hay que scrapear
    if scrape_button and product_url:
        with st.spinner("🔍 Scrapeando datos del producto..."):
            pdp_data = scrape_pdp_data(product_url)
            
            if pdp_data:
                st.success("✅ Producto scrapeado exitosamente")
                
                # Mostrar preview
                with st.expander("👁️ Preview de datos scrapeados", expanded=True):
                    col_a, col_b = st.columns(2)
                    
                    with col_a:
                        st.markdown(f"**Nombre:** {pdp_data.get('name', 'N/A')}")
                        st.markdown(f"**Precio:** {pdp_data.get('price', 'N/A')}")
                        st.markdown(f"**Marca:** {pdp_data.get('brand', 'N/A')}")
                    
                    with col_b:
                        st.markdown(f"**Disponibilidad:** {pdp_data.get('availability', 'N/A')}")
                        st.markdown(f"**Rating:** {pdp_data.get('rating', 'N/A')}")
                
                # Guardar en session state
                st.session_state['scraped_pdp_data'] = pdp_data
                
                return pdp_data
            else:
                st.error("❌ No se pudo scrapear el producto. Verifica la URL.")
                return None
    
    # Retornar datos guardados si existen
    return st.session_state.get('scraped_pdp_data')


# ============================================================================
# SECCIÓN: KEYWORDS Y SEO
# ============================================================================

def render_keywords_section() -> Tuple[List[str], str]:
    """
    Renderiza la sección de keywords y objetivo.
    
    Returns:
        Tuple[List[str], str]: (keywords, objetivo)
    """
    
    # Keyword principal
    keyword_principal = st.text_input(
        "Keyword Principal *",
        placeholder="Ej: mejor portátil gaming 2025",
        help="Keyword principal para la que quieres rankear"
    )
    
    # Keywords secundarias
    keywords_secundarias_input = st.text_area(
        "Keywords Secundarias (una por línea)",
        placeholder="keyword relacionada 1\nkeyword relacionada 2\nkeyword relacionada 3",
        help=f"Máximo {MAX_KEYWORDS} keywords en total",
        height=100
    )
    
    # Procesar keywords
    keywords = []
    if keyword_principal:
        keywords.append(keyword_principal.strip())
    
    if keywords_secundarias_input:
        secundarias = [
            k.strip() 
            for k in keywords_secundarias_input.split('\n') 
            if k.strip() and k.strip() != keyword_principal
        ]
        keywords.extend(secundarias[:MAX_KEYWORDS-1])
    
    # Mostrar contador
    if keywords:
        st.caption(f"📊 Total de keywords: {len(keywords)} / {MAX_KEYWORDS}")
    
    # Objetivo
    objetivo = st.text_area(
        "Objetivo del Contenido *",
        placeholder="Ej: Crear la guía más completa sobre portátiles gaming para rankear #1 en Google y generar tráfico a la categoría",
        help="¿Qué quieres lograr con este contenido?",
        height=100
    )
    
    return keywords, objetivo


# ============================================================================
# SECCIÓN: CONFIGURACIÓN DE CONTENIDO
# ============================================================================

def render_content_config_section(arquetipo: Dict) -> Tuple[int, str]:
    """
    Renderiza configuración de longitud y contexto.
    
    Args:
        arquetipo: Dict con información del arquetipo
        
    Returns:
        Tuple[int, str]: (target_length, context)
    """
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Longitud objetivo
        default_length = arquetipo.get('default_length', DEFAULT_CONTENT_LENGTH)
        
        target_length = st.number_input(
            "Longitud Objetivo (palabras) *",
            min_value=MIN_CONTENT_LENGTH,
            max_value=MAX_CONTENT_LENGTH,
            value=default_length,
            step=100,
            help=f"Longitud del contenido entre {MIN_CONTENT_LENGTH} y {MAX_CONTENT_LENGTH} palabras"
        )
    
    with col2:
        # Sugerencia del arquetipo
        st.info(f"💡 **Sugerencia del arquetipo:**\n\n~{default_length} palabras")
    
    # Contexto adicional
    context = st.text_area(
        "Contexto Adicional (opcional)",
        placeholder="Información adicional, datos internos, perspectiva única...",
        help="Cualquier información que ayude a generar mejor contenido",
        height=100
    )
    
    return target_length, context


# ============================================================================
# SECCIÓN: ENLACES
# ============================================================================

def render_links_section() -> Dict:
    """
    Renderiza la sección de enlaces.
    
    Returns:
        Dict con enlaces principales y secundarios
    """
    
    st.markdown("#### 🔗 Enlace Principal")
    
    col1, col2 = st.columns(2)
    
    with col1:
        link_principal_url = st.text_input(
            "URL del enlace principal",
            placeholder="https://www.pccomponentes.com/categoria",
            help="Enlace principal a incluir en los primeros párrafos"
        )
    
    with col2:
        link_principal_text = st.text_input(
            "Texto anchor",
            placeholder="Ej: portátiles gaming",
            help="Texto del enlace (natural y descriptivo)"
        )
    
    # Enlaces secundarios
    st.markdown("#### 🔗 Enlaces Secundarios (Opcional)")
    
    num_links_secundarios = st.number_input(
        "Número de enlaces secundarios",
        min_value=0,
        max_value=MAX_SECONDARY_LINKS,
        value=0,
        help=f"Máximo {MAX_SECONDARY_LINKS} enlaces"
    )
    
    links_secundarios = []
    
    if num_links_secundarios > 0:
        for i in range(num_links_secundarios):
            col_a, col_b = st.columns(2)
            
            with col_a:
                url = st.text_input(
                    f"URL #{i+1}",
                    key=f"link_sec_url_{i}",
                    placeholder="https://..."
                )
            
            with col_b:
                text = st.text_input(
                    f"Texto anchor #{i+1}",
                    key=f"link_sec_text_{i}",
                    placeholder="Texto del enlace"
                )
            
            if url and text:
                links_secundarios.append({
                    'url': url,
                    'text': text
                })
    
    return {
        'principal': {
            'url': link_principal_url,
            'text': link_principal_text
        },
        'secundarios': links_secundarios
    }


# ============================================================================
# SECCIÓN: EXTRAS
# ============================================================================

def render_extras_section() -> Tuple[Dict, List[str]]:
    """
    Renderiza sección de producto alternativo y casos de uso.
    
    Returns:
        Tuple[Dict, List[str]]: (producto_alternativo, casos_uso)
    """
    
    st.markdown("#### 🎯 Producto Alternativo")
    
    col1, col2 = st.columns(2)
    
    with col1:
        alternativo_url = st.text_input(
            "URL producto alternativo",
            placeholder="https://www.pccomponentes.com/producto-alternativo",
            help="Producto alternativo a mencionar en el veredicto"
        )
    
    with col2:
        alternativo_text = st.text_input(
            "Nombre del producto",
            placeholder="Nombre del producto alternativo",
            help="Cómo mencionar el producto"
        )
    
    # Casos de uso
    st.markdown("#### 📝 Casos de Uso Específicos")
    
    casos_uso_input = st.text_area(
        "Casos de uso (uno por línea)",
        placeholder="Gaming competitivo\nEdición de vídeo 4K\nTrabajo con CAD",
        help="Casos de uso específicos para el veredicto",
        height=100
    )
    
    casos_uso = [
        caso.strip() 
        for caso in casos_uso_input.split('\n') 
        if caso.strip()
    ] if casos_uso_input else []
    
    return {
        'url': alternativo_url,
        'text': alternativo_text
    }, casos_uso


# ============================================================================
# VALIDACIÓN Y RESUMEN
# ============================================================================

def validate_inputs(config: Dict, gsc_analysis: Optional[Dict]) -> Tuple[bool, List[str]]:
    """
    Valida que todos los inputs obligatorios estén completos.
    
    Args:
        config: Configuración actual
        gsc_analysis: Análisis de GSC (opcional)
        
    Returns:
        Tuple[bool, List[str]]: (is_valid, error_messages)
    """
    
    errors = []
    
    # Validar arquetipo
    if not config.get('arquetipo_codigo'):
        errors.append("❌ Selecciona un arquetipo")
    
    # Validar keywords
    if not config.get('keywords') or len(config['keywords']) == 0:
        errors.append("❌ Introduce al menos una keyword principal")
    
    # Validar objetivo
    if not config.get('objetivo') or len(config['objetivo'].strip()) < 10:
        errors.append("❌ Describe el objetivo del contenido")
    
    # Validar longitud
    if not config.get('target_length') or config['target_length'] < MIN_CONTENT_LENGTH:
        errors.append(f"❌ La longitud debe ser al menos {MIN_CONTENT_LENGTH} palabras")
    
    # Warning de GSC (no bloquea generación)
    if gsc_analysis and gsc_analysis.get('has_matches'):
        if gsc_analysis.get('recommendation') == 'already_ranking_well':
            errors.append("⚠️ Ya rankeas bien para esta keyword. ¿Seguro que necesitas nuevo contenido?")
    
    return len(errors) == 0, errors


def render_generation_summary(config: Dict, arquetipo: Dict) -> None:
    """
    Muestra un resumen de la configuración antes de generar.
    
    Args:
        config: Configuración actual
        arquetipo: Dict con info del arquetipo
    """
    
    st.markdown("### 📋 Resumen de Generación")
    
    with st.container():
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Configuración básica:**")
            st.markdown(f"- 📚 Arquetipo: `{arquetipo['code']} - {arquetipo['name']}`")
            st.markdown(f"- 🔑 Keyword principal: `{config['keywords'][0]}`")
            st.markdown(f"- 📝 Longitud: `{config['target_length']:,}` palabras")
            
            if config.get('pdp_data'):
                st.markdown(f"- 🛒 Producto: `{config['pdp_data'].get('name', 'N/A')}`")
        
        with col2:
            st.markdown("**Detalles:**")
            st.markdown(f"- 🔗 Enlaces: `{1 if config['links']['principal']['url'] else 0} + {len(config['links']['secundarios'])}`")
            st.markdown(f"- 📊 Keywords adicionales: `{len(config['keywords']) - 1}`")
            
            if config.get('gsc_analysis') and config['gsc_analysis'].get('has_matches'):
                st.markdown(f"- ⚠️ GSC: `{config['gsc_analysis'].get('total_urls', 0)} URLs rankeando`")
    
    st.info("""
    ✅ Todo listo para generar. El proceso tomará 3-5 minutos e incluirá:
    1. Borrador inicial
    2. Análisis crítico
    3. Versión final optimizada
    """)


# ============================================================================
# CONSTANTES
# ============================================================================

__version__ = "4.1.1"
