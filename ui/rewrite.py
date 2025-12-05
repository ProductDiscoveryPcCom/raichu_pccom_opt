# -*- coding: utf-8 -*-
"""
UI de Reescritura - PcComponentes Content Generator
Versión 4.7.1

Este módulo maneja la interfaz de usuario para el modo REESCRITURA,
que analiza contenido competidor y genera una versión mejorada.

CAMBIOS v4.7.1:
- Productos Alternativos: checkbox opcional + N productos con JSON cada uno (nuevo paso 8)
- Enlaces Posts/PLPs: selector tipo (Post/PLP) + campos HTML específicos
  - PLP: Top text + Bottom text (dos campos)
  - Post: Un campo HTML único
- Eliminado JSON de productos en enlaces editoriales (no necesario)

CAMBIOS v4.7.0:
- NUEVO: Paso 2 ahora es HTML a Reescribir (antes era Producto Principal)
- NUEVO: Instrucciones detalladas de reescritura (qué mejorar, mantener, eliminar)
- NUEVO: Modo Fusión de Artículos (para canibalizaciones con múltiples URLs)
- NUEVO: Modo Desambiguación (separar contenido Post vs PLP)
- NUEVO: Soporte para múltiples HTMLs a fusionar
- Todos los 34 arquetipos disponibles
- JSON con tabs (subir/pegar) en todos los enlaces

Flujo actualizado:
1. Input de keyword principal + Verificación GSC
2. Contenido HTML a reescribir (con opciones de fusión/desambiguación)
3. Instrucciones de reescritura (qué mejorar, mantener, eliminar)
4. Producto Principal (opcional con JSON)
5. Obtención de competidores (SEMrush API o manual)
6. Configuración de parámetros (con arquetipo completo)
7. Enlaces a posts/PLPs (con HTML contextual) y productos (con JSON)
8. Productos Alternativos (opcional con JSON cada uno) - NUEVO v4.7.1
9. Generación del contenido mejorado

Autor: PcComponentes - Product Discovery & Content
"""

import streamlit as st
from typing import Dict, List, Optional, Tuple, Any
import json
from datetime import datetime
import re

# Importar utilidades
from utils.html_utils import count_words_in_html

# Importar configuración
from config.settings import (
    GSC_VERIFICATION_ENABLED,
    SEMRUSH_ENABLED,
    SEMRUSH_API_KEY
)

# Importar arquetipos - TODOS los 34
try:
    from config.arquetipos import (
        ARQUETIPOS,
        get_arquetipo,
        get_arquetipo_names,
        get_guiding_questions,
        get_default_length,
        get_length_range,
        get_structure,
        get_tone,
    )
    _arquetipos_available = True
except ImportError:
    _arquetipos_available = False
    ARQUETIPOS = {}
    def get_arquetipo(code): return None
    def get_arquetipo_names(): return {}
    def get_guiding_questions(code, include_universal=True): return []
    def get_default_length(code): return 1500
    def get_length_range(code): return (800, 3000)
    def get_structure(code): return []
    def get_tone(code): return ""

# Importar sección GSC (con manejo de errores)
try:
    from ui.gsc_section import render_gsc_verification_section
    GSC_AVAILABLE = True
except ImportError:
    GSC_AVAILABLE = False

# Importar cliente SEMrush
try:
    from core.semrush import (
        SEMrushClient,
        SEMrushResponse,
        CompetitorData,
        format_competitors_for_display,
        is_semrush_available
    )
    SEMRUSH_MODULE_AVAILABLE = True
except ImportError:
    SEMRUSH_MODULE_AVAILABLE = False
    def is_semrush_available(): return False

# Importar utilidades de JSON de productos
try:
    from utils.product_json_utils import (
        parse_product_json,
        validate_product_json,
        format_product_for_prompt,
        create_product_summary,
        N8N_PRODUCT_JSON_WORKFLOW
    )
    _product_json_available = True
except ImportError:
    _product_json_available = False
    N8N_PRODUCT_JSON_WORKFLOW = "https://n8n.prod.pccomponentes.com/workflow/jsjhKAdZFBSM5XFV/d6c3eb"


# ============================================================================
# VERSIÓN Y CONSTANTES
# ============================================================================

__version__ = "4.7.1"

MAX_COMPETITORS = 10
DEFAULT_REWRITE_LENGTH = 1600
COMPETITION_BEAT_FACTOR = 1.2
MAX_ARTICLES_TO_MERGE = 5
MAX_ALTERNATIVE_PRODUCTS = 10  # NUEVO v4.7.1
MAX_EDITORIAL_LINKS = 10  # NUEVO v4.7.1
MAX_PRODUCT_LINKS = 10  # NUEVO v4.7.1


# ============================================================================
# MODOS DE REESCRITURA
# ============================================================================

class RewriteMode:
    """Modos de reescritura disponibles."""
    SINGLE = "single"           # Reescribir un solo artículo
    MERGE = "merge"             # Fusionar múltiples artículos (canibalización)
    DISAMBIGUATE = "disambiguate"  # Desambiguar post vs PLP


REWRITE_MODE_OPTIONS = {
    RewriteMode.SINGLE: {
        "name": "📝 Reescribir artículo",
        "description": "Mejora un artículo existente manteniendo su esencia",
        "help": "Ideal para actualizar contenido obsoleto o mejorar posicionamiento"
    },
    RewriteMode.MERGE: {
        "name": "🔀 Fusionar artículos",
        "description": "Combina varios artículos que canibalizan la misma keyword",
        "help": "Para resolver canibalizaciones: crea UN contenido definitivo a partir de varios"
    },
    RewriteMode.DISAMBIGUATE: {
        "name": "🎯 Desambiguar contenido",
        "description": "Separa contenido editorial (post) de contenido transaccional (PLP)",
        "help": "Cuando un post está robando tráfico a una PLP o viceversa"
    }
}


# ============================================================================
# TIPOS DE CONTENIDO EDITORIAL (NUEVO v4.7.1)
# ============================================================================

class EditorialType:
    """Tipos de contenido editorial para enlaces."""
    POST = "post"
    PLP = "plp"


EDITORIAL_TYPE_OPTIONS = {
    EditorialType.POST: {
        "name": "📝 Post / Guía / Blog",
        "description": "Contenido editorial con un único bloque HTML",
        "placeholder": """<article>
  <h1>Título del post...</h1>
  <p>Contenido del post que servirá de contexto para enlazar...</p>
</article>"""
    },
    EditorialType.PLP: {
        "name": "🛒 PLP / Categoría",
        "description": "Página de listado con Top text y Bottom text",
        "placeholder_top": """<div class="category-top">
  <h1>Portátiles Gaming</h1>
  <p>Descubre nuestra selección de portátiles gaming...</p>
</div>""",
        "placeholder_bottom": """<div class="category-bottom">
  <h2>¿Cómo elegir tu portátil gaming?</h2>
  <p>A la hora de elegir un portátil gaming...</p>
</div>"""
    }
}


# ============================================================================
# FUNCIÓN PRINCIPAL DE RENDERIZADO
# ============================================================================

def render_rewrite_section() -> Tuple[bool, Dict]:
    """
    Renderiza la sección completa del modo reescritura.
    
    Esta función gestiona toda la interfaz del modo reescritura, incluyendo:
    - Input de keyword y configuración
    - Verificación GSC
    - Contenido HTML a reescribir (con modos: single, merge, disambiguate)
    - Instrucciones de reescritura (qué mejorar, mantener, eliminar)
    - Producto Principal
    - Obtención de competidores (SEMrush o manual)
    - Configuración de parámetros de generación (con todos los arquetipos)
    - Enlaces a posts/PLPs (con HTML contextual) y productos (con JSON)
    - Productos Alternativos (con JSON cada uno)
    
    Returns:
        Tuple[bool, Dict]: (debe_generar, config_dict)
    """
    
    st.markdown("## 🔄 Modo: Reescritura Competitiva")
    
    # Determinar método de obtención de competidores
    semrush_available = SEMRUSH_MODULE_AVAILABLE and is_semrush_available()
    
    # Info box según disponibilidad
    if semrush_available:
        st.success("""
        **✅ SEMrush API Conectada**
        
        1. 🔍 Verifica si ya rankeas para esta keyword (GSC)
        2. 📄 Define el contenido a reescribir/fusionar/desambiguar
        3. ✏️ Indica qué mejorar, mantener o eliminar
        4. 📦 Define el producto principal (opcional)
        5. 📊 Analiza competidores automáticamente
        6. ✍️ Genera contenido **superior** optimizado
        """)
    else:
        st.info("""
        **📝 Modo Manual** (SEMrush no configurado)
        
        1. 🔍 Verifica si ya rankeas para esta keyword (GSC)
        2. 📄 Define el contenido a reescribir/fusionar/desambiguar
        3. ✏️ Indica qué mejorar, mantener o eliminar
        4. 📦 Define el producto principal (opcional)
        5. 🔍 Introduce URLs de competidores manualmente
        6. ✍️ Genera contenido **superior** optimizado
        """)
    
    # Inicializar estado si no existe
    _initialize_rewrite_state()
    
    # Procesar eliminaciones pendientes ANTES de renderizar widgets
    _process_pending_deletions()
    
    # =========================================================================
    # PASO 1: Keyword y verificación GSC
    # =========================================================================
    st.markdown("---")
    st.markdown("### 🎯 Paso 1: Keyword Principal")
    
    keyword, should_search = render_keyword_input()
    
    # Verificación GSC (si está habilitada y hay keyword)
    gsc_analysis = None
    if GSC_VERIFICATION_ENABLED and GSC_AVAILABLE and keyword and len(keyword.strip()) >= 3:
        st.markdown("---")
        gsc_analysis = render_gsc_verification_section(
            keyword=keyword,
            show_disclaimer=True
        )
        st.session_state.rewrite_gsc_analysis = gsc_analysis
        
        # Advertencia si ya rankea bien
        if gsc_analysis and gsc_analysis.get('has_matches'):
            if gsc_analysis.get('recommendation') == 'already_ranking_well':
                st.warning("""
                ⚠️ **Precaución**: Ya rankeas en top 10 para esta keyword.
                
                Considera si realmente necesitas crear contenido nuevo o si deberías 
                mejorar el contenido existente.
                """)
            
            # Sugerir fusión si hay múltiples URLs
            urls_ranking = gsc_analysis.get('matches', [])
            if len(set(m.get('url') for m in urls_ranking)) > 1:
                st.info("""
                💡 **Detectadas múltiples URLs rankeando** - Considera usar el modo 
                **🔀 Fusionar artículos** para consolidar el contenido y evitar canibalización.
                """)
    
    # =========================================================================
    # PASO 2: Contenido HTML a Reescribir (AHORA PRIMERO)
    # =========================================================================
    st.markdown("---")
    st.markdown("### 📄 Paso 2: Contenido a Reescribir")
    
    rewrite_mode, html_contents, disambiguation_config = render_html_content_section()
    
    # =========================================================================
    # PASO 3: Instrucciones de Reescritura (NUEVO)
    # =========================================================================
    st.markdown("---")
    st.markdown("### ✏️ Paso 3: Instrucciones de Reescritura")
    
    rewrite_instructions = render_rewrite_instructions_section(rewrite_mode)
    
    # =========================================================================
    # PASO 4: Producto Principal
    # =========================================================================
    st.markdown("---")
    st.markdown("### 📦 Paso 4: Producto Principal (Opcional)")
    
    main_product_data = render_main_product_section()
    
    # =========================================================================
    # PASO 5: Obtener competidores
    # =========================================================================
    st.markdown("---")
    st.markdown("### 🏆 Paso 5: Análisis de Competidores")
    
    if semrush_available:
        # Modo SEMrush automático
        if should_search and keyword:
            _fetch_competitors_semrush(keyword, gsc_analysis)
    else:
        # Modo manual
        render_manual_competitors_input(keyword)
    
    # Mostrar competidores si existen
    if st.session_state.rewrite_competitors_data:
        render_competitors_summary(st.session_state.rewrite_competitors_data)
    
    # =========================================================================
    # PASO 6: Configuración de parámetros (con TODOS los arquetipos)
    # =========================================================================
    st.markdown("---")
    st.markdown("### ⚙️ Paso 6: Configuración del Contenido")
    
    rewrite_config = render_rewrite_configuration(keyword, rewrite_mode)
    
    # =========================================================================
    # PASO 7: Enlaces a Incluir (ACTUALIZADO v4.7.1)
    # =========================================================================
    st.markdown("---")
    st.markdown("### 🔗 Paso 7: Enlaces a Incluir")
    
    # Sección 1: Posts/PLPs con HTML contextual (ACTUALIZADO v4.7.1)
    with st.expander("📝 Enlaces a Posts / PLPs (Contenido Editorial)", expanded=True):
        st.info("💡 **Enlaces a contenido editorial**: Añade el HTML del contenido destino para que los enlaces sean más contextuales y naturales.")
        posts_plps_links = render_posts_plps_links_section()
    
    # Sección 2: Productos con JSON
    with st.expander("🛒 Enlaces a Productos (con datos estructurados)", expanded=True):
        st.info(f"💡 **Enlaces a productos**: PDPs con opción de cargar JSON. [Workflow n8n]({N8N_PRODUCT_JSON_WORKFLOW})")
        product_links = render_product_links_section()
    
    # =========================================================================
    # PASO 8: Productos Alternativos (NUEVO v4.7.1)
    # =========================================================================
    st.markdown("---")
    st.markdown("### 🎯 Paso 8: Productos Alternativos (Opcional)")
    
    alternative_products = render_alternative_products_section()
    
    # =========================================================================
    # VALIDAR Y PREPARAR
    # =========================================================================
    
    # Validar que todo esté listo para generar
    can_generate = validate_rewrite_inputs(
        keyword,
        st.session_state.rewrite_competitors_data,
        rewrite_config,
        gsc_analysis,
        html_contents,
        rewrite_mode
    )
    
    st.markdown("---")
    
    if not can_generate:
        st.warning("⚠️ Completa todos los pasos anteriores para poder generar el contenido.")
        return False, {}
    
    # Mostrar resumen antes de generar
    render_generation_summary(
        keyword, rewrite_config, gsc_analysis, html_contents, 
        main_product_data, rewrite_mode, rewrite_instructions,
        alternative_products, posts_plps_links
    )
    
    # Preparar configuración completa (el botón está en app.py)
    full_config = prepare_rewrite_config(
        keyword=keyword,
        competitors_data=st.session_state.rewrite_competitors_data,
        rewrite_config=rewrite_config,
        gsc_analysis=gsc_analysis,
        html_contents=html_contents,
        rewrite_mode=rewrite_mode,
        rewrite_instructions=rewrite_instructions,
        disambiguation_config=disambiguation_config,
        main_product_data=main_product_data,
        posts_plps_links=posts_plps_links,
        product_links=product_links,
        alternative_products=alternative_products
    )
    
    return True, full_config


# ============================================================================
# INICIALIZACIÓN DE ESTADO
# ============================================================================

def _initialize_rewrite_state() -> None:
    """Inicializa variables de estado para el modo rewrite."""
    
    if 'rewrite_competitors_data' not in st.session_state:
        st.session_state.rewrite_competitors_data = None
    if 'rewrite_analysis' not in st.session_state:
        st.session_state.rewrite_analysis = None
    if 'rewrite_gsc_analysis' not in st.session_state:
        st.session_state.rewrite_gsc_analysis = None
    if 'last_rewrite_keyword' not in st.session_state:
        st.session_state.last_rewrite_keyword = ''
    if 'manual_urls_input' not in st.session_state:
        st.session_state.manual_urls_input = ''
    if 'semrush_response' not in st.session_state:
        st.session_state.semrush_response = None
    # Estado para modo de reescritura
    if 'rewrite_mode' not in st.session_state:
        st.session_state.rewrite_mode = RewriteMode.SINGLE
    # Estado para HTMLs (puede ser uno o múltiples)
    if 'html_contents' not in st.session_state:
        st.session_state.html_contents = []
    if 'html_articles_count' not in st.session_state:
        st.session_state.html_articles_count = 1
    # Estado para enlaces
    if 'rewrite_posts_plps_count' not in st.session_state:
        st.session_state.rewrite_posts_plps_count = 1
    if 'rewrite_product_links_count' not in st.session_state:
        st.session_state.rewrite_product_links_count = 1
    # Estado para producto principal
    if 'rewrite_main_product_enabled' not in st.session_state:
        st.session_state.rewrite_main_product_enabled = False
    if 'rewrite_main_product_json' not in st.session_state:
        st.session_state.rewrite_main_product_json = None
    # Estado para productos alternativos (NUEVO v4.7.1)
    if 'rewrite_alt_products_enabled' not in st.session_state:
        st.session_state.rewrite_alt_products_enabled = False
    if 'rewrite_alt_products_count' not in st.session_state:
        st.session_state.rewrite_alt_products_count = 1


# ============================================================================
# SECCIÓN: CONTENIDO HTML A REESCRIBIR (MEJORADA)
# ============================================================================

def render_html_content_section() -> Tuple[str, List[Dict[str, Any]], Optional[Dict]]:
    """
    Renderiza la sección de contenido HTML con opciones de:
    - Reescritura simple
    - Fusión de artículos
    - Desambiguación
    
    Returns:
        Tuple[mode, html_contents, disambiguation_config]
        - mode: Modo de reescritura (single/merge/disambiguate)
        - html_contents: Lista de dicts con {url, html, title, word_count}
        - disambiguation_config: Config para desambiguación (si aplica)
    """
    
    # Selector de modo
    st.markdown("**¿Qué quieres hacer?**")
    
    mode_options = list(REWRITE_MODE_OPTIONS.keys())
    mode_labels = [REWRITE_MODE_OPTIONS[m]["name"] for m in mode_options]
    
    selected_mode_idx = st.radio(
        "Modo de reescritura",
        options=range(len(mode_options)),
        format_func=lambda x: mode_labels[x],
        horizontal=True,
        key="rewrite_mode_selector",
        label_visibility="collapsed"
    )
    
    selected_mode = mode_options[selected_mode_idx]
    st.session_state.rewrite_mode = selected_mode
    
    # Mostrar descripción del modo
    mode_info = REWRITE_MODE_OPTIONS[selected_mode]
    st.caption(f"ℹ️ {mode_info['description']}")
    
    html_contents = []
    disambiguation_config = None
    
    # =========================================================================
    # MODO: Reescribir artículo único
    # =========================================================================
    if selected_mode == RewriteMode.SINGLE:
        html_contents = render_single_article_input()
    
    # =========================================================================
    # MODO: Fusionar artículos
    # =========================================================================
    elif selected_mode == RewriteMode.MERGE:
        html_contents = render_merge_articles_input()
    
    # =========================================================================
    # MODO: Desambiguar contenido
    # =========================================================================
    elif selected_mode == RewriteMode.DISAMBIGUATE:
        html_contents, disambiguation_config = render_disambiguate_input()
    
    return selected_mode, html_contents, disambiguation_config


def render_single_article_input() -> List[Dict[str, Any]]:
    """
    Renderiza input para un solo artículo a reescribir.
    
    Returns:
        Lista con un solo dict {url, html, title, word_count}
    """
    
    st.markdown("""
    Pega el código HTML del artículo que quieres mejorar.
    """)
    
    # Checkbox para activar
    use_existing = st.checkbox(
        "Tengo un artículo existente para reescribir",
        value=bool(st.session_state.get('html_to_rewrite', '')),
        help="Activa esta opción si quieres mejorar un artículo existente"
    )
    
    if not use_existing:
        st.caption("💡 Si no tienes contenido existente, se generará contenido nuevo basado en el análisis competitivo.")
        return []
    
    # URL del artículo original
    article_url = st.text_input(
        "URL del artículo original",
        key="rewrite_single_url",
        placeholder="https://www.pccomponentes.com/blog/...",
        help="URL actual del artículo (para referencia)"
    )
    
    # Título del artículo
    article_title = st.text_input(
        "Título del artículo",
        key="rewrite_single_title",
        placeholder="Título actual del artículo",
        help="Título H1 del artículo actual"
    )
    
    # HTML del artículo
    html_content = st.text_area(
        "Código HTML del artículo",
        value=st.session_state.get('html_to_rewrite', ''),
        height=200,
        key="rewrite_single_html",
        placeholder="""<article>
  <h1>Título del artículo...</h1>
  <p>Contenido...</p>
</article>""",
        help="Pega el código HTML completo del artículo"
    )
    
    # Guardar en session state
    st.session_state.html_to_rewrite = html_content
    
    # Mostrar estadísticas si hay contenido
    if html_content and html_content.strip():
        _show_html_stats(html_content)
        
        return [{
            'url': article_url.strip() if article_url else '',
            'html': html_content,
            'title': article_title.strip() if article_title else '',
            'word_count': len(_strip_html_tags(html_content).split()),
            'type': 'main'
        }]
    
    return []


def render_merge_articles_input() -> List[Dict[str, Any]]:
    """
    Renderiza input para múltiples artículos a fusionar.
    
    Returns:
        Lista de dicts {url, html, title, word_count, priority}
    """
    
    st.markdown("""
    **🔀 Fusión de Artículos**
    
    Añade todos los artículos que están canibalizando la misma keyword.
    Se creará UN único contenido definitivo que consolide lo mejor de cada uno.
    """)
    
    st.info("""
    💡 **Tips para fusionar:**
    - Ordena los artículos por **prioridad** (el primero será la base principal)
    - Indica qué **secciones únicas** de cada artículo deben conservarse
    - El nuevo contenido tendrá una estructura coherente sin duplicidades
    """)
    
    count_key = 'html_articles_count'
    current_count = st.session_state.get(count_key, 2)  # Mínimo 2 para fusión
    
    if current_count < 2:
        st.session_state[count_key] = 2
        current_count = 2
    
    html_contents = []
    
    for i in range(current_count):
        priority_label = "🥇 Principal" if i == 0 else f"🔗 Artículo {i + 1}"
        
        with st.expander(f"{priority_label}", expanded=(i < 2)):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                url = st.text_input(
                    f"URL del artículo {i+1}",
                    key=f"merge_url_{i}",
                    placeholder="https://www.pccomponentes.com/...",
                    help="URL actual del artículo"
                )
            
            with col2:
                title = st.text_input(
                    f"Título {i+1}",
                    key=f"merge_title_{i}",
                    placeholder="Título del artículo",
                    help="Título H1"
                )
            
            html = st.text_area(
                f"HTML del artículo {i+1}",
                height=150,
                key=f"merge_html_{i}",
                placeholder="<article>...</article>",
                help="Código HTML del artículo"
            )
            
            # Notas sobre qué conservar de este artículo
            keep_notes = st.text_input(
                f"¿Qué conservar de este artículo?",
                key=f"merge_keep_{i}",
                placeholder="Ej: La sección de comparativa, los datos técnicos...",
                help="Indica qué partes únicas de este artículo deben incluirse en el fusionado"
            )
            
            if html and html.strip():
                word_count = len(_strip_html_tags(html).split())
                st.caption(f"📊 {word_count} palabras")
                
                html_contents.append({
                    'url': url.strip() if url else '',
                    'html': html,
                    'title': title.strip() if title else f'Artículo {i+1}',
                    'word_count': word_count,
                    'priority': i + 1,
                    'keep_notes': keep_notes.strip() if keep_notes else '',
                    'type': 'main' if i == 0 else 'merge'
                })
            
            # Botón eliminar (solo si hay más de 2)
            if current_count > 2 and i > 0:
                if st.button(f"🗑️ Eliminar", key=f"merge_del_{i}"):
                    # Shift hacia arriba
                    for j in range(i, current_count - 1):
                        for field in ['url', 'title', 'html', 'keep']:
                            next_val = st.session_state.get(f"merge_{field}_{j+1}", "")
                            st.session_state[f"merge_{field}_{j}"] = next_val
                    
                    # Limpiar última
                    last_idx = current_count - 1
                    for field in ['url', 'title', 'html', 'keep']:
                        if f"merge_{field}_{last_idx}" in st.session_state:
                            del st.session_state[f"merge_{field}_{last_idx}"]
                    
                    st.session_state[count_key] = max(2, current_count - 1)
                    st.rerun()
    
    # Botón añadir
    if current_count < MAX_ARTICLES_TO_MERGE:
        if st.button("➕ Añadir otro artículo", key="merge_add"):
            st.session_state[count_key] = current_count + 1
            st.rerun()
    
    # Resumen
    if len(html_contents) >= 2:
        total_words = sum(a['word_count'] for a in html_contents)
        st.success(f"✅ {len(html_contents)} artículos para fusionar ({total_words:,} palabras totales)")
    elif len(html_contents) == 1:
        st.warning("⚠️ Necesitas al menos 2 artículos para fusionar")
    
    return html_contents


def render_disambiguate_input() -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """
    Renderiza input para desambiguar contenido (Post vs PLP).
    
    Returns:
        Tuple[html_contents, disambiguation_config]
    """
    
    st.markdown("""
    **🎯 Desambiguación de Contenido**
    
    Cuando un Post está canibalizando a una PLP (o viceversa), necesitas 
    diferenciar claramente la intención de cada uno.
    """)
    
    # Explicación de los tipos
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **📝 Post / Editorial**
        - Intención: Informativa
        - Contenido: Guías, tutoriales, comparativas
        - Enfoque: Educar, informar, ayudar
        - Keywords: "cómo", "qué es", "mejores"
        """)
    
    with col2:
        st.markdown("""
        **🛒 PLP / Categoría**
        - Intención: Transaccional
        - Contenido: Listado de productos
        - Enfoque: Vender, convertir
        - Keywords: "comprar", "precio", "oferta"
        """)
    
    st.markdown("---")
    
    # Qué tipo de contenido vas a crear
    output_type = st.radio(
        "¿Qué tipo de contenido quieres generar?",
        options=["post", "plp"],
        format_func=lambda x: "📝 Post / Editorial" if x == "post" else "🛒 PLP / Categoría",
        horizontal=True,
        key="disambiguate_output_type"
    )
    
    st.markdown("---")
    
    # Input del contenido conflictivo
    st.markdown("**Contenido actual que genera conflicto:**")
    
    conflict_url = st.text_input(
        "URL del contenido conflictivo",
        key="disambiguate_conflict_url",
        placeholder="https://www.pccomponentes.com/...",
        help="URL del contenido que está canibalizando"
    )
    
    conflict_html = st.text_area(
        "HTML del contenido conflictivo",
        height=200,
        key="disambiguate_conflict_html",
        placeholder="<article>...</article>",
        help="Pega el HTML del contenido que causa el conflicto"
    )
    
    html_contents = []
    
    if conflict_html and conflict_html.strip():
        word_count = len(_strip_html_tags(conflict_html).split())
        st.caption(f"📊 {word_count} palabras en contenido conflictivo")
        
        html_contents.append({
            'url': conflict_url.strip() if conflict_url else '',
            'html': conflict_html,
            'title': 'Contenido conflictivo',
            'word_count': word_count,
            'type': 'conflict'
        })
    
    # Instrucciones de desambiguación
    st.markdown("---")
    st.markdown("**Instrucciones de desambiguación:**")
    
    if output_type == "post":
        disambiguate_instructions = st.text_area(
            "¿Qué enfoque debe tener el POST?",
            key="disambiguate_post_instructions",
            height=100,
            placeholder="""Ej:
- Enfocarse en "cómo elegir" en lugar de "comprar"
- Añadir más contenido educativo sobre especificaciones
- Incluir comparativas detalladas
- Eliminar listados de productos y CTAs de compra""",
            help="Indica cómo debe diferenciarse el post de la PLP"
        )
    else:
        disambiguate_instructions = st.text_area(
            "¿Qué enfoque debe tener la PLP?",
            key="disambiguate_plp_instructions",
            height=100,
            placeholder="""Ej:
- Enfocarse en productos disponibles y precios
- Reducir contenido informativo extenso
- Destacar ofertas y CTAs de compra
- Mantener solo specs esenciales para filtrar""",
            help="Indica cómo debe diferenciarse la PLP del post"
        )
    
    # URL de la otra pieza (opcional)
    other_url = st.text_input(
        f"URL de la {'PLP' if output_type == 'post' else 'Post'} que debe diferenciarse",
        key="disambiguate_other_url",
        placeholder="https://www.pccomponentes.com/...",
        help="URL del otro contenido para asegurar que no se solapen"
    )
    
    disambiguation_config = {
        'output_type': output_type,
        'instructions': disambiguate_instructions.strip() if disambiguate_instructions else '',
        'other_url': other_url.strip() if other_url else '',
        'conflict_url': conflict_url.strip() if conflict_url else ''
    }
    
    return html_contents, disambiguation_config


# ============================================================================
# SECCIÓN: INSTRUCCIONES DE REESCRITURA (NUEVO)
# ============================================================================

def render_rewrite_instructions_section(rewrite_mode: str) -> Dict[str, Any]:
    """
    Renderiza la sección de instrucciones detalladas de reescritura.
    
    Args:
        rewrite_mode: Modo actual (single/merge/disambiguate)
        
    Returns:
        Dict con todas las instrucciones de reescritura
    """
    
    instructions = {
        'improve': [],
        'maintain': [],
        'remove': [],
        'add': [],
        'tone_changes': '',
        'structure_changes': '',
        'seo_focus': '',
        'additional_notes': ''
    }
    
    st.markdown("""
    Indica qué cambios específicos quieres en el contenido reescrito.
    Estas instrucciones guiarán la generación para obtener exactamente lo que necesitas.
    """)
    
    # =========================================================================
    # Qué MEJORAR
    # =========================================================================
    with st.expander("✨ ¿Qué MEJORAR?", expanded=True):
        st.caption("Aspectos del contenido actual que necesitan mejorarse")
        
        improve_text = st.text_area(
            "Puntos a mejorar",
            key="rewrite_improve",
            height=100,
            placeholder="""Ej:
- La introducción es muy larga y poco atractiva
- Faltan datos técnicos actualizados (benchmark 2024)
- Las comparativas son superficiales
- El contenido no responde bien a la intención de búsqueda
- SEO: faltan H2 con keywords secundarias""",
            help="Lista todo lo que debe mejorarse del contenido actual",
            label_visibility="collapsed"
        )
        
        if improve_text:
            instructions['improve'] = [
                line.strip().lstrip('-•*') 
                for line in improve_text.split('\n') 
                if line.strip()
            ]
    
    # =========================================================================
    # Qué MANTENER
    # =========================================================================
    with st.expander("✅ ¿Qué MANTENER?", expanded=True):
        st.caption("Aspectos del contenido actual que funcionan bien y deben conservarse")
        
        maintain_text = st.text_area(
            "Puntos a mantener",
            key="rewrite_maintain",
            height=100,
            placeholder="""Ej:
- La tabla comparativa de especificaciones
- El tono experto pero accesible
- La estructura de FAQs (están bien posicionadas)
- Los enlaces internos actuales
- El veredicto final (está bien argumentado)""",
            help="Lista todo lo que funciona y debe mantenerse",
            label_visibility="collapsed"
        )
        
        if maintain_text:
            instructions['maintain'] = [
                line.strip().lstrip('-•*') 
                for line in maintain_text.split('\n') 
                if line.strip()
            ]
    
    # =========================================================================
    # Qué ELIMINAR
    # =========================================================================
    with st.expander("🗑️ ¿Qué ELIMINAR?", expanded=False):
        st.caption("Contenido que debe eliminarse por obsoleto, irrelevante o perjudicial")
        
        remove_text = st.text_area(
            "Puntos a eliminar",
            key="rewrite_remove",
            height=100,
            placeholder="""Ej:
- Referencias a productos descatalogados
- Sección de "Ofertas Black Friday 2022" (obsoleta)
- Párrafos de relleno sin valor
- Enlaces rotos o a competidores
- Información incorrecta sobre specs""",
            help="Lista todo lo que debe eliminarse",
            label_visibility="collapsed"
        )
        
        if remove_text:
            instructions['remove'] = [
                line.strip().lstrip('-•*') 
                for line in remove_text.split('\n') 
                if line.strip()
            ]
    
    # =========================================================================
    # Qué AÑADIR
    # =========================================================================
    with st.expander("➕ ¿Qué AÑADIR?", expanded=False):
        st.caption("Contenido nuevo que debe incluirse")
        
        add_text = st.text_area(
            "Contenido a añadir",
            key="rewrite_add",
            height=100,
            placeholder="""Ej:
- Sección sobre modelos 2024/2025
- Comparativa con nuevos competidores (AMD vs Intel vs Apple)
- Benchmarks actualizados
- Sección de "Para quién es cada opción"
- Más productos de PcComponentes enlazados""",
            help="Lista todo el contenido nuevo a incluir",
            label_visibility="collapsed"
        )
        
        if add_text:
            instructions['add'] = [
                line.strip().lstrip('-•*') 
                for line in add_text.split('\n') 
                if line.strip()
            ]
    
    # =========================================================================
    # Cambios de TONO y ESTRUCTURA
    # =========================================================================
    col1, col2 = st.columns(2)
    
    with col1:
        with st.expander("🎭 Cambios de TONO", expanded=False):
            instructions['tone_changes'] = st.text_area(
                "Ajustes de tono",
                key="rewrite_tone",
                height=80,
                placeholder="""Ej:
- Más cercano y menos técnico
- Más directo al grano
- Añadir humor sutil
- Más orientado a venta""",
                help="Cómo debe cambiar el tono",
                label_visibility="collapsed"
            )
    
    with col2:
        with st.expander("📐 Cambios de ESTRUCTURA", expanded=False):
            instructions['structure_changes'] = st.text_area(
                "Ajustes de estructura",
                key="rewrite_structure",
                height=80,
                placeholder="""Ej:
- Introducción más corta (max 2 párrafos)
- Añadir tabla comparativa al inicio
- Mover FAQs al final
- Dividir secciones largas""",
                help="Cómo debe cambiar la estructura",
                label_visibility="collapsed"
            )
    
    # =========================================================================
    # Enfoque SEO
    # =========================================================================
    with st.expander("🔍 Enfoque SEO", expanded=False):
        instructions['seo_focus'] = st.text_area(
            "Instrucciones SEO específicas",
            key="rewrite_seo",
            height=80,
            placeholder="""Ej:
- Keyword principal en H1 y primer párrafo
- Añadir keywords secundarias: "mejor calidad precio", "comparativa 2024"
- Mejorar meta description
- Añadir schema FAQ
- Optimizar para featured snippet""",
            help="Instrucciones SEO específicas",
            label_visibility="collapsed"
        )
    
    # =========================================================================
    # Notas adicionales
    # =========================================================================
    instructions['additional_notes'] = st.text_area(
        "📝 Notas adicionales para la reescritura",
        key="rewrite_additional_notes",
        height=80,
        placeholder="Cualquier otra indicación importante para la reescritura...",
        help="Información adicional que deba tener en cuenta el generador"
    )
    
    # Mostrar resumen de instrucciones
    total_instructions = (
        len(instructions['improve']) + 
        len(instructions['maintain']) + 
        len(instructions['remove']) + 
        len(instructions['add'])
    )
    
    if total_instructions > 0:
        st.success(f"✅ {total_instructions} instrucciones configuradas")
    
    return instructions


# ============================================================================
# SECCIÓN: PRODUCTO PRINCIPAL
# ============================================================================

def render_main_product_section() -> Optional[Dict[str, Any]]:
    """
    Renderiza la sección de Producto Principal.
    
    Returns:
        Dict con datos del producto principal o None si no está habilitado
    """
    
    st.markdown("""
    Si el contenido se centra en un producto específico (review, análisis, etc.),
    puedes añadir sus datos aquí para enriquecer la generación.
    """)
    
    # Checkbox para habilitar
    is_enabled = st.checkbox(
        "Este contenido se centra en un producto específico",
        value=st.session_state.get('rewrite_main_product_enabled', False),
        key="rewrite_main_product_checkbox",
        help="Activa esta opción si el contenido es sobre un producto concreto"
    )
    
    st.session_state.rewrite_main_product_enabled = is_enabled
    
    if not is_enabled:
        st.caption("💡 Deja desactivado si el contenido es genérico (ej: 'mejores portátiles gaming')")
        st.session_state.rewrite_main_product_json = None
        return None
    
    # URL del producto
    col1, col2 = st.columns([3, 1])
    
    with col1:
        product_url = st.text_input(
            "🔗 URL del Producto Principal",
            key="rewrite_main_product_url",
            placeholder="https://www.pccomponentes.com/...",
            help="URL del producto en PcComponentes"
        )
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        st.caption("📦 Añade el JSON abajo")
    
    # Widget JSON con TABS
    st.markdown(f"""
    💡 **Obtén el JSON completo del producto** usando nuestro workflow de n8n:
    [🔗 Abrir Workflow de n8n]({N8N_PRODUCT_JSON_WORKFLOW})
    """)
    
    json_tab1, json_tab2 = st.tabs(["📁 Subir archivo", "📋 Pegar JSON"])
    
    json_content = None
    
    with json_tab1:
        uploaded_json = st.file_uploader(
            "Subir JSON del producto",
            type=['json'],
            key="rewrite_main_product_json_upload",
            help="JSON generado por el workflow de n8n"
        )
        
        if uploaded_json is not None:
            try:
                json_content = uploaded_json.read().decode('utf-8')
            except Exception as e:
                st.error(f"❌ Error al leer archivo: {str(e)}")
    
    with json_tab2:
        pasted_json = st.text_area(
            "Pegar JSON aquí",
            height=150,
            key="rewrite_main_product_json_paste",
            placeholder='{"id": "...", "name": "...", ...}',
            help="Pega el JSON directamente desde el workflow de n8n"
        )
        
        if pasted_json and pasted_json.strip():
            json_content = pasted_json.strip()
    
    product_json_data = None
    
    # Procesar JSON
    if json_content:
        try:
            if _product_json_available:
                is_valid, error_msg = validate_product_json(json_content)
                
                if is_valid:
                    product_data = parse_product_json(json_content)
                    
                    if product_data:
                        product_json_data = {
                            'product_id': product_data.product_id,
                            'legacy_id': product_data.legacy_id,
                            'title': product_data.title,
                            'description': product_data.description,
                            'brand_name': product_data.brand_name,
                            'family_name': product_data.family_name,
                            'attributes': product_data.attributes,
                            'images': product_data.images,
                            'totalComments': product_data.totalComments,
                            'advantages': product_data.advantages,
                            'disadvantages': product_data.disadvantages,
                            'comments': product_data.comments,
                        }
                        
                        st.session_state.rewrite_main_product_json = product_json_data
                        st.success(f"✅ JSON cargado: **{product_data.title}**")
                        
                        # Preview de datos
                        with st.expander("👁️ Preview de datos JSON", expanded=False):
                            summary = create_product_summary(product_data)
                            
                            col_a, col_b = st.columns(2)
                            with col_a:
                                st.markdown(f"**Producto:** {summary['title']}")
                                st.markdown(f"**Marca:** {summary['brand']}")
                                st.markdown(f"**Familia:** {summary['family']}")
                            with col_b:
                                st.markdown(f"**ID:** {summary['id']}")
                                st.markdown(f"**Reviews:** {summary['total_reviews']}")
                                st.markdown(f"**Imágenes:** {summary['image_count']}")
                    else:
                        st.error("❌ Error al parsear el JSON del producto")
                        st.session_state.rewrite_main_product_json = None
                else:
                    # Quitar prefijo "JSON inválido:" si ya viene en el mensaje
                    clean_error = error_msg.replace("JSON inválido: ", "").replace("JSON inválido:", "")
                    st.error(f"❌ JSON inválido: {clean_error}")
                    st.session_state.rewrite_main_product_json = None
            else:
                # Fallback sin validación
                parsed_json = json.loads(json_content)
                st.session_state.rewrite_main_product_json = parsed_json
                product_json_data = parsed_json
                st.success("✅ JSON cargado (sin validación detallada)")
                
        except json.JSONDecodeError as e:
            st.error(f"❌ Error JSON: {str(e)}")
            st.session_state.rewrite_main_product_json = None
        except Exception as e:
            st.error(f"❌ Error inesperado: {str(e)}")
            st.session_state.rewrite_main_product_json = None
    
    # Recuperar JSON si ya estaba cargado
    if st.session_state.get('rewrite_main_product_json') and not product_json_data:
        product_json_data = st.session_state.rewrite_main_product_json
        if product_json_data:
            title = product_json_data.get('title', 'Producto')
            st.caption(f"📦 JSON cargado previamente: {title[:50]}")
    
    # Retornar datos
    if product_url or product_json_data:
        return {
            'url': product_url.strip() if product_url else '',
            'json_data': product_json_data
        }
    
    return None


# ============================================================================
# SECCIÓN: PRODUCTOS ALTERNATIVOS (NUEVO v4.7.1)
# ============================================================================

def render_alternative_products_section() -> List[Dict[str, Any]]:
    """
    Renderiza la sección de productos alternativos.
    Cada producto tiene URL + JSON con tabs (subir/pegar).
    
    Returns:
        Lista de dicts con {url, anchor, product_data}
    """
    
    st.markdown("""
    Si quieres recomendar productos alternativos en el contenido, 
    añádelos aquí con sus datos para que los enlaces sean más contextuales.
    """)
    
    # Checkbox para habilitar
    is_enabled = st.checkbox(
        "Incluir productos alternativos",
        value=st.session_state.get('rewrite_alt_products_enabled', False),
        key="rewrite_alt_products_checkbox",
        help="Activa esta opción si quieres recomendar alternativas"
    )
    
    st.session_state.rewrite_alt_products_enabled = is_enabled
    
    if not is_enabled:
        st.caption("💡 Activa esta opción si quieres recomendar alternativas al producto principal o a los productos mencionados.")
        return []
    
    st.markdown(f"""
    💡 **Obtén el JSON de cada producto** usando el workflow de n8n:
    [🔗 Abrir Workflow de n8n]({N8N_PRODUCT_JSON_WORKFLOW})
    """)
    
    count_key = 'rewrite_alt_products_count'
    current_count = st.session_state.get(count_key, 1)
    
    alternative_products = []
    
    for i in range(current_count):
        with st.expander(f"🎯 Producto Alternativo {i+1}", expanded=(i == 0)):
            col1, col2 = st.columns([3, 2])
            
            with col1:
                url = st.text_input(
                    f"URL del producto {i+1}",
                    key=f"alt_prod_url_{i}",
                    placeholder="https://www.pccomponentes.com/producto",
                    help="URL del producto alternativo"
                )
            
            with col2:
                anchor = st.text_input(
                    f"Texto del enlace {i+1}",
                    key=f"alt_prod_anchor_{i}",
                    placeholder="Nombre del producto",
                    help="Texto que se usará para enlazar"
                )
            
            # Widget JSON con TABS
            st.markdown("**📦 JSON del producto**")
            
            json_tab1, json_tab2 = st.tabs(["📁 Subir JSON", "📋 Pegar JSON"])
            
            json_content = None
            json_key = f"alt_prod_json_{i}"
            
            with json_tab1:
                uploaded_json = st.file_uploader(
                    f"Subir JSON",
                    type=['json'],
                    key=f"alt_prod_json_upload_{i}",
                    help="JSON del producto"
                )
                
                if uploaded_json is not None:
                    try:
                        json_content = uploaded_json.read().decode('utf-8')
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
            
            with json_tab2:
                pasted_json = st.text_area(
                    "Pegar JSON",
                    height=100,
                    key=f"alt_prod_json_paste_{i}",
                    placeholder='{"id": "...", "name": "...", ...}'
                )
                
                if pasted_json and pasted_json.strip():
                    json_content = pasted_json.strip()
            
            product_json_data = _process_json_content(json_content, json_key)
            
            # Botón eliminar
            if current_count > 1:
                if st.button("🗑️ Eliminar producto", key=f"alt_prod_del_{i}"):
                    _delete_link_at_index(i, current_count, count_key, 'alt_prod')
            
            if url and url.strip():
                alternative_products.append({
                    'url': url.strip(),
                    'anchor': anchor.strip() if anchor else '',
                    'product_data': product_json_data
                })
    
    # Botón añadir
    if current_count < MAX_ALTERNATIVE_PRODUCTS:
        if st.button("➕ Añadir otro producto alternativo", key="alt_prod_add"):
            st.session_state[count_key] = current_count + 1
            st.rerun()
    
    if alternative_products:
        with_json = sum(1 for p in alternative_products if p.get('product_data'))
        st.success(f"✅ {len(alternative_products)} producto(s) alternativo(s) ({with_json} con JSON)")
    
    return alternative_products


# ============================================================================
# UTILIDADES HTML
# ============================================================================

def _strip_html_tags(html: str) -> str:
    """Elimina tags HTML y retorna texto plano."""
    text = re.sub(r'<[^>]+>', ' ', html)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def _show_html_stats(html_content: str) -> None:
    """Muestra estadísticas del contenido HTML."""
    text_content = _strip_html_tags(html_content)
    word_count = len(text_content.split())
    char_count = len(html_content)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📝 Palabras", f"{word_count:,}")
    with col2:
        st.metric("📊 Caracteres", f"{char_count:,}")
    with col3:
        h1_count = html_content.lower().count('<h1')
        h2_count = html_content.lower().count('<h2')
        st.metric("📑 Encabezados", f"{h1_count} H1, {h2_count} H2")
    
    if word_count < 100:
        st.warning("⚠️ El contenido parece muy corto. Asegúrate de haber pegado el artículo completo.")
    elif word_count > 50:
        st.success(f"✅ Contenido detectado: {word_count} palabras")


# ============================================================================
# SECCIÓN: ENLACES A POSTS/PLPs CON HTML CONTEXTUAL (ACTUALIZADO v4.7.1)
# ============================================================================

def render_posts_plps_links_section() -> List[Dict[str, Any]]:
    """
    Renderiza la sección de enlaces a posts/PLPs con HTML contextual.
    
    ACTUALIZADO v4.7.1:
    - Selector tipo: Post / PLP
    - Post: Un campo HTML único
    - PLP: Dos campos (Top text, Bottom text)
    - Eliminado JSON de productos (no necesario aquí)
    
    Returns:
        Lista de dicts con datos del enlace + HTML contextual
    """
    count_key = 'rewrite_posts_plps_count'
    current_count = st.session_state.get(count_key, 1)
    
    links = []
    
    for i in range(current_count):
        with st.expander(f"📝 Enlace Editorial {i+1}", expanded=(i == 0)):
            # Selector de tipo (NUEVO v4.7.1)
            editorial_type = st.radio(
                f"Tipo de contenido destino {i+1}",
                options=[EditorialType.POST, EditorialType.PLP],
                format_func=lambda x: EDITORIAL_TYPE_OPTIONS[x]["name"],
                horizontal=True,
                key=f"rewrite_editorial_type_{i}",
                help="Selecciona el tipo de contenido al que enlazas"
            )
            
            col1, col2 = st.columns([3, 2])
            
            with col1:
                url = st.text_input(
                    f"URL {i+1}",
                    key=f"rewrite_posts_url_{i}",
                    placeholder="https://www.pccomponentes.com/...",
                    help="URL del post, guía, categoría o PLP"
                )
            
            with col2:
                anchor = st.text_input(
                    f"Anchor text {i+1}",
                    key=f"rewrite_posts_anchor_{i}",
                    placeholder="Texto del enlace",
                    help="Texto visible del enlace"
                )
            
            # Campos HTML según tipo (NUEVO v4.7.1)
            html_content_data = {}
            
            if editorial_type == EditorialType.POST:
                # Un solo campo HTML para posts
                st.markdown("**📄 Contenido HTML del Post** (para contexto)")
                html_content = st.text_area(
                    "HTML del post",
                    height=150,
                    key=f"rewrite_posts_html_{i}",
                    placeholder=EDITORIAL_TYPE_OPTIONS[EditorialType.POST]["placeholder"],
                    help="Pega el HTML del post para que el enlace sea más contextual",
                    label_visibility="collapsed"
                )
                
                html_content_data['html_content'] = html_content
                html_content_data['editorial_type'] = EditorialType.POST
                
                if html_content and html_content.strip():
                    word_count = len(_strip_html_tags(html_content).split())
                    st.caption(f"📊 {word_count} palabras de contexto")
            
            else:  # PLP
                # Dos campos para PLPs
                st.markdown("**📄 Contenido de la PLP** (para contexto)")
                
                top_text = st.text_area(
                    "Top text (antes de productos)",
                    height=100,
                    key=f"rewrite_posts_top_{i}",
                    placeholder=EDITORIAL_TYPE_OPTIONS[EditorialType.PLP]["placeholder_top"],
                    help="Texto que aparece ANTES del listado de productos"
                )
                
                bottom_text = st.text_area(
                    "Bottom text (después de productos)",
                    height=100,
                    key=f"rewrite_posts_bottom_{i}",
                    placeholder=EDITORIAL_TYPE_OPTIONS[EditorialType.PLP]["placeholder_bottom"],
                    help="Texto que aparece DESPUÉS del listado de productos"
                )
                
                html_content_data['top_text'] = top_text
                html_content_data['bottom_text'] = bottom_text
                html_content_data['editorial_type'] = EditorialType.PLP
                
                # Estadísticas combinadas
                total_content = (top_text or '') + ' ' + (bottom_text or '')
                if total_content.strip():
                    word_count = len(_strip_html_tags(total_content).split())
                    st.caption(f"📊 {word_count} palabras de contexto (top + bottom)")
            
            # Botón eliminar
            if current_count > 1:
                if st.button("🗑️ Eliminar enlace", key=f"rewrite_posts_del_{i}"):
                    _delete_link_at_index(i, current_count, count_key, 'rewrite_posts')
            
            if url and url.strip():
                link_data = {
                    'url': url.strip(),
                    'anchor': anchor.strip() if anchor else '',
                    'type': 'editorial',
                    'editorial_type': html_content_data.get('editorial_type', EditorialType.POST),
                }
                
                # Añadir campos HTML según tipo
                if html_content_data.get('editorial_type') == EditorialType.POST:
                    link_data['html_content'] = html_content_data.get('html_content', '')
                else:
                    link_data['top_text'] = html_content_data.get('top_text', '')
                    link_data['bottom_text'] = html_content_data.get('bottom_text', '')
                
                links.append(link_data)
    
    # Botón añadir
    if current_count < MAX_EDITORIAL_LINKS:
        if st.button("➕ Añadir enlace a post/PLP", key="rewrite_posts_add"):
            st.session_state[count_key] = current_count + 1
            st.rerun()
    
    if links:
        posts = sum(1 for l in links if l.get('editorial_type') == EditorialType.POST)
        plps = sum(1 for l in links if l.get('editorial_type') == EditorialType.PLP)
        with_context = sum(1 for l in links if l.get('html_content') or l.get('top_text') or l.get('bottom_text'))
        st.caption(f"✅ {len(links)} enlace(s): {posts} posts, {plps} PLPs ({with_context} con contexto HTML)")
    
    return links


# ============================================================================
# SECCIÓN: ENLACES A PRODUCTOS CON JSON
# ============================================================================

def render_product_links_section() -> List[Dict[str, Any]]:
    """
    Renderiza la sección de enlaces a productos con JSON.
    
    Returns:
        Lista de dicts con {'url': str, 'anchor': str, 'product_data': dict|None}
    """
    count_key = 'rewrite_product_links_count'
    current_count = st.session_state.get(count_key, 1)
    
    links = []
    
    for i in range(current_count):
        with st.expander(f"🛒 Producto {i+1}", expanded=(i == 0)):
            col1, col2 = st.columns([3, 2])
            
            with col1:
                url = st.text_input(
                    f"URL del producto {i+1}",
                    key=f"rewrite_prod_url_{i}",
                    placeholder="https://www.pccomponentes.com/producto",
                    help="URL del PDP"
                )
            
            with col2:
                anchor = st.text_input(
                    f"Anchor text {i+1}",
                    key=f"rewrite_prod_anchor_{i}",
                    placeholder="Texto del enlace",
                    help="Texto visible"
                )
            
            # Widget JSON
            json_key = f"rewrite_prod_json_{i}"
            
            st.markdown(f"**📦 JSON del producto (opcional)**")
            
            json_tab1, json_tab2 = st.tabs(["📁 Subir archivo", "📋 Pegar JSON"])
            
            json_content = None
            
            with json_tab1:
                uploaded_json = st.file_uploader(
                    f"Subir JSON",
                    type=['json'],
                    key=f"rewrite_prod_json_upload_{i}",
                    help="JSON con datos del producto"
                )
                
                if uploaded_json is not None:
                    try:
                        json_content = uploaded_json.read().decode('utf-8')
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
            
            with json_tab2:
                pasted_json = st.text_area(
                    "Pegar JSON aquí",
                    height=120,
                    key=f"rewrite_prod_json_paste_{i}",
                    placeholder='{"id": "...", "name": "...", ...}'
                )
                
                if pasted_json and pasted_json.strip():
                    json_content = pasted_json.strip()
            
            product_json_data = _process_json_content(json_content, json_key)
            
            # Botón eliminar
            if current_count > 1:
                if st.button("🗑️ Eliminar producto", key=f"rewrite_prod_del_{i}"):
                    _delete_link_at_index(i, current_count, count_key, 'rewrite_prod')
            
            if url and url.strip():
                links.append({
                    'url': url.strip(),
                    'anchor': anchor.strip() if anchor else '',
                    'type': 'product',
                    'product_data': product_json_data
                })
    
    # Botón añadir
    if current_count < MAX_PRODUCT_LINKS:
        if st.button("➕ Añadir producto", key="rewrite_prod_add"):
            st.session_state[count_key] = current_count + 1
            st.rerun()
    
    if links:
        with_json = sum(1 for l in links if l.get('product_data'))
        st.caption(f"✅ {len(links)} producto(s) configurado(s) ({with_json} con JSON)")
    
    return links


def _process_json_content(json_content: Optional[str], json_key: str) -> Optional[Dict]:
    """Procesa contenido JSON y lo guarda en session state."""
    if not json_content:
        # Recuperar si ya estaba cargado
        if json_key in st.session_state:
            product_json_data = st.session_state[json_key]
            if product_json_data:
                title = product_json_data.get('title', 'Producto')
                st.caption(f"📦 JSON cargado: {title[:40]}")
            return product_json_data
        return None
    
    try:
        if _product_json_available:
            is_valid, error_msg = validate_product_json(json_content)
            
            if is_valid:
                product_data = parse_product_json(json_content)
                
                if product_data:
                    product_json_data = {
                        'product_id': product_data.product_id,
                        'legacy_id': product_data.legacy_id,
                        'title': product_data.title,
                        'description': product_data.description,
                        'brand_name': product_data.brand_name,
                        'family_name': product_data.family_name,
                        'attributes': product_data.attributes,
                        'images': product_data.images,
                        'totalComments': product_data.totalComments,
                        'advantages': product_data.advantages,
                        'disadvantages': product_data.disadvantages,
                        'comments': product_data.comments,
                    }
                    
                    st.session_state[json_key] = product_json_data
                    st.success(f"✅ JSON: {product_data.title[:50]}")
                    return product_json_data
                else:
                    st.error("❌ Error al parsear JSON")
            else:
                # Quitar prefijo duplicado si existe
                clean_error = error_msg.replace("JSON inválido: ", "").replace("JSON inválido:", "")
                st.error(f"❌ JSON inválido: {clean_error}")
        else:
            parsed_json = json.loads(json_content)
            st.session_state[json_key] = parsed_json
            st.success("✅ JSON cargado")
            return parsed_json
            
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
    
    return None


def _delete_link_at_index(idx: int, current_count: int, count_key: str, prefix: str) -> None:
    """
    Marca un enlace para eliminación.
    La eliminación real se procesa con _process_pending_deletions al inicio.
    """
    # Guardar la operación pendiente para procesarla en el siguiente rerun
    st.session_state[f"_pending_delete_{prefix}"] = {
        'idx': idx,
        'count': current_count,
        'count_key': count_key,
        'prefix': prefix
    }
    st.rerun()


def _process_pending_deletions() -> None:
    """
    Procesa eliminaciones pendientes al inicio del renderizado.
    Debe llamarse ANTES de renderizar los widgets de enlaces.
    """
    prefixes_to_check = ['rewrite_posts', 'rewrite_prod', 'alt_prod']
    
    for prefix in prefixes_to_check:
        pending_key = f"_pending_delete_{prefix}"
        
        if pending_key in st.session_state:
            pending = st.session_state[pending_key]
            del st.session_state[pending_key]
            
            idx = pending['idx']
            current_count = pending['count']
            count_key = pending['count_key']
            
            # Determinar campos según prefijo
            if prefix == 'rewrite_posts':
                fields = ['url', 'anchor', 'html', 'top', 'bottom']
            elif prefix == 'alt_prod':
                fields = ['url', 'anchor', 'json']
            else:
                fields = ['url', 'anchor', 'json']
            
            # Shift de valores hacia arriba
            for j in range(idx, current_count - 1):
                for field in fields:
                    next_key = f"{prefix}_{field}_{j+1}"
                    curr_key = f"{prefix}_{field}_{j}"
                    next_val = st.session_state.get(next_key, "")
                    st.session_state[curr_key] = next_val
            
            # Limpiar última posición
            last_idx = current_count - 1
            for field in fields:
                key_to_delete = f"{prefix}_{field}_{last_idx}"
                if key_to_delete in st.session_state:
                    del st.session_state[key_to_delete]
            
            # También limpiar keys relacionadas con editorial_type y uploads
            extra_keys = [
                f"rewrite_editorial_type_{last_idx}",
                f"{prefix}_json_upload_{last_idx}",
                f"{prefix}_json_paste_{last_idx}",
                f"alt_prod_json_upload_{last_idx}",
                f"alt_prod_json_paste_{last_idx}",
            ]
            for key in extra_keys:
                if key in st.session_state:
                    del st.session_state[key]
            
            # Decrementar contador
            st.session_state[count_key] = max(1, current_count - 1)


# ============================================================================
# INPUT DE KEYWORD Y BÚSQUEDA
# ============================================================================

def render_keyword_input() -> Tuple[str, bool]:
    """Renderiza el input de keyword principal y botón de búsqueda."""
    
    st.markdown("Introduce la **keyword principal** para la que quieres rankear.")
    
    semrush_available = SEMRUSH_MODULE_AVAILABLE and is_semrush_available()
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        current_keyword = st.text_input(
            "Keyword principal *",
            placeholder="Ej: mejor portátil gaming 2025",
            help="Keyword específica para la que quieres crear/mejorar contenido",
            key="rewrite_keyword_input"
        )
    
    with col2:
        if semrush_available:
            search_disabled = not current_keyword or len(current_keyword.strip()) < 3
            search_button = st.button(
                "🔍 Buscar Competidores",
                disabled=search_disabled,
                use_container_width=True,
                type="primary",
                key="btn_search_competitors"
            )
        else:
            search_button = False
            st.caption("💡 Introduce URLs manualmente abajo")
    
    # Detectar si cambió la keyword
    if 'last_rewrite_keyword' in st.session_state:
        if st.session_state.last_rewrite_keyword != current_keyword:
            st.session_state.rewrite_competitors_data = None
            st.session_state.rewrite_analysis = None
            st.session_state.rewrite_gsc_analysis = None
            st.session_state.semrush_response = None
    
    st.session_state.last_rewrite_keyword = current_keyword
    
    return current_keyword, search_button


# ============================================================================
# OBTENCIÓN DE COMPETIDORES
# ============================================================================

def _fetch_competitors_semrush(keyword: str, gsc_analysis: Optional[Dict]) -> None:
    """Obtiene competidores usando SEMrush API."""
    
    if gsc_analysis and gsc_analysis.get('has_matches'):
        st.info("💡 Procederemos a analizar competidores. Recuerda que ya tienes contenido rankeando.")
    
    with st.spinner("🔍 Consultando SEMrush y analizando competidores..."):
        try:
            client = SEMrushClient(api_key=SEMRUSH_API_KEY, database='es')
            
            response = client.get_organic_competitors(
                keyword=keyword,
                num_results=5,
                scrape_content=True,
                exclude_domains=['pccomponentes.com', 'pccomponentes.pt']
            )
            
            st.session_state.semrush_response = response
            
            if response.success and response.competitors:
                competitors_data = format_competitors_for_display(response.competitors)
                st.session_state.rewrite_competitors_data = competitors_data
                
                scraped_ok = sum(1 for c in competitors_data if c.get('scrape_success', False))
                
                st.success(f"✅ **SEMrush**: {len(competitors_data)} competidores encontrados ({scraped_ok} scrapeados)")
            else:
                st.error(f"❌ **Error de SEMrush**: {response.error_message}")
                st.session_state['show_manual_fallback'] = True
        
        except Exception as e:
            st.error(f"❌ **Error inesperado**: {str(e)}")
            st.session_state['show_manual_fallback'] = True
        
        st.rerun()


def render_manual_competitors_input(keyword: str) -> None:
    """Renderiza el input manual para URLs de competidores."""
    
    st.markdown("**Introduce las URLs de los competidores** que quieres analizar.")
    
    urls_input = st.text_area(
        "URLs de competidores (una por línea) *",
        value=st.session_state.get('manual_urls_input', ''),
        placeholder="""https://competitor1.com/article
https://competitor2.com/guide
https://competitor3.com/review""",
        height=150,
        help="Introduce las URLs de los competidores que rankean para tu keyword"
    )
    
    st.session_state.manual_urls_input = urls_input
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        analyze_btn = st.button(
            "🔍 Analizar URLs",
            disabled=not urls_input.strip(),
            type="primary",
            key="btn_analyze_urls"
        )
    
    with col2:
        if urls_input:
            urls = [u.strip() for u in urls_input.split('\n') if u.strip() and u.startswith('http')]
            st.caption(f"📋 {len(urls)} URLs detectadas")
    
    if analyze_btn and urls_input:
        _scrape_manual_urls(urls_input, keyword)


def _scrape_manual_urls(urls_input: str, keyword: str) -> None:
    """Scrapea las URLs introducidas manualmente."""
    
    urls = [u.strip() for u in urls_input.split('\n') if u.strip() and u.startswith('http')]
    
    if not urls:
        st.error("❌ No se encontraron URLs válidas")
        return
    
    if len(urls) > 10:
        st.warning("⚠️ Máximo 10 URLs. Solo se procesarán las primeras 10.")
        urls = urls[:10]
    
    with st.spinner(f"🔍 Analizando {len(urls)} URLs..."):
        competitors_data = []
        
        for i, url in enumerate(urls, 1):
            try:
                content_data = _scrape_single_url(url, i)
                competitors_data.append(content_data)
            except Exception as e:
                competitors_data.append({
                    'url': url,
                    'title': 'Error al scrapear',
                    'domain': _extract_domain(url),
                    'position': i,
                    'ranking_position': i,
                    'content': '',
                    'word_count': 0,
                    'scrape_success': False,
                    'error': str(e)[:100]
                })
        
        st.session_state.rewrite_competitors_data = competitors_data
        
        success_count = sum(1 for c in competitors_data if c.get('scrape_success', False))
        
        if success_count > 0:
            st.success(f"✅ Contenido analizado: {success_count}/{len(competitors_data)} URLs")
        else:
            st.error("❌ No se pudo scrapear ninguna URL")
        
        st.rerun()


def _scrape_single_url(url: str, position: int) -> Dict:
    """Scrapea una URL individual."""
    import requests
    from bs4 import BeautifulSoup
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml',
        'Accept-Language': 'es-ES,es;q=0.9',
    }
    
    response = requests.get(url, headers=headers, timeout=15)
    
    if response.status_code != 200:
        raise Exception(f"HTTP {response.status_code}")
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    title_tag = soup.find('title')
    title = title_tag.get_text(strip=True) if title_tag else ''
    
    meta_desc = soup.find('meta', attrs={'name': 'description'})
    description = meta_desc.get('content', '') if meta_desc else ''
    
    for element in soup(['script', 'style', 'nav', 'footer', 'header', 'aside']):
        element.decompose()
    
    main = soup.find('main') or soup.find('article') or soup.find('body')
    content = main.get_text(' ', strip=True) if main else ''
    content = re.sub(r'\s+', ' ', content).strip()
    
    if len(content) > 8000:
        content = content[:8000] + "..."
    
    return {
        'url': url,
        'title': title[:200] if title else 'Sin título',
        'domain': _extract_domain(url),
        'position': position,
        'ranking_position': position,
        'content': content,
        'word_count': len(content.split()),
        'meta_description': description[:300] if description else '',
        'scrape_success': True,
        'error': None
    }


def _extract_domain(url: str) -> str:
    """Extrae el dominio de una URL."""
    try:
        from urllib.parse import urlparse
        parsed = urlparse(url)
        return parsed.netloc.replace('www.', '')
    except Exception:
        return url


# ============================================================================
# RESUMEN DE COMPETIDORES
# ============================================================================

def render_competitors_summary(competitors_data: List[Dict]) -> None:
    """Renderiza un resumen de los competidores analizados."""
    
    st.markdown("#### 📊 Competidores Analizados")
    
    col1, col2, col3 = st.columns(3)
    
    scraped_ok = [c for c in competitors_data if c.get('scrape_success', False)]
    
    with col1:
        st.metric("📊 Total URLs", len(competitors_data))
    
    with col2:
        if scraped_ok:
            avg_words = sum(c.get('word_count', 0) for c in scraped_ok) / len(scraped_ok)
            st.metric("📝 Promedio palabras", f"{int(avg_words):,}")
        else:
            st.metric("📝 Promedio palabras", "N/A")
    
    with col3:
        st.metric("✅ Scrapeados", f"{len(scraped_ok)}/{len(competitors_data)}")
    
    for i, comp in enumerate(competitors_data, 1):
        position = comp.get('ranking_position', comp.get('position', i))
        title = comp.get('title', 'Sin título')[:60]
        
        if comp.get('scrape_success', False):
            icon = "✅"
            status = f"{comp.get('word_count', 0):,} palabras"
        else:
            icon = "❌"
            status = comp.get('error', 'Error')[:30]
        
        with st.expander(f"{icon} #{position} - {title}", expanded=False):
            st.markdown(f"**URL:** [{comp.get('url', 'N/A')}]({comp.get('url', '#')})")
            st.markdown(f"**Dominio:** {comp.get('domain', 'N/A')}")
            
            if comp.get('content') and comp.get('scrape_success'):
                content_preview = comp['content'][:400] + "..."
                st.text_area("Preview", content_preview, height=100, disabled=True, key=f"preview_comp_{i}")


# ============================================================================
# CONFIGURACIÓN DE REESCRITURA
# ============================================================================

def render_rewrite_configuration(keyword: str, rewrite_mode: str) -> Dict:
    """Renderiza los controles de configuración."""
    
    config = {}
    
    # Objetivo del contenido
    st.markdown("#### 📝 Información Básica")
    
    # Objetivo adaptado al modo
    if rewrite_mode == RewriteMode.MERGE:
        placeholder = "Ej: Crear UN contenido definitivo que consolide los mejores elementos de los artículos fusionados"
    elif rewrite_mode == RewriteMode.DISAMBIGUATE:
        placeholder = "Ej: Crear contenido claramente diferenciado para la intención de búsqueda específica"
    else:
        placeholder = "Ej: Mejorar el posicionamiento y actualizar la información del artículo existente"
    
    config['objetivo'] = st.text_area(
        "Objetivo del contenido *",
        placeholder=placeholder,
        help="¿Qué quieres lograr con este contenido?",
        height=100
    )
    
    # Arquetipo
    st.markdown("#### 📚 Arquetipo de Contenido")
    
    use_arquetipo = st.checkbox(
        "Usar arquetipo como guía estructural",
        value=True,
        help="El arquetipo define estructura y tono del contenido"
    )
    
    if use_arquetipo and _arquetipos_available:
        arquetipo_names = get_arquetipo_names()
        arquetipo_codes = sorted(arquetipo_names.keys())
        
        selected_arquetipo = st.selectbox(
            "Seleccionar arquetipo",
            options=arquetipo_codes,
            format_func=lambda x: f"{x}: {arquetipo_names.get(x, x)}",
            index=0,
            key="rewrite_arquetipo_selector"
        )
        
        config['arquetipo_codigo'] = selected_arquetipo
        
        arq_data = get_arquetipo(selected_arquetipo)
        if arq_data:
            description = arq_data.get('description', '')
            tone = arq_data.get('tone', '')
            
            if description:
                st.caption(f"ℹ️ **{description}**")
            if tone:
                st.caption(f"🎭 Tono: {tone}")
        
        min_len, max_len = get_length_range(selected_arquetipo)
        default_len = get_default_length(selected_arquetipo)
    else:
        config['arquetipo_codigo'] = None
        min_len, max_len = 800, 3000
        default_len = 1600
    
    # Longitud
    st.markdown("#### 📏 Longitud del Contenido")
    
    col1, col2 = st.columns(2)
    
    with col1:
        config['target_length'] = st.number_input(
            "Longitud objetivo (palabras) *",
            min_value=min_len,
            max_value=max_len,
            value=default_len,
            step=100
        )
    
    with col2:
        if st.session_state.rewrite_competitors_data:
            scraped = [c for c in st.session_state.rewrite_competitors_data if c.get('scrape_success')]
            if scraped:
                avg = int(sum(c.get('word_count', 0) for c in scraped) / len(scraped))
                suggested = int(avg * 1.2)
                st.info(f"💡 Sugerencia: ~{suggested:,} palabras (20% más que promedio: {avg:,})")
    
    # Keywords
    st.markdown("#### 🔑 Keywords SEO Adicionales")
    
    keywords_input = st.text_area(
        "Keywords secundarias (una por línea)",
        placeholder=f"{keyword}\nkeyword relacionada 1\nkeyword relacionada 2",
        height=100
    )
    
    config['keywords'] = [keyword] + [
        k.strip() for k in keywords_input.split('\n') 
        if k.strip() and k.strip() != keyword
    ]
    
    # Contexto
    st.markdown("#### 📋 Contexto Adicional")
    
    config['context'] = st.text_area(
        "Contexto o información adicional (opcional)",
        placeholder="Información específica, datos internos, perspectiva única de PcComponentes...",
        height=100
    )
    
    # Producto alternativo
    st.markdown("#### 🎯 Producto Alternativo (opcional)")
    
    col_alt1, col_alt2 = st.columns(2)
    
    with col_alt1:
        config['producto_alternativo_url'] = st.text_input(
            "URL del producto alternativo",
            placeholder="https://www.pccomponentes.com/producto"
        )
    
    with col_alt2:
        config['producto_alternativo_text'] = st.text_input(
            "Texto del producto",
            placeholder="Nombre del producto"
        )
    
    return config


# ============================================================================
# VALIDACIÓN DE INPUTS
# ============================================================================

def validate_rewrite_inputs(
    keyword: str,
    competitors_data: Optional[List[Dict]],
    config: Dict,
    gsc_analysis: Optional[Dict],
    html_contents: List[Dict],
    rewrite_mode: str
) -> bool:
    """Valida que todos los inputs necesarios estén completos."""
    
    missing = []
    
    if not keyword or len(keyword.strip()) < 3:
        missing.append("Keyword principal")
    
    # Validar según modo
    if rewrite_mode == RewriteMode.MERGE:
        if len(html_contents) < 2:
            missing.append("Al menos 2 artículos para fusionar")
    elif rewrite_mode == RewriteMode.DISAMBIGUATE:
        if len(html_contents) < 1:
            missing.append("Contenido conflictivo para desambiguar")
    else:
        # Modo single: necesita competidores O HTML
        has_competitors = competitors_data and len(competitors_data) > 0
        has_html = len(html_contents) > 0
        
        if not has_competitors and not has_html:
            missing.append("Análisis de competidores O contenido HTML a reescribir")
    
    if not config.get('objetivo') or len(config['objetivo'].strip()) < 10:
        missing.append("Objetivo del contenido")
    
    if not config.get('target_length') or config['target_length'] < 800:
        missing.append("Longitud objetivo válida (mínimo 800 palabras)")
    
    if missing:
        error_html = "<div style='background-color:#fff3cd;border:1px solid #ffc107;border-radius:5px;padding:10px;margin:10px 0;'>"
        error_html += "<span style='color:#856404;font-weight:bold;'>⚠️ Campos pendientes:</span>"
        error_html += "<ul style='margin:5px 0;padding-left:20px;color:#856404;'>"
        for m in missing:
            error_html += f"<li>{m}</li>"
        error_html += "</ul></div>"
        st.markdown(error_html, unsafe_allow_html=True)
        return False
    
    return True


# ============================================================================
# RESUMEN ANTES DE GENERAR (ACTUALIZADO v4.7.1)
# ============================================================================

def render_generation_summary(
    keyword: str, 
    config: Dict, 
    gsc_analysis: Optional[Dict],
    html_contents: List[Dict],
    main_product_data: Optional[Dict],
    rewrite_mode: str,
    rewrite_instructions: Dict,
    alternative_products: List[Dict] = None,
    posts_plps_links: List[Dict] = None
) -> None:
    """Muestra un resumen de la configuración antes de generar."""
    
    st.markdown("### 📋 Resumen de Generación")
    
    # Modo de reescritura
    mode_info = REWRITE_MODE_OPTIONS.get(rewrite_mode, {})
    st.markdown(f"**Modo:** {mode_info.get('name', rewrite_mode)}")
    
    with st.container():
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Configuración básica:**")
            st.markdown(f"- 🎯 Keyword: `{keyword}`")
            st.markdown(f"- 📝 Longitud: `{config['target_length']:,}` palabras")
            
            if config.get('arquetipo_codigo'):
                arq_names = get_arquetipo_names()
                arq_name = arq_names.get(config['arquetipo_codigo'], config['arquetipo_codigo'])
                st.markdown(f"- 📚 Arquetipo: `{arq_name}`")
            
            if html_contents:
                total_words = sum(a.get('word_count', 0) for a in html_contents)
                st.markdown(f"- 📄 Artículos: `{len(html_contents)}` ({total_words:,} palabras)")
            
            if main_product_data and main_product_data.get('json_data'):
                title = main_product_data['json_data'].get('title', 'Producto')
                st.markdown(f"- 📦 Producto principal: `{title[:30]}...`")
            
            # Productos alternativos (NUEVO v4.7.1)
            if alternative_products:
                with_json = sum(1 for p in alternative_products if p.get('product_data'))
                st.markdown(f"- 🎯 Productos alternativos: `{len(alternative_products)}` ({with_json} con JSON)")
        
        with col2:
            st.markdown("**Instrucciones de reescritura:**")
            
            total = (
                len(rewrite_instructions.get('improve', [])) +
                len(rewrite_instructions.get('maintain', [])) +
                len(rewrite_instructions.get('remove', [])) +
                len(rewrite_instructions.get('add', []))
            )
            
            st.markdown(f"- ✨ Mejorar: `{len(rewrite_instructions.get('improve', []))}` puntos")
            st.markdown(f"- ✅ Mantener: `{len(rewrite_instructions.get('maintain', []))}` puntos")
            st.markdown(f"- 🗑️ Eliminar: `{len(rewrite_instructions.get('remove', []))}` puntos")
            st.markdown(f"- ➕ Añadir: `{len(rewrite_instructions.get('add', []))}` puntos")
            
            if st.session_state.rewrite_competitors_data:
                scraped = [c for c in st.session_state.rewrite_competitors_data if c.get('scrape_success')]
                st.markdown(f"- 🏆 Competidores: `{len(scraped)}`")
            
            # Enlaces editoriales (NUEVO v4.7.1)
            if posts_plps_links:
                with_context = sum(1 for l in posts_plps_links if l.get('html_content') or l.get('top_text'))
                st.markdown(f"- 📝 Enlaces editoriales: `{len(posts_plps_links)}` ({with_context} con contexto)")
    
    st.info("""
    ✅ Todo listo para generar. El proceso incluirá:
    1. Análisis del contenido existente
    2. Aplicación de instrucciones de reescritura
    3. Generación del borrador mejorado
    4. Análisis crítico y versión final
    """)


# ============================================================================
# PREPARACIÓN DE CONFIGURACIÓN FINAL (ACTUALIZADO v4.7.1)
# ============================================================================

def prepare_rewrite_config(
    keyword: str,
    competitors_data: List[Dict],
    rewrite_config: Dict,
    gsc_analysis: Optional[Dict],
    html_contents: List[Dict],
    rewrite_mode: str,
    rewrite_instructions: Dict,
    disambiguation_config: Optional[Dict],
    main_product_data: Optional[Dict],
    posts_plps_links: List[Dict],
    product_links: List[Dict],
    alternative_products: List[Dict] = None
) -> Dict:
    """Prepara la configuración completa para el proceso de generación."""
    
    # Configuración base
    config = {
        'mode': 'rewrite',
        'rewrite_mode': rewrite_mode,  # single/merge/disambiguate
        'keyword': keyword,
        'target_length': rewrite_config['target_length'],
        'objetivo': rewrite_config['objetivo'],
        'keywords': rewrite_config.get('keywords', [keyword]),
        'context': rewrite_config.get('context', ''),
        'arquetipo_codigo': rewrite_config.get('arquetipo_codigo'),
    }
    
    # =========================================================================
    # INSTRUCCIONES DE REESCRITURA (para los prompts)
    # =========================================================================
    config['rewrite_instructions'] = {
        'improve': rewrite_instructions.get('improve', []),
        'maintain': rewrite_instructions.get('maintain', []),
        'remove': rewrite_instructions.get('remove', []),
        'add': rewrite_instructions.get('add', []),
        'tone_changes': rewrite_instructions.get('tone_changes', ''),
        'structure_changes': rewrite_instructions.get('structure_changes', ''),
        'seo_focus': rewrite_instructions.get('seo_focus', ''),
        'additional_notes': rewrite_instructions.get('additional_notes', ''),
    }
    
    # =========================================================================
    # CONTENIDO HTML (puede ser uno o múltiples)
    # =========================================================================
    config['html_contents'] = html_contents
    
    # Compatibilidad con código antiguo que espera html_to_rewrite
    if html_contents:
        config['html_to_rewrite'] = html_contents[0].get('html', '')
    else:
        config['html_to_rewrite'] = None
    
    # =========================================================================
    # CONFIGURACIÓN DE DESAMBIGUACIÓN (si aplica)
    # =========================================================================
    if rewrite_mode == RewriteMode.DISAMBIGUATE and disambiguation_config:
        config['disambiguation'] = {
            'output_type': disambiguation_config.get('output_type', 'post'),
            'instructions': disambiguation_config.get('instructions', ''),
            'other_url': disambiguation_config.get('other_url', ''),
            'conflict_url': disambiguation_config.get('conflict_url', ''),
        }
    else:
        config['disambiguation'] = None
    
    # =========================================================================
    # PRODUCTO PRINCIPAL
    # =========================================================================
    if main_product_data:
        config['main_product'] = {
            'url': main_product_data.get('url', ''),
            'json_data': main_product_data.get('json_data')
        }
        config['pdp_data'] = main_product_data.get('json_data')
        config['pdp_json_data'] = main_product_data.get('json_data')
    else:
        config['main_product'] = None
        config['pdp_data'] = None
        config['pdp_json_data'] = None
    
    # =========================================================================
    # PRODUCTOS ALTERNATIVOS (NUEVO v4.7.1)
    # =========================================================================
    config['alternative_products'] = alternative_products or []
    
    # =========================================================================
    # ENLACES EDITORIALES (ACTUALIZADO v4.7.1)
    # =========================================================================
    config['editorial_links'] = []
    
    if posts_plps_links:
        for link in posts_plps_links:
            link_dict = {
                'url': link.get('url', ''),
                'anchor': link.get('anchor', ''),
                'text': link.get('anchor', ''),
                'type': 'editorial',
                'editorial_type': link.get('editorial_type', EditorialType.POST),
            }
            
            # Añadir campos HTML según tipo
            if link.get('editorial_type') == EditorialType.PLP:
                link_dict['top_text'] = link.get('top_text', '')
                link_dict['bottom_text'] = link.get('bottom_text', '')
            else:
                link_dict['html_content'] = link.get('html_content', '')
            
            config['editorial_links'].append(link_dict)
    
    # =========================================================================
    # ENLACES A PRODUCTOS
    # =========================================================================
    config['product_links'] = []
    
    if product_links:
        for link in product_links:
            link_dict = {
                'url': link.get('url', ''),
                'anchor': link.get('anchor', ''),
                'text': link.get('anchor', ''),
                'type': 'product'
            }
            if link.get('product_data'):
                link_dict['product_data'] = link['product_data']
            config['product_links'].append(link_dict)
    
    # =========================================================================
    # ENLACES UNIFICADOS (compatibilidad)
    # =========================================================================
    all_links = config['editorial_links'] + config['product_links']
    config['links'] = all_links
    config['enlaces'] = all_links  # Alias
    
    # Producto alternativo (campo simple de configuración)
    config['producto_alternativo'] = {
        'url': rewrite_config.get('producto_alternativo_url', ''),
        'text': rewrite_config.get('producto_alternativo_text', '')
    }
    
    # Datos de competidores
    if competitors_data:
        config['competitors_data'] = [
            c for c in competitors_data if c.get('scrape_success', False)
        ]
    else:
        config['competitors_data'] = []
    
    # Análisis de GSC
    config['gsc_analysis'] = gsc_analysis
    
    # Campos específicos de arquetipo
    config['campos_arquetipo'] = {}
    
    # Metadata
    config['timestamp'] = datetime.now().isoformat()
    config['data_source'] = 'semrush' if SEMRUSH_ENABLED else 'manual'
    
    return config


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    '__version__',
    'RewriteMode',
    'REWRITE_MODE_OPTIONS',
    'EditorialType',
    'EDITORIAL_TYPE_OPTIONS',
    'render_rewrite_section',
    'render_keyword_input',
    'render_html_content_section',
    'render_rewrite_instructions_section',
    'render_main_product_section',
    'render_alternative_products_section',
    'render_posts_plps_links_section',
    'render_product_links_section',
    'render_manual_competitors_input',
    'render_competitors_summary',
    'render_rewrite_configuration',
    'validate_rewrite_inputs',
    'render_generation_summary',
    'prepare_rewrite_config',
    'MAX_COMPETITORS',
    'MAX_ALTERNATIVE_PRODUCTS',
    'MAX_EDITORIAL_LINKS',
    'MAX_PRODUCT_LINKS',
    'DEFAULT_REWRITE_LENGTH',
    'COMPETITION_BEAT_FACTOR',
    'MAX_ARTICLES_TO_MERGE',
]
