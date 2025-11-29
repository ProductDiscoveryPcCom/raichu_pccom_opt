"""
N8N Integration Module - PcComponentes Content Generator
Versión 1.0.0

Módulo para integración con n8n y APIs de PcComponentes.
Soporta:
- Llamadas a webhooks de n8n
- Llamadas directas a la API del catálogo
- Extracción de datos de producto (precio, nombre, atributos)

Configuración requerida en Streamlit secrets:
- N8N_WEBHOOK_URL: URL del webhook de n8n (opcional)
- CATALOG_API_TOKEN: Bearer token para API de catálogo (opcional)

Autor: PcComponentes - Product Discovery & Content
"""

import requests
import re
import json
import logging
from typing import Dict, Optional, Any, Tuple
from dataclasses import dataclass

# Configurar logger
logger = logging.getLogger(__name__)

__version__ = "1.0.0"


# ============================================================================
# CONFIGURACIÓN
# ============================================================================

# URLs de APIs
CATALOG_API_BASE = "http://catalog.prod.pccomponentes.com/v1/catalog/products"
N8N_CATALOGACION_WORKFLOW = "sGKT5G7F1VlnnUfe"  # ID del workflow de catalogación

# Patrones para extraer legacy_id de URLs
URL_PATTERNS = [
    r'/(\d{6,10})(?:\?|$|/)',  # Número de 6-10 dígitos en la URL
    r'-(\d{6,10})(?:\?|$)',     # Después de un guión
]


# ============================================================================
# DATACLASSES
# ============================================================================

@dataclass
class ProductData:
    """Datos de un producto de PcComponentes."""
    legacy_id: str
    product_id: str = ""
    name: str = ""
    brand: str = ""
    price: float = 0.0
    price_formatted: str = ""
    description: str = ""
    attributes: Dict[str, str] = None
    images: list = None
    url: str = ""
    available: bool = True
    
    def to_dict(self) -> Dict:
        """Convierte a diccionario."""
        return {
            'legacy_id': self.legacy_id,
            'product_id': self.product_id,
            'name': self.name,
            'brand': self.brand,
            'price': self.price,
            'price_formatted': self.price_formatted,
            'description': self.description,
            'attributes': self.attributes or {},
            'images': self.images or [],
            'url': self.url,
            'available': self.available,
        }


# ============================================================================
# FUNCIONES DE EXTRACCIÓN
# ============================================================================

def extract_legacy_id_from_url(url: str) -> Optional[str]:
    """
    Extrae el legacy_id de una URL de PcComponentes.
    
    Args:
        url: URL del producto
        
    Returns:
        legacy_id o None si no se encuentra
        
    Examples:
        >>> extract_legacy_id_from_url("https://www.pccomponentes.com/msi-geforce-rtx-4060-ventus-8gb-gddr6")
        None  # Algunas URLs no tienen legacy_id visible
        >>> extract_legacy_id_from_url("https://www.pccomponentes.com/producto/10856418")
        "10856418"
    """
    if not url:
        return None
    
    # Limpiar URL
    url = url.strip().split('?')[0]  # Quitar parámetros GET
    
    # Buscar patrones de legacy_id
    for pattern in URL_PATTERNS:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    return None


def extract_legacy_id_from_slug(slug: str) -> Optional[str]:
    """
    Intenta extraer legacy_id del slug del producto.
    Algunas URLs antiguas incluyen el ID al final.
    
    Args:
        slug: Slug del producto (ej: "portatil-msi-cyborg-15-10856418")
        
    Returns:
        legacy_id o None
    """
    if not slug:
        return None
    
    # Buscar número al final del slug
    match = re.search(r'-(\d{6,10})$', slug)
    if match:
        return match.group(1)
    
    return None


# ============================================================================
# INTEGRACIÓN CON N8N
# ============================================================================

def fetch_product_via_n8n(
    legacy_id: str,
    webhook_url: str,
    timeout: int = 30
) -> Tuple[bool, Optional[ProductData], str]:
    """
    Obtiene datos del producto llamando al webhook de n8n.
    
    Args:
        legacy_id: ID legacy del producto
        webhook_url: URL del webhook de n8n
        timeout: Timeout en segundos
        
    Returns:
        Tuple[success, ProductData, error_message]
    """
    if not webhook_url:
        return False, None, "No se ha configurado N8N_WEBHOOK_URL"
    
    if not legacy_id:
        return False, None, "legacy_id es requerido"
    
    try:
        # Preparar request
        payload = {"legacy_id": legacy_id}
        headers = {"Content-Type": "application/json"}
        
        logger.info(f"Llamando a n8n webhook para legacy_id: {legacy_id}")
        
        response = requests.post(
            webhook_url,
            json=payload,
            headers=headers,
            timeout=timeout
        )
        
        if response.status_code != 200:
            return False, None, f"Error HTTP {response.status_code}: {response.text}"
        
        data = response.json()
        
        # Parsear respuesta de n8n
        product = ProductData(
            legacy_id=legacy_id,
            product_id=data.get('product_id', ''),
            name=data.get('title', data.get('name', '')),
            brand=data.get('brand_name', data.get('brand', '')),
            price=float(data.get('price', 0)),
            price_formatted=data.get('price_formatted', f"{data.get('price', 0)}€"),
            description=data.get('description', ''),
            attributes=data.get('attributes_dict', data.get('attributes', {})),
            images=data.get('images', []),
            url=data.get('url', f"https://www.pccomponentes.com/producto/{legacy_id}"),
            available=data.get('available', True),
        )
        
        logger.info(f"Producto obtenido: {product.name}")
        return True, product, ""
        
    except requests.exceptions.Timeout:
        return False, None, "Timeout: El webhook de n8n no respondió a tiempo"
    except requests.exceptions.RequestException as e:
        return False, None, f"Error de conexión: {str(e)}"
    except json.JSONDecodeError:
        return False, None, "Error: La respuesta no es JSON válido"
    except Exception as e:
        logger.error(f"Error inesperado: {e}")
        return False, None, f"Error inesperado: {str(e)}"


# ============================================================================
# INTEGRACIÓN DIRECTA CON API DE CATÁLOGO
# ============================================================================

def fetch_product_via_catalog_api(
    product_id: str,
    api_token: str,
    timeout: int = 15
) -> Tuple[bool, Optional[ProductData], str]:
    """
    Obtiene datos del producto directamente de la API de catálogo.
    
    Args:
        product_id: UUID del producto (no legacy_id)
        api_token: Bearer token para autenticación
        timeout: Timeout en segundos
        
    Returns:
        Tuple[success, ProductData, error_message]
    """
    if not api_token:
        return False, None, "No se ha configurado CATALOG_API_TOKEN"
    
    if not product_id:
        return False, None, "product_id es requerido"
    
    try:
        url = f"{CATALOG_API_BASE}/{product_id}"
        headers = {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json"
        }
        
        logger.info(f"Llamando a API de catálogo para product_id: {product_id}")
        
        response = requests.get(url, headers=headers, timeout=timeout)
        
        if response.status_code == 404:
            return False, None, "Producto no encontrado"
        
        if response.status_code != 200:
            return False, None, f"Error HTTP {response.status_code}"
        
        data = response.json().get('data', response.json())
        
        # Parsear respuesta del catálogo
        product = ProductData(
            legacy_id=str(data.get('legacyId', '')),
            product_id=data.get('id', product_id),
            name=data.get('name', ''),
            brand=data.get('brand', {}).get('name', ''),
            price=0.0,  # El catálogo no tiene precio, hay que obtenerlo de otra API
            description=data.get('description', ''),
            attributes=_parse_attribute_values(data.get('attributeValues', [])),
            images=data.get('images', []),
            url=f"https://www.pccomponentes.com/{data.get('slug', '')}",
            available=True,
        )
        
        return True, product, ""
        
    except requests.exceptions.Timeout:
        return False, None, "Timeout: La API de catálogo no respondió"
    except requests.exceptions.RequestException as e:
        return False, None, f"Error de conexión: {str(e)}"
    except Exception as e:
        logger.error(f"Error inesperado: {e}")
        return False, None, f"Error inesperado: {str(e)}"


def _parse_attribute_values(attribute_values: list) -> Dict[str, str]:
    """Parsea los attributeValues del catálogo a un diccionario simple."""
    result = {}
    
    for attr in attribute_values:
        attr_id = attr.get('attributeId', 'unknown')
        value = attr.get('value')
        
        # El valor puede ser string, array o dict
        if isinstance(value, list):
            result[attr_id] = ', '.join(str(v) for v in value)
        elif isinstance(value, dict):
            result[attr_id] = str(value)
        else:
            result[attr_id] = str(value) if value else ''
    
    return result


# ============================================================================
# FUNCIÓN PRINCIPAL DE SCRAPING
# ============================================================================

def get_product_data(
    url_or_id: str,
    n8n_webhook_url: Optional[str] = None,
    catalog_api_token: Optional[str] = None,
) -> Tuple[bool, Optional[ProductData], str]:
    """
    Obtiene datos de producto usando el método disponible.
    
    Prioridad:
    1. Si hay webhook de n8n configurado, lo usa
    2. Si hay token de API de catálogo, lo usa
    3. Si no hay nada configurado, retorna error
    
    Args:
        url_or_id: URL del producto o legacy_id/product_id directo
        n8n_webhook_url: URL del webhook de n8n (opcional)
        catalog_api_token: Token de API de catálogo (opcional)
        
    Returns:
        Tuple[success, ProductData, error_message]
    """
    # Determinar si es URL o ID
    if url_or_id.startswith('http'):
        legacy_id = extract_legacy_id_from_url(url_or_id)
        if not legacy_id:
            # Intentar extraer del slug
            slug = url_or_id.split('/')[-1].split('?')[0]
            legacy_id = extract_legacy_id_from_slug(slug)
    else:
        legacy_id = url_or_id
    
    if not legacy_id:
        return False, None, "No se pudo extraer el ID del producto de la URL"
    
    # Intentar con n8n primero
    if n8n_webhook_url:
        success, product, error = fetch_product_via_n8n(legacy_id, n8n_webhook_url)
        if success:
            return success, product, error
        logger.warning(f"n8n falló: {error}, intentando otro método...")
    
    # Si no hay n8n o falló, intentar con API directa
    # Nota: La API de catálogo requiere UUID, no legacy_id
    # Por ahora retornamos error si n8n no está disponible
    if not n8n_webhook_url:
        return False, None, "Configuración requerida: N8N_WEBHOOK_URL en los secrets de Streamlit"
    
    return False, None, "No se pudo obtener datos del producto"


# ============================================================================
# FUNCIÓN PARA STREAMLIT
# ============================================================================

def fetch_product_for_streamlit(
    url: str,
    secrets: Optional[Dict] = None
) -> Tuple[bool, Dict[str, Any], str]:
    """
    Función wrapper para uso en Streamlit.
    
    Args:
        url: URL del producto
        secrets: st.secrets o dict con configuración
        
    Returns:
        Tuple[success, product_dict, error_message]
    """
    # Obtener configuración de secrets
    webhook_url = None
    api_token = None
    
    if secrets:
        webhook_url = secrets.get('N8N_WEBHOOK_URL') or secrets.get('n8n', {}).get('webhook_url')
        api_token = secrets.get('CATALOG_API_TOKEN') or secrets.get('catalog', {}).get('api_token')
    
    success, product, error = get_product_data(
        url_or_id=url,
        n8n_webhook_url=webhook_url,
        catalog_api_token=api_token
    )
    
    if success and product:
        return True, product.to_dict(), ""
    else:
        return False, {}, error


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    '__version__',
    'ProductData',
    'extract_legacy_id_from_url',
    'extract_legacy_id_from_slug',
    'fetch_product_via_n8n',
    'fetch_product_via_catalog_api',
    'get_product_data',
    'fetch_product_for_streamlit',
]
