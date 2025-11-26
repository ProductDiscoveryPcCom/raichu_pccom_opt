"""
UI Inputs - PcComponentes Content Generator
Versión 4.2.0

Módulo de componentes de entrada para la interfaz Streamlit.
Incluye validación robusta, manejo de errores específicos,
y renderizado de formularios de entrada.

Este módulo proporciona:
- Componentes de input reutilizables
- Validación de datos de entrada
- Manejo de errores específico por tipo de input
- Gestión de estado del formulario

Autor: PcComponentes - Product Discovery & Content
"""

import re
import streamlit as st
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass
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

__version__ = "4.2.0"

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

# Mensajes de error
ERROR_MESSAGES = {
    'keyword_empty': 'La keyword no puede estar vacía',
    'keyword_too_short': f'La keyword debe tener al menos {MIN_KEYWORD_LENGTH} caracteres',
    'keyword_too_long': f'La keyword no puede exceder {MAX_KEYWORD_LENGTH} caracteres',
    'keyword_invalid_chars': 'La keyword contiene caracteres no permitidos',
    'url_empty': 'La URL no puede estar vacía',
    'url_invalid_format': 'El formato de la URL no es válido',
    'url_too_long': f'La URL no puede exceder {MAX_URL_LENGTH} caracteres',
    'url_not_pccomponentes': 'La URL debe ser de PcComponentes',
    'length_out_of_range': f'La longitud debe estar entre {MIN_CONTENT_LENGTH} y {MAX_CONTENT_LENGTH}',
    'links_invalid_format': 'El formato de los enlaces no es válido',
    'competitors_limit': f'Máximo {MAX_COMPETITORS} URLs de competidores',
}


# ============================================================================
# EXCEPCIONES PERSONALIZADAS
# ============================================================================

class InputValidationError(Exception):
    """Excepción base para errores de validación de inputs."""
    
    def __init__(self, message: str, field: str, value: Any = None):
        super().__init__(message)
        self.message = message
        self.field = field
        self.value = value
    
    def __str__(self):
        return f"[{self.field}] {self.message}"


class KeywordValidationError(InputValidationError):
    """Error de validación de keyword."""
    
    def __init__(self, message: str, value: str = None):
        super().__init__(message, field='keyword', value=value)


class URLValidationError(InputValidationError):
    """Error de validación de URL."""
    
    def __init__(self, message: str, value: str = None, url_type: str = 'url'):
        super().__init__(message, field=url_type, value=value)
        self.url_type = url_type


class LengthValidationError(InputValidationError):
    """Error de validación de longitud."""
    
    def __init__(self, message: str, value: int = None):
        super().__init__(message, field='length', value=value)


class LinksValidationError(InputValidationError):
    """Error de validación de enlaces."""
    
    def __init__(self, message: str, value: Any = None, link_type: str = 'links'):
        super().__init__(message, field=link_type, value=value)
        self.link_type = link_type


class ArquetipoValidationError(InputValidationError):
    """Error de validación de arquetipo."""
    
    def __init__(self, message: str, value: str = None):
        super().__init__(message, field='arquetipo', value=value)


# ============================================================================
# ENUMS Y DATA CLASSES
# ============================================================================

class InputMode(Enum):
    """Modos de entrada disponibles."""
    NEW_CONTENT = "new"
    REWRITE = "rewrite"


class LinkType(Enum):
    """Tipos de enlaces."""
    INTERNAL = "internal"
    PDP = "pdp"
    EXTERNAL = "external"


@dataclass
class ValidationResult:
    """Resultado de una validación."""
    is_valid: bool
    value: Any
    error: Optional[str] = None
    warnings: Optional[List[str]] = None


@dataclass
class FormData:
    """Datos del formulario de entrada."""
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
# FUNCIONES DE VALIDACIÓN ESPECÍFICAS
# ============================================================================

def validate_keyword(keyword: str) -> ValidationResult:
    """
    Valida una keyword de búsqueda.
    
    Args:
        keyword: Keyword a validar
        
    Returns:
        ValidationResult con el resultado de la validación
        
    Raises:
        KeywordValidationError: Si la validación falla (solo en modo estricto)
    """
    warnings = []
    
    # Verificar que no sea None
    if keyword is None:
        return ValidationResult(
            is_valid=False,
            value=None,
            error=ERROR_MESSAGES['keyword_empty']
        )
    
    # Convertir a string y limpiar
    try:
        keyword = str(keyword).strip()
    except (ValueError, TypeError) as e:
        return ValidationResult(
            is_valid=False,
            value=keyword,
            error=f"No se pudo procesar la keyword: {e}"
        )
    
    # Verificar que no esté vacía
    if not keyword:
        return ValidationResult(
            is_valid=False,
            value=keyword,
            error=ERROR_MESSAGES['keyword_empty']
        )
    
    # Verificar longitud mínima
    if len(keyword) < MIN_KEYWORD_LENGTH:
        return ValidationResult(
            is_valid=False,
            value=keyword,
            error=ERROR_MESSAGES['keyword_too_short']
        )
    
    # Verificar longitud máxima
    if len(keyword) > MAX_KEYWORD_LENGTH:
        return ValidationResult(
            is_valid=False,
            value=keyword,
            error=ERROR_MESSAGES['keyword_too_long']
        )
    
    # Verificar caracteres permitidos
    if not KEYWORD_PATTERN.match(keyword):
        return ValidationResult(
            is_valid=False,
            value=keyword,
            error=ERROR_MESSAGES['keyword_invalid_chars']
        )
    
    # Advertencias (no bloquean)
    if len(keyword) < 5:
        warnings.append("Keywords muy cortas pueden dar resultados genéricos")
    
    if keyword.isupper():
        warnings.append("Considera usar minúsculas para mejor legibilidad")
        keyword = keyword.lower()
    
    return ValidationResult(
        is_valid=True,
        value=keyword,
        warnings=warnings if warnings else None
    )


def validate_url(
    url: str,
    require_pccomponentes: bool = False,
    url_type: str = 'url'
) -> ValidationResult:
    """
    Valida una URL.
    
    Args:
        url: URL a validar
        require_pccomponentes: Si True, solo acepta URLs de PcComponentes
        url_type: Tipo de URL para mensajes de error
        
    Returns:
        ValidationResult con el resultado de la validación
    """
    warnings = []
    
    # Verificar que no sea None
    if url is None:
        return ValidationResult(
            is_valid=False,
            value=None,
            error=ERROR_MESSAGES['url_empty']
        )
    
    # Convertir a string y limpiar
    try:
        url = str(url).strip()
    except (ValueError, TypeError) as e:
        return ValidationResult(
            is_valid=False,
            value=url,
            error=f"No se pudo procesar la URL: {e}"
        )
    
    # Verificar que no esté vacía
    if not url:
        return ValidationResult(
            is_valid=False,
            value=url,
            error=ERROR_MESSAGES['url_empty']
        )
    
    # Verificar longitud máxima
    if len(url) > MAX_URL_LENGTH:
        return ValidationResult(
            is_valid=False,
            value=url,
            error=ERROR_MESSAGES['url_too_long']
        )
    
    # Añadir protocolo si falta
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
        warnings.append("Se añadió 'https://' automáticamente")
    
    # Validar formato de URL
    if not URL_PATTERN.match(url):
        return ValidationResult(
            is_valid=False,
            value=url,
            error=ERROR_MESSAGES['url_invalid_format']
        )
    
    # Parsear URL para validaciones adicionales
    try:
        parsed = urlparse(url)
    except ValueError as e:
        return ValidationResult(
            is_valid=False,
            value=url,
            error=f"Error al parsear URL: {e}"
        )
    
    # Verificar dominio de PcComponentes si es requerido
    if require_pccomponentes:
        domain = parsed.netloc.lower()
        if not any(pcc_domain in domain for pcc_domain in PCCOMPONENTES_DOMAINS):
            return ValidationResult(
                is_valid=False,
                value=url,
                error=ERROR_MESSAGES['url_not_pccomponentes']
            )
    
    # Advertencias
    if parsed.scheme == 'http':
        warnings.append("Considera usar HTTPS para mayor seguridad")
    
    return ValidationResult(
        is_valid=True,
        value=url,
        warnings=warnings if warnings else None
    )


def validate_length(length: Union[int, str, float]) -> ValidationResult:
    """
    Valida la longitud objetivo del contenido.
    
    Args:
        length: Longitud a validar (puede ser int, str o float)
        
    Returns:
        ValidationResult con el resultado de la validación
    """
    # Convertir a entero
    try:
        if isinstance(length, str):
            length = int(length.strip())
        elif isinstance(length, float):
            length = int(length)
        else:
            length = int(length)
    except (ValueError, TypeError) as e:
        return ValidationResult(
            is_valid=False,
            value=length,
            error=f"La longitud debe ser un número válido: {e}"
        )
    
    # Verificar rango
    if length < MIN_CONTENT_LENGTH or length > MAX_CONTENT_LENGTH:
        return ValidationResult(
            is_valid=False,
            value=length,
            error=ERROR_MESSAGES['length_out_of_range']
        )
    
    warnings = []
    
    # Advertencias por longitudes extremas
    if length < 800:
        warnings.append("Longitudes menores a 800 palabras pueden resultar en contenido superficial")
    elif length > 3000:
        warnings.append("Longitudes mayores a 3000 palabras pueden requerir más tiempo de generación")
    
    return ValidationResult(
        is_valid=True,
        value=length,
        warnings=warnings if warnings else None
    )


def validate_arquetipo(arquetipo_code: str) -> ValidationResult:
    """
    Valida un código de arquetipo.
    
    Args:
        arquetipo_code: Código del arquetipo (ej: 'GC', 'RV')
        
    Returns:
        ValidationResult con el resultado de la validación
    """
    if not arquetipo_code:
        return ValidationResult(
            is_valid=False,
            value=arquetipo_code,
            error="Debe seleccionar un arquetipo"
        )
    
    arquetipo_code = str(arquetipo_code).strip().upper()
    
    if arquetipo_code not in ARQUETIPOS:
        available = ', '.join(ARQUETIPOS.keys())
        return ValidationResult(
            is_valid=False,
            value=arquetipo_code,
            error=f"Arquetipo '{arquetipo_code}' no válido. Disponibles: {available}"
        )
    
    return ValidationResult(
        is_valid=True,
        value=arquetipo_code
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
        return ValidationResult(
            is_valid=True,
            value=[],
            warnings=None
        )
    
    warnings = []
    valid_links = []
    invalid_links = []
    
    # Separar por líneas
    try:
        lines = links_text.strip().split('\n')
    except AttributeError as e:
        return ValidationResult(
            is_valid=False,
            value=[],
            error=f"Error al procesar enlaces: {e}"
        )
    
    for i, line in enumerate(lines, 1):
        line = line.strip()
        if not line:
            continue
        
        # Validar cada URL
        url_result = validate_url(line, require_pccomponentes=False, url_type=link_type)
        
        if url_result.is_valid:
            valid_links.append(url_result.value)
        else:
            invalid_links.append(f"Línea {i}: {url_result.error}")
    
    # Verificar límite
    if len(valid_links) > max_links:
        return ValidationResult(
            is_valid=False,
            value=valid_links[:max_links],
            error=f"Máximo {max_links} enlaces de tipo {link_type}. Se encontraron {len(valid_links)}."
        )
    
    # Agregar advertencias
    if invalid_links:
        warnings.append(f"Se ignoraron {len(invalid_links)} enlaces inválidos")
        for inv in invalid_links[:3]:  # Mostrar máximo 3
            warnings.append(f"  - {inv}")
        if len(invalid_links) > 3:
            warnings.append(f"  ... y {len(invalid_links) - 3} más")
    
    return ValidationResult(
        is_valid=True,
        value=valid_links,
        warnings=warnings if warnings else None
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
    
    # Verificar que no sean de PcComponentes
    if result.is_valid and result.value:
        warnings = result.warnings or []
        filtered_urls = []
        
        for url in result.value:
            try:
                parsed = urlparse(url)
                domain = parsed.netloc.lower()
                
                if any(pcc in domain for pcc in PCCOMPONENTES_DOMAINS):
                    warnings.append(f"Se excluyó URL de PcComponentes: {url[:50]}...")
                else:
                    filtered_urls.append(url)
            except ValueError:
                filtered_urls.append(url)  # Mantener si no se puede parsear
        
        return ValidationResult(
            is_valid=True,
            value=filtered_urls,
            warnings=warnings if warnings else None
        )
    
    return result


# ============================================================================
# FUNCIONES DE RENDERIZADO DE INPUTS
# ============================================================================

def render_keyword_input(
    key: str = "keyword_input",
    default_value: str = "",
    label: str = "🔑 Keyword Principal",
    help_text: str = "Palabra clave principal para el contenido SEO",
    required: bool = True
) -> Tuple[str, Optional[str]]:
    """
    Renderiza un input de keyword con validación.
    
    Args:
        key: Key única para el widget de Streamlit
        default_value: Valor por defecto
        label: Etiqueta del input
        help_text: Texto de ayuda
        required: Si es obligatorio
        
    Returns:
        Tuple[str, Optional[str]]: (valor, mensaje_error)
    """
    # Obtener valor guardado en estado
    saved_value = get_form_value('keyword', default_value)
    
    # Renderizar input
    keyword = st.text_input(
        label=label,
        value=saved_value,
        key=key,
        help=help_text,
        placeholder="Ej: mejores monitores gaming 2024"
    )
    
    # Validar
    if keyword:
        result = validate_keyword(keyword)
        
        if not result.is_valid:
            st.error(f"❌ {result.error}")
            return keyword, result.error
        
        if result.warnings:
            for warning in result.warnings:
                st.warning(f"⚠️ {warning}")
        
        # Guardar en estado
        save_form_data({'keyword': result.value})
        return result.value, None
    
    elif required:
        return "", "La keyword es obligatoria"
    
    return "", None


def render_url_input(
    key: str = "url_input",
    default_value: str = "",
    label: str = "🔗 URL del PDP",
    help_text: str = "URL de la página de producto de PcComponentes",
    required: bool = False,
    require_pccomponentes: bool = True
) -> Tuple[str, Optional[str]]:
    """
    Renderiza un input de URL con validación.
    
    Args:
        key: Key única para el widget
        default_value: Valor por defecto
        label: Etiqueta del input
        help_text: Texto de ayuda
        required: Si es obligatorio
        require_pccomponentes: Si debe ser URL de PcComponentes
        
    Returns:
        Tuple[str, Optional[str]]: (valor, mensaje_error)
    """
    saved_value = get_form_value('pdp_url', default_value)
    
    url = st.text_input(
        label=label,
        value=saved_value,
        key=key,
        help=help_text,
        placeholder="https://www.pccomponentes.com/..."
    )
    
    if url:
        result = validate_url(url, require_pccomponentes=require_pccomponentes)
        
        if not result.is_valid:
            st.error(f"❌ {result.error}")
            return url, result.error
        
        if result.warnings:
            for warning in result.warnings:
                st.info(f"ℹ️ {warning}")
        
        save_form_data({'pdp_url': result.value})
        return result.value, None
    
    elif required:
        return "", "La URL es obligatoria"
    
    return "", None


def render_length_slider(
    key: str = "length_slider",
    default_value: int = DEFAULT_CONTENT_LENGTH,
    label: str = "📏 Longitud del Contenido (palabras)"
) -> int:
    """
    Renderiza un slider para seleccionar longitud.
    
    Args:
        key: Key única para el widget
        default_value: Valor por defecto
        label: Etiqueta del slider
        
    Returns:
        int: Longitud seleccionada
    """
    saved_value = get_form_value('target_length', default_value)
    
    # Asegurar que el valor esté en rango
    try:
        saved_value = int(saved_value)
        if saved_value < MIN_CONTENT_LENGTH:
            saved_value = MIN_CONTENT_LENGTH
        elif saved_value > MAX_CONTENT_LENGTH:
            saved_value = MAX_CONTENT_LENGTH
    except (ValueError, TypeError):
        saved_value = default_value
    
    length = st.slider(
        label=label,
        min_value=MIN_CONTENT_LENGTH,
        max_value=MAX_CONTENT_LENGTH,
        value=saved_value,
        step=100,
        key=key,
        help=f"Rango: {MIN_CONTENT_LENGTH} - {MAX_CONTENT_LENGTH} palabras"
    )
    
    # Mostrar advertencias
    if length < 800:
        st.caption("⚠️ Contenido corto - puede resultar superficial")
    elif length > 3000:
        st.caption("⚠️ Contenido largo - mayor tiempo de generación")
    
    save_form_data({'target_length': length})
    return length


def render_arquetipo_selector(
    key: str = "arquetipo_selector",
    default_value: str = "GC",
    label: str = "📋 Tipo de Contenido (Arquetipo)"
) -> str:
    """
    Renderiza un selector de arquetipo.
    
    Args:
        key: Key única para el widget
        default_value: Código de arquetipo por defecto
        label: Etiqueta del selector
        
    Returns:
        str: Código del arquetipo seleccionado
    """
    saved_value = get_form_value('arquetipo', default_value)
    
    # Obtener opciones
    try:
        arquetipo_names = get_arquetipo_names()
    except Exception as e:
        logger.error(f"Error al obtener arquetipos: {e}")
        arquetipo_names = {k: v['name'] for k, v in ARQUETIPOS.items()}
    
    # Crear lista de opciones para el selectbox
    options = list(arquetipo_names.keys())
    
    # Encontrar índice del valor guardado
    try:
        default_index = options.index(saved_value) if saved_value in options else 0
    except ValueError:
        default_index = 0
    
    # Renderizar selectbox
    selected = st.selectbox(
        label=label,
        options=options,
        index=default_index,
        format_func=lambda x: f"{x} - {arquetipo_names.get(x, x)}",
        key=key,
        help="Selecciona el tipo de contenido a generar"
    )
    
    save_form_data({'arquetipo': selected})
    return selected


def render_links_textarea(
    key: str = "links_textarea",
    default_value: str = "",
    label: str = "🔗 Enlaces",
    help_text: str = "Un enlace por línea",
    link_type: str = "internal",
    max_links: int = MAX_LINKS_PER_TYPE
) -> Tuple[List[str], Optional[str]]:
    """
    Renderiza un textarea para múltiples enlaces.
    
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
        label="📝 Instrucciones Adicionales (Opcional)",
        value=default_value,
        key=key,
        help="Instrucciones específicas para la generación de contenido",
        placeholder="Ej: Enfocarse en gamers principiantes, mencionar presupuestos bajos...",
        height=80
    )
    
    if instructions:
        # Limpiar y validar longitud
        instructions = instructions.strip()
        
        if len(instructions) > 1000:
            st.warning("⚠️ Las instrucciones son muy largas. Se truncarán a 1000 caracteres.")
            instructions = instructions[:1000]
        
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
    
    # Sección expandible para enlaces
    with st.expander("🔗 Enlaces (Opcional)", expanded=False):
        link_col1, link_col2 = st.columns(2)
        
        with link_col1:
            internal_links, _ = render_links_textarea(
                key="main_internal_links",
                label="Enlaces Internos",
                link_type="internal",
                max_links=5
            )
        
        with link_col2:
            pdp_links, _ = render_links_textarea(
                key="main_pdp_links",
                label="Enlaces a PDPs",
                link_type="pdp",
                max_links=3
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
        internal_links=internal_links if internal_links else None,
        pdp_links=pdp_links if pdp_links else None,
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
# UTILIDADES
# ============================================================================

def clear_form_state() -> None:
    """Limpia el estado del formulario."""
    keys_to_clear = [
        'keyword', 'pdp_url', 'target_length', 'arquetipo', 'mode',
        'competitor_urls', 'internal_links', 'pdp_links', 'additional_instructions'
    ]
    
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]
    
    logger.info("Estado del formulario limpiado")


def get_form_summary(form_data: FormData) -> Dict[str, Any]:
    """
    Obtiene un resumen de los datos del formulario.
    
    Args:
        form_data: Datos del formulario
        
    Returns:
        dict: Resumen para mostrar al usuario
    """
    return {
        'Keyword': form_data.keyword,
        'Longitud objetivo': f"{form_data.target_length} palabras",
        'Arquetipo': f"{form_data.arquetipo} - {ARQUETIPOS.get(form_data.arquetipo, {}).get('name', form_data.arquetipo)}",
        'Modo': 'Nuevo contenido' if form_data.mode == 'new' else 'Reescritura',
        'URL PDP': form_data.pdp_url or 'No especificada',
        'Enlaces internos': len(form_data.internal_links or []),
        'Enlaces PDP': len(form_data.pdp_links or []),
        'URLs competidores': len(form_data.competitor_urls or []),
        'Instrucciones': 'Sí' if form_data.additional_instructions else 'No',
    }


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
    'LengthValidationError',
    'LinksValidationError',
    'ArquetipoValidationError',
    
    # Clases de datos
    'InputMode',
    'LinkType',
    'ValidationResult',
    'FormData',
    
    # Funciones de validación
    'validate_keyword',
    'validate_url',
    'validate_length',
    'validate_arquetipo',
    'validate_links_list',
    'validate_competitor_urls',
    
    # Funciones de renderizado
    'render_keyword_input',
    'render_url_input',
    'render_length_slider',
    'render_arquetipo_selector',
    'render_links_textarea',
    'render_competitor_urls_input',
    'render_additional_instructions',
    'render_main_form',
    'render_mode_selector',
    
    # Utilidades
    'clear_form_state',
    'get_form_summary',
    
    # Constantes
    'ERROR_MESSAGES',
    'MIN_KEYWORD_LENGTH',
    'MAX_KEYWORD_LENGTH',
    'MAX_URL_LENGTH',
    'MAX_LINKS_PER_TYPE',
]
