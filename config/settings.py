"""
Configuración Global - PcComponentes Content Generator
Versión 4.2.0

Configuración centralizada de la aplicación incluyendo:
- API keys (Claude, SEMrush)
- Parámetros de generación
- Configuración de GSC
- Settings generales

Autor: PcComponentes - Product Discovery & Content
"""

import os
from datetime import datetime
from typing import Optional, Tuple
import streamlit as st


# ============================================================================
# FUNCIONES DE CARGA DE CONFIGURACIÓN
# ============================================================================

def get_secret(key: str, section: str = None, default: str = None) -> Optional[str]:
    """
    Obtiene un valor secreto desde diferentes fuentes.
    
    Prioridad:
    1. Streamlit secrets (producción)
    2. Variable de entorno (desarrollo)
    3. Valor por defecto
    
    Args:
        key: Nombre de la clave
        section: Sección en secrets.toml (opcional)
        default: Valor por defecto si no se encuentra
        
    Returns:
        Valor del secreto o None/default
    """
    
    # 1. Intentar desde Streamlit secrets
    try:
        if hasattr(st, 'secrets'):
            if section and section in st.secrets:
                return st.secrets[section].get(key, default)
            elif key in st.secrets:
                return st.secrets[key]
    except Exception:
        pass
    
    # 2. Intentar desde variable de entorno
    env_value = os.getenv(key.upper())
    if env_value:
        return env_value
    
    # 3. Intentar cargar desde .env
    try:
        from dotenv import load_dotenv
        load_dotenv()
        env_value = os.getenv(key.upper())
        if env_value:
            return env_value
    except ImportError:
        pass
    
    return default


def get_api_key() -> Optional[str]:
    """
    Obtiene la API key de Claude.
    
    Returns:
        API key o None si no se encuentra
    """
    # Intentar múltiples variantes
    key = get_secret('claude_key', 'api')
    if key:
        return key
    
    key = get_secret('ANTHROPIC_API_KEY')
    if key:
        return key
    
    key = get_secret('anthropic_api_key', 'api')
    return key


def get_semrush_api_key() -> Optional[str]:
    """
    Obtiene la API key de SEMrush.
    
    Returns:
        API key o None si no se encuentra
    """
    key = get_secret('api_key', 'semrush')
    if key:
        return key
    
    key = get_secret('SEMRUSH_API_KEY')
    return key


# ============================================================================
# API KEYS Y CREDENCIALES
# ============================================================================

# Claude API
CLAUDE_API_KEY = get_api_key()

# SEMrush API
SEMRUSH_API_KEY = get_semrush_api_key()


# ============================================================================
# CONFIGURACIÓN DE CLAUDE
# ============================================================================

# Modelo a usar
CLAUDE_MODEL = get_secret('CLAUDE_MODEL') or 'claude-sonnet-4-20250514'

# Tokens máximos por respuesta
MAX_TOKENS = int(get_secret('MAX_TOKENS') or '8000')

# Temperature (0.0 - 1.0)
TEMPERATURE = float(get_secret('TEMPERATURE') or '0.7')


# ============================================================================
# CONFIGURACIÓN DE SEMRUSH
# ============================================================================

# Habilitar SEMrush (True si hay API key)
SEMRUSH_ENABLED = bool(SEMRUSH_API_KEY)

# Base de datos regional de SEMrush
# Opciones: 'es' (España), 'us', 'uk', 'fr', 'de', 'it', 'pt', 'mx', 'ar', 'co'
SEMRUSH_DATABASE = get_secret('database', 'semrush') or 'es'

# Número de competidores a obtener por defecto
SEMRUSH_DEFAULT_RESULTS = int(get_secret('default_results', 'semrush') or '5')

# Máximo de competidores permitidos
SEMRUSH_MAX_RESULTS = 10

# Timeout para requests de SEMrush (segundos)
SEMRUSH_TIMEOUT = int(get_secret('timeout', 'semrush') or '30')

# Delay entre requests (rate limiting)
SEMRUSH_RATE_LIMIT_DELAY = float(get_secret('rate_limit_delay', 'semrush') or '0.5')

# Dominios a excluir siempre de resultados
SEMRUSH_EXCLUDE_DOMAINS = [
    'pccomponentes.com',
    'pccomponentes.pt'
]

# Scrapear contenido automáticamente
SEMRUSH_AUTO_SCRAPE = True


# ============================================================================
# CONFIGURACIÓN DE LA APLICACIÓN
# ============================================================================

# Información de la app
APP_TITLE = get_secret('APP_TITLE') or 'PcComponentes Content Generator'
APP_VERSION = '4.2.0'
PAGE_ICON = '🚀'

# Modo debug
DEBUG_MODE = (get_secret('DEBUG_MODE') or 'False').lower() == 'true'

# Fecha de conocimiento de Claude
CLAUDE_KNOWLEDGE_CUTOFF = datetime(2025, 1, 31)


# ============================================================================
# CONFIGURACIÓN DE GOOGLE SEARCH CONSOLE
# ============================================================================

# Ruta al CSV de GSC
GSC_CSV_PATH = get_secret('GSC_CSV_PATH') or 'gsc_keywords.csv'

# Habilitar verificación GSC
GSC_VERIFICATION_ENABLED = (get_secret('GSC_VERIFICATION_ENABLED') or 'True').lower() == 'true'

# Período del dataset actual (ACTUALIZAR CUANDO SE RENUEVE EL CSV)
GSC_DATASET_START = datetime(2025, 10, 18)
GSC_DATASET_END = datetime(2025, 11, 17)

# Umbrales de alerta para freshness
GSC_DAYS_WARNING = int(get_secret('GSC_DAYS_WARNING') or '30')
GSC_DAYS_CRITICAL = int(get_secret('GSC_DAYS_CRITICAL') or '60')

# Configuración de matching de keywords
GSC_EXACT_MATCH_THRESHOLD = 1.0
GSC_HIGH_SIMILARITY_THRESHOLD = float(get_secret('GSC_HIGH_SIMILARITY_THRESHOLD') or '0.85')
GSC_MEDIUM_SIMILARITY_THRESHOLD = float(get_secret('GSC_MEDIUM_SIMILARITY_THRESHOLD') or '0.70')
GSC_ENABLE_CONTAINS_MATCH = (get_secret('GSC_ENABLE_CONTAINS_MATCH') or 'True').lower() == 'true'

# Mostrar disclaimer de freshness por defecto
GSC_SHOW_FRESHNESS_DISCLAIMER = (get_secret('GSC_SHOW_FRESHNESS_DISCLAIMER') or 'True').lower() == 'true'


# ============================================================================
# CONFIGURACIÓN DE SCRAPING
# ============================================================================

# n8n webhook para scraping de PDPs
N8N_WEBHOOK_URL = get_secret('N8N_WEBHOOK_URL')

# Zenrows API key (para scraping avanzado)
ZENROWS_API_KEY = get_secret('ZENROWS_API_KEY')

# User Agent para requests
USER_AGENT = get_secret('USER_AGENT') or (
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
    'AppleWebKit/537.36 (KHTML, like Gecko) '
    'Chrome/120.0.0.0 Safari/537.36'
)

# Timeout para requests (segundos)
REQUEST_TIMEOUT = int(get_secret('REQUEST_TIMEOUT') or '30')


# ============================================================================
# CONFIGURACIÓN DE CATEGORÍAS
# ============================================================================

# Ruta al CSV de categorías
CATEGORIES_CSV_PATH = get_secret('CATEGORIES_CSV_PATH') or 'data/categories.csv'


# ============================================================================
# CONFIGURACIÓN DE LOGGING
# ============================================================================

# Nivel de logging
LOG_LEVEL = get_secret('LOG_LEVEL') or 'INFO'

# Archivo de logs
LOG_FILE = get_secret('LOG_FILE') or 'logs/app.log'

# Habilitar logging a archivo
ENABLE_FILE_LOGGING = (get_secret('ENABLE_FILE_LOGGING') or 'False').lower() == 'true'


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
CACHE_TTL = int(get_secret('CACHE_TTL') or '3600')


# ============================================================================
# CONFIGURACIÓN DE UI
# ============================================================================

# Tema de colores (PcComponentes)
PRIMARY_COLOR = '#FF6000'  # Naranja PcComponentes
SECONDARY_COLOR = '#170453'  # Azul oscuro
BACKGROUND_COLOR = '#FFFFFF'
TEXT_COLOR = '#262730'


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
- 🔄 Modo reescritura con análisis competitivo (SEMrush)
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

# Mensaje de SEMrush no configurado
NO_SEMRUSH_MESSAGE = """
💡 **SEMrush no configurado**

Para obtener competidores automáticamente, configura tu API key de SEMrush:

**Streamlit Cloud**: Settings > Secrets:
```toml
[semrush]
api_key = "tu-api-key"
database = "es"
```

**Local**: En archivo `.env`:
```
SEMRUSH_API_KEY=tu-api-key
```

Sin SEMrush, puedes introducir URLs de competidores manualmente.
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
        'has_claude_key': bool(CLAUDE_API_KEY),
        'semrush_enabled': SEMRUSH_ENABLED,
        'semrush_database': SEMRUSH_DATABASE if SEMRUSH_ENABLED else None,
        'gsc_enabled': GSC_VERIFICATION_ENABLED,
        'gsc_csv_exists': os.path.exists(GSC_CSV_PATH) if GSC_CSV_PATH else False,
        'n8n_configured': bool(N8N_WEBHOOK_URL),
        'zenrows_configured': bool(ZENROWS_API_KEY)
    }


def get_gsc_dataset_info() -> dict:
    """
    Obtiene información del dataset de GSC.
    
    Returns:
        Dict con información del período y freshness
    """
    
    from datetime import timedelta
    
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


def validate_semrush_config() -> Tuple[bool, str]:
    """
    Valida la configuración de SEMrush.
    
    Returns:
        Tuple[bool, str]: (es_válida, mensaje)
    """
    
    if not SEMRUSH_API_KEY:
        return False, "API key de SEMrush no configurada"
    
    if SEMRUSH_DATABASE not in ['es', 'us', 'uk', 'fr', 'de', 'it', 'pt', 'mx', 'ar', 'co']:
        return False, f"Base de datos '{SEMRUSH_DATABASE}' no válida"
    
    return True, "Configuración de SEMrush válida"


# ============================================================================
# HELPER PARA MOSTRAR ESTADO DE CONFIGURACIÓN
# ============================================================================

def render_config_status() -> None:
    """
    Renderiza el estado de configuración en Streamlit.
    Útil para debug y para mostrar al usuario qué está configurado.
    """
    
    import streamlit as st
    
    config = get_configuration_summary()
    
    st.markdown("### ⚙️ Estado de Configuración")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**APIs:**")
        
        # Claude
        if config['has_claude_key']:
            st.success("✅ Claude API configurada")
        else:
            st.error("❌ Claude API no configurada")
        
        # SEMrush
        if config['semrush_enabled']:
            st.success(f"✅ SEMrush API configurada (DB: {config['semrush_database']})")
        else:
            st.warning("⚠️ SEMrush no configurado (modo manual)")
    
    with col2:
        st.markdown("**Integraciones:**")
        
        # GSC
        if config['gsc_enabled']:
            if config['gsc_csv_exists']:
                st.success("✅ GSC habilitado con datos")
            else:
                st.warning("⚠️ GSC habilitado pero sin CSV")
        else:
            st.info("ℹ️ GSC deshabilitado")
        
        # n8n
        if config['n8n_configured']:
            st.success("✅ n8n webhook configurado")
        else:
            st.info("ℹ️ n8n no configurado")


# ============================================================================
# SECRETS TEMPLATE (para documentación)
# ============================================================================

SECRETS_TEMPLATE = """
# ============================================================================
# Streamlit Secrets Template - PcComponentes Content Generator
# ============================================================================

# Claude API (REQUERIDO)
[api]
claude_key = "sk-ant-..."

# SEMrush API (OPCIONAL - para análisis automático de competidores)
[semrush]
api_key = "tu-semrush-api-key"
database = "es"  # es, us, uk, fr, de, it, pt, mx, ar, co
default_results = 5
timeout = 30

# Configuración general
[settings]
debug_mode = false
app_version = "4.2.0"

# n8n (OPCIONAL - para scraping avanzado de PDPs)
[n8n]
webhook_url = "https://tu-n8n.com/webhook/scrape"

# Zenrows (OPCIONAL - para scraping con JavaScript rendering)
[zenrows]
api_key = "tu-zenrows-key"
"""


# ============================================================================
# TIPO HINTS PARA EXPORTACIÓN
# ============================================================================

from typing import Tuple


# ============================================================================
# EXPORTAR CONFIGURACIÓN
# ============================================================================

__all__ = [
    # API Keys
    'CLAUDE_API_KEY',
    'SEMRUSH_API_KEY',
    
    # Claude
    'CLAUDE_MODEL',
    'MAX_TOKENS',
    'TEMPERATURE',
    
    # SEMrush
    'SEMRUSH_ENABLED',
    'SEMRUSH_DATABASE',
    'SEMRUSH_DEFAULT_RESULTS',
    'SEMRUSH_MAX_RESULTS',
    'SEMRUSH_TIMEOUT',
    'SEMRUSH_RATE_LIMIT_DELAY',
    'SEMRUSH_EXCLUDE_DOMAINS',
    'SEMRUSH_AUTO_SCRAPE',
    
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
    'NO_SEMRUSH_MESSAGE',
    
    # Funciones
    'validate_configuration',
    'get_configuration_summary',
    'get_gsc_dataset_info',
    'validate_semrush_config',
    'render_config_status',
    'get_secret',
    
    # Template
    'SECRETS_TEMPLATE'
]

__version__ = "4.2.0"
