"""
Utils package - PcComponentes Content Generator
Versión 4.3.0
"""

import logging

logger = logging.getLogger(__name__)

__version__ = "4.3.0"

# Importar html_utils
try:
    from .html_utils import (
        HTMLParser,
        get_html_parser,
        count_words_in_html,
        extract_content_structure,
        validate_html_structure,
        validate_cms_structure,
        analyze_links,
        strip_html_tags,
        get_heading_hierarchy,
        validate_word_count_target,
    )
    _html_utils_available = True
except ImportError as e:
    logger.warning(f"No se pudo importar html_utils: {e}")
    _html_utils_available = False
    
    # Fallbacks
    from html.parser import HTMLParser
    def get_html_parser(): return HTMLParser()
    def count_words_in_html(html): return 0
    def extract_content_structure(html): return {}
    def validate_html_structure(html): return {}
    def validate_cms_structure(html): return True, [], []
    def analyze_links(html): return {}
    def strip_html_tags(html): return html
    def get_heading_hierarchy(html): return []
    def validate_word_count_target(html, target, tol=0.05): return {}

# Importar state_manager
try:
    from .state_manager import (
        initialize_session_state,
        clear_generation_state,
        save_generation_to_state,
        save_config_to_state,
        clear_all_state,
        has_any_results,
        get_all_results,
        get_generation_progress,
        save_form_data,
        get_form_data,
        get_form_value,
    )
    _state_manager_available = True
except ImportError as e:
    logger.warning(f"No se pudo importar state_manager: {e}")
    _state_manager_available = False
    
    def initialize_session_state(): pass
    def clear_generation_state(): pass
    def save_generation_to_state(*args, **kwargs): return ""
    def save_config_to_state(config): pass
    def clear_all_state(): pass
    def has_any_results(): return False
    def get_all_results(): return {}
    def get_generation_progress(): return {}
    def save_form_data(data): pass
    def get_form_data(): return {}
    def get_form_value(key, default=None): return default

# GSC utils (opcional)
GSC_AVAILABLE = False
try:
    from .gsc_utils import load_gsc_data, get_dataset_age, analyze_keyword_coverage
    GSC_AVAILABLE = True
except ImportError:
    pass

__all__ = [
    '__version__',
    # HTML utils
    'HTMLParser',
    'get_html_parser',
    'count_words_in_html',
    'extract_content_structure',
    'validate_html_structure',
    'validate_cms_structure',
    'analyze_links',
    'strip_html_tags',
    'get_heading_hierarchy',
    'validate_word_count_target',
    # State manager
    'initialize_session_state',
    'clear_generation_state',
    'save_generation_to_state',
    'save_config_to_state',
    'clear_all_state',
    'has_any_results',
    'get_all_results',
    'get_generation_progress',
    'save_form_data',
    'get_form_data',
    'get_form_value',
    # Flags
    'GSC_AVAILABLE',
]
