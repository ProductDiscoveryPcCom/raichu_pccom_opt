# -*- coding: utf-8 -*-
"""
UI Inputs - PcComponentes Content Generator
Versión 4.5.1

Componentes de entrada para la interfaz Streamlit.
Incluye: validación, anchor text, preguntas guía, producto alternativo,
fecha GSC, análisis de canibalización, campo HTML para reescritura,
integración con n8n para obtener datos de producto.

Autor: PcComponentes - Product Discovery & Content
"""

import re
import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
from urllib.parse import urlparse
from datetime import datetime

import streamlit as st

# Importar integración con n8n (opcional)
try:
    from core.n8n_integration import fetch_product_for_streamlit
    _n8n_available = True
except ImportError:
    try:
        from n8n_integration import fetch_product_for_streamlit
        _n8n_available = True
    except ImportError:
        _n8n_available = False
        fetch_product_for_streamlit = None

logger = logging.getLogger(__name__)

# ============================================================================
# CONSTANTES
# ============================================================================

__version__ = "4.5.0"

DEFAULT_CONTENT_LENGTH = 1500
MIN_CONTENT_LENGTH = 500
MAX_CONTENT_LENGTH = 5000
MAX_COMPETITORS = 5
MAX_LINKS_PER_TYPE = 10
MAX_ANCHOR_LENGTH = 100
MIN_KEYWORD_LENGTH = 2
MAX_KEYWORD_LENGTH = 100
MAX_URL_LENGTH = 2000
GSC_DATA_WARNING_DAYS = 7

PCCOMPONENTES_DOMAINS = ['www.pccomponentes.com', 'pccomponentes.com']

URL_PATTERN = re.compile(
    r'^https?://'
    r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'
    r'localhost|'
    r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
    r'(?::\d+)?'
    r'(?:/?|[/?]\S+)$',
    re.IGNORECASE
)

ERROR_MESSAGES = {
    'keyword_empty': 'La keyword es obligatoria',
    'keyword_too_short': f'La keyword debe tener al menos {MIN_KEYWORD_LENGTH} caracteres',
    'keyword_too_long': f'La keyword no puede exceder {MAX_KEYWORD_LENGTH} caracteres',
    'url_invalid': 'La URL no tiene un formato válido',
    'url_not_pccomponentes': 'La URL debe ser de PcComponentes',
    'length_out_of_range': f'La longitud debe estar entre {MIN_CONTENT_LENGTH} y {MAX_CONTENT_LENGTH}',
    'anchor_too_long': f'El anchor text no puede exceder {MAX_ANCHOR_LENGTH} caracteres',
    'html_empty': 'El contenido HTML es obligatorio para reescritura',
}

# ============================================================================
# IMPORTS CON FALLBACKS ROBUSTOS
# ============================================================================

try:
    from config.settings import (
        DEFAULT_CONTENT_LENGTH as _DCL,
        MIN_CONTENT_LENGTH as _MCL,
        MAX_CONTENT_LENGTH as _MXCL,
        MAX_COMPETITORS as _MC,
        PCCOMPONENTES_DOMAINS as _PD,
    )
    DEFAULT_CONTENT_LENGTH = _DCL
    MIN_CONTENT_LENGTH = _MCL
    MAX_CONTENT_LENGTH = _MXCL
    MAX_COMPETITORS = _MC
    PCCOMPONENTES_DOMAINS = _PD
except ImportError:
    pass

# Arquetipos - Fallback completo con 34 arquetipos
_ARQUETIPOS_FALLBACK = {f"ARQ-{i}": {"code": f"ARQ-{i}", "name": f"Arquetipo {i}", "guiding_questions": []} for i in range(1, 35)}

try:
    from config.archetipos import (
        ARQUETIPOS,
        get_arquetipo,
        get_arquetipo_names,
        get_guiding_questions,
        get_default_length,
        get_length_range,
    )
except ImportError:
    ARQUETIPOS = _ARQUETIPOS_FALLBACK
    def get_arquetipo(code): return ARQUETIPOS.get(code)
    def get_arquetipo_names(): return {k: v['name'] for k, v in ARQUETIPOS.items()}
    def get_guiding_questions(code): return ARQUETIPOS.get(code, {}).get('guiding_questions', [])
    def get_default_length(code): return ARQUETIPOS.get(code, {}).get('default_length', DEFAULT_CONTENT_LENGTH)
    def get_length_range(code): 
        arq = ARQUETIPOS.get(code, {})
        return (arq.get('min_length', MIN_CONTENT_LENGTH), arq.get('max_length', MAX_CONTENT_LENGTH))

# GSC Utils - para verificación de canibalización
try:
    from utils.gsc_utils import (
        get_gsc_data_date,
        is_gsc_data_stale,
        check_cannibalization,
        get_cannibalization_summary,
        load_gsc_keywords_csv,
        search_existing_content,
        get_content_coverage_summary,
    )
    _gsc_available = True
except ImportError:
    _gsc_available = False
    def get_gsc_data_date(): return None
    def is_gsc_data_stale(days=7): return True
    def check_cannibalization(kw, **kwargs): return []
    def get_cannibalization_summary(kw): return {'has_risk': False, 'urls': [], 'recommendation': ''}
    def load_gsc_keywords_csv(): return []
    def search_existing_content(kw, **kwargs): return []
    def get_content_coverage_summary(kw): return {'has_coverage': False, 'recommendation': ''}


# ============================================================================
# CLASES DE DATOS
# ============================================================================

class InputValidationError(Exception):
    """Error de validación de input."""
    pass

class KeywordValidationError(InputValidationError):
    """Error de validación de keyword."""
    pass

class URLValidationError(InputValidationError):
    """Error de validación de URL."""
    pass

class LengthValidationError(InputValidationError):
    """Error de validación de longitud."""
    pass

class LinksValidationError(InputValidationError):
    """Error de validación de enlaces."""
    pass

class ArquetipoValidationError(InputValidationError):
    """Error de validación de arquetipo."""
    pass


class InputMode(Enum):
    """Modos de generación de contenido."""
    NEW = "new"
    REWRITE = "rewrite"


class LinkType(Enum):
    """Tipos de enlaces."""
    INTERNAL = "internal"
    PDP = "pdp"
    EXTERNAL = "external"


@dataclass
class LinkWithAnchor:
    """Enlace con anchor text personalizado."""
    url: str
    anchor: str = ""
    link_type: str = "internal"


@dataclass
class ValidationResult:
    """Resultado de validación."""
    is_valid: bool
    value: Any
    error: Optional[str] = None


@dataclass
class FormData:
    """Datos del formulario completo."""
    keyword: str
    pdp_url: Optional[str] = None
    pdp_data: Optional[Dict[str, Any]] = None  # Datos del producto obtenidos via n8n
    target_length: int = DEFAULT_CONTENT_LENGTH
    arquetipo: str = 'ARQ-1'
    mode: str = 'new'
    competitor_urls: Optional[List[str]] = None
    internal_links: Optional[List[LinkWithAnchor]] = None
    pdp_links: Optional[List[LinkWithAnchor]] = None
    additional_instructions: Optional[str] = None
    guiding_answers: Optional[Dict[str, str]] = None
    alternative_product_url: Optional[str] = None
    alternative_product_name: Optional[str] = None
    visual_elements: Optional[List[str]] = None  # Elementos visuales seleccionados


# ============================================================================
# FUNCIONES DE VALIDACIÓN
# ============================================================================

def validate_keyword(keyword: str) -> ValidationResult:
    """Valida la keyword principal."""
    if not keyword or not keyword.strip():
        return ValidationResult(False, '', ERROR_MESSAGES['keyword_empty'])
    keyword = keyword.strip()
    if len(keyword) < MIN_KEYWORD_LENGTH:
        return ValidationResult(False, keyword, ERROR_MESSAGES['keyword_too_short'])
    if len(keyword) > MAX_KEYWORD_LENGTH:
        return ValidationResult(False, keyword, ERROR_MESSAGES['keyword_too_long'])
    return ValidationResult(True, keyword)


def validate_url(url: str, require_pccomponentes: bool = False) -> ValidationResult:
    """Valida una URL."""
    if not url or not url.strip():
        return ValidationResult(True, '', None)
    url = url.strip()
    if len(url) > MAX_URL_LENGTH:
        return ValidationResult(False, url, 'URL demasiado larga')
    if not URL_PATTERN.match(url):
        return ValidationResult(False, url, ERROR_MESSAGES['url_invalid'])
    if require_pccomponentes:
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            if not any(pcc in domain for pcc in PCCOMPONENTES_DOMAINS):
                return ValidationResult(False, url, ERROR_MESSAGES['url_not_pccomponentes'])
        except Exception:
            return ValidationResult(False, url, ERROR_MESSAGES['url_invalid'])
    return ValidationResult(True, url)


def validate_length(length: int) -> ValidationResult:
    """Valida la longitud del contenido."""
    if length < MIN_CONTENT_LENGTH or length > MAX_CONTENT_LENGTH:
        return ValidationResult(False, length, ERROR_MESSAGES['length_out_of_range'])
    return ValidationResult(True, length)


def validate_arquetipo(arquetipo: str) -> ValidationResult:
    """Valida el código de arquetipo."""
    if arquetipo not in ARQUETIPOS:
        return ValidationResult(False, arquetipo, 'Arquetipo inválido')
    return ValidationResult(True, arquetipo)


def validate_html_content(html: str) -> ValidationResult:
    """Valida contenido HTML para reescritura."""
    if not html or not html.strip():
        return ValidationResult(False, '', ERROR_MESSAGES['html_empty'])
    html = html.strip()
    if len(html) < 100:
        return ValidationResult(False, html, 'El contenido HTML es demasiado corto (mínimo 100 caracteres)')
    return ValidationResult(True, html)


def validate_links_list(links_text: str, link_type: str = 'internal', max_links: int = MAX_LINKS_PER_TYPE) -> ValidationResult:
    """Valida una lista de enlaces."""
    if not links_text or not links_text.strip():
        return ValidationResult(True, [])
    lines = [line.strip() for line in links_text.strip().split('\n') if line.strip()]
    valid_links = []
    for line in lines[:max_links]:
        if URL_PATTERN.match(line):
            valid_links.append(line)
    return ValidationResult(True, valid_links)


def validate_competitor_urls(urls_text: str) -> ValidationResult:
    """Valida URLs de competidores (filtra PcComponentes)."""
    result = validate_links_list(urls_text, 'competitor', MAX_COMPETITORS)
    if result.is_valid and result.value:
        filtered = [u for u in result.value if not any(pcc in urlparse(u).netloc.lower() for pcc in PCCOMPONENTES_DOMAINS)]
        return ValidationResult(True, filtered)
    return result


# ============================================================================
# FUNCIONES DE ESTADO
# ============================================================================

def get_form_value(key: str, default: Any = None) -> Any:
    """Obtiene valor del formulario desde session_state."""
    form_data = st.session_state.get('form_data', {})
    return form_data.get(key, default)


def save_form_data(data: Dict[str, Any]) -> None:
    """Guarda datos en session_state."""
    if 'form_data' not in st.session_state:
        st.session_state.form_data = {}
    st.session_state.form_data.update(data)


def clear_form_data() -> None:
    """Limpia datos del formulario."""
    st.session_state.form_data = {}


# ============================================================================
# COMPONENTES UI: BÁSICOS
# ============================================================================

def render_keyword_input(
    key: str = "keyword_input",
    default_value: str = "",
    label: str = "🔑 Keyword Principal",
    required: bool = True,
    show_cannibalization: bool = True
) -> Tuple[str, Optional[str]]:
    """Renderiza input de keyword con validación y check de canibalización."""
    saved_value = get_form_value('keyword', default_value)
    keyword = st.text_input(
        label=label,
        value=saved_value,
        key=key,
        placeholder="Ej: mejores monitores gaming 2024"
    )
    
    if keyword:
        result = validate_keyword(keyword)
        if not result.is_valid:
            st.error(f"❌ {result.error}")
            return keyword, result.error
        save_form_data({'keyword': result.value})
        
        if show_cannibalization:
            _render_cannibalization_check(result.value)
        
        return result.value, None
    elif required:
        return "", "La keyword es obligatoria"
    return "", None


def render_url_input(
    key: str = "url_input",
    default_value: str = "",
    label: str = "🔗 URL del PDP",
    required: bool = False,
    require_pccomponentes: bool = True
) -> Tuple[str, Optional[str]]:
    """Renderiza input de URL."""
    saved_value = get_form_value('pdp_url', default_value)
    url = st.text_input(
        label=label,
        value=saved_value,
        key=key,
        placeholder="https://www.pccomponentes.com/..."
    )
    if url:
        result = validate_url(url, require_pccomponentes=require_pccomponentes)
        if not result.is_valid:
            st.error(f"❌ {result.error}")
            return url, result.error
        save_form_data({'pdp_url': result.value})
        return result.value, None
    elif required:
        return "", "La URL es obligatoria"
    return "", None


def render_product_url_with_fetch(
    key: str = "product_url",
    required: bool = False
) -> Tuple[str, Optional[Dict[str, Any]], Optional[str]]:
    """
    Renderiza input de URL de producto con botón para obtener datos via n8n.
    
    Args:
        key: Clave única para el widget
        required: Si la URL es obligatoria
        
    Returns:
        Tuple[url, product_data, error]
    """
    # Inicializar estado
    state_key = f"pdp_data_{key}"
    if state_key not in st.session_state:
        st.session_state[state_key] = None
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        saved_value = get_form_value('pdp_url', '')
        url = st.text_input(
            label="🔗 URL del Producto",
            value=saved_value,
            key=f"{key}_url",
            placeholder="https://www.pccomponentes.com/...",
            help="Pega la URL de un producto de PcComponentes"
        )
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)  # Espaciado
        fetch_disabled = not url or not _n8n_available
        
        # Tooltip si n8n no está disponible
        button_help = None
        if not _n8n_available:
            button_help = "Configura N8N_WEBHOOK_URL en secrets"
        elif not url:
            button_help = "Introduce una URL primero"
        
        if st.button("📥 Obtener datos", key=f"{key}_fetch", disabled=fetch_disabled, help=button_help):
            with st.spinner("Obteniendo datos del producto..."):
                try:
                    # Obtener secrets de Streamlit
                    secrets_dict = {}
                    if hasattr(st, 'secrets'):
                        try:
                            secrets_dict = dict(st.secrets)
                        except Exception:
                            secrets_dict = {}
                    
                    success, product_data, error = fetch_product_for_streamlit(url, secrets_dict)
                    
                    if success:
                        st.session_state[state_key] = product_data
                        st.success(f"✅ Datos obtenidos: {product_data.get('name', 'Producto')}")
                    else:
                        st.error(f"❌ {error}")
                        st.session_state[state_key] = None
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
                    st.session_state[state_key] = None
    
    # Validar URL
    error = None
    if url:
        result = validate_url(url, require_pccomponentes=True)
        if not result.is_valid:
            st.error(f"❌ {result.error}")
            error = result.error
        else:
            save_form_data({'pdp_url': result.value})
            url = result.value
    elif required:
        error = "La URL es obligatoria"
    
    # Mostrar datos obtenidos
    product_data = st.session_state.get(state_key)
    if product_data:
        with st.expander("📦 Datos del producto", expanded=True):
            col_a, col_b = st.columns(2)
            with col_a:
                st.markdown(f"**Nombre:** {product_data.get('name', 'N/A')}")
                st.markdown(f"**Marca:** {product_data.get('brand', 'N/A')}")
            with col_b:
                price = product_data.get('price_formatted') or product_data.get('price', 'N/A')
                st.markdown(f"**Precio:** {price}")
                st.markdown(f"**ID:** {product_data.get('legacy_id', 'N/A')}")
            
            # Atributos
            attrs = product_data.get('attributes', {})
            if attrs:
                st.markdown("**Características:**")
                for attr_name, attr_value in list(attrs.items())[:5]:
                    st.markdown(f"- {attr_name}: {attr_value}")
    
    return url or "", product_data, error


def render_length_slider(
    key: str = "length_slider",
    default_value: int = None,
    arquetipo_code: str = None
) -> int:
    """Renderiza slider de longitud adaptado al arquetipo."""
    min_len, max_len = MIN_CONTENT_LENGTH, MAX_CONTENT_LENGTH
    default_len = DEFAULT_CONTENT_LENGTH
    
    if arquetipo_code:
        try:
            min_len, max_len = get_length_range(arquetipo_code)
            default_len = get_default_length(arquetipo_code)
        except Exception:
            pass
    
    if default_value is not None:
        default_len = default_value
    
    saved_value = get_form_value('target_length', default_len)
    saved_value = max(min_len, min(saved_value, max_len))
    
    length = st.slider(
        label="📏 Longitud objetivo (palabras)",
        min_value=min_len,
        max_value=max_len,
        value=saved_value,
        step=100,
        key=key
    )
    save_form_data({'target_length': length})
    return length


def render_arquetipo_selector(key: str = "arquetipo_selector") -> str:
    """Renderiza selector de arquetipo."""
    saved_value = get_form_value('arquetipo', 'ARQ-1')
    names = get_arquetipo_names()
    options = list(names.keys())
    
    try:
        default_index = options.index(saved_value)
    except ValueError:
        default_index = 0
    
    arquetipo = st.selectbox(
        label="📋 Tipo de Contenido (Arquetipo)",
        options=options,
        format_func=lambda x: f"{x}: {names.get(x, x)}",
        index=default_index,
        key=key
    )
    save_form_data({'arquetipo': arquetipo})
    return arquetipo


def render_mode_selector(key: str = "mode_selector") -> str:
    """Renderiza selector de modo (nuevo/reescritura)."""
    saved_mode = get_form_value('mode', 'new')
    mode = st.radio(
        "🔄 Modo de Generación",
        options=['new', 'rewrite'],
        format_func=lambda x: '✨ Nuevo Contenido' if x == 'new' else '📝 Reescritura',
        index=0 if saved_mode == 'new' else 1,
        key=key,
        horizontal=True
    )
    save_form_data({'mode': mode})
    return mode


# ============================================================================
# COMPONENTES UI: AVANZADOS
# ============================================================================

def render_html_input(key: str = "html_input") -> Tuple[str, Optional[str]]:
    """Renderiza área de texto para pegar HTML de artículo a reescribir."""
    st.markdown("##### 📄 Contenido HTML a Reescribir")
    st.caption("Pega el código HTML del artículo que deseas reescribir")
    
    saved_value = get_form_value('html_content', '')
    html_content = st.text_area(
        label="Código HTML",
        value=saved_value,
        height=200,
        key=key,
        placeholder="<article>\n  <h1>Título del artículo...</h1>\n  <p>Contenido...</p>\n</article>",
        label_visibility="collapsed"
    )
    
    if html_content:
        result = validate_html_content(html_content)
        if not result.is_valid:
            st.error(f"❌ {result.error}")
            return html_content, result.error
        save_form_data({'html_content': result.value})
        
        # Mostrar preview
        word_count = len(html_content.split())
        char_count = len(html_content)
        st.caption(f"📊 {word_count} palabras · {char_count} caracteres")
        
        return result.value, None
    else:
        return "", "El contenido HTML es obligatorio para reescritura"


def render_links_with_anchors(
    key_prefix: str = "links",
    label: str = "Enlaces",
    link_type: str = "internal",
    max_links: int = 10
) -> List[LinkWithAnchor]:
    """Renderiza UI dinámica para enlaces con anchor text editable."""
    count_key = f"{key_prefix}_count"
    delete_key = f"{key_prefix}_delete_idx"
    
    # Inicializar estado
    if count_key not in st.session_state:
        st.session_state[count_key] = 1
    if delete_key not in st.session_state:
        st.session_state[delete_key] = None
    
    current_count = st.session_state[count_key]
    
    # Procesar eliminación pendiente
    if st.session_state[delete_key] is not None:
        idx_to_delete = st.session_state[delete_key]
        if 0 <= idx_to_delete < current_count:
            # Shift valores hacia arriba
            for j in range(idx_to_delete, current_count - 1):
                next_url = st.session_state.get(f"{key_prefix}_url_{j+1}", "")
                next_anchor = st.session_state.get(f"{key_prefix}_anchor_{j+1}", "")
                st.session_state[f"{key_prefix}_url_{j}"] = next_url
                st.session_state[f"{key_prefix}_anchor_{j}"] = next_anchor
            
            # Limpiar última fila
            last_idx = current_count - 1
            if f"{key_prefix}_url_{last_idx}" in st.session_state:
                del st.session_state[f"{key_prefix}_url_{last_idx}"]
            if f"{key_prefix}_anchor_{last_idx}" in st.session_state:
                del st.session_state[f"{key_prefix}_anchor_{last_idx}"]
            
            # Decrementar contador
            st.session_state[count_key] = max(1, current_count - 1)
        
        st.session_state[delete_key] = None
        st.rerun()
    
    current_count = st.session_state[count_key]
    links = []
    
    st.markdown(f"**{label}** (máx. {max_links})")
    
    for i in range(current_count):
        col1, col2, col3 = st.columns([5, 4, 1])
        
        with col1:
            url = st.text_input(
                label=f"URL {i+1}",
                key=f"{key_prefix}_url_{i}",
                placeholder="https://www.pccomponentes.com/...",
                label_visibility="collapsed"
            )
        
        with col2:
            anchor = st.text_input(
                label=f"Anchor {i+1}",
                key=f"{key_prefix}_anchor_{i}",
                placeholder="Texto del enlace (anchor)",
                label_visibility="collapsed"
            )
        
        with col3:
            if current_count > 1:
                if st.button("🗑️", key=f"{key_prefix}_del_{i}", help="Eliminar"):
                    st.session_state[delete_key] = i
                    st.rerun()
        
        if url and url.strip():
            validated = validate_url(url.strip())
            if validated.is_valid:
                links.append(LinkWithAnchor(
                    url=validated.value,
                    anchor=anchor.strip() if anchor else "",
                    link_type=link_type
                ))
    
    # Botón añadir
    if current_count < max_links:
        if st.button(f"➕ Añadir enlace", key=f"{key_prefix}_add"):
            st.session_state[count_key] = current_count + 1
            st.rerun()
    
    return links


def render_guiding_questions(arquetipo_code: str, key_prefix: str = "guiding") -> Dict[str, str]:
    """Renderiza preguntas guía del arquetipo en un expander."""
    questions = get_guiding_questions(arquetipo_code)
    
    if not questions:
        return {}
    
    arq = get_arquetipo(arquetipo_code)
    arq_name = arq.get('name', arquetipo_code) if arq else arquetipo_code
    
    with st.expander(f"💡 Briefing: {arq_name}", expanded=False):
        st.caption("Responde estas preguntas para guiar mejor la generación del contenido")
        
        answers = {}
        for i, question in enumerate(questions):
            answer = st.text_area(
                label=question,
                key=f"{key_prefix}_{i}",
                height=80,
                placeholder="Tu respuesta...",
                label_visibility="visible"
            )
            if answer and answer.strip():
                answers[question] = answer.strip()
        
        return answers


def render_gsc_date_warning() -> None:
    """Muestra aviso si los datos de GSC están desactualizados."""
    if not _gsc_available:
        return
    
    try:
        gsc_date = get_gsc_data_date()
        if gsc_date:
            if is_gsc_data_stale(GSC_DATA_WARNING_DAYS):
                days_old = (datetime.now() - gsc_date).days
                st.warning(
                    f"⚠️ Datos GSC de hace {days_old} días ({gsc_date.strftime('%d/%m/%Y')}). "
                    f"Considera actualizar para mejor análisis.",
                    icon="📅"
                )
            else:
                st.caption(f"📅 Datos GSC: {gsc_date.strftime('%d/%m/%Y')}")
    except Exception:
        pass


def _render_cannibalization_check(keyword: str) -> None:
    """Renderiza check de canibalización/cobertura para una keyword."""
    if not _gsc_available or not keyword:
        return
    
    try:
        # Usar la nueva función que busca en el CSV de keywords
        summary = get_content_coverage_summary(keyword)
        
        if summary.get('has_coverage'):
            exact = summary.get('exact_match')
            partial = summary.get('partial_matches', [])[:3]
            total = summary.get('total_urls', 0)
            
            # Determinar color según gravedad
            if exact:
                bg_color = "#fff3cd"  # Amarillo - coincidencia exacta
                border_color = "#ffc107"
                icon = "⚠️"
            else:
                bg_color = "#d1ecf1"  # Azul claro - solo parciales
                border_color = "#17a2b8"
                icon = "ℹ️"
            
            with st.container():
                st.markdown(
                    f"""<div style="background-color:{bg_color};padding:10px;border-radius:5px;border-left:4px solid {border_color};margin:10px 0;">
                    <strong>{icon} Contenido existente detectado</strong><br>
                    <small>Se encontraron <b>{total}</b> URLs con contenido relacionado:</small>
                    </div>""",
                    unsafe_allow_html=True
                )
                
                # Mostrar coincidencia exacta primero
                if exact:
                    url = exact.get('url', '')
                    clicks = exact.get('clicks', 0)
                    kw = exact.get('keyword', '')
                    st.caption(f"🎯 **Coincidencia exacta:** [{url[:50]}...]({url})")
                    st.caption(f"   Keyword: '{kw}' · {clicks} clicks")
                
                # Mostrar parciales
                for url_data in partial:
                    url = url_data.get('url', '')
                    clicks = url_data.get('clicks', 0)
                    kw = url_data.get('keyword', '')
                    st.caption(f"• [{url[:50]}...]({url}) - '{kw}' · {clicks} clicks")
                
                recommendation = summary.get('recommendation', '')
                if recommendation:
                    st.info(f"💡 {recommendation}")
    except Exception as e:
        logger.debug(f"Error en check canibalización: {e}")


def render_alternative_product_input(key_prefix: str = "alt_product") -> Tuple[str, str]:
    """Renderiza inputs para producto alternativo."""
    st.markdown("Sugiere un producto alternativo para mencionar en el contenido")
    
    col1, col2 = st.columns(2)
    
    with col1:
        alt_url = st.text_input(
            label="URL del producto alternativo",
            key=f"{key_prefix}_url",
            placeholder="https://www.pccomponentes.com/producto-alternativo"
        )
    
    with col2:
        alt_name = st.text_input(
            label="Nombre del producto",
            key=f"{key_prefix}_name",
            placeholder="Ej: ASUS ROG Strix..."
        )
    
    return alt_url.strip() if alt_url else "", alt_name.strip() if alt_name else ""


def render_competitor_urls_input(key: str = "competitor_urls") -> Tuple[List[str], Optional[str]]:
    """Renderiza input para URLs de competidores."""
    st.markdown("##### 🏆 URLs de Competencia")
    st.caption("Añade URLs de artículos competidores para análisis (máx. 5)")
    
    urls_text = st.text_area(
        label="URLs de competidores",
        key=key,
        height=100,
        placeholder="https://competidor1.com/articulo\nhttps://competidor2.com/articulo",
        label_visibility="collapsed"
    )
    
    if urls_text:
        result = validate_competitor_urls(urls_text)
        if result.value:
            st.caption(f"✅ {len(result.value)} URLs válidas de competencia")
        return result.value, None
    return [], None


def render_additional_instructions(key: str = "additional_instructions") -> str:
    """Renderiza área de instrucciones adicionales."""
    instructions = st.text_area(
        label="Instrucciones adicionales para el generador",
        key=key,
        height=100,
        placeholder="Ej: Enfócate en el rendimiento gaming, menciona la garantía extendida..."
    )
    return instructions.strip() if instructions else ""


def render_visual_elements_selector(key_prefix: str = "visual_elem") -> List[str]:
    """
    Renderiza checkboxes para seleccionar elementos visuales a incluir.
    
    Args:
        key_prefix: Prefijo para las keys de los checkboxes
        
    Returns:
        Lista de elementos visuales seleccionados
    """
    st.markdown("**Selecciona los elementos visuales a incluir:**")
    st.caption("Estos elementos se generarán con los estilos CSS de PcComponentes")
    
    # Definir elementos disponibles con descripción
    elements_config = {
        'toc': {
            'label': '📑 Tabla de Contenidos (TOC)',
            'description': 'Navegación interna del artículo',
            'default': True
        },
        'table': {
            'label': '📊 Tabla Comparativa',
            'description': 'Tabla para comparar productos o características',
            'default': False
        },
        'callout': {
            'label': '💡 Callouts/Destacados',
            'description': 'Cajas de información destacada',
            'default': False
        },
        'callout_bf': {
            'label': '🔥 Callout Black Friday',
            'description': 'Caja especial para ofertas BF/CM',
            'default': False
        },
        'verdict_box': {
            'label': '✅ Verdict Box',
            'description': 'Caja de veredicto final con estilo premium',
            'default': True
        },
        'grid': {
            'label': '📐 Grid Layout',
            'description': 'Distribución en rejilla para productos',
            'default': False
        },
    }
    
    selected_elements = []
    
    # Crear checkboxes en 2 columnas
    col1, col2 = st.columns(2)
    
    elements_list = list(elements_config.items())
    
    for i, (elem_id, elem_config) in enumerate(elements_list):
        target_col = col1 if i % 2 == 0 else col2
        with target_col:
            is_selected = st.checkbox(
                elem_config['label'],
                value=elem_config['default'],
                key=f"{key_prefix}_{elem_id}",
                help=elem_config['description']
            )
            if is_selected:
                selected_elements.append(elem_id)
    
    # Mostrar preview de elementos seleccionados
    if selected_elements:
        with st.expander("👁️ Preview de estilos seleccionados", expanded=False):
            for elem in selected_elements:
                st.markdown(f"**{elements_config[elem]['label']}**")
                if elem == 'toc':
                    st.code('''<nav class="toc">
    <p class="toc__title">En este artículo</p>
    <ol class="toc__list">...</ol>
</nav>''', language="html")
                elif elem == 'table':
                    st.code('''<table>
    <thead><tr><th>Columna 1</th><th>Columna 2</th></tr></thead>
    <tbody><tr><td>Dato 1</td><td>Dato 2</td></tr></tbody>
</table>''', language="html")
                elif elem == 'callout':
                    st.code('<div class="callout"><p><strong>💡 Importante:</strong> ...</p></div>', language="html")
                elif elem == 'callout_bf':
                    st.code('<div class="callout-bf"><p>🔥 <strong>OFERTA BLACK FRIDAY</strong> 🔥</p></div>', language="html")
                elif elem == 'verdict_box':
                    st.code('<div class="verdict-box"><h2>Veredicto Final</h2><p>...</p></div>', language="html")
                elif elem == 'grid':
                    st.code('<div class="grid-layout"><div class="grid-item">...</div></div>', language="html")
    
    return selected_elements


# ============================================================================
# VALIDACIÓN DE ERRORES COMPACTA
# ============================================================================

def render_validation_errors(errors: List[str]) -> None:
    """Renderiza errores de validación de forma compacta."""
    if not errors:
        return
    
    error_html = "<div style='background-color:#f8d7da;border:1px solid #f5c6cb;border-radius:5px;padding:10px;margin:10px 0;'>"
    error_html += "<span style='color:#721c24;font-weight:bold;font-size:14px;'>⚠️ Corrige los siguientes errores:</span><ul style='margin:5px 0;padding-left:20px;color:#721c24;font-size:13px;'>"
    
    for e in errors:
        error_html += f"<li>{e}</li>"
    
    error_html += "</ul></div>"
    
    st.markdown(error_html, unsafe_allow_html=True)


# ============================================================================
# FORMULARIO PRINCIPAL
# ============================================================================

def render_main_form(mode: str = "new") -> Optional[FormData]:
    """Renderiza el formulario principal completo."""
    errors = []
    
    st.markdown("### 📝 Configuración de Generación")
    
    # Fecha GSC
    render_gsc_date_warning()
    
    # Fila 1: Keyword y Arquetipo
    col1, col2 = st.columns(2)
    with col1:
        keyword, keyword_error = render_keyword_input(key="main_keyword", required=True)
        if keyword_error and keyword == "":
            errors.append(keyword_error)
        
        arquetipo = render_arquetipo_selector(key="main_arquetipo")
    
    with col2:
        # URL del producto con botón para obtener datos via n8n
        pdp_url, pdp_data, url_error = render_product_url_with_fetch(key="main_pdp", required=False)
        if url_error:
            errors.append(url_error)
        
        target_length = render_length_slider(key="main_length", arquetipo_code=arquetipo)
    
    # Preguntas guía
    guiding_answers = render_guiding_questions(arquetipo, key_prefix="main_guiding")
    
    # Enlaces internos con anchor
    with st.expander("🔗 Enlaces Internos", expanded=False):
        internal_links = render_links_with_anchors(
            key_prefix="main_internal",
            label="Enlaces Internos",
            link_type="internal",
            max_links=10
        )
    
    # Enlaces PDP con anchor
    with st.expander("🛒 Enlaces a PDPs", expanded=False):
        pdp_links = render_links_with_anchors(
            key_prefix="main_pdp",
            label="Enlaces a Productos",
            link_type="pdp",
            max_links=5
        )
    
    # Producto alternativo
    with st.expander("🔄 Producto Alternativo", expanded=False):
        alt_url, alt_name = render_alternative_product_input(key_prefix="main_alt")
    
    # Competidores (solo rewrite)
    competitor_urls = []
    if mode == "rewrite":
        with st.expander("🏆 Análisis de Competencia", expanded=True):
            competitor_urls, _ = render_competitor_urls_input(key="main_competitors")
    
    # Instrucciones adicionales
    with st.expander("📝 Instrucciones Adicionales", expanded=False):
        additional_instructions = render_additional_instructions(key="main_instructions")
    
    # Elementos visuales (checkboxes)
    with st.expander("🎨 Elementos Visuales", expanded=False):
        visual_elements = render_visual_elements_selector(key_prefix="main_visual")
    
    # Mostrar errores de forma compacta
    if errors:
        render_validation_errors(errors)
        return None
    
    return FormData(
        keyword=keyword,
        pdp_url=pdp_url or None,
        pdp_data=pdp_data,  # Datos del producto obtenidos via n8n
        target_length=target_length,
        arquetipo=arquetipo,
        mode=mode,
        competitor_urls=competitor_urls or None,
        internal_links=internal_links or None,
        pdp_links=pdp_links or None,
        additional_instructions=additional_instructions or None,
        guiding_answers=guiding_answers or None,
        alternative_product_url=alt_url,
        alternative_product_name=alt_name,
        visual_elements=visual_elements or None
    )


# ============================================================================
# FUNCIÓN PRINCIPAL PARA APP.PY
# ============================================================================

def render_content_inputs() -> Tuple[bool, Dict[str, Any]]:
    """
    Renderiza inputs y retorna configuración.
    Esta es la función que app.py importa.
    
    NOTA: El selector de modo está en app.py (render_app_header), NO aquí.
    Esta función solo maneja el modo 'new'. El modo 'rewrite' usa render_rewrite_section().
    
    NO incluye botón de generación - ese está en app.py para centralizar la lógica.
    
    Returns:
        Tuple[bool, Dict]: (is_valid, config) donde is_valid indica si el formulario
        está completo y config contiene los datos formateados.
    """
    # El modo siempre es 'new' aquí - app.py maneja el routing
    mode = 'new'
    
    # Formulario principal
    form_data = render_main_form(mode=mode)
    
    # Si no hay datos válidos, retornar False
    if form_data is None:
        return False, {}
    
    # Formatear enlaces internos
    internal_links_fmt = []
    if form_data.internal_links:
        for link in form_data.internal_links:
            internal_links_fmt.append({
                'url': link.url,
                'anchor': link.anchor,
                'type': 'internal'
            })
    
    # Formatear enlaces PDP
    pdp_links_fmt = []
    if form_data.pdp_links:
        for link in form_data.pdp_links:
            pdp_links_fmt.append({
                'url': link.url,
                'anchor': link.anchor,
                'type': 'pdp'
            })
    
    # Formatear contexto de preguntas guía
    context_from_questions = ""
    if form_data.guiding_answers:
        parts = [f"**{q}**\n{a}" for q, a in form_data.guiding_answers.items()]
        context_from_questions = "\n\n".join(parts)
    
    # Construir config
    # Combinar todos los enlaces en una lista única para el prompt
    all_links = internal_links_fmt + pdp_links_fmt
    
    config = {
        'keyword': form_data.keyword,
        'pdp_url': form_data.pdp_url,
        'pdp_data': form_data.pdp_data,  # Datos del producto obtenidos via n8n
        'target_length': form_data.target_length,
        'arquetipo_codigo': form_data.arquetipo,
        'mode': form_data.mode,
        'competitor_urls': form_data.competitor_urls or [],
        'internal_links': internal_links_fmt,
        'pdp_links': pdp_links_fmt,
        'links': all_links,  # Lista combinada para el prompt
        'additional_instructions': form_data.additional_instructions or '',
        'guiding_context': context_from_questions,
        'alternative_product': {
            'url': form_data.alternative_product_url or '',
            'name': form_data.alternative_product_name or ''
        } if form_data.alternative_product_url else None,
        'visual_elements': form_data.visual_elements or [],  # Elementos visuales seleccionados
    }
    
    return True, config


# ============================================================================
# UTILIDADES ADICIONALES
# ============================================================================

def get_form_summary(form_data: FormData) -> Dict[str, str]:
    """Genera resumen del formulario para mostrar."""
    return {
        'Keyword': form_data.keyword,
        'URL': form_data.pdp_url or 'No especificada',
        'Longitud': f"{form_data.target_length} palabras",
        'Arquetipo': form_data.arquetipo,
        'Modo': 'Nuevo' if form_data.mode == 'new' else 'Reescritura',
        'Enlaces internos': str(len(form_data.internal_links or [])),
        'Enlaces PDP': str(len(form_data.pdp_links or [])),
    }


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    # Versión
    '__version__',
    # Excepciones
    'InputValidationError', 'KeywordValidationError', 'URLValidationError',
    'LengthValidationError', 'LinksValidationError', 'ArquetipoValidationError',
    # Enums y clases
    'InputMode', 'LinkType', 'LinkWithAnchor', 'ValidationResult', 'FormData',
    # Validación
    'validate_keyword', 'validate_url', 'validate_length', 'validate_arquetipo',
    'validate_html_content', 'validate_links_list', 'validate_competitor_urls',
    # Estado
    'get_form_value', 'save_form_data', 'clear_form_data',
    # Componentes UI
    'render_keyword_input', 'render_url_input', 'render_length_slider',
    'render_arquetipo_selector', 'render_mode_selector', 'render_html_input',
    'render_links_with_anchors', 'render_guiding_questions',
    'render_gsc_date_warning', 'render_alternative_product_input',
    'render_competitor_urls_input', 'render_additional_instructions',
    'render_validation_errors',
    # Formulario principal
    'render_main_form', 'render_content_inputs',
    # Utilidades
    'get_form_summary',
]
