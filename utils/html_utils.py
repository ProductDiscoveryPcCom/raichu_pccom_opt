"""
HTML Utilities - PcComponentes Content Generator
Versión 4.2.0

Utilidades para manipulación y procesamiento de HTML.
Incluye parser consistente de BeautifulSoup con fallbacks automáticos.

Este módulo proporciona:
- Parser HTML consistente con detección automática de backend
- Extracción de contenido y metadatos
- Sanitización y limpieza de HTML
- Validación de estructura HTML
- Conversión entre formatos

IMPORTANTE: Este módulo usa un parser consistente en todo el código.
La prioridad de parsers es: lxml > html.parser > html5lib

Autor: PcComponentes - Product Discovery & Content
"""

import re
import html
import logging
from typing import Dict, List, Optional, Any, Tuple, Union, Set
from dataclasses import dataclass, field
from enum import Enum

# Configurar logging
logger = logging.getLogger(__name__)

# ============================================================================
# VERSIÓN Y CONSTANTES
# ============================================================================

__version__ = "4.2.0"

# Prioridad de parsers (de más rápido a más compatible)
PARSER_PRIORITY = ['lxml', 'html.parser', 'html5lib']

# Parser por defecto si no se detecta ninguno
DEFAULT_PARSER = 'html.parser'

# Tags que se consideran contenido principal
CONTENT_TAGS = ['article', 'main', 'section', 'div']

# Selectores de contenido (orden de prioridad)
CONTENT_SELECTORS = [
    'article',
    'main',
    '[role="main"]',
    '.content',
    '.article-content',
    '.post-content',
    '.entry-content',
    '#content',
    '#main-content',
    '.main-content',
]

# Tags a eliminar para extracción de texto
REMOVE_TAGS = [
    'script',
    'style',
    'noscript',
    'iframe',
    'svg',
    'canvas',
    'video',
    'audio',
    'map',
    'object',
    'embed',
]

# Tags de navegación/UI a eliminar
REMOVE_UI_TAGS = [
    'nav',
    'header',
    'footer',
    'aside',
    'menu',
    'menuitem',
]

# Clases CSS a eliminar
REMOVE_CLASSES = [
    'sidebar',
    'navigation',
    'nav',
    'menu',
    'footer',
    'header',
    'ads',
    'advertisement',
    'banner',
    'social',
    'social-share',
    'share-buttons',
    'comments',
    'comment-section',
    'related-posts',
    'related-articles',
    'breadcrumb',
    'breadcrumbs',
    'pagination',
    'cookie',
    'popup',
    'modal',
]

# IDs a eliminar
REMOVE_IDS = [
    'sidebar',
    'navigation',
    'nav',
    'menu',
    'footer',
    'header',
    'comments',
    'ads',
    'cookie-banner',
]

# Tags de estructura permitidos para contenido limpio
ALLOWED_STRUCTURE_TAGS = [
    'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
    'ul', 'ol', 'li',
    'table', 'thead', 'tbody', 'tr', 'th', 'td',
    'blockquote', 'pre', 'code',
    'a', 'strong', 'em', 'b', 'i', 'u', 's',
    'br', 'hr',
    'div', 'span', 'article', 'section',
    'figure', 'figcaption', 'img',
]

# Atributos permitidos por tag
ALLOWED_ATTRIBUTES = {
    'a': ['href', 'title', 'target', 'rel'],
    'img': ['src', 'alt', 'title', 'width', 'height'],
    'table': ['class'],
    'th': ['colspan', 'rowspan'],
    'td': ['colspan', 'rowspan'],
    'div': ['class', 'id'],
    'span': ['class'],
    'p': ['class'],
    'h1': ['class', 'id'],
    'h2': ['class', 'id'],
    'h3': ['class', 'id'],
    'h4': ['class', 'id'],
    'h5': ['class', 'id'],
    'h6': ['class', 'id'],
    'ul': ['class'],
    'ol': ['class'],
    'li': ['class'],
    'blockquote': ['class', 'cite'],
    'pre': ['class'],
    'code': ['class'],
}

# Longitudes máximas
MAX_HTML_LENGTH = 10 * 1024 * 1024  # 10 MB
MAX_TEXT_LENGTH = 1 * 1024 * 1024  # 1 MB


# ============================================================================
# DETECCIÓN DE PARSER
# ============================================================================

_available_parsers: List[str] = []
_selected_parser: Optional[str] = None
_bs4_available: bool = False


def _detect_available_parsers() -> List[str]:
    """
    Detecta los parsers de BeautifulSoup disponibles.
    
    Returns:
        Lista de parsers disponibles ordenados por prioridad
    """
    global _available_parsers, _bs4_available
    
    if _available_parsers:
        return _available_parsers
    
    try:
        from bs4 import BeautifulSoup
        _bs4_available = True
    except ImportError:
        logger.warning("BeautifulSoup4 no disponible")
        _bs4_available = False
        return []
    
    available = []
    
    # Probar lxml
    try:
        BeautifulSoup('<html></html>', 'lxml')
        available.append('lxml')
        logger.debug("Parser lxml disponible")
    except Exception:
        pass
    
    # html.parser siempre está disponible con Python
    try:
        BeautifulSoup('<html></html>', 'html.parser')
        available.append('html.parser')
        logger.debug("Parser html.parser disponible")
    except Exception:
        pass
    
    # Probar html5lib
    try:
        BeautifulSoup('<html></html>', 'html5lib')
        available.append('html5lib')
        logger.debug("Parser html5lib disponible")
    except Exception:
        pass
    
    _available_parsers = available
    logger.info(f"Parsers HTML disponibles: {available}")
    
    return available


def get_parser() -> str:
    """
    Obtiene el parser óptimo disponible.
    
    Returns:
        Nombre del parser a usar
    """
    global _selected_parser
    
    if _selected_parser:
        return _selected_parser
    
    available = _detect_available_parsers()
    
    if not available:
        logger.warning("No hay parsers disponibles, usando html.parser por defecto")
        _selected_parser = DEFAULT_PARSER
        return _selected_parser
    
    # Seleccionar por prioridad
    for parser in PARSER_PRIORITY:
        if parser in available:
            _selected_parser = parser
            logger.info(f"Parser HTML seleccionado: {parser}")
            return parser
    
    # Fallback al primero disponible
    _selected_parser = available[0]
    return _selected_parser


def is_bs4_available() -> bool:
    """Verifica si BeautifulSoup4 está disponible."""
    _detect_available_parsers()
    return _bs4_available


def get_available_parsers() -> List[str]:
    """Retorna lista de parsers disponibles."""
    return _detect_available_parsers()


# ============================================================================
# EXCEPCIONES
# ============================================================================

class HTMLError(Exception):
    """Excepción base para errores de HTML."""
    
    def __init__(self, message: str, details: Optional[Dict] = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}


class HTMLParseError(HTMLError):
    """Error al parsear HTML."""
    pass


class HTMLSanitizeError(HTMLError):
    """Error al sanitizar HTML."""
    pass


class HTMLExtractionError(HTMLError):
    """Error al extraer contenido."""
    pass


# ============================================================================
# DATA CLASSES
# ============================================================================

@dataclass
class ParsedHTML:
    """Resultado de parseo de HTML."""
    soup: Any  # BeautifulSoup object
    parser: str
    original_length: int
    has_errors: bool = False
    errors: List[str] = field(default_factory=list)


@dataclass
class ExtractedContent:
    """Contenido extraído de HTML."""
    text: str
    title: str = ""
    meta_description: str = ""
    headings: List[Dict[str, str]] = field(default_factory=list)
    links: List[Dict[str, str]] = field(default_factory=list)
    images: List[Dict[str, str]] = field(default_factory=list)
    word_count: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte a diccionario."""
        return {
            'text': self.text,
            'title': self.title,
            'meta_description': self.meta_description,
            'headings': self.headings,
            'links': self.links,
            'images': self.images,
            'word_count': self.word_count,
        }


@dataclass
class HTMLValidationResult:
    """Resultado de validación HTML."""
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    structure: Dict[str, Any] = field(default_factory=dict)


# ============================================================================
# CLASE PRINCIPAL: HTMLParser
# ============================================================================

class HTMLParser:
    """
    Parser HTML consistente con BeautifulSoup.
    
    Características:
    - Detección automática del mejor parser disponible
    - Parser consistente en todas las operaciones
    - Extracción de contenido optimizada
    - Sanitización de HTML
    - Manejo robusto de errores
    
    Example:
        >>> parser = HTMLParser()
        >>> content = parser.extract_content(html_string)
        >>> clean_html = parser.sanitize(html_string)
    """
    
    def __init__(self, parser: Optional[str] = None):
        """
        Inicializa el parser HTML.
        
        Args:
            parser: Parser específico a usar (None = auto-detectar)
        """
        self._parser = parser or get_parser()
        self._bs4_available = is_bs4_available()
        
        if not self._bs4_available:
            logger.warning("BeautifulSoup no disponible - funcionalidad limitada")
    
    def parse(self, html: str) -> ParsedHTML:
        """
        Parsea HTML y retorna objeto BeautifulSoup.
        
        Args:
            html: String HTML a parsear
            
        Returns:
            ParsedHTML con el soup y metadatos
            
        Raises:
            HTMLParseError: Si hay error de parseo
        """
        if not html:
            raise HTMLParseError("HTML vacío")
        
        if len(html) > MAX_HTML_LENGTH:
            raise HTMLParseError(f"HTML excede tamaño máximo ({MAX_HTML_LENGTH} bytes)")
        
        if not self._bs4_available:
            raise HTMLParseError("BeautifulSoup no disponible")
        
        from bs4 import BeautifulSoup
        
        errors = []
        
        try:
            soup = BeautifulSoup(html, self._parser)
            
            return ParsedHTML(
                soup=soup,
                parser=self._parser,
                original_length=len(html),
                has_errors=len(errors) > 0,
                errors=errors
            )
        except Exception as e:
            raise HTMLParseError(f"Error parseando HTML: {e}")
    
    def extract_content(
        self,
        html: str,
        include_links: bool = True,
        include_images: bool = True,
        remove_navigation: bool = True
    ) -> ExtractedContent:
        """
        Extrae contenido principal de HTML.
        
        Args:
            html: String HTML
            include_links: Incluir enlaces extraídos
            include_images: Incluir imágenes extraídas
            remove_navigation: Eliminar elementos de navegación
            
        Returns:
            ExtractedContent con el contenido extraído
        """
        if not self._bs4_available:
            # Fallback sin BeautifulSoup
            return self._extract_content_regex(html)
        
        parsed = self.parse(html)
        soup = parsed.soup
        
        # Extraer título
        title = self._extract_title(soup)
        
        # Extraer meta description
        meta_description = self._extract_meta_description(soup)
        
        # Eliminar elementos no deseados
        self._remove_unwanted_elements(soup, remove_navigation)
        
        # Buscar contenido principal
        content_element = self._find_content_element(soup)
        
        # Extraer texto
        text = self._extract_text(content_element or soup)
        
        # Extraer headings
        headings = self._extract_headings(content_element or soup)
        
        # Extraer enlaces
        links = []
        if include_links:
            links = self._extract_links(content_element or soup)
        
        # Extraer imágenes
        images = []
        if include_images:
            images = self._extract_images(content_element or soup)
        
        # Contar palabras
        word_count = len(text.split())
        
        return ExtractedContent(
            text=text,
            title=title,
            meta_description=meta_description,
            headings=headings,
            links=links,
            images=images,
            word_count=word_count
        )
    
    def extract_text(self, html: str) -> str:
        """
        Extrae solo el texto de HTML.
        
        Args:
            html: String HTML
            
        Returns:
            Texto extraído
        """
        content = self.extract_content(html, include_links=False, include_images=False)
        return content.text
    
    def sanitize(
        self,
        html: str,
        allowed_tags: Optional[List[str]] = None,
        allowed_attributes: Optional[Dict[str, List[str]]] = None,
        strip_comments: bool = True,
        strip_cdata: bool = True
    ) -> str:
        """
        Sanitiza HTML eliminando tags y atributos no permitidos.
        
        Args:
            html: String HTML a sanitizar
            allowed_tags: Tags permitidos (None = usar defaults)
            allowed_attributes: Atributos permitidos por tag
            strip_comments: Eliminar comentarios HTML
            strip_cdata: Eliminar secciones CDATA
            
        Returns:
            HTML sanitizado
        """
        if not html:
            return ""
        
        if not self._bs4_available:
            return self._sanitize_regex(html)
        
        allowed_tags = allowed_tags or ALLOWED_STRUCTURE_TAGS
        allowed_attributes = allowed_attributes or ALLOWED_ATTRIBUTES
        
        parsed = self.parse(html)
        soup = parsed.soup
        
        # Eliminar comentarios
        if strip_comments:
            from bs4 import Comment
            for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
                comment.extract()
        
        # Eliminar CDATA
        if strip_cdata:
            from bs4 import CData
            for cdata in soup.find_all(string=lambda text: isinstance(text, CData)):
                cdata.extract()
        
        # Procesar todos los tags
        for tag in soup.find_all(True):
            if tag.name not in allowed_tags:
                # Reemplazar tag no permitido con su contenido
                tag.unwrap()
            else:
                # Limpiar atributos
                tag_allowed_attrs = allowed_attributes.get(tag.name, [])
                attrs_to_remove = [
                    attr for attr in tag.attrs
                    if attr not in tag_allowed_attrs
                ]
                for attr in attrs_to_remove:
                    del tag[attr]
        
        return str(soup)
    
    def clean_for_display(self, html: str) -> str:
        """
        Limpia HTML para mostrar en UI.
        
        Args:
            html: String HTML
            
        Returns:
            HTML limpio para display
        """
        if not html:
            return ""
        
        if not self._bs4_available:
            return html
        
        parsed = self.parse(html)
        soup = parsed.soup
        
        # Eliminar scripts y styles
        for tag in soup.find_all(['script', 'style', 'noscript']):
            tag.decompose()
        
        # Limpiar atributos peligrosos
        for tag in soup.find_all(True):
            # Eliminar event handlers
            attrs_to_remove = [
                attr for attr in tag.attrs
                if attr.startswith('on') or attr in ['style']
            ]
            for attr in attrs_to_remove:
                del tag[attr]
            
            # Limpiar href javascript
            if tag.name == 'a' and tag.get('href', '').lower().startswith('javascript:'):
                tag['href'] = '#'
        
        return str(soup)
    
    def validate(self, html: str) -> HTMLValidationResult:
        """
        Valida estructura HTML.
        
        Args:
            html: String HTML a validar
            
        Returns:
            HTMLValidationResult con el resultado
        """
        errors = []
        warnings = []
        structure = {}
        
        if not html:
            return HTMLValidationResult(
                is_valid=False,
                errors=["HTML vacío"]
            )
        
        if not self._bs4_available:
            # Validación básica sin BeautifulSoup
            return HTMLValidationResult(
                is_valid=True,
                warnings=["BeautifulSoup no disponible - validación limitada"]
            )
        
        try:
            parsed = self.parse(html)
            soup = parsed.soup
            
            # Verificar estructura básica
            if not soup.find('html'):
                warnings.append("Falta tag <html>")
            
            if not soup.find('head'):
                warnings.append("Falta tag <head>")
            
            if not soup.find('body'):
                warnings.append("Falta tag <body>")
            
            # Verificar título
            title = soup.find('title')
            if not title:
                warnings.append("Falta tag <title>")
            elif not title.string or not title.string.strip():
                warnings.append("Tag <title> vacío")
            
            # Verificar meta description
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            if not meta_desc:
                warnings.append("Falta meta description")
            
            # Contar headings
            h1_count = len(soup.find_all('h1'))
            if h1_count == 0:
                warnings.append("No hay H1 en la página")
            elif h1_count > 1:
                warnings.append(f"Múltiples H1 ({h1_count}) - debería haber solo 1")
            
            # Verificar imágenes sin alt
            imgs_without_alt = soup.find_all('img', alt=False)
            imgs_without_alt += soup.find_all('img', alt='')
            if imgs_without_alt:
                warnings.append(f"{len(imgs_without_alt)} imágenes sin atributo alt")
            
            # Verificar enlaces rotos (javascript:void)
            bad_links = soup.find_all('a', href=re.compile(r'^javascript:', re.I))
            if bad_links:
                warnings.append(f"{len(bad_links)} enlaces con javascript:")
            
            # Estructura
            structure = {
                'has_html': bool(soup.find('html')),
                'has_head': bool(soup.find('head')),
                'has_body': bool(soup.find('body')),
                'has_title': bool(title),
                'has_meta_description': bool(meta_desc),
                'h1_count': h1_count,
                'h2_count': len(soup.find_all('h2')),
                'h3_count': len(soup.find_all('h3')),
                'link_count': len(soup.find_all('a')),
                'image_count': len(soup.find_all('img')),
            }
            
            is_valid = len(errors) == 0
            
            return HTMLValidationResult(
                is_valid=is_valid,
                errors=errors,
                warnings=warnings,
                structure=structure
            )
        
        except Exception as e:
            return HTMLValidationResult(
                is_valid=False,
                errors=[f"Error validando HTML: {e}"]
            )
    
    def minify(self, html: str) -> str:
        """
        Minifica HTML eliminando espacios innecesarios.
        
        Args:
            html: String HTML
            
        Returns:
            HTML minificado
        """
        if not html:
            return ""
        
        # Eliminar comentarios
        html = re.sub(r'<!--.*?-->', '', html, flags=re.DOTALL)
        
        # Eliminar espacios entre tags
        html = re.sub(r'>\s+<', '><', html)
        
        # Eliminar espacios múltiples
        html = re.sub(r'\s+', ' ', html)
        
        # Eliminar espacios al inicio/final de líneas
        html = re.sub(r'^\s+|\s+$', '', html, flags=re.MULTILINE)
        
        return html.strip()
    
    def prettify(self, html: str, indent: int = 2) -> str:
        """
        Formatea HTML con indentación.
        
        Args:
            html: String HTML
            indent: Espacios de indentación
            
        Returns:
            HTML formateado
        """
        if not html:
            return ""
        
        if not self._bs4_available:
            return html
        
        try:
            parsed = self.parse(html)
            return parsed.soup.prettify(formatter="html")
        except Exception:
            return html
    
    # ========================================================================
    # MÉTODOS PRIVADOS - EXTRACCIÓN
    # ========================================================================
    
    def _extract_title(self, soup) -> str:
        """Extrae el título de la página."""
        # Intentar tag title
        title_tag = soup.find('title')
        if title_tag and title_tag.string:
            return title_tag.string.strip()
        
        # Intentar og:title
        og_title = soup.find('meta', property='og:title')
        if og_title and og_title.get('content'):
            return og_title['content'].strip()
        
        # Intentar H1
        h1 = soup.find('h1')
        if h1:
            return h1.get_text(strip=True)
        
        return ""
    
    def _extract_meta_description(self, soup) -> str:
        """Extrae la meta description."""
        # Meta description estándar
        meta = soup.find('meta', attrs={'name': 'description'})
        if meta and meta.get('content'):
            return meta['content'].strip()
        
        # og:description
        og_desc = soup.find('meta', property='og:description')
        if og_desc and og_desc.get('content'):
            return og_desc['content'].strip()
        
        return ""
    
    def _remove_unwanted_elements(self, soup, remove_navigation: bool = True) -> None:
        """Elimina elementos no deseados del soup."""
        # Eliminar tags de script/style
        for tag_name in REMOVE_TAGS:
            for tag in soup.find_all(tag_name):
                tag.decompose()
        
        # Eliminar navegación si se solicita
        if remove_navigation:
            for tag_name in REMOVE_UI_TAGS:
                for tag in soup.find_all(tag_name):
                    tag.decompose()
        
        # Eliminar por clase
        for class_name in REMOVE_CLASSES:
            for tag in soup.find_all(class_=re.compile(class_name, re.I)):
                tag.decompose()
        
        # Eliminar por ID
        for id_name in REMOVE_IDS:
            tag = soup.find(id=re.compile(id_name, re.I))
            if tag:
                tag.decompose()
    
    def _find_content_element(self, soup):
        """Encuentra el elemento de contenido principal."""
        for selector in CONTENT_SELECTORS:
            try:
                element = soup.select_one(selector)
                if element and len(element.get_text(strip=True)) > 100:
                    return element
            except Exception:
                continue
        
        # Fallback: buscar el div con más texto
        best_element = None
        best_length = 0
        
        for div in soup.find_all(['article', 'main', 'div']):
            text = div.get_text(strip=True)
            if len(text) > best_length:
                best_length = len(text)
                best_element = div
        
        return best_element
    
    def _extract_text(self, element) -> str:
        """Extrae texto limpio de un elemento."""
        if element is None:
            return ""
        
        # Obtener texto
        text = element.get_text(separator=' ', strip=True)
        
        # Limpiar espacios múltiples
        text = re.sub(r'\s+', ' ', text)
        
        # Eliminar caracteres de control
        text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)
        
        return text.strip()
    
    def _extract_headings(self, element) -> List[Dict[str, str]]:
        """Extrae headings del elemento."""
        headings = []
        
        for level in range(1, 7):
            for heading in element.find_all(f'h{level}'):
                text = heading.get_text(strip=True)
                if text:
                    headings.append({
                        'level': level,
                        'tag': f'h{level}',
                        'text': text,
                        'id': heading.get('id', ''),
                    })
        
        return headings
    
    def _extract_links(self, element) -> List[Dict[str, str]]:
        """Extrae enlaces del elemento."""
        links = []
        seen_hrefs = set()
        
        for link in element.find_all('a', href=True):
            href = link['href']
            
            # Saltar duplicados
            if href in seen_hrefs:
                continue
            seen_hrefs.add(href)
            
            # Saltar javascript y anclas vacías
            if href.startswith(('javascript:', '#', 'mailto:', 'tel:')):
                continue
            
            text = link.get_text(strip=True)
            
            links.append({
                'href': href,
                'text': text or href,
                'title': link.get('title', ''),
                'rel': link.get('rel', []),
            })
        
        return links
    
    def _extract_images(self, element) -> List[Dict[str, str]]:
        """Extrae imágenes del elemento."""
        images = []
        seen_srcs = set()
        
        for img in element.find_all('img'):
            src = img.get('src') or img.get('data-src', '')
            
            if not src or src in seen_srcs:
                continue
            seen_srcs.add(src)
            
            images.append({
                'src': src,
                'alt': img.get('alt', ''),
                'title': img.get('title', ''),
                'width': img.get('width', ''),
                'height': img.get('height', ''),
            })
        
        return images
    
    # ========================================================================
    # MÉTODOS PRIVADOS - FALLBACKS SIN BS4
    # ========================================================================
    
    def _extract_content_regex(self, html: str) -> ExtractedContent:
        """Extrae contenido usando regex (fallback sin BeautifulSoup)."""
        # Eliminar scripts y styles
        html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
        html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL | re.IGNORECASE)
        
        # Extraer título
        title_match = re.search(r'<title[^>]*>(.*?)</title>', html, re.IGNORECASE | re.DOTALL)
        title = title_match.group(1).strip() if title_match else ""
        
        # Extraer meta description
        meta_match = re.search(
            r'<meta[^>]*name=["\']description["\'][^>]*content=["\']([^"\']*)["\']',
            html, re.IGNORECASE
        )
        meta_description = meta_match.group(1).strip() if meta_match else ""
        
        # Eliminar todos los tags
        text = re.sub(r'<[^>]+>', ' ', html)
        
        # Decodificar entidades HTML
        text = html.unescape(text)
        
        # Limpiar espacios
        text = re.sub(r'\s+', ' ', text).strip()
        
        return ExtractedContent(
            text=text,
            title=title,
            meta_description=meta_description,
            word_count=len(text.split())
        )
    
    def _sanitize_regex(self, html: str) -> str:
        """Sanitiza HTML usando regex (fallback sin BeautifulSoup)."""
        # Eliminar scripts
        html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
        
        # Eliminar styles
        html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL | re.IGNORECASE)
        
        # Eliminar comentarios
        html = re.sub(r'<!--.*?-->', '', html, flags=re.DOTALL)
        
        # Eliminar event handlers
        html = re.sub(r'\s+on\w+\s*=\s*["\'][^"\']*["\']', '', html, flags=re.IGNORECASE)
        
        # Eliminar javascript: en href
        html = re.sub(r'href\s*=\s*["\']javascript:[^"\']*["\']', 'href="#"', html, flags=re.IGNORECASE)
        
        return html


# ============================================================================
# INSTANCIA GLOBAL
# ============================================================================

_default_parser: Optional[HTMLParser] = None


def get_html_parser() -> HTMLParser:
    """
    Obtiene el parser HTML global.
    
    Returns:
        Instancia de HTMLParser
    """
    global _default_parser
    
    if _default_parser is None:
        _default_parser = HTMLParser()
    
    return _default_parser


def reset_html_parser() -> None:
    """Resetea el parser HTML global."""
    global _default_parser
    _default_parser = None


# ============================================================================
# FUNCIONES DE CONVENIENCIA
# ============================================================================

def parse_html(html: str) -> ParsedHTML:
    """
    Parsea HTML.
    
    Args:
        html: String HTML
        
    Returns:
        ParsedHTML con el resultado
    """
    return get_html_parser().parse(html)


def extract_content(html: str) -> ExtractedContent:
    """
    Extrae contenido de HTML.
    
    Args:
        html: String HTML
        
    Returns:
        ExtractedContent con el contenido
    """
    return get_html_parser().extract_content(html)


def extract_text(html: str) -> str:
    """
    Extrae texto de HTML.
    
    Args:
        html: String HTML
        
    Returns:
        Texto extraído
    """
    return get_html_parser().extract_text(html)


def sanitize_html(html: str) -> str:
    """
    Sanitiza HTML.
    
    Args:
        html: String HTML
        
    Returns:
        HTML sanitizado
    """
    return get_html_parser().sanitize(html)


def clean_html(html: str) -> str:
    """
    Limpia HTML para display.
    
    Args:
        html: String HTML
        
    Returns:
        HTML limpio
    """
    return get_html_parser().clean_for_display(html)


def validate_html(html: str) -> HTMLValidationResult:
    """
    Valida estructura HTML.
    
    Args:
        html: String HTML
        
    Returns:
        HTMLValidationResult
    """
    return get_html_parser().validate(html)


def minify_html(html: str) -> str:
    """
    Minifica HTML.
    
    Args:
        html: String HTML
        
    Returns:
        HTML minificado
    """
    return get_html_parser().minify(html)


def prettify_html(html: str) -> str:
    """
    Formatea HTML con indentación.
    
    Args:
        html: String HTML
        
    Returns:
        HTML formateado
    """
    return get_html_parser().prettify(html)


def strip_tags(html: str) -> str:
    """
    Elimina todos los tags HTML.
    
    Args:
        html: String HTML
        
    Returns:
        Texto sin tags
    """
    if not html:
        return ""
    
    # Eliminar tags
    text = re.sub(r'<[^>]+>', '', html)
    
    # Decodificar entidades
    text = html_module_unescape(text)
    
    # Limpiar espacios
    text = re.sub(r'\s+', ' ', text)
    
    return text.strip()


def html_module_unescape(text: str) -> str:
    """
    Decodifica entidades HTML.
    
    Args:
        text: Texto con entidades
        
    Returns:
        Texto decodificado
    """
    return html.unescape(text)


def escape_html(text: str) -> str:
    """
    Escapa caracteres especiales HTML.
    
    Args:
        text: Texto a escapar
        
    Returns:
        Texto escapado
    """
    return html.escape(text)


def get_word_count(html: str) -> int:
    """
    Cuenta palabras en HTML.
    
    Args:
        html: String HTML
        
    Returns:
        Número de palabras
    """
    text = extract_text(html)
    return len(text.split())


def extract_meta_tags(html: str) -> Dict[str, str]:
    """
    Extrae todos los meta tags.
    
    Args:
        html: String HTML
        
    Returns:
        Dict con meta tags
    """
    parser = get_html_parser()
    
    if not is_bs4_available():
        return {}
    
    try:
        parsed = parser.parse(html)
        soup = parsed.soup
        
        meta_tags = {}
        
        # Title
        title = soup.find('title')
        if title:
            meta_tags['title'] = title.string.strip() if title.string else ''
        
        # Meta tags estándar
        for meta in soup.find_all('meta'):
            name = meta.get('name') or meta.get('property')
            content = meta.get('content')
            
            if name and content:
                meta_tags[name] = content
        
        # Canonical
        canonical = soup.find('link', rel='canonical')
        if canonical and canonical.get('href'):
            meta_tags['canonical'] = canonical['href']
        
        return meta_tags
    
    except Exception:
        return {}


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    # Versión
    '__version__',
    
    # Detección de parser
    'get_parser',
    'is_bs4_available',
    'get_available_parsers',
    
    # Excepciones
    'HTMLError',
    'HTMLParseError',
    'HTMLSanitizeError',
    'HTMLExtractionError',
    
    # Data classes
    'ParsedHTML',
    'ExtractedContent',
    'HTMLValidationResult',
    
    # Clase principal
    'HTMLParser',
    
    # Parser global
    'get_html_parser',
    'reset_html_parser',
    
    # Funciones de conveniencia
    'parse_html',
    'extract_content',
    'extract_text',
    'sanitize_html',
    'clean_html',
    'validate_html',
    'minify_html',
    'prettify_html',
    'strip_tags',
    'escape_html',
    'get_word_count',
    'extract_meta_tags',
    
    # Constantes
    'CONTENT_SELECTORS',
    'ALLOWED_STRUCTURE_TAGS',
    'ALLOWED_ATTRIBUTES',
]
