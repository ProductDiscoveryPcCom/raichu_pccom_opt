"""
Utilidades para procesamiento de HTML - PcComponentes Content Generator
Versión 4.1.1

Este módulo proporciona funciones para:
- Contar palabras en HTML
- Extraer estructura de contenido
- Validar estructura HTML básica
- Validar estructura compatible con CMS de PcComponentes

Autor: PcComponentes - Product Discovery & Content
"""

import re
from typing import Dict, List, Optional, Tuple
from bs4 import BeautifulSoup


# ============================================================================
# FUNCIONES DE ANÁLISIS DE CONTENIDO
# ============================================================================

def count_words_in_html(html_content: str) -> int:
    """
    Cuenta el número de palabras en un contenido HTML excluyendo las etiquetas.
    
    Esta función elimina todos los tags HTML y cuenta las palabras del texto
    resultante. Es útil para verificar si se cumple con la longitud objetivo
    del contenido generado.
    
    Args:
        html_content (str): HTML completo del contenido
        
    Returns:
        int: Número de palabras en el texto (sin contar HTML tags)
        
    Examples:
        >>> html = "<p>Hola mundo</p>"
        >>> count_words_in_html(html)
        2
        
        >>> html = "<article><h1>Título</h1><p>Contenido de prueba aquí</p></article>"
        >>> count_words_in_html(html)
        5
    """
    # Eliminar todos los tags HTML
    text = re.sub(r'<[^>]+>', '', html_content)
    
    # Normalizar espacios en blanco
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Contar palabras
    if not text:
        return 0
    
    words = len(text.split())
    return words


def extract_content_structure(html_content: str) -> Dict:
    """
    Extrae la estructura del contenido HTML para análisis.
    
    Analiza el HTML y extrae información relevante como:
    - Título principal (H1)
    - Subtítulos (H2, H3, H4)
    - Número de palabras
    - Elementos especiales (tablas, callouts, FAQs, verdict-box)
    - Conteo de enlaces internos y externos
    
    Args:
        html_content (str): HTML completo del contenido
        
    Returns:
        Dict: Diccionario con la estructura detectada o información de error
        
        Estructura del diccionario de retorno (éxito):
        {
            'title': str,                    # Título principal (H1)
            'headings': List[Dict],          # Lista de encabezados con level y text
            'word_count': int,               # Número de palabras
            'has_table': bool,               # Si tiene tablas
            'has_callout': bool,             # Si tiene callouts
            'has_faq': bool,                 # Si tiene sección de FAQs
            'has_verdict': bool,             # Si tiene verdict-box
            'internal_links_count': int,     # Número de enlaces internos
            'external_links_count': int,     # Número de enlaces externos
            'structure_valid': bool          # True si se procesó correctamente
        }
        
        Estructura del diccionario de retorno (error):
        {
            'error': str,                    # Mensaje de error
            'structure_valid': bool          # False
        }
        
    Examples:
        >>> html = "<article><h1>Título</h1><p>Contenido</p></article>"
        >>> result = extract_content_structure(html)
        >>> result['title']
        'Título'
        >>> result['word_count']
        2
    """
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Extraer título principal (H1)
        title = ""
        h1 = soup.find('h1')
        if h1:
            title = h1.get_text(strip=True)
        
        # Extraer subtítulos (H2, H3, H4)
        headings = []
        for h in soup.find_all(['h2', 'h3', 'h4']):
            heading_text = h.get_text(strip=True)
            if heading_text:  # Solo añadir si tiene texto
                headings.append({
                    'level': h.name,
                    'text': heading_text
                })
        
        # Contar palabras del contenido completo
        text = soup.get_text(' ', strip=True)
        word_count = len(text.split()) if text else 0
        
        # Detectar elementos especiales
        has_table = bool(soup.find('table') or soup.find(class_='lt'))
        has_callout = bool(soup.find(class_=['callout', 'bf-callout']))
        has_faq = bool(soup.find(class_='faqs'))
        has_verdict = bool(soup.find(class_='verdict-box'))
        
        # Contar enlaces internos y externos
        links = soup.find_all('a', href=True)
        internal_links = []
        external_links = []
        
        for link in links:
            href = link.get('href', '')
            if 'pccomponentes.com' in href:
                internal_links.append(link)
            elif href.startswith('http'):
                external_links.append(link)
        
        return {
            'title': title,
            'headings': headings,
            'word_count': word_count,
            'has_table': has_table,
            'has_callout': has_callout,
            'has_faq': has_faq,
            'has_verdict': has_verdict,
            'internal_links_count': len(internal_links),
            'external_links_count': len(external_links),
            'structure_valid': True
        }
        
    except Exception as e:
        return {
            'error': str(e),
            'structure_valid': False
        }


# ============================================================================
# FUNCIONES DE VALIDACIÓN
# ============================================================================

def validate_html_structure(html_content: str) -> Dict[str, bool]:
    """
    Valida la estructura HTML básica (v4.1).
    
    Realiza validaciones básicas de estructura HTML sin entrar en el detalle
    de la estructura específica del CMS. Esta función es útil para validaciones
    rápidas durante el proceso de generación.
    
    Args:
        html_content (str): HTML completo a validar
        
    Returns:
        Dict[str, bool]: Diccionario con checks de validación básicos
        
        Keys del diccionario:
        - has_article: Si tiene tag <article>
        - kicker_uses_span: Si el kicker usa <span> (no <div>)
        - css_has_root: Si el CSS incluye variables :root
        - has_bf_callout: Si incluye el callout de Black Friday
        - no_markdown: Si no contiene sintaxis markdown
        
    Examples:
        >>> html = "<article><span class='kicker'>Test</span></article>"
        >>> result = validate_html_structure(html)
        >>> result['has_article']
        True
        >>> result['kicker_uses_span']
        True
    """
    html_lower = html_content.lower()
    
    return {
        'has_article': '<article>' in html_lower,
        'kicker_uses_span': '<span class="kicker">' in html_lower,
        'css_has_root': ':root' in html_content,
        'has_bf_callout': 'bf-callout' in html_lower,
        'no_markdown': not any(md in html_content for md in ['```', '**', '##'])
    }


def validate_cms_structure(html_content: str) -> Tuple[bool, List[str], List[str]]:
    """
    Valida que el HTML cumpla con los requisitos del CMS de PcComponentes (v4.1.1).
    
    Esta función realiza una validación exhaustiva de la estructura HTML para
    asegurar que sea compatible con el CMS de PcComponentes. El CMS requiere
    una estructura específica de 3 articles separados.
    
    Verifica:
    1. Estructura de 3 articles separados
    2. Primer article contiene solo el kicker
    3. Segundo article está vacío (separador)
    4. Tercer article contiene todo el contenido
    5. CSS al inicio del documento
    6. Uso de H2 como título principal (NO H1)
    7. Kicker usa <span>, no <div>
    
    Args:
        html_content (str): HTML completo a validar
        
    Returns:
        Tuple[bool, List[str], List[str]]: Tupla con 3 elementos:
            - is_valid (bool): True si pasa todas las validaciones críticas
            - errors (List[str]): Lista de errores críticos encontrados
            - warnings (List[str]): Lista de advertencias no críticas
            
    Examples:
        >>> html = '''
        ... <style>:root{}</style>
        ... <article><span class="kicker">Test</span></article>
        ... <article></article>
        ... <article><h2>Título</h2><p>Contenido</p></article>
        ... '''
        >>> is_valid, errors, warnings = validate_cms_structure(html)
        >>> is_valid
        True
        >>> len(errors)
        0
        
    Notes:
        - Los errores bloquean la publicación en el CMS
        - Los warnings son recomendaciones que no bloquean
        - La función es case-sensitive para preservar la estructura HTML
    """
    errors = []
    warnings = []
    
    # ========================================================================
    # VALIDACIÓN 1: CSS al inicio
    # ========================================================================
    if not html_content.strip().startswith('<style>'):
        errors.append("❌ El HTML debe empezar con <style>")
    
    # ========================================================================
    # VALIDACIÓN 2: Conteo de tags <article>
    # ========================================================================
    article_count = html_content.count('<article>')
    
    if article_count < 3:
        errors.append(
            f"❌ Se encontraron {article_count} tags <article>, "
            f"deben ser mínimo 3 para cumplir con la estructura del CMS"
        )
    elif article_count > 3:
        warnings.append(
            f"⚠️ Se encontraron {article_count} tags <article>, "
            f"lo normal son exactamente 3"
        )
    
    # ========================================================================
    # VALIDACIÓN 3: Estructura del primer article (kicker)
    # ========================================================================
    # Patrón: <article> seguido de <span class="kicker">TEXTO</span> y </article>
    kicker_pattern = r'<article>\s*<span class="kicker">[^<]+</span>\s*</article>'
    
    if not re.search(kicker_pattern, html_content):
        errors.append(
            '❌ El primer <article> debe contener SOLO '
            '<span class="kicker">TEXTO</span>'
        )
    
    # ========================================================================
    # VALIDACIÓN 4: Segundo article vacío
    # ========================================================================
    # Patrón: </article> seguido de <article></article> seguido de <article>
    empty_article_pattern = r'</article>\s*<article>\s*</article>\s*<article>'
    
    if not re.search(empty_article_pattern, html_content):
        errors.append(
            '❌ Debe haber un <article></article> vacío como segundo article '
            '(separador entre kicker y contenido)'
        )
    
    # ========================================================================
    # VALIDACIÓN 5: Título principal debe ser H2, NO H1
    # ========================================================================
    if '<h1>' in html_content or '<h1 ' in html_content:
        errors.append(
            '❌ No se debe usar <h1>. '
            'El título principal debe ser <h2> según las reglas del CMS'
        )
    
    # ========================================================================
    # VALIDACIÓN 6: Contenido en el tercer article
    # ========================================================================
    # Extraer todos los articles
    articles = re.findall(r'<article>(.*?)</article>', html_content, re.DOTALL)
    
    if len(articles) >= 3:
        third_article = articles[2]
        # Eliminar espacios y saltos de línea para contar contenido real
        third_article_clean = third_article.strip()
        
        if len(third_article_clean) < 100:
            errors.append(
                '❌ El tercer <article> parece vacío o con muy poco contenido. '
                'Todo el contenido principal debe ir en el tercer article'
            )
    
    # ========================================================================
    # VALIDACIÓN 7: Kicker debe usar <span>, NO <div>
    # ========================================================================
    if '<div class="kicker">' in html_content:
        errors.append(
            '❌ El kicker debe usar <span class="kicker">, NO <div>. '
            'Esto es crítico para la compatibilidad con el CMS'
        )
    
    # ========================================================================
    # VALIDACIÓN 8: Verificar CSS con variables :root
    # ========================================================================
    if ':root' not in html_content:
        errors.append(
            '❌ Falta el CSS con variables :root. '
            'El CSS debe incluir todas las variables del design system'
        )
    
    # ========================================================================
    # VALIDACIÓN 9: Verificar que hay contenido significativo
    # ========================================================================
    # Contar palabras totales
    total_words = count_words_in_html(html_content)
    
    if total_words < 500:
        warnings.append(
            f"⚠️ El contenido tiene solo {total_words} palabras. "
            f"Lo recomendado es mínimo 800 palabras"
        )
    
    # ========================================================================
    # VALIDACIÓN 10: Verificar callout de Black Friday
    # ========================================================================
    if 'bf-callout' not in html_content:
        warnings.append(
            "⚠️ No se encontró el callout de Black Friday (.bf-callout). "
            "Es recomendable incluirlo según las directrices actuales"
        )
    
    # Determinar si es válido
    is_valid = len(errors) == 0
    
    return is_valid, errors, warnings


# ============================================================================
# FUNCIONES AUXILIARES
# ============================================================================

def strip_html_tags(html_content: str) -> str:
    """
    Elimina todos los tags HTML de un contenido, dejando solo el texto.
    
    Args:
        html_content (str): HTML con tags
        
    Returns:
        str: Texto sin tags HTML
        
    Examples:
        >>> strip_html_tags("<p>Hola <strong>mundo</strong></p>")
        'Hola mundo'
    """
    text = re.sub(r'<[^>]+>', '', html_content)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def get_heading_hierarchy(html_content: str) -> List[Dict[str, str]]:
    """
    Extrae la jerarquía de encabezados del HTML.
    
    Args:
        html_content (str): HTML completo
        
    Returns:
        List[Dict[str, str]]: Lista de diccionarios con level y text de cada encabezado
        
    Examples:
        >>> html = "<h1>Main</h1><h2>Sub1</h2><h3>Sub2</h3>"
        >>> hierarchy = get_heading_hierarchy(html)
        >>> len(hierarchy)
        3
        >>> hierarchy[0]
        {'level': 'h1', 'text': 'Main'}
    """
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        headings = []
        
        for h in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
            heading_text = h.get_text(strip=True)
            if heading_text:
                headings.append({
                    'level': h.name,
                    'text': heading_text
                })
        
        return headings
        
    except Exception:
        return []


def validate_word_count_target(html_content: str, target: int, tolerance: float = 0.05) -> Dict:
    """
    Valida si el conteo de palabras está dentro del objetivo con tolerancia.
    
    Args:
        html_content (str): HTML completo
        target (int): Número objetivo de palabras
        tolerance (float): Tolerancia como porcentaje (0.05 = 5%)
        
    Returns:
        Dict: Información sobre el conteo
        {
            'actual': int,           # Palabras actuales
            'target': int,           # Palabras objetivo
            'min_acceptable': int,   # Mínimo aceptable
            'max_acceptable': int,   # Máximo aceptable
            'within_range': bool,    # Si está en rango
            'difference': int,       # Diferencia con objetivo
            'percentage_diff': float # Diferencia en porcentaje
        }
        
    Examples:
        >>> html = "<p>" + " ".join(["word"] * 1000) + "</p>"
        >>> result = validate_word_count_target(html, 1000, 0.05)
        >>> result['within_range']
        True
    """
    actual = count_words_in_html(html_content)
    min_acceptable = int(target * (1 - tolerance))
    max_acceptable = int(target * (1 + tolerance))
    within_range = min_acceptable <= actual <= max_acceptable
    difference = actual - target
    percentage_diff = (difference / target * 100) if target > 0 else 0
    
    return {
        'actual': actual,
        'target': target,
        'min_acceptable': min_acceptable,
        'max_acceptable': max_acceptable,
        'within_range': within_range,
        'difference': difference,
        'percentage_diff': round(percentage_diff, 2)
    }


# ============================================================================
# FUNCIONES DE ANÁLISIS DE ENLACES
# ============================================================================

def analyze_links(html_content: str) -> Dict:
    """
    Analiza todos los enlaces del HTML y los categoriza.
    
    Args:
        html_content (str): HTML completo
        
    Returns:
        Dict: Análisis completo de enlaces
        {
            'total': int,
            'internal': List[Dict],  # {'href': str, 'text': str}
            'external': List[Dict],
            'broken': List[Dict],    # Enlaces sin href
            'internal_count': int,
            'external_count': int,
            'broken_count': int
        }
    """
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        links = soup.find_all('a')
        
        internal = []
        external = []
        broken = []
        
        for link in links:
            href = link.get('href', '')
            text = link.get_text(strip=True)
            
            link_data = {'href': href, 'text': text}
            
            if not href:
                broken.append(link_data)
            elif 'pccomponentes.com' in href or href.startswith('/'):
                internal.append(link_data)
            elif href.startswith('http'):
                external.append(link_data)
        
        return {
            'total': len(links),
            'internal': internal,
            'external': external,
            'broken': broken,
            'internal_count': len(internal),
            'external_count': len(external),
            'broken_count': len(broken)
        }
        
    except Exception:
        return {
            'total': 0,
            'internal': [],
            'external': [],
            'broken': [],
            'internal_count': 0,
            'external_count': 0,
            'broken_count': 0
        }


# ============================================================================
# CONSTANTES Y CONFIGURACIÓN
# ============================================================================

# Tolerancia por defecto para validación de longitud
DEFAULT_WORD_COUNT_TOLERANCE = 0.05  # 5%

# Longitud mínima recomendada para contenido
MIN_RECOMMENDED_WORD_COUNT = 800

# Número esperado de articles en estructura CMS
EXPECTED_ARTICLE_COUNT = 3
