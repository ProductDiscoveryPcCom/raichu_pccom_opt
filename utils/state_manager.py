"""
State Manager - PcComponentes Content Generator
Versión 4.2.0

Gestión centralizada del estado de la aplicación Streamlit.
Maneja el estado de generación, historial, configuración y persistencia.

Este módulo proporciona:
- Inicialización del estado de sesión
- Guardado/recuperación de generaciones
- Historial de contenido generado
- Gestión de configuración persistente
- Utilidades de limpieza y reset

Autor: PcComponentes - Product Discovery & Content
"""

import json
import hashlib
from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from pathlib import Path

import streamlit as st


# ============================================================================
# CONSTANTES Y CONFIGURACIÓN
# ============================================================================

# Versión del módulo
__version__ = "4.2.0"

# Claves del estado de sesión
STATE_KEYS = {
    'initialized': 'app_initialized',
    'generation_history': 'generation_history',
    'current_generation': 'current_generation',
    'generation_stages': 'generation_stages',
    'config': 'app_config',
    'form_data': 'form_data',
    'competitors_data': 'competitors_data',
    'pdp_data': 'pdp_data',
    'semrush_data': 'semrush_data',
    'gsc_data': 'gsc_data',
    'error_log': 'error_log',
    'debug_mode': 'debug_mode',
}

# Número máximo de generaciones en historial
MAX_HISTORY_SIZE = 50

# Número máximo de etapas por generación
MAX_STAGES = 5

# Directorio para persistencia (opcional)
PERSISTENCE_DIR = Path(".streamlit/state")


# ============================================================================
# INICIALIZACIÓN DEL ESTADO
# ============================================================================

def init_session_state() -> None:
    """
    Inicializa todas las claves necesarias en st.session_state.
    
    Debe llamarse al inicio de la aplicación para garantizar que
    todas las claves existen con valores por defecto.
    
    Example:
        >>> init_session_state()
        >>> assert 'generation_history' in st.session_state
    """
    # Estado de inicialización
    if STATE_KEYS['initialized'] not in st.session_state:
        st.session_state[STATE_KEYS['initialized']] = True
        
        # Historial de generaciones
        st.session_state[STATE_KEYS['generation_history']] = []
        
        # Generación actual
        st.session_state[STATE_KEYS['current_generation']] = None
        
        # Etapas de la generación actual
        st.session_state[STATE_KEYS['generation_stages']] = {}
        
        # Configuración de la app
        st.session_state[STATE_KEYS['config']] = get_default_config()
        
        # Datos del formulario
        st.session_state[STATE_KEYS['form_data']] = {}
        
        # Datos de competidores
        st.session_state[STATE_KEYS['competitors_data']] = []
        
        # Datos del PDP
        st.session_state[STATE_KEYS['pdp_data']] = None
        
        # Datos de SEMrush
        st.session_state[STATE_KEYS['semrush_data']] = None
        
        # Datos de GSC
        st.session_state[STATE_KEYS['gsc_data']] = None
        
        # Log de errores
        st.session_state[STATE_KEYS['error_log']] = []
        
        # Modo debug
        st.session_state[STATE_KEYS['debug_mode']] = False


def get_default_config() -> Dict[str, Any]:
    """
    Retorna la configuración por defecto de la aplicación.
    
    Returns:
        Dict con valores de configuración por defecto
    """
    return {
        'model': 'claude-sonnet-4-20250514',
        'max_tokens': 16000,
        'temperature': 0.7,
        'default_length': 1500,
        'auto_save': True,
        'show_debug': False,
        'theme': 'light',
        'language': 'es',
    }


def is_initialized() -> bool:
    """
    Verifica si el estado de sesión está inicializado.
    
    Returns:
        True si está inicializado, False en caso contrario
    """
    return st.session_state.get(STATE_KEYS['initialized'], False)


def ensure_initialized() -> None:
    """
    Asegura que el estado esté inicializado, inicializándolo si es necesario.
    """
    if not is_initialized():
        init_session_state()


# ============================================================================
# GESTIÓN DE GENERACIONES - FUNCIONES PRINCIPALES
# ============================================================================

def save_generation_to_state(
    stage_or_data: Union[int, Dict[str, Any]],
    content: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
    **kwargs
) -> str:
    """
    Guarda una generación completa en el estado de sesión.
    
    COMPATIBLE CON DOS FIRMAS:
    
    1. Firma nueva (recomendada): save_generation_to_state(data: Dict)
       >>> save_generation_to_state({
       ...     'stage': 1,
       ...     'content': '<article>...</article>',
       ...     'keyword': 'test'
       ... })
    
    2. Firma antigua (compatibilidad): save_generation_to_state(stage, content, metadata)
       >>> save_generation_to_state(1, '<article>...</article>', {'keyword': 'test'})
    
    Args:
        stage_or_data: Si es int, es el número de etapa (firma antigua).
                      Si es dict, contiene todos los datos (firma nueva).
        content: Contenido HTML (solo para firma antigua)
        metadata: Metadatos adicionales (solo para firma antigua)
        **kwargs: Argumentos adicionales para ambas firmas
            
    Returns:
        str: ID único de la generación guardada
        
    Notes:
        - Genera automáticamente ID único basado en contenido y timestamp
        - Añade timestamp si no se proporciona
        - Actualiza tanto la generación actual como el historial
        - Limita el historial a MAX_HISTORY_SIZE elementos
    """
    ensure_initialized()
    
    # Detectar qué firma se está usando
    if isinstance(stage_or_data, dict):
        # FIRMA NUEVA: save_generation_to_state(data: Dict)
        data = stage_or_data
    else:
        # FIRMA ANTIGUA: save_generation_to_state(stage, content, metadata)
        data = {
            'stage': stage_or_data,
            'content': content or '',
            'metadata': metadata or {},
            **kwargs
        }
    
    # Extraer campos del diccionario
    stage = data.get('stage', 1)
    content_str = data.get('content', '')
    metadata_dict = data.get('metadata', {})
    
    # Generar timestamp si no existe
    timestamp = data.get('timestamp') or datetime.now().isoformat()
    
    # Generar ID único
    generation_id = _generate_id(content_str, timestamp)
    
    # Construir objeto de generación completo
    generation = {
        'id': generation_id,
        'stage': stage,
        'content': content_str,
        'timestamp': timestamp,
        'keyword': data.get('keyword', ''),
        'mode': data.get('mode', 'new'),
        'word_count': data.get('word_count', _count_words(content_str)),
        'generation_time': data.get('generation_time', 0),
        'model': data.get('model', ''),
        'tokens_used': data.get('tokens_used', 0),
        'metadata': {
            **metadata_dict,
            'arquetipo': data.get('arquetipo'),
            'target_length': data.get('target_length'),
            'links': data.get('links'),
            'competitor_analysis': data.get('competitor_analysis'),
        }
    }
    
    # Guardar en etapas de generación actual
    stages = st.session_state.get(STATE_KEYS['generation_stages'], {})
    stages[stage] = generation
    st.session_state[STATE_KEYS['generation_stages']] = stages
    
    # Actualizar generación actual (última etapa)
    st.session_state[STATE_KEYS['current_generation']] = generation
    
    # Añadir al historial si es etapa final (3) o única
    if stage >= 3 or data.get('is_final', False):
        _add_to_history(generation)
    
    return generation_id


def save_stage_content(
    stage: int,
    content: str,
    metadata: Optional[Dict[str, Any]] = None,
    **kwargs
) -> str:
    """
    Guarda el contenido de una etapa específica.
    
    Función de conveniencia que construye el diccionario y llama a
    save_generation_to_state.
    
    Args:
        stage: Número de etapa (1, 2, 3)
        content: Contenido HTML generado
        metadata: Metadatos adicionales opcionales
        **kwargs: Argumentos adicionales (keyword, mode, etc.)
        
    Returns:
        str: ID único de la generación guardada
        
    Example:
        >>> gen_id = save_stage_content(
        ...     stage=1,
        ...     content='<article>...</article>',
        ...     keyword='monitores gaming'
        ... )
    """
    data = {
        'stage': stage,
        'content': content,
        'metadata': metadata or {},
        **kwargs
    }
    return save_generation_to_state(data)


def get_current_generation() -> Optional[Dict[str, Any]]:
    """
    Obtiene la generación actual (última guardada).
    
    Returns:
        Dict con datos de la generación o None si no hay ninguna
    """
    ensure_initialized()
    return st.session_state.get(STATE_KEYS['current_generation'])


def get_stage_content(stage: int) -> Optional[Dict[str, Any]]:
    """
    Obtiene el contenido de una etapa específica.
    
    Args:
        stage: Número de etapa (1, 2, 3)
        
    Returns:
        Dict con datos de la etapa o None si no existe
    """
    ensure_initialized()
    stages = st.session_state.get(STATE_KEYS['generation_stages'], {})
    return stages.get(stage)


def get_all_stages() -> Dict[int, Dict[str, Any]]:
    """
    Obtiene todas las etapas de la generación actual.
    
    Returns:
        Dict con todas las etapas indexadas por número
    """
    ensure_initialized()
    return st.session_state.get(STATE_KEYS['generation_stages'], {})


def clear_current_generation() -> None:
    """
    Limpia la generación actual y todas sus etapas.
    
    Útil al iniciar una nueva generación.
    """
    ensure_initialized()
    st.session_state[STATE_KEYS['current_generation']] = None
    st.session_state[STATE_KEYS['generation_stages']] = {}


# ============================================================================
# HISTORIAL DE GENERACIONES
# ============================================================================

def get_generation_history() -> List[Dict[str, Any]]:
    """
    Obtiene el historial completo de generaciones.
    
    Returns:
        Lista de generaciones ordenadas por timestamp (más reciente primero)
    """
    ensure_initialized()
    history = st.session_state.get(STATE_KEYS['generation_history'], [])
    return sorted(history, key=lambda x: x.get('timestamp', ''), reverse=True)


def get_generation_by_id(generation_id: str) -> Optional[Dict[str, Any]]:
    """
    Busca una generación por su ID único.
    
    Args:
        generation_id: ID de la generación a buscar
        
    Returns:
        Dict con datos de la generación o None si no se encuentra
    """
    ensure_initialized()
    history = st.session_state.get(STATE_KEYS['generation_history'], [])
    for gen in history:
        if gen.get('id') == generation_id:
            return gen
    return None


def delete_generation(generation_id: str) -> bool:
    """
    Elimina una generación del historial.
    
    Args:
        generation_id: ID de la generación a eliminar
        
    Returns:
        True si se eliminó, False si no se encontró
    """
    ensure_initialized()
    history = st.session_state.get(STATE_KEYS['generation_history'], [])
    original_length = len(history)
    
    st.session_state[STATE_KEYS['generation_history']] = [
        gen for gen in history if gen.get('id') != generation_id
    ]
    
    return len(st.session_state[STATE_KEYS['generation_history']]) < original_length


def clear_history() -> int:
    """
    Limpia todo el historial de generaciones.
    
    Returns:
        Número de generaciones eliminadas
    """
    ensure_initialized()
    history = st.session_state.get(STATE_KEYS['generation_history'], [])
    count = len(history)
    st.session_state[STATE_KEYS['generation_history']] = []
    return count


def _add_to_history(generation: Dict[str, Any]) -> None:
    """
    Añade una generación al historial interno.
    
    Args:
        generation: Datos de la generación a añadir
        
    Notes:
        - Evita duplicados por ID
        - Mantiene el historial limitado a MAX_HISTORY_SIZE
    """
    history = st.session_state.get(STATE_KEYS['generation_history'], [])
    
    # Evitar duplicados
    history = [g for g in history if g.get('id') != generation.get('id')]
    
    # Añadir nueva generación al inicio
    history.insert(0, generation)
    
    # Limitar tamaño
    if len(history) > MAX_HISTORY_SIZE:
        history = history[:MAX_HISTORY_SIZE]
    
    st.session_state[STATE_KEYS['generation_history']] = history


# ============================================================================
# GESTIÓN DE DATOS EXTERNOS (PDP, COMPETIDORES, SEMRUSH, GSC)
# ============================================================================

def save_pdp_data(pdp_data: Optional[Dict[str, Any]]) -> None:
    """
    Guarda los datos del PDP (Product Detail Page) scrapeados.
    
    Args:
        pdp_data: Diccionario con datos del producto o None
    """
    ensure_initialized()
    st.session_state[STATE_KEYS['pdp_data']] = pdp_data


def get_pdp_data() -> Optional[Dict[str, Any]]:
    """
    Obtiene los datos del PDP guardados.
    
    Returns:
        Dict con datos del PDP o None
    """
    ensure_initialized()
    return st.session_state.get(STATE_KEYS['pdp_data'])


def save_competitors_data(competitors: List[Dict[str, Any]]) -> None:
    """
    Guarda los datos de competidores scrapeados.
    
    Args:
        competitors: Lista de dicts con datos de competidores
    """
    ensure_initialized()
    st.session_state[STATE_KEYS['competitors_data']] = competitors


def get_competitors_data() -> List[Dict[str, Any]]:
    """
    Obtiene los datos de competidores guardados.
    
    Returns:
        Lista de dicts con datos de competidores
    """
    ensure_initialized()
    return st.session_state.get(STATE_KEYS['competitors_data'], [])


def save_semrush_data(semrush_data: Optional[Dict[str, Any]]) -> None:
    """
    Guarda los datos de SEMrush.
    
    Args:
        semrush_data: Diccionario con datos de SEMrush o None
    """
    ensure_initialized()
    st.session_state[STATE_KEYS['semrush_data']] = semrush_data


def get_semrush_data() -> Optional[Dict[str, Any]]:
    """
    Obtiene los datos de SEMrush guardados.
    
    Returns:
        Dict con datos de SEMrush o None
    """
    ensure_initialized()
    return st.session_state.get(STATE_KEYS['semrush_data'])


def save_gsc_data(gsc_data: Optional[Dict[str, Any]]) -> None:
    """
    Guarda los datos de Google Search Console.
    
    Args:
        gsc_data: Diccionario con datos de GSC o None
    """
    ensure_initialized()
    st.session_state[STATE_KEYS['gsc_data']] = gsc_data


def get_gsc_data() -> Optional[Dict[str, Any]]:
    """
    Obtiene los datos de GSC guardados.
    
    Returns:
        Dict con datos de GSC o None
    """
    ensure_initialized()
    return st.session_state.get(STATE_KEYS['gsc_data'])


def clear_external_data() -> None:
    """
    Limpia todos los datos externos (PDP, competidores, SEMrush, GSC).
    
    Útil al cambiar de keyword o modo de generación.
    """
    ensure_initialized()
    st.session_state[STATE_KEYS['pdp_data']] = None
    st.session_state[STATE_KEYS['competitors_data']] = []
    st.session_state[STATE_KEYS['semrush_data']] = None
    st.session_state[STATE_KEYS['gsc_data']] = None


# ============================================================================
# GESTIÓN DE FORMULARIO
# ============================================================================

def save_form_data(form_data: Dict[str, Any]) -> None:
    """
    Guarda los datos del formulario de entrada.
    
    Args:
        form_data: Diccionario con valores del formulario
    """
    ensure_initialized()
    current = st.session_state.get(STATE_KEYS['form_data'], {})
    current.update(form_data)
    st.session_state[STATE_KEYS['form_data']] = current


def get_form_data() -> Dict[str, Any]:
    """
    Obtiene los datos del formulario guardados.
    
    Returns:
        Dict con datos del formulario
    """
    ensure_initialized()
    return st.session_state.get(STATE_KEYS['form_data'], {})


def get_form_value(key: str, default: Any = None) -> Any:
    """
    Obtiene un valor específico del formulario.
    
    Args:
        key: Clave del valor a obtener
        default: Valor por defecto si no existe
        
    Returns:
        Valor del formulario o default
    """
    form_data = get_form_data()
    return form_data.get(key, default)


def clear_form_data() -> None:
    """
    Limpia todos los datos del formulario.
    """
    ensure_initialized()
    st.session_state[STATE_KEYS['form_data']] = {}


# ============================================================================
# CONFIGURACIÓN DE LA APLICACIÓN
# ============================================================================

def get_config() -> Dict[str, Any]:
    """
    Obtiene la configuración actual de la aplicación.
    
    Returns:
        Dict con configuración
    """
    ensure_initialized()
    return st.session_state.get(STATE_KEYS['config'], get_default_config())


def update_config(updates: Dict[str, Any]) -> None:
    """
    Actualiza la configuración de la aplicación.
    
    Args:
        updates: Dict con valores a actualizar
    """
    ensure_initialized()
    config = get_config()
    config.update(updates)
    st.session_state[STATE_KEYS['config']] = config


def get_config_value(key: str, default: Any = None) -> Any:
    """
    Obtiene un valor específico de configuración.
    
    Args:
        key: Clave del valor a obtener
        default: Valor por defecto si no existe
        
    Returns:
        Valor de configuración o default
    """
    config = get_config()
    return config.get(key, default)


def reset_config() -> None:
    """
    Resetea la configuración a valores por defecto.
    """
    ensure_initialized()
    st.session_state[STATE_KEYS['config']] = get_default_config()


# ============================================================================
# LOGGING Y DEBUG
# ============================================================================

def log_error(error: Union[str, Exception], context: Optional[Dict] = None) -> None:
    """
    Registra un error en el log de la sesión.
    
    Args:
        error: Mensaje de error o excepción
        context: Contexto adicional opcional
    """
    ensure_initialized()
    
    error_entry = {
        'timestamp': datetime.now().isoformat(),
        'error': str(error),
        'type': type(error).__name__ if isinstance(error, Exception) else 'str',
        'context': context or {}
    }
    
    error_log = st.session_state.get(STATE_KEYS['error_log'], [])
    error_log.append(error_entry)
    
    # Limitar a últimos 100 errores
    if len(error_log) > 100:
        error_log = error_log[-100:]
    
    st.session_state[STATE_KEYS['error_log']] = error_log


def get_error_log() -> List[Dict[str, Any]]:
    """
    Obtiene el log de errores de la sesión.
    
    Returns:
        Lista de errores registrados
    """
    ensure_initialized()
    return st.session_state.get(STATE_KEYS['error_log'], [])


def clear_error_log() -> None:
    """
    Limpia el log de errores.
    """
    ensure_initialized()
    st.session_state[STATE_KEYS['error_log']] = []


def set_debug_mode(enabled: bool) -> None:
    """
    Activa o desactiva el modo debug.
    
    Args:
        enabled: True para activar, False para desactivar
    """
    ensure_initialized()
    st.session_state[STATE_KEYS['debug_mode']] = enabled


def is_debug_mode() -> bool:
    """
    Verifica si el modo debug está activo.
    
    Returns:
        True si está activo, False en caso contrario
    """
    ensure_initialized()
    return st.session_state.get(STATE_KEYS['debug_mode'], False)


# ============================================================================
# PERSISTENCIA OPCIONAL (ARCHIVO)
# ============================================================================

def save_state_to_file(filepath: Optional[Path] = None) -> bool:
    """
    Guarda el estado actual a un archivo JSON.
    
    Args:
        filepath: Ruta del archivo (usa default si no se especifica)
        
    Returns:
        True si se guardó correctamente, False en caso de error
    """
    try:
        filepath = filepath or PERSISTENCE_DIR / "state.json"
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        # Construir estado serializable
        state = {
            'generation_history': get_generation_history(),
            'config': get_config(),
            'form_data': get_form_data(),
            'saved_at': datetime.now().isoformat()
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
        
        return True
    except Exception as e:
        log_error(e, {'action': 'save_state_to_file', 'filepath': str(filepath)})
        return False


def load_state_from_file(filepath: Optional[Path] = None) -> bool:
    """
    Carga el estado desde un archivo JSON.
    
    Args:
        filepath: Ruta del archivo (usa default si no se especifica)
        
    Returns:
        True si se cargó correctamente, False en caso de error
    """
    try:
        filepath = filepath or PERSISTENCE_DIR / "state.json"
        
        if not filepath.exists():
            return False
        
        with open(filepath, 'r', encoding='utf-8') as f:
            state = json.load(f)
        
        # Restaurar estado
        ensure_initialized()
        
        if 'generation_history' in state:
            st.session_state[STATE_KEYS['generation_history']] = state['generation_history']
        
        if 'config' in state:
            st.session_state[STATE_KEYS['config']] = state['config']
        
        if 'form_data' in state:
            st.session_state[STATE_KEYS['form_data']] = state['form_data']
        
        return True
    except Exception as e:
        log_error(e, {'action': 'load_state_from_file', 'filepath': str(filepath)})
        return False


# ============================================================================
# UTILIDADES INTERNAS
# ============================================================================

def _generate_id(content: str, timestamp: str) -> str:
    """
    Genera un ID único basado en contenido y timestamp.
    
    Args:
        content: Contenido para hashear
        timestamp: Timestamp ISO
        
    Returns:
        str: ID único de 12 caracteres
    """
    hash_input = f"{content[:500]}{timestamp}".encode('utf-8')
    return hashlib.sha256(hash_input).hexdigest()[:12]


def _count_words(html_content: str) -> int:
    """
    Cuenta palabras en contenido HTML.
    
    Args:
        html_content: Contenido HTML
        
    Returns:
        int: Número de palabras
    """
    if not html_content:
        return 0
    
    import re
    # Remover tags HTML
    text = re.sub(r'<[^>]+>', ' ', html_content)
    # Remover espacios múltiples
    text = ' '.join(text.split())
    # Contar palabras
    words = text.split()
    return len(words)


# ============================================================================
# RESET COMPLETO
# ============================================================================

def reset_all_state() -> None:
    """
    Resetea completamente todo el estado de la sesión.
    
    ⚠️ CUIDADO: Esta acción elimina TODO el estado incluyendo historial.
    """
    # Limpiar todas las claves conocidas
    for key in STATE_KEYS.values():
        if key in st.session_state:
            del st.session_state[key]
    
    # Reinicializar
    init_session_state()


def get_state_summary() -> Dict[str, Any]:
    """
    Obtiene un resumen del estado actual para debugging.
    
    Returns:
        Dict con resumen del estado
    """
    ensure_initialized()
    
    history = get_generation_history()
    stages = get_all_stages()
    
    return {
        'initialized': is_initialized(),
        'history_count': len(history),
        'current_stages': list(stages.keys()),
        'has_current_generation': get_current_generation() is not None,
        'has_pdp_data': get_pdp_data() is not None,
        'competitors_count': len(get_competitors_data()),
        'has_semrush_data': get_semrush_data() is not None,
        'has_gsc_data': get_gsc_data() is not None,
        'error_count': len(get_error_log()),
        'debug_mode': is_debug_mode(),
        'config': get_config()
    }


# ============================================================================
# COMPATIBILIDAD HACIA ATRÁS (DEPRECATED)
# ============================================================================

def save_generation(stage: int, content: str, metadata: Optional[Dict] = None) -> str:
    """
    DEPRECATED: Usa save_generation_to_state() o save_stage_content() en su lugar.
    
    Mantiene compatibilidad con código antiguo.
    """
    import warnings
    warnings.warn(
        "save_generation() está deprecated. Usa save_generation_to_state() o save_stage_content().",
        DeprecationWarning,
        stacklevel=2
    )
    return save_stage_content(stage, content, metadata)


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    # Inicialización
    'init_session_state',
    'is_initialized',
    'ensure_initialized',
    
    # Generaciones
    'save_generation_to_state',
    'save_stage_content',
    'get_current_generation',
    'get_stage_content',
    'get_all_stages',
    'clear_current_generation',
    
    # Historial
    'get_generation_history',
    'get_generation_by_id',
    'delete_generation',
    'clear_history',
    
    # Datos externos
    'save_pdp_data',
    'get_pdp_data',
    'save_competitors_data',
    'get_competitors_data',
    'save_semrush_data',
    'get_semrush_data',
    'save_gsc_data',
    'get_gsc_data',
    'clear_external_data',
    
    # Formulario
    'save_form_data',
    'get_form_data',
    'get_form_value',
    'clear_form_data',
    
    # Configuración
    'get_config',
    'update_config',
    'get_config_value',
    'reset_config',
    
    # Logging
    'log_error',
    'get_error_log',
    'clear_error_log',
    'set_debug_mode',
    'is_debug_mode',
    
    # Persistencia
    'save_state_to_file',
    'load_state_from_file',
    
    # Utilidades
    'reset_all_state',
    'get_state_summary',
    
    # Constantes
    'STATE_KEYS',
    'MAX_HISTORY_SIZE',
]
