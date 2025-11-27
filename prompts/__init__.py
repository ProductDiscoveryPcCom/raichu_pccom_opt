"""
Prompts Module - PcComponentes Content Generator
Versión 4.3.0

Módulo centralizado de prompts y templates para generación de contenido.

USO:
    from prompts import new_content, rewrite

Autor: PcComponentes - Product Discovery & Content
"""

import logging

logger = logging.getLogger(__name__)

__version__ = "4.3.0"

# ============================================================================
# IMPORTS DE SUBMÓDULOS
# ============================================================================

try:
    from prompts import new_content
except ImportError as e:
    logger.warning(f"No se pudo importar prompts.new_content: {e}")
    new_content = None

try:
    from prompts import rewrite
except ImportError as e:
    logger.warning(f"No se pudo importar prompts.rewrite: {e}")
    rewrite = None

# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    '__version__',
    'new_content',
    'rewrite',
]
