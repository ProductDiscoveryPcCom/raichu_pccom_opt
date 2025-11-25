"""
Scraper de Productos - PcComponentes Content Generator
Versión 4.1.1

Funciones para scrapear datos de productos desde PcComponentes usando n8n webhook
y BeautifulSoup como fallback.

Autor: PcComponentes - Product Discovery & Content
"""

import requests
from bs4 import BeautifulSoup
from typing import Dict, Optional
import json

# Importar configuración
from config.settings import (
    N8N_WEBHOOK_URL,
    USER_AGENT,
    REQUEST_TIMEOUT
)


# ============================================================================
# SCRAPING VÍA N8N WEBHOOK
# ============================================================================

def scrape_pdp_data(url: str) -> Optional[Dict]:
    """
    Scrapea datos de un producto desde su URL de PDP.
    
    Intenta usar n8n webhook primero, y si falla usa BeautifulSoup como fallback.
    
    Args:
        url: URL del producto en PcComponentes
        
    Returns:
        Dict con datos del producto o None si falla
        
    Example:
        >>> data = scrape_pdp_data("https://www.pccomponentes.com/producto")
        >>> print(data['name'])
        'Nombre del producto'
        
    Notes:
        - Prioridad: n8n webhook > BeautifulSoup
        - Maneja errores gracefully
        - Retorna None si todo falla
    """
    
    if not url or not url.startswith('http'):
        return None
    
    # Intentar con n8n webhook primero (si está configurado)
    if N8N_WEBHOOK_URL:
        try:
            data = scrape_via_n8n(url)
            if data:
                return data
        except Exception:
            pass  # Fallar silenciosamente y probar fallback
    
    # Fallback: BeautifulSoup directo
    try:
        return scrape_via_beautifulsoup(url)
    except Exception:
        return None


def scrape_via_n8n(url: str) -> Optional[Dict]:
    """
    Scrapea usando el webhook de n8n.
    
    Args:
        url: URL del producto
        
    Returns:
        Dict con datos del producto o None si falla
        
    Notes:
        - Requiere N8N_WEBHOOK_URL configurado
        - Timeout de 30 segundos
    """
    
    if not N8N_WEBHOOK_URL:
        return None
    
    try:
        response = requests.post(
            N8N_WEBHOOK_URL,
            json={'url': url},
            timeout=REQUEST_TIMEOUT
        )
        
        if response.status_code == 200:
            return response.json()
        
        return None
    
    except Exception:
        return None


# ============================================================================
# SCRAPING VÍA BEAUTIFULSOUP (FALLBACK)
# ============================================================================

def scrape_via_beautifulsoup(url: str) -> Optional[Dict]:
    """
    Scrapea usando BeautifulSoup directamente.
    
    Args:
        url: URL del producto
        
    Returns:
        Dict con datos del producto o None si falla
        
    Notes:
        - Fallback cuando n8n no está disponible
        - Parsea HTML directamente
        - Puede fallar si PcComponentes cambia su estructura
    """
    
    try:
        # Headers para simular navegador
        headers = {
            'User-Agent': USER_AGENT,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
        }
        
        # Request
        response = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
        
        if response.status_code != 200:
            return None
        
        # Parse HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extraer datos usando selectores de PcComponentes
        product_data = extract_product_data_from_html(soup, url)
        
        return product_data
    
    except Exception:
        return None


def extract_product_data_from_html(soup: BeautifulSoup, url: str) -> Dict:
    """
    Extrae datos del producto desde el HTML parseado.
    
    Args:
        soup: Objeto BeautifulSoup con el HTML
        url: URL original del producto
        
    Returns:
        Dict con datos extraídos
        
    Notes:
        - Usa selectores específicos de PcComponentes
        - Puede necesitar actualización si cambia la estructura
        - Retorna dict con valores por defecto si no encuentra algo
    """
    
    data = {
        'url': url,
        'name': None,
        'price': None,
        'original_price': None,
        'discount': None,
        'brand': None,
        'model': None,
        'sku': None,
        'availability': None,
        'rating': None,
        'reviews_count': None,
        'description': None,
        'specifications': {},
        'images': [],
        'category': None
    }
    
    try:
        # Nombre del producto
        name_elem = soup.select_one('h1[data-testid="product-title"]')
        if not name_elem:
            name_elem = soup.select_one('h1.product-title')
        if name_elem:
            data['name'] = name_elem.get_text(strip=True)
        
        # Precio
        price_elem = soup.select_one('[data-testid="product-price"]')
        if not price_elem:
            price_elem = soup.select_one('.precio-actual')
        if price_elem:
            price_text = price_elem.get_text(strip=True)
            data['price'] = clean_price(price_text)
        
        # Precio original (si hay descuento)
        original_price_elem = soup.select_one('[data-testid="product-original-price"]')
        if not original_price_elem:
            original_price_elem = soup.select_one('.precio-tachado')
        if original_price_elem:
            original_price_text = original_price_elem.get_text(strip=True)
            data['original_price'] = clean_price(original_price_text)
        
        # Marca
        brand_elem = soup.select_one('[data-testid="product-brand"]')
        if not brand_elem:
            brand_elem = soup.select_one('.marca')
        if brand_elem:
            data['brand'] = brand_elem.get_text(strip=True)
        
        # Disponibilidad
        availability_elem = soup.select_one('[data-testid="product-availability"]')
        if not availability_elem:
            availability_elem = soup.select_one('.disponibilidad')
        if availability_elem:
            data['availability'] = availability_elem.get_text(strip=True)
        else:
            data['availability'] = 'Disponible'  # Default
        
        # Rating
        rating_elem = soup.select_one('[data-testid="product-rating"]')
        if rating_elem:
            rating_text = rating_elem.get_text(strip=True)
            data['rating'] = extract_rating(rating_text)
        
        # Número de reviews
        reviews_elem = soup.select_one('[data-testid="product-reviews-count"]')
        if reviews_elem:
            reviews_text = reviews_elem.get_text(strip=True)
            data['reviews_count'] = extract_number(reviews_text)
        
        # Descripción
        desc_elem = soup.select_one('[data-testid="product-description"]')
        if not desc_elem:
            desc_elem = soup.select_one('.descripcion')
        if desc_elem:
            data['description'] = desc_elem.get_text(strip=True)
        
        # SKU
        sku_elem = soup.select_one('[data-testid="product-sku"]')
        if sku_elem:
            data['sku'] = sku_elem.get_text(strip=True)
        
        # Imágenes
        image_elems = soup.select('[data-testid="product-image"]')
        if not image_elems:
            image_elems = soup.select('.imagen-producto')
        for img in image_elems[:5]:  # Máximo 5 imágenes
            img_url = img.get('src') or img.get('data-src')
            if img_url:
                data['images'].append(img_url)
        
        # Especificaciones (tabla de características)
        specs = {}
        spec_rows = soup.select('.caracteristicas tr')
        for row in spec_rows:
            cells = row.find_all(['th', 'td'])
            if len(cells) == 2:
                key = cells[0].get_text(strip=True)
                value = cells[1].get_text(strip=True)
                specs[key] = value
        
        if specs:
            data['specifications'] = specs
    
    except Exception:
        pass  # Si falla alguna extracción, continuar con lo que se tenga
    
    return data


# ============================================================================
# UTILIDADES
# ============================================================================

def clean_price(price_text: str) -> Optional[str]:
    """
    Limpia y formatea un string de precio.
    
    Args:
        price_text: Texto con el precio (ej: "1.299,99 €")
        
    Returns:
        String con precio limpio (ej: "1299.99") o None
        
    Example:
        >>> clean_price("1.299,99 €")
        "1299.99"
    """
    
    if not price_text:
        return None
    
    try:
        # Eliminar símbolo de euro y espacios
        clean = price_text.replace('€', '').replace(' ', '').strip()
        
        # Reemplazar coma decimal por punto
        clean = clean.replace(',', '.')
        
        # Eliminar puntos de miles
        parts = clean.split('.')
        if len(parts) > 2:
            # Tiene punto de miles
            clean = ''.join(parts[:-1]) + '.' + parts[-1]
        
        # Verificar que es un número válido
        float(clean)
        
        return clean
    
    except:
        return None


def extract_rating(rating_text: str) -> Optional[float]:
    """
    Extrae rating numérico de un texto.
    
    Args:
        rating_text: Texto con rating (ej: "4.5 de 5 estrellas")
        
    Returns:
        Float con rating o None
    """
    
    if not rating_text:
        return None
    
    try:
        import re
        # Buscar primer número decimal
        match = re.search(r'(\d+\.?\d*)', rating_text)
        if match:
            return float(match.group(1))
    except:
        pass
    
    return None


def extract_number(text: str) -> Optional[int]:
    """
    Extrae un número entero de un texto.
    
    Args:
        text: Texto que contiene un número
        
    Returns:
        Int con el número o None
    """
    
    if not text:
        return None
    
    try:
        import re
        # Eliminar separadores de miles
        clean = text.replace('.', '').replace(',', '')
        # Buscar primer número
        match = re.search(r'(\d+)', clean)
        if match:
            return int(match.group(1))
    except:
        pass
    
    return None


def validate_pccomponentes_url(url: str) -> bool:
    """
    Valida que una URL sea de PcComponentes.
    
    Args:
        url: URL a validar
        
    Returns:
        bool: True si es una URL válida de PcComponentes
    """
    
    if not url:
        return False
    
    return 'pccomponentes.com' in url.lower()


# ============================================================================
# CONSTANTES Y CONFIGURACIÓN
# ============================================================================

# Versión del módulo
__version__ = "4.1.1"

# Timeout por defecto (segundos)
DEFAULT_TIMEOUT = 30

# Headers por defecto
DEFAULT_HEADERS = {
    'User-Agent': USER_AGENT,
    'Accept': 'text/html,application/xhtml+xml',
    'Accept-Language': 'es-ES,es;q=0.9',
}
