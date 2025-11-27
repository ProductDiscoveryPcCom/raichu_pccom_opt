"""
State Manager - PcComponentes Content Generator
Versión 4.3.0

Autor: PcComponentes - Product Discovery & Content
"""

import streamlit as st
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

__version__ = "4.3.0"

STATE_KEYS = {
    'initialized': '_app_initialized',
    'current_generation': 'current_generation',
    'generation_stages': 'generation_stages',
    'generation_history': 'generation_history',
    'form_data': 'form_data',
    'config': 'app_config',
    'pdp_data': 'pdp_data',
    'competitors_data': 'competitors_data',
    'error_log': 'error_log',
    'debug_mode': 'debug_mode',
}

MAX_HISTORY_SIZE = 10
DEFAULT_CONFIG = {'model': 'claude-sonnet-4-20250514', 'max_tokens': 16000, 'temperature': 0.7, 'target_length': 1500}


def init_session_state() -> None:
    """Inicializa el estado de sesión."""
    if STATE_KEYS['initialized'] not in st.session_state:
        st.session_state[STATE_KEYS['initialized']] = True
        st.session_state[STATE_KEYS['current_generation']] = None
        st.session_state[STATE_KEYS['generation_stages']] = {}
        st.session_state[STATE_KEYS['generation_history']] = []
        st.session_state[STATE_KEYS['form_data']] = {}
        st.session_state[STATE_KEYS['config']] = DEFAULT_CONFIG.copy()
        st.session_state[STATE_KEYS['pdp_data']] = None
        st.session_state[STATE_KEYS['competitors_data']] = []
        st.session_state[STATE_KEYS['error_log']] = []
        st.session_state[STATE_KEYS['debug_mode']] = False
        st.session_state['draft_html'] = None
        st.session_state['analysis_json'] = None
        st.session_state['final_html'] = None
        st.session_state['target_length'] = 1500
        st.session_state['current_stage'] = 0
        st.session_state['rewrite_analysis'] = None


def initialize_session_state() -> None:
    """Alias para init_session_state."""
    init_session_state()


def is_initialized() -> bool:
    return st.session_state.get(STATE_KEYS['initialized'], False)


def ensure_initialized() -> None:
    if not is_initialized():
        init_session_state()


def save_generation_to_state(stage_or_data: Union[int, Dict], content: Optional[str] = None, metadata: Optional[Dict] = None, **kwargs) -> str:
    """Guarda una generación en el estado."""
    ensure_initialized()
    if isinstance(stage_or_data, dict):
        data = stage_or_data
        stage = data.get('stage', 1)
        content = data.get('content', '')
        metadata = data.get('metadata', {})
    else:
        stage = stage_or_data
        data = {'stage': stage, 'content': content or '', 'metadata': metadata or {}, **kwargs}
    
    timestamp = datetime.now().isoformat()
    generation_id = f"gen_{timestamp.replace(':', '-').replace('.', '-')}"
    
    stages = st.session_state.get(STATE_KEYS['generation_stages'], {})
    stages[stage] = {'id': generation_id, 'content': content, 'timestamp': timestamp, 'metadata': metadata or {}}
    st.session_state[STATE_KEYS['generation_stages']] = stages
    st.session_state[STATE_KEYS['current_generation']] = {'id': generation_id, 'stage': stage, 'timestamp': timestamp, **data}
    
    return generation_id


def clear_generation_state() -> None:
    """Limpia el estado de generación."""
    ensure_initialized()
    st.session_state[STATE_KEYS['current_generation']] = None
    st.session_state[STATE_KEYS['generation_stages']] = {}
    st.session_state['draft_html'] = None
    st.session_state['analysis_json'] = None
    st.session_state['final_html'] = None
    st.session_state['current_stage'] = 0
    st.session_state['rewrite_analysis'] = None


def save_form_data(data: Dict) -> None:
    """Guarda datos del formulario."""
    ensure_initialized()
    form_data = st.session_state.get(STATE_KEYS['form_data'], {})
    form_data.update(data)
    st.session_state[STATE_KEYS['form_data']] = form_data
    for key, value in data.items():
        st.session_state[key] = value


def get_form_data() -> Dict:
    """Obtiene datos del formulario."""
    ensure_initialized()
    return st.session_state.get(STATE_KEYS['form_data'], {})


def get_form_value(key: str, default: Any = None) -> Any:
    """Obtiene un valor del formulario."""
    ensure_initialized()
    if key in st.session_state:
        return st.session_state[key]
    return st.session_state.get(STATE_KEYS['form_data'], {}).get(key, default)


def save_config_to_state(config: Dict) -> None:
    """Guarda configuración."""
    ensure_initialized()
    current = st.session_state.get(STATE_KEYS['config'], DEFAULT_CONFIG.copy())
    current.update(config)
    st.session_state[STATE_KEYS['config']] = current


def get_config() -> Dict:
    ensure_initialized()
    return st.session_state.get(STATE_KEYS['config'], DEFAULT_CONFIG.copy())


def clear_all_state() -> None:
    """Limpia todo el estado."""
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    init_session_state()


def has_any_results() -> bool:
    """Verifica si hay resultados."""
    ensure_initialized()
    return any([st.session_state.get('draft_html'), st.session_state.get('analysis_json'), st.session_state.get('final_html')])


def get_all_results() -> Dict:
    """Obtiene todos los resultados."""
    ensure_initialized()
    return {
        'draft_html': st.session_state.get('draft_html'),
        'analysis_json': st.session_state.get('analysis_json'),
        'final_html': st.session_state.get('final_html'),
        'target_length': st.session_state.get('target_length', 1500),
        'current_stage': st.session_state.get('current_stage', 0)
    }


def get_generation_progress() -> Dict:
    """Obtiene progreso de generación."""
    ensure_initialized()
    stages = sum([1 for x in ['draft_html', 'analysis_json', 'final_html'] if st.session_state.get(x)])
    return {'current_stage': st.session_state.get('current_stage', 0), 'stages_completed': stages, 'total_stages': 3, 'is_complete': stages == 3}


__all__ = [
    '__version__', 'STATE_KEYS', 'MAX_HISTORY_SIZE', 'DEFAULT_CONFIG',
    'init_session_state', 'initialize_session_state', 'is_initialized', 'ensure_initialized',
    'save_generation_to_state', 'clear_generation_state',
    'save_form_data', 'get_form_data', 'get_form_value',
    'save_config_to_state', 'get_config',
    'clear_all_state', 'has_any_results', 'get_all_results', 'get_generation_progress',
]
