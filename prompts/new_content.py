"""
New Content Prompts - PcComponentes Content Generator
Versión 4.3.0

Prompts para generación de contenido nuevo en 3 etapas:
1. Borrador inicial
2. Análisis y correcciones
3. Versión final

Autor: PcComponentes - Product Discovery & Content
"""

from typing import Dict, List, Optional, Any

__version__ = "4.3.0"


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
    
    # Construir sección de enlaces
    links_section = ""
    if links_data:
        links_section = "\n## ENLACES A INCLUIR\n"
        for link in links_data:
            link_type = link.get('type', 'interno')
            url = link.get('url', '')
            anchor = link.get('anchor', '')
            context = link.get('context', '')
            links_section += f"- [{anchor}]({url}) - Tipo: {link_type}"
            if context:
                links_section += f" - Contexto: {context}"
            links_section += "\n"
    
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

## INSTRUCCIONES DE ESTRUCTURA HTML

El contenido debe seguir esta estructura CMS-compatible:

```html
<article class="contentGenerator__main">
    <span class="kicker">TEXTO KICKER</span>
    <h2>Título Principal con Keyword</h2>
    
    <!-- Tabla de contenidos -->
    <nav class="toc">
        <p class="toc__title">En este artículo</p>
        <ol class="toc__list">
            <li><a href="#seccion1">Sección 1</a></li>
            <!-- más items -->
        </ol>
    </nav>
    
    <!-- Contenido principal -->
    <section id="seccion1">
        <h3>Subtítulo</h3>
        <p>Contenido...</p>
    </section>
    
    <!-- Más secciones... -->
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

**IMPORTANTE:** 
- Genera SOLO el HTML, sin explicaciones previas ni posteriores
- Usa las clases CSS exactas indicadas
- Incluye la keyword de forma natural (densidad 1-2%)
- El contenido debe ser ÚTIL y COMPLETO
"""
    
    return prompt


# ============================================================================
# ETAPA 2: ANÁLISIS Y CORRECCIONES
# ============================================================================

def build_new_content_correction_prompt_stage2(
    draft_content: str,
    target_length: int = 1500,
    keyword: str = "",
) -> str:
    """
    Construye el prompt para la Etapa 2: Análisis crítico del borrador.
    
    Args:
        draft_content: HTML del borrador generado en etapa 1
        target_length: Longitud objetivo en palabras
        keyword: Keyword principal
        
    Returns:
        Prompt para el análisis
    """
    prompt = f"""Eres un editor SEO senior de PcComponentes. Tu tarea es ANALIZAR críticamente el siguiente borrador.

# BORRADOR A ANALIZAR

```html
{draft_content[:8000]}
```

# CRITERIOS DE EVALUACIÓN

## 1. Estructura CMS
- ¿Tiene los 3 articles obligatorios? (main, faqs, verdict)
- ¿Usa las clases CSS correctas?
- ¿El kicker es un <span>, no un <div>?
- ¿El título principal es H2?
- ¿Sólo se utilizan los emojis soportados ⚡✅?

## 2. SEO
- ¿La keyword "{keyword}" aparece de forma natural?
- ¿Densidad aproximada correcta (1-2%)?
- ¿Hay heading stuffing?
- ¿Los H3 son descriptivos?

## 3. Contenido
- ¿La longitud es aproximadamente {target_length} palabras?
- ¿El contenido es útil y completo?
- ¿Hay información redundante?
- ¿El tono es el de PcComponentes?

## 4. UX
- ¿Hay tabla de contenidos?
- ¿Las secciones están bien estructuradas?
- ¿Hay FAQs relevantes?
- ¿El veredicto es concluyente?

# FORMATO DE RESPUESTA

Responde SOLO con un JSON válido con esta estructura:

```json
{{
    "word_count_actual": 0,
    "word_count_objetivo": {target_length},
    "estructura_correcta": true,
    "problemas_encontrados": [
        {{
            "tipo": "estructura|seo|contenido|ux",
            "severidad": "alta|media|baja",
            "descripcion": "Descripción del problema",
            "ubicacion": "Dónde está el problema",
            "solucion": "Cómo solucionarlo"
        }}
    ],
    "aspectos_positivos": [
        "Aspecto positivo 1",
        "Aspecto positivo 2"
    ],
    "puntuacion_general": 0,
    "recomendacion_principal": "La mejora más importante a realizar"
}}
```

**IMPORTANTE:** Responde ÚNICAMENTE con el JSON, sin texto adicional.
"""
    
    return prompt


# ============================================================================
# ETAPA 3: VERSIÓN FINAL
# ============================================================================

def build_final_generation_prompt_stage3(
    draft_content: str,
    corrections_json: str,
    target_length: int = 1500,
) -> str:
    """
    Construye el prompt para la Etapa 3: Generación de la versión final.
    
    Args:
        draft_content: HTML del borrador original
        corrections_json: JSON con el análisis de la etapa 2
        target_length: Longitud objetivo
        
    Returns:
        Prompt para la versión final
    """
    prompt = f"""Eres un editor SEO senior de PcComponentes. Tu tarea es generar la VERSIÓN FINAL del contenido aplicando las correcciones identificadas.

# BORRADOR ORIGINAL

```html
{draft_content[:8000]}
```

# ANÁLISIS Y CORRECCIONES A APLICAR

```json
{corrections_json[:3000]}
```

# INSTRUCCIONES

1. **Aplica TODAS las correcciones** identificadas en el análisis
2. **Mantén lo que funciona** - los aspectos positivos deben conservarse
3. **Ajusta la longitud** a aproximadamente {target_length} palabras
4. **Verifica la estructura CMS**:
   - 3 articles: main, faqs, verdict
   - Clases CSS correctas
   - Kicker con <span>
   - Título con H2

# ESTRUCTURA REQUERIDA

```html
<article class="contentGenerator__main">
    <span class="kicker">KICKER</span>
    <h2>Título Principal</h2>
    <nav class="toc">...</nav>
    <!-- Secciones con H3 -->
</article>

<article class="contentGenerator__faqs">
    <h2>Preguntas frecuentes</h2>
    <div class="faqs">...</div>
</article>

<article class="contentGenerator__verdict">
    <div class="verdict-box">
        <h2>Veredicto Final</h2>
        <p>...</p>
    </div>
</article>
```

---

**IMPORTANTE:**
- Genera SOLO el HTML final, sin explicaciones
- Aplica TODAS las correcciones del análisis
- Mantén el tono PcComponentes
- Verifica que el HTML sea válido y completo
"""
    
    return prompt


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

Tono de marca:
- Expertos sin ser pedantes
- Frikis sin vergüenza  
- Cercanos pero profesionales
- Tuteamos al lector
- Usamos analogías tech cuando aportan valor
- Hablamos claro, no vendemos humo
"""


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    '__version__',
    'build_new_content_prompt_stage1',
    'build_new_content_correction_prompt_stage2',
    'build_final_generation_prompt_stage3',
    'build_system_prompt',
]
