"""
Content Prompts - PcComponentes Content Generator
Versión 4.2.0

Prompts específicos para cada tipo de contenido (arquetipos).
Usa SafeTemplate para evitar conflictos con JSON y llaves.

Tipos de contenido soportados:
- GC: Guía de Compra
- RV: Review/Análisis
- CP: Comparativa
- TU: Tutorial
- TP: Top/Ranking

Autor: PcComponentes - Product Discovery & Content
"""

from typing import Dict, List, Optional, Any, Callable
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
# TEMPLATES DE GUÍA DE COMPRA (GC)
# ============================================================================

GUIDE_PROMPT_TEMPLATE = SafeTemplate("""
Genera una GUÍA DE COMPRA completa y optimizada para SEO.

KEYWORD PRINCIPAL: "$keyword"
LONGITUD OBJETIVO: $target_length palabras

CONTEXTO DEL PRODUCTO/CATEGORÍA:
$product_context

ESTRUCTURA REQUERIDA:

1. **INTRODUCCIÓN** (150-200 palabras)
   - Hook que conecte con el problema del usuario
   - Promesa de valor clara
   - Anticipo de lo que encontrará

2. **¿PARA QUIÉN ES ESTA GUÍA?** (100-150 palabras)
   - 3-4 perfiles de usuario típicos
   - Sus necesidades específicas

3. **CRITERIOS DE SELECCIÓN** (200-300 palabras)
   - Los 4-6 factores más importantes al elegir
   - Explicación práctica de cada uno
   - Cómo afectan al usuario final

4. **SELECCIÓN RECOMENDADA** (400-600 palabras)
   - 3-5 productos destacados
   - Para cada uno: nombre, para quién, punto fuerte
   - Usar formato de cards si aplica

5. **TABLA COMPARATIVA**
   - Comparar los productos seleccionados
   - Columnas: Producto, Característica clave, Ideal para, Precio aproximado

6. **CONSEJOS DE COMPRA** (150-200 palabras)
   - 4-6 tips prácticos
   - Errores comunes a evitar

7. **PREGUNTAS FRECUENTES** (200-300 palabras)
   - 4-6 FAQs relevantes
   - Respuestas concisas y útiles

8. **VEREDICTO FINAL** (100-150 palabras)
   - Resumen de la mejor opción por perfil
   - CTA hacia productos

$links_section

KEYWORDS SECUNDARIAS A INCLUIR:
$secondary_keywords

INSTRUCCIONES ADICIONALES:
$additional_instructions

FORMATO:
- HTML semántico con clases CSS de PcComponentes
- Usar .kicker, .toc, .callout, .verdict-box, .faqs
- Tablas con clase .lt
- Incluir tabla de contenidos al inicio
""", name="guide_prompt")


# ============================================================================
# TEMPLATES DE REVIEW (RV)
# ============================================================================

REVIEW_PROMPT_TEMPLATE = SafeTemplate("""
Genera una REVIEW/ANÁLISIS detallado y optimizado para SEO.

KEYWORD PRINCIPAL: "$keyword"
LONGITUD OBJETIVO: $target_length palabras

DATOS DEL PRODUCTO:
$product_data

ESTRUCTURA REQUERIDA:

1. **INTRODUCCIÓN Y PRIMERA IMPRESIÓN** (150-200 palabras)
   - Contexto del producto en el mercado
   - Primera impresión general
   - Expectativas vs realidad

2. **ESPECIFICACIONES TÉCNICAS** (150-200 palabras)
   - Tabla con specs principales
   - Destacar las más relevantes
   - Comparar con la competencia si aplica

3. **DISEÑO Y CONSTRUCCIÓN** (200-250 palabras)
   - Materiales y acabados
   - Ergonomía y usabilidad
   - Calidad percibida

4. **RENDIMIENTO EN USO REAL** (300-400 palabras)
   - Tests y pruebas realizadas
   - Rendimiento en diferentes escenarios
   - Datos concretos cuando sea posible

5. **PUNTOS FUERTES Y DÉBILES**
   - Lista de pros (5-7 puntos)
   - Lista de contras (3-5 puntos)
   - Ser honesto y equilibrado

6. **¿PARA QUIÉN ES IDEAL?** (150-200 palabras)
   - Perfiles de usuario recomendados
   - Casos de uso ideales
   - Quién debería evitarlo

7. **ALTERNATIVAS A CONSIDERAR** (150-200 palabras)
   - 2-3 alternativas relevantes
   - Breve comparación
   - Cuándo elegir cada una

8. **VEREDICTO Y PUNTUACIÓN** (150-200 palabras)
   - Puntuación general (X/10)
   - Resumen del veredicto
   - Recomendación final

$links_section

KEYWORDS SECUNDARIAS:
$secondary_keywords

INSTRUCCIONES ADICIONALES:
$additional_instructions

FORMATO:
- HTML semántico con clases CSS de PcComponentes
- Usar .verdict-box para la puntuación final
- Incluir tabla de specs
- Usar callouts para destacar información importante
""", name="review_prompt")


# ============================================================================
# TEMPLATES DE COMPARATIVA (CP)
# ============================================================================

COMPARISON_PROMPT_TEMPLATE = SafeTemplate("""
Genera una COMPARATIVA detallada y optimizada para SEO.

KEYWORD PRINCIPAL: "$keyword"
LONGITUD OBJETIVO: $target_length palabras

PRODUCTOS A COMPARAR:
$products_to_compare

ESTRUCTURA REQUERIDA:

1. **INTRODUCCIÓN** (150-200 palabras)
   - Por qué es relevante esta comparativa
   - Qué productos/opciones comparamos
   - Criterios de comparación

2. **TABLA COMPARATIVA RÁPIDA**
   - Vista general de todas las opciones
   - Specs principales lado a lado
   - Usar clase .lt con columnas apropiadas

3. **ANÁLISIS DETALLADO** (por cada producto/opción)
   - Características principales (150-200 palabras cada uno)
   - Puntos fuertes
   - Puntos débiles
   - Para quién es mejor

4. **COMPARATIVA PUNTO A PUNTO** (300-400 palabras)
   - Rendimiento
   - Calidad/Construcción
   - Relación calidad-precio
   - Experiencia de usuario

5. **¿CUÁL ELEGIR SEGÚN TU CASO?** (200-300 palabras)
   - El mejor para gaming
   - El mejor calidad-precio
   - El mejor para profesionales
   - El mejor para principiantes
   (adaptar según los productos)

6. **PREGUNTAS FRECUENTES** (150-200 palabras)
   - 3-5 FAQs sobre la elección
   - Dudas comunes resueltas

7. **CONCLUSIÓN: EL GANADOR** (150-200 palabras)
   - Ganador general (si lo hay)
   - Ganador por categoría/perfil
   - Recomendación final

$links_section

KEYWORDS SECUNDARIAS:
$secondary_keywords

INSTRUCCIONES ADICIONALES:
$additional_instructions

FORMATO:
- HTML semántico con clases CSS de PcComponentes
- Múltiples tablas comparativas
- Usar callouts para destacar ganadores
- Grid de productos si aplica
""", name="comparison_prompt")


# ============================================================================
# TEMPLATES DE TUTORIAL (TU)
# ============================================================================

TUTORIAL_PROMPT_TEMPLATE = SafeTemplate("""
Genera un TUTORIAL paso a paso optimizado para SEO.

KEYWORD PRINCIPAL: "$keyword"
LONGITUD OBJETIVO: $target_length palabras

OBJETIVO DEL TUTORIAL:
$tutorial_objective

ESTRUCTURA REQUERIDA:

1. **INTRODUCCIÓN** (100-150 palabras)
   - Qué aprenderá el usuario
   - Por qué es útil este tutorial
   - Nivel de dificultad

2. **LO QUE NECESITAS** (100-150 palabras)
   - Requisitos previos
   - Materiales/herramientas necesarias
   - Tiempo estimado

3. **PASOS DETALLADOS** (principal del contenido)
   - Paso 1: [Título descriptivo]
     * Explicación clara
     * Tips o advertencias si aplica
   - Paso 2: [Título descriptivo]
     * ...
   (Repetir para cada paso necesario)

4. **CONSEJOS Y TRUCOS** (150-200 palabras)
   - 4-6 tips de experto
   - Atajos o mejoras
   - Cómo optimizar resultados

5. **PROBLEMAS COMUNES Y SOLUCIONES** (200-250 palabras)
   - 3-5 problemas frecuentes
   - Solución para cada uno
   - Cómo prevenirlos

6. **PREGUNTAS FRECUENTES** (150-200 palabras)
   - 4-5 FAQs del proceso
   - Respuestas prácticas

7. **CONCLUSIÓN** (100-150 palabras)
   - Resumen de lo aprendido
   - Siguientes pasos recomendados
   - Recursos adicionales

$links_section

KEYWORDS SECUNDARIAS:
$secondary_keywords

INSTRUCCIONES ADICIONALES:
$additional_instructions

FORMATO:
- HTML semántico con clases CSS de PcComponentes
- Numerar claramente cada paso
- Usar callouts para advertencias/tips
- Incluir tabla de contenidos
""", name="tutorial_prompt")


# ============================================================================
# TEMPLATES DE TOP/RANKING (TP)
# ============================================================================

RANKING_PROMPT_TEMPLATE = SafeTemplate("""
Genera un TOP/RANKING optimizado para SEO.

KEYWORD PRINCIPAL: "$keyword"
LONGITUD OBJETIVO: $target_length palabras
NÚMERO DE POSICIONES: $num_positions

CRITERIOS DEL RANKING:
$ranking_criteria

ESTRUCTURA REQUERIDA:

1. **INTRODUCCIÓN** (150-200 palabras)
   - Presentación del ranking
   - Criterios de selección
   - Fecha de actualización

2. **EL TOP $num_positions** (resumen rápido)
   - Lista numerada con los ganadores
   - Una línea descriptiva cada uno
   - Enlace a cada sección

3. **ANÁLISIS DETALLADO** (por cada posición)
   - #N: [Nombre del producto]
   - Por qué está en esta posición (100-150 palabras)
   - Características destacadas
   - Para quién es ideal
   - Precio aproximado

4. **TABLA RESUMEN**
   - Posición, Producto, Punto fuerte, Ideal para
   - Usar clase .lt apropiada

5. **MENCIONES HONORÍFICAS** (100-150 palabras)
   - 2-3 opciones que casi entran
   - Por qué merecen mención

6. **CÓMO ELEGIR EL TUYO** (150-200 palabras)
   - Guía rápida de decisión
   - Según presupuesto
   - Según necesidades

7. **CONCLUSIÓN** (100-150 palabras)
   - El ganador absoluto
   - Mejor calidad-precio
   - Recomendación según perfil

$links_section

KEYWORDS SECUNDARIAS:
$secondary_keywords

INSTRUCCIONES ADICIONALES:
$additional_instructions

FORMATO:
- HTML semántico con clases CSS de PcComponentes
- Numeración clara de posiciones
- Usar badges para destacar (#1, Mejor calidad-precio, etc.)
- Grid o cards para los productos
""", name="ranking_prompt")


# ============================================================================
# FUNCIONES BUILDER
# ============================================================================

def build_guide_prompt(
    keyword: str,
    target_length: int = 1500,
    product_context: str = "",
    internal_links: Optional[List[str]] = None,
    pdp_links: Optional[List[str]] = None,
    secondary_keywords: Optional[List[str]] = None,
    additional_instructions: str = ""
) -> str:
    """
    Construye prompt para Guía de Compra.
    
    Args:
        keyword: Keyword principal
        target_length: Longitud objetivo en palabras
        product_context: Contexto del producto/categoría
        internal_links: Enlaces internos a incluir
        pdp_links: Enlaces a PDPs
        secondary_keywords: Keywords secundarias
        additional_instructions: Instrucciones adicionales
        
    Returns:
        Prompt completo para guía de compra
    """
    return GUIDE_PROMPT_TEMPLATE.render(
        keyword=keyword,
        target_length=str(target_length),
        product_context=product_context or "(Contexto general de la categoría)",
        links_section=build_links_section(internal_links, pdp_links),
        secondary_keywords=format_list_for_prompt(secondary_keywords or []),
        additional_instructions=additional_instructions or "(Ninguna)"
    )


def build_review_prompt(
    keyword: str,
    target_length: int = 1500,
    product_data: str = "",
    internal_links: Optional[List[str]] = None,
    pdp_links: Optional[List[str]] = None,
    secondary_keywords: Optional[List[str]] = None,
    additional_instructions: str = ""
) -> str:
    """
    Construye prompt para Review/Análisis.
    
    Args:
        keyword: Keyword principal
        target_length: Longitud objetivo
        product_data: Datos del producto
        internal_links: Enlaces internos
        pdp_links: Enlaces a PDPs
        secondary_keywords: Keywords secundarias
        additional_instructions: Instrucciones adicionales
        
    Returns:
        Prompt completo para review
    """
    return REVIEW_PROMPT_TEMPLATE.render(
        keyword=keyword,
        target_length=str(target_length),
        product_data=product_data or "(Datos del producto no especificados)",
        links_section=build_links_section(internal_links, pdp_links),
        secondary_keywords=format_list_for_prompt(secondary_keywords or []),
        additional_instructions=additional_instructions or "(Ninguna)"
    )


def build_comparison_prompt(
    keyword: str,
    target_length: int = 1500,
    products_to_compare: Optional[List[str]] = None,
    internal_links: Optional[List[str]] = None,
    pdp_links: Optional[List[str]] = None,
    secondary_keywords: Optional[List[str]] = None,
    additional_instructions: str = ""
) -> str:
    """
    Construye prompt para Comparativa.
    
    Args:
        keyword: Keyword principal
        target_length: Longitud objetivo
        products_to_compare: Lista de productos a comparar
        internal_links: Enlaces internos
        pdp_links: Enlaces a PDPs
        secondary_keywords: Keywords secundarias
        additional_instructions: Instrucciones adicionales
        
    Returns:
        Prompt completo para comparativa
    """
    products_str = ""
    if products_to_compare:
        products_str = "\n".join(f"- {p}" for p in products_to_compare)
    else:
        products_str = "(Productos a determinar según la keyword)"
    
    return COMPARISON_PROMPT_TEMPLATE.render(
        keyword=keyword,
        target_length=str(target_length),
        products_to_compare=products_str,
        links_section=build_links_section(internal_links, pdp_links),
        secondary_keywords=format_list_for_prompt(secondary_keywords or []),
        additional_instructions=additional_instructions or "(Ninguna)"
    )


def build_tutorial_prompt(
    keyword: str,
    target_length: int = 1500,
    tutorial_objective: str = "",
    internal_links: Optional[List[str]] = None,
    pdp_links: Optional[List[str]] = None,
    secondary_keywords: Optional[List[str]] = None,
    additional_instructions: str = ""
) -> str:
    """
    Construye prompt para Tutorial.
    
    Args:
        keyword: Keyword principal
        target_length: Longitud objetivo
        tutorial_objective: Objetivo del tutorial
        internal_links: Enlaces internos
        pdp_links: Enlaces a PDPs
        secondary_keywords: Keywords secundarias
        additional_instructions: Instrucciones adicionales
        
    Returns:
        Prompt completo para tutorial
    """
    return TUTORIAL_PROMPT_TEMPLATE.render(
        keyword=keyword,
        target_length=str(target_length),
        tutorial_objective=tutorial_objective or "(Enseñar al usuario sobre: " + keyword + ")",
        links_section=build_links_section(internal_links, pdp_links),
        secondary_keywords=format_list_for_prompt(secondary_keywords or []),
        additional_instructions=additional_instructions or "(Ninguna)"
    )


def build_ranking_prompt(
    keyword: str,
    target_length: int = 1500,
    num_positions: int = 10,
    ranking_criteria: str = "",
    internal_links: Optional[List[str]] = None,
    pdp_links: Optional[List[str]] = None,
    secondary_keywords: Optional[List[str]] = None,
    additional_instructions: str = ""
) -> str:
    """
    Construye prompt para Top/Ranking.
    
    Args:
        keyword: Keyword principal
        target_length: Longitud objetivo
        num_positions: Número de posiciones en el ranking
        ranking_criteria: Criterios del ranking
        internal_links: Enlaces internos
        pdp_links: Enlaces a PDPs
        secondary_keywords: Keywords secundarias
        additional_instructions: Instrucciones adicionales
        
    Returns:
        Prompt completo para ranking
    """
    return RANKING_PROMPT_TEMPLATE.render(
        keyword=keyword,
        target_length=str(target_length),
        num_positions=str(num_positions),
        ranking_criteria=ranking_criteria or "Calidad, rendimiento, relación calidad-precio, opiniones de usuarios",
        links_section=build_links_section(internal_links, pdp_links),
        secondary_keywords=format_list_for_prompt(secondary_keywords or []),
        additional_instructions=additional_instructions or "(Ninguna)"
    )


# ============================================================================
# MAPEO DE BUILDERS POR TIPO
# ============================================================================

CONTENT_TYPE_BUILDERS: Dict[str, Callable] = {
    'GC': build_guide_prompt,
    'RV': build_review_prompt,
    'CP': build_comparison_prompt,
    'TU': build_tutorial_prompt,
    'TP': build_ranking_prompt,
}


def get_content_prompt_by_type(
    content_type: str,
    keyword: str,
    **kwargs
) -> str:
    """
    Obtiene el prompt correcto según el tipo de contenido.
    
    Args:
        content_type: Código del tipo (GC, RV, CP, TU, TP)
        keyword: Keyword principal
        **kwargs: Argumentos adicionales para el builder
        
    Returns:
        Prompt completo para el tipo de contenido
        
    Raises:
        ValueError: Si el tipo de contenido no es válido
    """
    content_type = content_type.upper()
    
    builder = CONTENT_TYPE_BUILDERS.get(content_type)
    
    if not builder:
        available = ", ".join(CONTENT_TYPE_BUILDERS.keys())
        raise ValueError(
            f"Tipo de contenido '{content_type}' no válido. "
            f"Tipos disponibles: {available}"
        )
    
    return builder(keyword=keyword, **kwargs)


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    # Versión
    '__version__',
    
    # Templates
    'GUIDE_PROMPT_TEMPLATE',
    'REVIEW_PROMPT_TEMPLATE',
    'COMPARISON_PROMPT_TEMPLATE',
    'TUTORIAL_PROMPT_TEMPLATE',
    'RANKING_PROMPT_TEMPLATE',
    
    # Builders
    'build_guide_prompt',
    'build_review_prompt',
    'build_comparison_prompt',
    'build_tutorial_prompt',
    'build_ranking_prompt',
    
    # Utilidades
    'get_content_prompt_by_type',
    'CONTENT_TYPE_BUILDERS',
]
