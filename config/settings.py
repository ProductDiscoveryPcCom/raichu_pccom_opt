"""
Configuración - PcComponentes Content Generator
Versión 4.3.0

Autor: PcComponentes - Product Discovery & Content
"""

import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)

__version__ = "4.3.0"

# ============================================================================
# API KEYS - ANTHROPIC/CLAUDE
# ============================================================================
CLAUDE_API_KEY: str = os.getenv('ANTHROPIC_API_KEY', os.getenv('CLAUDE_API_KEY', ''))
ANTHROPIC_API_KEY: str = CLAUDE_API_KEY  # Alias

CLAUDE_MODEL: str = os.getenv('CLAUDE_MODEL', 'claude-sonnet-4-20250514')
MAX_TOKENS: int = int(os.getenv('MAX_TOKENS', '16000'))
TEMPERATURE: float = float(os.getenv('TEMPERATURE', '0.7'))

# ============================================================================
# APP SETTINGS
# ============================================================================
APP_NAME: str = "PcComponentes Content Generator"
APP_TITLE: str = APP_NAME  # Alias
APP_VERSION: str = "4.3.0"
PAGE_ICON: str = "🚀"
DEBUG_MODE: bool = os.getenv('DEBUG_MODE', 'false').lower() == 'true'

# ============================================================================
# GOOGLE SEARCH CONSOLE
# ============================================================================
GSC_VERIFICATION_ENABLED: bool = os.getenv('GSC_VERIFICATION_ENABLED', 'false').lower() == 'true'
GSC_CREDENTIALS_FILE: str = os.getenv('GSC_CREDENTIALS_FILE', 'credentials.json')
GSC_PROPERTY_URL: str = os.getenv('GSC_PROPERTY_URL', 'https://www.pccomponentes.com/')
GSC_CACHE_TTL: int = int(os.getenv('GSC_CACHE_TTL', '3600'))

# ============================================================================
# SEMRUSH
# ============================================================================
SEMRUSH_ENABLED: bool = os.getenv('SEMRUSH_ENABLED', 'false').lower() == 'true'
SEMRUSH_API_KEY: str = os.getenv('SEMRUSH_API_KEY', '')
SEMRUSH_DATABASE: str = os.getenv('SEMRUSH_DATABASE', 'es')

# ============================================================================
# SCRAPER SETTINGS
# ============================================================================
MAX_RETRIES: int = int(os.getenv('MAX_RETRIES', '3'))
RETRY_DELAY: float = float(os.getenv('RETRY_DELAY', '1.0'))
REQUEST_TIMEOUT: int = int(os.getenv('REQUEST_TIMEOUT', '30'))
USER_AGENT: str = os.getenv(
    'USER_AGENT', 
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
)

# ============================================================================
# N8N WEBHOOK
# ============================================================================
N8N_WEBHOOK_URL: str = os.getenv('N8N_WEBHOOK_URL', '')
N8N_ENABLED: bool = bool(N8N_WEBHOOK_URL)

# ============================================================================
# CONTENT SETTINGS
# ============================================================================
DEFAULT_CONTENT_LENGTH: int = 1500
MIN_CONTENT_LENGTH: int = 500
MAX_CONTENT_LENGTH: int = 5000
MAX_COMPETITORS: int = 5
TARGET_WORD_COUNT_TOLERANCE: float = 0.05  # ±5%

# ============================================================================
# DOMINIOS
# ============================================================================
PCCOMPONENTES_DOMAINS: list = ['www.pccomponentes.com', 'pccomponentes.com']
ALLOWED_EXTERNAL_DOMAINS: list = []

# ============================================================================
# CACHE SETTINGS
# ============================================================================
CACHE_ENABLED: bool = os.getenv('CACHE_ENABLED', 'true').lower() == 'true'
CACHE_TTL: int = int(os.getenv('CACHE_TTL', '3600'))
CACHE_MAX_SIZE: int = int(os.getenv('CACHE_MAX_SIZE', '100'))

# ============================================================================
# LOGGING
# ============================================================================
LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')
LOG_FORMAT: str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# Configurar logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL.upper(), logging.INFO),
    format=LOG_FORMAT
)

# ============================================================================
# VALIDACIÓN
# ============================================================================
def validate_config() -> tuple[bool, list[str]]:
    """Valida la configuración y retorna (is_valid, errors)."""
    errors = []
    
    if not CLAUDE_API_KEY:
        errors.append("ANTHROPIC_API_KEY o CLAUDE_API_KEY no configurada")
    
    if GSC_VERIFICATION_ENABLED and not os.path.exists(GSC_CREDENTIALS_FILE):
        errors.append(f"GSC habilitado pero no existe {GSC_CREDENTIALS_FILE}")
    
    if SEMRUSH_ENABLED and not SEMRUSH_API_KEY:
        errors.append("SEMRUSH habilitado pero SEMRUSH_API_KEY no configurada")
    
    return len(errors) == 0, errors


def get_api_key() -> str:
    """Obtiene la API key de Claude."""
    return CLAUDE_API_KEY


def is_configured() -> bool:
    """Verifica si la configuración mínima está presente."""
    return bool(CLAUDE_API_KEY)


# ============================================================================
# EXPORTS
# ============================================================================
__all__ = [
    '__version__',
    # API
    'CLAUDE_API_KEY',
    'ANTHROPIC_API_KEY',
    'CLAUDE_MODEL',
    'MAX_TOKENS',
    'TEMPERATURE',
    # App
    'APP_NAME',
    'APP_TITLE',
    'APP_VERSION',
    'PAGE_ICON',
    'DEBUG_MODE',
    # GSC
    'GSC_VERIFICATION_ENABLED',
    'GSC_CREDENTIALS_FILE',
    'GSC_PROPERTY_URL',
    'GSC_CACHE_TTL',
    # SEMrush
    'SEMRUSH_ENABLED',
    'SEMRUSH_API_KEY',
    'SEMRUSH_DATABASE',
    # Scraper
    'MAX_RETRIES',
    'RETRY_DELAY',
    'REQUEST_TIMEOUT',
    'USER_AGENT',
    # N8N
    'N8N_WEBHOOK_URL',
    'N8N_ENABLED',
    # Content
    'DEFAULT_CONTENT_LENGTH',
    'MIN_CONTENT_LENGTH',
    'MAX_CONTENT_LENGTH',
    'MAX_COMPETITORS',
    'TARGET_WORD_COUNT_TOLERANCE',
    # Domains
    'PCCOMPONENTES_DOMAINS',
    'ALLOWED_EXTERNAL_DOMAINS',
    # Cache
    'CACHE_ENABLED',
    'CACHE_TTL',
    'CACHE_MAX_SIZE',
    # Logging
    'LOG_LEVEL',
    'LOG_FORMAT',
    # Functions
    'validate_config',
    'get_api_key',
    'is_configured',
]
