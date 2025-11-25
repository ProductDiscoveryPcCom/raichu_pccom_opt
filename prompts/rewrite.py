"""
Prompts para reescritura de contenido competitivo - PcComponentes Content Generator
Versión 4.1.1

Este módulo contiene las funciones para construir los prompts del modo REESCRITURA,
que analiza contenido competidor y genera una versión mejorada.

Flujo de reescritura:
1. Análisis de URLs competidoras (top 5 resultados orgánicos)
2. Identificación de gaps y oportunidades de mejora
3. Generación de versión mejorada en 3 etapas:
   - Etapa 1: Borrador mejorado basado en análisis competitivo
   - Etapa 2: Análisis crítico y detección de problemas
   - Etapa 3: Generación final con correcciones aplicadas

Autor: PcComponentes - Product Discovery & Content
"""

import json
import re
from typing import Dict, List, Optional

# Importar configuración y estilos
from config.brand import CSS_CMS_COMPATIBLE, BRAND_TONE


# ============================================================================
# INSTRUCCIONES DE ESTRUCTURA HTML - v4.1.1
# ============================================================================

HTML_STRUCTURE_INSTRUCTIONS = """
# ESTRUCTURA HTML OBLIGATORIA (v4.1.1 - COMPATIBLE CMS):

⚠️ CRITICAL: El CMS de PcComponentes requiere EXACTAMENTE esta estructura:
```html
<style>
[CSS con variables :root - OBLIGATORIO]
</style>

<article><span class="kicker">⚡ OFERTA BLACK FRIDAY 2025</span></article>

<article></article>

<article>
  <div class="bf-callout">⚡ <strong>Black Friday 2025:</strong> Texto del callout con <a href="url">enlace</a>.</div>
  
  <h2>[Título principal del artículo - USAR H2, NO H1]</h2>
  
  <p>Primer párrafo introductorio...</p>
  
  [Resto del contenido: TOC, secciones H2, callouts, tablas, FAQs, verdict-box, etc.]
  
  <p class="note">Nota final si aplica</p>
</article>
```

# REGLAS CRÍTICAS DEL CMS:

1. ✅ ESTRUCTURA DE 3 ARTICLES (OBLIGATORIO):
   - ARTICLE 1: Solo el kicker → <article><span class="kicker">TEXTO</span></article>
   - ARTICLE 2: Vacío (separador) → <article></article>
   - ARTICLE 3: Todo el contenido → <article>[CONTENIDO COMPLETO]</article>

2. ✅ KICKER:
   - Debe estar SOLO en el primer <article>
   - Formato: <span class="kicker">⚡ TEXTO</span>
   - Nunca usar <div class="kicker">

3. ✅ TÍTULO PRINCIPAL:
   - Usar <h2> como título principal (NO <h1>)
   - El H2 va dentro del tercer <article>
   - Subsecciones con <h2>, <h3>, <h4>

4. ✅ CSS COMPLETO:
   - Incluir ANTES del primer <article>
   - Con todas las variables :root definidas
   - Todas las clases disponibles

5. ✅ SIN MÓDULOS:
   - NO incluir shortcodes #MODULE_START# ni #MODULE_END#
   - Los módulos se añaden manualmente después

# EJEMPLO COMPLETO VÁLIDO:

<style>
:root{{
  --orange-900:#FF6000;--blue-m-900:#170453;--white:#FFFFFF;
  [resto de variables...]
}}
[resto de CSS...]
</style>

<article><span class="kicker">⚡ BLACK FRIDAY 2025</span></article>

<article></article>

<article>
  <div class="bf-callout">⚡ <strong>Black Friday 2025:</strong> Ofertas reales en <a href="#">categoría</a>.</div>
  
  <h2>Título Principal del Artículo</h2>
  
  <p>Introducción al contenido...</p>
  
  <div class="toc">
    <h4>Lo que vas a encontrar</h4>
    <a href="#seccion1">Primera sección</a>
    <a href="#seccion2">Segunda sección</a>
  </div>
  
  <h2 id="seccion1">Primera Sección</h2>
  <p>Contenido de la sección...</p>
  
  <div class="faqs">
    <div class="q">¿Pregunta?</div>
    <div class="a">Respuesta...</div>
  </div>
  
  <div class="verdict-box">
    <h3>Veredicto final</h3>
    <ul><li>Punto 1</li></ul>
  </div>
  
  <p class="note">Nota final del artículo.</p>
</article>
"""


# ============================================================================
# FUNCIONES DE FORMATEO DE COMPETIDORES
# ============================================================================

def format_competitors_for_prompt(competitors_data: List[Dict]) -> List[Dict[str, str]]:
    """
    Formatea los datos de competidores para usar en el prompt de análisis.
    
    Esta función es el punto de entrada principal para formatear datos de
    competidores antes de pasarlos al prompt de análisis competitivo.
    
    Args:
        competitors_data: Lista de dicts con datos de competidores.
            Cada dict puede contener:
            - url: URL del competidor
            - title: Título de la página
            - content: Contenido scrapeado
            - word_count: Número de palabras
            - scrape_success: Si el scraping fue exitoso
            
    Returns:
        Lista de dicts formateados con 'url', 'title', 'content' listos
        para ser usados en el prompt de análisis.
        
    Example:
        >>> competitors = [
        ...     {'url': 'https://example.com', 'title': 'Test', 'content': 'Content...', 'scrape_success': True}
        ... ]
        >>> formatted = format_competitors_for_prompt(competitors)
        >>> len(formatted)
        1
        
    Notes:
        - Filtra competidores sin contenido válido
        - Limita contenido a 3000 caracteres por competidor
        - Máximo 5 competidores procesados
    """
    if not competitors_data:
        return []
    
    formatted = []
    
    for comp in competitors_data[:5]:  # Máximo 5 competidores
        # Solo incluir si tiene contenido válido
        if not comp.get('scrape_success', False) and not comp.get('content'):
            continue
        
        formatted_comp = {
            'url': comp.get('url', 'N/A'),
            'title': comp.get('title', 'Sin título'),
            'content': clean_content_for_analysis(comp.get('content', ''))
        }
        
        # Solo añadir si tiene contenido
        if formatted_comp['content'] and len(formatted_comp['content']) > 50:
            formatted.append(formatted_comp)
    
    return formatted


def format_competitor_data_for_analysis(competitors: List[Dict]) -> List[Dict[str, str]]:
    """
    Formatea los datos de competidores para el análisis.
    
    Alias de format_competitors_for_prompt para compatibilidad.
    
    Args:
        competitors: Lista de dicts con datos scrapeados de competidores
        
    Returns:
        Lista de dicts formateados con 'url', 'title', 'content'
    """
    return format_competitors_for_prompt(competitors)


def clean_content_for_analysis(content: str, max_chars: int = 3000) -> str:
    """
    Limpia contenido HTML para análisis, removiendo tags y limitando longitud.
    
    Args:
        content: Contenido HTML a limpiar
        max_chars: Número máximo de caracteres a retornar
        
    Returns:
        str: Contenido limpio y truncado
        
    Notes:
        - Remueve todos los tags HTML
        - Normaliza espacios en blanco
        - Trunca a max_chars si es más largo
    """
    if not content:
        return "No se pudo extraer contenido"
    
    # Remover tags HTML básicos
    clean = re.sub(r'<[^>]+>', '', content)
    
    # Normalizar espacios
    clean = ' '.join(clean.split())
    
    # Truncar si es necesario
    if len(clean) > max_chars:
        clean = clean[:max_chars] + "...[truncado]"
    
    return clean


# ============================================================================
# ANÁLISIS DE COMPETIDORES
# ============================================================================

def build_competitor_analysis_prompt(
    keyword: str,
    competitor_contents: List[Dict[str, str]],
    target_length: int
) -> str:
    """
    Construye el prompt para analizar el contenido de los competidores.
    
    Este análisis identifica:
    - Temas y subtemas cubiertos por cada competidor
    - Gaps de contenido (qué falta o está poco desarrollado)
    - Oportunidades de mejora y diferenciación
    - Fortalezas y debilidades del contenido competidor
    
    Args:
        keyword: Keyword principal para la que se quiere rankear
        competitor_contents: Lista de dicts con 'url', 'title' y 'content' de cada competidor
        target_length: Longitud objetivo para nuestro contenido
        
    Returns:
        str: Prompt completo para análisis competitivo
        
    Notes:
        - El output esperado es un JSON estructurado
        - Analiza máximo 5 URLs competidoras
        - Identifica gaps y oportunidades concretas
    """
    
    # Formatear contenido de competidores
    competitors_formatted = ""
    for i, comp in enumerate(competitor_contents[:5], 1):  # Máximo 5
        competitors_formatted += f"""
## COMPETIDOR {i}:
URL: {comp.get('url', 'N/A')}
Título: {comp.get('title', 'Sin título')}

Contenido:
{comp.get('content', 'No se pudo extraer contenido')[:3000]}
{'...[contenido truncado]' if len(comp.get('content', '')) > 3000 else ''}

---
"""
    
    prompt = f"""
# TAREA: ANÁLISIS COMPETITIVO DE CONTENIDO

Eres estratega SEO y content analyst de PcComponentes.
Tu trabajo es analizar el contenido de los competidores que rankean en top 5 para la keyword objetivo.

# KEYWORD OBJETIVO:
"{keyword}"

# CONTENIDO DE COMPETIDORES (TOP 5):

{competitors_formatted}

# TU TRABAJO:

Analiza el contenido competidor y responde en formato JSON estructurado:

{{
  "keyword_analizada": "{keyword}",
  "competidores_analizados": <número de URLs analizadas>,
  "temas_comunes": [
    {{
      "tema": "Tema que todos cubren",
      "frecuencia": "Cuántos competidores lo mencionan",
      "profundidad": "superficial|media|profunda",
      "calidad_promedio": "baja|media|alta"
    }}
  ],
  "gaps_identificados": [
    {{
      "gap": "Descripción del gap de contenido",
      "oportunidad": "Por qué es una oportunidad para nosotros",
      "prioridad": "alta|media|baja",
      "como_cubrirlo": "Cómo deberíamos abordarlo"
    }}
  ],
  "fortalezas_competidores": [
    "Aspectos que los competidores hacen bien"
  ],
  "debilidades_competidores": [
    "Aspectos donde los competidores fallan o son débiles"
  ],
  "oportunidades_diferenciacion": [
    {{
      "oportunidad": "Descripción de la oportunidad",
      "como_aprovecharla": "Estrategia concreta para diferenciarnos",
      "valor_para_usuario": "Qué valor aporta esto al usuario"
    }}
  ],
  "estructura_recomendada": [
    "Lista ordenada de secciones que nuestro contenido debería tener",
    "Basándote en lo que funciona + los gaps identificados"
  ],
  "enfoque_diferenciador": "Descripción de cómo nuestro contenido debe diferenciarse",
  "longitud_competidores": {{
    "promedio_palabras": <número estimado>,
    "rango": "X-Y palabras",
    "recomendacion_nuestra": "Nuestra longitud objetivo de {target_length} palabras es adecuada|corta|larga"
  }}
}}

# CRITERIOS DE ANÁLISIS:

1. **Cobertura de temas**: ¿Qué temas cubren todos? ¿Cuáles solo algunos?
2. **Profundidad**: ¿Qué tan profundo es el análisis en cada tema?
3. **Estructura**: ¿Qué estructuras usan? ¿Funcionan bien?
4. **Valor práctico**: ¿Dan información útil y accionable?
5. **Actualidad**: ¿Contenido actualizado o desactualizado?
6. **Autoridad**: ¿Demuestran expertise real?
7. **UX del contenido**: ¿Fácil de leer y navegar?
8. **Elementos visuales**: ¿Usan tablas, callouts, FAQs efectivamente?
9. **Gaps críticos**: ¿Qué información importante falta?
10. **Oportunidades SEO**: ¿Qué keywords relacionadas no explotan?

# ENFOQUE ESTRATÉGICO:

- Identifica los **3-5 gaps más importantes** que podemos aprovechar
- Propón una **estructura diferenciadora** que supere a la competencia
- Sugiere un **ángulo único** que nos haga destacar
- Prioriza **valor real para el usuario** sobre optimización SEO mecánica

# IMPORTANTE:

- Sé específico y concreto en tus recomendaciones
- No te limites a describir; propón acciones claras
- Piensa como usuario: ¿qué mejoraría su experiencia?
- Considera la autoridad de PcComponentes como expertos en tecnología

GENERA AHORA EL ANÁLISIS COMPETITIVO.
Responde SOLO con el JSON (sin bloques de código markdown, solo el JSON puro).
"""
    
    return prompt


# ============================================================================
# ETAPA 1: GENERACIÓN DEL BORRADOR MEJORADO
# ============================================================================

def build_rewrite_prompt_stage1_draft(
    keyword: str,
    competitor_analysis: str,
    pdp_data: Optional[Dict],
    target_length: int,
    keywords: List[str],
    context: str,
    links: Dict,
    objetivo: str,
    producto_alternativo: Dict,
    arquetipo: Optional[Dict] = None
) -> str:
    """
    Construye el prompt para la ETAPA 1: Borrador mejorado basado en análisis competitivo.
    
    Esta etapa genera un borrador inicial del contenido reescrito, aprovechando
    los insights del análisis competitivo para crear algo superior a lo que
    rankea actualmente en Google.
    
    Args:
        keyword: Keyword principal objetivo
        competitor_analysis: JSON con el análisis de competidores
        pdp_data: Datos del producto scrapeados (opcional)
        target_length: Longitud objetivo en palabras
        keywords: Lista de keywords SEO adicionales
        context: Contexto adicional del usuario
        links: Dict con enlaces principales y secundarios
        objetivo: Objetivo del contenido
        producto_alternativo: Dict con URL y texto del producto alternativo
        arquetipo: Dict con información del arquetipo (opcional en modo rewrite)
        
    Returns:
        str: Prompt completo para la etapa 1 de reescritura
        
    Notes:
        - Usa el análisis competitivo como guía estratégica
        - Debe superar al contenido competidor identificando y cubriendo gaps
        - Mantiene estructura HTML v4.1.1
    """
    
    # Formatear keywords
    keywords_str = ", ".join(keywords) if keywords else "No especificadas"
    
    # Extraer información de enlaces
    link_principal = links.get('principal', {})
    links_secundarios = links.get('secundarios', [])
    
    # Construir sección de enlaces
    link_info = ""
    if link_principal.get('url'):
        link_info = f"""
# ENLACES A INCLUIR:

## Enlace Principal (OBLIGATORIO):
URL: {link_principal.get('url')}
Texto anchor: {link_principal.get('text')}
Ubicación: Primeros 2-3 párrafos del contenido

Integra este enlace de forma natural en el contexto del contenido.
"""
    
    if links_secundarios:
        link_info += f"""
## Enlaces Secundarios (Opcional):
{chr(10).join([f"- URL: {link.get('url')} | Texto anchor: {link.get('text')}" for link in links_secundarios])}

Integra estos enlaces donde sean relevantes en el contenido.
"""
    
    # Construir sección de producto alternativo
    alternativo_info = ""
    if producto_alternativo.get('url'):
        alternativo_info = f"""
# PRODUCTO ALTERNATIVO CONFIGURADO:

URL: {producto_alternativo.get('url')}
Texto: {producto_alternativo.get('text', 'producto alternativo')}

IMPORTANTE: En el veredicto final, incluye una sección "Considera alternativas si:"
con enlace a este producto alternativo para casos de uso específicos.
"""
    else:
        alternativo_info = """
# PRODUCTO ALTERNATIVO: NO CONFIGURADO

En el veredicto final usa SOLO la sección "✅ Perfecto si:" desarrollada extensamente.
NO incluyas sección "Considera alternativas si:" a menos que menciones productos
de forma genérica (sin enlaces específicos).
"""
    
    # Contexto de arquetipo si está disponible
    arquetipo_info = ""
    if arquetipo:
        arquetipo_info = f"""
# ARQUETIPO DE REFERENCIA:
{arquetipo['code']} - {arquetipo['name']}
Descripción: {arquetipo['description']}

Usa este arquetipo como guía estructural, pero prioriza el análisis competitivo.
"""
    
    # Calcular rangos de longitud
    min_length = int(target_length * 0.95)
    max_length = int(target_length * 1.05)
    
    prompt = f"""
# TAREA: REESCRITURA MEJORADA - BORRADOR INICIAL (ETAPA 1/3)

Eres experto redactor de PcComponentes especializado en contenido que supera a la competencia.

Esta es la ETAPA 1 del proceso de REESCRITURA: Genera un BORRADOR MEJORADO que supere
al contenido competidor actualmente rankeando en Google.

# KEYWORD OBJETIVO:
"{keyword}"

# OBJETIVO DEL CONTENIDO:
{objetivo}

{arquetipo_info}

# ANÁLISIS COMPETITIVO:

{competitor_analysis}

# ESTRATEGIA DE REESCRITURA:

Basándote en el análisis competitivo, tu contenido debe:

1. **Cubrir todos los gaps identificados**: No dejes preguntas sin responder
2. **Superar en profundidad**: Donde la competencia es superficial, profundiza
3. **Diferenciarse claramente**: Usa el enfoque diferenciador sugerido
4. **Aportar valor único**: Información que otros no tienen
5. **Mejor estructura**: Más clara, lógica y navegable que la competencia
6. **Autoridad PcComponentes**: Usa nuestro expertise en tecnología
7. **Actualidad**: Información más actual y relevante que los competidores

# DATOS DEL PRODUCTO:
{json.dumps(pdp_data, indent=2, ensure_ascii=False) if pdp_data else "N/A - Este contenido no está centrado en un producto específico"}

# CONTEXTO ADICIONAL:
{context if context else "Condiciones estándar de PcComponentes"}

# KEYWORDS SEO:
Keyword principal: {keyword}
Keywords secundarias: {keywords_str}

Integra las keywords de forma NATURAL en el contenido, sin forzar su inclusión.

{link_info}

{alternativo_info}

# CONTROL ESTRICTO DE LONGITUD:

**LONGITUD OBJETIVO: {target_length} palabras**

CRÍTICO - CONTROL DE EXTENSIÓN:
- Genera EXACTAMENTE entre {min_length} y {max_length} palabras
- Cuenta palabras mientras escribes
- Si te quedas corto, desarrolla más las secciones principales
- Si te pasas, sé más conciso en descripciones
- La longitud es CRÍTICA para la aprobación del contenido

# FORMATO DE OUTPUT - HTML PURO (NO MARKDOWN):

Genera HTML puro y funcional. NO uses sintaxis markdown en ningún caso.
NO uses bloques de código con ```.

{HTML_STRUCTURE_INSTRUCTIONS}

# CSS OBLIGATORIO (COPIAR EXACTAMENTE AL INICIO):

{CSS_CMS_COMPATIBLE}

# ESTRUCTURA DETALLADA DEL CONTENIDO:

El contenido debe seguir esta estructura EXACTA:

1. <style> con CSS completo
2. <article><span class="kicker">⚡ ETIQUETA</span></article>
3. <article></article>
4. <article>
   - Callout Black Friday (.bf-callout)
   - Título principal (<h2>) - más atractivo que la competencia
   - Introducción (2-3 párrafos) - más engaging que competidores
   - Tabla de contenidos (.toc) - estructura clara
   - Secciones principales con <h2> - cubriendo gaps identificados
   - Subsecciones con <h3> y <h4> - mayor profundidad
   - Callouts para información importante
   - Tablas para comparaciones (usa .lt) - mejor organizadas
   - FAQs si es relevante (.faqs) - responde dudas que competencia ignora
   - Veredicto final (.verdict-box) - más útil y práctico
   - Nota final opcional (.note)
   </article>

# CLASES CSS OBLIGATORIAS A USAR:

✅ .kicker - Para la etiqueta superior (usar con <span>, NUNCA con <div>)
✅ .bf-callout - Para el callout de Black Friday (OBLIGATORIO)
✅ .callout - Para destacados importantes
✅ .callout.accent - Para destacados urgentes (ofertas)
✅ .toc - Para tabla de contenidos
✅ .lt, .lt .r, .lt .c - Para tablas de especificaciones
✅ .lt.zebra - Para tablas con filas alternas
✅ .lt.cols-2, .lt.cols-3, .lt.cols-7 - Para definir columnas en tablas
✅ .grid, .grid.cols-2, .grid.cols-3 - Para layouts en grid
✅ .card - Para tarjetas de contenido
✅ .badges, .badge - Para tags de características
✅ .btns, .btn, .btn.primary, .btn.ghost - Para botones (si aplica)
✅ .faqs, .faqs .q, .faqs .a - Para sección de FAQs
✅ .verdict-box - Para el box de veredicto final
✅ .hr - Para separadores visuales
✅ .note - Para notas pequeñas al final

# TONO DE MARCA PCCOMPONENTES:

{BRAND_TONE}

## RECORDATORIOS CLAVE DEL TONO:

✅ HACER:
- Enfoque aspiracional y positivo
- "Perfecto si..." en lugar de "Evita si..."
- Honestidad sin negatividad
- Expertos sin pedantería
- Cercanos pero profesionales

❌ NO HACER:
- Negatividad o desánimo
- "Este producto no tiene X" → "Funciona con Y; si necesitas X, hay alternativas"
- Lenguaje robótico o corporativo
- Exceso de emojis (solo ✅ ⚡ en puntos clave)
- Frases como "No recomendado para..."

# VENTAJA COMPETITIVA - LO QUE HARÁS MEJOR:

Basándote en el análisis competitivo, supera a los competidores en:

1. **Gaps cubiertos**: Responde todas las preguntas que ellos dejaron sin responder
2. **Mayor profundidad**: Desarrolla temas que ellos solo mencionan superficialmente
3. **Mejor estructura**: Organización más lógica y fácil de navegar
4. **Valor práctico**: Más ejemplos, casos reales, consejos accionables
5. **Actualidad**: Información más reciente y relevante
6. **Autoridad**: Demuestra el expertise real de PcComponentes
7. **UX superior**: Mejor uso de callouts, tablas, FAQs, elementos visuales
8. **Diferenciación clara**: El ángulo único que nos hace destacar

# VERIFICACIÓN FINAL ANTES DE ENTREGAR EL BORRADOR:

Antes de generar el output, verifica TODOS estos puntos:

1. ✅ ¿Tiene estructura de 3 articles separados?
2. ✅ ¿Primer article solo tiene kicker con <span>?
3. ✅ ¿Segundo article está vacío?
4. ✅ ¿Todo el contenido está en el tercer article?
5. ✅ ¿El CSS completo está al inicio?
6. ✅ ¿El título principal usa <h2> (NO <h1>)?
7. ✅ ¿Tiene entre {min_length} y {max_length} palabras?
8. ✅ ¿Es HTML puro (sin markdown)?
9. ✅ ¿El tono es aspiracional y positivo?
10. ✅ ¿Los enlaces están incluidos y bien integrados?
11. ✅ ¿Usa las clases CSS definidas (NO estilos inline)?
12. ✅ ¿Incluye el callout de Black Friday?
13. ✅ ¿Cubre TODOS los gaps identificados en el análisis?
14. ✅ ¿Supera en profundidad al contenido competidor?
15. ✅ ¿Tiene el enfoque diferenciador del análisis?
16. ✅ ¿Aporta valor único más allá de la competencia?

# INSTRUCCIONES FINALES:

GENERA AHORA EL BORRADOR MEJORADO que SUPERE al contenido competidor.

Este contenido debe ser:
- Más completo que la competencia
- Más útil para el usuario
- Mejor estructurado
- Más actual y relevante
- Con información que solo PcComponentes puede aportar

Responde SOLO con el HTML completo (desde <style> hasta el cierre del tercer </article>).
NO incluyas explicaciones, comentarios ni texto adicional fuera del HTML.
"""
    
    return prompt


# ============================================================================
# ETAPA 2: ANÁLISIS CRÍTICO DEL BORRADOR REESCRITO
# ============================================================================

def build_rewrite_correction_prompt_stage2(
    draft_content: str,
    target_length: int,
    keyword: str,
    competitor_analysis: str,
    objetivo: str
) -> str:
    """
    Construye el prompt para la ETAPA 2: Análisis crítico del borrador reescrito.
    
    Esta etapa analiza el borrador generado en Etapa 1 y verifica que:
    - Cumple con los requisitos técnicos (estructura HTML, longitud, etc.)
    - Supera efectivamente al contenido competidor
    - Cubre todos los gaps identificados
    - Mantiene el enfoque diferenciador
    
    Args:
        draft_content: HTML del borrador generado en Etapa 1
        target_length: Longitud objetivo en palabras
        keyword: Keyword principal
        competitor_analysis: JSON con análisis competitivo previo
        objetivo: Objetivo del contenido
        
    Returns:
        str: Prompt completo para la etapa 2
        
    Notes:
        - El output esperado es un JSON estructurado
        - Debe validar que se superó a la competencia
        - Verifica cobertura de gaps identificados
    """
    
    min_length = int(target_length * 0.95)
    max_length = int(target_length * 1.05)
    
    prompt = f"""
# TAREA: ANÁLISIS CRÍTICO DEL BORRADOR REESCRITO (ETAPA 2/3)

Eres editor senior de PcComponentes especializado en content review y análisis competitivo.
Tu trabajo es CRITICAR el borrador reescrito y verificar que SUPERA al contenido competidor.

# KEYWORD OBJETIVO:
"{keyword}"

# OBJETIVO DEL CONTENIDO:
{objetivo}

# ANÁLISIS COMPETITIVO DE REFERENCIA:

{competitor_analysis}

# BORRADOR REESCRITO A ANALIZAR:

{draft_content}

# TU TRABAJO:

Analiza el borrador con dos enfoques:

1. **Validación técnica**: Cumple requisitos de estructura, longitud, formato
2. **Validación competitiva**: Supera efectivamente al contenido competidor

Responde SOLO en formato JSON:

{{
  "longitud_actual": <número de palabras contadas en el borrador>,
  "longitud_objetivo": {target_length},
  "necesita_ajuste_longitud": true/false,
  "estructura_html": {{
    "tiene_3_articles": true/false,
    "primer_article_solo_kicker": true/false,
    "segundo_article_vacio": true/false,
    "kicker_usa_span": true/false,
    "titulo_usa_h2": true/false,
    "css_tiene_root": true/false
  }},
  "analisis_competitivo": {{
    "gaps_cubiertos": [
      {{
        "gap": "Gap identificado en análisis",
        "cubierto": true/false,
        "comentario": "Cómo se cubrió o por qué falta"
      }}
    ],
    "supera_en_profundidad": true/false,
    "comentario_profundidad": "Evaluación de la profundidad vs competencia",
    "tiene_enfoque_diferenciador": true/false,
    "comentario_diferenciacion": "Evaluación del enfoque diferenciador",
    "aporta_valor_unico": true/false,
    "comentario_valor": "Qué valor único aporta vs competencia"
  }},
  "problemas_encontrados": [
    {{
      "tipo": "longitud|estructura|tono|enlaces|seo|css|contenido|competitivo",
      "gravedad": "crítico|medio|menor",
      "descripcion": "Descripción clara y específica del problema",
      "ubicacion": "Dónde exactamente está el problema",
      "correccion_sugerida": "Cómo corregirlo paso a paso"
    }}
  ],
  "fortalezas_vs_competencia": [
    "Aspectos donde nuestro contenido supera claramente a la competencia"
  ],
  "debilidades_vs_competencia": [
    "Aspectos donde aún no superamos a la competencia o quedamos cortos"
  ],
  "instrucciones_revision": [
    "Instrucciones específicas y detalladas para la corrección final"
  ],
  "veredicto_competitivo": "supera_claramente|supera_parcialmente|no_supera",
  "necesita_reescritura_completa": true/false
}}

# CRITERIOS DE EVALUACIÓN (ORDEN DE PRIORIDAD):

## A. VALIDACIÓN TÉCNICA (REQUISITOS MÍNIMOS):

### 1. ESTRUCTURA HTML v4.1.1 (CRÍTICO):
   - ¿Tiene exactamente 3 tags <article>? → CRÍTICO si no
   - ¿Primer <article> contiene SOLO <span class="kicker">TEXTO</span>? → CRÍTICO si no
   - ¿Segundo <article> está completamente vacío? → CRÍTICO si no
   - ¿Todo el contenido está en el tercer <article>? → CRÍTICO si no
   - ¿El kicker usa <span class="kicker"> y NO <div>? → CRÍTICO si usa div
   - ¿El título principal usa <h2> y NO <h1>? → CRÍTICO si usa h1
   - ¿El CSS tiene variables :root? → CRÍTICO si falta

### 2. LONGITUD (CRÍTICO):
   - ¿Está en rango {min_length}-{max_length} palabras?
   - Si no, ¿qué secciones específicas se deben ampliar o reducir?

### 3. HTML PURO (CRÍTICO):
   - ¿Hay sintaxis markdown (**, ##, [], ```)? → CRÍTICO
   - ¿Está bien formateado y sin errores?

### 4. CSS Y CLASES:
   - ¿Usa las clases CSS definidas correctamente?
   - ¿Las tablas usan estructura .lt correcta?

### 5. TONO DE MARCA:
   - ¿Es aspiracional y positivo?
   - ¿Evita negatividad?

## B. VALIDACIÓN COMPETITIVA (DIFERENCIACIÓN):

### 6. COBERTURA DE GAPS (CRÍTICO):
   - Para cada gap identificado en el análisis competitivo:
     * ¿Está cubierto en nuestro contenido?
     * ¿Con suficiente profundidad?
     * ¿Aporta más valor que si los competidores lo hubieran cubierto?

### 7. PROFUNDIDAD VS COMPETENCIA:
   - En temas comunes, ¿profundizamos más?
   - ¿Aportamos información adicional útil?
   - ¿Ejemplos más prácticos y aplicables?

### 8. ENFOQUE DIFERENCIADOR:
   - ¿Se aplica el enfoque diferenciador del análisis?
   - ¿Es claro por qué somos diferentes?
   - ¿La diferenciación aporta valor real?

### 9. VALOR ÚNICO DE PCCOMPONENTES:
   - ¿Se aprovecha nuestra autoridad en tecnología?
   - ¿Hay información que solo nosotros podemos aportar?
   - ¿Insights basados en nuestra experiencia?

### 10. ESTRUCTURA SUPERIOR:
    - ¿Más fácil de navegar que la competencia?
    - ¿Mejor uso de elementos visuales (tablas, callouts, FAQs)?
    - ¿Organización más lógica?

### 11. ACTUALIDAD:
    - ¿Información más reciente que competidores?
    - ¿Referencias a tendencias actuales?

### 12. UTILIDAD PRÁCTICA:
    - ¿Más accionable que la competencia?
    - ¿Ayuda mejor al usuario a tomar decisiones?

# IMPORTANTE:

## Para problemas técnicos:
- Sé preciso en ubicación y corrección
- Prioriza por gravedad

## Para problemas competitivos:
- Compara específicamente con lo que hace la competencia
- Identifica exactamente dónde nos quedamos cortos
- Sugiere cómo superar esa brecha específica

## Veredicto competitivo:
- "supera_claramente": Nuestro contenido es objetivamente mejor en la mayoría de aspectos
- "supera_parcialmente": Cubrimos gaps pero aún hay áreas donde no destacamos
- "no_supera": No logramos diferenciarnos suficientemente

GENERA AHORA EL ANÁLISIS CRÍTICO COMPLETO.
Responde SOLO con el JSON (sin bloques de código markdown, solo el JSON puro).
"""
    
    return prompt


# ============================================================================
# ETAPA 3: GENERACIÓN FINAL CON CORRECCIONES
# ============================================================================

def build_rewrite_final_prompt_stage3(
    draft_content: str,
    corrections_json: str,
    target_length: int,
    keyword: str
) -> str:
    """
    Construye el prompt para la ETAPA 3: Versión final con correcciones aplicadas.
    
    Esta etapa genera la versión final del contenido reescrito, aplicando
    todas las correcciones técnicas y competitivas identificadas en la Etapa 2.
    
    Args:
        draft_content: HTML del borrador de Etapa 1
        corrections_json: JSON con análisis y correcciones de Etapa 2
        target_length: Longitud objetivo en palabras
        keyword: Keyword principal
        
    Returns:
        str: Prompt completo para la etapa 3
        
    Notes:
        - Esta es la versión final que se entregará
        - Debe aplicar TODAS las correcciones
        - Debe garantizar superioridad vs competencia
    """
    
    min_length = int(target_length * 0.95)
    max_length = int(target_length * 1.05)
    
    prompt = f"""
# TAREA: VERSIÓN FINAL REESCRITA CON CORRECCIONES (ETAPA 3/3)

Esta es la ETAPA FINAL del proceso de reescritura.
Tu trabajo es generar la versión DEFINITIVA que SUPERE al contenido competidor.

# KEYWORD OBJETIVO:
"{keyword}"

# BORRADOR INICIAL (ETAPA 1):

{draft_content}

# ANÁLISIS CRÍTICO Y CORRECCIONES (ETAPA 2):

{corrections_json}

# TU TRABAJO:

Genera la VERSIÓN FINAL aplicando TODAS las correcciones (técnicas y competitivas).

Esta versión debe:
1. ✅ Cumplir TODOS los requisitos técnicos
2. ✅ Cubrir TODOS los gaps competitivos identificados
3. ✅ Superar CLARAMENTE a la competencia
4. ✅ Aportar valor único de PcComponentes

# INSTRUCCIONES CRÍTICAS (v4.1.1):

## Requisitos Técnicos Obligatorios:

1. **Estructura de 3 articles**: OBLIGATORIO mantener estructura exacta del CMS
2. **Primer article**: Solo <span class="kicker">TEXTO</span>
3. **Segundo article**: Completamente vacío
4. **Tercer article**: Todo el contenido
5. **Título principal**: DEBE usar <h2>, NUNCA <h1>
6. **Kicker**: OBLIGATORIO usar <span class="kicker">, NUNCA <div>
7. **Longitud**: DEBE estar entre {min_length} y {max_length} palabras
8. **HTML puro**: Elimina TODO resto de markdown si quedó alguno
9. **CSS**: Debe incluir el CSS completo con variables :root
10. **Clases CSS**: Usa TODAS las clases definidas correctamente
11. **NO estilos inline**: Reemplaza por clases CSS apropiadas

## Requisitos Competitivos Obligatorios:

12. **Gaps cubiertos**: TODOS los gaps identificados deben estar cubiertos
13. **Profundidad superior**: Desarrolla más que la competencia en temas clave
14. **Enfoque diferenciador**: Aplica la estrategia de diferenciación
15. **Valor único**: Incluye información que solo PcComponentes puede aportar
16. **Estructura superior**: Mejor organización y navegabilidad que competidores
17. **Utilidad práctica**: Más accionable y útil para toma de decisiones

## Calidad Final:

18. **Correcciones aplicadas**: TODAS las del JSON sin excepción
19. **Perfección técnica**: Sin errores de ningún tipo
20. **Superioridad competitiva**: Objetivamente mejor que lo que rankea ahora

# CSS OBLIGATORIO (debe aparecer al inicio):

{CSS_CMS_COMPATIBLE}

# ESTRUCTURA FINAL OBLIGATORIA:

<style>[CSS completo con :root y todas las clases]</style>

<article><span class="kicker">⚡ ETIQUETA</span></article>

<article></article>

<article>
  <div class="bf-callout">⚡ <strong>Black Friday:</strong> Texto con <a href="#">enlace</a>.</div>
  
  <h2>Título Principal (H2, NO H1)</h2>
  
  <p>Introducción superior a la competencia...</p>
  
  [Contenido completo, corregido, y que supera a competidores]
  
  <div class="verdict-box">
    <h3>Veredicto final</h3>
    <ul>
      <li>Conclusiones más útiles que la competencia</li>
    </ul>
  </div>
  
  <p class="note">Nota final opcional.</p>
</article>

# CHECKLIST DE VERIFICACIÓN FINAL:

Antes de generar el output, CONFIRMA que cumples:

## Técnicos:
✅ Estructura de 3 articles separados
✅ Primer article: solo kicker con <span>
✅ Segundo article: vacío
✅ Tercer article: todo el contenido
✅ CSS completo con :root al inicio
✅ Título principal usa <h2> (NO <h1>)
✅ Kicker con <span class="kicker"> (NO div)
✅ Longitud: {min_length}-{max_length} palabras
✅ Sin markdown (sin **, ##, [], ```)
✅ Clases CSS usadas correctamente
✅ Sin estilos inline innecesarios
✅ Callout Black Friday presente
✅ Todas las correcciones técnicas aplicadas

## Competitivos:
✅ Todos los gaps identificados cubiertos
✅ Mayor profundidad que competidores
✅ Enfoque diferenciador aplicado
✅ Valor único de PcComponentes presente
✅ Mejor estructura que competencia
✅ Más útil y práctico que competidores
✅ Información más actual
✅ Todas las correcciones competitivas aplicadas

## Calidad:
✅ Contenido perfecto y sin errores
✅ Supera objetivamente a la competencia
✅ Listo para publicación inmediata

# RECORDATORIO CRÍTICO:

Esta es la VERSIÓN FINAL que se publicará para competir con contenido que ya rankea en Google.
Debe ser IMPECABLE técnicamente y SUPERIOR competitivamente.

Si el análisis crítico identificó gaps sin cubrir o áreas donde no superamos a la competencia,
esta es tu oportunidad de CORREGIRLO completamente.

GENERA AHORA LA VERSIÓN FINAL PERFECTA Y COMPETITIVA.
Responde SOLO con el HTML completo (desde <style> hasta el cierre del tercer </article>).
NO incluyas explicaciones, comentarios ni bloques de código markdown.
"""
    
    return prompt


# ============================================================================
# FUNCIONES AUXILIARES ADICIONALES
# ============================================================================

def extract_gaps_from_analysis(analysis_json: str) -> List[str]:
    """
    Extrae los gaps identificados del JSON de análisis competitivo.
    
    Útil para verificar que todos los gaps se cubrieron en el contenido final.
    
    Args:
        analysis_json: String JSON con el análisis competitivo
        
    Returns:
        Lista de strings con los gaps identificados
        
    Notes:
        - Retorna lista vacía si el JSON es inválido
        - Extrae solo el campo 'gap' de cada elemento
    """
    try:
        analysis = json.loads(analysis_json)
        gaps = analysis.get('gaps_identificados', [])
        return [gap.get('gap', '') for gap in gaps if gap.get('gap')]
    except (json.JSONDecodeError, TypeError, AttributeError):
        return []


def validate_competitor_data(competitors_data: List[Dict]) -> List[Dict]:
    """
    Valida y filtra datos de competidores para asegurar calidad.
    
    Args:
        competitors_data: Lista de dicts con datos de competidores
        
    Returns:
        Lista filtrada con solo competidores válidos
        
    Notes:
        - Filtra competidores sin URL
        - Filtra competidores sin contenido scrapeado
        - Limita a máximo 5 competidores
    """
    if not competitors_data:
        return []
    
    valid_competitors = []
    
    for comp in competitors_data:
        # Debe tener URL
        if not comp.get('url'):
            continue
        
        # Debe tener contenido o ser marcado como exitoso
        has_content = bool(comp.get('content') and len(comp.get('content', '')) > 100)
        is_success = comp.get('scrape_success', False)
        
        if has_content or is_success:
            valid_competitors.append(comp)
        
        # Máximo 5 competidores
        if len(valid_competitors) >= 5:
            break
    
    return valid_competitors


def get_competitor_summary(competitors_data: List[Dict]) -> Dict:
    """
    Genera un resumen estadístico de los competidores analizados.
    
    Args:
        competitors_data: Lista de dicts con datos de competidores
        
    Returns:
        Dict con estadísticas:
        - total: número total de competidores
        - scraped_ok: número con scraping exitoso
        - avg_word_count: promedio de palabras
        - min_word_count: mínimo de palabras
        - max_word_count: máximo de palabras
    """
    if not competitors_data:
        return {
            'total': 0,
            'scraped_ok': 0,
            'avg_word_count': 0,
            'min_word_count': 0,
            'max_word_count': 0
        }
    
    scraped = [c for c in competitors_data if c.get('scrape_success', False)]
    word_counts = [c.get('word_count', 0) for c in scraped if c.get('word_count', 0) > 0]
    
    return {
        'total': len(competitors_data),
        'scraped_ok': len(scraped),
        'avg_word_count': int(sum(word_counts) / len(word_counts)) if word_counts else 0,
        'min_word_count': min(word_counts) if word_counts else 0,
        'max_word_count': max(word_counts) if word_counts else 0
    }


# ============================================================================
# CONSTANTES Y CONFIGURACIÓN
# ============================================================================

# Versión del módulo
__version__ = "4.1.1"

# Tolerancia de longitud por defecto (5%)
DEFAULT_LENGTH_TOLERANCE = 0.05

# Número máximo de competidores a analizar
MAX_COMPETITORS_ANALYZED = 5

# Número de caracteres máximo por competidor en análisis
MAX_COMPETITOR_CONTENT_CHARS = 3000

# Número mínimo de caracteres para considerar contenido válido
MIN_VALID_CONTENT_CHARS = 50
