"""
Prompts Module - PcComponentes Content Generator
Versión 4.2.0

Módulo centralizado de prompts y templates para generación de contenido.
Usa string.Template (sintaxis $variable) para evitar conflictos con JSON y llaves.

USO:
    from prompts import build_system_prompt, build_content_prompt
    
    system = build_system_prompt(keyword="monitores gaming", target_length=1500)
    prompt = build_content_prompt(keyword="monitores gaming", content_type="GC")

IMPORTANTE:
    Este módulo NO usa f-strings para templates.
    Usa $variable en lugar de {variable} para evitar conflictos con JSON.

Autor: PcComponentes - Product Discovery & Content
"""

# ============================================================================
# IMPORTS DESDE TEMPLATES
# ============================================================================

from prompts.templates import (
    # Versión
    __version__,
    
    # Excepciones
    TemplateError,
    MissingVariableError,
    InvalidTemplateError,
    
    # Clases
    SafeTemplate,
    TemplateRegistry,
    
    # Registro global
    get_registry,
    
    # Templates predefinidos
    SYSTEM_PROMPT_TEMPLATE,
    CONTENT_GENERATION_TEMPLATE,
    REWRITE_TEMPLATE,
    ANALYSIS_TEMPLATE,
    LINKS_SECTION_TEMPLATE,
    COMPETITOR_TEMPLATE,
    HTML_STRUCTURE_TEMPLATE,
    FAQS_TEMPLATE,
    FAQ_ITEM_TEMPLATE,
    CALLOUT_TEMPLATE,
    COMPARISON_TABLE_TEMPLATE,
    PRODUCT_GRID_TEMPLATE,
    PRODUCT_CARD_TEMPLATE,
    
    # Funciones builder
    build_system_prompt,
    build_content_prompt,
    build_rewrite_prompt,
    build_analysis_prompt,
    build_links_section,
    build_competitor_section,
    build_faqs_section,
    build_callout,
    
    # Utilidades
    escape_for_json,
    format_list_for_prompt,
    format_dict_for_prompt,
    validate_template_variables,
    render_template_safe,
)

# ============================================================================
# IMPORTS DESDE CONTENT
# ============================================================================

try:
    from prompts.content import (
        build_guide_prompt,
        build_review_prompt,
        build_comparison_prompt,
        build_tutorial_prompt,
        build_ranking_prompt,
        get_content_prompt_by_type,
        CONTENT_TYPE_BUILDERS,
    )
except ImportError:
    # Funciones placeholder si content.py no existe aún
    def build_guide_prompt(*args, **kwargs):
        return build_content_prompt(*args, content_type="GC", **kwargs)
    
    def build_review_prompt(*args, **kwargs):
        return build_content_prompt(*args, content_type="RV", **kwargs)
    
    def build_comparison_prompt(*args, **kwargs):
        return build_content_prompt(*args, content_type="CP", **kwargs)
    
    def build_tutorial_prompt(*args, **kwargs):
        return build_content_prompt(*args, content_type="TU", **kwargs)
    
    def build_ranking_prompt(*args, **kwargs):
        return build_content_prompt(*args, content_type="TP", **kwargs)
    
    def get_content_prompt_by_type(content_type: str, **kwargs):
        return build_content_prompt(content_type=content_type, **kwargs)
    
    CONTENT_TYPE_BUILDERS = {}

# ============================================================================
# IMPORTS DESDE REWRITE
# ============================================================================

try:
    from prompts.rewrite import (
        build_seo_rewrite_prompt,
        build_competitor_rewrite_prompt,
        build_update_prompt,
        build_expand_prompt,
        format_competitors_for_prompt,
        analyze_content_for_rewrite,
    )
except ImportError:
    # Funciones placeholder si rewrite.py no existe aún
    def build_seo_rewrite_prompt(*args, **kwargs):
        return build_rewrite_prompt(*args, **kwargs)
    
    def build_competitor_rewrite_prompt(*args, **kwargs):
        return build_rewrite_prompt(*args, **kwargs)
    
    def build_update_prompt(*args, **kwargs):
        return build_rewrite_prompt(*args, **kwargs)
    
    def build_expand_prompt(*args, **kwargs):
        return build_rewrite_prompt(*args, **kwargs)
    
    def format_competitors_for_prompt(competitors):
        return build_competitor_section(competitors)
    
    def analyze_content_for_rewrite(content, keyword):
        return build_analysis_prompt(content, keyword)


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    # Versión
    '__version__',
    
    # Excepciones
    'TemplateError',
    'MissingVariableError',
    'InvalidTemplateError',
    
    # Clases
    'SafeTemplate',
    'TemplateRegistry',
    
    # Registro global
    'get_registry',
    
    # Templates predefinidos
    'SYSTEM_PROMPT_TEMPLATE',
    'CONTENT_GENERATION_TEMPLATE',
    'REWRITE_TEMPLATE',
    'ANALYSIS_TEMPLATE',
    'LINKS_SECTION_TEMPLATE',
    'COMPETITOR_TEMPLATE',
    'HTML_STRUCTURE_TEMPLATE',
    'FAQS_TEMPLATE',
    'FAQ_ITEM_TEMPLATE',
    'CALLOUT_TEMPLATE',
    'COMPARISON_TABLE_TEMPLATE',
    'PRODUCT_GRID_TEMPLATE',
    'PRODUCT_CARD_TEMPLATE',
    
    # Funciones builder principales
    'build_system_prompt',
    'build_content_prompt',
    'build_rewrite_prompt',
    'build_analysis_prompt',
    'build_links_section',
    'build_competitor_section',
    'build_faqs_section',
    'build_callout',
    
    # Funciones de contenido específicas
    'build_guide_prompt',
    'build_review_prompt',
    'build_comparison_prompt',
    'build_tutorial_prompt',
    'build_ranking_prompt',
    'get_content_prompt_by_type',
    'CONTENT_TYPE_BUILDERS',
    
    # Funciones de reescritura
    'build_seo_rewrite_prompt',
    'build_competitor_rewrite_prompt',
    'build_update_prompt',
    'build_expand_prompt',
    'format_competitors_for_prompt',
    'analyze_content_for_rewrite',
    
    # Utilidades
    'escape_for_json',
    'format_list_for_prompt',
    'format_dict_for_prompt',
    'validate_template_variables',
    'render_template_safe',
]
