"""
Config package - PcComponentes Content Generator
Versión 4.3.0
"""

import logging

logger = logging.getLogger(__name__)

__version__ = "4.3.0"

# Importar settings
try:
    from .settings import (
        # API
        CLAUDE_API_KEY,
        ANTHROPIC_API_KEY,
        CLAUDE_MODEL,
        MAX_TOKENS,
        TEMPERATURE,
        # App
        APP_NAME,
        APP_TITLE,
        APP_VERSION,
        PAGE_ICON,
        DEBUG_MODE,
        # GSC
        GSC_VERIFICATION_ENABLED,
        GSC_CREDENTIALS_FILE,
        GSC_PROPERTY_URL,
        GSC_CACHE_TTL,
        # SEMrush
        SEMRUSH_ENABLED,
        SEMRUSH_API_KEY,
        SEMRUSH_DATABASE,
        # Scraper
        MAX_RETRIES,
        RETRY_DELAY,
        REQUEST_TIMEOUT,
        USER_AGENT,
        # N8N
        N8N_WEBHOOK_URL,
        N8N_ENABLED,
        # Content
        DEFAULT_CONTENT_LENGTH,
        MIN_CONTENT_LENGTH,
        MAX_CONTENT_LENGTH,
        MAX_COMPETITORS,
        TARGET_WORD_COUNT_TOLERANCE,
        # Domains
        PCCOMPONENTES_DOMAINS,
        # Cache
        CACHE_ENABLED,
        CACHE_TTL,
        CACHE_MAX_SIZE,
        # Functions
        validate_config,
        get_api_key,
        is_configured,
    )
    _settings_available = True
except ImportError as e:
    logger.warning(f"No se pudo importar settings: {e}")
    _settings_available = False
    
    # Fallbacks mínimos
    import os
    CLAUDE_API_KEY = os.getenv('ANTHROPIC_API_KEY', '')
    ANTHROPIC_API_KEY = CLAUDE_API_KEY
    CLAUDE_MODEL = 'claude-sonnet-4-20250514'
    MAX_TOKENS = 16000
    TEMPERATURE = 0.7
    APP_NAME = "PcComponentes Content Generator"
    APP_TITLE = APP_NAME
    APP_VERSION = "4.3.0"
    PAGE_ICON = "🚀"
    DEBUG_MODE = False
    GSC_VERIFICATION_ENABLED = False
    SEMRUSH_ENABLED = False
    SEMRUSH_API_KEY = ""
    MAX_RETRIES = 3
    DEFAULT_CONTENT_LENGTH = 1500
    MIN_CONTENT_LENGTH = 500
    MAX_CONTENT_LENGTH = 5000

# Importar archetipos
try:
    from .archetipos import (
        ARQUETIPOS,
        get_arquetipo,
        list_arquetipos,
        get_arquetipo_names,
        get_arquetipo_by_name,
        get_default_length,
        validate_arquetipo_code,
        get_all_codes,
    )
    _archetipos_available = True
except ImportError as e:
    logger.warning(f"No se pudo importar archetipos: {e}")
    _archetipos_available = False
    
    # Fallbacks
    ARQUETIPOS = {}
    def get_arquetipo(code): return None
    def list_arquetipos(): return []
    def get_arquetipo_names(): return {}
    def get_arquetipo_by_name(name): return None
    def get_default_length(code): return 1500
    def validate_arquetipo_code(code): return False
    def get_all_codes(): return []

# También intentar importar archetypes (alias en inglés) por compatibilidad
try:
    from .archetipos import ARQUETIPOS as ARCHETYPES
except ImportError:
    ARCHETYPES = ARQUETIPOS

__all__ = [
    '__version__',
    # Settings
    'CLAUDE_API_KEY',
    'ANTHROPIC_API_KEY',
    'CLAUDE_MODEL',
    'MAX_TOKENS',
    'TEMPERATURE',
    'APP_NAME',
    'APP_TITLE',
    'APP_VERSION',
    'PAGE_ICON',
    'DEBUG_MODE',
    'GSC_VERIFICATION_ENABLED',
    'SEMRUSH_ENABLED',
    'SEMRUSH_API_KEY',
    'MAX_RETRIES',
    'DEFAULT_CONTENT_LENGTH',
    'MIN_CONTENT_LENGTH',
    'MAX_CONTENT_LENGTH',
    # Arquetipos
    'ARQUETIPOS',
    'ARCHETYPES',
    'get_arquetipo',
    'list_arquetipos',
    'get_arquetipo_names',
    'get_arquetipo_by_name',
    'get_default_length',
    'validate_arquetipo_code',
    'get_all_codes',
]
