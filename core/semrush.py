"""
SEMrush Integration - PcComponentes Content Generator
Versión 4.2.0

Integración completa con SEMrush API para:
- Obtener URLs competidoras para una keyword
- Analizar contenido de competidores
- Extraer métricas SEO relevantes

Autor: PcComponentes - Product Discovery & Content
"""

import requests
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import time
import re

# BeautifulSoup para scraping de contenido
from bs4 import BeautifulSoup


# ============================================================================
# CONFIGURACIÓN Y CONSTANTES
# ============================================================================

# Endpoints de SEMrush API
SEMRUSH_API_BASE = "https://api.semrush.com"
SEMRUSH_ORGANIC_RESULTS = f"{SEMRUSH_API_BASE}/"

# Databases disponibles (España por defecto)
SEMRUSH_DATABASES = {
    'es': 'es',      # España
    'us': 'us',      # Estados Unidos
    'uk': 'uk',      # Reino Unido
    'fr': 'fr',      # Francia
    'de': 'de',      # Alemania
    'it': 'it',      # Italia
    'pt': 'pt',      # Portugal
    'mx': 'mx',      # México
    'ar': 'ar',      # Argentina
    'co': 'co',      # Colombia
}

# Límites y configuración
MAX_COMPETITORS = 10
DEFAULT_COMPETITORS = 5
REQUEST_TIMEOUT = 30
RATE_LIMIT_DELAY = 0.5  # Segundos entre requests

# User Agent para scraping de contenido
DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)


# ============================================================================
# DATA CLASSES
# ============================================================================

@dataclass
class CompetitorData:
    """
    Datos de un competidor obtenidos de SEMrush y scraping.
    
    Attributes:
        url: URL del competidor
        title: Título de la página
        domain: Dominio del sitio
        position: Posición en SERP
        traffic: Tráfico estimado (SEMrush)
        traffic_cost: Coste de tráfico estimado (SEMrush)
        content: Contenido scrapeado de la página
        word_count: Número de palabras del contenido
        headings: Lista de encabezados (H1, H2, H3)
        meta_description: Meta descripción
        scrape_success: Si el scraping fue exitoso
        error_message: Mensaje de error si falló
    """
    url: str
    title: str = ""
    domain: str = ""
    position: int = 0
    traffic: float = 0.0
    traffic_cost: float = 0.0
    content: str = ""
    word_count: int = 0
    headings: List[Dict[str, str]] = None
    meta_description: str = ""
    scrape_success: bool = False
    error_message: str = ""
    
    def __post_init__(self):
        if self.headings is None:
            self.headings = []
    
    def to_dict(self) -> Dict:
        """Convierte a diccionario para serialización."""
        return {
            'url': self.url,
            'title': self.title,
            'domain': self.domain,
            'position': self.position,
            'ranking_position': self.position,  # Alias para compatibilidad
            'traffic': self.traffic,
            'traffic_cost': self.traffic_cost,
            'content': self.content,
            'word_count': self.word_count,
            'headings': self.headings,
            'meta_description': self.meta_description,
            'scrape_success': self.scrape_success,
            'error_message': self.error_message
        }


@dataclass
class SEMrushResponse:
    """
    Respuesta estructurada de SEMrush API.
    
    Attributes:
        success: Si la llamada fue exitosa
        competitors: Lista de CompetitorData
        keyword: Keyword buscada
        database: Base de datos usada
        total_results: Número total de resultados
        error_message: Mensaje de error si falló
        api_units_used: Unidades de API consumidas
    """
    success: bool
    competitors: List[CompetitorData]
    keyword: str
    database: str
    total_results: int = 0
    error_message: str = ""
    api_units_used: int = 0
    
    def to_dict(self) -> Dict:
        """Convierte a diccionario para serialización."""
        return {
            'success': self.success,
            'competitors': [c.to_dict() for c in self.competitors],
            'keyword': self.keyword,
            'database': self.database,
            'total_results': self.total_results,
            'error_message': self.error_message,
            'api_units_used': self.api_units_used
        }


# ============================================================================
# CLASE PRINCIPAL - SEMRUSH CLIENT
# ============================================================================

class SEMrushClient:
    """
    Cliente para interactuar con SEMrush API.
    
    Permite:
    - Obtener resultados orgánicos para una keyword
    - Scrapear contenido de URLs competidoras
    - Analizar métricas SEO de competidores
    
    Example:
        >>> client = SEMrushClient(api_key="tu-api-key")
        >>> response = client.get_organic_competitors("mejor portátil gaming")
        >>> for comp in response.competitors:
        ...     print(f"{comp.position}. {comp.title}")
    """
    
    def __init__(
        self,
        api_key: str,
        database: str = 'es',
        user_agent: str = DEFAULT_USER_AGENT,
        timeout: int = REQUEST_TIMEOUT
    ):
        """
        Inicializa el cliente de SEMrush.
        
        Args:
            api_key: API key de SEMrush
            database: Base de datos regional (default: 'es' para España)
            user_agent: User agent para scraping de contenido
            timeout: Timeout para requests en segundos
            
        Raises:
            ValueError: Si la API key está vacía
        """
        if not api_key:
            raise ValueError("SEMrush API key es requerida")
        
        self.api_key = api_key
        self.database = database if database in SEMRUSH_DATABASES else 'es'
        self.user_agent = user_agent
        self.timeout = timeout
        self._last_request_time = 0
    
    def _rate_limit(self) -> None:
        """Aplica rate limiting entre requests."""
        elapsed = time.time() - self._last_request_time
        if elapsed < RATE_LIMIT_DELAY:
            time.sleep(RATE_LIMIT_DELAY - elapsed)
        self._last_request_time = time.time()
    
    def get_organic_competitors(
        self,
        keyword: str,
        num_results: int = DEFAULT_COMPETITORS,
        scrape_content: bool = True,
        exclude_domains: Optional[List[str]] = None
    ) -> SEMrushResponse:
        """
        Obtiene los competidores orgánicos para una keyword.
        
        Args:
            keyword: Keyword a buscar
            num_results: Número de resultados a obtener (max 10)
            scrape_content: Si True, scrapea el contenido de cada URL
            exclude_domains: Lista de dominios a excluir (ej: ['pccomponentes.com'])
            
        Returns:
            SEMrushResponse con la lista de competidores
            
        Notes:
            - Usa el endpoint phrase_organic de SEMrush
            - Aplica rate limiting automático
            - Excluye dominios propios por defecto
        """
        
        # Validar parámetros
        num_results = min(max(1, num_results), MAX_COMPETITORS)
        
        if exclude_domains is None:
            exclude_domains = ['pccomponentes.com', 'pccomponentes.pt']
        
        # Aplicar rate limiting
        self._rate_limit()
        
        try:
            # Construir parámetros de la API
            params = {
                'type': 'phrase_organic',
                'key': self.api_key,
                'phrase': keyword,
                'database': self.database,
                'display_limit': num_results + len(exclude_domains) + 5,  # Extra para filtrar
                'export_columns': 'Ph,Po,Nq,Cp,Co,Ur,Tt,Ds,Vu,Fk'
            }
            
            # Hacer request a SEMrush
            response = requests.get(
                SEMRUSH_ORGANIC_RESULTS,
                params=params,
                timeout=self.timeout
            )
            
            # Verificar respuesta
            if response.status_code != 200:
                return SEMrushResponse(
                    success=False,
                    competitors=[],
                    keyword=keyword,
                    database=self.database,
                    error_message=f"Error HTTP {response.status_code}: {response.text[:200]}"
                )
            
            # Verificar errores de API
            if response.text.startswith('ERROR'):
                return SEMrushResponse(
                    success=False,
                    competitors=[],
                    keyword=keyword,
                    database=self.database,
                    error_message=f"SEMrush API Error: {response.text}"
                )
            
            # Parsear respuesta CSV de SEMrush
            competitors = self._parse_semrush_response(
                response.text,
                exclude_domains,
                num_results
            )
            
            # Scrapear contenido si se solicita
            if scrape_content and competitors:
                competitors = self._scrape_competitors_content(competitors)
            
            return SEMrushResponse(
                success=True,
                competitors=competitors,
                keyword=keyword,
                database=self.database,
                total_results=len(competitors),
                api_units_used=1  # Aproximación
            )
        
        except requests.Timeout:
            return SEMrushResponse(
                success=False,
                competitors=[],
                keyword=keyword,
                database=self.database,
                error_message="Timeout al conectar con SEMrush API"
            )
        
        except requests.RequestException as e:
            return SEMrushResponse(
                success=False,
                competitors=[],
                keyword=keyword,
                database=self.database,
                error_message=f"Error de conexión: {str(e)}"
            )
        
        except Exception as e:
            return SEMrushResponse(
                success=False,
                competitors=[],
                keyword=keyword,
                database=self.database,
                error_message=f"Error inesperado: {str(e)}"
            )
    
    def _parse_semrush_response(
        self,
        csv_text: str,
        exclude_domains: List[str],
        max_results: int
    ) -> List[CompetitorData]:
        """
        Parsea la respuesta CSV de SEMrush.
        
        El formato de SEMrush es CSV con columnas:
        Ph (Phrase), Po (Position), Nq (Number of queries), Cp (CPC),
        Co (Competition), Ur (URL), Tt (Title), Ds (Description),
        Vu (Visibility), Fk (Features in SERP)
        
        Args:
            csv_text: Texto CSV de la respuesta
            exclude_domains: Dominios a excluir
            max_results: Número máximo de resultados
            
        Returns:
            Lista de CompetitorData parseados
        """
        competitors = []
        lines = csv_text.strip().split('\n')
        
        if len(lines) < 2:
            return competitors
        
        # Primera línea son los headers
        headers = lines[0].split(';')
        
        # Mapear índices de columnas
        col_map = {}
        for i, header in enumerate(headers):
            col_map[header.strip()] = i
        
        # Procesar cada línea de datos
        for line in lines[1:]:
            if len(competitors) >= max_results:
                break
            
            values = line.split(';')
            
            if len(values) < 6:
                continue
            
            try:
                # Extraer URL
                url_idx = col_map.get('Ur', col_map.get('url', 5))
                url = values[url_idx].strip() if url_idx < len(values) else ''
                
                if not url:
                    continue
                
                # Extraer dominio
                domain = self._extract_domain(url)
                
                # Filtrar dominios excluidos
                if any(excluded in domain.lower() for excluded in exclude_domains):
                    continue
                
                # Extraer posición
                pos_idx = col_map.get('Po', col_map.get('position', 1))
                position = int(values[pos_idx]) if pos_idx < len(values) else 0
                
                # Extraer título
                title_idx = col_map.get('Tt', col_map.get('title', 6))
                title = values[title_idx].strip() if title_idx < len(values) else ''
                
                # Extraer tráfico (si está disponible)
                traffic_idx = col_map.get('Vu', -1)
                traffic = float(values[traffic_idx]) if traffic_idx >= 0 and traffic_idx < len(values) else 0.0
                
                # Extraer descripción
                desc_idx = col_map.get('Ds', col_map.get('description', 7))
                description = values[desc_idx].strip() if desc_idx < len(values) else ''
                
                competitor = CompetitorData(
                    url=url,
                    title=title,
                    domain=domain,
                    position=position,
                    traffic=traffic,
                    meta_description=description
                )
                
                competitors.append(competitor)
            
            except (ValueError, IndexError) as e:
                # Ignorar líneas mal formateadas
                continue
        
        return competitors
    
    def _extract_domain(self, url: str) -> str:
        """Extrae el dominio de una URL."""
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            return parsed.netloc.replace('www.', '')
        except Exception:
            return url
    
    def _scrape_competitors_content(
        self,
        competitors: List[CompetitorData]
    ) -> List[CompetitorData]:
        """
        Scrapea el contenido de cada URL competidora.
        
        Args:
            competitors: Lista de CompetitorData a scrapear
            
        Returns:
            Lista actualizada con contenido scrapeado
        """
        
        headers = {
            'User-Agent': self.user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
        }
        
        for competitor in competitors:
            self._rate_limit()
            
            try:
                response = requests.get(
                    competitor.url,
                    headers=headers,
                    timeout=self.timeout,
                    allow_redirects=True
                )
                
                if response.status_code != 200:
                    competitor.error_message = f"HTTP {response.status_code}"
                    continue
                
                # Parsear HTML
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Extraer título si no lo teníamos
                if not competitor.title:
                    title_tag = soup.find('title')
                    if title_tag:
                        competitor.title = title_tag.get_text(strip=True)
                
                # Extraer meta description si no la teníamos
                if not competitor.meta_description:
                    meta_desc = soup.find('meta', attrs={'name': 'description'})
                    if meta_desc:
                        competitor.meta_description = meta_desc.get('content', '')
                
                # Extraer contenido principal
                competitor.content = self._extract_main_content(soup)
                competitor.word_count = len(competitor.content.split())
                
                # Extraer headings
                competitor.headings = self._extract_headings(soup)
                
                competitor.scrape_success = True
            
            except requests.Timeout:
                competitor.error_message = "Timeout"
            
            except requests.RequestException as e:
                competitor.error_message = f"Request error: {str(e)[:50]}"
            
            except Exception as e:
                competitor.error_message = f"Error: {str(e)[:50]}"
        
        return competitors
    
    def _extract_main_content(self, soup: BeautifulSoup) -> str:
        """
        Extrae el contenido principal de una página.
        
        Intenta encontrar el contenido principal eliminando
        navegación, footers, sidebars, etc.
        
        Args:
            soup: Objeto BeautifulSoup parseado
            
        Returns:
            str: Contenido de texto limpio
        """
        
        # Clonar soup para no modificar el original
        soup_copy = BeautifulSoup(str(soup), 'html.parser')
        
        # Eliminar elementos no deseados
        for element in soup_copy.find_all([
            'nav', 'header', 'footer', 'aside', 'script', 'style',
            'noscript', 'iframe', 'form', 'button', 'input'
        ]):
            element.decompose()
        
        # Eliminar por clases comunes de navegación/sidebar
        for selector in [
            '[class*="nav"]', '[class*="menu"]', '[class*="sidebar"]',
            '[class*="footer"]', '[class*="header"]', '[class*="cookie"]',
            '[class*="banner"]', '[class*="ad"]', '[class*="social"]',
            '[id*="nav"]', '[id*="menu"]', '[id*="sidebar"]',
            '[id*="footer"]', '[id*="header"]'
        ]:
            for element in soup_copy.select(selector):
                element.decompose()
        
        # Intentar encontrar el contenido principal
        main_content = None
        
        # Buscar por elementos semánticos
        for selector in ['main', 'article', '[role="main"]', '.content', '#content']:
            main_content = soup_copy.select_one(selector)
            if main_content:
                break
        
        # Si no encontramos contenedor principal, usar body
        if not main_content:
            main_content = soup_copy.find('body') or soup_copy
        
        # Extraer texto
        text = main_content.get_text(' ', strip=True)
        
        # Limpiar espacios múltiples
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Limitar longitud para evitar contenido excesivo
        max_chars = 10000
        if len(text) > max_chars:
            text = text[:max_chars] + "..."
        
        return text
    
    def _extract_headings(self, soup: BeautifulSoup) -> List[Dict[str, str]]:
        """
        Extrae los encabezados (H1-H4) de la página.
        
        Args:
            soup: Objeto BeautifulSoup parseado
            
        Returns:
            Lista de dicts con 'level' y 'text'
        """
        headings = []
        
        for tag in soup.find_all(['h1', 'h2', 'h3', 'h4']):
            text = tag.get_text(strip=True)
            if text and len(text) > 2:
                headings.append({
                    'level': tag.name,
                    'text': text[:200]  # Limitar longitud
                })
        
        return headings[:30]  # Máximo 30 headings
    
    def validate_api_key(self) -> Tuple[bool, str]:
        """
        Valida que la API key de SEMrush sea válida.
        
        Returns:
            Tuple[bool, str]: (es_válida, mensaje)
        """
        
        try:
            # Hacer una consulta mínima para validar
            params = {
                'type': 'phrase_organic',
                'key': self.api_key,
                'phrase': 'test',
                'database': 'us',
                'display_limit': 1
            }
            
            response = requests.get(
                SEMRUSH_ORGANIC_RESULTS,
                params=params,
                timeout=10
            )
            
            if 'ERROR' in response.text:
                if 'INVALID KEY' in response.text.upper():
                    return False, "API key inválida"
                elif 'LIMIT' in response.text.upper():
                    return True, "API key válida (límite alcanzado)"
                else:
                    return False, f"Error: {response.text[:100]}"
            
            return True, "API key válida"
        
        except Exception as e:
            return False, f"Error de conexión: {str(e)}"


# ============================================================================
# FUNCIONES DE UTILIDAD
# ============================================================================

def get_semrush_client(api_key: Optional[str] = None) -> Optional[SEMrushClient]:
    """
    Obtiene un cliente de SEMrush configurado.
    
    Args:
        api_key: API key de SEMrush (opcional, usa config si no se proporciona)
        
    Returns:
        SEMrushClient configurado o None si no hay API key
    """
    
    if not api_key:
        try:
            from config.settings import SEMRUSH_API_KEY
            api_key = SEMRUSH_API_KEY
        except ImportError:
            pass
    
    if not api_key:
        return None
    
    try:
        from config.settings import SEMRUSH_DATABASE
        database = SEMRUSH_DATABASE
    except ImportError:
        database = 'es'
    
    return SEMrushClient(api_key=api_key, database=database)


def format_competitors_for_display(competitors: List[CompetitorData]) -> List[Dict]:
    """
    Formatea los competidores para mostrar en la UI.
    
    Args:
        competitors: Lista de CompetitorData
        
    Returns:
        Lista de dicts formateados para la UI
    """
    
    formatted = []
    
    for comp in competitors:
        formatted.append({
            'url': comp.url,
            'title': comp.title or 'Sin título',
            'domain': comp.domain,
            'position': comp.position,
            'ranking_position': comp.position,
            'word_count': comp.word_count,
            'content': comp.content,
            'headings': comp.headings,
            'meta_description': comp.meta_description,
            'scrape_success': comp.scrape_success,
            'error': comp.error_message if not comp.scrape_success else None
        })
    
    return formatted


def is_semrush_available() -> bool:
    """
    Verifica si SEMrush está configurado y disponible.
    
    Returns:
        bool: True si SEMrush está disponible
    """
    
    try:
        from config.settings import SEMRUSH_API_KEY, SEMRUSH_ENABLED
        return bool(SEMRUSH_API_KEY) and SEMRUSH_ENABLED
    except ImportError:
        return False


# ============================================================================
# CONSTANTES Y CONFIGURACIÓN
# ============================================================================

# Versión del módulo
__version__ = "4.2.0"
