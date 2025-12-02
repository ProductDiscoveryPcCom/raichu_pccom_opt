# -*- coding: utf-8 -*-
"""
Rewrite Prompts - PcComponentes Content Generator
Versión 4.7.0

Prompts para reescritura de contenido basada en análisis competitivo.

CAMBIOS v4.7.0:
- NUEVO: Soporte para instrucciones de reescritura (mejorar, mantener, eliminar, añadir)
- NUEVO: Modo FUSIÓN de artículos (canibalizaciones)
- NUEVO: Modo DESAMBIGUACIÓN (post vs PLP)
- NUEVO: Instrucciones de tono, estructura y SEO
- Integración completa con ui/rewrite.py v4.7.0

Flujo de 3 etapas:
1. Borrador basado en análisis de competidores + instrucciones del usuario
2. Análisis y correcciones
3. Versión final

Autor: PcComponentes - Product Discovery & Content
"""

from typing import Dict, List, Optional, Any
import json

__version__ = "4.7.0"

# ============================================================================
# CONSTANTES
# ============================================================================

DEFAULT_LENGTH_TOLERANCE = 0.05
MAX_COMPETITORS_ANALYZED = 5
MAX_COMPETITOR_CONTENT_CHARS = 8000
MIN_VALID_CONTENT_CHARS = 200

# Estructura HTML del CMS de PcComponentes
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
            <!-- más items -->
        </ul>
    </nav>
    
    <!-- Secciones con H3 -->
    <section id="seccion1">
        <h3>Título de Sección</h3>
        <p>Contenido...</p>
    </section>
    
    <!-- FAQs si aplica -->
    <section class="faqs">
        <h3>Preguntas frecuentes</h3>
        <div class="faq-item">
            <h4 class="faq-question">¿Pregunta?</h4>
            <p class="faq-answer">Respuesta...</p>
        </div>
    </section>
    
    <!-- Veredicto final -->
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


# ============================================================================
# FORMATEO DE INSTRUCCIONES DE REESCRITURA
# ============================================================================

def format_rewrite_instructions(instructions: Dict[str, Any]) -> str:
    """
    Formatea las instrucciones de reescritura proporcionadas por el usuario.
    
    Args:
        instructions: Dict con keys: improve, maintain, remove, add, 
                     tone_changes, structure_changes, seo_focus, additional_notes
    
    Returns:
        Texto formateado para incluir en el prompt
    """
    if not instructions:
        return ""
    
    sections = []
    
    # Qué MEJORAR
    improve = instructions.get('improve', [])
    if improve:
        sections.append("### ✨ ASPECTOS A MEJORAR (obligatorio aplicar)")
        for item in improve:
            sections.append(f"- {item}")
        sections.append("")
    
    # Qué MANTENER
    maintain = instructions.get('maintain', [])
    if maintain:
        sections.append("### ✅ ASPECTOS A MANTENER (no modificar)")
        for item in maintain:
            sections.append(f"- {item}")
        sections.append("")
    
    # Qué ELIMINAR
    remove = instructions.get('remove', [])
    if remove:
        sections.append("### 🗑️ CONTENIDO A ELIMINAR (obligatorio quitar)")
        for item in remove:
            sections.append(f"- {item}")
        sections.append("")
    
    # Qué AÑADIR
    add = instructions.get('add', [])
    if add:
        sections.append("### ➕ CONTENIDO NUEVO A AÑADIR (obligatorio incluir)")
        for item in add:
            sections.append(f"- {item}")
        sections.append("")
    
    # Cambios de TONO
    tone_changes = instructions.get('tone_changes', '')
    if tone_changes and tone_changes.strip():
        sections.append("### 🎭 CAMBIOS DE TONO")
        sections.append(tone_changes.strip())
        sections.append("")
    
    # Cambios de ESTRUCTURA
    structure_changes = instructions.get('structure_changes', '')
    if structure_changes and structure_changes.strip():
        sections.append("### 📐 CAMBIOS DE ESTRUCTURA")
        sections.append(structure_changes.strip())
        sections.append("")
    
    # Enfoque SEO
    seo_focus = instructions.get('seo_focus', '')
    if seo_focus and seo_focus.strip():
        sections.append("### 🔍 ENFOQUE SEO ESPECÍFICO")
        sections.append(seo_focus.strip())
        sections.append("")
    
    # Notas adicionales
    additional_notes = instructions.get('additional_notes', '')
    if additional_notes and additional_notes.strip():
        sections.append("### 📝 NOTAS ADICIONALES")
        sections.append(additional_notes.strip())
        sections.append("")
    
    if not sections:
        return ""
    
    return "## 📋 INSTRUCCIONES DE REESCRITURA DEL USUARIO\n\n" + "\n".join(sections)


def format_merge_articles_info(html_contents: List[Dict[str, Any]]) -> str:
    """
    Formatea la información de múltiples artículos para fusión.
    
    Args:
        html_contents: Lista de dicts con url, html, title, word_count, keep_notes
    
    Returns:
        Texto formateado para el prompt de fusión
    """
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
        
        # Incluir extracto del contenido
        html_content = article.get('html', '')
        if html_content:
            # Extraer texto limpio (primeros 500 chars)
            import re
            text = re.sub(r'<[^>]+>', ' ', html_content)
            text = re.sub(r'\s+', ' ', text).strip()
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
6. **Mejor de cada uno**: Combina lo mejor de cada artículo, no solo el texto
""")
    
    return "\n".join(sections)


def format_disambiguation_info(
    disambiguation_config: Dict[str, Any],
    html_contents: List[Dict[str, Any]]
) -> str:
    """
    Formatea la información para desambiguación post/PLP.
    
    Args:
        disambiguation_config: Config con output_type, instructions, other_url
        html_contents: Lista con el contenido conflictivo
    
    Returns:
        Texto formateado para el prompt de desambiguación
    """
    if not disambiguation_config:
        return ""
    
    output_type = disambiguation_config.get('output_type', 'post')
    instructions = disambiguation_config.get('instructions', '')
    other_url = disambiguation_config.get('other_url', '')
    conflict_url = disambiguation_config.get('conflict_url', '')
    
    sections = ["## 🎯 DESAMBIGUACIÓN DE CONTENIDO\n"]
    
    # Tipo de output
    if output_type == 'post':
        sections.append("### OBJETIVO: Crear contenido EDITORIAL (Post/Guía)")
        sections.append("""
El contenido debe tener **intención INFORMATIVA**:
- Enfoque: Educar, informar, ayudar a decidir
- Tono: Experto y consultivo
- Estructura: Guía, tutorial, comparativa
- Keywords: "cómo elegir", "qué es", "mejores", "diferencias"
- CTAs: Suaves, orientados a seguir leyendo o explorar opciones
- NO incluir: Listados de productos con precios, CTAs de compra directa
""")
    else:  # plp
        sections.append("### OBJETIVO: Crear contenido TRANSACCIONAL (PLP/Categoría)")
        sections.append("""
El contenido debe tener **intención TRANSACCIONAL**:
- Enfoque: Vender, convertir, facilitar la compra
- Tono: Directo y orientado a la acción
- Estructura: Intro breve + destacados + filtros/categorías
- Keywords: "comprar", "precio", "oferta", "en stock"
- CTAs: Directos a producto o categoría
- NO incluir: Contenido extenso educativo, comparativas detalladas
""")
    
    sections.append("")
    
    # URLs de referencia
    if conflict_url:
        sections.append(f"**URL conflictiva (a reescribir):** {conflict_url}")
    if other_url:
        sections.append(f"**URL que debe diferenciarse:** {other_url}")
        sections.append(f"⚠️ El nuevo contenido debe ser CLARAMENTE DIFERENTE de {other_url}")
    
    sections.append("")
    
    # Instrucciones específicas del usuario
    if instructions:
        sections.append("### 📋 INSTRUCCIONES DE DESAMBIGUACIÓN")
        sections.append(instructions)
        sections.append("")
    
    # Contenido conflictivo
    if html_contents:
        content = html_contents[0]
        sections.append("### 📄 CONTENIDO CONFLICTIVO ACTUAL")
        sections.append(f"- **Palabras:** {content.get('word_count', 0):,}")
        
        html_content = content.get('html', '')
        if html_content:
            import re
            text = re.sub(r'<[^>]+>', ' ', html_content)
            text = re.sub(r'\s+', ' ', text).strip()
            preview = text[:800] + "..." if len(text) > 800 else text
            sections.append(f"\n**Preview del contenido actual:**\n{preview}")
    
    return "\n".join(sections)


# ============================================================================
# FORMATEO DE COMPETIDORES
# ============================================================================

def format_competitors_for_prompt(competitors: List[Dict]) -> str:
    """
    Formatea lista de competidores para incluir en prompt.
    
    Args:
        competitors: Lista de dicts con datos de competidores
        
    Returns:
        Texto formateado con análisis de competidores
    """
    if not competitors:
        return "(Sin datos de competidores)"
    
    sections = ["## 🏆 ANÁLISIS DE COMPETIDORES\n"]
    
    # Estadísticas generales
    valid_competitors = [c for c in competitors if c.get('scrape_success', False)]
    
    if valid_competitors:
        word_counts = [c.get('word_count', 0) for c in valid_competitors]
        avg_words = sum(word_counts) / len(word_counts) if word_counts else 0
        max_words = max(word_counts) if word_counts else 0
        min_words = min(word_counts) if word_counts else 0
        
        sections.append(f"**Estadísticas:**")
        sections.append(f"- Competidores analizados: {len(valid_competitors)}")
        sections.append(f"- Promedio de palabras: {int(avg_words):,}")
        sections.append(f"- Rango: {min_words:,} - {max_words:,} palabras")
        sections.append("")
    
    # Detalle de cada competidor
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
        
        # Extracto del contenido
        if content:
            preview = content[:1500] + "..." if len(content) > 1500 else content
            sections.append(f"\n**Contenido:**\n{preview}")
        
        sections.append("")
    
    return "\n".join(sections)


def format_competitor_data_for_analysis(competitors: List[Dict]) -> str:
    """Alias para compatibilidad con código existente."""
    return format_competitors_for_prompt(competitors)


# ============================================================================
# FORMATEO DE ENLACES
# ============================================================================

def format_links_for_prompt(links: List[Dict[str, Any]]) -> str:
    """
    Formatea enlaces para incluir en el prompt.
    
    Args:
        links: Lista de dicts con url, anchor, type, product_data
        
    Returns:
        Texto formateado con instrucciones de enlaces
    """
    if not links:
        return ""
    
    sections = ["## 🔗 ENLACES A INCLUIR\n"]
    sections.append("IMPORTANTE: Todos estos enlaces DEBEN aparecer en el contenido final.\n")
    
    editorial_links = [l for l in links if l.get('type') == 'editorial']
    product_links = [l for l in links if l.get('type') == 'product']
    
    # Enlaces editoriales
    if editorial_links:
        sections.append("### 📝 Enlaces a Contenido Editorial")
        for link in editorial_links:
            url = link.get('url', '')
            anchor = link.get('anchor', link.get('text', ''))
            has_data = bool(link.get('product_data'))
            
            sections.append(f"- **[{anchor}]({url})**")
            if has_data:
                prod_data = link['product_data']
                title = prod_data.get('title', '')
                brand = prod_data.get('brand_name', '')
                if title:
                    sections.append(f"  - Producto relacionado: {brand} {title}")
        sections.append("")
    
    # Enlaces a productos
    if product_links:
        sections.append("### 🛒 Enlaces a Productos")
        for link in product_links:
            url = link.get('url', '')
            anchor = link.get('anchor', link.get('text', ''))
            prod_data = link.get('product_data')
            
            sections.append(f"- **[{anchor}]({url})**")
            
            if prod_data:
                title = prod_data.get('title', '')
                brand = prod_data.get('brand_name', '')
                family = prod_data.get('family_name', '')
                
                if title:
                    sections.append(f"  - Producto: {brand} {title}")
                if family:
                    sections.append(f"  - Familia: {family}")
                
                # Atributos clave
                attributes = prod_data.get('attributes', {})
                if attributes and isinstance(attributes, dict):
                    key_attrs = list(attributes.items())[:5]
                    if key_attrs:
                        sections.append(f"  - Specs: " + ", ".join(f"{k}: {v}" for k, v in key_attrs))
        sections.append("")
    
    sections.append("""
### 📋 INSTRUCCIONES DE ENLACES

1. **Integración natural**: Los enlaces deben fluir con el texto, no parecer forzados
2. **Contexto relevante**: Cada enlace debe aparecer donde tenga sentido temático
3. **Anchor text**: Usar el anchor proporcionado o uno que incluya las keywords
4. **Datos de producto**: Si hay datos de producto, úsalos para contextualizar
5. **No agrupar**: Distribuir enlaces a lo largo del contenido, no todos juntos
""")
    
    return "\n".join(sections)


# ============================================================================
# FORMATEO DE PRODUCTO PRINCIPAL
# ============================================================================

def format_main_product_for_prompt(main_product: Dict[str, Any]) -> str:
    """
    Formatea datos del producto principal para el prompt.
    
    Args:
        main_product: Dict con url y json_data del producto
        
    Returns:
        Texto formateado con información del producto
    """
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
        
        # Descripción
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
# ETAPA 1: BORRADOR CON ANÁLISIS COMPETITIVO
# ============================================================================

def build_rewrite_prompt_stage1(
    keyword: str,
    competitor_analysis: str,
    config: Dict[str, Any],
) -> str:
    """
    Construye el prompt para la Etapa 1: Borrador basado en análisis competitivo
    e instrucciones del usuario.
    
    Args:
        keyword: Keyword principal
        competitor_analysis: Análisis formateado de competidores
        config: Configuración completa con:
            - rewrite_mode: single/merge/disambiguate
            - rewrite_instructions: Dict con instrucciones del usuario
            - html_contents: Lista de artículos a reescribir/fusionar
            - disambiguation: Config de desambiguación
            - main_product: Producto principal
            - links: Enlaces a incluir
            - target_length: Longitud objetivo
            - objetivo: Objetivo del contenido
            - context: Contexto adicional
            - arquetipo_codigo: Código del arquetipo
            
    Returns:
        Prompt completo para la etapa 1
    """
    # Extraer configuración
    rewrite_mode = config.get('rewrite_mode', 'single')
    rewrite_instructions = config.get('rewrite_instructions', {})
    html_contents = config.get('html_contents', [])
    disambiguation = config.get('disambiguation')
    main_product = config.get('main_product')
    links = config.get('links', [])
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
    
    # Construir secciones del prompt
    sections = [f"""# TAREA: {mode_title} (ETAPA 1/3)

{mode_description}

## 🎯 INFORMACIÓN BÁSICA

**Keyword principal:** {keyword}
**Longitud objetivo:** {target_length} palabras (rango: {min_length}-{max_length})
**Objetivo:** {objetivo if objetivo else 'Crear contenido superior a la competencia'}
"""]
    
    # Contexto adicional
    if context:
        sections.append(f"\n**Contexto adicional:**\n{context}")
    
    # Arquetipo
    if arquetipo_codigo:
        sections.append(f"\n**Arquetipo:** {arquetipo_codigo}")
    
    sections.append("")
    
    # Instrucciones de reescritura del usuario (CRÍTICO)
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
        # Modo single - incluir HTML original si existe
        if html_contents:
            content = html_contents[0]
            sections.append("## 📄 ARTÍCULO ORIGINAL A REESCRIBIR\n")
            sections.append(f"**URL:** {content.get('url', 'N/A')}")
            sections.append(f"**Título:** {content.get('title', 'N/A')}")
            sections.append(f"**Palabras:** {content.get('word_count', 0):,}")
            
            html = content.get('html', '')
            if html:
                # Limitar longitud del HTML
                html_preview = html[:6000] + "\n\n[... contenido truncado ...]" if len(html) > 6000 else html
                sections.append(f"\n**Contenido HTML:**\n```html\n{html_preview}\n```")
            sections.append("")
    
    # Producto principal
    product_info = format_main_product_for_prompt(main_product)
    if product_info:
        sections.append(product_info)
    
    # Análisis de competidores
    sections.append(competitor_analysis)
    
    # Enlaces
    links_info = format_links_for_prompt(links)
    if links_info:
        sections.append(links_info)
    
    # Estructura HTML
    sections.append(HTML_STRUCTURE_INSTRUCTIONS)
    
    # Instrucciones finales
    sections.append(f"""
# 📋 INSTRUCCIONES FINALES

## Prioridades de esta etapa:

1. **APLICAR INSTRUCCIONES DEL USUARIO** - Las instrucciones de mejorar/mantener/eliminar/añadir son OBLIGATORIAS
2. **SUPERAR A LA COMPETENCIA** - El contenido debe ser mejor que todos los competidores analizados
3. **INCLUIR TODOS LOS ENLACES** - Cada enlace proporcionado debe aparecer
4. **USAR DATOS DE PRODUCTO** - Si hay producto principal o datos de productos, integrarlos
5. **LONGITUD CORRECTA** - Entre {min_length} y {max_length} palabras

## Checklist antes de generar:

- [ ] ¿Apliqué TODOS los puntos a mejorar?
- [ ] ¿Mantuve los puntos que funcionan bien?
- [ ] ¿Eliminé el contenido obsoleto/incorrecto?
- [ ] ¿Añadí el contenido nuevo solicitado?
- [ ] ¿Ajusté el tono según las instrucciones?
- [ ] ¿La estructura sigue las indicaciones?
- [ ] ¿Incluí todos los enlaces?
- [ ] ¿Es mejor que la competencia?

---

**GENERA AHORA EL BORRADOR HTML COMPLETO.**

Responde SOLO con el HTML (desde el primer <article> hasta el último </article>).
NO incluyas explicaciones ni texto fuera del HTML.
""")
    
    return "\n".join(sections)


# ============================================================================
# ETAPA 2: ANÁLISIS CRÍTICO DEL BORRADOR
# ============================================================================

def build_rewrite_correction_prompt_stage2(
    draft_content: str,
    target_length: int,
    keyword: str,
    competitor_analysis: str,
    config: Dict[str, Any],
) -> str:
    """
    Construye el prompt para la Etapa 2: Análisis crítico del borrador.
    
    Args:
        draft_content: HTML del borrador de Etapa 1
        target_length: Longitud objetivo en palabras
        keyword: Keyword principal
        competitor_analysis: Análisis de competidores
        config: Configuración completa
        
    Returns:
        Prompt para análisis crítico
    """
    rewrite_instructions = config.get('rewrite_instructions', {})
    rewrite_mode = config.get('rewrite_mode', 'single')
    objetivo = config.get('objetivo', '')
    links = config.get('links', [])
    
    min_length = int(target_length * 0.95)
    max_length = int(target_length * 1.05)
    
    # Formatear checklist de instrucciones
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
    if links:
        links_checklist = "\n### Verificar ENLACES incluidos:\n"
        for link in links:
            url = link.get('url', '')
            anchor = link.get('anchor', link.get('text', ''))
            links_checklist += f"- [ ] [{anchor}]({url})\n"
    
    prompt = f"""# TAREA: ANÁLISIS CRÍTICO DEL BORRADOR (ETAPA 2/3)

Eres un editor SEO senior. Analiza el borrador y genera un informe de correcciones.

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

Genera un JSON con la siguiente estructura:

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
    "mejoras_aplicadas": ["lista de mejoras que SÍ se aplicaron"],
    "mejoras_pendientes": ["lista de mejoras que NO se aplicaron"],
    "elementos_mantenidos": ["elementos que se mantuvieron correctamente"],
    "elementos_modificados_indebidamente": ["elementos que debían mantenerse pero se cambiaron"],
    "contenido_eliminado": ["contenido que se eliminó correctamente"],
    "contenido_no_eliminado": ["contenido que debía eliminarse pero permanece"],
    "contenido_añadido": ["contenido nuevo que se añadió"],
    "contenido_faltante": ["contenido que debía añadirse pero falta"]
  }},
  
  "cumplimiento_enlaces": {{
    "enlaces_incluidos": ["URLs que sí aparecen"],
    "enlaces_faltantes": ["URLs que NO aparecen"],
    "integracion_natural": true/false,
    "notas_enlaces": "observaciones sobre integración"
  }},
  
  "superioridad_competitiva": {{
    "es_superior": true/false,
    "gaps_cubiertos": ["gaps de competidores que cubrimos"],
    "gaps_pendientes": ["gaps que aún no cubrimos"],
    "diferenciacion": "descripción de qué nos diferencia",
    "areas_mejora": ["áreas donde podemos mejorar más"]
  }},
  
  "correcciones_prioritarias": [
    {{
      "tipo": "tecnico/contenido/seo/enlace",
      "descripcion": "descripción del problema",
      "solucion": "cómo corregirlo",
      "prioridad": "alta/media/baja"
    }}
  ],
  
  "puntuacion_general": {{
    "tecnica": 0-100,
    "cumplimiento_instrucciones": 0-100,
    "superioridad_competitiva": 0-100,
    "total": 0-100
  }}
}}
```

---

Responde SOLO con el JSON (sin bloques de código markdown, solo el JSON puro).
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
    """
    Construye el prompt para la Etapa 3: Versión final con correcciones.
    
    Args:
        draft_content: HTML del borrador
        corrections_json: JSON con análisis y correcciones de Etapa 2
        config: Configuración completa
        
    Returns:
        Prompt para versión final
    """
    target_length = config.get('target_length', 1500)
    keyword = config.get('keyword', '')
    links = config.get('links', [])
    rewrite_instructions = config.get('rewrite_instructions', {})
    rewrite_mode = config.get('rewrite_mode', 'single')
    
    min_length = int(target_length * 0.95)
    max_length = int(target_length * 1.05)
    
    # Recordatorio de instrucciones críticas
    critical_reminders = []
    
    # Mejoras pendientes
    improve = rewrite_instructions.get('improve', [])
    if improve:
        critical_reminders.append("### ✨ MEJORAS QUE DEBEN ESTAR APLICADAS:")
        for item in improve:
            critical_reminders.append(f"- {item}")
    
    # Contenido a añadir
    add = rewrite_instructions.get('add', [])
    if add:
        critical_reminders.append("\n### ➕ CONTENIDO QUE DEBE ESTAR PRESENTE:")
        for item in add:
            critical_reminders.append(f"- {item}")
    
    # Enlaces
    if links:
        critical_reminders.append("\n### 🔗 ENLACES OBLIGATORIOS:")
        for link in links:
            url = link.get('url', '')
            anchor = link.get('anchor', link.get('text', ''))
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

---

# INSTRUCCIONES CRÍTICAS PARA LA VERSIÓN FINAL

## Requisitos Técnicos (OBLIGATORIOS):

1. **Estructura de 3 articles** exacta del CMS
2. **Título principal con <h2>** (NUNCA <h1>)
3. **Kicker con <span class="kicker">** (NUNCA <div>)
4. **Longitud entre {min_length} y {max_length} palabras**
5. **HTML puro** sin restos de markdown
6. **Clases CSS correctas** sin estilos inline

## Requisitos de Contenido (OBLIGATORIOS):

7. **APLICAR todas las correcciones** del análisis
8. **INCLUIR todos los enlaces** proporcionados
9. **MANTENER lo que funciona** del borrador
10. **MEJORAR las áreas identificadas**
11. **SUPERAR a la competencia** en calidad y completitud

## Verificación Final:

Antes de generar, verifica:
- [ ] ¿Todas las correcciones técnicas aplicadas?
- [ ] ¿Todas las correcciones de contenido aplicadas?
- [ ] ¿Todos los enlaces incluidos?
- [ ] ¿Longitud dentro del rango?
- [ ] ¿Estructura HTML correcta?
- [ ] ¿Superior a la competencia?

---

**GENERA AHORA LA VERSIÓN FINAL.**

Responde SOLO con el HTML completo (desde el primer <article> hasta el último </article>).
NO incluyas explicaciones ni texto fuera del HTML.
"""
    
    return prompt


# ============================================================================
# FUNCIONES AUXILIARES
# ============================================================================

def extract_gaps_from_analysis(analysis_json: str) -> List[str]:
    """Extrae gaps pendientes del JSON de análisis."""
    try:
        analysis = json.loads(analysis_json)
        gaps = analysis.get('superioridad_competitiva', {}).get('gaps_pendientes', [])
        return gaps if isinstance(gaps, list) else []
    except:
        return []


def validate_competitor_data(competitors: List[Dict]) -> tuple[bool, str]:
    """
    Valida que los datos de competidores sean válidos.
    
    Returns:
        Tuple (is_valid, error_message)
    """
    if not competitors:
        return False, "No hay datos de competidores"
    
    valid_count = sum(1 for c in competitors if c.get('scrape_success', False))
    
    if valid_count == 0:
        return False, "Ningún competidor fue scrapeado exitosamente"
    
    return True, f"{valid_count} competidores válidos"


def get_competitor_summary(competitors: List[Dict]) -> Dict[str, Any]:
    """Genera resumen estadístico de competidores."""
    valid = [c for c in competitors if c.get('scrape_success', False)]
    
    if not valid:
        return {
            'total': len(competitors),
            'valid': 0,
            'avg_words': 0,
            'max_words': 0,
            'min_words': 0,
            'domains': []
        }
    
    word_counts = [c.get('word_count', 0) for c in valid]
    
    return {
        'total': len(competitors),
        'valid': len(valid),
        'avg_words': int(sum(word_counts) / len(word_counts)),
        'max_words': max(word_counts),
        'min_words': min(word_counts),
        'domains': [c.get('domain', '') for c in valid]
    }


# ============================================================================
# SISTEMA DE PROMPTS
# ============================================================================

def build_system_prompt() -> str:
    """Construye el system prompt para los agentes de reescritura."""
    return """Eres un experto redactor y editor SEO de PcComponentes, la tienda líder de tecnología en España.

Tu trabajo es crear y mejorar contenido que:
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
- SIEMPRE orientados a ayudar al usuario a encontrar el producto adecuado
- NUNCA desanimamos la compra, siempre ofrecemos alternativas

Reglas críticas:
- Las instrucciones del usuario (mejorar/mantener/eliminar/añadir) son OBLIGATORIAS
- Todos los enlaces proporcionados DEBEN aparecer en el contenido
- El contenido debe ser SUPERIOR a la competencia
- La estructura HTML del CMS es INNEGOCIABLE
"""


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    '__version__',
    'HTML_STRUCTURE_INSTRUCTIONS',
    'DEFAULT_LENGTH_TOLERANCE',
    'MAX_COMPETITORS_ANALYZED',
    'MAX_COMPETITOR_CONTENT_CHARS',
    'MIN_VALID_CONTENT_CHARS',
    # Formateo
    'format_rewrite_instructions',
    'format_merge_articles_info',
    'format_disambiguation_info',
    'format_competitors_for_prompt',
    'format_competitor_data_for_analysis',
    'format_links_for_prompt',
    'format_main_product_for_prompt',
    # Prompts de etapas
    'build_rewrite_prompt_stage1',
    'build_rewrite_correction_prompt_stage2',
    'build_rewrite_final_prompt_stage3',
    'build_system_prompt',
    # Utilidades
    'extract_gaps_from_analysis',
    'validate_competitor_data',
    'get_competitor_summary',
]
