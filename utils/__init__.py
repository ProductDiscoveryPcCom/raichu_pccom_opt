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
    save_generation_to_state
)

__all__ = [
    'count_words_in_html',
    'extract_content_structure',
    'validate_html_structure',
    'validate_cms_structure',
    'analyze_links',
    'initialize_session_state',
    'clear_generation_state',
    'save_generation_to_state'
]

__version__ = "4.1.1"
