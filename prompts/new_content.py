# -*- coding: utf-8 -*-
"""
New Content Prompts - PcComponentes Content Generator
Versión 4.9.2

Prompts para generación de contenido nuevo en 3 etapas.

CAMBIOS v4.9.2:
- FIX: Callout-bf con padding reducido, sin espacio extra abajo
- FIX: Responsive en callouts para móvil
- FIX: Solo emojis permitidos en contenido: ⚡ 💡 ✅
- FIX: Templates sin emojis no soportados por CMS

CAMBIOS v4.9.1:
- FIX: Tablas con table-layout:fixed para alinear columnas correctamente
- FIX: Más espaciado entre headings y cajas (margin-bottom en h2/h3)
- FIX: Mayor padding interno en grid-item y product-module
- FIX: Enlaces en fondos oscuros ahora son visibles (dorado en verdict-box, blanco en callout-bf)
- Nueva variable CSS --space-xl:32px para espaciados mayores

CAMBIOS v4.9.0:
- Fusión de pdp_data (n8n) + pdp_json_data (JSON subido)
- Procesamiento de product_data en enlaces PDP
- Soporte completo para alternative_product.json_data
- Implementación de visual_elements (TOC, tablas, callouts, etc.)
- Nuevo parámetro pdp_json_data en build_new_content_prompt_stage1

CARACTERÍSTICAS:
- Funciona igual de bien CON o SIN datos de producto
- CON datos: usa ventajas/desventajas/opiniones para contenido auténtico
- SIN datos: instrucciones alternativas basadas en conocimiento general
- Tono de marca PcComponentes integrado (desde config/brand.py)
- Instrucciones anti-IA para evitar patrones artificiales

CAMPOS DE PRODUCTO SOPORTADOS (del Dict pdp_data o pdp_json_data):
| Campo              | Tipo         | Uso en Prompt                         |
|--------------------|--------------|---------------------------------------|
| title              | str          | Nombre del producto                   |
| brand_name         | str          | Marca                                 |
| family_name        | str          | Categoría                             |
| attributes         | Dict         | Especificaciones técnicas             |
| total_comments     | int          | Credibilidad (N valoraciones)         |
| advantages_list    | List[str]    | Ventajas procesadas → argumentar      |
| disadvantages_list | List[str]    | Desventajas → honestidad              |
| top_comments       | List[str]    | Opiniones → lenguaje natural          |
| has_user_feedback  | bool         | Flag si hay feedback de usuarios      |

Autor: PcComponentes - Product Discovery & Content
"""

from typing import Dict, List, Optional, Any

__version__ = "4.9.2"

# Importar constantes de tono desde config.brand (existente)
try:
    from config.brand import get_tone_instructions, get_system_prompt_base
except ImportError:
    try:
        from brand import get_tone_instructions, get_system_prompt_base
    except ImportError:
        # Fallback inline si no existen las funciones
        def get_tone_instructions(has_product_data: bool = False) -> str:
            return ""
        def get_system_prompt_base() -> str:
            return "Eres un redactor SEO experto de PcComponentes."


# ============================================================================
# CSS MINIFICADO v4.9.2
# Correcciones:
# - Tablas: table-layout:fixed para alinear columnas correctamente
# - Espaciado: más margen entre headings y cajas, padding interno aumentado
# - Enlaces: color claro en fondos oscuros (verdict-box, callout-bf)
# - Callouts: padding ajustado, p:last-child sin margin, responsive
# ============================================================================

CSS_INLINE_MINIFIED = """:root{--orange-900:#FF6000;--blue-m-900:#170453;--white:#FFFFFF;--gray-100:#F5F5F5;--gray-200:#E5E5E5;--gray-700:#404040;--gray-900:#171717;--space-md:16px;--space-lg:24px;--space-xl:32px;--radius-md:8px;}
.contentGenerator__main,.contentGenerator__faqs,.contentGenerator__verdict{font-family:'Inter',sans-serif;line-height:1.7;color:var(--gray-900);max-width:100%;}
.contentGenerator__main h2,.contentGenerator__main h3{margin-bottom:var(--space-lg);}
.kicker{display:inline-block;background:var(--orange-900);color:var(--white);padding:4px 12px;font-size:12px;font-weight:700;text-transform:uppercase;border-radius:4px;margin-bottom:16px;}
.toc{background:var(--gray-100);border-radius:var(--radius-md);padding:var(--space-lg);margin:var(--space-lg) 0;}
.toc__title{font-weight:700;margin-bottom:12px;}
.toc__list{margin:0;padding-left:20px;}
.toc__list li{margin-bottom:8px;}
.faqs__item{border-bottom:1px solid var(--gray-200);padding:var(--space-md) 0;}
.faqs__question{font-weight:600;margin-bottom:8px;}
.verdict-box{background:linear-gradient(135deg,var(--blue-m-900),#2E1A7A);color:var(--white);padding:var(--space-xl);border-radius:var(--radius-md);margin-top:var(--space-lg);}
.verdict-box a{color:#FFD700;text-decoration:underline;}
.verdict-box a:hover{color:var(--white);}
.verdict-box p:last-child{margin-bottom:0;}
.callout{background:var(--gray-100);border-left:4px solid var(--orange-900);padding:var(--space-md) var(--space-lg);margin:var(--space-lg) 0;border-radius:0 var(--radius-md) var(--radius-md) 0;}
.callout p:last-child{margin-bottom:0;}
.callout-bf{background:linear-gradient(135deg,#FF6000,#FF8533);color:var(--white);padding:var(--space-lg);border-radius:var(--radius-md);text-align:center;margin:var(--space-lg) 0;}
.callout-bf p{font-size:1.1em;line-height:1.5;margin:0 auto;max-width:90%;}
.callout-bf p:first-of-type{font-weight:700;text-transform:uppercase;letter-spacing:0.5px;margin-bottom:8px;}
.callout-bf p:last-child{margin-bottom:0;}
.callout-bf a{color:var(--white);text-decoration:underline;font-weight:600;}
.callout-bf a:hover{color:#FFD700;}
@media(max-width:768px){.callout-bf{padding:var(--space-md);}.callout-bf p{font-size:1em;max-width:100%;}}
table{width:100%;border-collapse:collapse;margin:var(--space-lg) 0;table-layout:fixed;}
th,td{padding:12px 16px;text-align:left;border-bottom:1px solid var(--gray-200);word-wrap:break-word;}
th{background:var(--gray-100);font-weight:600;}
th:first-child,td:first-child{width:30%;}
.grid-layout{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:var(--space-lg);margin-top:var(--space-lg);}
.grid-item{background:var(--white);border:1px solid var(--gray-200);border-radius:var(--radius-md);padding:var(--space-lg) var(--space-xl);}
.grid-item h4{margin-top:0;margin-bottom:var(--space-md);}
.grid-item p{margin-bottom:var(--space-md);}
.grid-item a{color:var(--orange-900);font-weight:600;}
.card.destacado{border:2px solid var(--orange-900);position:relative;}
.card.destacado::before{content:'DESTACADO';position:absolute;top:-10px;left:20px;background:var(--orange-900);color:var(--white);padding:2px 8px;font-size:11px;border-radius:4px;}
.product-module{background:var(--gray-100);padding:var(--space-xl);border-radius:var(--radius-md);margin:var(--space-lg) 0;}
.product-module h4{margin-top:0;}
.price-tag{font-size:1.5em;font-weight:700;color:var(--orange-900);}"""


# ============================================================================
# FUSIÓN DE DATOS DE PRODUCTO
# ============================================================================

def _merge_product_data(
    pdp_data: Optional[Dict],
    pdp_json_data: Optional[Dict]
) -> Optional[Dict]:
    """
    Fusiona datos de producto de múltiples fuentes.
    
    Prioridad:
    1. pdp_json_data (JSON subido por usuario) - más completo
    2. pdp_data (datos de n8n webhook) - fallback
    
    Args:
        pdp_data: Datos del webhook n8n
        pdp_json_data: Datos del JSON subido
        
    Returns:
        Dict fusionado con todos los datos disponibles
    """
    if not pdp_data and not pdp_json_data:
        return None
    
    # Si solo hay una fuente, usarla
    if not pdp_data:
        return pdp_json_data
    if not pdp_json_data:
        return pdp_data
    
    # Fusionar: pdp_json_data tiene prioridad
    merged = dict(pdp_data)  # Copiar base
    
    # Campos de pdp_json_data que tienen prioridad
    priority_fields = [
        'title', 'description', 'brand_name', 'family_name',
        'attributes', 'images', 'totalComments', 'total_comments',
        'advantages', 'disadvantages', 'comments',
        'advantages_list', 'disadvantages_list', 'top_comments',
        'has_user_feedback'
    ]
    
    for field in priority_fields:
        if field in pdp_json_data and pdp_json_data[field]:
            merged[field] = pdp_json_data[field]
    
    # Normalizar campos
    if 'totalComments' in merged and 'total_comments' not in merged:
        merged['total_comments'] = merged['totalComments']
    
    # Procesar ventajas/desventajas si vienen como string
    if 'advantages' in merged and isinstance(merged['advantages'], str):
        if 'advantages_list' not in merged:
            merged['advantages_list'] = _parse_advantages_string(merged['advantages'])
    
    if 'disadvantages' in merged and isinstance(merged['disadvantages'], str):
        if 'disadvantages_list' not in merged:
            merged['disadvantages_list'] = _parse_advantages_string(merged['disadvantages'])
    
    # Procesar comentarios
    if 'comments' in merged and isinstance(merged['comments'], list):
        if 'top_comments' not in merged:
            merged['top_comments'] = _extract_comment_texts(merged['comments'])
    
    # Flag de feedback
    if 'has_user_feedback' not in merged:
        merged['has_user_feedback'] = bool(
            merged.get('advantages_list') or 
            merged.get('disadvantages_list') or 
            merged.get('top_comments')
        )
    
    return merged


def _parse_advantages_string(text: str, max_items: int = 10) -> List[str]:
    """Parsea string de ventajas/desventajas a lista."""
    if not text:
        return []
    
    # Normalizar separadores
    normalized = text.replace('\n\n', '\n')
    items = [item.strip() for item in normalized.split('\n')]
    
    # Filtrar
    skip_words = ['ninguno', 'nada', 'ninguna', 'n/a', '-', '']
    filtered = []
    for item in items:
        if not item or len(item) < 8:
            continue
        if item.lower().strip() in skip_words:
            continue
        filtered.append(item)
    
    return filtered[:max_items]


def _extract_comment_texts(comments: List[Any], max_items: int = 5) -> List[str]:
    """Extrae textos de comentarios."""
    if not comments:
        return []
    
    result = []
    for item in comments:
        if isinstance(item, dict):
            text = item.get('opinion') or item.get('text') or item.get('content')
            if text and isinstance(text, str) and len(text) >= 15:
                result.append(text.strip())
        elif isinstance(item, str) and len(item) >= 15:
            result.append(item.strip())
    
    return result[:max_items]


# ============================================================================
# FORMATEAR DATOS DE PRODUCTO PARA PROMPT
# ============================================================================

def _format_product_section(pdp_data: Optional[Dict]) -> tuple:
    """
    Formatea datos del producto para el prompt.
    
    Args:
        pdp_data: Dict con datos del producto (ya fusionados)
        
    Returns:
        Tuple[section_text: str, has_feedback: bool]
    """
    if not pdp_data:
        return "", False
    
    lines = []
    has_feedback = pdp_data.get('has_user_feedback', False)
    
    lines.append("=" * 60)
    lines.append("📦 DATOS DEL PRODUCTO PRINCIPAL")
    lines.append("=" * 60)
    
    # Info básica
    title = pdp_data.get('title') or pdp_data.get('name', '')
    if title:
        lines.append(f"\n**Producto:** {title}")
    
    brand = pdp_data.get('brand_name') or pdp_data.get('brand', '')
    if brand:
        lines.append(f"**Marca:** {brand}")
    
    family = pdp_data.get('family_name') or pdp_data.get('family', '')
    if family:
        lines.append(f"**Categoría:** {family}")
    
    # Descripción breve
    desc = pdp_data.get('description', '')
    if desc and len(desc) > 50:
        short_desc = desc[:300] + "..." if len(desc) > 300 else desc
        lines.append(f"\n**Descripción:** {short_desc}")
    
    # Especificaciones
    attrs = pdp_data.get('attributes', {})
    if attrs:
        lines.append("\n**📋 ESPECIFICACIONES:**")
        for i, (k, v) in enumerate(attrs.items()):
            if i >= 10:
                lines.append(f"  ... (+{len(attrs) - 10} más)")
                break
            lines.append(f"  • {k}: {v}")
    
    # Credibilidad
    total = pdp_data.get('total_comments') or pdp_data.get('totalComments', 0)
    if total and total > 0:
        lines.append(f"\n**⭐ VALORACIONES:** {total} opiniones de compradores")
    
    # Ventajas (procesadas)
    advs = pdp_data.get('advantages_list', [])
    if advs:
        lines.append("\n**🟢 LO QUE VALORAN LOS USUARIOS (usa para argumentar):**")
        for adv in advs[:8]:
            lines.append(f"  ✓ {adv}")
    
    # Desventajas (procesadas)
    disadvs = pdp_data.get('disadvantages_list', [])
    if disadvs:
        lines.append("\n**🟡 PUNTOS A CONSIDERAR (menciona con honestidad):**")
        for dis in disadvs[:5]:
            lines.append(f"  • {dis}")
    
    # Opiniones
    comments = pdp_data.get('top_comments', [])
    if comments:
        lines.append("\n**💬 ASÍ HABLAN LOS USUARIOS (inspírate en su lenguaje):**")
        for i, c in enumerate(comments[:3]):
            short = c[:200] + "..." if len(c) > 200 else c
            lines.append(f'\n  [{i+1}] "{short}"')
    
    lines.append("\n" + "=" * 60)
    return "\n".join(lines), has_feedback


def _format_pdp_links_with_data(links_data: Optional[List[Dict]]) -> str:
    """
    Formatea enlaces PDP incluyendo datos de producto de cada uno.
    
    Args:
        links_data: Lista de enlaces [{url, anchor, type, product_data}]
        
    Returns:
        Sección formateada para el prompt
    """
    if not links_data:
        return ""
    
    lines = []
    lines.append("\n## 🔗 ENLACES OBLIGATORIOS")
    lines.append("Incluye TODOS estos enlaces de forma natural en el contenido.\n")
    
    pdp_with_data = []
    other_links = []
    
    for link in links_data:
        if link.get('product_data'):
            pdp_with_data.append(link)
        else:
            other_links.append(link)
    
    # Primero enlaces con datos de producto
    if pdp_with_data:
        lines.append("### 🛒 Productos con datos (enriquece el contenido con esta info):\n")
        
        for i, link in enumerate(pdp_with_data, 1):
            url = link.get('url', '')
            anchor = link.get('anchor', '')
            pdata = link.get('product_data', {})
            
            lines.append(f"**{i}. [{anchor}]({url})**")
            
            # Info del producto
            title = pdata.get('title', '')
            if title:
                lines.append(f"   • Producto: {title}")
            
            brand = pdata.get('brand_name', '')
            if brand:
                lines.append(f"   • Marca: {brand}")
            
            # Ventajas breves
            advs = pdata.get('advantages_list', [])[:3]
            if advs:
                lines.append(f"   • Puntos fuertes: {', '.join(advs)}")
            
            # Desventajas breves
            disadvs = pdata.get('disadvantages_list', [])[:2]
            if disadvs:
                lines.append(f"   • A considerar: {', '.join(disadvs)}")
            
            lines.append("")
    
    # Luego enlaces sin datos
    if other_links:
        lines.append("### 🔗 Enlaces adicionales:\n")
        for i, link in enumerate(other_links, 1):
            url = link.get('url', '')
            anchor = link.get('anchor', '')
            ltype = link.get('type', 'interno')
            lines.append(f"{i}. [{anchor}]({url}) - {ltype}")
    
    return "\n".join(lines)


def _format_alternative_product(alternative_product: Optional[Dict]) -> str:
    """
    Formatea producto alternativo incluyendo datos JSON si disponibles.
    
    Args:
        alternative_product: Dict con url, name y opcionalmente json_data
        
    Returns:
        Sección formateada
    """
    if not alternative_product:
        return ""
    
    url = alternative_product.get('url', '')
    name = alternative_product.get('name', 'Alternativa')
    json_data = alternative_product.get('json_data')
    
    if not url and not json_data:
        return ""
    
    lines = []
    lines.append("\n## 🔄 PRODUCTO ALTERNATIVO A MENCIONAR")
    lines.append("Incluye este producto como alternativa en el contenido.\n")
    
    if json_data:
        # Tenemos datos completos
        title = json_data.get('title', name)
        brand = json_data.get('brand_name', '')
        
        lines.append(f"**Producto:** {title}")
        if brand:
            lines.append(f"**Marca:** {brand}")
        if url:
            lines.append(f"**URL:** {url}")
        
        # Atributos clave
        attrs = json_data.get('attributes', {})
        if attrs:
            key_attrs = list(attrs.items())[:5]
            lines.append("\n**Características clave:**")
            for k, v in key_attrs:
                lines.append(f"  • {k}: {v}")
        
        # Ventajas
        advs = json_data.get('advantages_list', [])[:4]
        if advs:
            lines.append("\n**Puntos fuertes:**")
            for adv in advs:
                lines.append(f"  ✓ {adv}")
        
        # Por qué recomendarlo
        lines.append("\n**Cómo mencionarlo:**")
        lines.append("  - Como alternativa para un perfil diferente de usuario")
        lines.append("  - Cuando el producto principal no encaje con ciertas necesidades")
        lines.append("  - En la sección de veredicto como opción complementaria")
    else:
        # Solo URL y nombre
        lines.append(f"- **{name}**: {url}")
        lines.append("\nMenciónalo como alternativa sin inventar características.")
    
    return "\n".join(lines)


def _format_visual_elements_instructions(visual_elements: Optional[List[str]]) -> str:
    """
    Genera instrucciones para elementos visuales seleccionados.
    
    Args:
        visual_elements: Lista de elementos ['toc', 'table', 'callout', etc.]
        
    Returns:
        Instrucciones para el prompt
    """
    if not visual_elements:
        return ""
    
    lines = []
    lines.append("\n## 🎨 ELEMENTOS VISUALES A INCLUIR")
    lines.append("El usuario ha solicitado estos elementos. Inclúyelos donde corresponda:\n")
    
    element_instructions = {
        'toc': """**📑 Tabla de Contenidos (TOC):**
```html
<nav class="toc">
    <p class="toc__title">En este artículo</p>
    <ol class="toc__list">
        <li><a href="#seccion1">Sección 1</a></li>
        <!-- Más secciones -->
    </ol>
</nav>
```
Colócala después del H2 principal.""",

        'table': """**📊 Tabla Comparativa:**
```html
<table>
    <thead>
        <tr><th>Característica</th><th>Producto A</th><th>Producto B</th></tr>
    </thead>
    <tbody>
        <tr><td>Spec</td><td>Valor</td><td>Valor</td></tr>
    </tbody>
</table>
```
Úsala para comparar productos o características de forma visual.""",

        'callout': """**💡 Callouts/Destacados:**
```html
<div class="callout">
    <p><strong>💡 Consejo:</strong> Información importante destacada.</p>
</div>
```
Usa callouts para tips, advertencias o información clave.""",

        'callout_bf': """**Callout Black Friday:**
```html
<div class="callout-bf">
    <p><strong>OFERTA BLACK FRIDAY</strong></p>
    <p>Descripción de la oferta especial.</p>
</div>
```
Para destacar ofertas especiales o promociones.""",

        'verdict_box': """**✅ Verdict Box (OBLIGATORIO):**
```html
<div class="verdict-box">
    <h2>Veredicto Final</h2>
    <p>Conclusión honesta que APORTE valor real...</p>
</div>
```
Siempre al final, con conclusión que aporte, no que resuma.""",

        'grid': """**📐 Grid Layout:**
```html
<div class="grid-layout">
    <div class="grid-item">
        <h4>Producto 1</h4>
        <p>Descripción breve...</p>
    </div>
    <!-- Más items -->
</div>
```
Para mostrar múltiples productos o características en rejilla.""",
    }
    
    for elem in visual_elements:
        if elem in element_instructions:
            lines.append(element_instructions[elem])
            lines.append("")
    
    return "\n".join(lines)


def _get_data_usage_instructions(has_data: bool, has_feedback: bool) -> str:
    """
    Genera instrucciones específicas según los datos disponibles.
    """
    if has_data and has_feedback:
        return """
## 📦 CÓMO USAR LOS DATOS DEL PRODUCTO

Tienes datos REALES del producto incluyendo opiniones de usuarios. ÚSALOS:

1. **Ventajas (🟢):** Puntos que compradores REALES han destacado
   - Úsalos para argumentar beneficios con credibilidad
   - Parafrasea con tu estilo, no copies literalmente

2. **Desventajas (🟡):** Los "peros" que han encontrado
   - MENCIÓNALOS con honestidad (genera CONFIANZA)
   - Contextualiza: "para el precio no se puede pedir más"

3. **Opiniones (💬):** Lenguaje de usuarios reales
   - Inspírate en sus expresiones naturales
   - Evita sonar robótico: ellos hablan como personas

4. **Especificaciones:** Traduce datos técnicos a beneficios PRÁCTICOS
"""
    elif has_data:
        return """
## 📦 DATOS DISPONIBLES

Tienes información básica del producto pero sin feedback de usuarios.
Usa los datos como contexto y complementa con tu conocimiento del sector.
"""
    else:
        return """
## 📝 SIN DATOS ESPECÍFICOS DE PRODUCTO

No tienes datos del producto, pero puedes crear contenido IGUAL DE BUENO:

1. **Céntrate en la keyword:** Es tu guía principal
2. **Usa conocimiento general:** Eres experto en tecnología
3. **Habla de la categoría:** Qué busca alguien interesado en esto
4. **Da consejos prácticos:** Qué debería considerar el comprador
5. **Sé honesto:** "Depende de tu uso" es mejor que inventar

El tono debe ser el mismo: cercano, experto, con chispa y honesto.
"""


# ============================================================================
# ETAPA 1: BORRADOR INICIAL
# ============================================================================

def build_new_content_prompt_stage1(
    keyword: str,
    arquetipo: Dict[str, Any],
    target_length: int = 1500,
    pdp_data: Optional[Dict] = None,
    pdp_json_data: Optional[Dict] = None,  # NUEVO v4.9.0
    links_data: Optional[List[Dict]] = None,
    secondary_keywords: Optional[List[str]] = None,
    additional_instructions: str = "",
    campos_especificos: Optional[Dict] = None,
    visual_elements: Optional[List[str]] = None,
    guiding_context: str = "",
    alternative_product: Optional[Dict] = None,
) -> str:
    """
    Construye prompt para Etapa 1: Borrador inicial.
    
    Funciona igual de bien CON o SIN datos de producto.
    
    NUEVO v4.9.0:
    - Fusiona pdp_data + pdp_json_data
    - Procesa product_data en enlaces PDP
    - Usa alternative_product.json_data
    - Implementa visual_elements
    
    Args:
        keyword: Keyword principal
        arquetipo: Dict con name, description del arquetipo
        target_length: Longitud objetivo en palabras
        pdp_data: Dict con datos del producto (de n8n webhook)
        pdp_json_data: Dict con datos del JSON subido (NUEVO - tiene prioridad)
        links_data: Lista de enlaces [{url, anchor, type, product_data}]
        secondary_keywords: Keywords secundarias
        additional_instructions: Instrucciones adicionales del usuario
        campos_especificos: Campos específicos del arquetipo
        visual_elements: Elementos visuales a incluir ['toc', 'table', etc.]
        guiding_context: Contexto guía del usuario
        alternative_product: Producto alternativo {url, name, json_data}
        
    Returns:
        Prompt completo para Claude
    """
    arquetipo_name = arquetipo.get('name', 'Contenido SEO')
    arquetipo_desc = arquetipo.get('description', '')
    
    # NUEVO: Fusionar datos de producto
    merged_product_data = _merge_product_data(pdp_data, pdp_json_data)
    
    # Formatear producto principal
    product_section, has_feedback = _format_product_section(merged_product_data)
    has_product_data = bool(merged_product_data)
    
    # Instrucciones de tono (adapta según si hay datos)
    tone_instructions = get_tone_instructions(has_product_data)
    
    # Instrucciones de uso de datos
    data_instructions = _get_data_usage_instructions(has_product_data, has_feedback)
    
    # NUEVO: Enlaces con datos de producto
    links_section = _format_pdp_links_with_data(links_data)
    
    # Keywords secundarias
    sec_kw = ""
    if secondary_keywords:
        sec_kw = "\n## 🔑 KEYWORDS SECUNDARIAS\n" + "\n".join(f"- {k}" for k in secondary_keywords)
    
    # Contexto guía
    context = f"\n## 📖 CONTEXTO DEL USUARIO\n{guiding_context}\n" if guiding_context else ""
    
    # NUEVO: Producto alternativo con datos JSON
    alt_prod = _format_alternative_product(alternative_product)
    
    # NUEVO: Elementos visuales
    visual_section = _format_visual_elements_instructions(visual_elements)
    
    # Campos específicos del arquetipo
    campos_section = ""
    if campos_especificos:
        campos_section = "\n## 📋 CAMPOS ESPECÍFICOS DEL ARQUETIPO\n"
        for key, value in campos_especificos.items():
            if value:
                campos_section += f"- **{key}:** {value}\n"
    
    # Construir prompt
    prompt = f"""Eres un redactor SEO de PcComponentes, la tienda líder de tecnología en España.

# TAREA
Genera un BORRADOR tipo "{arquetipo_name}" para la keyword "{keyword}".

{arquetipo_desc}

## PARÁMETROS
- **Keyword principal:** {keyword}
- **Longitud objetivo:** ~{target_length} palabras
- **Tipo de contenido:** {arquetipo_name}

{product_section}

{tone_instructions}

{data_instructions}
{links_section}
{sec_kw}
{context}
{alt_prod}
{visual_section}
{campos_section}

## ESTRUCTURA HTML REQUERIDA

El HTML debe empezar DIRECTAMENTE con <style>:

```
<style>
{CSS_INLINE_MINIFIED}
</style>

<article class="contentGenerator__main">
    <span class="kicker">KICKER ATRACTIVO</span>
    <h2>Título que incluya {keyword}</h2>
    
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
            <h3 class="faqs__question">¿Pregunta con keyword?</h3>
            <p class="faqs__answer">Respuesta útil...</p>
        </div>
    </div>
</article>

<article class="contentGenerator__verdict">
    <div class="verdict-box">
        <h2>Veredicto Final</h2>
        <p>Conclusión honesta que APORTE valor real, no un resumen...</p>
    </div>
</article>
```

## INSTRUCCIONES ADICIONALES
{additional_instructions or "(Ninguna)"}

---

## REGLAS CRÍTICAS

1. **NO** uses ```html ni marcadores markdown
2. Empieza DIRECTAMENTE con `<style>`
3. FAQs DEBEN incluir keyword: "Preguntas frecuentes sobre {keyword}"
4. Si tienes datos de usuarios, ÚSALOS (ventajas/desventajas)
5. Si tienes datos de productos enlazados, MENCIÓNALOS con sus características
6. SÉ HONESTO: si hay "peros", menciónalos
7. **EVITA frases de IA:** "en el mundo actual", "sin lugar a dudas", etc.
8. El veredicto debe APORTAR, no solo resumir
9. Incluye TODOS los enlaces proporcionados con su anchor text exacto
10. **EMOJIS:** Solo puedes usar estos 3 emojis en el contenido: ⚡ 💡 ✅ (ningún otro)

**Genera el HTML ahora:**
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
    Construye prompt para Etapa 2: Análisis crítico del borrador.
    
    Args:
        draft_content: HTML del borrador generado en Stage 1
        target_length: Longitud objetivo
        keyword: Keyword principal
        links_to_verify: Enlaces que deben estar presentes
        alternative_product: Producto alternativo que debe aparecer
        
    Returns:
        Prompt para análisis
    """
    # Verificación de enlaces
    links_check = ""
    if links_to_verify:
        links_check = "\n## ENLACES A VERIFICAR\n"
        links_check += "Cada uno de estos enlaces DEBE aparecer en el contenido:\n"
        for link in links_to_verify:
            anchor = link.get('anchor', '')
            url = link.get('url', '')
            has_data = "✓ con datos" if link.get('product_data') else ""
            links_check += f"- [{anchor}]({url}) {has_data}\n"
    
    # Verificación de producto alternativo
    alt_check = ""
    if alternative_product:
        url = alternative_product.get('url', '')
        name = alternative_product.get('name', '')
        has_json = "✓ con datos JSON" if alternative_product.get('json_data') else ""
        if url or name:
            alt_check = f"\n## PRODUCTO ALTERNATIVO QUE DEBE APARECER\n- {name} ({url}) {has_json}\n"
    
    return f"""Eres un editor SEO senior de PcComponentes. Analiza críticamente este borrador.

# BORRADOR A ANALIZAR

{draft_content[:12000]}

# PARÁMETROS
- **Keyword:** {keyword}
- **Longitud objetivo:** ~{target_length} palabras
{links_check}
{alt_check}

# CHECKLIST DE VERIFICACIÓN

## 1. TONO DE MARCA PCCOMPONENTES
- [ ] ¿Suena a PcComponentes? (cercano, experto, con chispa)
- [ ] ¿Tutea al lector de forma natural?
- [ ] ¿Es honesto sobre pros y contras?
- [ ] ¿Tiene personalidad o suena genérico?

## 2. ANTI-IA (CRÍTICO)
- [ ] ¿Evita "En el mundo actual...", "Sin lugar a dudas..."?
- [ ] ¿Evita adjetivos vacíos (increíble, revolucionario)?
- [ ] ¿Varía la estructura de los párrafos?
- [ ] ¿El veredicto aporta valor o solo resume?

## 3. ESTRUCTURA HTML
- [ ] ¿Empieza con <style> (NO con ```html)?
- [ ] ¿Tiene contentGenerator__main con kicker y toc?
- [ ] ¿Tiene contentGenerator__faqs con keyword en título?
- [ ] ¿Tiene contentGenerator__verdict con verdict-box?

## 4. SEO Y CONTENIDO
- [ ] ¿La keyword aparece de forma natural?
- [ ] ¿TODOS los enlaces proporcionados están incluidos?
- [ ] ¿Se mencionan los datos de los productos enlazados?
- [ ] ¿La longitud es aproximada al objetivo?

## 5. DATOS DE PRODUCTO (si aplica)
- [ ] ¿Se usan las ventajas/desventajas proporcionadas?
- [ ] ¿Se menciona el producto alternativo?
- [ ] ¿Los datos de productos enlazados enriquecen el contenido?

---

**Responde SOLO con JSON estructurado:**

```json
{{
    "longitud_actual": 0,
    "longitud_objetivo": {target_length},
    "necesita_ajuste_longitud": false,
    
    "estructura": {{
        "tiene_style": false,
        "tiene_main": false,
        "tiene_faqs": false,
        "tiene_verdict": false,
        "faqs_incluye_keyword": false,
        "tiene_markdown_wrapper": false
    }},
    
    "tono": {{
        "es_cercano": false,
        "es_honesto": false,
        "tiene_personalidad": false,
        "evita_frases_ia": false,
        "frases_ia_detectadas": []
    }},
    
    "enlaces": {{
        "presentes": [],
        "faltantes": [],
        "con_datos_usados": []
    }},
    
    "datos_producto": {{
        "usa_ventajas": false,
        "usa_desventajas": false,
        "menciona_alternativa": false,
        "datos_pdp_links_usados": false
    }},
    
    "problemas": [
        {{
            "tipo": "estructura|seo|tono|formato|datos",
            "severidad": "critico|alto|medio|bajo",
            "descripcion": "...",
            "solucion": "..."
        }}
    ],
    
    "aspectos_positivos": [],
    "puntuacion_general": 0,
    "recomendacion_principal": ""
}}
```

**Responde ÚNICAMENTE con el JSON, sin texto adicional.**
"""


# Alias de compatibilidad
def build_correction_prompt_stage2(*args, **kwargs):
    return build_new_content_correction_prompt_stage2(*args, **kwargs)


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
    Construye prompt para Etapa 3: Versión final corregida.
    
    Args:
        draft_content: HTML del borrador
        analysis_feedback: Feedback del análisis (JSON o texto)
        keyword: Keyword principal
        target_length: Longitud objetivo
        links_data: Enlaces obligatorios (ahora con product_data)
        alternative_product: Producto alternativo (ahora con json_data)
        
    Returns:
        Prompt para generación final
    """
    # Enlaces con datos
    links_section = ""
    if links_data:
        links_section = "\n## ENLACES OBLIGATORIOS (con datos si disponibles)\n"
        for i, link in enumerate(links_data, 1):
            anchor = link.get('anchor', '')
            url = link.get('url', '')
            pdata = link.get('product_data')
            
            links_section += f"{i}. [{anchor}]({url})"
            if pdata:
                title = pdata.get('title', '')
                if title:
                    links_section += f" - {title}"
            links_section += "\n"
    
    # Producto alternativo
    alt_section = ""
    if alternative_product:
        url = alternative_product.get('url', '')
        name = alternative_product.get('name', '')
        json_data = alternative_product.get('json_data')
        
        if url or json_data:
            alt_section = f"\n## PRODUCTO ALTERNATIVO\n"
            if json_data:
                title = json_data.get('title', name)
                brand = json_data.get('brand_name', '')
                alt_section += f"- **{title}** ({brand}) - {url}\n"
                advs = json_data.get('advantages_list', [])[:3]
                if advs:
                    alt_section += f"  Puntos fuertes: {', '.join(advs)}\n"
            else:
                alt_section += f"- {name} ({url})\n"
    
    return f"""Genera la VERSIÓN FINAL corregida como editor SEO senior de PcComponentes.

# BORRADOR ORIGINAL

{draft_content[:10000]}

# ANÁLISIS Y CORRECCIONES A APLICAR

{analysis_feedback[:4000]}
{links_section}
{alt_section}

# RECORDATORIO DE TONO PCCOMPONENTES

- **Expertos sin pedantes:** Explica sin tecnicismos innecesarios
- **Frikis sin vergüenza:** Referencias tech y humor cuando encaje
- **Honestos pero no aburridos:** Si hay "peros", dilos
- **Cercanos sin forzados:** Natural, no diminutivos ni emojis excesivos

## ❌ EVITAR SIGNOS DE IA (CRÍTICO)
- "En el mundo actual..." / "Sin lugar a dudas..."
- Adjetivos vacíos: increíble, revolucionario, impresionante
- El veredicto NO debe repetir lo ya dicho
- Estructuras repetitivas párrafo tras párrafo

# ESTRUCTURA FINAL REQUERIDA

```
<style>
{CSS_INLINE_MINIFIED}
</style>

<article class="contentGenerator__main">
    <span class="kicker">KICKER</span>
    <h2>Título con {keyword}</h2>
    <nav class="toc">...</nav>
    <section>...</section>
</article>

<article class="contentGenerator__faqs">
    <h2>Preguntas frecuentes sobre {keyword}</h2>
    <div class="faqs">...</div>
</article>

<article class="contentGenerator__verdict">
    <div class="verdict-box">
        <h2>Veredicto Final</h2>
        <p>Conclusión que APORTE valor real...</p>
    </div>
</article>
```

---

## REGLAS ABSOLUTAS

1. **NUNCA** uses ```html ni markdown
2. Empieza DIRECTAMENTE con `<style>`
3. Longitud aproximada: ~{target_length} palabras
4. FAQs: "Preguntas frecuentes sobre {keyword}"
5. Incluye verdict-box
6. Aplica TODAS las correcciones del análisis
7. Incluye TODOS los enlaces con datos de producto si disponibles
8. Menciona el producto alternativo si lo hay
9. Tono PcComponentes en cada párrafo
10. **EMOJIS:** Solo usa estos 3 emojis: ⚡ 💡 ✅ (ningún otro)

**Genera SOLO el HTML final, sin explicaciones:**
"""


# Alias de compatibilidad
def build_final_generation_prompt_stage3(
    draft_content: str,
    corrections_json: str,
    target_length: int = 1500,
) -> str:
    return build_final_prompt_stage3(
        draft_content, corrections_json, "", target_length, None, None
    )


# ============================================================================
# FUNCIONES AUXILIARES
# ============================================================================

def build_system_prompt() -> str:
    """System prompt para todas las etapas."""
    return get_system_prompt_base()


def get_css_styles() -> str:
    """Retorna el CSS minificado."""
    return CSS_INLINE_MINIFIED


def get_element_template(name: str) -> str:
    """Retorna plantilla de elemento."""
    templates = {
        'callout': '<div class="callout"><p><strong>💡 Dato:</strong> [Contenido]</p></div>',
        'callout_bf': '<div class="callout-bf"><p><strong>OFERTA</strong></p><p>[Contenido]</p></div>',
        'verdict_box': '<div class="verdict-box"><h2>Veredicto Final</h2><p>[Conclusión]</p></div>',
        'table': '<table><thead><tr><th>Característica</th><th>Valor</th></tr></thead><tbody><tr><td>...</td><td>...</td></tr></tbody></table>',
        'grid': '<div class="grid-layout"><div class="grid-item">...</div></div>',
        'product_module': '<div class="product-module"><h4>[Producto]</h4><p>[Descripción]</p></div>',
    }
    return templates.get(name, "")


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    '__version__',
    # Funciones principales
    'build_new_content_prompt_stage1',
    'build_new_content_correction_prompt_stage2',
    'build_correction_prompt_stage2',
    'build_final_prompt_stage3',
    'build_final_generation_prompt_stage3',
    'build_system_prompt',
    # Utilidades
    'get_css_styles',
    'get_element_template',
    # Constantes
    'CSS_INLINE_MINIFIED',
]
