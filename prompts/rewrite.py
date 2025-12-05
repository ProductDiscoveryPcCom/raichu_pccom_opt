# -*- coding: utf-8 -*-
"""
Rewrite Prompts - PcComponentes Content Generator
Versión 4.7.1

Prompts para reescritura de contenido basada en análisis competitivo.

CAMBIOS v4.7.1:
- NUEVO: Formateo de productos alternativos con JSON
- NUEVO: Formateo de enlaces editoriales con HTML contextual
  - Post: campo html_content único
  - PLP: campos top_text y bottom_text
- Mantiene todo de v4.7.0: instrucciones, fusión, desambiguación

Flujo de 3 etapas:
1. Borrador basado en análisis + instrucciones del usuario
2. Análisis crítico y correcciones
3. Versión final

Autor: PcComponentes - Product Discovery & Content
"""

from typing import Dict, List, Optional, Any
import json
import re

__version__ = "4.7.1"

# ============================================================================
# CONSTANTES
# ============================================================================

DEFAULT_LENGTH_TOLERANCE = 0.05
MAX_COMPETITORS_ANALYZED = 5
MAX_COMPETITOR_CONTENT_CHARS = 8000
MIN_VALID_CONTENT_CHARS = 200

# Estructura HTML del CMS
HTML_STRUCTURE_INSTRUCTIONS = """
## ESTRUCTURA HTML OBLIGATORIA (CMS PcComponentes)

El contenido DEBE seguir esta estructura exacta de 3 articles:

```html
<!-- ARTICLE 1: CABECERA -->
<article class="contentGenerator__header">
    <span class="kicker">TEXTO DEL KICKER</span>
</article>

<!-- ARTICLE 2: VACÍO (reservado para el CMS) -->
<article class="contentGenerator__reserved"></article>

<!-- ARTICLE 3: CONTENIDO PRINCIPAL -->
<article class="contentGenerator__main">
    <h2>Título Principal (NUNCA h1)</h2>
    
    <nav class="toc">
        <p class="toc__title">Contenido</p>
        <ul>
            <li><a href="#seccion1">Sección 1</a></li>
        </ul>
    </nav>
    
    <section id="seccion1">
        <h3>Título de Sección</h3>
        <p>Contenido...</p>
    </section>
    
    <section class="faqs">
        <h3>Preguntas frecuentes</h3>
        <div class="faq-item">
            <h4 class="faq-question">¿Pregunta?</h4>
            <p class="faq-answer">Respuesta...</p>
        </div>
    </section>
    
    <div class="verdict-box">
        <h3>Veredicto Final</h3>
        <p>Conclusión...</p>
    </div>
</article>
```

REGLAS CRÍTICAS:
- El título principal SIEMPRE es <h2>, NUNCA <h1>
- El kicker SIEMPRE usa <span class="kicker">, NUNCA <div>
- Las secciones usan <h3>, las FAQs usan <h4>
- NO usar estilos inline, solo clases CSS definidas
"""

# Tono de marca PcComponentes
BRAND_TONE = """
## TONO DE MARCA PCCOMPONENTES

Características esenciales:
- **Expertos sin ser pedantes**: Conocemos la tecnología pero la explicamos para todos
- **Frikis sin vergüenza**: Nos apasiona la tech y se nota
- **Cercanos pero profesionales**: Tuteamos, usamos humor sutil, pero con rigor
- **Orientados a ayudar**: Siempre guiamos hacia la mejor opción para el usuario
- **Nunca desanimamos**: Si algo no encaja, ofrecemos alternativas

Evitar:
- Lenguaje corporativo frío o distante
- Tecnicismos innecesarios sin explicación
- Frases negativas tipo "no hay opciones" o "no recomendamos"
- Comparaciones despectivas con competidores
- Promesas exageradas o marketing vacío

Usar:
- Segunda persona (tú/te/tu)
- Analogías tech cuando aportan valor
- Datos concretos y verificables
- Estructura clara y escaneable
- CTAs naturales integrados en el contenido
"""


# ============================================================================
# FORMATEO DE INSTRUCCIONES DE REESCRITURA
# ============================================================================

def format_rewrite_instructions(instructions: Dict[str, Any]) -> str:
    """
    Formatea las instrucciones de reescritura del usuario.
    """
    if not instructions:
        return ""
    
    sections = []
    
    improve = instructions.get('improve', [])
    if improve:
        sections.append("### ✨ ASPECTOS A MEJORAR (obligatorio aplicar)")
        for item in improve:
            sections.append(f"- {item}")
        sections.append("")
    
    maintain = instructions.get('maintain', [])
    if maintain:
        sections.append("### ✅ ASPECTOS A MANTENER (no modificar)")
        for item in maintain:
            sections.append(f"- {item}")
        sections.append("")
    
    remove = instructions.get('remove', [])
    if remove:
        sections.append("### 🗑️ CONTENIDO A ELIMINAR (obligatorio quitar)")
        for item in remove:
            sections.append(f"- {item}")
        sections.append("")
    
    add = instructions.get('add', [])
    if add:
        sections.append("### ➕ CONTENIDO NUEVO A AÑADIR (obligatorio incluir)")
        for item in add:
            sections.append(f"- {item}")
        sections.append("")
    
    tone_changes = instructions.get('tone_changes', '')
    if tone_changes and tone_changes.strip():
        sections.append("### 🎭 CAMBIOS DE TONO")
        sections.append(tone_changes.strip())
        sections.append("")
    
    structure_changes = instructions.get('structure_changes', '')
    if structure_changes and structure_changes.strip():
        sections.append("### 📐 CAMBIOS DE ESTRUCTURA")
        sections.append(structure_changes.strip())
        sections.append("")
    
    seo_focus = instructions.get('seo_focus', '')
    if seo_focus and seo_focus.strip():
        sections.append("### 🔍 ENFOQUE SEO ESPECÍFICO")
        sections.append(seo_focus.strip())
        sections.append("")
    
    additional_notes = instructions.get('additional_notes', '')
    if additional_notes and additional_notes.strip():
        sections.append("### 📝 NOTAS ADICIONALES")
        sections.append(additional_notes.strip())
        sections.append("")
    
    if not sections:
        return ""
    
    return "## 📋 INSTRUCCIONES DE REESCRITURA DEL USUARIO\n\n" + "\n".join(sections)


# ============================================================================
# FORMATEO DE ARTÍCULOS PARA FUSIÓN
# ============================================================================

def format_merge_articles_info(html_contents: List[Dict[str, Any]]) -> str:
    """Formatea información de múltiples artículos para fusión."""
    if not html_contents or len(html_contents) < 2:
        return ""
    
    sections = ["## 🔀 ARTÍCULOS A FUSIONAR\n"]
    sections.append(f"Total: {len(html_contents)} artículos")
    sections.append(f"Palabras totales: {sum(a.get('word_count', 0) for a in html_contents):,}\n")
    
    for i, article in enumerate(html_contents):
        priority = "🥇 PRINCIPAL" if i == 0 else f"🔗 Artículo {i + 1}"
        title = article.get('title', f'Artículo {i + 1}')
        url = article.get('url', 'Sin URL')
        word_count = article.get('word_count', 0)
        keep_notes = article.get('keep_notes', '')
        
        sections.append(f"### {priority}: {title}")
        sections.append(f"- **URL:** {url}")
        sections.append(f"- **Palabras:** {word_count:,}")
        
        if keep_notes:
            sections.append(f"- **⭐ CONSERVAR:** {keep_notes}")
        
        html_content = article.get('html', '')
        if html_content:
            text = _strip_html(html_content)
            preview = text[:500] + "..." if len(text) > 500 else text
            sections.append(f"- **Preview:** {preview}")
        
        sections.append("")
    
    sections.append("""
### 📋 INSTRUCCIONES DE FUSIÓN

1. **Estructura base**: Usa el artículo principal (🥇) como base estructural
2. **Contenido único**: Incorpora las secciones únicas de cada artículo secundario
3. **Sin duplicidades**: Elimina contenido repetido entre artículos
4. **Coherencia**: El resultado debe leerse como UN SOLO artículo coherente
5. **Conservar lo marcado**: Presta especial atención a las notas "⭐ CONSERVAR"
6. **Mejor de cada uno**: Combina lo mejor de cada artículo
""")
    
    return "\n".join(sections)


# ============================================================================
# FORMATEO DE DESAMBIGUACIÓN
# ============================================================================

def format_disambiguation_info(
    disambiguation_config: Dict[str, Any],
    html_contents: List[Dict[str, Any]]
) -> str:
    """Formatea información para desambiguación post/PLP."""
    if not disambiguation_config:
        return ""
    
    output_type = disambiguation_config.get('output_type', 'post')
    instructions = disambiguation_config.get('instructions', '')
    other_url = disambiguation_config.get('other_url', '')
    conflict_url = disambiguation_config.get('conflict_url', '')
    
    sections = ["## 🎯 DESAMBIGUACIÓN DE CONTENIDO\n"]
    
    if output_type == 'post':
        sections.append("### OBJETIVO: Crear contenido EDITORIAL (Post/Guía)")
        sections.append("""
El contenido debe tener **intención INFORMATIVA**:
- Enfoque: Educar, informar, ayudar a decidir
- Tono: Experto y consultivo
- Estructura: Guía, tutorial, comparativa
- Keywords: "cómo elegir", "qué es", "mejores", "diferencias"
- CTAs: Suaves, orientados a seguir leyendo
- NO incluir: Listados de productos con precios, CTAs de compra directa
""")
    else:
        sections.append("### OBJETIVO: Crear contenido TRANSACCIONAL (PLP/Categoría)")
        sections.append("""
El contenido debe tener **intención TRANSACCIONAL**:
- Enfoque: Vender, convertir, facilitar la compra
- Tono: Directo y orientado a la acción
- Estructura: Intro breve + destacados + filtros
- Keywords: "comprar", "precio", "oferta", "en stock"
- CTAs: Directos a producto o categoría
- NO incluir: Contenido extenso educativo
""")
    
    sections.append("")
    
    if conflict_url:
        sections.append(f"**URL conflictiva (a reescribir):** {conflict_url}")
    if other_url:
        sections.append(f"**URL que debe diferenciarse:** {other_url}")
        sections.append(f"⚠️ El nuevo contenido debe ser CLARAMENTE DIFERENTE")
    
    if instructions:
        sections.append("\n### 📋 INSTRUCCIONES DE DESAMBIGUACIÓN")
        sections.append(instructions)
    
    if html_contents:
        content = html_contents[0]
        sections.append("\n### 📄 CONTENIDO CONFLICTIVO ACTUAL")
        sections.append(f"- **Palabras:** {content.get('word_count', 0):,}")
        
        html = content.get('html', '')
        if html:
            text = _strip_html(html)
            preview = text[:800] + "..." if len(text) > 800 else text
            sections.append(f"\n**Preview:**\n{preview}")
    
    return "\n".join(sections)


# ============================================================================
# FORMATEO DE COMPETIDORES
# ============================================================================

def format_competitors_for_prompt(competitors: List[Dict]) -> str:
    """Formatea lista de competidores para el prompt."""
    if not competitors:
        return "(Sin datos de competidores)"
    
    sections = ["## 🏆 ANÁLISIS DE COMPETIDORES\n"]
    
    valid_competitors = [c for c in competitors if c.get('scrape_success', False)]
    
    if valid_competitors:
        word_counts = [c.get('word_count', 0) for c in valid_competitors]
        avg_words = sum(word_counts) / len(word_counts) if word_counts else 0
        
        sections.append(f"**Estadísticas:**")
        sections.append(f"- Competidores analizados: {len(valid_competitors)}")
        sections.append(f"- Promedio de palabras: {int(avg_words):,}")
        sections.append(f"- Rango: {min(word_counts):,} - {max(word_counts):,} palabras")
        sections.append("")
    
    for i, comp in enumerate(competitors[:MAX_COMPETITORS_ANALYZED], 1):
        if not comp.get('scrape_success', False):
            continue
        
        title = comp.get('title', 'Sin título')[:80]
        domain = comp.get('domain', 'desconocido')
        position = comp.get('ranking_position', comp.get('position', i))
        word_count = comp.get('word_count', 0)
        content = comp.get('content', '')
        
        sections.append(f"### #{position} - {domain}")
        sections.append(f"**Título:** {title}")
        sections.append(f"**Palabras:** {word_count:,}")
        
        if content:
            preview = content[:1500] + "..." if len(content) > 1500 else content
            sections.append(f"\n**Contenido:**\n{preview}")
        
        sections.append("")
    
    return "\n".join(sections)


def format_competitor_data_for_analysis(competitors: List[Dict]) -> str:
    """Alias para compatibilidad."""
    return format_competitors_for_prompt(competitors)


# ============================================================================
# FORMATEO DE ENLACES EDITORIALES (NUEVO v4.7.1)
# ============================================================================

def format_editorial_links_for_prompt(links: List[Dict[str, Any]]) -> str:
    """
    Formatea enlaces editoriales con su HTML contextual.
    - Post: html_content único
    - PLP: top_text + bottom_text
    """
    if not links:
        return ""
    
    sections = ["## 📝 ENLACES EDITORIALES A INCLUIR\n"]
    sections.append("""
Estos enlaces deben integrarse de forma **natural y contextual** en el contenido.
El HTML proporcionado te ayuda a entender el contexto del destino para crear
enlaces más relevantes y útiles.
""")
    
    for i, link in enumerate(links, 1):
        url = link.get('url', '')
        anchor = link.get('anchor', '')
        editorial_type = link.get('editorial_type', 'post')
        
        type_label = "📝 Post/Guía" if editorial_type == 'post' else "🛒 PLP/Categoría"
        
        sections.append(f"### {i}. {type_label}: [{anchor}]({url})")
        sections.append(f"- **Anchor sugerido:** {anchor}")
        sections.append(f"- **URL destino:** {url}")
        
        # Contenido según tipo
        if editorial_type == 'post':
            html_content = link.get('html_content', '')
            if html_content:
                text = _strip_html(html_content)
                preview = text[:600] + "..." if len(text) > 600 else text
                sections.append(f"\n**Contexto del Post destino:**\n{preview}")
                sections.append("")
                sections.append("💡 *Usa este contexto para crear un enlace que fluya naturalmente y aporte valor al lector.*")
        else:  # PLP
            top_text = link.get('top_text', '')
            bottom_text = link.get('bottom_text', '')
            
            if top_text:
                text = _strip_html(top_text)
                preview = text[:400] + "..." if len(text) > 400 else text
                sections.append(f"\n**Top text de la PLP:**\n{preview}")
            
            if bottom_text:
                text = _strip_html(bottom_text)
                preview = text[:400] + "..." if len(text) > 400 else text
                sections.append(f"\n**Bottom text de la PLP:**\n{preview}")
            
            if top_text or bottom_text:
                sections.append("")
                sections.append("💡 *Enlaza a esta PLP cuando hables de categorías de productos o cuando el usuario pueda querer explorar opciones.*")
        
        sections.append("")
    
    sections.append("""
### 📋 BUENAS PRÁCTICAS PARA ENLACES EDITORIALES

1. **Contextuales**: El enlace debe aparecer donde tenga sentido temático
2. **Naturales**: Debe leerse como parte del contenido, no como publicidad
3. **Útiles**: Aporta valor al lector, no solo SEO
4. **Distribuidos**: No agrupar todos los enlaces juntos
5. **Con el anchor correcto**: Usa el anchor sugerido o uno similar con keywords
""")
    
    return "\n".join(sections)


# ============================================================================
# FORMATEO DE ENLACES A PRODUCTOS (CON JSON)
# ============================================================================

def format_product_links_for_prompt(links: List[Dict[str, Any]]) -> str:
    """Formatea enlaces a productos con sus datos JSON."""
    if not links:
        return ""
    
    sections = ["## 🛒 ENLACES A PRODUCTOS A INCLUIR\n"]
    sections.append("Estos enlaces a productos deben integrarse donde sea relevante.\n")
    
    for i, link in enumerate(links, 1):
        url = link.get('url', '')
        anchor = link.get('anchor', '')
        prod_data = link.get('product_data')
        
        sections.append(f"### {i}. [{anchor}]({url})")
        sections.append(f"- **Anchor:** {anchor}")
        sections.append(f"- **URL:** {url}")
        
        if prod_data:
            title = prod_data.get('title', '')
            brand = prod_data.get('brand_name', '')
            family = prod_data.get('family_name', '')
            
            if title:
                sections.append(f"- **Producto:** {brand} {title}")
            if family:
                sections.append(f"- **Familia:** {family}")
            
            # Atributos clave
            attributes = prod_data.get('attributes', {})
            if attributes and isinstance(attributes, dict):
                key_attrs = list(attributes.items())[:5]
                if key_attrs:
                    specs = ", ".join(f"{k}: {v}" for k, v in key_attrs)
                    sections.append(f"- **Specs:** {specs}")
            
            # Reviews
            total_comments = prod_data.get('totalComments', 0)
            if total_comments:
                sections.append(f"- **Reviews:** {total_comments} opiniones")
            
            advantages = prod_data.get('advantages', [])
            if advantages:
                sections.append(f"- **Puntos fuertes:** {', '.join(advantages[:3])}")
        
        sections.append("")
    
    return "\n".join(sections)


# ============================================================================
# FORMATEO DE PRODUCTOS ALTERNATIVOS (NUEVO v4.7.1)
# ============================================================================

def format_alternative_products_for_prompt(products: List[Dict[str, Any]]) -> str:
    """
    Formatea productos alternativos con sus datos JSON.
    """
    if not products:
        return ""
    
    sections = ["## 🎯 PRODUCTOS ALTERNATIVOS A RECOMENDAR\n"]
    sections.append("""
Estos productos deben mencionarse como **alternativas** al producto principal
o como opciones adicionales para diferentes perfiles de usuario.
""")
    
    for i, product in enumerate(products, 1):
        url = product.get('url', '')
        anchor = product.get('anchor', '')
        prod_data = product.get('product_data')
        
        sections.append(f"### Alternativa {i}: [{anchor}]({url})")
        sections.append(f"- **URL:** {url}")
        
        if prod_data:
            title = prod_data.get('title', '')
            brand = prod_data.get('brand_name', '')
            family = prod_data.get('family_name', '')
            description = prod_data.get('description', '')
            
            if title:
                sections.append(f"- **Producto:** {brand} {title}")
            if family:
                sections.append(f"- **Familia:** {family}")
            
            # Atributos para comparar
            attributes = prod_data.get('attributes', {})
            if attributes and isinstance(attributes, dict):
                key_attrs = list(attributes.items())[:8]
                if key_attrs:
                    sections.append("- **Especificaciones:**")
                    for k, v in key_attrs:
                        sections.append(f"  - {k}: {v}")
            
            # Reviews
            total_comments = prod_data.get('totalComments', 0)
            advantages = prod_data.get('advantages', [])
            disadvantages = prod_data.get('disadvantages', [])
            
            if total_comments:
                sections.append(f"- **Reviews:** {total_comments} opiniones")
            
            if advantages:
                sections.append(f"- **✅ Ventajas:** {', '.join(advantages[:3])}")
            
            if disadvantages:
                sections.append(f"- **⚠️ Consideraciones:** {', '.join(disadvantages[:2])}")
            
            if description:
                desc_preview = description[:300] + "..." if len(description) > 300 else description
                sections.append(f"- **Descripción:** {desc_preview}")
        else:
            sections.append("- *(Sin datos JSON - mencionar de forma genérica)*")
        
        sections.append("")
    
    sections.append("""
### 📋 CÓMO INTEGRAR ALTERNATIVAS

1. **Por perfil**: "Si buscas más potencia, el [Alternativa 1] es ideal..."
2. **Por presupuesto**: "Para quien busque una opción más económica..."
3. **Por uso**: "Si tu enfoque es gaming competitivo, considera..."
4. **Comparativa**: Puedes crear una mini-tabla comparando specs clave
5. **Natural**: No forzar, solo donde tenga sentido
""")
    
    return "\n".join(sections)


# ============================================================================
# FORMATEO DE PRODUCTO PRINCIPAL
# ============================================================================

def format_main_product_for_prompt(main_product: Dict[str, Any]) -> str:
    """Formatea datos del producto principal."""
    if not main_product:
        return ""
    
    url = main_product.get('url', '')
    json_data = main_product.get('json_data')
    
    if not json_data and not url:
        return ""
    
    sections = ["## 📦 PRODUCTO PRINCIPAL\n"]
    
    if url:
        sections.append(f"**URL:** {url}")
    
    if json_data:
        title = json_data.get('title', '')
        brand = json_data.get('brand_name', '')
        family = json_data.get('family_name', '')
        description = json_data.get('description', '')
        
        if title:
            sections.append(f"**Producto:** {title}")
        if brand:
            sections.append(f"**Marca:** {brand}")
        if family:
            sections.append(f"**Familia:** {family}")
        
        # Atributos
        attributes = json_data.get('attributes', {})
        if attributes and isinstance(attributes, dict):
            sections.append("\n**Especificaciones técnicas:**")
            for key, value in list(attributes.items())[:15]:
                sections.append(f"- {key}: {value}")
        
        # Reviews
        total_comments = json_data.get('totalComments', 0)
        advantages = json_data.get('advantages', [])
        disadvantages = json_data.get('disadvantages', [])
        
        if total_comments:
            sections.append(f"\n**Reviews:** {total_comments} opiniones")
        
        if advantages:
            sections.append("\n**Ventajas destacadas por usuarios:**")
            for adv in advantages[:5]:
                sections.append(f"- ✅ {adv}")
        
        if disadvantages:
            sections.append("\n**Puntos a mejorar según usuarios:**")
            for dis in disadvantages[:3]:
                sections.append(f"- ⚠️ {dis}")
        
        if description:
            desc_preview = description[:500] + "..." if len(description) > 500 else description
            sections.append(f"\n**Descripción:**\n{desc_preview}")
    
    sections.append("""
### 📋 USO DEL PRODUCTO PRINCIPAL

1. **Es el protagonista**: Todo el contenido gira en torno a este producto
2. **Usa las specs**: Menciona especificaciones técnicas relevantes
3. **Incluye opiniones**: Referencia las ventajas/desventajas de usuarios
4. **Enlaza al producto**: Debe haber enlaces directos al PDP
""")
    
    return "\n".join(sections)


# ============================================================================
# UTILIDADES
# ============================================================================

def _strip_html(html: str) -> str:
    """Elimina tags HTML y retorna texto plano."""
    text = re.sub(r'<[^>]+>', ' ', html)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


# ============================================================================
# ETAPA 1: BORRADOR
# ============================================================================

def build_rewrite_prompt_stage1(
    keyword: str,
    competitor_analysis: str,
    config: Dict[str, Any],
) -> str:
    """
    Construye el prompt para la Etapa 1: Borrador.
    
    Incluye toda la información del usuario para generar contenido de calidad.
    """
    # Extraer configuración
    rewrite_mode = config.get('rewrite_mode', 'single')
    rewrite_instructions = config.get('rewrite_instructions', {})
    html_contents = config.get('html_contents', [])
    disambiguation = config.get('disambiguation')
    main_product = config.get('main_product')
    editorial_links = config.get('editorial_links', [])
    product_links = config.get('product_links', [])
    alternative_products = config.get('alternative_products', [])
    target_length = config.get('target_length', 1500)
    objetivo = config.get('objetivo', '')
    context = config.get('context', '')
    arquetipo_codigo = config.get('arquetipo_codigo', '')
    
    min_length = int(target_length * 0.95)
    max_length = int(target_length * 1.05)
    
    # Determinar título según modo
    if rewrite_mode == 'merge':
        mode_title = "FUSIÓN DE ARTÍCULOS"
        mode_description = "Vas a FUSIONAR múltiples artículos en UNO SOLO definitivo."
    elif rewrite_mode == 'disambiguate':
        output_type = disambiguation.get('output_type', 'post') if disambiguation else 'post'
        mode_title = f"DESAMBIGUACIÓN - Crear {'POST' if output_type == 'post' else 'PLP'}"
        mode_description = "Vas a crear contenido CLARAMENTE DIFERENCIADO del contenido conflictivo."
    else:
        mode_title = "REESCRITURA DE ARTÍCULO"
        mode_description = "Vas a MEJORAR un artículo existente siguiendo las instrucciones."
    
    sections = [f"""# TAREA: {mode_title} (ETAPA 1/3)

{mode_description}

## 🎯 INFORMACIÓN BÁSICA

**Keyword principal:** {keyword}
**Longitud objetivo:** {target_length} palabras (rango: {min_length}-{max_length})
**Objetivo:** {objetivo if objetivo else 'Crear contenido superior a la competencia'}
"""]
    
    if context:
        sections.append(f"\n**Contexto adicional:**\n{context}")
    
    if arquetipo_codigo:
        sections.append(f"\n**Arquetipo:** {arquetipo_codigo}")
    
    sections.append("")
    
    # Tono de marca
    sections.append(BRAND_TONE)
    
    # Instrucciones de reescritura
    instructions_text = format_rewrite_instructions(rewrite_instructions)
    if instructions_text:
        sections.append(instructions_text)
    
    # Información según modo
    if rewrite_mode == 'merge':
        merge_info = format_merge_articles_info(html_contents)
        if merge_info:
            sections.append(merge_info)
    elif rewrite_mode == 'disambiguate':
        disamb_info = format_disambiguation_info(disambiguation, html_contents)
        if disamb_info:
            sections.append(disamb_info)
    else:
        if html_contents:
            content = html_contents[0]
            sections.append("## 📄 ARTÍCULO ORIGINAL A REESCRIBIR\n")
            sections.append(f"**URL:** {content.get('url', 'N/A')}")
            sections.append(f"**Título:** {content.get('title', 'N/A')}")
            sections.append(f"**Palabras:** {content.get('word_count', 0):,}")
            
            html = content.get('html', '')
            if html:
                html_preview = html[:6000] + "\n\n[... truncado ...]" if len(html) > 6000 else html
                sections.append(f"\n**Contenido HTML:**\n```html\n{html_preview}\n```")
            sections.append("")
    
    # Producto principal
    product_info = format_main_product_for_prompt(main_product)
    if product_info:
        sections.append(product_info)
    
    # Productos alternativos
    alt_products_info = format_alternative_products_for_prompt(alternative_products)
    if alt_products_info:
        sections.append(alt_products_info)
    
    # Competidores
    sections.append(competitor_analysis)
    
    # Enlaces editoriales
    editorial_links_info = format_editorial_links_for_prompt(editorial_links)
    if editorial_links_info:
        sections.append(editorial_links_info)
    
    # Enlaces a productos
    product_links_info = format_product_links_for_prompt(product_links)
    if product_links_info:
        sections.append(product_links_info)
    
    # Estructura HTML
    sections.append(HTML_STRUCTURE_INSTRUCTIONS)
    
    # Instrucciones finales
    sections.append(f"""
# 📋 INSTRUCCIONES FINALES

## Prioridades de esta etapa:

1. **APLICAR INSTRUCCIONES DEL USUARIO** - Las instrucciones son OBLIGATORIAS
2. **USAR EL TONO DE MARCA** - PcComponentes: experto, cercano, nunca negativo
3. **SUPERAR A LA COMPETENCIA** - Mejor contenido que todos los competidores
4. **INCLUIR TODOS LOS ENLACES** - Cada enlace proporcionado debe aparecer
5. **INTEGRAR PRODUCTOS** - Usar datos de producto principal y alternativos
6. **LONGITUD CORRECTA** - Entre {min_length} y {max_length} palabras

## Checklist antes de generar:

- [ ] ¿Apliqué TODOS los puntos a mejorar?
- [ ] ¿Mantuve los puntos que funcionan bien?
- [ ] ¿Eliminé el contenido obsoleto/incorrecto?
- [ ] ¿Añadí el contenido nuevo solicitado?
- [ ] ¿El tono es el de PcComponentes?
- [ ] ¿Incluí todos los enlaces editoriales de forma contextual?
- [ ] ¿Incluí todos los enlaces a productos?
- [ ] ¿Mencioné los productos alternativos donde tiene sentido?
- [ ] ¿Es mejor que la competencia?

---

**GENERA AHORA EL BORRADOR HTML COMPLETO.**

Responde SOLO con el HTML (desde el primer <article> hasta el último </article>).
NO incluyas explicaciones ni texto fuera del HTML.
""")
    
    return "\n".join(sections)


# ============================================================================
# ETAPA 2: ANÁLISIS CRÍTICO
# ============================================================================

def build_rewrite_correction_prompt_stage2(
    draft_content: str,
    target_length: int,
    keyword: str,
    competitor_analysis: str,
    config: Dict[str, Any],
) -> str:
    """Construye el prompt para la Etapa 2: Análisis crítico."""
    
    rewrite_instructions = config.get('rewrite_instructions', {})
    rewrite_mode = config.get('rewrite_mode', 'single')
    objetivo = config.get('objetivo', '')
    editorial_links = config.get('editorial_links', [])
    product_links = config.get('product_links', [])
    alternative_products = config.get('alternative_products', [])
    
    min_length = int(target_length * 0.95)
    max_length = int(target_length * 1.05)
    
    # Checklist de instrucciones
    instruction_checklist = []
    
    improve = rewrite_instructions.get('improve', [])
    if improve:
        instruction_checklist.append("### Verificar MEJORAS aplicadas:")
        for item in improve:
            instruction_checklist.append(f"- [ ] {item}")
    
    maintain = rewrite_instructions.get('maintain', [])
    if maintain:
        instruction_checklist.append("\n### Verificar ELEMENTOS MANTENIDOS:")
        for item in maintain:
            instruction_checklist.append(f"- [ ] {item}")
    
    remove = rewrite_instructions.get('remove', [])
    if remove:
        instruction_checklist.append("\n### Verificar CONTENIDO ELIMINADO:")
        for item in remove:
            instruction_checklist.append(f"- [ ] {item} (debe estar ausente)")
    
    add = rewrite_instructions.get('add', [])
    if add:
        instruction_checklist.append("\n### Verificar CONTENIDO AÑADIDO:")
        for item in add:
            instruction_checklist.append(f"- [ ] {item}")
    
    instruction_checklist_text = "\n".join(instruction_checklist) if instruction_checklist else "(Sin instrucciones específicas)"
    
    # Checklist de enlaces
    links_checklist = ""
    if editorial_links or product_links or alternative_products:
        links_checklist = "\n### Verificar ENLACES incluidos:\n"
        
        for link in editorial_links:
            url = link.get('url', '')
            anchor = link.get('anchor', '')
            links_checklist += f"- [ ] Editorial: [{anchor}]({url})\n"
        
        for link in product_links:
            url = link.get('url', '')
            anchor = link.get('anchor', '')
            links_checklist += f"- [ ] Producto: [{anchor}]({url})\n"
        
        for prod in alternative_products:
            url = prod.get('url', '')
            anchor = prod.get('anchor', '')
            links_checklist += f"- [ ] Alternativo: [{anchor}]({url})\n"
    
    prompt = f"""# TAREA: ANÁLISIS CRÍTICO DEL BORRADOR (ETAPA 2/3)

Eres un editor SEO senior de PcComponentes. Analiza el borrador y genera un informe de correcciones.

## BORRADOR A ANALIZAR

```html
{draft_content[:12000]}
```

## KEYWORD OBJETIVO
"{keyword}"

## OBJETIVO DEL CONTENIDO
{objetivo if objetivo else 'Superar a la competencia'}

## MODO DE REESCRITURA
{rewrite_mode.upper()}

## CHECKLIST DE INSTRUCCIONES DEL USUARIO

{instruction_checklist_text}
{links_checklist}

## REFERENCIA COMPETITIVA

{competitor_analysis[:3000] if competitor_analysis else "(Sin referencia)"}

---

# ANÁLISIS REQUERIDO

Genera un JSON con esta estructura:

```json
{{
  "analisis_tecnico": {{
    "estructura_html_correcta": true/false,
    "errores_estructura": ["lista de errores"],
    "longitud_actual": número,
    "longitud_objetivo": {target_length},
    "dentro_de_rango": true/false,
    "ajuste_necesario": "ninguno/aumentar/reducir"
  }},
  
  "cumplimiento_instrucciones": {{
    "mejoras_aplicadas": ["lista"],
    "mejoras_pendientes": ["lista"],
    "elementos_mantenidos": ["lista"],
    "elementos_modificados_indebidamente": ["lista"],
    "contenido_eliminado": ["lista"],
    "contenido_no_eliminado": ["lista"],
    "contenido_añadido": ["lista"],
    "contenido_faltante": ["lista"]
  }},
  
  "cumplimiento_enlaces": {{
    "editoriales_incluidos": ["URLs"],
    "editoriales_faltantes": ["URLs"],
    "productos_incluidos": ["URLs"],
    "productos_faltantes": ["URLs"],
    "alternativos_mencionados": ["URLs"],
    "alternativos_faltantes": ["URLs"],
    "integracion_natural": true/false
  }},
  
  "tono_marca": {{
    "es_correcto": true/false,
    "problemas_detectados": ["lista"],
    "frases_a_corregir": ["lista"]
  }},
  
  "superioridad_competitiva": {{
    "es_superior": true/false,
    "gaps_cubiertos": ["lista"],
    "gaps_pendientes": ["lista"],
    "diferenciacion": "descripción"
  }},
  
  "correcciones_prioritarias": [
    {{
      "tipo": "tecnico/contenido/enlace/tono",
      "descripcion": "problema",
      "solucion": "cómo corregir",
      "prioridad": "alta/media/baja"
    }}
  ],
  
  "puntuacion_general": {{
    "tecnica": 0-100,
    "instrucciones": 0-100,
    "enlaces": 0-100,
    "tono": 0-100,
    "competitiva": 0-100,
    "total": 0-100
  }}
}}
```

---

Responde SOLO con el JSON puro.
"""
    
    return prompt


# ============================================================================
# ETAPA 3: VERSIÓN FINAL
# ============================================================================

def build_rewrite_final_prompt_stage3(
    draft_content: str,
    corrections_json: str,
    config: Dict[str, Any],
) -> str:
    """Construye el prompt para la Etapa 3: Versión final."""
    
    target_length = config.get('target_length', 1500)
    keyword = config.get('keyword', '')
    editorial_links = config.get('editorial_links', [])
    product_links = config.get('product_links', [])
    alternative_products = config.get('alternative_products', [])
    rewrite_instructions = config.get('rewrite_instructions', {})
    rewrite_mode = config.get('rewrite_mode', 'single')
    
    min_length = int(target_length * 0.95)
    max_length = int(target_length * 1.05)
    
    # Recordatorios críticos
    critical_reminders = []
    
    improve = rewrite_instructions.get('improve', [])
    if improve:
        critical_reminders.append("### ✨ MEJORAS OBLIGATORIAS:")
        for item in improve:
            critical_reminders.append(f"- {item}")
    
    add = rewrite_instructions.get('add', [])
    if add:
        critical_reminders.append("\n### ➕ CONTENIDO OBLIGATORIO:")
        for item in add:
            critical_reminders.append(f"- {item}")
    
    if editorial_links:
        critical_reminders.append("\n### 📝 ENLACES EDITORIALES OBLIGATORIOS:")
        for link in editorial_links:
            url = link.get('url', '')
            anchor = link.get('anchor', '')
            critical_reminders.append(f"- [{anchor}]({url})")
    
    if product_links:
        critical_reminders.append("\n### 🛒 ENLACES A PRODUCTOS OBLIGATORIOS:")
        for link in product_links:
            url = link.get('url', '')
            anchor = link.get('anchor', '')
            critical_reminders.append(f"- [{anchor}]({url})")
    
    if alternative_products:
        critical_reminders.append("\n### 🎯 PRODUCTOS ALTERNATIVOS A MENCIONAR:")
        for prod in alternative_products:
            url = prod.get('url', '')
            anchor = prod.get('anchor', '')
            critical_reminders.append(f"- [{anchor}]({url})")
    
    reminders_text = "\n".join(critical_reminders) if critical_reminders else ""
    
    prompt = f"""# TAREA: VERSIÓN FINAL CON CORRECCIONES (ETAPA 3/3)

Esta es la ETAPA FINAL. Genera la versión DEFINITIVA aplicando TODAS las correcciones.

## KEYWORD OBJETIVO
"{keyword}"

## MODO
{rewrite_mode.upper()}

## BORRADOR ORIGINAL (ETAPA 1)

```html
{draft_content[:10000]}
```

## ANÁLISIS Y CORRECCIONES (ETAPA 2)

```json
{corrections_json[:4000]}
```

{reminders_text}

{BRAND_TONE}

---

# INSTRUCCIONES CRÍTICAS

## Requisitos Técnicos:

1. **Estructura de 3 articles** exacta del CMS
2. **Título principal con <h2>** (NUNCA <h1>)
3. **Kicker con <span class="kicker">**
4. **Longitud entre {min_length} y {max_length} palabras**
5. **HTML puro** sin markdown
6. **Clases CSS correctas**

## Requisitos de Contenido:

7. **APLICAR todas las correcciones**
8. **INCLUIR todos los enlaces** (editoriales, productos, alternativos)
9. **TONO PcComponentes** - Experto, cercano, nunca negativo
10. **SUPERAR a la competencia**

---

**GENERA AHORA LA VERSIÓN FINAL.**

Responde SOLO con el HTML completo.
NO incluyas explicaciones.
"""
    
    return prompt


# ============================================================================
# SISTEMA
# ============================================================================

def build_system_prompt() -> str:
    """System prompt para los agentes."""
    return """Eres un experto redactor y editor SEO de PcComponentes, la tienda líder de tecnología en España.

Tu trabajo es crear contenido que:
1. Sea útil y valioso para los usuarios
2. Esté optimizado para SEO sin sobre-optimizar
3. Siga el tono de marca de PcComponentes
4. Cumpla con la estructura CMS requerida
5. APLIQUE todas las instrucciones del usuario

Tono de marca PcComponentes:
- Expertos sin ser pedantes
- Frikis sin vergüenza  
- Cercanos pero profesionales
- Tuteamos al lector
- Usamos analogías tech cuando aportan valor
- Hablamos claro, no vendemos humo
- SIEMPRE orientados a ayudar
- NUNCA desanimamos, siempre ofrecemos alternativas

Reglas críticas:
- Las instrucciones del usuario son OBLIGATORIAS
- Todos los enlaces proporcionados DEBEN aparecer
- El contenido debe ser SUPERIOR a la competencia
- La estructura HTML del CMS es INNEGOCIABLE
"""


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    '__version__',
    'HTML_STRUCTURE_INSTRUCTIONS',
    'BRAND_TONE',
    'DEFAULT_LENGTH_TOLERANCE',
    'MAX_COMPETITORS_ANALYZED',
    # Formateo
    'format_rewrite_instructions',
    'format_merge_articles_info',
    'format_disambiguation_info',
    'format_competitors_for_prompt',
    'format_competitor_data_for_analysis',
    'format_editorial_links_for_prompt',
    'format_product_links_for_prompt',
    'format_alternative_products_for_prompt',
    'format_main_product_for_prompt',
    # Prompts
    'build_rewrite_prompt_stage1',
    'build_rewrite_correction_prompt_stage2',
    'build_rewrite_final_prompt_stage3',
    'build_system_prompt',
]
