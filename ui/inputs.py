"""
UI Inputs - PcComponentes Content Generator
Versión 4.3.0

Módulo de componentes de entrada para la interfaz Streamlit.
Incluye validación robusta, manejo de errores específicos,
y renderizado de formularios de entrada.

Este módulo proporciona:
- Componentes de input reutilizables
- Validación de datos de entrada
- Manejo de errores específico por tipo de input
- Gestión de estado del formulario
- Sistema mejorado de enlaces con tipos

Autor: PcComponentes - Product Discovery & Content
"""

import re
import streamlit as st
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, field
from enum import Enum
from urllib.parse import urlparse
import logging

# Configurar logging
logger = logging.getLogger(__name__)

# ============================================================================
# IMPORTS CON MANEJO DE ERRORES
# ============================================================================

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
    DEFAULT_CONTENT_LENGTH = 1500
    MIN_CONTENT_LENGTH = 500
    MAX_CONTENT_LENGTH = 5000
    MAX_COMPETITORS = 5
    PCCOMPONENTES_DOMAINS = ['www.pccomponentes.com', 'pccomponentes.com']

try:
    from config.archetypes import ARQUETIPOS, get_arquetipo_names
except ImportError as e:
    logger.warning(f"No se pudo importar config.archetypes: {e}")
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
    from utils.state_manager import save_form_data, get_form_data, get_form_value
except ImportError as e:
    logger.warning(f"No se pudo importar utils.state_manager: {e}")
    def save_form_data(data): pass
    def get_form_data(): return {}
    def get_form_value(key, default=None): return default


# ============================================================================
# VERSIÓN Y CONSTANTES
# ============================================================================

__version__ = "4.3.0"

# Patrones de validación
URL_PATTERN = re.compile(
    r'^https?://'  # http:// o https://
    r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # dominio
    r'localhost|'  # localhost
    r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # IP
    r'(?::\d+)?'  # puerto opcional
    r'(?:/?|[/?]\S+)$', re.IGNORECASE
)

KEYWORD_PATTERN = re.compile(r'^[\w\sáéíóúüñÁÉÍÓÚÜÑ\-]+$', re.UNICODE)

# Límites de caracteres
MIN_KEYWORD_LENGTH = 2
MAX_KEYWORD_LENGTH = 100
MAX_URL_LENGTH = 2000
MAX_LINKS_PER_TYPE = 10
MAX_ANCHOR_LENGTH = 150

# Mensajes de error
ERROR_MESSAGES = {
    'keyword_empty': 'La keyword no puede estar vacía',
    'keyword_too_short': f'La keyword debe tener al menos {MIN_KEYWORD_LENGTH} caracteres',
    'keyword_too_long': f'La keyword no puede exceder {MAX_KEYWORD_LENGTH} caracteres',
    'keyword_invalid': 'La keyword contiene caracteres no válidos',
    'url_empty': 'La URL no puede estar vacía',
    'url_invalid_format': 'El formato de la URL no es válido',
    'url_too_long': f'La URL no puede exceder {MAX_URL_LENGTH} caracteres',
    'url_not_pccomponentes': 'La URL debe ser de PcComponentes',
    'links_invalid_format': 'El formato de los enlaces no es válido',
    'anchor_too_long': f'El anchor text no puede exceder {MAX_ANCHOR_LENGTH} caracteres',
}


# ============================================================================
# EXCEPCIONES
# ============================================================================

class InputValidationError(Exception):
    """Excepción base para errores de validación de input."""
    
    def __init__(self, message: str, field: str = None, value: Any = None):
        super().__init__(message)
        self.message = message
        self.field = field
        self.value = value


class KeywordValidationError(InputValidationError):
    """Error de validación de keyword."""
    
    def __init__(self, message: str, value: Any = None):
        super().__init__(message, field='keyword', value=value)


class URLValidationError(InputValidationError):
    """Error de validación de URL."""
    
    def __init__(self, message: str, value: Any = None, url_type: str = 'url'):
        super().__init__(message, field=url_type, value=value)
        self.url_type = url_type


class LinksValidationError(InputValidationError):
    """Error de validación de enlaces."""
    
    def __init__(self, message: str, value: Any = None, link_type: str = 'links'):
        super().__init__(message, field=link_type, value=value)
        self.link_type = link_type


# ============================================================================
# ENUMS Y DATA CLASSES
# ============================================================================

class LinkType(Enum):
    """Tipos de enlaces para el contenido."""
    BLOG = "blog"           # Otro post de blog
    CATEGORY = "category"   # Listado de productos
    PDP = "pdp"             # Ficha de producto


# Configuración de tipos de enlaces para mostrar en UI
LINK_TYPE_CONFIG = {
    LinkType.BLOG: {
        'name': '📝 Post de Blog',
        'description': 'Enlace a otro artículo del blog',
        'icon': '📝',
        'color': '#4A90D9',
    },
    LinkType.CATEGORY: {
        'name': '📂 Listado de Productos',
        'description': 'Enlace a una categoría o listado',
        'icon': '📂',
        'color': '#7CB342',
    },
    LinkType.PDP: {
        'name': '🛒 Ficha de Producto',
        'description': 'Enlace a una página de producto',
        'icon': '🛒',
        'color': '#FF7043',
    },
}


@dataclass
class EnhancedLink:
    """
    Representa un enlace mejorado con contexto.
    
    Attributes:
        url: URL del enlace
        anchor: Texto ancla para el enlace
        link_type: Tipo de enlace (blog, category, pdp)
    """
    url: str
    anchor: str
    link_type: LinkType
    
    def to_dict(self) -> Dict[str, str]:
        """Convierte a diccionario."""
        return {
            'url': self.url,
            'anchor': self.anchor,
            'type': self.link_type.value,
            'type_name': LINK_TYPE_CONFIG[self.link_type]['name'],
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> 'EnhancedLink':
        """Crea desde diccionario."""
        link_type = LinkType(data.get('type', 'blog'))
        return cls(
            url=data.get('url', ''),
            anchor=data.get('anchor', ''),
            link_type=link_type
        )
    
    def format_for_prompt(self) -> str:
        """Formatea el enlace para incluir en prompts."""
        type_desc = {
            LinkType.BLOG: "otro artículo del blog",
            LinkType.CATEGORY: "listado/categoría de productos",
            LinkType.PDP: "ficha de producto",
        }
        return f'- [{self.anchor}]({self.url}) → Tipo: {type_desc[self.link_type]}'


@dataclass
class ValidationResult:
    """Resultado de una validación."""
    is_valid: bool
    value: Any = None
    error: Optional[str] = None
    warnings: List[str] = field(default_factory=list)


@dataclass
class FormData:
    """Datos del formulario de generación."""
    keyword: str
    target_length: int = DEFAULT_CONTENT_LENGTH
    arquetipo: str = 'GC'
    mode: str = 'new'
    pdp_url: Optional[str] = None
    competitor_urls: Optional[List[str]] = None
    # Enlaces mejorados (nuevo sistema)
    enhanced_links: Optional[List[EnhancedLink]] = None
    # Mantener compatibilidad con sistema anterior
    internal_links: Optional[List[str]] = None
    pdp_links: Optional[List[str]] = None
    additional_instructions: Optional[str] = None
    
    def get_links_by_type(self, link_type: LinkType) -> List[EnhancedLink]:
        """Obtiene enlaces filtrados por tipo."""
        if not self.enhanced_links:
            return []
        return [link for link in self.enhanced_links if link.link_type == link_type]
    
    def get_all_links_for_prompt(self) -> str:
        """Formatea todos los enlaces para el prompt."""
        if not self.enhanced_links:
            return ""
        
        sections = []
        
        # Agrupar por tipo
        blog_links = self.get_links_by_type(LinkType.BLOG)
        category_links = self.get_links_by_type(LinkType.CATEGORY)
        pdp_links = self.get_links_by_type(LinkType.PDP)
        
        if blog_links:
            sections.append("**Enlaces a otros artículos del blog:**")
            for link in blog_links:
                sections.append(link.format_for_prompt())
        
        if category_links:
            sections.append("\n**Enlaces a listados/categorías de productos:**")
            for link in category_links:
                sections.append(link.format_for_prompt())
        
        if pdp_links:
            sections.append("\n**Enlaces a fichas de producto:**")
            for link in pdp_links:
                sections.append(link.format_for_prompt())
        
        return "\n".join(sections)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte a diccionario."""
        return {
            'keyword': self.keyword,
            'target_length': self.target_length,
            'arquetipo': self.arquetipo,
            'mode': self.mode,
            'pdp_url': self.pdp_url,
            'competitor_urls': self.competitor_urls,
            'enhanced_links': [link.to_dict() for link in self.enhanced_links] if self.enhanced_links else None,
            'internal_links': self.internal_links,
            'pdp_links': self.pdp_links,
            'additional_instructions': self.additional_instructions,
        }


# ============================================================================
# FUNCIONES DE VALIDACIÓN
# ============================================================================

def validate_keyword(keyword: str, required: bool = True) -> ValidationResult:
    """
    Valida una keyword de búsqueda.
    
    Args:
        keyword: Keyword a validar
        required: Si es obligatoria
        
    Returns:
        ValidationResult con el resultado
    """
    warnings = []
    
    if not keyword or not keyword.strip():
        if required:
            return ValidationResult(
                is_valid=False,
                value="",
                error=ERROR_MESSAGES['keyword_empty']
            )
        return ValidationResult(is_valid=True, value="")
    
    keyword = keyword.strip()
    
    # Validar longitud mínima
    if len(keyword) < MIN_KEYWORD_LENGTH:
        return ValidationResult(
            is_valid=False,
            value=keyword,
            error=ERROR_MESSAGES['keyword_too_short']
        )
    
    # Validar longitud máxima
    if len(keyword) > MAX_KEYWORD_LENGTH:
        return ValidationResult(
            is_valid=False,
            value=keyword,
            error=ERROR_MESSAGES['keyword_too_long']
        )
    
    # Advertencia para keywords muy largas
    if len(keyword) > 60:
        warnings.append("Keywords muy largas pueden afectar el SEO")
    
    return ValidationResult(
        is_valid=True,
        value=keyword,
        warnings=warnings
    )


def validate_url(
    url: str,
    required: bool = False,
    require_pccomponentes: bool = False,
    url_type: str = 'url'
) -> ValidationResult:
    """
    Valida una URL.
    
    Args:
        url: URL a validar
        required: Si es obligatoria
        require_pccomponentes: Si debe ser de PcComponentes
        url_type: Tipo de URL para mensajes
        
    Returns:
        ValidationResult con el resultado
    """
    warnings = []
    
    if not url or not url.strip():
        if required:
            return ValidationResult(
                is_valid=False,
                value="",
                error=ERROR_MESSAGES['url_empty']
            )
        return ValidationResult(is_valid=True, value="")
    
    url = url.strip()
    
    # Añadir https:// si no tiene protocolo
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
        warnings.append("Se añadió https:// automáticamente")
    
    # Validar longitud
    if len(url) > MAX_URL_LENGTH:
        return ValidationResult(
            is_valid=False,
            value=url,
            error=ERROR_MESSAGES['url_too_long']
        )
    
    # Validar formato
    if not URL_PATTERN.match(url):
        return ValidationResult(
            is_valid=False,
            value=url,
            error=ERROR_MESSAGES['url_invalid_format']
        )
    
    # Validar dominio PcComponentes si es requerido
    if require_pccomponentes:
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            
            is_pcc = any(pcc in domain for pcc in PCCOMPONENTES_DOMAINS)
            
            if not is_pcc:
                return ValidationResult(
                    is_valid=False,
                    value=url,
                    error=ERROR_MESSAGES['url_not_pccomponentes']
                )
        except Exception:
            pass
    
    return ValidationResult(
        is_valid=True,
        value=url,
        warnings=warnings
    )


def validate_anchor_text(anchor: str) -> ValidationResult:
    """
    Valida un texto de anchor.
    
    Args:
        anchor: Texto anchor a validar
        
    Returns:
        ValidationResult con el resultado
    """
    if not anchor or not anchor.strip():
        return ValidationResult(
            is_valid=False,
            value="",
            error="El texto ancla no puede estar vacío"
        )
    
    anchor = anchor.strip()
    
    if len(anchor) > MAX_ANCHOR_LENGTH:
        return ValidationResult(
            is_valid=False,
            value=anchor,
            error=ERROR_MESSAGES['anchor_too_long']
        )
    
    warnings = []
    
    # Advertencias SEO
    if len(anchor) < 3:
        warnings.append("Anchor muy corto, considera usar texto más descriptivo")
    
    if anchor.lower() in ['aquí', 'click aquí', 'leer más', 'ver más', 'enlace']:
        warnings.append("Evita anchors genéricos, usa texto descriptivo")
    
    return ValidationResult(
        is_valid=True,
        value=anchor,
        warnings=warnings
    )


def validate_enhanced_link(
    url: str,
    anchor: str,
    link_type: LinkType
) -> ValidationResult:
    """
    Valida un enlace mejorado completo.
    
    Args:
        url: URL del enlace
        anchor: Texto ancla
        link_type: Tipo de enlace
        
    Returns:
        ValidationResult con EnhancedLink si es válido
    """
    warnings = []
    
    # Validar URL
    url_result = validate_url(url, required=True)
    if not url_result.is_valid:
        return url_result
    warnings.extend(url_result.warnings)
    
    # Validar anchor
    anchor_result = validate_anchor_text(anchor)
    if not anchor_result.is_valid:
        return anchor_result
    warnings.extend(anchor_result.warnings)
    
    # Crear enlace
    enhanced_link = EnhancedLink(
        url=url_result.value,
        anchor=anchor_result.value,
        link_type=link_type
    )
    
    return ValidationResult(
        is_valid=True,
        value=enhanced_link,
        warnings=warnings
    )


def validate_links_list(
    links_text: str,
    link_type: str = 'internal',
    max_links: int = MAX_LINKS_PER_TYPE
) -> ValidationResult:
    """
    Valida una lista de enlaces (separados por líneas).
    
    Args:
        links_text: Texto con enlaces separados por líneas
        link_type: Tipo de enlace para mensajes
        max_links: Número máximo de enlaces permitidos
        
    Returns:
        ValidationResult con lista de URLs válidas
    """
    if not links_text or not links_text.strip():
        return ValidationResult(is_valid=True, value=[])
    
    warnings = []
    
    try:
        lines = links_text.strip().split('\n')
    except Exception as e:
        return ValidationResult(
            is_valid=False,
            value=[],
            error=f"Error al procesar enlaces: {e}"
        )
    
    valid_links = []
    invalid_links = []
    
    for i, line in enumerate(lines, 1):
        line = line.strip()
        if not line:
            continue
        
        url_result = validate_url(line, require_pccomponentes=False, url_type=link_type)
        
        if url_result.is_valid:
            valid_links.append(url_result.value)
        else:
            invalid_links.append(f"Línea {i}: {url_result.error}")
    
    # Verificar límite
    if len(valid_links) > max_links:
        return ValidationResult(
            is_valid=True,
            value=valid_links[:max_links],
            error=f"Máximo {max_links} enlaces de tipo {link_type}. Se encontraron {len(valid_links)}."
        )
    
    if invalid_links:
        warnings.append(f"Se ignoraron {len(invalid_links)} enlaces inválidos")
        for inv in invalid_links[:3]:
            warnings.append(f"  {inv}")
        if len(invalid_links) > 3:
            warnings.append(f"  ... y {len(invalid_links) - 3} más")
    
    return ValidationResult(
        is_valid=True,
        value=valid_links,
        warnings=warnings
    )


def validate_competitor_urls(urls_text: str) -> ValidationResult:
    """
    Valida URLs de competidores.
    
    Args:
        urls_text: Texto con URLs separadas por líneas
        
    Returns:
        ValidationResult con lista de URLs válidas
    """
    result = validate_links_list(
        links_text=urls_text,
        link_type='competitor',
        max_links=MAX_COMPETITORS
    )
    
    if not result.is_valid:
        return result
    
    # Verificar que no sean de PcComponentes
    valid_urls = []
    warnings = list(result.warnings)
    
    for url in result.value:
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            
            is_pcc = any(pcc in domain for pcc in PCCOMPONENTES_DOMAINS)
            
            if is_pcc:
                warnings.append(f"Ignorada URL de PcComponentes: {url[:50]}...")
            else:
                valid_urls.append(url)
        except Exception:
            valid_urls.append(url)
    
    return ValidationResult(
        is_valid=True,
        value=valid_urls,
        warnings=warnings
    )


# ============================================================================
# COMPONENTES DE RENDERIZADO
# ============================================================================

def render_keyword_input(
    key: str = "keyword_input",
    default_value: str = "",
    required: bool = True
) -> Tuple[str, Optional[str]]:
    """
    Renderiza input para keyword.
    
    Args:
        key: Key única para el widget
        default_value: Valor por defecto
        required: Si es obligatorio
        
    Returns:
        Tuple[str, Optional[str]]: (keyword, mensaje_error)
    """
    saved_value = get_form_value('keyword', default_value)
    
    label = "🔍 Keyword Principal"
    if required:
        label += " *"
    
    keyword = st.text_input(
        label=label,
        value=saved_value,
        key=key,
        help="Palabra clave principal para optimizar el contenido",
        placeholder="Ej: mejores portátiles gaming 2024"
    )
    
    result = validate_keyword(keyword, required)
    
    if not result.is_valid:
        st.error(f"❌ {result.error}")
        return keyword, result.error
    
    if result.warnings:
        for warning in result.warnings:
            st.warning(f"⚠️ {warning}")
    
    save_form_data({'keyword': result.value})
    return result.value, None


def render_url_input(
    key: str = "url_input",
    default_value: str = "",
    label: str = "🔗 URL",
    required: bool = False,
    require_pccomponentes: bool = False,
    help_text: str = "URL de la página"
) -> Tuple[str, Optional[str]]:
    """
    Renderiza input para URL.
    
    Args:
        key: Key única para el widget
        default_value: Valor por defecto
        label: Etiqueta del input
        required: Si es obligatorio
        require_pccomponentes: Si debe ser de PcComponentes
        help_text: Texto de ayuda
        
    Returns:
        Tuple[str, Optional[str]]: (url, mensaje_error)
    """
    saved_value = get_form_value('pdp_url', default_value)
    
    if required:
        label += " *"
    
    url = st.text_input(
        label=label,
        value=saved_value,
        key=key,
        help=help_text,
        placeholder="https://www.pccomponentes.com/..."
    )
    
    result = validate_url(url, required, require_pccomponentes)
    
    if not result.is_valid:
        st.error(f"❌ {result.error}")
        return url, result.error
    
    if result.warnings:
        for warning in result.warnings:
            st.warning(f"⚠️ {warning}")
    
    if result.value:
        save_form_data({'pdp_url': result.value})
    
    return result.value, None


def render_length_slider(
    key: str = "length_slider",
    default_value: int = DEFAULT_CONTENT_LENGTH
) -> int:
    """
    Renderiza slider para longitud del contenido.
    
    Args:
        key: Key única para el widget
        default_value: Valor por defecto
        
    Returns:
        int: Longitud seleccionada
    """
    saved_value = get_form_value('target_length', default_value)
    
    # Asegurar que el valor esté en rango
    saved_value = max(MIN_CONTENT_LENGTH, min(saved_value, MAX_CONTENT_LENGTH))
    
    length = st.slider(
        label="📏 Longitud Objetivo (palabras)",
        min_value=MIN_CONTENT_LENGTH,
        max_value=MAX_CONTENT_LENGTH,
        value=saved_value,
        step=100,
        key=key,
        help="Número aproximado de palabras para el contenido generado"
    )
    
    # Mostrar indicador visual
    if length < 800:
        st.caption("📄 Contenido corto - ideal para descripciones")
    elif length < 1500:
        st.caption("📝 Contenido medio - ideal para guías básicas")
    elif length < 2500:
        st.caption("📚 Contenido largo - ideal para guías completas")
    else:
        st.caption("📖 Contenido muy extenso - ideal para pilares SEO")
    
    save_form_data({'target_length': length})
    return length


def render_arquetipo_selector(
    key: str = "arquetipo_selector",
    default_value: str = 'GC'
) -> str:
    """
    Renderiza selector de arquetipo de contenido.
    
    Args:
        key: Key única para el widget
        default_value: Valor por defecto
        
    Returns:
        str: Código del arquetipo seleccionado
    """
    saved_value = get_form_value('arquetipo', default_value)
    arquetipo_names = get_arquetipo_names()
    
    options = list(arquetipo_names.keys())
    
    try:
        default_index = options.index(saved_value)
    except ValueError:
        default_index = 0
    
    selected = st.selectbox(
        label="📋 Tipo de Contenido",
        options=options,
        index=default_index,
        format_func=lambda x: f"{arquetipo_names.get(x, x)} ({x})",
        key=key,
        help="Selecciona el tipo de contenido a generar"
    )
    
    save_form_data({'arquetipo': selected})
    return selected


# ============================================================================
# SISTEMA MEJORADO DE ENLACES
# ============================================================================

def _get_links_from_session(key: str = "enhanced_links") -> List[Dict]:
    """Obtiene enlaces del session state."""
    if key not in st.session_state:
        st.session_state[key] = []
    return st.session_state[key]


def _save_links_to_session(links: List[Dict], key: str = "enhanced_links"):
    """Guarda enlaces en session state."""
    st.session_state[key] = links


def _add_link_to_session(
    url: str,
    anchor: str,
    link_type: str,
    key: str = "enhanced_links"
):
    """Añade un enlace al session state."""
    links = _get_links_from_session(key)
    links.append({
        'url': url,
        'anchor': anchor,
        'type': link_type
    })
    _save_links_to_session(links, key)


def _remove_link_from_session(index: int, key: str = "enhanced_links"):
    """Elimina un enlace por índice."""
    links = _get_links_from_session(key)
    if 0 <= index < len(links):
        links.pop(index)
        _save_links_to_session(links, key)


def render_enhanced_links_section(
    key: str = "enhanced_links",
    title: str = "🔗 Enlaces para el Contenido",
    expanded: bool = True
) -> List[EnhancedLink]:
    """
    Renderiza sección mejorada de enlaces con tipos.
    
    Permite añadir múltiples enlaces sin límite, cada uno con:
    - URL del enlace
    - Texto ancla (anchor)
    - Tipo de enlace (blog, listado, producto)
    
    Args:
        key: Key única para el widget
        title: Título de la sección
        expanded: Si el expander está abierto por defecto
        
    Returns:
        List[EnhancedLink]: Lista de enlaces configurados
    """
    with st.expander(title, expanded=expanded):
        st.markdown("""
        <style>
        .link-card {
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 10px;
            border-left: 4px solid #4A90D9;
        }
        .link-type-blog { border-left-color: #4A90D9; }
        .link-type-category { border-left-color: #7CB342; }
        .link-type-pdp { border-left-color: #FF7043; }
        </style>
        """, unsafe_allow_html=True)
        
        st.info("""
        💡 **Añade los enlaces que quieras incluir en el contenido.**
        
        El tipo de enlace ayuda al redactor a entender el contexto y ubicar 
        cada enlace de forma natural en el texto.
        """)
        
        # Formulario para añadir nuevo enlace
        st.markdown("##### ➕ Añadir Nuevo Enlace")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            new_url = st.text_input(
                "URL del enlace",
                key=f"{key}_new_url",
                placeholder="https://www.pccomponentes.com/...",
                label_visibility="collapsed"
            )
        
        with col2:
            link_type_options = {
                'blog': '📝 Post de Blog',
                'category': '📂 Listado de Productos',
                'pdp': '🛒 Ficha de Producto'
            }
            new_type = st.selectbox(
                "Tipo",
                options=list(link_type_options.keys()),
                format_func=lambda x: link_type_options[x],
                key=f"{key}_new_type",
                label_visibility="collapsed"
            )
        
        new_anchor = st.text_input(
            "Texto ancla (anchor text)",
            key=f"{key}_new_anchor",
            placeholder="Ej: mejores monitores gaming, ver producto, guía completa...",
            help="El texto que aparecerá como enlace en el contenido"
        )
        
        # Botón de añadir
        add_col1, add_col2, add_col3 = st.columns([1, 1, 2])
        
        with add_col1:
            if st.button("➕ Añadir Enlace", key=f"{key}_add_btn", type="primary"):
                if new_url and new_anchor:
                    # Validar
                    result = validate_enhanced_link(
                        url=new_url,
                        anchor=new_anchor,
                        link_type=LinkType(new_type)
                    )
                    
                    if result.is_valid:
                        _add_link_to_session(new_url, new_anchor, new_type, key)
                        st.success("✅ Enlace añadido")
                        st.rerun()
                    else:
                        st.error(f"❌ {result.error}")
                else:
                    st.warning("⚠️ Completa URL y texto ancla")
        
        with add_col2:
            if st.button("🗑️ Limpiar Todo", key=f"{key}_clear_btn"):
                _save_links_to_session([], key)
                st.rerun()
        
        st.markdown("---")
        
        # Mostrar enlaces existentes
        links_data = _get_links_from_session(key)
        
        if links_data:
            st.markdown(f"##### 📋 Enlaces Configurados ({len(links_data)})")
            
            for i, link in enumerate(links_data):
                link_type_str = link.get('type', 'blog')
                type_config = LINK_TYPE_CONFIG.get(
                    LinkType(link_type_str),
                    LINK_TYPE_CONFIG[LinkType.BLOG]
                )
                
                with st.container():
                    col1, col2, col3 = st.columns([3, 1, 0.5])
                    
                    with col1:
                        st.markdown(f"""
                        **{type_config['icon']} {link.get('anchor', '')}**  
                        <small style="color: #666;">{link.get('url', '')[:60]}{'...' if len(link.get('url', '')) > 60 else ''}</small>
                        """, unsafe_allow_html=True)
                    
                    with col2:
                        st.caption(type_config['name'])
                    
                    with col3:
                        if st.button("🗑️", key=f"{key}_del_{i}", help="Eliminar enlace"):
                            _remove_link_from_session(i, key)
                            st.rerun()
                    
                    st.markdown("<hr style='margin: 5px 0; opacity: 0.3;'>", unsafe_allow_html=True)
        else:
            st.caption("📭 No hay enlaces configurados. Añade enlaces arriba.")
        
        # Resumen por tipo
        if links_data:
            st.markdown("##### 📊 Resumen")
            
            type_counts = {
                'blog': 0,
                'category': 0,
                'pdp': 0
            }
            
            for link in links_data:
                lt = link.get('type', 'blog')
                if lt in type_counts:
                    type_counts[lt] += 1
            
            cols = st.columns(3)
            
            with cols[0]:
                st.metric("📝 Posts de Blog", type_counts['blog'])
            with cols[1]:
                st.metric("📂 Listados", type_counts['category'])
            with cols[2]:
                st.metric("🛒 Productos", type_counts['pdp'])
    
    # Convertir a objetos EnhancedLink
    enhanced_links = []
    for link in links_data:
        try:
            enhanced_links.append(EnhancedLink(
                url=link.get('url', ''),
                anchor=link.get('anchor', ''),
                link_type=LinkType(link.get('type', 'blog'))
            ))
        except Exception as e:
            logger.warning(f"Error creando EnhancedLink: {e}")
    
    return enhanced_links


def render_links_textarea(
    key: str = "links_textarea",
    default_value: str = "",
    label: str = "🔗 Enlaces",
    help_text: str = "Un enlace por línea",
    link_type: str = "internal",
    max_links: int = MAX_LINKS_PER_TYPE
) -> Tuple[List[str], Optional[str]]:
    """
    Renderiza un textarea para múltiples enlaces (versión simple).
    
    NOTA: Esta función se mantiene para compatibilidad.
    Para nuevas implementaciones usar render_enhanced_links_section().
    
    Args:
        key: Key única para el widget
        default_value: Valor por defecto
        label: Etiqueta del textarea
        help_text: Texto de ayuda
        link_type: Tipo de enlace (internal, pdp, external)
        max_links: Número máximo de enlaces
        
    Returns:
        Tuple[List[str], Optional[str]]: (lista_urls, mensaje_error)
    """
    links_text = st.text_area(
        label=label,
        value=default_value,
        key=key,
        help=f"{help_text} (máximo {max_links})",
        placeholder="https://ejemplo.com/pagina1\nhttps://ejemplo.com/pagina2",
        height=100
    )
    
    if links_text:
        result = validate_links_list(links_text, link_type, max_links)
        
        if not result.is_valid:
            st.error(f"❌ {result.error}")
            return result.value or [], result.error
        
        if result.warnings:
            for warning in result.warnings:
                st.warning(f"⚠️ {warning}")
        
        if result.value:
            st.caption(f"✅ {len(result.value)} enlace(s) válido(s)")
        
        save_form_data({f'{link_type}_links': result.value})
        return result.value, None
    
    return [], None


def render_competitor_urls_input(
    key: str = "competitor_urls",
    default_value: str = ""
) -> Tuple[List[str], Optional[str]]:
    """
    Renderiza input para URLs de competidores.
    
    Args:
        key: Key única para el widget
        default_value: Valor por defecto
        
    Returns:
        Tuple[List[str], Optional[str]]: (lista_urls, mensaje_error)
    """
    st.markdown("##### 🏆 URLs de Competidores")
    st.caption(f"URLs de páginas competidoras a analizar (máximo {MAX_COMPETITORS})")
    
    urls_text = st.text_area(
        label="URLs de competidores",
        value=default_value,
        key=key,
        help="Una URL por línea. No incluir URLs de PcComponentes.",
        placeholder="https://competidor1.com/articulo\nhttps://competidor2.com/guia",
        height=120,
        label_visibility="collapsed"
    )
    
    if urls_text:
        result = validate_competitor_urls(urls_text)
        
        if not result.is_valid:
            st.error(f"❌ {result.error}")
            return result.value or [], result.error
        
        if result.warnings:
            for warning in result.warnings:
                st.warning(f"⚠️ {warning}")
        
        if result.value:
            st.success(f"✅ {len(result.value)} URL(s) de competidores válida(s)")
        
        save_form_data({'competitor_urls': result.value})
        return result.value, None
    
    return [], None


def render_additional_instructions(
    key: str = "additional_instructions",
    default_value: str = ""
) -> str:
    """
    Renderiza textarea para instrucciones adicionales.
    
    Args:
        key: Key única para el widget
        default_value: Valor por defecto
        
    Returns:
        str: Instrucciones adicionales
    """
    instructions = st.text_area(
        label="📝 Instrucciones Adicionales",
        value=default_value,
        key=key,
        help="Instrucciones específicas para la generación",
        placeholder="Ej: Enfocarse en gaming, mencionar ofertas actuales, tono más técnico...",
        height=100
    )
    
    if instructions:
        save_form_data({'additional_instructions': instructions})
    
    return instructions


# ============================================================================
# FORMULARIO COMPLETO
# ============================================================================

def render_main_form(mode: str = "new") -> Optional[FormData]:
    """
    Renderiza el formulario principal completo.
    
    Args:
        mode: Modo de generación ('new' o 'rewrite')
        
    Returns:
        FormData si el formulario es válido, None si hay errores
    """
    errors = []
    
    st.markdown("### 📝 Configuración de Generación")
    
    # Columnas principales
    col1, col2 = st.columns(2)
    
    with col1:
        # Keyword (obligatoria)
        keyword, keyword_error = render_keyword_input(
            key="main_keyword",
            required=True
        )
        if keyword_error and keyword == "":
            errors.append(keyword_error)
        
        # Longitud
        target_length = render_length_slider(key="main_length")
    
    with col2:
        # Arquetipo
        arquetipo = render_arquetipo_selector(key="main_arquetipo")
        
        # URL del PDP (opcional)
        pdp_url, url_error = render_url_input(
            key="main_pdp_url",
            required=False,
            require_pccomponentes=True
        )
        if url_error:
            errors.append(url_error)
    
    # =========================================================================
    # SECCIÓN DE ENLACES MEJORADA
    # =========================================================================
    enhanced_links = render_enhanced_links_section(
        key="main_enhanced_links",
        title="🔗 Paso 5: Enlaces para el Contenido",
        expanded=True
    )
    
    # Competidores (solo en modo rewrite)
    competitor_urls = []
    if mode == "rewrite":
        with st.expander("🏆 Análisis de Competencia", expanded=True):
            competitor_urls, comp_error = render_competitor_urls_input(
                key="main_competitors"
            )
            if comp_error:
                errors.append(comp_error)
    
    # Instrucciones adicionales
    with st.expander("📝 Instrucciones Adicionales", expanded=False):
        additional_instructions = render_additional_instructions(
            key="main_instructions"
        )
    
    # Mostrar errores si existen
    if errors:
        st.markdown("---")
        st.error("### ❌ Por favor corrige los siguientes errores:")
        for error in errors:
            st.markdown(f"- {error}")
        return None
    
    # Retornar datos del formulario
    return FormData(
        keyword=keyword,
        pdp_url=pdp_url if pdp_url else None,
        target_length=target_length,
        arquetipo=arquetipo,
        mode=mode,
        competitor_urls=competitor_urls if competitor_urls else None,
        enhanced_links=enhanced_links if enhanced_links else None,
        additional_instructions=additional_instructions if additional_instructions else None
    )


def render_mode_selector(key: str = "mode_selector") -> str:
    """
    Renderiza selector de modo (nuevo contenido vs reescritura).
    
    Args:
        key: Key única para el widget
        
    Returns:
        str: Modo seleccionado ('new' o 'rewrite')
    """
    saved_mode = get_form_value('mode', 'new')
    
    mode = st.radio(
        label="Modo de Generación",
        options=['new', 'rewrite'],
        index=0 if saved_mode == 'new' else 1,
        format_func=lambda x: "🆕 Nuevo Contenido" if x == 'new' else "✏️ Reescritura con Análisis",
        key=key,
        horizontal=True
    )
    
    save_form_data({'mode': mode})
    return mode


# ============================================================================
# FUNCIONES DE UTILIDAD
# ============================================================================

def clear_form_data():
    """Limpia todos los datos del formulario."""
    keys_to_clear = [
        'keyword', 'pdp_url', 'target_length', 'arquetipo', 'mode',
        'competitor_urls', 'enhanced_links', 'additional_instructions'
    ]
    
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]
    
    # Limpiar enlaces mejorados
    if 'main_enhanced_links' in st.session_state:
        del st.session_state['main_enhanced_links']
    
    save_form_data({})


def get_form_summary(form_data: FormData) -> Dict[str, Any]:
    """
    Genera resumen del formulario para mostrar.
    
    Args:
        form_data: Datos del formulario
        
    Returns:
        Dict con resumen
    """
    arquetipo_names = get_arquetipo_names()
    
    # Contar enlaces por tipo
    links_by_type = {
        'blog': 0,
        'category': 0,
        'pdp': 0
    }
    
    if form_data.enhanced_links:
        for link in form_data.enhanced_links:
            lt = link.link_type.value
            if lt in links_by_type:
                links_by_type[lt] += 1
    
    total_links = sum(links_by_type.values())
    
    return {
        'Keyword': form_data.keyword,
        'Tipo': arquetipo_names.get(form_data.arquetipo, form_data.arquetipo),
        'Longitud': f"{form_data.target_length} palabras",
        'URL PDP': form_data.pdp_url or 'No especificada',
        'Total Enlaces': total_links,
        'Enlaces Blog': links_by_type['blog'],
        'Enlaces Listados': links_by_type['category'],
        'Enlaces Productos': links_by_type['pdp'],
        'URLs Competidores': len(form_data.competitor_urls or []),
        'Modo': 'Nuevo' if form_data.mode == 'new' else 'Reescritura',
    }


def format_links_for_prompt(enhanced_links: List[EnhancedLink]) -> str:
    """
    Formatea los enlaces mejorados para incluir en el prompt.
    
    Args:
        enhanced_links: Lista de enlaces mejorados
        
    Returns:
        String formateado para el prompt
    """
    if not enhanced_links:
        return ""
    
    sections = []
    
    # Agrupar por tipo
    blog_links = [l for l in enhanced_links if l.link_type == LinkType.BLOG]
    category_links = [l for l in enhanced_links if l.link_type == LinkType.CATEGORY]
    pdp_links = [l for l in enhanced_links if l.link_type == LinkType.PDP]
    
    sections.append("## ENLACES A INCLUIR EN EL CONTENIDO\n")
    sections.append("Incluye estos enlaces de forma natural en el texto, respetando el tipo y contexto de cada uno:\n")
    
    if blog_links:
        sections.append("### Enlaces a otros artículos del blog:")
        sections.append("Estos enlaces deben aparecer en contextos donde se mencionen temas relacionados, guías complementarias o información adicional.\n")
        for link in blog_links:
            sections.append(f"- **Anchor:** \"{link.anchor}\"")
            sections.append(f"  **URL:** {link.url}")
            sections.append("")
    
    if category_links:
        sections.append("### Enlaces a listados/categorías de productos:")
        sections.append("Estos enlaces deben aparecer cuando se mencionen categorías de productos, comparativas generales o recomendaciones de explorar más opciones.\n")
        for link in category_links:
            sections.append(f"- **Anchor:** \"{link.anchor}\"")
            sections.append(f"  **URL:** {link.url}")
            sections.append("")
    
    if pdp_links:
        sections.append("### Enlaces a fichas de producto:")
        sections.append("Estos enlaces deben aparecer cuando se mencione un producto específico, en recomendaciones concretas o en CTAs de compra.\n")
        for link in pdp_links:
            sections.append(f"- **Anchor:** \"{link.anchor}\"")
            sections.append(f"  **URL:** {link.url}")
            sections.append("")
    
    return "\n".join(sections)


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    # Versión
    '__version__',
    
    # Excepciones
    'InputValidationError',
    'KeywordValidationError',
    'URLValidationError',
    'LinksValidationError',
    
    # Enums y Data Classes
    'LinkType',
    'EnhancedLink',
    'ValidationResult',
    'FormData',
    'LINK_TYPE_CONFIG',
    
    # Funciones de validación
    'validate_keyword',
    'validate_url',
    'validate_anchor_text',
    'validate_enhanced_link',
    'validate_links_list',
    'validate_competitor_urls',
    
    # Componentes de renderizado
    'render_keyword_input',
    'render_url_input',
    'render_length_slider',
    'render_arquetipo_selector',
    'render_enhanced_links_section',
    'render_links_textarea',
    'render_competitor_urls_input',
    'render_additional_instructions',
    
    # Formularios
    'render_main_form',
    'render_mode_selector',
    
    # Utilidades
    'clear_form_data',
    'get_form_summary',
    'format_links_for_prompt',
]
