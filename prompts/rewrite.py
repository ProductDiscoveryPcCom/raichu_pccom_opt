"""
Rewrite Prompts - PcComponentes Content Generator
Versión 4.3.0

Prompts para reescritura de contenido basada en análisis competitivo.
Flujo de 3 etapas:
1. Borrador basado en análisis de competidores
2. Análisis y correcciones
3. Versión final

Autor: PcComponentes - Product Discovery & Content
"""

from typing import Dict, List, Optional, Any

__version__ = "4.3.0"


# ============================================================================
# ETAPA 1: BORRADOR CON ANÁLISIS COMPETITIVO
# ============================================================================

def build_rewrite_prompt_stage1(
    keyword: str,
    competitor_analysis: str,
    pdp_data: Optional[Dict] = None,
    target_length: int = 1500,
    keywords: Optional[List[str]] = None,
    context: str = "",
    links: Optional[List[Dict]] = None,
    objetivo: str = "",
    producto_alternativo: Optional[Dict] = None,
    arquetipo: Optional[Dict] = None,
) -> str:
    """
    Construye el prompt para la Etapa 1: Borrador basado en análisis competitivo.
    
    Args:
        keyword: Keyword principal
        competitor_analysis: Análisis de contenido competidor
        pdp_data: Datos del producto
        target_length: Longitud objetivo
        keywords: Keywords secundarias
        context: Contexto adicional
        links: Enlaces a incluir
        objetivo: Objetivo del contenido
        producto_alternativo: Producto alternativo a mencionar
        arquetipo: Arquetipo de contenido
        
    Returns:
        Prompt completo para el borrador
    """
    # Sección de producto
    product_section = ""
    if pdp_data:
        product_section = f"""
## DATOS DEL PRODUCTO PRINCIPAL
- Nombre: {pdp_data.get('name', 'N/A')}
- Precio: {pdp_data.get('price', 'N/A')}
- URL: {pdp_data.get('url', 'N/A')}
- Descripción: {pdp_data.get('description', 'N/A')[:500] if pdp_data.get('description') else 'N/A'}
"""
    
    # Sección de producto alternativo
    alt_product_section = ""
    if producto_alternativo and producto_alternativo.get('url'):
        alt_product_section = f"""
## PRODUCTO ALTERNATIVO (mencionar en veredicto)
- Nombre: {producto_alternativo.get('text', 'Alternativa')}
- URL: {producto_alternativo.get('url', '')}
"""
    
    # Sección de enlaces
    links_section = ""
    if links:
        links_section = "\n## ENLACES A INCLUIR\n"
        for link in links:
            link_type = link.get('type', 'interno')
            url = link.get('url', '')
            anchor = link.get('anchor', '')
            links_section += f"- [{anchor}]({url}) - Tipo: {link_type}\n"
    
    # Keywords secundarias
    keywords_section = ""
    if keywords:
        keywords_section = "\n## KEYWORDS SECUNDARIAS\n"
        for kw in keywords:
            keywords_section += f"- {kw}\n"
    
    # Arquetipo
    arquetipo_section = ""
    if arquetipo:
        arquetipo_section = f"""
## ARQUETIPO DE REFERENCIA
- Tipo: {arquetipo.get('name', 'N/A')}
- Descripción: {arquetipo.get('description', 'N/A')}
"""
    
    prompt = f"""Eres un experto redactor SEO de PcComponentes, la tienda líder de tecnología en España.

# TAREA
Genera un contenido SUPERIOR a la competencia para la keyword "{keyword}".

## OBJETIVO
{objetivo if objetivo else "Crear contenido que supere a los competidores en utilidad, profundidad y optimización SEO."}

## ANÁLISIS COMPETITIVO
{competitor_analysis[:6000] if competitor_analysis else "(Sin análisis de competidores disponible)"}
{product_section}
{alt_product_section}
{links_section}
{keywords_section}
{arquetipo_section}

## CONTEXTO ADICIONAL
{context if context else "(Ninguno)"}

## PARÁMETROS
- **Keyword principal:** {keyword}
- **Longitud objetivo:** {target_length} palabras
- **Superar a competencia en:** profundidad, utilidad, estructura

## INSTRUCCIONES DE ESTRUCTURA HTML

```html
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

---

**IMPORTANTE:** 
- Genera SOLO el HTML, sin explicaciones
- SUPERA a la competencia en valor y profundidad
- Incluye información que los competidores no cubren
"""
    
    return prompt


# ============================================================================
# ETAPA 2: ANÁLISIS DE REESCRITURA
# ============================================================================

def build_rewrite_correction_prompt_stage2(
    draft_content: str,
    target_length: int = 1500,
    keyword: str = "",
    competitor_analysis: str = "",
    objetivo: str = "",
) -> str:
    """
    Construye el prompt para la Etapa 2: Análisis del borrador de reescritura.
    
    Args:
        draft_content: HTML del borrador
        target_length: Longitud objetivo
        keyword: Keyword principal
        competitor_analysis: Análisis de competidores
        objetivo: Objetivo del contenido
        
    Returns:
        Prompt para el análisis
    """
    prompt = f"""Eres un editor SEO senior de PcComponentes. Analiza críticamente este borrador de REESCRITURA.

# OBJETIVO DE LA REESCRITURA
{objetivo if objetivo else "Superar a la competencia en todos los aspectos."}

# BORRADOR A ANALIZAR

```html
{draft_content[:8000]}
```

# ANÁLISIS DE COMPETIDORES (referencia)

{competitor_analysis[:3000] if competitor_analysis else "(Sin análisis disponible)"}

# CRITERIOS DE EVALUACIÓN

## 1. Superioridad vs Competencia
- ¿El contenido es MEJOR que la competencia?
- ¿Cubre gaps que los competidores no cubren?
- ¿Es más útil y profundo?

## 2. Estructura CMS
- ¿Tiene los 3 articles obligatorios?
- ¿Clases CSS correctas?
- ¿Kicker con <span>?

## 3. SEO
- ¿Keyword "{keyword}" natural?
- ¿Densidad correcta (1-2%)?
- ¿H3 descriptivos?

## 4. Contenido
- ¿Longitud ~{target_length} palabras?
- ¿Tono PcComponentes?
- ¿Información única y valiosa?

# FORMATO DE RESPUESTA

Responde SOLO con JSON:

```json
{{
    "word_count_actual": 0,
    "word_count_objetivo": {target_length},
    "supera_competencia": true,
    "estructura_correcta": true,
    "problemas_encontrados": [
        {{
            "tipo": "competencia|estructura|seo|contenido",
            "severidad": "alta|media|baja",
            "descripcion": "Descripción",
            "solucion": "Solución"
        }}
    ],
    "aspectos_positivos": [],
    "gaps_cubiertos": [],
    "puntuacion_general": 0,
    "recomendacion_principal": ""
}}
```

**IMPORTANTE:** Solo JSON, sin texto adicional.
"""
    
    return prompt


# ============================================================================
# ETAPA 3: VERSIÓN FINAL DE REESCRITURA
# ============================================================================

def build_rewrite_final_prompt_stage3(
    draft_content: str,
    corrections_json: str,
    target_length: int = 1500,
    competitor_analysis: str = "",
) -> str:
    """
    Construye el prompt para la Etapa 3: Versión final de reescritura.
    
    Args:
        draft_content: HTML del borrador
        corrections_json: JSON con correcciones
        target_length: Longitud objetivo
        competitor_analysis: Análisis de competidores
        
    Returns:
        Prompt para la versión final
    """
    prompt = f"""Eres un editor SEO senior de PcComponentes. Genera la VERSIÓN FINAL aplicando las correcciones.

# BORRADOR ORIGINAL

```html
{draft_content[:8000]}
```

# CORRECCIONES A APLICAR

```json
{corrections_json[:3000]}
```

# REFERENCIA COMPETITIVA

{competitor_analysis[:2000] if competitor_analysis else "(Sin referencia)"}

# INSTRUCCIONES

1. **Aplica TODAS las correcciones**
2. **Mantén superioridad** sobre competencia
3. **Ajusta longitud** a ~{target_length} palabras
4. **Verifica estructura CMS** (3 articles, clases correctas)

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

**IMPORTANTE:** Solo HTML final, sin explicaciones.
"""
    
    return prompt


# ============================================================================
# FUNCIONES AUXILIARES
# ============================================================================

def format_competitors_for_prompt(competitors: List[Dict]) -> str:
    """Formatea lista de competidores para incluir en prompt."""
    if not competitors:
        return "(Sin competidores analizados)"
    
    result = ""
    for i, comp in enumerate(competitors, 1):
        result += f"\n### Competidor {i}: {comp.get('title', 'Sin título')}\n"
        result += f"- URL: {comp.get('url', 'N/A')}\n"
        result += f"- Posición: {comp.get('position', 'N/A')}\n"
        result += f"- Palabras: {comp.get('word_count', 'N/A')}\n"
        if comp.get('headings'):
            result += f"- Estructura: {', '.join(comp['headings'][:5])}\n"
    
    return result


def analyze_content_for_rewrite(content: str, keyword: str) -> Dict:
    """Analiza contenido para reescritura."""
    import re
    
    # Contar palabras
    text = re.sub(r'<[^>]+>', ' ', content)
    words = len(text.split())
    
    # Buscar keyword
    keyword_count = content.lower().count(keyword.lower())
    density = (keyword_count / words * 100) if words > 0 else 0
    
    # Buscar headings
    headings = re.findall(r'<h[1-6][^>]*>(.*?)</h[1-6]>', content, re.I | re.DOTALL)
    
    return {
        'word_count': words,
        'keyword_count': keyword_count,
        'keyword_density': round(density, 2),
        'headings': [re.sub(r'<[^>]+>', '', h).strip() for h in headings],
        'has_faqs': 'faqs' in content.lower(),
        'has_verdict': 'verdict' in content.lower(),
    }


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    '__version__',
    'build_rewrite_prompt_stage1',
    'build_rewrite_correction_prompt_stage2',
    'build_rewrite_final_prompt_stage3',
    'format_competitors_for_prompt',
    'analyze_content_for_rewrite',
]
