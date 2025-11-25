"""
Utils package - PcComponentes Content Generator
"""

from .html_utils import (
    count_words_in_html,
    extract_content_structure,
    validate_html_structure,
    validate_cms_structure,
    analyze_links
)
from .state_manager import (
    initialize_session_state,
    clear_generation_state,
    save_generation_to_state,
    save_config_to_state,
    clear_all_state,
    has_any_results,
    get_all_results,
    get_generation_progress
)

# Intentar importar GSC utils si están disponibles
try:
    from .gsc_utils import (
        load_gsc_data,
        get_dataset_age,
        analyze_keyword_coverage
    )
    GSC_AVAILABLE = True
except ImportError:
    GSC_AVAILABLE = False

__all__ = [
    # HTML utils
    'count_words_in_html',
    'extract_content_structure',
    'validate_html_structure',
    'validate_cms_structure',
    'analyze_links',
    
    # State manager
    'initialize_session_state',
    'clear_generation_state',
    'save_generation_to_state',
    'save_config_to_state',
    'clear_all_state',
    'has_any_results',
    'get_all_results',
    'get_generation_progress',
    
    # GSC (si está disponible)
    'GSC_AVAILABLE',
]

# Añadir GSC utils a __all__ si están disponibles
if GSC_AVAILABLE:
    __all__.extend([
        'load_gsc_data',
        'get_dataset_age',
        'analyze_keyword_coverage'
    ])

__version__ = "4.1.1"
