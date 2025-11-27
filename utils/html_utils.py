"""
Utilidades HTML - PcComponentes Content Generator
Versión 4.3.0

Autor: PcComponentes - Product Discovery & Content
"""

import re
from typing import Dict, List, Tuple, Optional, Any
from html.parser import HTMLParser as BaseHTMLParser
from dataclasses import dataclass, field

__version__ = "4.3.0"

# ============================================================================
# VERIFICAR BEAUTIFULSOUP
# ============================================================================

try:
    from bs4 import BeautifulSoup
    _bs4_available = True
except ImportError:
    _bs4_available = False

def is_bs4_available() -> bool:
    """Verifica si BeautifulSoup está disponible."""
    return _bs4_available

# ============================================================================
# DATA CLASSES
# ============================================================================

@dataclass
class ExtractedContent:
    """Contenido extraído de HTML."""
    text: str = ""
    title: str = ""
    headings: List[Dict[str, str]] = field(default_factory=list)
    links: List[Dict[str, str]] = field(default_factory=list)
    word_count: int = 0
    meta: Dict[str, str] = field(default_factory=dict)

# ============================================================================
# HTML PARSER CLASS
# ============================================================================

class HTMLParser(BaseHTMLParser):
    """Parser HTML personalizado para extracción de contenido."""
    
    def __init__(self):
        super().__init__()
        self.text_content = []
        self.current_tag = None
        self.headings = []
        self.links = []
        self.in_script = False
        self.in_style = False
    
    def handle_starttag(self, tag: str, attrs: list):
        self.current_tag = tag
        if tag == 'script':
            self.in_script = True
        elif tag == 'style':
            self.in_style = True
        elif tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            self.headings.append({'level': tag, 'text': ''})
        elif tag == 'a':
            href = dict(attrs).get('href', '')
            if href:
                self.links.append({'href': href, 'text': ''})
    
    def handle_endtag(self, tag: str):
        if tag == 'script':
            self.in_script = False
        elif tag == 'style':
            self.in_style = False
        self.current_tag = None
    
    def handle_data(self, data: str):
        if self.in_script or self.in_style:
            return
        text = data.strip()
        if text:
            self.text_content.append(text)
            if self.headings and self.current_tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                self.headings[-1]['text'] += text
            if self.links and self.current_tag == 'a':
                self.links[-1]['text'] += text
    
    def get_text(self) -> str:
        return ' '.join(self.text_content)
    
    def get_headings(self) -> List[Dict]:
        return self.headings
    
    def get_links(self) -> List[Dict]:
        return self.links

# ============================================================================
# FUNCIONES DE PARSER
# ============================================================================

def get_html_parser() -> HTMLParser:
    """Retorna una nueva instancia del HTMLParser."""
    return HTMLParser()

def get_parser():
    """Retorna el parser de BeautifulSoup o 'html.parser'."""
    return 'html.parser'

def get_bs4_parser():
    """Alias para get_parser."""
    return get_parser()

# ============================================================================
# FUNCIONES DE CONTEO
# ============================================================================

def count_words_in_html(html_content: str) -> int:
    """Cuenta palabras en HTML excluyendo tags."""
    if not html_content:
        return 0
    text = re.sub(r'<[^>]+>', ' ', html_content)
    text = re.sub(r'&[a-zA-Z]+;', ' ', text)
    text = re.sub(r'&#\d+;', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return len(text.split()) if text else 0

def get_word_count(html_content: str) -> int:
    """Alias para count_words_in_html."""
    return count_words_in_html(html_content)

def strip_html_tags(html_content: str) -> str:
    """Elimina tags HTML dejando solo texto."""
    if not html_content:
        return ""
    text = re.sub(r'<[^>]+>', ' ', html_content)
    return re.sub(r'\s+', ' ', text).strip()

def strip_tags(html_content: str) -> str:
    """Alias para strip_html_tags."""
    return strip_html_tags(html_content)

# ============================================================================
# FUNCIONES DE EXTRACCIÓN
# ============================================================================

def extract_content_structure(html_content: str) -> Dict:
    """Extrae estructura del contenido HTML."""
    if not html_content:
        return {'word_count': 0, 'structure_valid': False}
    
    try:
        title_match = re.search(r'<h[12][^>]*>(.*?)</h[12]>', html_content, re.I | re.DOTALL)
        title = strip_html_tags(title_match.group(1)) if title_match else None
        
        headings = []
        for level, text in re.findall(r'<(h[1-6])[^>]*>(.*?)</\1>', html_content, re.I | re.DOTALL):
            headings.append({'level': level.lower(), 'text': strip_html_tags(text)})
        
        html_lower = html_content.lower()
        links = re.findall(r'href=["\']([^"\']+)["\']', html_content, re.I)
        
        return {
            'title': title,
            'headings': headings,
            'word_count': count_words_in_html(html_content),
            'has_table': '<table' in html_lower,
            'has_callout': 'callout' in html_lower,
            'has_faq': 'faq' in html_lower,
            'has_verdict': 'verdict' in html_lower,
            'internal_links_count': len([l for l in links if 'pccomponentes.com' in l]),
            'external_links_count': len([l for l in links if l.startswith('http') and 'pccomponentes.com' not in l]),
            'structure_valid': True
        }
    except Exception as e:
        return {'error': str(e), 'structure_valid': False}

def extract_content(html_content: str) -> ExtractedContent:
    """Extrae contenido estructurado de HTML."""
    result = ExtractedContent()
    
    if not html_content:
        return result
    
    result.text = strip_html_tags(html_content)
    result.word_count = count_words_in_html(html_content)
    
    # Título
    title_match = re.search(r'<title[^>]*>(.*?)</title>', html_content, re.I | re.DOTALL)
    result.title = strip_html_tags(title_match.group(1)) if title_match else ""
    
    # Headings
    for level, text in re.findall(r'<(h[1-6])[^>]*>(.*?)</\1>', html_content, re.I | re.DOTALL):
        result.headings.append({'level': level.lower(), 'text': strip_html_tags(text)})
    
    # Links
    for match in re.findall(r'<a[^>]+href=["\']([^"\']+)["\'][^>]*>(.*?)</a>', html_content, re.I | re.DOTALL):
        result.links.append({'href': match[0], 'text': strip_html_tags(match[1])})
    
    return result

def extract_text(html_content: str) -> str:
    """Extrae solo el texto de HTML."""
    return strip_html_tags(html_content)

def extract_meta_tags(html_content: str) -> Dict[str, str]:
    """Extrae meta tags de HTML."""
    meta = {}
    if not html_content:
        return meta
    
    for match in re.findall(r'<meta[^>]+>', html_content, re.I):
        name_match = re.search(r'name=["\']([^"\']+)["\']', match, re.I)
        property_match = re.search(r'property=["\']([^"\']+)["\']', match, re.I)
        content_match = re.search(r'content=["\']([^"\']+)["\']', match, re.I)
        
        key = (name_match or property_match)
        if key and content_match:
            meta[key.group(1)] = content_match.group(1)
    
    return meta

# ============================================================================
# FUNCIONES DE LIMPIEZA
# ============================================================================

def sanitize_html(html_content: str) -> str:
    """Sanitiza HTML eliminando scripts y styles."""
    if not html_content:
        return ""
    
    html = re.sub(r'<script[^>]*>.*?</script>', '', html_content, flags=re.DOTALL | re.I)
    html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL | re.I)
    html = re.sub(r'<!--.*?-->', '', html, flags=re.DOTALL)
    
    return html.strip()

def clean_html(html_content: str) -> str:
    """Alias para sanitize_html."""
    return sanitize_html(html_content)

# ============================================================================
# FUNCIONES DE VALIDACIÓN
# ============================================================================

def validate_html_structure(html_content: str) -> Dict[str, bool]:
    """Valida estructura HTML básica."""
    if not html_content:
        return {'has_article': False, 'kicker_uses_span': False, 'css_has_root': False, 'has_bf_callout': False, 'no_markdown': True}
    
    html_lower = html_content.lower()
    return {
        'has_article': '<article' in html_lower,
        'kicker_uses_span': 'class="kicker"' in html_lower or "class='kicker'" in html_lower,
        'css_has_root': ':root' in html_content,
        'has_bf_callout': 'bf-callout' in html_lower,
        'no_markdown': not any(md in html_content for md in ['```', '**', '## '])
    }

def validate_cms_structure(html_content: str) -> Tuple[bool, List[str], List[str]]:
    """Valida que el HTML cumpla con requisitos del CMS."""
    errors = []
    warnings = []
    
    if not html_content:
        return False, ["❌ El contenido HTML está vacío"], []
    
    html_lower = html_content.lower()
    
    article_count = html_lower.count('<article')
    if article_count < 3:
        errors.append(f"❌ Se encontraron {article_count} tags <article>, deben ser mínimo 3")
    elif article_count > 3:
        warnings.append(f"⚠️ Se encontraron {article_count} tags <article>, lo normal son 3")
    
    has_div_kicker = '<div class="kicker">' in html_lower
    has_span_kicker = '<span class="kicker">' in html_lower
    if has_div_kicker and not has_span_kicker:
        errors.append("❌ El kicker usa <div> pero debe usar <span>")
    
    if '<h1' in html_lower:
        errors.append("❌ Se encontró <h1> pero el CMS usa H2 como título principal")
    if '<h2' not in html_lower:
        warnings.append("⚠️ No se encontró ningún <h2> para el título principal")
    
    if 'contentgenerator__main' not in html_lower and 'content-generator' not in html_lower:
        warnings.append("⚠️ No se encontró article principal")
    if 'faq' not in html_lower:
        warnings.append("⚠️ No se encontró sección de FAQs")
    if 'verdict' not in html_lower:
        warnings.append("⚠️ No se encontró sección de veredicto")
    
    word_count = count_words_in_html(html_content)
    if word_count < 300:
        errors.append(f"❌ Solo {word_count} palabras. Mínimo: 500")
    elif word_count < 500:
        warnings.append(f"⚠️ {word_count} palabras. Recomendado: 800+")
    
    if any(md in html_content for md in ['```', '**', '## ']):
        warnings.append("⚠️ Se detectó posible Markdown residual")
    
    return len(errors) == 0, errors, warnings

def validate_word_count_target(html_content: str, target: int, tolerance: float = 0.05) -> Dict:
    """Valida si el word count está dentro del rango objetivo."""
    actual = count_words_in_html(html_content)
    min_ok = int(target * (1 - tolerance))
    max_ok = int(target * (1 + tolerance))
    diff = actual - target
    pct = (diff / target * 100) if target > 0 else 0
    
    return {
        'actual': actual,
        'target': target,
        'min_acceptable': min_ok,
        'max_acceptable': max_ok,
        'within_range': min_ok <= actual <= max_ok,
        'difference': diff,
        'percentage_diff': round(pct, 2)
    }

# ============================================================================
# FUNCIONES DE ANÁLISIS DE ENLACES
# ============================================================================

def analyze_links(html_content: str) -> Dict:
    """Analiza enlaces del HTML."""
    if not html_content:
        return {'total': 0, 'internal': [], 'external': [], 'pdp': [], 'blog': []}
    
    matches = re.findall(r'<a[^>]+href=["\']([^"\']+)["\'][^>]*>(.*?)</a>', html_content, re.I | re.DOTALL)
    
    internal, external, pdp, blog = [], [], [], []
    
    for url, anchor in matches:
        info = {'url': url, 'anchor': strip_html_tags(anchor)}
        if 'pccomponentes.com' in url:
            internal.append(info)
            if '/blog/' in url:
                blog.append(info)
            elif any(p in url for p in ['/producto/', '/p/']):
                pdp.append(info)
        elif url.startswith('http'):
            external.append(info)
    
    return {
        'total': len(matches),
        'internal': internal,
        'external': external,
        'pdp': pdp,
        'blog': blog,
        'internal_count': len(internal),
        'external_count': len(external)
    }

def get_heading_hierarchy(html_content: str) -> List[Dict[str, str]]:
    """Extrae jerarquía de encabezados."""
    if not html_content:
        return []
    
    return [
        {'level': level.lower(), 'text': strip_html_tags(text)}
        for level, text in re.findall(r'<(h[1-6])[^>]*>(.*?)</\1>', html_content, re.I | re.DOTALL)
    ]

# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    '__version__',
    # Parser
    'HTMLParser',
    'get_html_parser',
    'get_parser',
    'get_bs4_parser',
    'is_bs4_available',
    # Data classes
    'ExtractedContent',
    # Conteo
    'count_words_in_html',
    'get_word_count',
    'strip_html_tags',
    'strip_tags',
    # Extracción
    'extract_content_structure',
    'extract_content',
    'extract_text',
    'extract_meta_tags',
    # Limpieza
    'sanitize_html',
    'clean_html',
    # Validación
    'validate_html_structure',
    'validate_cms_structure',
    'validate_word_count_target',
    # Enlaces
    'analyze_links',
    'get_heading_hierarchy',
]
