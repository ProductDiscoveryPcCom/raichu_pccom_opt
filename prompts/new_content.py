# -*- coding: utf-8 -*-
"""
New Content Prompts - PcComponentes Content Generator
Versión 4.8.0

Prompts para generación de contenido nuevo en 3 etapas.

CARACTERÍSTICAS:
- Funciona igual de bien CON o SIN datos de producto
- CON datos: usa ventajas/desventajas/opiniones para contenido auténtico
- SIN datos: instrucciones alternativas basadas en conocimiento general
- Tono de marca PcComponentes integrado (desde config/brand.py)
- Instrucciones anti-IA para evitar patrones artificiales

CAMPOS DE PRODUCTO SOPORTADOS (del Dict pdp_data):
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

__version__ = "4.8.0"

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
# CSS MINIFICADO
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
table{width:100%;border-collapse:collapse;margin:var(--space-lg) 0;}
th,td{padding:12px;text-align:left;border-bottom:1px solid var(--gray-200);}
th{background:var(--gray-100);font-weight:600;}"""


# ============================================================================
# FORMATEAR DATOS DE PRODUCTO PARA PROMPT
# ============================================================================

def _format_product_section(pdp_data: Optional[Dict]) -> tuple:
    """
    Formatea datos del producto para el prompt.
    
    Args:
        pdp_data: Dict con datos del producto (resultado de PDPProductData.to_dict())
                  Puede ser None si no hay datos
        
    Returns:
        Tuple[section_text: str, has_feedback: bool]
    """
    if not pdp_data:
        return "", False
    
    lines = []
    has_feedback = pdp_data.get('has_user_feedback', False)
    
    lines.append("=" * 60)
    lines.append("DATOS DEL PRODUCTO")
    lines.append("=" * 60)
    
    # Info básica
    title = pdp_data.get('title', '')
    if title:
        lines.append(f"\n**Producto:** {title}")
    
    brand = pdp_data.get('brand_name', '')
    if brand:
        lines.append(f"**Marca:** {brand}")
    
    family = pdp_data.get('family_name', '')
    if family:
        lines.append(f"**Categoría:** {family}")
    
    # Especificaciones
    attrs = pdp_data.get('attributes', {})
    if attrs:
        lines.append("\n**📋 ESPECIFICACIONES:**")
        for i, (k, v) in enumerate(attrs.items()):
            if i >= 8:
                lines.append(f"  ... (+{len(attrs) - 8} más)")
                break
            lines.append(f"  • {k}: {v}")
    
    # Credibilidad
    total = pdp_data.get('total_comments', 0)
    if total > 0:
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


def _get_data_usage_instructions(has_data: bool, has_feedback: bool) -> str:
    """
    Genera instrucciones específicas según los datos disponibles.
    
    Args:
        has_data: Si hay datos de producto
        has_feedback: Si hay feedback de usuarios (ventajas/desventajas/opiniones)
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
    
    Args:
        keyword: Keyword principal
        arquetipo: Dict con name, description del arquetipo
        target_length: Longitud objetivo en palabras
        pdp_data: Dict con datos del producto (de PDPProductData.to_dict())
        links_data: Lista de enlaces [{url, anchor, type, product_data}]
        secondary_keywords: Keywords secundarias
        additional_instructions: Instrucciones adicionales del usuario
        campos_especificos: Campos específicos del arquetipo
        visual_elements: Elementos visuales a incluir
        guiding_context: Contexto guía del usuario
        alternative_product: Producto alternativo a mencionar
        
    Returns:
        Prompt completo para Claude
    """
    arquetipo_name = arquetipo.get('name', 'Contenido SEO')
    arquetipo_desc = arquetipo.get('description', '')
    
    # Formatear producto
    product_section, has_feedback = _format_product_section(pdp_data)
    has_product_data = bool(pdp_data)
    
    # Instrucciones de tono (adapta según si hay datos)
    tone_instructions = get_tone_instructions(has_product_data)
    
    # Instrucciones de uso de datos
    data_instructions = _get_data_usage_instructions(has_product_data, has_feedback)
    
    # Enlaces
    links_section = ""
    if links_data:
        links_section = "\n## 🔗 ENLACES OBLIGATORIOS (USA SOLO ESTOS)\n"
        for i, link in enumerate(links_data, 1):
            url = link.get('url', '')
            anchor = link.get('anchor', '')
            ltype = link.get('type', 'interno')
            links_section += f"{i}. **[{anchor}]({url})** - {ltype}\n"
    
    # Keywords secundarias
    sec_kw = ""
    if secondary_keywords:
        sec_kw = "\n## 🔑 KEYWORDS SECUNDARIAS\n" + "\n".join(f"- {k}" for k in secondary_keywords)
    
    # Contexto guía
    context = f"\n## 📖 CONTEXTO DEL USUARIO\n{guiding_context}\n" if guiding_context else ""
    
    # Producto alternativo
    alt_prod = ""
    if alternative_product and alternative_product.get('url'):
        alt_prod = f"\n## 🔄 PRODUCTO ALTERNATIVO A MENCIONAR\n- {alternative_product.get('name', 'Alternativa')} ({alternative_product['url']})\n"
    
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

## ⚠️ REGLAS CRÍTICAS

1. ❌ **NO** uses ```html ni marcadores markdown
2. ✅ Empieza DIRECTAMENTE con `<style>`
3. ✅ FAQs DEBEN incluir keyword: "Preguntas frecuentes sobre {keyword}"
4. ✅ Si tienes datos de usuarios, ÚSALOS (ventajas/desventajas)
5. ✅ SÉ HONESTO: si hay "peros", menciónalos
6. ✅ **EVITA frases de IA:** "en el mundo actual", "sin lugar a dudas", etc.
7. ✅ El veredicto debe APORTAR, no solo resumir

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
    links_check = ""
    if links_to_verify:
        links_check = "\n## ENLACES A VERIFICAR\n"
        for link in links_to_verify:
            links_check += f"- [{link.get('anchor', '')}]({link.get('url', '')})\n"
    
    alt_check = ""
    if alternative_product and alternative_product.get('url'):
        alt_check = f"\n## PRODUCTO ALTERNATIVO QUE DEBE APARECER\n- {alternative_product.get('name', '')} ({alternative_product['url']})\n"
    
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
- [ ] ¿Los enlaces proporcionados están incluidos?
- [ ] ¿La longitud es aproximada al objetivo?

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
        "faltantes": []
    }},
    
    "problemas": [
        {{
            "tipo": "estructura|seo|tono|formato",
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
        links_data: Enlaces obligatorios
        alternative_product: Producto alternativo
        
    Returns:
        Prompt para generación final
    """
    links_section = ""
    if links_data:
        links_section = "\n## ENLACES OBLIGATORIOS\n"
        for i, link in enumerate(links_data, 1):
            links_section += f"{i}. [{link.get('anchor', '')}]({link.get('url', '')})\n"
    
    alt_section = ""
    if alternative_product and alternative_product.get('url'):
        alt_section = f"\n## PRODUCTO ALTERNATIVO\n- {alternative_product.get('name', '')} ({alternative_product['url']})\n"
    
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

## ⚠️ REGLAS ABSOLUTAS

1. ❌ **NUNCA** uses ```html ni markdown
2. ✅ Empieza DIRECTAMENTE con `<style>`
3. ✅ Longitud aproximada: ~{target_length} palabras
4. ✅ FAQs: "Preguntas frecuentes sobre {keyword}"
5. ✅ Incluye verdict-box
6. ✅ Aplica TODAS las correcciones del análisis
7. ✅ Tono PcComponentes en cada párrafo

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
        'verdict_box': '<div class="verdict-box"><h2>Veredicto Final</h2><p>[Conclusión]</p></div>',
        'table': '<table><thead><tr><th>Característica</th><th>Valor</th></tr></thead><tbody><tr><td>...</td><td>...</td></tr></tbody></table>',
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
