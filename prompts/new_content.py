"""
New Content Prompts - PcComponentes Content Generator
Versión 4.4.0

Prompts para generación de contenido nuevo en 3 etapas:
1. Borrador inicial
2. Análisis y correcciones  
3. Versión final

Soporta: preguntas guía, producto alternativo, anchor text específico.

Autor: PcComponentes - Product Discovery & Content
"""

from typing import Dict, List, Optional, Any

__version__ = "4.4.0"

# ============================================================================
# ETAPA 1: BORRADOR INICIAL
# ============================================================================

def build_new_content_prompt_stage1(
    keyword: str,
    arquetipo: Dict[str, Any],
    target_length: int = 1500,
    pdp_data: Optional[Dict] = None,
    links_data: Optional[List[Dict]] = None,
    secondary_keywords: Optional[List[str]] = None,
    additional_instructions: str = "",
    campos_especificos: Optional[Dict] = None,
    guiding_context: Optional[str] = None,
    alternative_product: Optional[Dict] = None,
) -> str:
    """
    Construye el prompt para Etapa 1: Borrador inicial.
    
    Args:
        keyword: Keyword principal
        arquetipo: Dict con datos del arquetipo
        target_length: Longitud objetivo en palabras
        pdp_data: Datos del producto (si aplica)
        links_data: Enlaces a incluir [{url, anchor, type}]
        secondary_keywords: Keywords secundarias
        additional_instructions: Instrucciones adicionales
        campos_especificos: Campos específicos del arquetipo
        guiding_context: Contexto de preguntas guía respondidas
        alternative_product: Producto alternativo {url, name}
    """
    arquetipo_name = arquetipo.get('name', 'Contenido SEO')
    arquetipo_desc = arquetipo.get('description', '')
    arquetipo_tone = arquetipo.get('tone', 'informativo')
    arquetipo_structure = arquetipo.get('structure', [])
    
    # Producto principal
    product_section = ""
    if pdp_data:
        product_section = f"""
## DATOS DEL PRODUCTO
- **Nombre:** {pdp_data.get('name', 'N/A')}
- **Precio:** {pdp_data.get('price', 'N/A')}
- **Descripción:** {pdp_data.get('description', 'N/A')[:500]}
- **Características:** {pdp_data.get('features', 'N/A')}
"""
    
    # Producto alternativo
    alt_product_section = ""
    if alternative_product and alternative_product.get('url'):
        alt_name = alternative_product.get('name', 'Producto alternativo')
        alt_url = alternative_product.get('url', '')
        alt_product_section = f"""
## PRODUCTO ALTERNATIVO A MENCIONAR
Incluye una mención natural a este producto como alternativa:
- **Nombre:** {alt_name}
- **URL:** {alt_url}
- **Instrucción:** Sugiérelo para usuarios con necesidades o presupuesto diferente.
"""
    
    # Enlaces con anchor text
    links_section = ""
    if links_data:
        links_section = """
## ENLACES A INCLUIR

**⚠️ IMPORTANTE:** Usa EXACTAMENTE el anchor text especificado para cada enlace.

"""
        for i, link in enumerate(links_data, 1):
            url = link.get('url', '')
            anchor = link.get('anchor', '')
            link_type = link.get('type', 'interno')
            
            if anchor:
                links_section += f"""**Enlace {i}** ({link_type}):
- URL: {url}
- Anchor text EXACTO: "{anchor}"
- Uso: `<a href="{url}">{anchor}</a>`

"""
            else:
                links_section += f"""**Enlace {i}** ({link_type}):
- URL: {url}
- Anchor text: (crea uno descriptivo)

"""
    
    # Keywords secundarias
    secondary_kw_section = ""
    if secondary_keywords:
        secondary_kw_section = "\n## KEYWORDS SECUNDARIAS\n"
        for kw in secondary_keywords:
            secondary_kw_section += f"- {kw}\n"
    
    # Contexto de preguntas guía
    guiding_section = ""
    if guiding_context and guiding_context.strip():
        guiding_section = f"""
## CONTEXTO DEL EDITOR

El editor ha proporcionado esta información adicional:

{guiding_context}

**Usa esta información para dar profundidad y especificidad al contenido.**
"""
    
    # Campos específicos
    campos_section = ""
    if campos_especificos:
        campos_section = "\n## INFORMACIÓN ESPECÍFICA\n"
        for key, value in campos_especificos.items():
            if value:
                campos_section += f"- **{key}:** {value}\n"
    
    # Estructura
    structure_section = ""
    if arquetipo_structure:
        structure_section = f"""
## ESTRUCTURA RECOMENDADA
{' → '.join(arquetipo_structure)}
"""
    
    prompt = f"""Eres un experto redactor SEO de PcComponentes, la tienda líder de tecnología en España.

# TAREA
Genera un BORRADOR de contenido tipo "{arquetipo_name}" para la keyword "{keyword}".

{arquetipo_desc}

## PARÁMETROS
- **Keyword principal:** {keyword}
- **Longitud objetivo:** {target_length} palabras
- **Tipo:** {arquetipo_name}
- **Tono:** {arquetipo_tone}
{structure_section}
{product_section}
{alt_product_section}
{links_section}
{secondary_kw_section}
{guiding_section}
{campos_section}

## ESTRUCTURA HTML

```html
<article class="contentGenerator__main">
    <span class="kicker">CATEGORÍA</span>
    <h2>Título con Keyword</h2>
    
    <nav class="toc">
        <p class="toc__title">En este artículo</p>
        <ol class="toc__list">
            <li><a href="#seccion1">Sección 1</a></li>
        </ol>
    </nav>
    
    <section id="seccion1">
        <h3>Subtítulo</h3>
        <p>Contenido...</p>
    </section>
</article>

<article class="contentGenerator__faqs">
    <h2>Preguntas frecuentes</h2>
    <div class="faqs">
        <div class="faqs__item">
            <h3 class="faqs__question">¿Pregunta?</h3>
            <p class="faqs__answer">Respuesta...</p>
        </div>
    </div>
</article>

<article class="contentGenerator__verdict">
    <div class="verdict-box">
        <h2>Veredicto Final</h2>
        <p>Conclusión...</p>
    </div>
</article>
```

## TONO PCCOMPONENTES
- Expertos sin ser pedantes
- Frikis sin vergüenza
- Cercanos pero profesionales
- Tuteamos al lector
- Hablamos claro, no vendemos humo

## INSTRUCCIONES ADICIONALES
{additional_instructions if additional_instructions else "(Ninguna)"}

---

**REGLAS:**
1. Genera SOLO el HTML, sin explicaciones
2. Usa las clases CSS exactas
3. Keyword con densidad 1-2%
4. **USA EXACTAMENTE los anchor text especificados**
5. Menciona el producto alternativo si se indica
6. Contenido ÚTIL basado en el contexto proporcionado
"""
    
    return prompt


# ============================================================================
# ETAPA 2: ANÁLISIS Y CORRECCIONES
# ============================================================================

def build_correction_prompt_stage2(
    draft_content: str,
    target_length: int = 1500,
    keyword: str = "",
    links_to_verify: Optional[List[Dict]] = None,
    alternative_product: Optional[Dict] = None,
) -> str:
    """
    Construye el prompt para Etapa 2: Análisis crítico.
    
    Args:
        draft_content: HTML del borrador
        target_length: Longitud objetivo
        keyword: Keyword principal
        links_to_verify: Enlaces que deben estar incluidos
        alternative_product: Producto alternativo que debe mencionarse
    """
    # Verificación de enlaces
    links_check = ""
    if links_to_verify:
        links_check = """
## VERIFICACIÓN DE ENLACES (CRÍTICO)

Verifica que estos enlaces estén incluidos con anchor EXACTO:

"""
        for i, link in enumerate(links_to_verify, 1):
            url = link.get('url', '')
            anchor = link.get('anchor', '')
            if anchor:
                links_check += f'{i}. URL: {url}\n   Anchor: "{anchor}"\n\n'
            else:
                links_check += f'{i}. URL: {url}\n   (anchor libre)\n\n'
    
    # Verificación producto alternativo
    alt_check = ""
    if alternative_product and alternative_product.get('url'):
        alt_check = f"""
## VERIFICACIÓN PRODUCTO ALTERNATIVO

¿Se menciona el producto alternativo?
- URL: {alternative_product.get('url')}
- Nombre: {alternative_product.get('name', 'Producto alternativo')}
"""
    
    prompt = f"""Eres un editor SEO senior. Analiza críticamente este borrador.

# BORRADOR

```html
{draft_content[:8000]}
```

# CHECKLIST

## 1. SEO
- [ ] Keyword "{keyword}" en H2 principal
- [ ] Densidad keyword 1-2%
- [ ] H3 descriptivos

## 2. ESTRUCTURA HTML
- [ ] Clases CSS correctas
- [ ] IDs coinciden con TOC
- [ ] HTML válido

## 3. CONTENIDO
- [ ] Longitud cerca de {target_length} palabras
- [ ] Contenido útil, no genérico
- [ ] Tono PcComponentes
- [ ] FAQs relevantes

## 4. ENLACES
- [ ] Todos los enlaces incluidos
- [ ] Anchor text EXACTO
- [ ] Integrados naturalmente
{links_check}
{alt_check}

# RESPONDE CON:

```
## ANÁLISIS SEO
[observaciones]

## ANÁLISIS ESTRUCTURA
[observaciones]

## ANÁLISIS CONTENIDO
[observaciones]

## VERIFICACIÓN ENLACES
[cada enlace: ✅ o ❌ con anchor usado]

## PROBLEMAS CRÍTICOS
[lista numerada]

## SUGERENCIAS MEJORA
[lista numerada]

## CORRECCIONES ESPECÍFICAS
[antes → después]
```
"""
    
    return prompt


# ============================================================================
# ETAPA 3: VERSIÓN FINAL
# ============================================================================

def build_final_prompt_stage3(
    draft_content: str,
    analysis_feedback: str,
    keyword: str = "",
    target_length: int = 1500,
    links_data: Optional[List[Dict]] = None,
    alternative_product: Optional[Dict] = None,
) -> str:
    """
    Construye el prompt para Etapa 3: Versión final.
    
    Args:
        draft_content: HTML del borrador
        analysis_feedback: Feedback de etapa 2
        keyword: Keyword principal
        target_length: Longitud objetivo
        links_data: Enlaces requeridos
        alternative_product: Producto alternativo
    """
    # Recordatorio enlaces
    links_reminder = ""
    if links_data:
        links_reminder = "\n## ENLACES REQUERIDOS\n\n"
        for link in links_data:
            url = link.get('url', '')
            anchor = link.get('anchor', '')
            if anchor:
                links_reminder += f'- `<a href="{url}">{anchor}</a>`\n'
            else:
                links_reminder += f'- {url} (anchor descriptivo)\n'
    
    # Recordatorio producto alternativo
    alt_reminder = ""
    if alternative_product and alternative_product.get('url'):
        alt_reminder = f"""
## PRODUCTO ALTERNATIVO

Incluir: {alternative_product.get('name', 'Producto alternativo')} ({alternative_product.get('url')})
"""
    
    prompt = f"""Eres un redactor SEO senior. Genera la VERSIÓN FINAL del contenido.

# BORRADOR

```html
{draft_content[:6000]}
```

# FEEDBACK

{analysis_feedback[:3000]}

# INSTRUCCIONES

1. **Corrige TODOS los problemas críticos**
2. **Implementa las sugerencias**
3. **Mantén lo que funciona**
4. **Verifica:**
   - Keyword "{keyword}" bien integrada
   - Longitud ~{target_length} palabras
   - HTML válido con clases correctas
   - **TODOS los enlaces con anchor EXACTO**
   - Tono PcComponentes
{links_reminder}
{alt_reminder}

# SALIDA

Genera ÚNICAMENTE el HTML final.
Empieza con `<article class="contentGenerator__main">`.

---

VERSIÓN FINAL:
"""
    
    return prompt


# ============================================================================
# FUNCIONES AUXILIARES
# ============================================================================

def format_links_for_prompt(links: List[Dict]) -> str:
    """Formatea enlaces para incluir en prompt."""
    if not links:
        return ""
    
    lines = []
    for link in links:
        url = link.get('url', '')
        anchor = link.get('anchor', '')
        link_type = link.get('type', 'interno')
        
        if anchor:
            lines.append(f'- [{anchor}]({url}) ({link_type})')
        else:
            lines.append(f'- {url} ({link_type})')
    
    return "\n".join(lines)


def format_guiding_answers_for_prompt(answers: Dict[str, str]) -> str:
    """Formatea respuestas a preguntas guía."""
    if not answers:
        return ""
    
    parts = []
    for question, answer in answers.items():
        if answer and answer.strip():
            parts.append(f"**{question}**\n{answer}")
    
    return "\n\n".join(parts)


def build_complete_stage1_prompt(
    keyword: str,
    arquetipo: Dict[str, Any],
    target_length: int = 1500,
    pdp_data: Optional[Dict] = None,
    links_data: Optional[List[Dict]] = None,
    secondary_keywords: Optional[List[str]] = None,
    additional_instructions: str = "",
    guiding_answers: Optional[Dict[str, str]] = None,
    alternative_product: Optional[Dict] = None,
) -> str:
    """
    Función de conveniencia para construir prompt Stage 1.
    Formatea automáticamente guiding_answers.
    """
    guiding_context = None
    if guiding_answers:
        guiding_context = format_guiding_answers_for_prompt(guiding_answers)
    
    return build_new_content_prompt_stage1(
        keyword=keyword,
        arquetipo=arquetipo,
        target_length=target_length,
        pdp_data=pdp_data,
        links_data=links_data,
        secondary_keywords=secondary_keywords,
        additional_instructions=additional_instructions,
        guiding_context=guiding_context,
        alternative_product=alternative_product,
    )


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    '__version__',
    # Prompts principales
    'build_new_content_prompt_stage1',
    'build_correction_prompt_stage2',
    'build_final_prompt_stage3',
    # Auxiliares
    'format_links_for_prompt',
    'format_guiding_answers_for_prompt',
    'build_complete_stage1_prompt',
]
