"""
Rewrite Prompts - PcComponentes Content Generator
Versión 4.2.0

Prompts específicos para reescritura y mejora de contenido.
Usa SafeTemplate para evitar conflictos con JSON y llaves.

Tipos de reescritura:
- SEO: Optimización para buscadores
- Competitor: Basada en análisis de competidores
- Update: Actualización de contenido existente
- Expand: Expansión y enriquecimiento

Autor: PcComponentes - Product Discovery & Content
"""

from typing import Dict, List, Optional, Any
from prompts.templates import (
    SafeTemplate,
    build_links_section,
    format_list_for_prompt,
    escape_for_json,
)

# ============================================================================
# VERSIÓN
# ============================================================================

__version__ = "4.2.0"


# ============================================================================
# TEMPLATES DE REESCRITURA SEO
# ============================================================================

SEO_REWRITE_TEMPLATE = SafeTemplate("""
Reescribe el siguiente contenido optimizándolo para SEO.

KEYWORD PRINCIPAL: "$keyword"
LONGITUD OBJETIVO: $target_length palabras

CONTENIDO ORIGINAL:
---
$original_content
---

ANÁLISIS DEL CONTENIDO ACTUAL:
- Densidad de keyword actual: $current_density
- Estructura actual: $current_structure
- Puntos débiles identificados: $weaknesses

MEJORAS SEO REQUERIDAS:

1. **OPTIMIZACIÓN DE KEYWORD**
   - Incluir "$keyword" en el primer párrafo
   - Densidad objetivo: 1-2% (natural, sin forzar)
   - Usar variaciones semánticas: $keyword_variations

2. **ESTRUCTURA**
   - Mejorar jerarquía de headings (H1 > H2 > H3)
   - Añadir tabla de contenidos si no existe
   - Optimizar para featured snippets

3. **CONTENIDO**
   - Ampliar secciones con poco contenido
   - Añadir datos y cifras concretas
   - Mejorar la introducción para engagement

4. **ELEMENTOS SEO**
   - Optimizar para preguntas frecuentes (FAQs)
   - Incluir listas cuando aporten claridad
   - Mejorar CTAs hacia productos

$links_section

KEYWORDS SECUNDARIAS A POTENCIAR:
$secondary_keywords

INSTRUCCIONES ADICIONALES:
$additional_instructions

IMPORTANTE:
- Mantén el tono de marca PcComponentes
- No copies literalmente, reescribe con mejoras
- El contenido debe ser más completo que el original
""", name="seo_rewrite")


# ============================================================================
# TEMPLATES DE REESCRITURA CON COMPETIDORES
# ============================================================================

COMPETITOR_REWRITE_TEMPLATE = SafeTemplate("""
Reescribe el contenido superando a la competencia analizada.

KEYWORD PRINCIPAL: "$keyword"
LONGITUD OBJETIVO: $target_length palabras

CONTENIDO ACTUAL DE PCCOMPONENTES:
---
$original_content
---

ANÁLISIS DE COMPETIDORES:
$competitor_analysis

GAPS IDENTIFICADOS (lo que tienen los competidores y nosotros no):
$content_gaps

OPORTUNIDADES DE MEJORA:
$improvement_opportunities

ESTRATEGIA DE REESCRITURA:

1. **SUPERAR EN PROFUNDIDAD**
   - Cubrir todos los temas que cubren los competidores
   - Añadir información adicional que ellos no tienen
   - Ser más específicos y detallados

2. **SUPERAR EN ESTRUCTURA**
   - Mejor organización del contenido
   - Navegación más clara
   - Elementos visuales (tablas, listas, callouts)

3. **SUPERAR EN VALOR**
   - Información más actualizada
   - Datos exclusivos si es posible
   - Mejor experiencia de lectura

4. **MANTENER DIFERENCIACIÓN**
   - Tono de marca PcComponentes
   - Enfoque práctico y cercano
   - CTAs hacia nuestros productos

$links_section

KEYWORDS A INCLUIR (de los competidores):
$competitor_keywords

INSTRUCCIONES ADICIONALES:
$additional_instructions

RESULTADO ESPERADO:
- Contenido que supere a todos los competidores analizados
- Más completo, mejor estructurado, más útil
- Optimizado para posicionar por encima de ellos
""", name="competitor_rewrite")


# ============================================================================
# TEMPLATES DE ACTUALIZACIÓN
# ============================================================================

UPDATE_TEMPLATE = SafeTemplate("""
Actualiza el siguiente contenido con información reciente.

KEYWORD PRINCIPAL: "$keyword"
FECHA DEL CONTENIDO ORIGINAL: $original_date

CONTENIDO A ACTUALIZAR:
---
$original_content
---

INFORMACIÓN DESACTUALIZADA DETECTADA:
$outdated_info

ACTUALIZACIONES REQUERIDAS:

1. **DATOS Y CIFRAS**
   - Actualizar precios si se mencionan
   - Actualizar especificaciones de productos
   - Actualizar estadísticas del mercado

2. **PRODUCTOS MENCIONADOS**
   - Verificar disponibilidad
   - Añadir nuevos modelos relevantes
   - Eliminar productos descatalogados

3. **INFORMACIÓN TÉCNICA**
   - Actualizar estándares (WiFi, USB, etc.)
   - Actualizar mejores prácticas
   - Corregir información obsoleta

4. **ESTRUCTURA Y SEO**
   - Mejorar estructura si es necesario
   - Actualizar FAQs con preguntas actuales
   - Refrescar introducción y conclusión

$links_section

NOVEDADES A INCLUIR:
$new_information

MANTENER SIN CAMBIOS:
$keep_unchanged

INSTRUCCIONES ADICIONALES:
$additional_instructions

IMPORTANTE:
- Indica claramente que el contenido ha sido actualizado
- Mantén la esencia y estructura general si funcionaba
- Asegura que toda la información sea actual y precisa
""", name="update")


# ============================================================================
# TEMPLATES DE EXPANSIÓN
# ============================================================================

EXPAND_TEMPLATE = SafeTemplate("""
Expande y enriquece el siguiente contenido.

KEYWORD PRINCIPAL: "$keyword"
LONGITUD ACTUAL: $current_length palabras
LONGITUD OBJETIVO: $target_length palabras

CONTENIDO A EXPANDIR:
---
$original_content
---

SECCIONES A AMPLIAR:
$sections_to_expand

NUEVO CONTENIDO A AÑADIR:
$new_sections

ESTRATEGIA DE EXPANSIÓN:

1. **AMPLIAR SECCIONES EXISTENTES**
   - Añadir más detalle y profundidad
   - Incluir ejemplos prácticos
   - Añadir datos de soporte

2. **AÑADIR NUEVAS SECCIONES**
   $new_sections_list

3. **ENRIQUECER CON ELEMENTOS**
   - Tablas comparativas donde aplique
   - FAQs adicionales
   - Callouts informativos
   - Más enlaces internos

4. **MEJORAR ENGAGEMENT**
   - Introducción más gancho
   - Transiciones más fluidas
   - Conclusión más potente

$links_section

KEYWORDS ADICIONALES A INCLUIR:
$additional_keywords

INSTRUCCIONES ADICIONALES:
$additional_instructions

RESULTADO ESPERADO:
- Contenido significativamente más completo
- Valor añadido en cada sección
- Mejor posicionamiento potencial
""", name="expand")


# ============================================================================
# TEMPLATE DE ANÁLISIS PARA REESCRITURA
# ============================================================================

ANALYSIS_FOR_REWRITE_TEMPLATE = SafeTemplate("""
Analiza el siguiente contenido y proporciona recomendaciones de mejora.

CONTENIDO A ANALIZAR:
---
$content
---

KEYWORD PRINCIPAL: "$keyword"
TIPO DE CONTENIDO: $content_type

Proporciona un análisis estructurado en formato JSON:

{
    "seo_analysis": {
        "keyword_density": "<porcentaje>",
        "keyword_in_title": <true/false>,
        "keyword_in_first_paragraph": <true/false>,
        "heading_structure": "<descripción>",
        "meta_optimization": "<descripción>"
    },
    "content_quality": {
        "depth_score": <1-10>,
        "originality_score": <1-10>,
        "readability_score": <1-10>,
        "value_score": <1-10>
    },
    "structure_analysis": {
        "has_toc": <true/false>,
        "has_faqs": <true/false>,
        "section_count": <número>,
        "avg_section_length": "<palabras>"
    },
    "improvement_priorities": [
        {
            "area": "<área>",
            "priority": "<alta/media/baja>",
            "suggestion": "<sugerencia concreta>"
        }
    ],
    "competitor_gaps": [
        "<gap 1>",
        "<gap 2>"
    ],
    "rewrite_recommendation": {
        "type": "<seo/competitor/update/expand>",
        "effort": "<bajo/medio/alto>",
        "expected_improvement": "<descripción>"
    }
}

Sé específico y accionable en las recomendaciones.
""", name="analysis_for_rewrite")


# ============================================================================
# FUNCIONES BUILDER
# ============================================================================

def build_seo_rewrite_prompt(
    keyword: str,
    original_content: str,
    target_length: int = 1500,
    current_density: str = "desconocida",
    current_structure: str = "por analizar",
    weaknesses: str = "",
    keyword_variations: Optional[List[str]] = None,
    internal_links: Optional[List[str]] = None,
    pdp_links: Optional[List[str]] = None,
    secondary_keywords: Optional[List[str]] = None,
    additional_instructions: str = ""
) -> str:
    """
    Construye prompt para reescritura SEO.
    
    Args:
        keyword: Keyword principal
        original_content: Contenido original
        target_length: Longitud objetivo
        current_density: Densidad actual de keyword
        current_structure: Estructura actual
        weaknesses: Puntos débiles identificados
        keyword_variations: Variaciones de la keyword
        internal_links: Enlaces internos
        pdp_links: Enlaces a PDPs
        secondary_keywords: Keywords secundarias
        additional_instructions: Instrucciones adicionales
        
    Returns:
        Prompt de reescritura SEO
    """
    variations_str = ""
    if keyword_variations:
        variations_str = ", ".join(f'"{v}"' for v in keyword_variations)
    else:
        variations_str = "(usar variaciones naturales)"
    
    return SEO_REWRITE_TEMPLATE.render(
        keyword=keyword,
        target_length=str(target_length),
        original_content=_truncate_content(original_content, 6000),
        current_density=current_density,
        current_structure=current_structure,
        weaknesses=weaknesses or "(Por analizar durante la reescritura)",
        keyword_variations=variations_str,
        links_section=build_links_section(internal_links, pdp_links),
        secondary_keywords=format_list_for_prompt(secondary_keywords or []),
        additional_instructions=additional_instructions or "(Ninguna)"
    )


def build_competitor_rewrite_prompt(
    keyword: str,
    original_content: str,
    competitors: List[Dict[str, Any]],
    target_length: int = 1500,
    content_gaps: str = "",
    improvement_opportunities: str = "",
    competitor_keywords: Optional[List[str]] = None,
    internal_links: Optional[List[str]] = None,
    pdp_links: Optional[List[str]] = None,
    additional_instructions: str = ""
) -> str:
    """
    Construye prompt para reescritura basada en competidores.
    
    Args:
        keyword: Keyword principal
        original_content: Contenido actual
        competitors: Lista de datos de competidores
        target_length: Longitud objetivo
        content_gaps: Gaps de contenido identificados
        improvement_opportunities: Oportunidades de mejora
        competitor_keywords: Keywords de competidores
        internal_links: Enlaces internos
        pdp_links: Enlaces a PDPs
        additional_instructions: Instrucciones adicionales
        
    Returns:
        Prompt de reescritura con análisis de competidores
    """
    return COMPETITOR_REWRITE_TEMPLATE.render(
        keyword=keyword,
        target_length=str(target_length),
        original_content=_truncate_content(original_content, 4000),
        competitor_analysis=format_competitors_for_prompt(competitors),
        content_gaps=content_gaps or "(Por identificar durante el análisis)",
        improvement_opportunities=improvement_opportunities or "(Por identificar)",
        links_section=build_links_section(internal_links, pdp_links),
        competitor_keywords=format_list_for_prompt(competitor_keywords or []),
        additional_instructions=additional_instructions or "(Ninguna)"
    )


def build_update_prompt(
    keyword: str,
    original_content: str,
    original_date: str = "desconocida",
    outdated_info: str = "",
    new_information: str = "",
    keep_unchanged: str = "",
    internal_links: Optional[List[str]] = None,
    pdp_links: Optional[List[str]] = None,
    additional_instructions: str = ""
) -> str:
    """
    Construye prompt para actualización de contenido.
    
    Args:
        keyword: Keyword principal
        original_content: Contenido a actualizar
        original_date: Fecha del contenido original
        outdated_info: Información desactualizada detectada
        new_information: Nueva información a incluir
        keep_unchanged: Elementos a mantener sin cambios
        internal_links: Enlaces internos
        pdp_links: Enlaces a PDPs
        additional_instructions: Instrucciones adicionales
        
    Returns:
        Prompt de actualización
    """
    return UPDATE_TEMPLATE.render(
        keyword=keyword,
        original_date=original_date,
        original_content=_truncate_content(original_content, 6000),
        outdated_info=outdated_info or "(Por identificar durante la revisión)",
        new_information=new_information or "(Incluir novedades relevantes del mercado)",
        keep_unchanged=keep_unchanged or "(Mantener estructura general si funciona)",
        links_section=build_links_section(internal_links, pdp_links),
        additional_instructions=additional_instructions or "(Ninguna)"
    )


def build_expand_prompt(
    keyword: str,
    original_content: str,
    current_length: int,
    target_length: int = 2000,
    sections_to_expand: str = "",
    new_sections: str = "",
    new_sections_list: str = "",
    additional_keywords: Optional[List[str]] = None,
    internal_links: Optional[List[str]] = None,
    pdp_links: Optional[List[str]] = None,
    additional_instructions: str = ""
) -> str:
    """
    Construye prompt para expansión de contenido.
    
    Args:
        keyword: Keyword principal
        original_content: Contenido a expandir
        current_length: Longitud actual en palabras
        target_length: Longitud objetivo
        sections_to_expand: Secciones a ampliar
        new_sections: Nuevas secciones a añadir
        new_sections_list: Lista de nuevas secciones
        additional_keywords: Keywords adicionales
        internal_links: Enlaces internos
        pdp_links: Enlaces a PDPs
        additional_instructions: Instrucciones adicionales
        
    Returns:
        Prompt de expansión
    """
    return EXPAND_TEMPLATE.render(
        keyword=keyword,
        current_length=str(current_length),
        target_length=str(target_length),
        original_content=_truncate_content(original_content, 5000),
        sections_to_expand=sections_to_expand or "(Todas las secciones cortas)",
        new_sections=new_sections or "(Añadir FAQs, comparativas, tips adicionales)",
        new_sections_list=new_sections_list or "- FAQs ampliadas\n- Consejos adicionales\n- Sección de errores comunes",
        links_section=build_links_section(internal_links, pdp_links),
        additional_keywords=format_list_for_prompt(additional_keywords or []),
        additional_instructions=additional_instructions or "(Ninguna)"
    )


def format_competitors_for_prompt(
    competitors: List[Dict[str, Any]],
    max_competitors: int = 5,
    max_content_length: int = 1500
) -> str:
    """
    Formatea datos de competidores para incluir en prompt.
    
    Args:
        competitors: Lista de dicts con datos de competidores
        max_competitors: Máximo de competidores a incluir
        max_content_length: Máximo de caracteres de contenido por competidor
        
    Returns:
        String formateado con análisis de competidores
    """
    if not competitors:
        return "(Sin datos de competidores disponibles)"
    
    sections = []
    
    for i, comp in enumerate(competitors[:max_competitors], 1):
        url = comp.get('url', 'URL no disponible')
        title = comp.get('title', 'Sin título')
        word_count = comp.get('word_count', 0)
        content = comp.get('content', '')
        
        # Truncar contenido
        if len(content) > max_content_length:
            content = content[:max_content_length] + "..."
        
        section = f"""
COMPETIDOR #{i}: {url}
Título: {title}
Palabras: {word_count}

Extracto del contenido:
{content}

---"""
        sections.append(section)
    
    return "\n".join(sections)


def analyze_content_for_rewrite(
    content: str,
    keyword: str,
    content_type: str = "GC"
) -> str:
    """
    Construye prompt para analizar contenido antes de reescribir.
    
    Args:
        content: Contenido a analizar
        keyword: Keyword principal
        content_type: Tipo de contenido
        
    Returns:
        Prompt de análisis
    """
    content_type_names = {
        'GC': 'Guía de Compra',
        'RV': 'Review/Análisis',
        'CP': 'Comparativa',
        'TU': 'Tutorial',
        'TP': 'Top/Ranking',
    }
    
    return ANALYSIS_FOR_REWRITE_TEMPLATE.render(
        content=_truncate_content(content, 8000),
        keyword=keyword,
        content_type=content_type_names.get(content_type.upper(), content_type)
    )


# ============================================================================
# FUNCIONES HELPER
# ============================================================================

def _truncate_content(content: str, max_length: int) -> str:
    """Trunca contenido si excede longitud máxima."""
    if not content:
        return "(Sin contenido)"
    
    if len(content) <= max_length:
        return content
    
    return content[:max_length] + "\n\n[... contenido truncado para el análisis ...]"


def get_rewrite_type_description(rewrite_type: str) -> str:
    """
    Obtiene descripción del tipo de reescritura.
    
    Args:
        rewrite_type: Tipo de reescritura (seo, competitor, update, expand)
        
    Returns:
        Descripción del tipo
    """
    descriptions = {
        'seo': 'Optimización SEO: Mejora el posicionamiento en buscadores',
        'competitor': 'Análisis competitivo: Supera a la competencia',
        'update': 'Actualización: Refresca contenido desactualizado',
        'expand': 'Expansión: Amplía y enriquece el contenido',
    }
    return descriptions.get(rewrite_type.lower(), 'Tipo de reescritura no especificado')


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    # Versión
    '__version__',
    
    # Templates
    'SEO_REWRITE_TEMPLATE',
    'COMPETITOR_REWRITE_TEMPLATE',
    'UPDATE_TEMPLATE',
    'EXPAND_TEMPLATE',
    'ANALYSIS_FOR_REWRITE_TEMPLATE',
    
    # Builders
    'build_seo_rewrite_prompt',
    'build_competitor_rewrite_prompt',
    'build_update_prompt',
    'build_expand_prompt',
    
    # Utilidades
    'format_competitors_for_prompt',
    'analyze_content_for_rewrite',
    'get_rewrite_type_description',
]
