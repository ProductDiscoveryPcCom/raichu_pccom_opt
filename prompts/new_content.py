"""
Prompts para generación de contenido nuevo - PcComponentes Content Generator
Versión 4.1.1

Este módulo contiene las funciones para construir los prompts de las 3 etapas
del flujo de generación de contenido NUEVO (no reescritura):

Etapa 1: Generación del borrador inicial
Etapa 2: Análisis crítico y detección de problemas
Etapa 3: Generación final con correcciones aplicadas

Autor: PcComponentes - Product Discovery & Content
"""

import json
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
# ETAPA 1: GENERACIÓN DEL BORRADOR INICIAL
# ============================================================================

def build_generation_prompt_stage1_draft(
    pdp_data: Optional[Dict],
    arquetipo: Dict,
    target_length: int,
    keywords: List[str],
    context: str,
    links: Dict,
    objetivo: str,
    producto_alternativo: Dict,
    casos_uso: List[str],
    campos_arquetipo: Dict
) -> str:
    """
    Construye el prompt para la ETAPA 1: Generación del borrador inicial.
    
    Esta es la primera etapa del flujo de 3 etapas. Genera un borrador inicial
    del contenido basándose en todos los inputs proporcionados por el usuario.
    
    Args:
        pdp_data: Datos del producto scrapeados (opcional)
        arquetipo: Dict con información del arquetipo seleccionado
        target_length: Longitud objetivo en palabras
        keywords: Lista de keywords SEO
        context: Contexto adicional proporcionado por el usuario
        links: Dict con enlaces principales y secundarios
        objetivo: Objetivo del contenido (OBLIGATORIO)
        producto_alternativo: Dict con URL y texto del producto alternativo
        casos_uso: Lista de casos de uso
        campos_arquetipo: Dict con valores de campos específicos del arquetipo
        
    Returns:
        str: Prompt completo para la etapa 1
        
    Notes:
        - El prompt incluye estructura HTML v4.1.1 con 3 articles
        - Incluye CSS completo compatible con CMS
        - Define control estricto de longitud (±5%)
        - Incluye tono de marca PcComponentes
    """
    
    # Formatear keywords
    keywords_str = ", ".join(keywords) if keywords else "No especificadas"
    
    # Construir contexto del arquetipo
    arquetipo_context = build_arquetipo_context(arquetipo['code'], campos_arquetipo)
    
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
        # Si no hay producto alternativo, dar instrucciones para casos de uso
        casos_uso_str = ""
        if casos_uso:
            casos_uso_str = f"\n\nCasos de uso proporcionados:\n" + "\n".join([f"- {caso}" for caso in casos_uso])
        
        alternativo_info = f"""
# PRODUCTO ALTERNATIVO: NO CONFIGURADO

Como no hay producto alternativo configurado, en el veredicto final usa SOLO
la sección "✅ Perfecto si:" desarrollada extensamente.

NO incluyas sección "Considera alternativas si:" a menos que menciones productos
de forma genérica (sin enlaces específicos).{casos_uso_str}
"""
    
    # Calcular rangos de longitud
    min_length = int(target_length * 0.95)
    max_length = int(target_length * 1.05)
    
    # Construir prompt completo
    prompt = f"""
# TAREA: GENERACIÓN DE BORRADOR INICIAL (ETAPA 1/3)

Eres experto redactor de PcComponentes especializado en contenido optimizado para Google Discover.

Esta es la ETAPA 1 del proceso de generación: Genera un BORRADOR INICIAL del contenido.

# OBJETIVO DEL CONTENIDO:
{objetivo}

# ARQUETIPO SELECCIONADO:
Código: {arquetipo['code']}
Nombre: {arquetipo['name']}
Descripción: {arquetipo['description']}
Embudo: {arquetipo['funnel']}
Caso de uso: {arquetipo['use_case']}

{arquetipo_context}

# DATOS DEL PRODUCTO:
{json.dumps(pdp_data, indent=2, ensure_ascii=False) if pdp_data else "N/A - Este contenido no está centrado en un producto específico"}

# CONTEXTO ADICIONAL:
{context if context else "Condiciones estándar de PcComponentes"}

# KEYWORDS SEO:
Keyword principal: {keywords[0] if keywords else "No especificada"}
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
   - Título principal (<h2>)
   - Introducción (2-3 párrafos)
   - Tabla de contenidos (.toc) si el contenido es extenso
   - Secciones principales con <h2>
   - Subsecciones con <h3> y <h4>
   - Callouts para información importante
   - Tablas para comparaciones (usa .lt)
   - FAQs si es relevante (.faqs)
   - Veredicto final (.verdict-box)
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
13. ✅ ¿Las tablas usan la estructura .lt correcta?
14. ✅ ¿Tiene veredicto final con .verdict-box?

# INSTRUCCIONES FINALES:

GENERA AHORA EL BORRADOR INICIAL del contenido.

Responde SOLO con el HTML completo (desde <style> hasta el cierre del tercer </article>).
NO incluyas explicaciones, comentarios ni texto adicional fuera del HTML.
"""
    
    return prompt


# ============================================================================
# ETAPA 2: ANÁLISIS CRÍTICO Y CORRECCIONES
# ============================================================================

def build_correction_prompt_stage2(
    draft_content: str,
    target_length: int,
    arquetipo: Dict,
    objetivo: str
) -> str:
    """
    Construye el prompt para la ETAPA 2: Análisis crítico del borrador.
    
    Esta etapa analiza el borrador generado en la Etapa 1 y detecta problemas,
    errores o áreas de mejora. El output es un JSON estructurado con los
    problemas encontrados y las correcciones sugeridas.
    
    Args:
        draft_content: HTML del borrador generado en Etapa 1
        target_length: Longitud objetivo en palabras
        arquetipo: Dict con información del arquetipo
        objetivo: Objetivo del contenido
        
    Returns:
        str: Prompt completo para la etapa 2
        
    Notes:
        - El output esperado es un JSON estructurado
        - Debe ser crítico y encontrar 3-5 problemas reales
        - Valida estructura HTML v4.1.1, longitud, tono, SEO
    """
    
    min_length = int(target_length * 0.95)
    max_length = int(target_length * 1.05)
    
    prompt = f"""
# TAREA: ANÁLISIS CRÍTICO DEL BORRADOR (ETAPA 2/3)

Eres editor senior de PcComponentes con años de experiencia en content review.
Tu trabajo es CRITICAR el borrador generado y proponer CORRECCIONES específicas.

# BORRADOR A ANALIZAR:

{draft_content}

# CONTEXTO DEL CONTENIDO:
- Arquetipo: {arquetipo['code']} - {arquetipo['name']}
- Objetivo: {objetivo}
- Longitud objetivo: {target_length} palabras (rango aceptable: {min_length}-{max_length})

# TU TRABAJO:

Analiza el borrador con OJO CRÍTICO de editor profesional y responde SOLO en formato JSON:

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
  "problemas_encontrados": [
    {{
      "tipo": "longitud|estructura|tono|enlaces|seo|css|contenido",
      "gravedad": "crítico|medio|menor",
      "descripcion": "Descripción clara y específica del problema",
      "ubicacion": "Dónde exactamente está el problema",
      "correccion_sugerida": "Cómo corregirlo paso a paso"
    }}
  ],
  "aspectos_positivos": [
    "Lista de cosas que están bien hechas en el borrador"
  ],
  "instrucciones_revision": [
    "Instrucciones específicas y detalladas para la corrección final"
  ],
  "necesita_reescritura_completa": true/false
}}

# CRITERIOS DE EVALUACIÓN (ORDEN DE PRIORIDAD):

## 1. ESTRUCTURA HTML v4.1.1 (CRÍTICO):
   - ¿Tiene exactamente 3 tags <article>? → CRÍTICO si no
   - ¿Primer <article> contiene SOLO <span class="kicker">TEXTO</span>? → CRÍTICO si no
   - ¿Segundo <article> está completamente vacío? → CRÍTICO si no
   - ¿Todo el contenido está en el tercer <article>? → CRÍTICO si no
   - ¿El kicker usa <span class="kicker"> y NO <div>? → CRÍTICO si usa div
   - ¿El título principal usa <h2> y NO <h1>? → CRÍTICO si usa h1
   - ¿El CSS tiene variables :root? → CRÍTICO si falta

## 2. LONGITUD (CRÍTICO):
   - ¿Está en rango {min_length}-{max_length} palabras?
   - Si no, ¿qué secciones específicas se deben ampliar o reducir?
   - ¿Cuántas palabras faltan o sobran exactamente?

## 3. HTML PURO (CRÍTICO):
   - ¿Hay sintaxis markdown (**, ##, [], ```)? → CRÍTICO
   - ¿Está bien formateado y sin errores de sintaxis?
   - ¿Todos los tags están correctamente cerrados?

## 4. CSS Y CLASES:
   - ¿Usa las clases CSS definidas (.kicker, .callout, .lt, .grid, etc.)?
   - ¿Hay estilos inline que deberían ser clases?
   - ¿Las tablas usan estructura .lt correcta?
   - ¿Falta alguna clase importante?

## 5. TONO DE MARCA:
   - ¿Es aspiracional y positivo (no negativo)?
   - ¿Evita frases como "no recomendado", "evita si"?
   - ¿Suena humano y cercano (no robótico)?
   - ¿Mantiene profesionalidad sin ser pedante?

## 6. ESTRUCTURA DE CONTENIDO:
   - ¿Sigue las directrices del arquetipo {arquetipo['code']}?
   - ¿Hay jerarquía HTML clara (h2 → h3 → h4)?
   - ¿Las secciones tienen orden lógico?
   - ¿Hay tabla de contenidos si el artículo es largo?

## 7. ENLACES:
   - ¿Están los enlaces obligatorios incluidos?
   - ¿Están integrados naturalmente en el texto?
   - ¿Incluye el callout de Black Friday (.bf-callout)?
   - ¿Los anchors son descriptivos?

## 8. SEO:
   - ¿Keywords integradas naturalmente (no forzadas)?
   - ¿Títulos y subtítulos optimizados?
   - ¿Meta información implícita clara?

## 9. VALOR Y UTILIDAD:
    - ¿Aporta información útil y práctica?
    - ¿Ayuda realmente al usuario a tomar decisiones?
    - ¿Hay suficiente profundidad en el análisis?
    - ¿Falta información importante?

## 10. ELEMENTOS ESPECÍFICOS:
    - ¿Tiene veredicto final (.verdict-box)?
    - ¿Las tablas son claras y útiles?
    - ¿Los callouts destacan lo importante?
    - ¿FAQs responden dudas reales?

# INSTRUCCIONES IMPORTANTES:

1. SÉ CRÍTICO Y RIGUROSO: Debes encontrar entre 3-5 problemas REALES
2. PRIORIZA por gravedad: Primero críticos, luego medios, luego menores
3. SÉ ESPECÍFICO: No digas "mejorar tono", di exactamente qué frases cambiar
4. DA SOLUCIONES: Cada problema debe tener una corrección clara
5. VALIDA TODO: Revisa cada criterio sistemáticamente

# RECORDATORIO:

Si el borrador es PERFECTO o casi perfecto (muy raro), indica que necesita
pocos cambios. Pero normalmente encontrarás varios problemas a corregir.

GENERA AHORA EL ANÁLISIS CRÍTICO.
Responde SOLO con el JSON (sin bloques de código markdown, solo el JSON puro).
"""
    
    return prompt


# ============================================================================
# ETAPA 3: GENERACIÓN FINAL CON CORRECCIONES
# ============================================================================

def build_final_generation_prompt_stage3(
    draft_content: str,
    corrections_json: str,
    target_length: int
) -> str:
    """
    Construye el prompt para la ETAPA 3: Generación final con correcciones.
    
    Esta etapa toma el borrador de la Etapa 1 y el análisis de la Etapa 2,
    y genera la versión final del contenido aplicando todas las correcciones
    identificadas.
    
    Args:
        draft_content: HTML del borrador de Etapa 1
        corrections_json: JSON con el análisis y correcciones de Etapa 2
        target_length: Longitud objetivo en palabras
        
    Returns:
        str: Prompt completo para la etapa 3
        
    Notes:
        - Esta es la versión final que se entregará al usuario
        - Debe aplicar TODAS las correcciones del JSON
        - Debe cumplir con todos los requisitos v4.1.1
    """
    
    min_length = int(target_length * 0.95)
    max_length = int(target_length * 1.05)
    
    prompt = f"""
# TAREA: GENERACIÓN FINAL CON CORRECCIONES (ETAPA 3/3)

Esta es la ETAPA FINAL del proceso de generación.
Tu trabajo es generar la versión DEFINITIVA del contenido aplicando TODAS las correcciones.

# BORRADOR INICIAL (ETAPA 1):

{draft_content}

# ANÁLISIS CRÍTICO Y CORRECCIONES (ETAPA 2):

{corrections_json}

# TU TRABAJO:

Genera la VERSIÓN FINAL del contenido aplicando METICULOSAMENTE todas las correcciones indicadas.

# INSTRUCCIONES CRÍTICAS (v4.1.1):

1. **Estructura de 3 articles**: OBLIGATORIO mantener estructura exacta del CMS
2. **Primer article**: Solo <span class="kicker">TEXTO</span>
3. **Segundo article**: Completamente vacío
4. **Tercer article**: Todo el contenido
5. **Título principal**: DEBE usar <h2>, NUNCA <h1>
6. **Kicker**: OBLIGATORIO usar <span class="kicker">, NUNCA <div>
7. **Longitud**: DEBE estar entre {min_length} y {max_length} palabras
8. **HTML puro**: Elimina TODO resto de markdown si quedó alguno
9. **CSS**: Debe incluir el CSS completo con variables :root
10. **Clases CSS**: Usa TODAS las clases definidas (.kicker, .callout, .lt, .grid, etc.)
11. **NO estilos inline**: Reemplaza estilos inline por clases CSS apropiadas
12. **Correcciones del JSON**: Aplica TODAS las correcciones listadas
13. **Calidad final**: Esta es la versión que verá el usuario - máxima calidad

# CSS OBLIGATORIO (debe aparecer al inicio):

{CSS_CMS_COMPATIBLE}

# ESTRUCTURA FINAL OBLIGATORIA:

<style>[CSS completo con :root y todas las clases]</style>

<article><span class="kicker">⚡ ETIQUETA</span></article>

<article></article>

<article>
  <div class="bf-callout">⚡ <strong>Black Friday:</strong> Texto con <a href="#">enlace</a>.</div>
  
  <h2>Título Principal (H2, NO H1)</h2>
  
  <p>Introducción...</p>
  
  [Contenido completo y corregido]
  
  <div class="verdict-box">
    <h3>Veredicto final</h3>
    <ul>
      <li>Punto 1</li>
      <li>Punto 2</li>
    </ul>
  </div>
  
  <p class="note">Nota final opcional.</p>
</article>

# CHECKLIST DE VERIFICACIÓN FINAL:

Antes de generar el output, CONFIRMA que cumples:

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
✅ Todas las correcciones del JSON aplicadas
✅ Tono aspiracional y positivo
✅ Enlaces incluidos y bien integrados
✅ Callout Black Friday presente (.bf-callout)
✅ Tablas con estructura .lt correcta
✅ Veredicto final con .verdict-box
✅ Contenido valioso y útil

# RECORDATORIO IMPORTANTE:

Esta es la VERSIÓN FINAL que se entregará al usuario.
Debe ser PERFECTA: sin errores, bien estructurada, útil y optimizada.

Si las correcciones indican que la longitud debe ajustarse:
- Para ALARGAR: Desarrolla más las secciones principales con información útil
- Para ACORTAR: Elimina redundancias y sé más conciso, pero mantén la calidad

GENERA AHORA LA VERSIÓN FINAL PERFECTA.
Responde SOLO con el HTML completo (desde <style> hasta el cierre del tercer </article>).
NO incluyas explicaciones, comentarios ni bloques de código markdown.
"""
    
    return prompt


# ============================================================================
# FUNCIONES AUXILIARES
# ============================================================================

def build_arquetipo_context(arquetipo_code: str, campos_valores: Dict) -> str:
    """
    Construye el contexto específico del arquetipo basado en los campos rellenados.
    
    Esta función toma los valores que el usuario ha introducido en los campos
    específicos del arquetipo y los formatea para incluirlos en el prompt.
    
    Args:
        arquetipo_code: Código del arquetipo (ej: "ARQ-1")
        campos_valores: Dict con los valores de los campos específicos
        
    Returns:
        str: Contexto formateado para incluir en el prompt, o string vacío si
             no hay campos rellenados
             
    Examples:
        >>> campos = {"noticia_principal": "Xiaomi lanza E5 Pro", "fecha_evento": "25/11/2025"}
        >>> context = build_arquetipo_context("ARQ-1", campos)
        >>> "Noticia Principal" in context
        True
    """
    if not campos_valores:
        return ""
    
    # Filtrar solo campos con valor
    campos_llenos = {k: v for k, v in campos_valores.items() if v and str(v).strip()}
    
    if not campos_llenos:
        return ""
    
    context = f"\n# INFORMACIÓN ESPECÍFICA DEL ARQUETIPO {arquetipo_code}:\n\n"
    context += "El usuario ha proporcionado la siguiente información específica para este tipo de contenido:\n\n"
    
    for campo_key, valor in campos_llenos.items():
        # Convertir el key a un label legible (snake_case a Title Case)
        label = campo_key.replace('_', ' ').title()
        context += f"**{label}:**\n{valor}\n\n"
    
    context += "IMPORTANTE: Usa esta información específica para crear contenido relevante y personalizado.\n"
    
    return context


def get_arquetipo_guidelines(arquetipo_code: str) -> str:
    """
    Devuelve directrices específicas de estructura para cada arquetipo.
    
    Algunos arquetipos tienen estructuras recomendadas específicas que ayudan
    a generar contenido más efectivo. Esta función devuelve esas directrices.
    
    Args:
        arquetipo_code: Código del arquetipo (ej: "ARQ-1")
        
    Returns:
        str: Directrices de estructura para el arquetipo, o directriz genérica
             si no hay específicas definidas
             
    Notes:
        - No todos los arquetipos tienen directrices específicas
        - Las directrices son recomendaciones, no requisitos estrictos
    """
    
    guidelines = {
        "ARQ-1": """
**Estructura recomendada para Noticia:**
1. Lead (primer párrafo): Las 5W (qué, quién, cuándo, dónde, por qué)
2. Contexto y antecedentes: Información de fondo relevante
3. Detalles específicos: Profundiza en la noticia
4. Declaraciones y fuentes: Citas o información oficial
5. Implicaciones para usuarios: Qué significa para los lectores
6. Conclusión: Proyección futura o próximos pasos
""",
        
        "ARQ-2": """
**Estructura recomendada para Guía Paso a Paso:**
1. Introducción: Qué se va a lograr
2. Requisitos previos: Qué se necesita antes de empezar
3. Pasos numerados: Instrucciones claras y secuenciales
4. Capturas o descripciones visuales: Para cada paso importante
5. Troubleshooting: Problemas comunes y soluciones
6. Conclusión: Verificación de que se logró el objetivo
""",
        
        "ARQ-4": """
**Estructura recomendada para Review:**
1. Veredicto rápido: Resumen ejecutivo (2-3 frases)
2. Contexto: Precio, competencia, posicionamiento
3. Diseño y construcción: Primera impresión física
4. Rendimiento: Datos reales de uso
5. Experiencia práctica: Uso en escenarios reales
6. Comparativa: Vs competencia directa
7. FAQs: Dudas comunes
8. Veredicto final: Recomendación clara con casos de uso
""",
        
        "ARQ-7": """
**Estructura recomendada para Roundup/Top:**
1. Introducción: Contexto de la selección
2. Criterios de selección: Por qué estos productos
3. Lista de productos: Del mejor al "peor" (o por categorías)
4. Cada producto: Análisis breve con pros destacados
5. Tabla comparativa: Especificaciones clave
6. Recomendaciones finales: Cuál elegir según perfil
7. Conclusión: Resumen ejecutivo
"""
    }
    
    return guidelines.get(
        arquetipo_code,
        "Sigue las mejores prácticas del arquetipo seleccionado, " 
        "estructurando el contenido de forma lógica y útil para el usuario."
    )


# ============================================================================
# CONSTANTES Y CONFIGURACIÓN
# ============================================================================

# Versión del módulo
__version__ = "4.1.1"

# Tolerancia de longitud por defecto (5%)
DEFAULT_LENGTH_TOLERANCE = 0.05

# Número de palabras mínimo recomendado
MIN_RECOMMENDED_WORDS = 800

# Número de palabras máximo recomendado
MAX_RECOMMENDED_WORDS = 3000
