"""
Settings - PcComponentes Content Generator
Versión 4.2.0

Configuración centralizada de la aplicación.
Carga variables de entorno y define constantes globales.

IMPORTANTE: Este módulo usa CLAUDE_API_KEY como nombre estándar.
NO usar ANTHROPIC_API_KEY en ninguna parte del código.

Autor: PcComponentes - Product Discovery & Content
"""

import os
import logging
from pathlib import Path
from typing import Optional, Dict, Any
from dotenv import load_dotenv

# ============================================================================
# CARGA DE VARIABLES DE ENTORNO
# ============================================================================

# Cargar .env desde la raíz del proyecto
_project_root = Path(__file__).parent.parent
_env_path = _project_root / ".env"

if _env_path.exists():
    load_dotenv(_env_path)
else:
    # Intentar cargar desde directorio actual
    load_dotenv()

# Configurar logging básico
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================================================
# VERSIÓN DE LA APLICACIÓN
# ============================================================================

APP_VERSION = "4.2.0"
APP_NAME = "PcComponentes Content Generator"
APP_AUTHOR = "Product Discovery & Content"


# ============================================================================
# API KEYS - UNIFICADO A CLAUDE_API_KEY
# ============================================================================

# IMPORTANTE: Usar CLAUDE_API_KEY en todo el código
# Soporta ambos nombres en .env por compatibilidad, pero internamente usa CLAUDE_API_KEY
CLAUDE_API_KEY: str = os.getenv('CLAUDE_API_KEY') or os.getenv('ANTHROPIC_API_KEY') or ''

# Alias para compatibilidad hacia atrás (DEPRECATED - no usar en código nuevo)
# Este alias existe solo para evitar errores en código legacy
ANTHROPIC_API_KEY: str = CLAUDE_API_KEY  # DEPRECATED: usar CLAUDE_API_KEY

# SEMrush API Key (opcional)
SEMRUSH_API_KEY: str = os.getenv('SEMRUSH_API_KEY', '')

# Otras API keys opcionales
GOOGLE_API_KEY: str = os.getenv('GOOGLE_API_KEY', '')
SERP_API_KEY: str = os.getenv('SERP_API_KEY', '')


# ============================================================================
# CONFIGURACIÓN DEL MODELO CLAUDE
# ============================================================================

# Modelo por defecto
DEFAULT_MODEL: str = os.getenv('CLAUDE_MODEL', 'claude-sonnet-4-20250514')

# Modelos disponibles
AVAILABLE_MODELS: Dict[str, str] = {
    'claude-sonnet-4-20250514': 'Claude Sonnet 4 (Recomendado)',
    'claude-opus-4-20250514': 'Claude Opus 4 (Más potente)',
    'claude-3-5-sonnet-20241022': 'Claude 3.5 Sonnet',
    'claude-3-opus-20240229': 'Claude 3 Opus',
    'claude-3-haiku-20240307': 'Claude 3 Haiku (Rápido)',
}

# Límites de tokens
MAX_TOKENS: int = int(os.getenv('MAX_TOKENS', '16000'))
MAX_INPUT_TOKENS: int = int(os.getenv('MAX_INPUT_TOKENS', '100000'))

# Temperatura por defecto
DEFAULT_TEMPERATURE: float = float(os.getenv('TEMPERATURE', '0.7'))

# Reintentos en caso de error
API_MAX_RETRIES: int = int(os.getenv('API_MAX_RETRIES', '3'))
API_RETRY_DELAY: float = float(os.getenv('API_RETRY_DELAY', '1.0'))


# ============================================================================
# CONFIGURACIÓN DE CONTENIDO
# ============================================================================

# Longitud de contenido
DEFAULT_CONTENT_LENGTH: int = int(os.getenv('DEFAULT_CONTENT_LENGTH', '1500'))
MIN_CONTENT_LENGTH: int = 500
MAX_CONTENT_LENGTH: int = 5000

# Tolerancia de longitud (±5%)
WORD_COUNT_TOLERANCE: float = 0.05

# Número máximo de competidores a analizar
MAX_COMPETITORS: int = int(os.getenv('MAX_COMPETITORS', '5'))

# Límite de caracteres por competidor en análisis
MAX_COMPETITOR_CONTENT_CHARS: int = 3000


# ============================================================================
# CONFIGURACIÓN DE SCRAPING
# ============================================================================

# Timeout para requests HTTP
REQUEST_TIMEOUT: int = int(os.getenv('REQUEST_TIMEOUT', '30'))

# Reintentos de scraping
SCRAPER_MAX_RETRIES: int = int(os.getenv('SCRAPER_MAX_RETRIES', '3'))

# User Agent
USER_AGENT: str = os.getenv(
    'USER_AGENT',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
)

# Headers por defecto para requests
DEFAULT_HEADERS: Dict[str, str] = {
    'User-Agent': USER_AGENT,
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
}

# Dominios de PcComponentes
PCCOMPONENTES_DOMAINS: list = [
    'www.pccomponentes.com',
    'pccomponentes.com',
    'www.pccomponentes.pt',
    'pccomponentes.pt',
]


# ============================================================================
# CONFIGURACIÓN DE SEMRUSH
# ============================================================================

# Base URL de la API de SEMrush
SEMRUSH_API_BASE_URL: str = 'https://api.semrush.com/'

# Database por defecto (España)
SEMRUSH_DEFAULT_DATABASE: str = os.getenv('SEMRUSH_DATABASE', 'es')

# Límite de resultados
SEMRUSH_RESULTS_LIMIT: int = int(os.getenv('SEMRUSH_RESULTS_LIMIT', '100'))


# ============================================================================
# CONFIGURACIÓN DE STREAMLIT
# ============================================================================

# Título de la página
PAGE_TITLE: str = f"{APP_NAME} v{APP_VERSION}"

# Icono de la página
PAGE_ICON: str = "🚀"

# Layout por defecto
PAGE_LAYOUT: str = "wide"

# Estado inicial del sidebar
SIDEBAR_STATE: str = "expanded"


# ============================================================================
# RUTAS DE ARCHIVOS
# ============================================================================

# Directorio raíz del proyecto
PROJECT_ROOT: Path = _project_root

# Directorio de datos
DATA_DIR: Path = PROJECT_ROOT / "data"

# Directorio de assets
ASSETS_DIR: Path = PROJECT_ROOT / "assets"

# Archivo de CSS del CMS
CSS_FILE_PATH: Path = ASSETS_DIR / "cms_styles.css"

# Directorio de exports
EXPORTS_DIR: Path = PROJECT_ROOT / "exports"

# Archivo de GSC data
GSC_DATA_FILE: Path = DATA_DIR / "gsc_data.csv"


# ============================================================================
# FUNCIONES DE VALIDACIÓN
# ============================================================================

def validate_api_key() -> bool:
    """
    Valida que la API key de Claude esté configurada.
    
    Returns:
        bool: True si la API key está configurada y tiene formato válido
    """
    if not CLAUDE_API_KEY:
        logger.warning("CLAUDE_API_KEY no está configurada")
        return False
    
    # Verificar formato básico (empieza con 'sk-ant-')
    if not CLAUDE_API_KEY.startswith('sk-ant-'):
        logger.warning("CLAUDE_API_KEY tiene formato inválido")
        return False
    
    return True


def validate_environment() -> tuple:
    """
    Valida la configuración del entorno.
    
    Returns:
        tuple: (is_valid, list_of_errors)
    """
    errors = []
    
    # Validar API key de Claude
    if not CLAUDE_API_KEY:
        errors.append("CLAUDE_API_KEY no está configurada. Añádela al archivo .env")
    elif not CLAUDE_API_KEY.startswith('sk-ant-'):
        errors.append("CLAUDE_API_KEY tiene formato inválido. Debe empezar con 'sk-ant-'")
    
    # Advertencias (no errores críticos)
    if not SEMRUSH_API_KEY:
        logger.info("SEMRUSH_API_KEY no configurada - funcionalidad de keywords limitada")
    
    # Verificar directorios
    if not DATA_DIR.exists():
        try:
            DATA_DIR.mkdir(parents=True, exist_ok=True)
            logger.info(f"Directorio de datos creado: {DATA_DIR}")
        except Exception as e:
            errors.append(f"No se pudo crear directorio de datos: {e}")
    
    if not EXPORTS_DIR.exists():
        try:
            EXPORTS_DIR.mkdir(parents=True, exist_ok=True)
            logger.info(f"Directorio de exports creado: {EXPORTS_DIR}")
        except Exception as e:
            errors.append(f"No se pudo crear directorio de exports: {e}")
    
    is_valid = len(errors) == 0
    return is_valid, errors


def get_config_summary() -> Dict[str, Any]:
    """
    Retorna un resumen de la configuración actual.
    
    Returns:
        dict: Resumen de configuración (sin exponer API keys completas)
    """
    return {
        'app_version': APP_VERSION,
        'app_name': APP_NAME,
        'claude_api_key_configured': bool(CLAUDE_API_KEY),
        'claude_api_key_valid': validate_api_key(),
        'semrush_api_key_configured': bool(SEMRUSH_API_KEY),
        'default_model': DEFAULT_MODEL,
        'max_tokens': MAX_TOKENS,
        'default_temperature': DEFAULT_TEMPERATURE,
        'default_content_length': DEFAULT_CONTENT_LENGTH,
        'max_competitors': MAX_COMPETITORS,
        'request_timeout': REQUEST_TIMEOUT,
        'project_root': str(PROJECT_ROOT),
        'data_dir_exists': DATA_DIR.exists(),
        'exports_dir_exists': EXPORTS_DIR.exists(),
    }


def mask_api_key(api_key: str) -> str:
    """
    Enmascara una API key para mostrarla de forma segura.
    
    Args:
        api_key: La API key a enmascarar
        
    Returns:
        str: API key enmascarada (ej: "sk-ant-***...***xyz")
    """
    if not api_key:
        return "(no configurada)"
    
    if len(api_key) < 12:
        return "***"
    
    return f"{api_key[:7]}***...***{api_key[-3:]}"


# ============================================================================
# INICIALIZACIÓN
# ============================================================================

def init_settings() -> bool:
    """
    Inicializa y valida la configuración.
    
    Returns:
        bool: True si la configuración es válida
    """
    logger.info(f"Inicializando {APP_NAME} v{APP_VERSION}")
    
    is_valid, errors = validate_environment()
    
    if not is_valid:
        for error in errors:
            logger.error(f"Error de configuración: {error}")
        return False
    
    logger.info("Configuración validada correctamente")
    logger.info(f"Modelo por defecto: {DEFAULT_MODEL}")
    logger.info(f"API Key Claude: {mask_api_key(CLAUDE_API_KEY)}")
    
    return True


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    # Versión
    'APP_VERSION',
    'APP_NAME',
    'APP_AUTHOR',
    
    # API Keys
    'CLAUDE_API_KEY',
    'ANTHROPIC_API_KEY',  # Alias deprecated
    'SEMRUSH_API_KEY',
    'GOOGLE_API_KEY',
    'SERP_API_KEY',
    
    # Modelo Claude
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
    
    # Funciones
    'validate_api_key',
    'validate_environment',
    'get_config_summary',
    'mask_api_key',
    'init_settings',
]


# ============================================================================
# VALIDACIÓN AL IMPORTAR (OPCIONAL)
# ============================================================================

# Descomentar para validar automáticamente al importar
# if not validate_api_key():
#     logger.warning("⚠️ CLAUDE_API_KEY no configurada o inválida")
