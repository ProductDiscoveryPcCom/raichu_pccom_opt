"""
PcComponentes Content Generator - App Principal
Versión 4.5.0 CORREGIDA

Aplicación Streamlit para generación de contenido SEO.
Flujo de 3 etapas: Borrador → Análisis → Final

CORRECCIONES v4.5.0:
- Nombres de funciones correctos (build_new_content_prompt_stage1, etc.)
- Parámetros correctos (secondary_keywords, guiding_context, links_data)
- GenerationResult.content en lugar de asignar GenerationResult a str
- Análisis competitivo inline (build_competitor_analysis_prompt no existe)

Autor: PcComponentes - Product Discovery & Content
"""

import streamlit as st
import time
import logging
import traceback
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime

# ============================================================================
# CONFIGURACIÓN DE LOGGING
# ============================================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================================================
# VERSIÓN
# ============================================================================

__version__ = "4.5.0"
APP_TITLE = "PcComponentes Content Generator"

# ============================================================================
# IMPORTS CON MANEJO DE ERRORES
# ============================================================================

# Configuración - Primero st.secrets (Streamlit Cloud), luego config.settings, luego env vars
def _load_config():
    """Carga la configuración desde múltiples fuentes."""
    config = {
        'api_key': '',
        'model': 'claude-sonnet-4-20250514',
        'max_tokens': 8000,
        'temperature': 0.7,
        'debug_mode': False,
    }
    
    # 1. Intentar cargar desde st.secrets (Streamlit Cloud)
    try:
        # Nombres según tu archivo secrets.toml
        # Usamos acceso directo con fallback para compatibilidad
        if 'claude_key' in st.secrets:
            config['api_key'] = st.secrets['claude_key']
        if 'claude_model' in st.secrets:
            config['model'] = st.secrets['claude_model']
        if 'max_tokens' in st.secrets:
            config['max_tokens'] = st.secrets['max_tokens']
        if 'temperature' in st.secrets:
            config['temperature'] = st.secrets['temperature']
        
        # Debug mode está en [settings]
        if 'settings' in st.secrets and 'debug_mode' in st.secrets.settings:
            config['debug_mode'] = st.secrets.settings['debug_mode']
        
        if config['api_key']:
            logger.info("Configuración cargada desde st.secrets")
            return config
    except Exception as e:
        logger.debug(f"No se pudo cargar de st.secrets: {e}")
    
    # 2. Intentar cargar desde config.settings
    try:
        from config.settings import (
            CLAUDE_API_KEY,
            CLAUDE_MODEL,
            MAX_TOKENS,
            TEMPERATURE,
            DEBUG_MODE,
        )
        config['api_key'] = CLAUDE_API_KEY
        config['model'] = CLAUDE_MODEL
        config['max_tokens'] = MAX_TOKENS
        config['temperature'] = TEMPERATURE
        config['debug_mode'] = DEBUG_MODE
        
        if config['api_key']:
            logger.info("Configuración cargada desde config.settings")
            return config
    except ImportError:
        logger.debug("config.settings no disponible")
    
    # 3. Fallback a variables de entorno
    import os
    config['api_key'] = os.getenv('CLAUDE_API_KEY', os.getenv('ANTHROPIC_API_KEY', ''))
    config['model'] = os.getenv('CLAUDE_MODEL', config['model'])
    config['max_tokens'] = int(os.getenv('MAX_TOKENS', config['max_tokens']))
    config['temperature'] = float(os.getenv('TEMPERATURE', config['temperature']))
    config['debug_mode'] = os.getenv('DEBUG_MODE', 'false').lower() == 'true'
    
    if config['api_key']:
        logger.info("Configuración cargada desde variables de entorno")
    else:
        logger.warning("No se encontró API key en ninguna fuente")
    
    return config

# Cargar configuración
_config = _load_config()
CLAUDE_API_KEY = _config['api_key']
CLAUDE_MODEL = _config['model']
MAX_TOKENS = _config['max_tokens']
TEMPERATURE = _config['temperature']
DEBUG_MODE = _config['debug_mode']

# Arquetipos
try:
    from config.archetipos import get_arquetipo, ARQUETIPOS
except ImportError:
    logger.warning("No se pudo importar arquetipos")
    ARQUETIPOS = {}
    def get_arquetipo(code):
        return {'code': code, 'name': 'Default', 'tone': 'informativo'}

# Generador de contenido
try:
    from core.generator import ContentGenerator, GenerationResult
    _generator_available = True
except ImportError as e:
    logger.error(f"No se pudo importar ContentGenerator: {e}")
    ContentGenerator = None
    GenerationResult = None
    _generator_available = False

# Prompts - new_content
try:
    from prompts import new_content
    _new_content_available = True
except ImportError as e:
    logger.error(f"No se pudo importar prompts.new_content: {e}")
    new_content = None
    _new_content_available = False

# Prompts - rewrite
try:
    from prompts import rewrite
    _rewrite_available = True
except ImportError as e:
    logger.error(f"No se pudo importar prompts.rewrite: {e}")
    rewrite = None
    _rewrite_available = False

# UI Components
try:
    from ui.inputs import render_content_inputs
    _inputs_available = True
except ImportError:
    logger.warning("No se pudo importar ui.inputs")
    _inputs_available = False
    render_content_inputs = None

try:
    from ui.rewrite import render_rewrite_section
    _rewrite_ui_available = True
except ImportError:
    logger.warning("No se pudo importar ui.rewrite")
    _rewrite_ui_available = False
    render_rewrite_section = None

try:
    from ui.results import render_results_section
    _results_available = True
except ImportError:
    logger.warning("No se pudo importar ui.results")
    _results_available = False
    render_results_section = None

try:
    from ui.sidebar import render_sidebar
    _sidebar_available = True
except ImportError:
    logger.warning("No se pudo importar ui.sidebar")
    _sidebar_available = False
    render_sidebar = None

# Utilidades HTML
try:
    from utils.html_utils import count_words_in_html, extract_html_content
except ImportError:
    def count_words_in_html(html: str) -> int:
        import re
        text = re.sub(r'<[^>]+>', ' ', html)
        return len(text.split())
    
    def extract_html_content(content: str) -> str:
        return content


# ============================================================================
# INICIALIZACIÓN
# ============================================================================

def initialize_app() -> None:
    """Inicializa el estado de la aplicación."""
    
    if 'initialized' not in st.session_state:
        st.session_state.initialized = True
        st.session_state.mode = 'new'
        st.session_state.generation_in_progress = False
        st.session_state.current_stage = 0
        st.session_state.draft_html = None
        st.session_state.analysis_json = None
        st.session_state.final_html = None
        st.session_state.rewrite_analysis = None
        st.session_state.content_history = []
        st.session_state.last_config = None
        st.session_state.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        logger.info("Aplicación inicializada")


def check_configuration() -> Tuple[bool, List[str]]:
    """
    Verifica que la configuración sea válida.
    
    Returns:
        Tuple (is_valid, list_of_errors)
    """
    errors = []
    
    if not CLAUDE_API_KEY:
        errors.append(
            "API Key no configurada. Verifica que en tu secrets.toml tengas: "
            "claude_key = \"sk-ant-...\""
        )
    elif not CLAUDE_API_KEY.startswith('sk-ant-'):
        errors.append(
            f"API Key tiene formato inválido (debe empezar con 'sk-ant-'). "
            f"Valor actual empieza con: '{CLAUDE_API_KEY[:10]}...'"
        )
    
    if not _generator_available:
        errors.append("ContentGenerator no está disponible - verifica core/generator.py")
    
    if not _new_content_available:
        errors.append("Módulo prompts.new_content no está disponible")
    
    # Log para debug
    if errors:
        logger.error(f"Errores de configuración: {errors}")
        logger.debug(f"CLAUDE_API_KEY presente: {bool(CLAUDE_API_KEY)}")
        logger.debug(f"CLAUDE_MODEL: {CLAUDE_MODEL}")
    else:
        logger.info("Configuración verificada correctamente")
    
    return len(errors) == 0, errors


# ============================================================================
# HEADER Y NAVEGACIÓN
# ============================================================================

def render_app_header() -> str:
    """
    Renderiza el header de la aplicación.
    
    Returns:
        Modo seleccionado ('new', 'rewrite' o 'verify')
    """
    st.title(f"🚀 {APP_TITLE}")
    st.caption(f"Versión {__version__} | Generación de contenido SEO en 3 etapas")
    
    st.markdown("---")
    
    # Selector de modo - ÚNICO en toda la app (ahora con 3 opciones)
    col1, col2, col3 = st.columns([3, 1, 1])
    
    with col1:
        mode = st.radio(
            "Modo",
            options=['new', 'rewrite', 'verify'],
            format_func=lambda x: {
                'new': '📝 Nuevo Contenido',
                'rewrite': '🔄 Reescritura Competitiva',
                'verify': '🔍 Verificar Keyword'
            }.get(x, x),
            horizontal=True,
            key='mode_selector_main'
        )
    
    with col3:
        if st.button("🗑️ Limpiar", use_container_width=True):
            clear_session_state()
            st.rerun()
    
    st.session_state.mode = mode
    return mode


def clear_session_state() -> None:
    """
    Limpia el estado de la sesión - resetea todos los campos del formulario.
    
    Limpia:
    - Resultados de generación (draft, análisis, final)
    - Campos de reescritura (competidores, HTML, enlaces)
    - Datos del formulario de nuevo contenido
    - Estado de búsquedas (SEMrush, GSC)
    - Valores de widgets (inputs de texto, selectores, etc.)
    
    NO limpia:
    - mode (mantiene el modo actual)
    - initialized (estado de inicialización)
    - mode_selector_main (selector de modo)
    """
    
    # --- Resultados de generación ---
    generation_keys = [
        'draft_html',
        'analysis_json', 
        'final_html',
        'rewrite_analysis',
        'generation_in_progress',
        'current_stage',
        'content_history',
        'last_config',
        'generation_metadata',
        'verify_result',
        # Refinamiento
        'refine_prompt_input',
    ]
    
    # --- Campos de reescritura ---
    rewrite_keys = [
        'html_to_rewrite',
        'last_rewrite_keyword',
        'manual_urls_input',
        'rewrite_competitors_data',
        'rewrite_gsc_analysis',
        'rewrite_links',
        'semrush_response',
        'show_manual_fallback',
        # Widgets de reescritura
        'html_rewrite_input',
        'rewrite_keyword_input',
    ]
    
    # --- Datos del formulario de nuevo contenido ---
    form_keys = [
        'form_data',
        # Widgets principales de inputs
        'main_keyword',
        'main_arquetipo', 
        'main_pdp_url',
        'main_length',
        'main_competitors',
        'main_instructions',
    ]
    
    # Combinar todas las keys a limpiar
    all_keys_to_clear = generation_keys + rewrite_keys + form_keys
    
    # Limpiar cada key
    for key in all_keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]
    
    # Limpiar keys dinámicas de enlaces y otros widgets dinámicos
    # Importante: convertir a lista para evitar "dictionary changed size during iteration"
    keys_to_delete = []
    for key in list(st.session_state.keys()):
        # NO borrar el selector de modo
        if key == 'mode_selector_main' or key == 'mode' or key == 'initialized':
            continue
            
        # Enlaces de inputs_FINAL.py (main_internal_url_X, main_pdp_anchor_X, etc.)
        # Enlaces de rewrite_FINAL.py (rewrite_link_url_X, rewrite_link_text_X)
        # Preguntas guía del briefing (main_guiding_X)
        # Producto alternativo (main_alt_url, main_alt_name)
        # Previews de competidores (preview_comp_X)
        # Contadores de enlaces (X_link_count)
        if any(pattern in key for pattern in [
            # Patrones de enlaces
            '_url_', '_anchor_', '_link_', '_del_', '_add',
            'link_url', 'link_anchor', 'link_text',
            'rewrite_link_url_', 'rewrite_link_text_', 'remove_rewrite_link_',
            # Patrones de briefing/guiding
            '_guiding_', 'guiding_',
            # Patrones de producto alternativo  
            '_alt_url', '_alt_name',
            # Patrones de competidores y previews
            'preview_comp_', 'competitor_',
            # Contadores
            '_link_count', '_count',
        ]):
            keys_to_delete.append(key)
    
    for key in keys_to_delete:
        if key in st.session_state:
            del st.session_state[key]
    
    # Resetear timestamp
    st.session_state.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    logger.info(f"Estado de sesión limpiado: {len(all_keys_to_clear) + len(keys_to_delete)} keys eliminadas")


# ============================================================================
# MODOS DE GENERACIÓN
# ============================================================================

def render_new_content_mode() -> None:
    """Renderiza el modo de nuevo contenido."""
    
    st.markdown("### 📝 Generación de Nuevo Contenido")
    
    if not _inputs_available or render_content_inputs is None:
        st.error("❌ El módulo de inputs no está disponible")
        return
    
    # Renderizar inputs y obtener configuración
    is_valid, config = render_content_inputs()
    
    if not is_valid:
        return
    
    # Botón de generación
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        generate_clicked = st.button(
            "🚀 Generar Contenido",
            type="primary",
            use_container_width=True,
            disabled=st.session_state.get('generation_in_progress', False)
        )
    
    if generate_clicked:
        execute_generation_pipeline(config, mode='new')


def render_rewrite_mode() -> None:
    """Renderiza el modo de reescritura competitiva."""
    
    st.markdown("### 🔄 Reescritura Competitiva")
    
    if not _rewrite_ui_available or render_rewrite_section is None:
        st.error("❌ El módulo de reescritura no está disponible")
        return
    
    if not _rewrite_available:
        st.error("❌ El módulo prompts.rewrite no está disponible")
        return
    
    # Renderizar sección de reescritura
    is_valid, config = render_rewrite_section()
    
    if not is_valid:
        return
    
    # Botón de generación
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        generate_clicked = st.button(
            "🚀 Generar Reescritura",
            type="primary",
            use_container_width=True,
            disabled=st.session_state.get('generation_in_progress', False)
        )
    
    if generate_clicked:
        execute_generation_pipeline(config, mode='rewrite')


# ============================================================================
# MODO VERIFICAR KEYWORD
# ============================================================================

def render_verify_mode() -> None:
    """
    Renderiza el modo de verificación de keyword.
    Solo comprueba si la keyword ya rankea sin generar contenido.
    """
    
    st.markdown("### 🔍 Verificar Keyword en Contenido Existente")
    
    st.info("""
    **¿Para qué sirve?**
    
    Comprueba si ya tienes contenido rankeando para una keyword antes de crear algo nuevo.
    Esto te ayuda a evitar **canibalización de keywords** (cuando múltiples URLs 
    compiten por la misma búsqueda).
    """)
    
    # Input de keyword
    keyword = st.text_input(
        "🎯 Keyword a verificar",
        placeholder="Ej: mejores portátiles gaming 2025",
        help="Introduce la keyword que quieres verificar"
    )
    
    if not keyword or len(keyword.strip()) < 3:
        st.warning("👆 Introduce una keyword de al menos 3 caracteres para verificar")
        return
    
    # Cargar módulo GSC
    try:
        from utils.gsc_utils import (
            search_existing_content,
            get_content_coverage_summary,
            load_gsc_keywords_csv
        )
        _gsc_utils_available = True
    except ImportError:
        _gsc_utils_available = False
    
    st.markdown("---")
    
    # Botón de verificación
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        verify_clicked = st.button(
            "🔍 Verificar Keyword",
            type="primary",
            use_container_width=True
        )
    
    if verify_clicked:
        if _gsc_utils_available:
            # Usar funciones directamente
            st.markdown("---")
            with st.spinner(f"🔍 Buscando '{keyword}' en datos de GSC..."):
                try:
                    # Cargar datos
                    df = load_gsc_keywords_csv()
                    
                    if df is None or (hasattr(df, 'empty') and df.empty):
                        st.warning("⚠️ No se pudieron cargar los datos de GSC")
                        return
                    
                    # Buscar contenido existente
                    matches = search_existing_content(keyword)
                    summary = get_content_coverage_summary(keyword)
                    
                    # Mostrar resultados
                    render_verify_results(keyword, matches, summary)
                    
                except Exception as e:
                    st.error(f"❌ Error al verificar: {e}")
                    logger.error(f"Error en verificación GSC: {e}")
        
        else:
            st.error("""
            ❌ **Módulo GSC no disponible**
            
            Para usar esta funcionalidad necesitas:
            1. El archivo `ui/gsc_section.py` o
            2. El archivo `utils/gsc_utils.py` con las funciones de búsqueda
            3. Un CSV con datos de Google Search Console (`gsc_keywords.csv`)
            """)


def render_verify_results(keyword: str, matches: List[Dict], summary: Dict) -> None:
    """
    Renderiza los resultados de verificación de keyword.
    
    Args:
        keyword: Keyword verificada
        matches: Lista de URLs que coinciden
        summary: Resumen del análisis
    """
    
    st.markdown("### 📊 Resultados de la Verificación")
    
    if not matches:
        st.success(f"""
        ✅ **No se encontró contenido existente para "{keyword}"**
        
        Puedes crear contenido nuevo para esta keyword sin riesgo de canibalización.
        
        💡 **Recomendación:** Procede con la generación usando el modo "Nuevo Contenido" 
        o "Reescritura Competitiva".
        """)
        return
    
    # Hay matches - mostrar alerta según gravedad
    num_urls = len(set(m.get('url', '') for m in matches))
    
    if num_urls == 1:
        st.warning(f"""
        ⚠️ **Ya tienes contenido rankeando para "{keyword}"**
        
        Se encontró **1 URL** que ya posiciona para esta keyword o variaciones similares.
        
        💡 **Recomendación:** Considera mejorar el contenido existente en lugar de crear uno nuevo.
        """)
    else:
        st.error(f"""
        🔴 **Posible canibalización detectada para "{keyword}"**
        
        Se encontraron **{num_urls} URLs** compitiendo por esta keyword.
        
        💡 **Recomendación:** Consolida el contenido en una sola URL o diferencia 
        claramente la intención de cada página.
        """)
    
    # Métricas principales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("URLs Encontradas", num_urls)
    
    with col2:
        best_position = min(m.get('position', 100) for m in matches) if matches else 0
        st.metric("Mejor Posición", f"#{best_position:.0f}")
    
    with col3:
        total_clicks = sum(m.get('clicks', 0) for m in matches)
        st.metric("Total Clics", f"{total_clicks:,}")
    
    with col4:
        total_impressions = sum(m.get('impressions', 0) for m in matches)
        st.metric("Total Impresiones", f"{total_impressions:,}")
    
    # Tabla de matches
    with st.expander("📋 Ver URLs que rankean", expanded=True):
        # Crear tabla
        table_data = []
        for m in matches:
            table_data.append({
                'URL': m.get('url', ''),
                'Query': m.get('query', m.get('keyword', '')),
                'Posición': f"#{m.get('position', 0):.0f}",
                'Clics': m.get('clicks', 0),
                'Impresiones': f"{m.get('impressions', 0):,}",
                'CTR': f"{m.get('ctr', 0):.2%}" if isinstance(m.get('ctr', 0), (int, float)) else m.get('ctr', '0%'),
                'Score': m.get('match_score', 0),
            })
        
        if table_data:
            import pandas as pd
            df = pd.DataFrame(table_data)
            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    'URL': st.column_config.LinkColumn('URL', width='large'),
                    'Clics': st.column_config.NumberColumn('Clics', format='%d'),
                }
            )
    
    # Recomendaciones según summary
    if summary:
        st.markdown("---")
        st.markdown("### 💡 Recomendaciones")
        
        recommendation = summary.get('recommendation', '')
        
        if 'create_new' in recommendation.lower() or not matches:
            st.success("✅ Puedes crear contenido nuevo para esta keyword")
        elif 'improve' in recommendation.lower():
            st.info("📝 Considera mejorar el contenido existente")
        elif 'consolidate' in recommendation.lower():
            st.warning("🔄 Considera consolidar el contenido en una sola URL")
        elif 'caution' in recommendation.lower() or num_urls > 1:
            st.error("⚠️ Procede con cautela - hay riesgo de canibalización")


# ============================================================================
# REFINAMIENTO POST-GENERACIÓN
# ============================================================================

def render_refinement_section() -> None:
    """Renderiza la sección de refinamiento post-generación."""
    
    if not st.session_state.get('final_html'):
        return
    
    st.markdown("---")
    st.markdown("### ✨ Refinamiento del Contenido")
    
    st.info("""
    ¿No estás satisfecho con algún aspecto? Puedes pedir ajustes específicos 
    y Claude refinará el contenido manteniendo la estructura.
    """)
    
    # Input de refinamiento
    refine_prompt = st.text_area(
        "Instrucciones de refinamiento",
        placeholder="Ej: Hazlo más técnico, añade más ejemplos prácticos, reduce la introducción...",
        height=100,
        key="refine_prompt_input"
    )
    
    # Ejemplos de refinamiento
    with st.expander("💡 Ejemplos de refinamiento"):
        st.markdown("""
        - "Hazlo más técnico y detallado"
        - "Añade más ejemplos prácticos de uso"
        - "Reduce la introducción y ve al grano"
        - "Mejora la sección de FAQs con preguntas más específicas"
        - "Añade comparativas con productos similares"
        - "Haz el tono más cercano y menos formal"
        - "Incluye más datos técnicos y especificaciones"
        """)
    
    # Botones de acción
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🚀 Aplicar Refinamiento", type="primary", use_container_width=True):
            if refine_prompt.strip():
                execute_refinement(refine_prompt)
            else:
                st.warning("⚠️ Escribe instrucciones de refinamiento")
    
    with col2:
        render_undo_button()


def execute_refinement(refine_prompt: str) -> None:
    """
    Ejecuta el refinamiento del contenido.
    
    Args:
        refine_prompt: Instrucciones de refinamiento del usuario
    """
    
    if ContentGenerator is None:
        st.error("❌ El generador de contenido no está disponible")
        return
    
    with st.spinner("✨ Refinando contenido..."):
        try:
            # Construir prompt de refinamiento
            current_content = st.session_state.final_html
            current_word_count = count_words_in_html(current_content)
            
            # Prompt completo con system incluido
            refinement_prompt = f"""Eres un editor experto en contenido SEO para PcComponentes.
Tu tarea es refinar el contenido existente según las instrucciones del usuario.

REGLAS:
1. Mantén el formato HTML válido
2. Preserva los enlaces internos existentes
3. Mantén aproximadamente la misma longitud ({current_word_count} palabras ±10%)
4. Mejora según las instrucciones sin perder información valiosa
5. Mantén el tono de marca PcComponentes (experto, cercano, confiable)
6. NO uses frases negativas como "evita este producto" - usa alternativas positivas

---

CONTENIDO ACTUAL:
{current_content}

---

INSTRUCCIONES DE REFINAMIENTO:
{refine_prompt}

---

Genera el contenido refinado aplicando los cambios solicitados. 
Responde SOLO con el HTML mejorado, sin explicaciones adicionales."""

            # Crear generador y ejecutar
            generator = ContentGenerator(
                api_key=CLAUDE_API_KEY,
                model=CLAUDE_MODEL,
                max_tokens=MAX_TOKENS,
                temperature=TEMPERATURE
            )
            
            # CORRECCIÓN: generator.generate() retorna GenerationResult
            result = generator.generate(refinement_prompt)
            
            if not result.success:
                st.error(f"❌ Error en refinamiento: {result.error}")
                return
            
            refined_content = result.content
            
            # Validar resultado
            if not refined_content or len(refined_content) < 100:
                st.error("❌ El contenido refinado está vacío o es muy corto")
                return
            
            # Guardar versión anterior en historial
            st.session_state.content_history.append({
                'content': current_content,
                'timestamp': datetime.now().isoformat(),
                'word_count': current_word_count
            })
            
            # Actualizar contenido
            st.session_state.final_html = extract_html_content(refined_content)
            
            # Mostrar métricas
            new_word_count = count_words_in_html(st.session_state.final_html)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Palabras antes", current_word_count)
            with col2:
                st.metric("Palabras después", new_word_count)
            with col3:
                diff = new_word_count - current_word_count
                st.metric("Diferencia", f"{diff:+d}")
            
            st.success("✅ Contenido refinado correctamente")
            st.rerun()
            
        except Exception as e:
            logger.error(f"Error en refinamiento: {e}")
            st.error(f"❌ Error: {str(e)}")


def render_undo_button() -> None:
    """Renderiza el botón de deshacer."""
    
    history = st.session_state.get('content_history', [])
    
    if not history:
        st.button("↩️ Deshacer", disabled=True, use_container_width=True)
        return
    
    if st.button("↩️ Deshacer último cambio", use_container_width=True):
        # Restaurar última versión
        last_version = history.pop()
        st.session_state.final_html = last_version['content']
        st.success(f"✅ Restaurada versión de {last_version['timestamp']}")
        st.rerun()


# ============================================================================
# PIPELINE DE GENERACIÓN
# ============================================================================

def execute_generation_pipeline(config: Dict[str, Any], mode: str = 'new') -> None:
    """
    Ejecuta el pipeline completo de generación en 3 etapas.
    
    Args:
        config: Configuración de generación
        mode: 'new' para nuevo contenido, 'rewrite' para reescritura
    """
    
    if ContentGenerator is None:
        st.error("❌ ContentGenerator no está disponible")
        return
    
    # Validar módulos según modo
    if mode == 'new' and not _new_content_available:
        st.error("❌ Módulo prompts.new_content no disponible")
        return
    
    if mode == 'rewrite' and not _rewrite_available:
        st.error("❌ Módulo prompts.rewrite no disponible")
        return
    
    # Marcar generación en progreso
    st.session_state.generation_in_progress = True
    st.session_state.last_config = config
    
    # Crear generador
    try:
        generator = ContentGenerator(
            api_key=CLAUDE_API_KEY,
            model=CLAUDE_MODEL,
            max_tokens=MAX_TOKENS,
            temperature=TEMPERATURE
        )
    except Exception as e:
        st.error(f"❌ Error al crear generador: {e}")
        st.session_state.generation_in_progress = False
        return
    
    # Contenedor de progreso
    progress_container = st.container()
    
    try:
        # ====================================================================
        # ETAPA 0 (solo rewrite): ANÁLISIS COMPETITIVO
        # ====================================================================
        
        if mode == 'rewrite':
            if not st.session_state.get('rewrite_analysis'):
                with progress_container:
                    st.markdown("### 🔍 Análisis Competitivo")
                    
                    with st.spinner("Analizando contenido de competidores..."):
                        # Verificar que tenemos los datos necesarios
                        competitors_data = config.get('competitors_data', [])
                        html_to_rewrite = config.get('html_to_rewrite', '')
                        
                        if not competitors_data and not html_to_rewrite:
                            st.warning("⚠️ No hay competidores ni contenido HTML para analizar.")
                        
                        # Formatear competidores
                        competitor_contents = rewrite.format_competitors_for_prompt(competitors_data)
                        
                        # Si hay HTML a reescribir, añadirlo
                        if html_to_rewrite:
                            competitor_contents += f"""

---
CONTENIDO ACTUAL A MEJORAR:
{html_to_rewrite}
---
"""
                        
                        # NOTA: build_competitor_analysis_prompt() NO EXISTE
                        # Construimos el prompt de análisis inline
                        analysis_prompt = f"""Analiza el siguiente contenido de competidores para la keyword "{config['keyword']}".

{competitor_contents}

Proporciona un análisis estructurado que incluya:
1. Fortalezas comunes de los competidores
2. Debilidades y gaps de contenido
3. Oportunidades de diferenciación
4. Longitud promedio y estructura
5. Keywords secundarias detectadas
6. Recomendaciones para superar a la competencia

Formato tu respuesta de manera clara y accionable."""
                        
                        # Ejecutar análisis
                        result = generator.generate(analysis_prompt)
                        
                        if result.success:
                            st.session_state.rewrite_analysis = result.content
                            st.success("✅ Análisis competitivo completado")
                        else:
                            st.warning(f"⚠️ Análisis parcial: {result.error}")
                            st.session_state.rewrite_analysis = "Análisis no disponible"
                        
                        time.sleep(0.5)
        
        # ====================================================================
        # ETAPA 1: BORRADOR INICIAL
        # ====================================================================
        
        with progress_container:
            st.markdown("### 📝 Etapa 1/3: Generando Borrador Inicial")
            st.session_state.current_stage = 1
            
            with st.spinner("Claude está escribiendo el borrador inicial..."):
                # Construir prompt según el modo
                if mode == 'new':
                    # Obtener arquetipo
                    arquetipo = get_arquetipo(config.get('arquetipo_codigo', 'ARQ-1'))
                    
                    if arquetipo is None:
                        logger.warning(f"Arquetipo no encontrado: {config.get('arquetipo_codigo')}")
                        arquetipo = {'code': 'ARQ-1', 'name': 'Review', 'tone': 'experto'}
                    
                    # CORRECCIÓN: Usar nombre correcto y parámetros correctos
                    stage1_prompt = new_content.build_new_content_prompt_stage1(
                        keyword=config.get('keyword', ''),  # REQUERIDO, posición 1
                        arquetipo=arquetipo,  # REQUERIDO, posición 2
                        target_length=config.get('target_length', 1500),
                        pdp_data=config.get('pdp_data'),
                        links_data=config.get('links', config.get('internal_links', [])),  # links_data, NO links
                        secondary_keywords=config.get('keywords', []),  # secondary_keywords, NO keywords
                        additional_instructions=config.get('objetivo', ''),
                        campos_especificos=config.get('campos_arquetipo', {}),  # campos_especificos, NO campos_arquetipo
                        guiding_context=config.get('context', config.get('guiding_context', '')),  # guiding_context, NO context
                        alternative_product=config.get('producto_alternativo', config.get('alternative_product'))  # alternative_product
                    )
                else:  # mode == 'rewrite'
                    # Obtener arquetipo si está configurado
                    arquetipo = None
                    if config.get('arquetipo_codigo'):
                        arq_code = config['arquetipo_codigo']
                        if ':' in arq_code:
                            arq_code = arq_code.split(':')[0].strip()
                        arquetipo = get_arquetipo(arq_code)
                    
                    # Preparar contexto con HTML a reescribir si existe
                    context_with_html = config.get('context', '')
                    if config.get('html_to_rewrite'):
                        context_with_html += f"""

CONTENIDO ACTUAL A MEJORAR/REESCRIBIR:
{config.get('html_to_rewrite')}

Usa este contenido como base, mejóralo y amplíalo según el análisis competitivo.
"""
                    
                    # CORRECCIÓN: Usar nombre correcto (build_rewrite_prompt_stage1, NO _draft)
                    stage1_prompt = rewrite.build_rewrite_prompt_stage1(
                        keyword=config['keyword'],
                        competitor_analysis=st.session_state.get('rewrite_analysis', ''),
                        pdp_data=config.get('pdp_data'),
                        target_length=config.get('target_length', 1500),
                        keywords=config.get('keywords', [config['keyword']]),  # Aquí SÍ es keywords
                        context=context_with_html,  # Aquí SÍ es context
                        links=config.get('links', {}),  # Aquí SÍ es links
                        objetivo=config.get('objetivo', ''),
                        producto_alternativo=config.get('producto_alternativo', {}),
                        arquetipo=arquetipo
                    )
                
                # Generar borrador
                # CORRECCIÓN: generator.generate() retorna GenerationResult
                result = generator.generate(stage1_prompt)
                
                if not result.success:
                    st.error(f"❌ Error en Etapa 1: {result.error}")
                    st.session_state.generation_in_progress = False
                    return
                
                draft_html = result.content
                
                # Validar que obtuvimos contenido
                if not draft_html or len(draft_html) < 100:
                    st.error("❌ El borrador generado está vacío o es muy corto")
                    st.session_state.generation_in_progress = False
                    return
                
                # Extraer HTML limpio
                st.session_state.draft_html = extract_html_content(draft_html)
                
                # Mostrar métricas
                word_count = count_words_in_html(st.session_state.draft_html)
                st.success(f"✅ Borrador completado: {word_count} palabras")
                time.sleep(0.5)
        
        # ====================================================================
        # ETAPA 2: ANÁLISIS CRÍTICO
        # ====================================================================
        
        with progress_container:
            st.markdown("### 🔍 Etapa 2/3: Análisis Crítico")
            st.session_state.current_stage = 2
            
            with st.spinner("Claude está analizando el borrador..."):
                # Construir prompt de análisis según modo
                if mode == 'new':
                    # CORRECCIÓN: Usar parámetros correctos
                    stage2_prompt = new_content.build_correction_prompt_stage2(
                        draft_content=st.session_state.draft_html,
                        target_length=config.get('target_length', 1500),
                        keyword=config.get('keyword', ''),
                        links_to_verify=config.get('links', config.get('internal_links', [])),
                        alternative_product=config.get('producto_alternativo', config.get('alternative_product'))
                    )
                else:  # mode == 'rewrite'
                    stage2_prompt = rewrite.build_rewrite_correction_prompt_stage2(
                        draft_content=st.session_state.draft_html,
                        target_length=config.get('target_length', 1500),
                        keyword=config.get('keyword', ''),
                        competitor_analysis=st.session_state.get('rewrite_analysis', ''),
                        objetivo=config.get('objetivo', '')
                    )
                
                # Generar análisis
                # CORRECCIÓN: generator.generate() retorna GenerationResult
                result = generator.generate(stage2_prompt)
                
                if not result.success:
                    st.warning(f"⚠️ Análisis parcial: {result.error}")
                    st.session_state.analysis_json = "{}"
                else:
                    st.session_state.analysis_json = result.content
                
                st.success("✅ Análisis completado")
                time.sleep(0.5)
        
        # ====================================================================
        # ETAPA 3: VERSIÓN FINAL
        # ====================================================================
        
        with progress_container:
            st.markdown("### ✅ Etapa 3/3: Generando Versión Final")
            st.session_state.current_stage = 3
            
            with st.spinner("Claude está generando la versión final..."):
                # Construir prompt final según modo
                if mode == 'new':
                    # CORRECCIÓN: Usar nombre correcto (build_final_prompt_stage3, NO build_final_generation_prompt_stage3)
                    stage3_prompt = new_content.build_final_prompt_stage3(
                        draft_content=st.session_state.draft_html,
                        analysis_feedback=st.session_state.analysis_json,
                        keyword=config.get('keyword', ''),
                        target_length=config.get('target_length', 1500),
                        links_data=config.get('links', config.get('internal_links', [])),
                        alternative_product=config.get('producto_alternativo', config.get('alternative_product'))
                    )
                else:  # mode == 'rewrite'
                    stage3_prompt = rewrite.build_rewrite_final_prompt_stage3(
                        draft_content=st.session_state.draft_html,
                        corrections_json=st.session_state.analysis_json,
                        target_length=config.get('target_length', 1500),
                        competitor_analysis=st.session_state.get('rewrite_analysis', '')
                    )
                
                # Generar versión final
                # CORRECCIÓN: generator.generate() retorna GenerationResult
                result = generator.generate(stage3_prompt)
                
                if not result.success:
                    st.error(f"❌ Error en Etapa 3: {result.error}")
                    st.session_state.generation_in_progress = False
                    return
                
                final_html = result.content
                
                # Validar contenido final
                if not final_html or len(final_html) < 100:
                    st.error("❌ El contenido final está vacío o es muy corto")
                    st.session_state.generation_in_progress = False
                    return
                
                # Extraer HTML limpio
                st.session_state.final_html = extract_html_content(final_html)
                
                # Mostrar métricas finales
                final_word_count = count_words_in_html(st.session_state.final_html)
                target = config.get('target_length', 1500)
                diff_pct = ((final_word_count - target) / target) * 100 if target > 0 else 0
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Palabras Finales", final_word_count)
                with col2:
                    st.metric("Objetivo", target)
                with col3:
                    st.metric("Precisión", f"{100 - abs(diff_pct):.1f}%")
                
                st.success("✅ ¡Generación completada!")
        
        # Guardar metadata
        save_generation_to_state(config, mode)
        
    except Exception as e:
        logger.error(f"Error en pipeline: {e}\n{traceback.format_exc()}")
        st.error(f"❌ Error durante la generación: {str(e)}")
        
        with st.expander("Ver detalles del error"):
            st.code(traceback.format_exc())
    
    finally:
        st.session_state.generation_in_progress = False
        st.session_state.current_stage = 0


def save_generation_to_state(config: Dict[str, Any], mode: str) -> None:
    """Guarda metadata de la generación."""
    
    st.session_state.generation_metadata = {
        'timestamp': datetime.now().isoformat(),
        'mode': mode,
        'keyword': config.get('keyword', ''),
        'target_length': config.get('target_length', 1500),
        'arquetipo': config.get('arquetipo_codigo', ''),
        'config': {k: v for k, v in config.items() if k not in ['html_to_rewrite', 'competitors_data', 'pdp_data']},
    }


# ============================================================================
# RESULTADOS Y FOOTER
# ============================================================================

def render_results() -> None:
    """Renderiza la sección de resultados."""
    
    if not any([
        st.session_state.get('draft_html'),
        st.session_state.get('analysis_json'),
        st.session_state.get('final_html')
    ]):
        return
    
    if _results_available and render_results_section:
        render_results_section(
            draft_html=st.session_state.get('draft_html'),
            analysis_json=st.session_state.get('analysis_json'),
            final_html=st.session_state.get('final_html'),
            target_length=st.session_state.get('last_config', {}).get('target_length', 1500),
            mode=st.session_state.get('mode', 'new')
        )
    else:
        # Fallback simple si render_results_section no está disponible
        st.markdown("---")
        st.subheader("📊 Resultados")
        
        if st.session_state.get('final_html'):
            st.markdown("### ✅ Contenido Final")
            with st.expander("Ver HTML"):
                st.code(st.session_state.final_html, language="html")
            
            st.download_button(
                "📥 Descargar HTML",
                st.session_state.final_html,
                file_name=f"content_{st.session_state.get('timestamp', 'export')}.html",
                mime="text/html"
            )


def render_footer() -> None:
    """Renderiza el footer de la aplicación."""
    
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.caption(f"📦 Versión {__version__}")
    
    with col2:
        st.caption("🏢 PcComponentes - Product Discovery & Content")
    
    with col3:
        if DEBUG_MODE:
            st.caption("🐛 Modo Debug Activo")


def render_debug_panel() -> None:
    """Renderiza panel de debug (solo si DEBUG_MODE=True)."""
    
    if not DEBUG_MODE:
        return
    
    with st.expander("🐛 Debug Panel"):
        st.json({
            'mode': st.session_state.get('mode'),
            'generation_in_progress': st.session_state.get('generation_in_progress'),
            'current_stage': st.session_state.get('current_stage'),
            'has_draft': st.session_state.get('draft_html') is not None,
            'has_analysis': st.session_state.get('analysis_json') is not None,
            'has_final': st.session_state.get('final_html') is not None,
            'history_length': len(st.session_state.get('content_history', [])),
            'modules': {
                'generator': _generator_available,
                'new_content': _new_content_available,
                'rewrite': _rewrite_available,
                'inputs_ui': _inputs_available,
                'rewrite_ui': _rewrite_ui_available,
                'results_ui': _results_available,
            }
        })


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Función principal de la aplicación."""
    
    # Configuración de página
    st.set_page_config(
        page_title=APP_TITLE,
        page_icon="🚀",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    # Inicializar
    initialize_app()
    
    # Verificar configuración
    is_valid, errors = check_configuration()
    
    if not is_valid:
        st.error("❌ Error de Configuración")
        for error in errors:
            st.warning(f"• {error}")
        st.stop()
    
    # Sidebar
    if _sidebar_available and render_sidebar:
        render_sidebar()
    
    # Header con selector de modo
    mode = render_app_header()
    
    # Renderizar según modo
    if mode == 'new':
        render_new_content_mode()
    elif mode == 'rewrite':
        render_rewrite_mode()
    elif mode == 'verify':
        render_verify_mode()
    
    # Resultados (solo para modos de generación)
    if mode in ['new', 'rewrite']:
        render_results()
    
    # Refinamiento (solo si hay contenido final)
    if st.session_state.get('final_html'):
        render_refinement_section()
    
    # Footer
    render_footer()
    
    # Debug panel
    render_debug_panel()


if __name__ == "__main__":
    main()
