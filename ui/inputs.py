"""
UI Inputs - PcComponentes Content Generator
Versión 4.4.0

Componentes de entrada para la interfaz Streamlit.
Incluye: validación, anchor text, preguntas guía, producto alternativo,
fecha GSC, análisis de canibalización.

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

logger = logging.getLogger(__name__)

# ============================================================================
# CONSTANTES
# ============================================================================

__version__ = "4.4.0"

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
}

# ============================================================================
# IMPORTS CON FALLBACKS ROBUSTOS
# ============================================================================

# Settings
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
    def get_default_length(code): return ARQUETIPOS.get(code, {}).get('default_length', 1500)
    def get_length_range(code): 
        arq = ARQUETIPOS.get(code, {})
        return (arq.get('min_length', 500), arq.get('max_length', 3000))

# State manager
def _save_form_data_fallback(data):
    for k, v in data.items():
        st.session_state[k] = v

def _get_form_value_fallback(key, default=None):
    return st.session_state.get(key, default)

save_form_data = _save_form_data_fallback
get_form_value = _get_form_value_fallback

try:
    from utils.state_manager import save_form_data, get_form_value
except ImportError:
    pass

# GSC utils
def _get_gsc_data_date_fallback():
    return st.session_state.get('gsc_data_date')

def _check_cannibalization_fallback(keyword):
    return []

get_gsc_data_date = _get_gsc_data_date_fallback
check_cannibalization = _check_cannibalization_fallback

try:
    from utils.gsc_utils import get_gsc_data_date, check_cannibalization
except ImportError:
    pass

# ============================================================================
# EXCEPCIONES
# ============================================================================

class InputValidationError(Exception):
    def __init__(self, message: str, field: str = '', value: Any = None):
        super().__init__(message)
        self.message = message
        self.field = field
        self.value = value

class KeywordValidationError(InputValidationError):
    def __init__(self, message: str, value: str = None):
        super().__init__(message, field='keyword', value=value)

class URLValidationError(InputValidationError):
    def __init__(self, message: str, value: str = None):
        super().__init__(message, field='url', value=value)

class LengthValidationError(InputValidationError):
    def __init__(self, message: str, value: int = None):
        super().__init__(message, field='length', value=value)

class LinksValidationError(InputValidationError):
    def __init__(self, message: str, value: Any = None, link_type: str = 'links'):
        super().__init__(message, field=link_type, value=value)

class ArquetipoValidationError(InputValidationError):
    def __init__(self, message: str, value: str = None):
        super().__init__(message, field='arquetipo', value=value)

# ============================================================================
# DATA CLASSES
# ============================================================================

class InputMode(Enum):
    NEW_CONTENT = "new"
    REWRITE = "rewrite"

class LinkType(Enum):
    INTERNAL = "internal"
    PDP = "pdp"
    EXTERNAL = "external"

@dataclass
class LinkWithAnchor:
    """Enlace con su anchor text."""
    url: str
    anchor: str = ""
    link_type: str = "internal"

@dataclass
class ValidationResult:
    is_valid: bool
    value: Any
    error: Optional[str] = None
    warnings: Optional[List[str]] = None

@dataclass
class FormData:
    keyword: str
    pdp_url: Optional[str] = None
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
    
    if default_value is None:
        default_value = default_len
    
    saved_value = get_form_value('target_length', default_value)
    saved_value = max(min_len, min(max_len, saved_value))
    
    length = st.slider(
        "📏 Longitud (palabras)",
        min_len, max_len, saved_value, 50,
        key=key,
        help=f"Rango recomendado: {min_len}-{max_len} palabras"
    )
    save_form_data({'target_length': length})
    return length

def render_arquetipo_selector(key: str = "arquetipo_selector", default_value: str = "ARQ-1") -> str:
    """Renderiza selector de arquetipo."""
    saved_value = get_form_value('arquetipo', default_value)
    arquetipo_list = list(ARQUETIPOS.keys())
    
    try:
        default_index = arquetipo_list.index(saved_value)
    except ValueError:
        default_index = 0
    
    def format_arq(code):
        arq = ARQUETIPOS.get(code, {})
        name = arq.get('name', code)
        return f"{code} - {name}"
    
    arquetipo = st.selectbox(
        "📋 Tipo de Contenido",
        arquetipo_list,
        default_index,
        format_func=format_arq,
        key=key
    )
    
    arq = ARQUETIPOS.get(arquetipo, {})
    if arq.get('description'):
        st.caption(f"ℹ️ {arq['description']}")
    
    save_form_data({'arquetipo': arquetipo})
    return arquetipo

def render_mode_selector(key: str = "mode_selector") -> str:
    """Renderiza selector de modo."""
    saved_mode = get_form_value('mode', 'new')
    mode = st.radio(
        "Modo de Generación",
        ['new', 'rewrite'],
        index=0 if saved_mode == 'new' else 1,
        format_func=lambda x: "🆕 Nuevo Contenido" if x == 'new' else "✏️ Reescritura",
        key=key,
        horizontal=True
    )
    save_form_data({'mode': mode})
    return mode

def render_additional_instructions(key: str = "additional_instructions", default_value: str = "") -> str:
    """Renderiza textarea para instrucciones adicionales."""
    saved = get_form_value('additional_instructions', default_value)
    instructions = st.text_area(
        "📝 Instrucciones Adicionales",
        value=saved,
        key=key,
        height=80,
        placeholder="Ej: Enfocarse en gamers principiantes..."
    )
    if instructions:
        instructions = instructions.strip()[:1000]
        save_form_data({'additional_instructions': instructions})
    return instructions or ""

def render_competitor_urls_input(key: str = "competitor_urls") -> Tuple[List[str], Optional[str]]:
    """Renderiza input de URLs de competidores."""
    urls_text = st.text_area(
        "🏆 URLs de Competidores",
        key=key,
        height=120,
        placeholder="https://competidor1.com/articulo\nhttps://..."
    )
    if urls_text:
        result = validate_competitor_urls(urls_text)
        return result.value, None
    return [], None

# ============================================================================
# COMPONENTES UI: NUEVAS FUNCIONALIDADES
# ============================================================================

def render_links_with_anchors(
    key_prefix: str = "links",
    label: str = "🔗 Enlaces",
    link_type: str = "internal",
    max_links: int = 5,
    help_text: str = "Añade enlaces con su texto ancla"
) -> List[LinkWithAnchor]:
    """
    Renderiza inputs para enlaces con anchor text editable.
    
    Cada enlace tiene:
    - Campo URL (validado)
    - Campo Anchor text (opcional)
    - Botón eliminar (excepto el primero)
    
    Args:
        key_prefix: Prefijo para las keys de session_state
        label: Etiqueta del bloque
        link_type: Tipo de enlace (internal, pdp, external)
        max_links: Máximo de enlaces permitidos
        help_text: Texto de ayuda
    
    Returns:
        Lista de LinkWithAnchor con los enlaces válidos
    """
    st.markdown(f"**{label}**")
    st.caption(help_text)
    
    # Estado: número de filas de enlaces
    count_key = f"{key_prefix}_count"
    if count_key not in st.session_state:
        st.session_state[count_key] = 1
    
    # Estado: índice a eliminar (para manejar eliminación de forma segura)
    delete_key = f"{key_prefix}_delete_idx"
    if delete_key in st.session_state and st.session_state[delete_key] is not None:
        idx_to_delete = st.session_state[delete_key]
        current_count = st.session_state[count_key]
        
        # Shift de valores hacia arriba
        for j in range(idx_to_delete, current_count - 1):
            next_url = st.session_state.get(f"{key_prefix}_url_{j+1}", "")
            next_anchor = st.session_state.get(f"{key_prefix}_anchor_{j+1}", "")
            st.session_state[f"{key_prefix}_url_{j}"] = next_url
            st.session_state[f"{key_prefix}_anchor_{j}"] = next_anchor
        
        # Limpiar última fila (ya movida)
        last_idx = current_count - 1
        if f"{key_prefix}_url_{last_idx}" in st.session_state:
            del st.session_state[f"{key_prefix}_url_{last_idx}"]
        if f"{key_prefix}_anchor_{last_idx}" in st.session_state:
            del st.session_state[f"{key_prefix}_anchor_{last_idx}"]
        
        # Decrementar contador
        st.session_state[count_key] = max(1, current_count - 1)
        st.session_state[delete_key] = None
        st.rerun()
    
    links_data = []
    current_count = st.session_state[count_key]
    
    for i in range(current_count):
        col1, col2, col3 = st.columns([3, 2, 0.5])
        
        with col1:
            url = st.text_input(
                f"URL {i+1}",
                key=f"{key_prefix}_url_{i}",
                placeholder="https://www.pccomponentes.com/...",
                label_visibility="collapsed"
            )
        
        with col2:
            anchor = st.text_input(
                f"Anchor {i+1}",
                key=f"{key_prefix}_anchor_{i}",
                placeholder="Texto ancla descriptivo",
                label_visibility="collapsed"
            )
        
        with col3:
            # Solo mostrar botón eliminar si no es el primer enlace
            if i > 0:
                if st.button("🗑️", key=f"{key_prefix}_del_{i}", help="Eliminar enlace"):
                    st.session_state[delete_key] = i
                    st.rerun()
            else:
                st.write("")  # Espacio vacío para alinear
        
        # Validar y añadir enlace si URL es válida
        if url and url.strip():
            url_result = validate_url(url)
            if url_result.is_valid and url_result.value:
                links_data.append(LinkWithAnchor(
                    url=url_result.value,
                    anchor=anchor.strip() if anchor else "",
                    link_type=link_type
                ))
    
    # Botón para añadir más enlaces
    if current_count < max_links:
        if st.button(f"➕ Añadir enlace", key=f"{key_prefix}_add"):
            st.session_state[count_key] = current_count + 1
            st.rerun()
    
    return links_data

def render_guiding_questions(arquetipo_code: str, key_prefix: str = "guiding") -> Dict[str, str]:
    """Renderiza preguntas guía del arquetipo en expander."""
    questions = get_guiding_questions(arquetipo_code)
    
    if not questions:
        return {}
    
    answers = {}
    answered_count = 0
    
    with st.expander(f"💡 Preguntas Guía ({len(questions)} preguntas)", expanded=False):
        st.caption("Responde para añadir contexto al contenido (opcional pero recomendado)")
        
        for i, question in enumerate(questions):
            answer_key = f"{key_prefix}_q{i}"
            saved_answer = get_form_value(answer_key, "")
            
            answer = st.text_area(
                question,
                value=saved_answer,
                key=answer_key,
                height=60,
                placeholder="Tu respuesta..."
            )
            
            if answer and answer.strip():
                answers[question] = answer.strip()
                save_form_data({answer_key: answer.strip()})
                answered_count += 1
        
        if answered_count > 0:
            st.success(f"✅ {answered_count}/{len(questions)} preguntas respondidas")
    
    return answers

def render_gsc_date_warning() -> Optional[datetime]:
    """Muestra aviso si los datos de GSC están desactualizados."""
    try:
        gsc_date = get_gsc_data_date()
        
        if gsc_date:
            days_old = (datetime.now() - gsc_date).days
            
            if days_old > GSC_DATA_WARNING_DAYS:
                st.warning(
                    f"⚠️ **Datos GSC desactualizados** "
                    f"({gsc_date.strftime('%d/%m/%Y')} - hace {days_old} días)"
                )
            else:
                st.info(f"📊 Datos GSC: {gsc_date.strftime('%d/%m/%Y')} (hace {days_old} días)")
            
            return gsc_date
        return None
    except Exception as e:
        logger.debug(f"No se pudo obtener fecha GSC: {e}")
        return None

def _render_cannibalization_check(keyword: str) -> None:
    """Muestra alerta si hay posible canibalización."""
    if not keyword:
        return
    
    try:
        existing = check_cannibalization(keyword)
        
        if existing:
            with st.expander(f"⚠️ Posible canibalización ({len(existing)} URLs)", expanded=True):
                st.markdown(f"URLs existentes que posicionan para '{keyword}':")
                
                for item in existing[:5]:
                    url = item.get('url', '')
                    pos = item.get('position', 0)
                    clicks = item.get('clicks', 0)
                    
                    st.markdown(f"- `{url[:60]}...` (Pos: {pos:.1f}, Clicks: {clicks})")
                
                st.info("💡 Considera actualizar contenido existente en lugar de crear nuevo")
    except Exception:
        pass

def render_alternative_product_input(key_prefix: str = "alt_product") -> Tuple[Optional[str], Optional[str]]:
    """Renderiza input para producto alternativo."""
    st.markdown("**🔄 Producto Alternativo**")
    st.caption("Producto del catálogo para sugerir como alternativa")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        url = st.text_input(
            "URL producto alternativo",
            key=f"{key_prefix}_url",
            placeholder="https://www.pccomponentes.com/producto",
            label_visibility="collapsed"
        )
    
    with col2:
        name = st.text_input(
            "Nombre",
            key=f"{key_prefix}_name",
            placeholder="Nombre producto",
            label_visibility="collapsed"
        )
    
    if url and url.strip():
        result = validate_url(url, require_pccomponentes=True)
        if not result.is_valid:
            st.error(f"❌ {result.error}")
            return None, None
        return result.value, name.strip() if name else None
    
    return None, None

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
        pdp_url, url_error = render_url_input(key="main_pdp_url", required=False)
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
    
    if errors:
        st.error("### ❌ Corrige los siguientes errores:")
        for e in errors:
            st.markdown(f"- {e}")
        return None
    
    return FormData(
        keyword=keyword,
        pdp_url=pdp_url or None,
        target_length=target_length,
        arquetipo=arquetipo,
        mode=mode,
        competitor_urls=competitor_urls or None,
        internal_links=internal_links or None,
        pdp_links=pdp_links or None,
        additional_instructions=additional_instructions or None,
        guiding_answers=guiding_answers or None,
        alternative_product_url=alt_url,
        alternative_product_name=alt_name
    )

# ============================================================================
# FUNCIÓN PRINCIPAL PARA APP.PY
# ============================================================================

def render_content_inputs() -> Tuple[bool, Dict[str, Any]]:
    """
    Renderiza inputs y retorna configuración.
    Esta es la función que app.py importa.
    """
    mode = render_mode_selector(key="main_mode")
    form_data = render_main_form(mode=mode)
    
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        generate_clicked = st.button(
            "🚀 Generar Contenido",
            type="primary",
            use_container_width=True,
            disabled=(form_data is None)
        )
    
    if form_data and generate_clicked:
        # Formatear enlaces
        internal_links_fmt = []
        if form_data.internal_links:
            for link in form_data.internal_links:
                internal_links_fmt.append({
                    'url': link.url,
                    'anchor': link.anchor,
                    'type': 'internal'
                })
        
        pdp_links_fmt = []
        if form_data.pdp_links:
            for link in form_data.pdp_links:
                pdp_links_fmt.append({
                    'url': link.url,
                    'anchor': link.anchor,
                    'type': 'pdp'
                })
        
        # Formatear contexto de preguntas
        context_from_questions = ""
        if form_data.guiding_answers:
            parts = [f"**{q}**\n{a}" for q, a in form_data.guiding_answers.items()]
            context_from_questions = "\n\n".join(parts)
        
        config = {
            'keyword': form_data.keyword,
            'pdp_url': form_data.pdp_url,
            'target_length': form_data.target_length,
            'arquetipo_codigo': form_data.arquetipo,
            'mode': form_data.mode,
            'competitor_urls': form_data.competitor_urls or [],
            'internal_links': internal_links_fmt,
            'pdp_links': pdp_links_fmt,
            'links': internal_links_fmt + pdp_links_fmt,
            'additional_instructions': form_data.additional_instructions or '',
            'guiding_answers': form_data.guiding_answers or {},
            'context_from_questions': context_from_questions,
            'producto_alternativo': {
                'url': form_data.alternative_product_url,
                'name': form_data.alternative_product_name
            } if form_data.alternative_product_url else None,
            'objetivo': '',
            'keywords': [],
            'context': context_from_questions,
            'pdp_data': None,
        }
        return True, config
    
    return False, {}

# ============================================================================
# UTILIDADES
# ============================================================================

def clear_form_state() -> None:
    """Limpia el estado del formulario."""
    keys_to_clear = [
        'keyword', 'pdp_url', 'target_length', 'arquetipo', 'mode',
        'competitor_urls', 'additional_instructions'
    ]
    
    for i in range(20):
        keys_to_clear.append(f"main_guiding_q{i}")
    
    for prefix in ['main_internal', 'main_pdp']:
        keys_to_clear.append(f"{prefix}_count")
        for i in range(15):
            keys_to_clear.append(f"{prefix}_url_{i}")
            keys_to_clear.append(f"{prefix}_anchor_{i}")
    
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]

def get_form_summary(form_data: FormData) -> Dict[str, Any]:
    """Retorna resumen del formulario."""
    summary = {
        'Keyword': form_data.keyword,
        'Longitud': f"{form_data.target_length} palabras",
        'Arquetipo': form_data.arquetipo,
        'Modo': 'Nuevo' if form_data.mode == 'new' else 'Reescritura',
    }
    
    if form_data.internal_links:
        summary['Enlaces internos'] = len(form_data.internal_links)
    if form_data.pdp_links:
        summary['Enlaces PDP'] = len(form_data.pdp_links)
    if form_data.guiding_answers:
        summary['Preguntas respondidas'] = len(form_data.guiding_answers)
    if form_data.alternative_product_url:
        summary['Producto alternativo'] = form_data.alternative_product_name or 'Sí'
    
    return summary

# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    '__version__',
    # Excepciones
    'InputValidationError', 'KeywordValidationError', 'URLValidationError',
    'LengthValidationError', 'LinksValidationError', 'ArquetipoValidationError',
    # Clases
    'InputMode', 'LinkType', 'LinkWithAnchor', 'ValidationResult', 'FormData',
    # Validación
    'validate_keyword', 'validate_url', 'validate_length', 'validate_arquetipo',
    'validate_links_list', 'validate_competitor_urls',
    # Componentes básicos
    'render_keyword_input', 'render_url_input', 'render_length_slider',
    'render_arquetipo_selector', 'render_mode_selector',
    'render_additional_instructions', 'render_competitor_urls_input',
    # Nuevas funcionalidades
    'render_links_with_anchors', 'render_guiding_questions',
    'render_gsc_date_warning', 'render_alternative_product_input',
    # Formulario
    'render_main_form', 'render_content_inputs',
    # Utilidades
    'clear_form_state', 'get_form_summary',
    # Constantes
    'ERROR_MESSAGES', 'PCCOMPONENTES_DOMAINS',
]
