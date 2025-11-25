"""
Configuración Global - PcComponentes Content Generator
Versión 4.1.1

Configuración centralizada de la aplicación incluyendo API keys,
parámetros de Claude, configuración de GSC y settings generales.

Autor: PcComponentes - Product Discovery & Content
"""

import os
from datetime import datetime
from typing import Optional
import streamlit as st


# ============================================================================
# API KEYS Y CREDENCIALES
# ============================================================================

def get_api_key() -> Optional[str]:
    """
    Obtiene la API key de Claude desde diferentes fuentes.
    
    Prioridad:
    1. Streamlit secrets (producción)
    2. Variable de entorno (desarrollo)
    3. Archivo .env (desarrollo local)
    
    Returns:
        API key o None si no se encuentra
    """
    
    # 1. Intentar desde Streamlit secrets (Streamlit Cloud)
    try:
        if hasattr(st, 'secrets') and 'api' in st.secrets:
            return st.secrets['api']['claude_key']
    except Exception:
        pass
    
    # 2. Intentar desde variable de entorno
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if api_key:
        return api_key
    
    # 3. Intentar cargar desde .env
    try:
        from dotenv import load_dotenv
        load_dotenv()
        return os.getenv('ANTHROPIC_API_KEY')
    except ImportError:
        pass
    
    return None


# API Key de Claude
CLAUDE_API_KEY = get_api_key()

def get_semrush_api_key() -> Optional[str]:
    try:
        if hasattr(st, 'secrets') and 'api' in st.secrets:
            return st.secrets['api'].get('semrush_key')
    except:
        pass
    return os.getenv('SEMRUSH_API_KEY')

SEMRUSH_API_KEY = get_semrush_api_key()

# ============================================================================
# CONFIGURACIÓN DE CLAUDE
# ============================================================================

# Modelo a usar
CLAUDE_MODEL = os.getenv('CLAUDE_MODEL', 'claude-sonnet-4-20250514')

# Tokens máximos por respuesta
MAX_TOKENS = int(os.getenv('MAX_TOKENS', '8000'))

# Temperature (0.0 - 1.0)
TEMPERATURE = float(os.getenv('TEMPERATURE', '0.7'))


# ============================================================================
# CONFIGURACIÓN DE SEMRUSH
# ============================================================================

# API Key de SEMrush
SEMRUSH_API_KEY = os.getenv('SEMRUSH_API_KEY')

# Base de datos por defecto (España)
SEMRUSH_DATABASE = os.getenv('SEMRUSH_DATABASE', 'es')

# Habilitar integración SEMrush
SEMRUSH_ENABLED = os.getenv('SEMRUSH_ENABLED', 'True').lower() == 'true' and bool(SEMRUSH_API_KEY)


# ============================================================================
# CONFIGURACIÓN DE LA APLICACIÓN
# ============================================================================

# Información de la app
APP_TITLE = os.getenv('APP_TITLE', 'PcComponentes Content Generator')
APP_VERSION = '4.1.1'
PAGE_ICON = '🚀'

# Modo debug
DEBUG_MODE = os.getenv('DEBUG_MODE', 'False').lower() == 'true'

# Fecha de conocimiento de Claude
CLAUDE_KNOWLEDGE_CUTOFF = datetime(2025, 1, 31)


# ============================================================================
# CONFIGURACIÓN DE GOOGLE SEARCH CONSOLE
# ============================================================================

# Ruta al CSV de GSC
GSC_CSV_PATH = os.getenv('GSC_CSV_PATH', 'gsc_keywords.csv')

# Habilitar verificación GSC
GSC_VERIFICATION_ENABLED = os.getenv('GSC_VERIFICATION_ENABLED', 'True').lower() == 'true'

# Período del dataset actual (ACTUALIZAR CUANDO SE RENUEVE EL CSV)
GSC_DATASET_START = datetime(2025, 10, 18)
GSC_DATASET_END = datetime(2025, 11, 17)

# Umbrales de alerta para freshness
GSC_DAYS_WARNING = int(os.getenv('GSC_DAYS_WARNING', '30'))  # Avisar después de 30 días
GSC_DAYS_CRITICAL = int(os.getenv('GSC_DAYS_CRITICAL', '60'))  # Crítico después de 60 días

# Configuración de matching de keywords
GSC_EXACT_MATCH_THRESHOLD = 1.0
GSC_HIGH_SIMILARITY_THRESHOLD = float(os.getenv('GSC_HIGH_SIMILARITY_THRESHOLD', '0.85'))
GSC_MEDIUM_SIMILARITY_THRESHOLD = float(os.getenv('GSC_MEDIUM_SIMILARITY_THRESHOLD', '0.70'))
GSC_ENABLE_CONTAINS_MATCH = os.getenv('GSC_ENABLE_CONTAINS_MATCH', 'True').lower() == 'true'

# Mostrar disclaimer de freshness por defecto
GSC_SHOW_FRESHNESS_DISCLAIMER = os.getenv('GSC_SHOW_FRESHNESS_DISCLAIMER', 'True').lower() == 'true'


# ============================================================================
# CONFIGURACIÓN DE SCRAPING
# ============================================================================

# n8n webhook para scraping de PDPs
N8N_WEBHOOK_URL = os.getenv('N8N_WEBHOOK_URL')

# Zenrows API key (para scraping avanzado)
ZENROWS_API_KEY = os.getenv('ZENROWS_API_KEY')

# User Agent para requests
USER_AGENT = os.getenv(
    'USER_AGENT',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
)

# Timeout para requests (segundos)
REQUEST_TIMEOUT = int(os.getenv('REQUEST_TIMEOUT', '30'))


# ============================================================================
# CONFIGURACIÓN DE CATEGORÍAS
# ============================================================================

# Ruta al CSV de categorías
CATEGORIES_CSV_PATH = os.getenv('CATEGORIES_CSV_PATH', 'data/categories.csv')


# ============================================================================
# CONFIGURACIÓN DE LOGGING
# ============================================================================

# Nivel de logging
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

# Archivo de logs
LOG_FILE = os.getenv('LOG_FILE', 'logs/app.log')

# Habilitar logging a archivo
ENABLE_FILE_LOGGING = os.getenv('ENABLE_FILE_LOGGING', 'False').lower() == 'true'


# ============================================================================
# LÍMITES Y VALIDACIONES
# ============================================================================

# Longitud de contenido
MIN_CONTENT_LENGTH = 800  # Palabras mínimas
MAX_CONTENT_LENGTH = 3000  # Palabras máximas
DEFAULT_CONTENT_LENGTH = 1500  # Longitud por defecto

# Tolerancia de word count (±5%)
WORD_COUNT_TOLERANCE = 0.05

# Límites de keywords
MAX_KEYWORDS = 20
MIN_KEYWORD_LENGTH = 3
MAX_KEYWORD_LENGTH = 100

# Límites de enlaces
MAX_SECONDARY_LINKS = 10


# ============================================================================
# CONFIGURACIÓN DE CACHÉ
# ============================================================================

# TTL de caché de Streamlit (segundos)
CACHE_TTL = int(os.getenv('CACHE_TTL', '3600'))  # 1 hora por defecto


# ============================================================================
# CONFIGURACIÓN DE UI
# ============================================================================

# Tema de colores (PcComponentes)
PRIMARY_COLOR = '#FF6000'  # Naranja PcComponentes
SECONDARY_COLOR = '#170453'  # Azul oscuro
BACKGROUND_COLOR = '#FFFFFF'
TEXT_COLOR = '#262730'

# Configuración de tabs
DEFAULT_TAB_ICON = '📄'


# ============================================================================
# MENSAJES Y TEXTOS
# ============================================================================

# Mensaje de bienvenida
WELCOME_MESSAGE = """
Bienvenido al **Content Generator** de PcComponentes.

Esta herramienta te ayuda a crear contenido SEO optimizado de alta calidad
usando inteligencia artificial (Claude Sonnet 4).

**Características principales:**
- 📝 18 arquetipos de contenido predefinidos
- 🔄 Modo reescritura con análisis competitivo
- ✅ Validación automática CMS v4.1.1
- 🔍 Verificación de keywords en Google Search Console
- 📊 Control preciso de longitud y estructura
"""

# Mensaje de error cuando no hay API key
NO_API_KEY_MESSAGE = """
⚠️ **No se encontró API Key de Claude**

Para usar esta aplicación necesitas una API key de Anthropic Claude.

**Configuración:**

1. **Streamlit Cloud**: Settings > Secrets > añadir:
```toml
   [api]
   claude_key = "tu-api-key"
```

2. **Local**: Crear archivo `.env` con:
```
   ANTHROPIC_API_KEY=tu-api-key
```

Obtén tu API key en: https://console.anthropic.com/
"""


# ============================================================================
# VALIDACIÓN DE CONFIGURACIÓN
# ============================================================================

def validate_configuration() -> bool:
    """
    Valida que la configuración esté completa.
    
    Returns:
        True si la configuración es válida, False si falta algo crítico
    """
    
    if not CLAUDE_API_KEY:
        return False
    
    # Validar que los archivos necesarios existan (en producción)
    # if not DEBUG_MODE:
    #     if GSC_VERIFICATION_ENABLED and not os.path.exists(GSC_CSV_PATH):
    #         return False
    
    return True


def get_configuration_summary() -> dict:
    """
    Obtiene un resumen de la configuración actual.
    
    Returns:
        Dict con información de configuración
    """
    
    return {
        'app_version': APP_VERSION,
        'claude_model': CLAUDE_MODEL,
        'max_tokens': MAX_TOKENS,
        'temperature': TEMPERATURE,
        'debug_mode': DEBUG_MODE,
        'gsc_enabled': GSC_VERIFICATION_ENABLED,
        'gsc_csv_exists': os.path.exists(GSC_CSV_PATH) if GSC_CSV_PATH else False,
        'has_api_key': bool(CLAUDE_API_KEY),
        'n8n_configured': bool(N8N_WEBHOOK_URL),
        'zenrows_configured': bool(ZENROWS_API_KEY)
    }


# ============================================================================
# FUNCIONES DE UTILIDAD
# ============================================================================

def get_gsc_dataset_info() -> dict:
    """
    Obtiene información del dataset de GSC.
    
    Returns:
        Dict con información del período y freshness
    """
    
    from datetime import datetime, timedelta
    
    today = datetime.now()
    days_since_end = (today - GSC_DATASET_END).days
    
    return {
        'start_date': GSC_DATASET_START,
        'end_date': GSC_DATASET_END,
        'days_since_end': days_since_end,
        'is_fresh': days_since_end <= GSC_DAYS_WARNING,
        'needs_update': days_since_end > GSC_DAYS_WARNING,
        'is_critical': days_since_end > GSC_DAYS_CRITICAL,
        'period_days': (GSC_DATASET_END - GSC_DATASET_START).days
    }


# ============================================================================
# EXPORTAR CONFIGURACIÓN
# ============================================================================

__all__ = [
    # API y Claude
    'CLAUDE_API_KEY',
    'CLAUDE_MODEL',
    'MAX_TOKENS',
    'TEMPERATURE',
    
    # App
    'APP_TITLE',
    'APP_VERSION',
    'PAGE_ICON',
    'DEBUG_MODE',
    'CLAUDE_KNOWLEDGE_CUTOFF',
    
    # GSC
    'GSC_CSV_PATH',
    'GSC_VERIFICATION_ENABLED',
    'GSC_DATASET_START',
    'GSC_DATASET_END',
    'GSC_DAYS_WARNING',
    'GSC_DAYS_CRITICAL',
    'GSC_HIGH_SIMILARITY_THRESHOLD',
    'GSC_MEDIUM_SIMILARITY_THRESHOLD',
    'GSC_ENABLE_CONTAINS_MATCH',
    'GSC_SHOW_FRESHNESS_DISCLAIMER',
    
    # Scraping
    'N8N_WEBHOOK_URL',
    'ZENROWS_API_KEY',
    'USER_AGENT',
    'REQUEST_TIMEOUT',
    
    # Categorías
    'CATEGORIES_CSV_PATH',
    
    # Logging
    'LOG_LEVEL',
    'LOG_FILE',
    'ENABLE_FILE_LOGGING',
    
    # Límites
    'MIN_CONTENT_LENGTH',
    'MAX_CONTENT_LENGTH',
    'DEFAULT_CONTENT_LENGTH',
    'WORD_COUNT_TOLERANCE',
    'MAX_KEYWORDS',
    'MIN_KEYWORD_LENGTH',
    'MAX_KEYWORD_LENGTH',
    'MAX_SECONDARY_LINKS',
    
    # Caché
    'CACHE_TTL',
    
    # UI
    'PRIMARY_COLOR',
    'SECONDARY_COLOR',
    'BACKGROUND_COLOR',
    'TEXT_COLOR',
    
    # Mensajes
    'WELCOME_MESSAGE',
    'NO_API_KEY_MESSAGE',
    
    # Funciones
    'validate_configuration',
    'get_configuration_summary',
    'get_gsc_dataset_info'
]

__version__ = "4.1.1"
