"""
Config Module - PcComponentes Content Generator
Versión 4.2.0

Paquete de configuración que centraliza todos los settings,
constantes de marca, y arquetipos de contenido.

Este __init__.py exporta todas las configuraciones necesarias
para facilitar las importaciones en el resto de la aplicación.

Uso:
    from config import CLAUDE_API_KEY, DEFAULT_MODEL, ARQUETIPOS
    from config import CSS_CMS_COMPATIBLE, BRAND_TONE

IMPORTANTE: Este módulo usa CLAUDE_API_KEY como nombre estándar.
NO usar ANTHROPIC_API_KEY en código nuevo.

Autor: PcComponentes - Product Discovery & Content
"""

import logging

# Configurar logger
logger = logging.getLogger(__name__)

# ============================================================================
# VERSIÓN DEL MÓDULO
# ============================================================================

__version__ = "4.2.0"


# ============================================================================
# IMPORTS DE SETTINGS
# ============================================================================

try:
    from config.settings import (
        # Versión
        APP_VERSION,
        APP_NAME,
        APP_AUTHOR,
        
        # API Keys - USAR CLAUDE_API_KEY
        CLAUDE_API_KEY,
        ANTHROPIC_API_KEY,  # Alias deprecated, solo para compatibilidad
        SEMRUSH_API_KEY,
        GOOGLE_API_KEY,
        SERP_API_KEY,
        
        # Modelo Claude
        DEFAULT_MODEL,
        AVAILABLE_MODELS,
        MAX_TOKENS,
        MAX_INPUT_TOKENS,
        DEFAULT_TEMPERATURE,
        API_MAX_RETRIES,
        API_RETRY_DELAY,
        
        # Contenido
        DEFAULT_CONTENT_LENGTH,
        MIN_CONTENT_LENGTH,
        MAX_CONTENT_LENGTH,
        WORD_COUNT_TOLERANCE,
        MAX_COMPETITORS,
        MAX_COMPETITOR_CONTENT_CHARS,
        
        # Scraping
        REQUEST_TIMEOUT,
        SCRAPER_MAX_RETRIES,
        USER_AGENT,
        DEFAULT_HEADERS,
        PCCOMPONENTES_DOMAINS,
        
        # SEMrush
        SEMRUSH_API_BASE_URL,
        SEMRUSH_DEFAULT_DATABASE,
        SEMRUSH_RESULTS_LIMIT,
        
        # Streamlit
        PAGE_TITLE,
        PAGE_ICON,
        PAGE_LAYOUT,
        SIDEBAR_STATE,
        
        # Rutas
        PROJECT_ROOT,
        DATA_DIR,
        ASSETS_DIR,
        CSS_FILE_PATH,
        EXPORTS_DIR,
        GSC_DATA_FILE,
        
        # Funciones
        validate_api_key,
        validate_environment,
        get_config_summary,
        mask_api_key,
        init_settings,
    )
    _settings_available = True
except ImportError as e:
    logger.warning(f"No se pudo importar settings: {e}")
    _settings_available = False
    
    # Valores por defecto mínimos
    import os
    APP_VERSION = "4.2.0"
    APP_NAME = "PcComponentes Content Generator"
    CLAUDE_API_KEY = os.getenv('CLAUDE_API_KEY', '')
    ANTHROPIC_API_KEY = CLAUDE_API_KEY
    DEFAULT_MODEL = 'claude-sonnet-4-20250514'
    MAX_TOKENS = 16000
    DEFAULT_TEMPERATURE = 0.7
    DEFAULT_CONTENT_LENGTH = 1500


# ============================================================================
# IMPORTS DE BRAND (CSS, TONO, ESTILOS)
# ============================================================================

try:
    from config.brand import (
        # CSS
        CSS_CMS_COMPATIBLE,
        CSS_FALLBACK,
        
        # Tono de marca
        BRAND_TONE,
        BRAND_VOICE_GUIDELINES,
        
        # Colores
        BRAND_COLORS,
        
        # Otros
        BRAND_NAME,
        BRAND_DOMAIN,
    )
    _brand_available = True
except ImportError as e:
    logger.warning(f"No se pudo importar brand: {e}")
    _brand_available = False
    
    # Valores por defecto
    CSS_CMS_COMPATIBLE = ""
    CSS_FALLBACK = ""
    BRAND_TONE = "Profesional, cercano y experto en tecnología."
    BRAND_VOICE_GUIDELINES = {}
    BRAND_COLORS = {}
    BRAND_NAME = "PcComponentes"
    BRAND_DOMAIN = "www.pccomponentes.com"


# ============================================================================
# IMPORTS DE ARQUETIPOS
# ============================================================================

try:
    from config.archetypes import (
        ARQUETIPOS,
        get_arquetipo_by_code,
        get_arquetipo_names,
        get_default_arquetipo,
    )
    _archetypes_available = True
except ImportError as e:
    logger.warning(f"No se pudo importar archetypes: {e}")
    _archetypes_available = False
    
    # Arquetipos por defecto
    ARQUETIPOS = {
        'GC': {
            'code': 'GC',
            'name': 'Guía de Compra',
            'description': 'Guía completa para ayudar en la decisión de compra',
            'structure': ['introducción', 'características', 'comparativa', 'conclusión'],
        },
        'RV': {
            'code': 'RV',
            'name': 'Review',
            'description': 'Análisis detallado de un producto específico',
            'structure': ['introducción', 'especificaciones', 'pruebas', 'veredicto'],
        },
        'CP': {
            'code': 'CP',
            'name': 'Comparativa',
            'description': 'Comparación entre múltiples productos',
            'structure': ['introducción', 'productos', 'comparativa', 'recomendación'],
        },
        'TU': {
            'code': 'TU',
            'name': 'Tutorial',
            'description': 'Guía paso a paso para realizar una tarea',
            'structure': ['introducción', 'requisitos', 'pasos', 'consejos'],
        },
        'TP': {
            'code': 'TP',
            'name': 'Top/Ranking',
            'description': 'Lista ordenada de los mejores productos',
            'structure': ['introducción', 'criterios', 'ranking', 'conclusión'],
        },
    }
    
    def get_arquetipo_by_code(code: str):
        return ARQUETIPOS.get(code)
    
    def get_arquetipo_names():
        return {k: v['name'] for k, v in ARQUETIPOS.items()}
    
    def get_default_arquetipo():
        return ARQUETIPOS.get('GC')


# ============================================================================
# FUNCIONES DE UTILIDAD
# ============================================================================

def is_settings_available() -> bool:
    """Verifica si el módulo settings está disponible."""
    return _settings_available


def is_brand_available() -> bool:
    """Verifica si el módulo brand está disponible."""
    return _brand_available


def is_archetypes_available() -> bool:
    """Verifica si el módulo archetypes está disponible."""
    return _archetypes_available


def get_available_config_modules() -> dict:
    """
    Retorna el estado de disponibilidad de cada módulo de configuración.
    
    Returns:
        dict: Estado de cada módulo
    """
    return {
        'settings': _settings_available,
        'brand': _brand_available,
        'archetypes': _archetypes_available,
    }


def validate_config() -> tuple:
    """
    Valida toda la configuración del paquete.
    
    Returns:
        tuple: (is_valid, list_of_errors)
    """
    errors = []
    
    if not _settings_available:
        errors.append("Módulo settings no disponible")
    
    if not CLAUDE_API_KEY:
        errors.append("CLAUDE_API_KEY no configurada")
    
    if not _brand_available:
        logger.warning("Módulo brand no disponible - usando valores por defecto")
    
    if not _archetypes_available:
        logger.warning("Módulo archetypes no disponible - usando valores por defecto")
    
    is_valid = len(errors) == 0
    return is_valid, errors


# ============================================================================
# EXPORTS (__all__)
# ============================================================================

__all__ = [
    # Versión
    '__version__',
    
    # === SETTINGS ===
    'APP_VERSION',
    'APP_NAME',
    'APP_AUTHOR',
    
    # API Keys
    'CLAUDE_API_KEY',
    'ANTHROPIC_API_KEY',  # Deprecated
    'SEMRUSH_API_KEY',
    'GOOGLE_API_KEY',
    'SERP_API_KEY',
    
    # Modelo
    'DEFAULT_MODEL',
    'AVAILABLE_MODELS',
    'MAX_TOKENS',
    'MAX_INPUT_TOKENS',
    'DEFAULT_TEMPERATURE',
    'API_MAX_RETRIES',
    'API_RETRY_DELAY',
    
    # Contenido
    'DEFAULT_CONTENT_LENGTH',
    'MIN_CONTENT_LENGTH',
    'MAX_CONTENT_LENGTH',
    'WORD_COUNT_TOLERANCE',
    'MAX_COMPETITORS',
    'MAX_COMPETITOR_CONTENT_CHARS',
    
    # Scraping
    'REQUEST_TIMEOUT',
    'SCRAPER_MAX_RETRIES',
    'USER_AGENT',
    'DEFAULT_HEADERS',
    'PCCOMPONENTES_DOMAINS',
    
    # SEMrush
    'SEMRUSH_API_BASE_URL',
    'SEMRUSH_DEFAULT_DATABASE',
    'SEMRUSH_RESULTS_LIMIT',
    
    # Streamlit
    'PAGE_TITLE',
    'PAGE_ICON',
    'PAGE_LAYOUT',
    'SIDEBAR_STATE',
    
    # Rutas
    'PROJECT_ROOT',
    'DATA_DIR',
    'ASSETS_DIR',
    'CSS_FILE_PATH',
    'EXPORTS_DIR',
    'GSC_DATA_FILE',
    
    # Funciones settings
    'validate_api_key',
    'validate_environment',
    'get_config_summary',
    'mask_api_key',
    'init_settings',
    
    # === BRAND ===
    'CSS_CMS_COMPATIBLE',
    'CSS_FALLBACK',
    'BRAND_TONE',
    'BRAND_VOICE_GUIDELINES',
    'BRAND_COLORS',
    'BRAND_NAME',
    'BRAND_DOMAIN',
    
    # === ARQUETIPOS ===
    'ARQUETIPOS',
    'get_arquetipo_by_code',
    'get_arquetipo_names',
    'get_default_arquetipo',
    
    # === UTILIDADES ===
    'is_settings_available',
    'is_brand_available',
    'is_archetypes_available',
    'get_available_config_modules',
    'validate_config',
]
