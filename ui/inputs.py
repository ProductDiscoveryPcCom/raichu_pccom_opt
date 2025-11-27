"""
UI Inputs - PcComponentes Content Generator
Versión 4.3.0

Módulo de componentes de entrada para la interfaz Streamlit.

Autor: PcComponentes - Product Discovery & Content
"""

import re
import streamlit as st
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
from urllib.parse import urlparse
import logging

logger = logging.getLogger(__name__)

# ============================================================================
# CONSTANTES POR DEFECTO
# ============================================================================

DEFAULT_CONTENT_LENGTH = 1500
MIN_CONTENT_LENGTH = 500
MAX_CONTENT_LENGTH = 5000
MAX_COMPETITORS = 5
PCCOMPONENTES_DOMAINS = ['www.pccomponentes.com', 'pccomponentes.com']

try:
    from config.settings import (
        DEFAULT_CONTENT_LENGTH,
        MIN_CONTENT_LENGTH,
        MAX_CONTENT_LENGTH,
        MAX_COMPETITORS,
        PCCOMPONENTES_DOMAINS,
    )
except ImportError as e:
    logger.warning(f"No se pudo importar config.settings: {e}")

# Arquetipos con fallback
ARQUETIPOS = {
    'GC': {'code': 'GC', 'name': 'Guía de Compra'},
    'RV': {'code': 'RV', 'name': 'Review'},
    'CP': {'code': 'CP', 'name': 'Comparativa'},
    'TU': {'code': 'TU', 'name': 'Tutorial'},
    'TP': {'code': 'TP', 'name': 'Top/Ranking'},
}

def get_arquetipo_names():
    return {k: v['name'] for k, v in ARQUETIPOS.items()}

try:
    from config.archetipos import ARQUETIPOS, get_arquetipo, list_arquetipos
    def get_arquetipo_names():
        arquetipos = list_arquetipos()
        return {a['code']: a['name'] for a in arquetipos}
except ImportError as e:
    logger.warning(f"No se pudo importar config.archetipos: {e}")

# State manager con fallbacks
def save_form_data(data): 
    for key, value in data.items():
        st.session_state[key] = value

def get_form_value(key, default=None): 
    return st.session_state.get(key, default)

try:
    from utils.state_manager import save_form_data, get_form_data, get_form_value
except ImportError as e:
    logger.warning(f"No se pudo importar utils.state_manager: {e}")

# ============================================================================
# VERSIÓN Y CONSTANTES
# ============================================================================

__version__ = "4.3.0"

URL_PATTERN = re.compile(
    r'^https?://'
    r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'
    r'localhost|'
    r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
    r'(?::\d+)?'
    r'(?:/?|[/?]\S+)$',
    re.IGNORECASE
)

MIN_KEYWORD_LENGTH = 2
MAX_KEYWORD_LENGTH = 100
MAX_URL_LENGTH = 2000
MAX_LINKS_PER_TYPE = 10

ERROR_MESSAGES = {
    'keyword_empty': 'La keyword es obligatoria',
    'keyword_too_short': f'La keyword debe tener al menos {MIN_KEYWORD_LENGTH} caracteres',
    'keyword_too_long': f'La keyword no puede exceder {MAX_KEYWORD_LENGTH} caracteres',
    'url_invalid': 'La URL no tiene un formato válido',
    'url_not_pccomponentes': 'La URL debe ser de PcComponentes',
    'length_out_of_range': f'La longitud debe estar entre {MIN_CONTENT_LENGTH} y {MAX_CONTENT_LENGTH}',
}

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
    arquetipo: str = 'GC'
    mode: str = 'new'
    competitor_urls: Optional[List[str]] = None
    internal_links: Optional[List[str]] = None
    pdp_links: Optional[List[str]] = None
    additional_instructions: Optional[str] = None

# ============================================================================
# FUNCIONES DE VALIDACIÓN
# ============================================================================

def validate_keyword(keyword: str) -> ValidationResult:
    if not keyword or not keyword.strip():
        return ValidationResult(False, '', ERROR_MESSAGES['keyword_empty'])
    keyword = keyword.strip()
    if len(keyword) < MIN_KEYWORD_LENGTH:
        return ValidationResult(False, keyword, ERROR_MESSAGES['keyword_too_short'])
    if len(keyword) > MAX_KEYWORD_LENGTH:
        return ValidationResult(False, keyword, ERROR_MESSAGES['keyword_too_long'])
    return ValidationResult(True, keyword)

def validate_url(url: str, require_pccomponentes: bool = False) -> ValidationResult:
    if not url or not url.strip():
        return ValidationResult(True, '', None)
    url = url.strip()
    if len(url) > MAX_URL_LENGTH:
        return ValidationResult(False, url, f'URL demasiado larga')
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
    if length < MIN_CONTENT_LENGTH or length > MAX_CONTENT_LENGTH:
        return ValidationResult(False, length, ERROR_MESSAGES['length_out_of_range'])
    return ValidationResult(True, length)

def validate_arquetipo(arquetipo: str) -> ValidationResult:
    if arquetipo not in ARQUETIPOS:
        return ValidationResult(False, arquetipo, f'Arquetipo inválido')
    return ValidationResult(True, arquetipo)

def validate_links_list(links_text: str, link_type: str = 'internal', max_links: int = MAX_LINKS_PER_TYPE) -> ValidationResult:
    if not links_text or not links_text.strip():
        return ValidationResult(True, [])
    lines = [line.strip() for line in links_text.strip().split('\n') if line.strip()]
    valid_links = []
    for line in lines[:max_links]:
        if URL_PATTERN.match(line):
            valid_links.append(line)
    return ValidationResult(True, valid_links)

def validate_competitor_urls(urls_text: str) -> ValidationResult:
    result = validate_links_list(urls_text, 'competitor', MAX_COMPETITORS)
    if result.is_valid and result.value:
        filtered = [u for u in result.value if not any(pcc in urlparse(u).netloc.lower() for pcc in PCCOMPONENTES_DOMAINS)]
        return ValidationResult(True, filtered)
    return result

# ============================================================================
# FUNCIONES DE RENDERIZADO
# ============================================================================

def render_keyword_input(key: str = "keyword_input", default_value: str = "", 
                         label: str = "🔑 Keyword Principal", required: bool = True) -> Tuple[str, Optional[str]]:
    saved_value = get_form_value('keyword', default_value)
    keyword = st.text_input(label=label, value=saved_value, key=key, placeholder="Ej: mejores monitores gaming 2024")
    if keyword:
        result = validate_keyword(keyword)
        if not result.is_valid:
            st.error(f"❌ {result.error}")
            return keyword, result.error
        save_form_data({'keyword': result.value})
        return result.value, None
    elif required:
        return "", "La keyword es obligatoria"
    return "", None

def render_url_input(key: str = "url_input", default_value: str = "", label: str = "🔗 URL del PDP",
                     required: bool = False, require_pccomponentes: bool = True) -> Tuple[str, Optional[str]]:
    saved_value = get_form_value('pdp_url', default_value)
    url = st.text_input(label=label, value=saved_value, key=key, placeholder="https://www.pccomponentes.com/...")
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

def render_length_slider(key: str = "length_slider", default_value: int = DEFAULT_CONTENT_LENGTH) -> int:
    saved_value = get_form_value('target_length', default_value)
    length = st.slider("📏 Longitud (palabras)", MIN_CONTENT_LENGTH, MAX_CONTENT_LENGTH, saved_value, 100, key=key)
    save_form_data({'target_length': length})
    return length

def render_arquetipo_selector(key: str = "arquetipo_selector", default_value: str = "GC") -> str:
    saved_value = get_form_value('arquetipo', default_value)
    arquetipo_names = get_arquetipo_names()
    options = list(arquetipo_names.keys())
    try:
        default_index = options.index(saved_value)
    except ValueError:
        default_index = 0
    arquetipo = st.selectbox("📋 Tipo de Contenido", options, default_index, 
                              format_func=lambda x: f"{x} - {arquetipo_names.get(x, x)}", key=key)
    save_form_data({'arquetipo': arquetipo})
    return arquetipo

def render_links_textarea(key: str = "links_textarea", default_value: str = "", 
                          label: str = "🔗 Enlaces", link_type: str = "internal", max_links: int = 5) -> Tuple[List[str], Optional[str]]:
    links_text = st.text_area(label=label, value=default_value, key=key, height=100,
                               placeholder="https://...\nhttps://...")
    if links_text:
        result = validate_links_list(links_text, link_type, max_links)
        return result.value, None
    return [], None

def render_competitor_urls_input(key: str = "competitor_urls") -> Tuple[List[str], Optional[str]]:
    urls_text = st.text_area("🏆 URLs de Competidores", key=key, height=120,
                              placeholder="https://competidor1.com/articulo\nhttps://...")
    if urls_text:
        result = validate_competitor_urls(urls_text)
        return result.value, None
    return [], None

def render_additional_instructions(key: str = "additional_instructions", default_value: str = "") -> str:
    instructions = st.text_area("📝 Instrucciones Adicionales", value=default_value, key=key, height=80,
                                 placeholder="Ej: Enfocarse en gamers principiantes...")
    if instructions:
        instructions = instructions.strip()[:1000]
        save_form_data({'additional_instructions': instructions})
    return instructions

def render_mode_selector(key: str = "mode_selector") -> str:
    saved_mode = get_form_value('mode', 'new')
    mode = st.radio("Modo de Generación", ['new', 'rewrite'], 
                    index=0 if saved_mode == 'new' else 1,
                    format_func=lambda x: "🆕 Nuevo Contenido" if x == 'new' else "✏️ Reescritura",
                    key=key, horizontal=True)
    save_form_data({'mode': mode})
    return mode

# ============================================================================
# FORMULARIO PRINCIPAL
# ============================================================================

def render_main_form(mode: str = "new") -> Optional[FormData]:
    errors = []
    st.markdown("### 📝 Configuración de Generación")
    
    col1, col2 = st.columns(2)
    with col1:
        keyword, keyword_error = render_keyword_input(key="main_keyword", required=True)
        if keyword_error and keyword == "":
            errors.append(keyword_error)
        target_length = render_length_slider(key="main_length")
    
    with col2:
        arquetipo = render_arquetipo_selector(key="main_arquetipo")
        pdp_url, url_error = render_url_input(key="main_pdp_url", required=False)
        if url_error:
            errors.append(url_error)
    
    with st.expander("🔗 Enlaces (Opcional)", expanded=False):
        c1, c2 = st.columns(2)
        with c1:
            internal_links, _ = render_links_textarea(key="main_internal_links", label="Enlaces Internos")
        with c2:
            pdp_links, _ = render_links_textarea(key="main_pdp_links", label="Enlaces a PDPs", max_links=3)
    
    competitor_urls = []
    if mode == "rewrite":
        with st.expander("🏆 Análisis de Competencia", expanded=True):
            competitor_urls, _ = render_competitor_urls_input(key="main_competitors")
    
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
        additional_instructions=additional_instructions or None
    )

# ============================================================================
# FUNCIÓN PRINCIPAL QUE USA APP.PY
# ============================================================================

def render_content_inputs() -> Tuple[bool, Dict[str, Any]]:
    """
    Renderiza inputs de contenido y retorna configuración.
    Esta es la función que app.py importa.
    """
    form_data = render_main_form(mode="new")
    
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        generate_clicked = st.button("🚀 Generar Contenido", type="primary", 
                                      use_container_width=True, disabled=(form_data is None))
    
    if form_data and generate_clicked:
        config = {
            'keyword': form_data.keyword,
            'pdp_url': form_data.pdp_url,
            'target_length': form_data.target_length,
            'arquetipo_codigo': form_data.arquetipo,
            'mode': form_data.mode,
            'competitor_urls': form_data.competitor_urls or [],
            'internal_links': form_data.internal_links or [],
            'pdp_links': form_data.pdp_links or [],
            'additional_instructions': form_data.additional_instructions or '',
            'objetivo': '',
            'keywords': [],
            'context': '',
            'links': [],
            'producto_alternativo': None,
            'pdp_data': None,
        }
        return True, config
    
    return False, {}

# ============================================================================
# UTILIDADES
# ============================================================================

def clear_form_state() -> None:
    keys = ['keyword', 'pdp_url', 'target_length', 'arquetipo', 'mode',
            'competitor_urls', 'internal_links', 'pdp_links', 'additional_instructions']
    for key in keys:
        if key in st.session_state:
            del st.session_state[key]

def get_form_summary(form_data: FormData) -> Dict[str, Any]:
    return {
        'Keyword': form_data.keyword,
        'Longitud': f"{form_data.target_length} palabras",
        'Arquetipo': form_data.arquetipo,
        'Modo': 'Nuevo' if form_data.mode == 'new' else 'Reescritura',
    }

# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    '__version__',
    'InputValidationError', 'KeywordValidationError', 'URLValidationError',
    'LengthValidationError', 'LinksValidationError', 'ArquetipoValidationError',
    'InputMode', 'LinkType', 'ValidationResult', 'FormData',
    'validate_keyword', 'validate_url', 'validate_length', 'validate_arquetipo',
    'validate_links_list', 'validate_competitor_urls',
    'render_keyword_input', 'render_url_input', 'render_length_slider',
    'render_arquetipo_selector', 'render_links_textarea', 'render_competitor_urls_input',
    'render_additional_instructions', 'render_main_form', 'render_mode_selector',
    'render_content_inputs',
    'clear_form_state', 'get_form_summary',
    'ERROR_MESSAGES', 'MIN_KEYWORD_LENGTH', 'MAX_KEYWORD_LENGTH', 'MAX_URL_LENGTH', 'MAX_LINKS_PER_TYPE',
]
