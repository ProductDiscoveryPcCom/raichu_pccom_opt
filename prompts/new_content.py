"""
New Content Prompts - PcComponentes Content Generator
Versión 4.5.1

Prompts para generación de contenido nuevo en 3 etapas:
1. Borrador inicial
2. Análisis y correcciones
3. Versión final

CORRECCIONES v4.5.1:
- Añadido build_final_prompt_stage3 como alias (compatibilidad con app.py)
- Incluidos parámetros keyword, links_data, alternative_product en Stage 3
- Añadido CSS completo con :root en la generación
- Instrucciones explícitas para NO usar markdown
- FAQs deben incluir la keyword
- Plantillas para elementos visuales opcionales

Autor: PcComponentes - Product Discovery & Content
"""

from typing import Dict, List, Optional, Any

__version__ = "4.5.1"


# ============================================================================
# CSS MINIFICADO PARA INCLUIR EN EL HTML
# ============================================================================

CSS_INLINE_MINIFIED = """:root{--orange-900:#FF6000;--blue-m-900:#170453;--white:#FFFFFF;--gray-100:#F5F5F5;--gray-200:#E5E5E5;--gray-700:#404040;--gray-900:#171717;--space-md:16px;--space-lg:24px;--radius-md:8px;}
.contentGenerator__main,.contentGenerator__faqs,.contentGenerator__verdict{font-family:'Inter',sans-serif;line-height:1.7;color:var(--gray-900);max-width:100%;}
.kicker{display:inline-block;background:var(--orange-900);color:var(--white);padding:4px 12px;font-size:12px;font-weight:700;text-transform:uppercase;border-radius:4px;margin-bottom:16px;}
.toc{background:var(--gray-100);border-radius:var(--radius-md);padding:var(--space-lg);margin:var(--space-lg) 0;}
.toc__title{font-weight:700;margin-bottom:12px;}
.toc__list{margin:0;padding-left:20px;}
.toc__list li{margin-bottom:8px;}
.faqs__item{border-bottom:1px solid var(--gray-200);padding:var(--space-md) 0;}
.faqs__question{font-weight:600;margin-bottom:8px;}
.verdict-box{background:linear-gradient(135deg,var(--blue-m-900),#2E1A7A);color:var(--white);padding:var(--space-lg);border-radius:var(--radius-md);}
.callout{background:var(--gray-100);border-left:4px solid var(--orange-900);padding:var(--space-md);margin:var(--space-lg) 0;border-radius:0 var(--radius-md) var(--radius-md) 0;}
.callout-bf{background:var(--blue-m-900);color:var(--white);padding:var(--space-lg);border-radius:var(--radius-md);text-align:center;}
table{width:100%;border-collapse:collapse;margin:var(--space-lg) 0;}
th,td{padding:12px;text-align:left;border-bottom:1px solid var(--gray-200);}
th{background:var(--gray-100);font-weight:600;}"""


# ============================================================================
# PLANTILLAS DE ELEMENTOS VISUALES
# ============================================================================

ELEMENT_TEMPLATES = {
    'callout': '''<div class="callout">
    <p><strong>💡 Dato importante:</strong> [Tu contenido aquí]</p>
</div>''',
    
    'callout_bf': '''<div class="callout-bf">
    <p>🔥 <strong>OFERTA BLACK FRIDAY</strong> 🔥</p>
    <p>[Descripción de la oferta]</p>
</div>''',
    
    'table': '''<table>
    <thead>
        <tr>
            <th>Característica</th>
            <th>Opción A</th>
            <th>Opción B</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>Especificación 1</td>
            <td>Valor A</td>
            <td>Valor B</td>
        </tr>
    </tbody>
</table>''',
    
    'verdict_box': '''<div class="verdict-box">
    <h2>Veredicto Final</h2>
    <p>[Tu conclusión aquí]</p>
</div>''',
    
    'grid': '''<div class="grid-layout">
    <div class="grid-item">[Item 1]</div>
    <div class="grid-item">[Item 2]</div>
    <div class="grid-item">[Item 3]</div>
</div>''',
}


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
    visual_elements: Optional[List[str]] = None,
    guiding_context: str = "",  # AÑADIDO: Contexto guía del usuario
    alternative_product: Optional[Dict] = None,  # AÑADIDO: Producto alternativo
) -> str:
    """
    Construye el prompt para la Etapa 1: Generación del borrador inicial.
    
    Args:
        keyword: Keyword principal
        arquetipo: Dict con datos del arquetipo seleccionado
        target_length: Longitud objetivo en palabras
        pdp_data: Datos del producto (si aplica)
        links_data: Lista de enlaces a incluir
        secondary_keywords: Keywords secundarias
        additional_instructions: Instrucciones adicionales
        campos_especificos: Campos específicos del arquetipo
        visual_elements: Lista de elementos visuales a incluir
        guiding_context: Contexto guía proporcionado por el usuario
        alternative_product: Producto alternativo a mencionar
        
    Returns:
        Prompt completo para el borrador
    """
    arquetipo_name = arquetipo.get('name', 'Contenido SEO')
    arquetipo_desc = arquetipo.get('description', '')
    
    # Construir sección de producto
    product_section = ""
    if pdp_data:
        product_section = f"""
## DATOS DEL PRODUCTO
- Nombre: {pdp_data.get('name', 'N/A')}
- Precio: {pdp_data.get('price', 'N/A')}
- Descripción: {pdp_data.get('description', 'N/A')[:500]}
- Características: {pdp_data.get('features', 'N/A')}
"""
    
    # Construir sección de enlaces - OBLIGATORIOS
    links_section = ""
    if links_data:
        links_section = "\n## ENLACES OBLIGATORIOS (USA SOLO ESTOS)\n"
        links_section += "**IMPORTANTE: Incluye ÚNICAMENTE estos enlaces en el contenido. NO inventes otros.**\n\n"
        for i, link in enumerate(links_data, 1):
            link_type = link.get('type', 'interno')
            url = link.get('url', '')
            anchor = link.get('anchor', link.get('text', ''))
            links_section += f"{i}. **[{anchor}]({url})** - Tipo: {link_type}\n"
    
    # Keywords secundarias
    secondary_kw_section = ""
    if secondary_keywords:
        secondary_kw_section = "\n## KEYWORDS SECUNDARIAS\n"
        for kw in secondary_keywords:
            secondary_kw_section += f"- {kw}\n"
    
    # Campos específicos del arquetipo
    campos_section = ""
    if campos_especificos:
        campos_section = "\n## INFORMACIÓN ESPECÍFICA\n"
        for key, value in campos_especificos.items():
            if value:
                campos_section += f"- {key}: {value}\n"
    
    # Contexto guía del usuario
    guiding_section = ""
    if guiding_context:
        guiding_section = f"\n## CONTEXTO Y GUÍA DEL USUARIO\n{guiding_context}\n"
    
    # Producto alternativo
    alt_product_section = ""
    if alternative_product and alternative_product.get('url'):
        alt_product_section = f"""
## PRODUCTO ALTERNATIVO A MENCIONAR
- URL: {alternative_product.get('url', '')}
- Nombre: {alternative_product.get('name', '')}
Incluye este producto de forma natural como alternativa en el contenido.
"""
    
    # Elementos visuales opcionales
    elements_section = ""
    if visual_elements:
        elements_section = "\n## ELEMENTOS VISUALES A INCLUIR\n"
        for elem in visual_elements:
            if elem in ELEMENT_TEMPLATES:
                elements_section += f"\n### {elem.upper()}\n```html\n{ELEMENT_TEMPLATES[elem]}\n```\n"
    
    prompt = f"""Eres un experto redactor SEO de PcComponentes, la tienda líder de tecnología en España.

# TAREA
Genera un BORRADOR de contenido tipo "{arquetipo_name}" para la keyword "{keyword}".

{arquetipo_desc}

## PARÁMETROS
- **Keyword principal:** {keyword}
- **Longitud objetivo:** {target_length} palabras
- **Tipo de contenido:** {arquetipo_name}
{product_section}
{links_section}
{secondary_kw_section}
{campos_section}
{guiding_section}
{alt_product_section}
{elements_section}

## ESTRUCTURA HTML REQUERIDA

**CRÍTICO: El HTML debe empezar con <style> y usar las clases CSS exactas.**

```html
<style>
{CSS_INLINE_MINIFIED}
</style>

<article class="contentGenerator__main">
    <span class="kicker">TEXTO KICKER</span>
    <h2>Título Principal con Keyword</h2>
    
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
    <h2>Preguntas frecuentes sobre {keyword}</h2>
    <div class="faqs">
        <div class="faqs__item">
            <h3 class="faqs__question">¿Pregunta con {keyword}?</h3>
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

## TONO DE MARCA PCCOMPONENTES
- Expertos sin ser pedantes
- Frikis sin vergüenza
- Cercanos pero profesionales
- Tuteamos al lector
- Usamos analogías tech cuando aportan valor
- Hablamos claro, no vendemos humo

## INSTRUCCIONES ADICIONALES
{additional_instructions if additional_instructions else "(Ninguna)"}

---

**REGLAS CRÍTICAS:**
1. ❌ NO uses marcadores markdown como ```html o ```
2. ✅ Genera SOLO el HTML directo, empezando con <style>
3. ✅ El título de FAQs DEBE incluir la keyword: "Preguntas frecuentes sobre {keyword}"
4. ✅ Usa ÚNICAMENTE los enlaces proporcionados, no inventes otros
5. ✅ Incluye el bloque <style> con CSS al principio
"""
    
    return prompt


# ============================================================================
# ETAPA 2: ANÁLISIS Y CORRECCIONES
# ============================================================================

def build_new_content_correction_prompt_stage2(
    draft_content: str,
    target_length: int = 1500,
    keyword: str = "",
    links_to_verify: Optional[List[Dict]] = None,
    alternative_product: Optional[Dict] = None,
) -> str:
    """
    Construye el prompt para la Etapa 2: Análisis crítico del borrador.
    
    Args:
        draft_content: HTML del borrador a analizar
        target_length: Longitud objetivo en palabras
        keyword: Keyword principal
        links_to_verify: Enlaces que deberían estar en el contenido
        alternative_product: Producto alternativo que debería mencionarse
    """
    # Construir sección de enlaces a verificar
    links_verification = ""
    if links_to_verify:
        links_verification = "\n## 5. Enlaces\nVerifica que estos enlaces están incluidos:\n"
        for link in links_to_verify:
            url = link.get('url', '')
            anchor = link.get('anchor', link.get('text', ''))
            links_verification += f"- [{anchor}]({url})\n"
    
    # Construir sección de producto alternativo
    alt_product_verification = ""
    if alternative_product and alternative_product.get('url'):
        alt_product_verification = f"""
## 6. Producto Alternativo
Verifica que se menciona el producto alternativo:
- URL: {alternative_product.get('url', '')}
- Nombre: {alternative_product.get('name', '')}
"""
    
    prompt = f"""Eres un editor SEO senior de PcComponentes. Tu tarea es ANALIZAR críticamente el siguiente borrador.

# BORRADOR A ANALIZAR

{draft_content[:8000]}

# CRITERIOS DE EVALUACIÓN

## 1. Estructura CMS
- ¿Tiene bloque <style> con :root y variables CSS?
- ¿Tiene los 3 articles obligatorios? (main, faqs, verdict)
- ¿Usa las clases CSS correctas?
- ¿El kicker es un <span>, no un <div>?
- ¿El título principal es H2?
- ¿Tiene verdict-box?

## 2. SEO
- ¿La keyword "{keyword}" aparece de forma natural?
- ¿El título de FAQs incluye la keyword?
- ¿Densidad aproximada correcta (1-2%)?
- ¿Hay heading stuffing?

## 3. Contenido
- ¿La longitud es aproximadamente {target_length} palabras?
- ¿El contenido es útil y completo?
- ¿El tono es el de PcComponentes?

## 4. Formato
- ¿Hay marcadores markdown (```html)?
- ¿El HTML es válido?
{links_verification}
{alt_product_verification}

# FORMATO DE RESPUESTA

Responde SOLO con un JSON válido:

```json
{{
    "longitud_actual": 0,
    "longitud_objetivo": {target_length},
    "necesita_ajuste_longitud": false,
    "tiene_css_root": false,
    "tiene_verdict_box": false,
    "tiene_callouts": false,
    "faqs_incluye_keyword": false,
    "tiene_markdown_wrapper": false,
    "enlaces_presentes": [],
    "enlaces_faltantes": [],
    "producto_alternativo_mencionado": false,
    "problemas_encontrados": [
        {{
            "tipo": "estructura|seo|contenido|formato|enlaces",
            "severidad": "critico|alto|medio|bajo",
            "descripcion": "Descripción del problema",
            "solucion": "Cómo solucionarlo"
        }}
    ],
    "aspectos_positivos": [],
    "puntuacion_general": 0,
    "recomendacion_principal": ""
}}
```

**IMPORTANTE:** Responde ÚNICAMENTE con el JSON, sin texto adicional ni marcadores.
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
    Construye el prompt para la Etapa 3: Generación de la versión final.
    
    NOTA: Esta función tiene el nombre que app.py espera (build_final_prompt_stage3)
    
    Args:
        draft_content: HTML del borrador original
        analysis_feedback: JSON con el análisis de la etapa 2
        keyword: Keyword principal (NUEVO)
        target_length: Longitud objetivo
        links_data: Enlaces a incluir (NUEVO)
        alternative_product: Producto alternativo (NUEVO)
        
    Returns:
        Prompt para la versión final
    """
    # Construir sección de enlaces obligatorios
    links_section = ""
    if links_data:
        links_section = "\n## ENLACES OBLIGATORIOS\n"
        links_section += "**IMPORTANTE: Usa ÚNICAMENTE estos enlaces. NO inventes otros.**\n\n"
        for i, link in enumerate(links_data, 1):
            url = link.get('url', '')
            anchor = link.get('anchor', link.get('text', ''))
            link_type = link.get('type', 'interno')
            links_section += f"{i}. [{anchor}]({url}) - {link_type}\n"
    
    # Producto alternativo
    alt_product_section = ""
    if alternative_product and alternative_product.get('url'):
        alt_product_section = f"""
## PRODUCTO ALTERNATIVO A MENCIONAR
- URL: {alternative_product.get('url', '')}
- Nombre: {alternative_product.get('name', '')}
Inclúyelo de forma natural en el contenido como alternativa.
"""
    
    prompt = f"""Eres un editor SEO senior de PcComponentes. Tu tarea es generar la VERSIÓN FINAL del contenido.

# BORRADOR ORIGINAL

{draft_content[:8000]}

# ANÁLISIS Y CORRECCIONES

{analysis_feedback[:3000]}
{links_section}
{alt_product_section}

# INSTRUCCIONES CRÍTICAS

1. **Aplica TODAS las correcciones** del análisis
2. **Ajusta la longitud** a ~{target_length} palabras
3. **OBLIGATORIO - El HTML debe empezar con <style>:**

```html
<style>
{CSS_INLINE_MINIFIED}
</style>
```

4. **Estructura requerida:**

<article class="contentGenerator__main">
    <span class="kicker">KICKER</span>
    <h2>Título con {keyword}</h2>
    <nav class="toc">...</nav>
    <!-- Secciones -->
</article>

<article class="contentGenerator__faqs">
    <h2>Preguntas frecuentes sobre {keyword}</h2>
    <div class="faqs">...</div>
</article>

<article class="contentGenerator__verdict">
    <div class="verdict-box">
        <h2>Veredicto Final</h2>
        <p>...</p>
    </div>
</article>

---

**REGLAS ABSOLUTAS:**
1. ❌ NUNCA uses marcadores markdown (```html, ```)
2. ✅ Empieza DIRECTAMENTE con <style>
3. ✅ El título de FAQs DEBE ser: "Preguntas frecuentes sobre {keyword}"
4. ✅ Incluye el verdict-box obligatoriamente
5. ✅ Usa SOLO los enlaces proporcionados
6. ✅ Genera HTML válido y completo

**Genera SOLO el HTML final, sin explicaciones.**
"""
    
    return prompt


# Alias para compatibilidad (nombre antiguo)
def build_final_generation_prompt_stage3(
    draft_content: str,
    corrections_json: str,
    target_length: int = 1500,
) -> str:
    """
    Alias de compatibilidad - Redirige a build_final_prompt_stage3
    """
    return build_final_prompt_stage3(
        draft_content=draft_content,
        analysis_feedback=corrections_json,
        keyword="",
        target_length=target_length,
        links_data=None,
        alternative_product=None
    )


# Alias para compatibilidad con app.py (nombre corto)
def build_correction_prompt_stage2(
    draft_content: str,
    target_length: int = 1500,
    keyword: str = "",
    links_to_verify: Optional[List[Dict]] = None,
    alternative_product: Optional[Dict] = None,
) -> str:
    """
    Alias de compatibilidad - Redirige a build_new_content_correction_prompt_stage2
    """
    return build_new_content_correction_prompt_stage2(
        draft_content=draft_content,
        target_length=target_length,
        keyword=keyword,
        links_to_verify=links_to_verify,
        alternative_product=alternative_product
    )


# ============================================================================
# FUNCIONES AUXILIARES
# ============================================================================

def build_system_prompt() -> str:
    """Genera el system prompt para todas las etapas."""
    return """Eres un experto redactor y editor SEO de PcComponentes, la tienda líder de tecnología en España.

Tu trabajo es crear contenido que:
1. Sea útil y valioso para los usuarios
2. Esté optimizado para SEO sin sobre-optimizar
3. Siga el tono de marca de PcComponentes
4. Cumpla con la estructura CMS requerida
5. NUNCA use marcadores markdown en el HTML generado

Tono de marca:
- Expertos sin ser pedantes
- Frikis sin vergüenza  
- Cercanos pero profesionales
- Tuteamos al lector
- Usamos analogías tech cuando aportan valor
- Hablamos claro, no vendemos humo

IMPORTANTE: Cuando generes HTML, genera SOLO HTML puro sin envolverlo en ```html o similares.
"""


def get_css_styles() -> str:
    """Retorna el CSS minificado para incluir en el HTML."""
    return CSS_INLINE_MINIFIED


def get_element_template(element_name: str) -> str:
    """Retorna la plantilla HTML para un elemento visual."""
    return ELEMENT_TEMPLATES.get(element_name, "")


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    '__version__',
    # Funciones principales
    'build_new_content_prompt_stage1',
    'build_new_content_correction_prompt_stage2',
    'build_correction_prompt_stage2',  # Alias para app.py
    'build_final_prompt_stage3',  # Nombre correcto para app.py
    'build_final_generation_prompt_stage3',  # Alias de compatibilidad
    'build_system_prompt',
    # Utilidades
    'get_css_styles',
    'get_element_template',
    # Constantes
    'CSS_INLINE_MINIFIED',
    'ELEMENT_TEMPLATES',
]
