"""
State Manager - PcComponentes Content Generator
Versión 4.1.1

Utilidades para gestionar el estado de la sesión en Streamlit.

Autor: PcComponentes - Product Discovery & Content
"""

import streamlit as st
from typing import Any, Dict, Optional
from datetime import datetime


# ============================================================================
# INICIALIZACIÓN DE SESSION STATE
# ============================================================================

def initialize_session_state() -> None:
    """
    Inicializa todas las variables de session state necesarias.
    
    Notes:
        - Se ejecuta una sola vez al inicio de la app
        - Define valores por defecto para todas las variables
        - Previene KeyError en accesos posteriores
    """
    
    # Modo actual (new o rewrite)
    if 'current_mode' not in st.session_state:
        st.session_state.current_mode = 'new'
    
    # Estado de generación
    if 'generation_in_progress' not in st.session_state:
        st.session_state.generation_in_progress = False
    
    if 'current_stage' not in st.session_state:
        st.session_state.current_stage = 0
    
    # Resultados de cada etapa
    if 'draft_html' not in st.session_state:
        st.session_state.draft_html = None
    
    if 'analysis_json' not in st.session_state:
        st.session_state.analysis_json = None
    
    if 'final_html' not in st.session_state:
        st.session_state.final_html = None
    
    # Configuración de generación
    if 'target_length' not in st.session_state:
        st.session_state.target_length = 1500
    
    if 'generation_config' not in st.session_state:
        st.session_state.generation_config = {}
    
    # Datos de producto scrapeado
    if 'scraped_pdp_data' not in st.session_state:
        st.session_state.scraped_pdp_data = None
    
    # Modo rewrite específico
    if 'rewrite_competitors_data' not in st.session_state:
        st.session_state.rewrite_competitors_data = None
    
    if 'rewrite_analysis' not in st.session_state:
        st.session_state.rewrite_analysis = None
    
    if 'rewrite_gsc_analysis' not in st.session_state:
        st.session_state.rewrite_gsc_analysis = None
    
    if 'last_rewrite_keyword' not in st.session_state:
        st.session_state.last_rewrite_keyword = ''
    
    # Análisis GSC
    if 'gsc_analysis' not in st.session_state:
        st.session_state.gsc_analysis = None
    
    # Metadata de generación
    if 'generation_metadata' not in st.session_state:
        st.session_state.generation_metadata = {}


# ============================================================================
# LIMPIEZA DE ESTADO
# ============================================================================

def clear_generation_state() -> None:
    """
    Limpia el estado relacionado con la generación actual.
    
    Notes:
        - Mantiene configuración general de la app
        - Limpia solo resultados de generación
        - Útil al cambiar de modo o iniciar nueva generación
    """
    
    st.session_state.generation_in_progress = False
    st.session_state.current_stage = 0
    st.session_state.draft_html = None
    st.session_state.analysis_json = None
    st.session_state.final_html = None
    st.session_state.generation_config = {}
    st.session_state.generation_metadata = {}


def clear_all_state() -> None:
    """
    Limpia TODO el estado de la sesión.
    
    Notes:
        - Útil para "empezar de cero"
        - Ejecutar solo cuando el usuario lo solicita explícitamente
    """
    
    # Obtener todas las keys actuales
    keys_to_delete = list(st.session_state.keys())
    
    # Eliminar todas
    for key in keys_to_delete:
        del st.session_state[key]
    
    # Re-inicializar
    initialize_session_state()


def clear_mode_specific_state(mode: str) -> None:
    """
    Limpia estado específico de un modo (new o rewrite).
    
    Args:
        mode: 'new' o 'rewrite'
        
    Notes:
        - Útil al cambiar entre modos
        - Mantiene estado general de la app
    """
    
    if mode == 'rewrite':
        st.session_state.rewrite_competitors_data = None
        st.session_state.rewrite_analysis = None
        st.session_state.rewrite_gsc_analysis = None
        st.session_state.last_rewrite_keyword = ''
    
    elif mode == 'new':
        st.session_state.scraped_pdp_data = None
        st.session_state.gsc_analysis = None
    
    # Siempre limpiar resultados de generación
    clear_generation_state()


# ============================================================================
# GUARDADO DE DATOS
# ============================================================================

def save_generation_to_state(
    stage: int,
    content: str,
    metadata: Optional[Dict] = None
) -> None:
    """
    Guarda el resultado de una etapa de generación en session state.
    
    Args:
        stage: Número de etapa (1, 2 o 3)
        content: Contenido generado (HTML o JSON)
        metadata: Metadata adicional opcional
        
    Notes:
        - Etapa 1: Borrador HTML
        - Etapa 2: Análisis JSON
        - Etapa 3: HTML final
    """
    
    # Guardar contenido según etapa
    if stage == 1:
        st.session_state.draft_html = content
    elif stage == 2:
        st.session_state.analysis_json = content
    elif stage == 3:
        st.session_state.final_html = content
    
    # Actualizar stage actual
    st.session_state.current_stage = max(st.session_state.current_stage, stage)
    
    # Guardar metadata si se proporciona
    if metadata:
        if 'stages' not in st.session_state.generation_metadata:
            st.session_state.generation_metadata['stages'] = {}
        
        st.session_state.generation_metadata['stages'][stage] = {
            'timestamp': datetime.now().isoformat(),
            **metadata
        }


def save_config_to_state(config: Dict) -> None:
    """
    Guarda la configuración de generación en session state.
    
    Args:
        config: Dict con la configuración completa
    """
    
    st.session_state.generation_config = config
    st.session_state.target_length = config.get('target_length', 1500)
    
    # Guardar metadata
    st.session_state.generation_metadata = {
        'mode': config.get('mode', 'new'),
        'arquetipo': config.get('arquetipo_codigo'),
        'keyword': config.get('keywords', [''])[0] if config.get('keywords') else '',
        'started_at': datetime.now().isoformat()
    }


# ============================================================================
# HELPERS
# ============================================================================

def get_generation_progress() -> Dict[str, Any]:
    """
    Obtiene el progreso actual de la generación.
    
    Returns:
        Dict con información del progreso:
        - current_stage: Etapa actual (0-3)
        - has_draft: bool
        - has_analysis: bool
        - has_final: bool
        - is_complete: bool
    """
    
    return {
        'current_stage': st.session_state.get('current_stage', 0),
        'has_draft': st.session_state.get('draft_html') is not None,
        'has_analysis': st.session_state.get('analysis_json') is not None,
        'has_final': st.session_state.get('final_html') is not None,
        'is_complete': st.session_state.get('current_stage', 0) >= 3,
        'in_progress': st.session_state.get('generation_in_progress', False)
    }


def has_any_results() -> bool:
    """
    Verifica si hay algún resultado de generación guardado.
    
    Returns:
        bool: True si hay al menos un resultado
    """
    
    return (
        st.session_state.get('draft_html') is not None or
        st.session_state.get('analysis_json') is not None or
        st.session_state.get('final_html') is not None
    )


def get_all_results() -> Dict[str, Optional[str]]:
    """
    Obtiene todos los resultados de generación.
    
    Returns:
        Dict con draft, analysis y final (pueden ser None)
    """
    
    return {
        'draft': st.session_state.get('draft_html'),
        'analysis': st.session_state.get('analysis_json'),
        'final': st.session_state.get('final_html')
    }


# ============================================================================
# CONSTANTES
# ============================================================================

# Versión del módulo
__version__ = "4.1.1"

# Etapas de generación
STAGE_DRAFT = 1
STAGE_ANALYSIS = 2
STAGE_FINAL = 3

# Modos de generación
MODE_NEW = 'new'
MODE_REWRITE = 'rewrite'
