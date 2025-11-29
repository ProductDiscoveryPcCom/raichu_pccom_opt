# -*- coding: utf-8 -*-
"""
N8N Integration Module - PcComponentes Content Generator
Versión 1.2.0

Módulo para integración con n8n y APIs de PcComponentes.
Soporta múltiples métodos de obtención de datos:
1. Webhook de n8n (formato legacy_id o chatInput)
2. Llamada directa a ClickHouse + API Catálogo

Configuración en Streamlit secrets:
- [n8n] N8N_WEBHOOK_URL: URL del webhook
- [n8n] verify_ssl: false (para servidores internos con certificados autofirmados)
- [n8n] CATALOG_API_TOKEN: Bearer token para API catálogo (opcional)

Autor: PcComponentes - Product Discovery & Content
"""

import requests
import re
import json
import logging
import urllib3
from typing import Dict, Optional, Any, Tuple, List
from dataclasses import dataclass, field

# Configurar logger
logger = logging.getLogger(__name__)

# Suprimir warnings de SSL cuando se deshabilita verificación
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

__version__ = "1.2.0"


# ============================================================================
# CONFIGURACIÓN
# ============================================================================

# URLs de APIs internas
CATALOG_API_BASE = "http://catalog.prod.pccomponentes.com/v1/catalog/products"
CLICKHOUSE_URL = "http://clickhouse.clickhouse-prod:8123"

# Bearer token por defecto para API catálogo (del workflow)
DEFAULT_CATALOG_TOKEN = "Bearer header.eyJpYXQiOjE1NzE5MDAzMTIsImV4cCI6MTU3MTkwMzkxMiwicm9sZXMiOlsiUk9MRV9QSU1fUE0iLCJST0xFX1VTRVIiXSwidXNlcm5hbWUiOiJhaUBwY2NvbXBvbmVudGVzLmNvbSIsInVzZXJfaWQiOiIwN2UxNzViMC0yM2ZhLTRjYTgtYWYzYi1jMDhiYzZkZDAwNmUifQ==.signature"

# Patrones para extraer legacy_id de URLs
URL_PATTERNS = [
    r'/(\d{6,10})(?:\?|$|/)',  # Número de 6-10 dígitos en la URL
    r'-(\d{6,10})(?:\?|$)',     # Después de un guión
    r'(\d{7,10})$',             # Al final de la URL
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
    attributes: Dict[str, str] = field(default_factory=dict)
    images: List[str] = field(default_factory=list)
    url: str = ""
    available: bool = True
    category: str = ""
    
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
            'category': self.category,
        }


# ============================================================================
# FUNCIONES DE EXTRACCIÓN DE ID
# ============================================================================

def extract_legacy_id_from_url(url: str) -> Optional[str]:
    """
    Extrae el legacy_id de una URL de PcComponentes.
    
    Args:
        url: URL del producto
        
    Returns:
        legacy_id o None si no se encuentra
    """
    if not url:
        return None
    
    for pattern in URL_PATTERNS:
        match = re.search(pattern, url)
        if match:
            legacy_id = match.group(1)
            logger.info(f"legacy_id extraído de URL: {legacy_id}")
            return legacy_id
    
    return None


def extract_legacy_id_from_slug(slug: str) -> Optional[str]:
    """
    Extrae el legacy_id del slug del producto.
    
    Args:
        slug: Slug del producto (última parte de la URL)
        
    Returns:
        legacy_id o None
    """
    if not slug:
        return None
    
    # Buscar números de 6-10 dígitos en el slug
    match = re.search(r'(\d{6,10})', slug)
    if match:
        return match.group(1)
    
    return None


# ============================================================================
# MÉTODO 1: WEBHOOK N8N
# ============================================================================

def fetch_product_via_n8n_webhook(
    legacy_id: str,
    product_url: str,
    webhook_url: str,
    timeout: int = 30,
    verify_ssl: bool = True
) -> Tuple[bool, Optional[ProductData], str]:
    """
    Obtiene datos del producto via webhook de n8n.
    Intenta múltiples formatos de payload.
    
    Args:
        legacy_id: ID legacy del producto
        product_url: URL completa del producto
        webhook_url: URL del webhook de n8n
        timeout: Timeout en segundos
        verify_ssl: Si False, no verifica certificado SSL (para servidores internos)
        
    Returns:
        Tuple[success, ProductData, error_message]
    """
    if not webhook_url:
        return False, None, "No se ha configurado N8N_WEBHOOK_URL"
    
    headers = {"Content-Type": "application/json"}
    
    # Lista de payloads a intentar en orden
    payloads_to_try = [
        # Formato 1: legacy_id directo (workflow CATALOGACIÓN)
        {"legacy_id": legacy_id} if legacy_id else None,
        
        # Formato 2: chatInput con URL (workflow Generador Reviews)
        {"chatInput": product_url, "sessionId": "streamlit"} if product_url else None,
        
        # Formato 3: product_url directo
        {"product_url": product_url} if product_url else None,
        
        # Formato 4: url simple
        {"url": product_url} if product_url else None,
    ]
    
    # Filtrar payloads None
    payloads_to_try = [p for p in payloads_to_try if p]
    
    last_error = "No hay datos para enviar"
    
    for payload in payloads_to_try:
        try:
            logger.info(f"Intentando webhook con payload: {list(payload.keys())}")
            
            response = requests.post(
                webhook_url,
                json=payload,
                headers=headers,
                timeout=timeout,
                verify=verify_ssl  # Permite deshabilitar verificación SSL
            )
            
            # Log de respuesta
            logger.info(f"Respuesta HTTP {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    
                    # Manejar respuesta como lista
                    if isinstance(data, list) and len(data) > 0:
                        data = data[0]
                    
                    # Verificar si hay error en la respuesta
                    if data.get('error') == True:
                        last_error = data.get('message', 'Error en el webhook')
                        continue
                    
                    # Parsear respuesta exitosa
                    product = _parse_n8n_response(data, legacy_id, product_url)
                    if product:
                        return True, product, ""
                    else:
                        last_error = "Respuesta vacía o inválida del webhook"
                        continue
                        
                except json.JSONDecodeError:
                    last_error = f"Respuesta no es JSON válido: {response.text[:200]}"
                    continue
            else:
                last_error = f"Error HTTP {response.status_code}: {response.text[:200]}"
                continue
                
        except requests.exceptions.Timeout:
            last_error = f"Timeout después de {timeout}s"
            continue
        except requests.exceptions.RequestException as e:
            last_error = f"Error de conexión: {str(e)}"
            continue
        except Exception as e:
            last_error = f"Error inesperado: {str(e)}"
            continue
    
    return False, None, last_error


def _parse_n8n_response(data: Dict, legacy_id: str, product_url: str) -> Optional[ProductData]:
    """Parsea la respuesta del webhook de n8n."""
    
    # Si no hay datos significativos, retornar None
    if not data:
        return None
    
    # Verificar si es una respuesta válida con datos del producto
    has_valid_data = any([
        data.get('title'),
        data.get('name'),
        data.get('brand'),
        data.get('brand_name'),
        data.get('price'),
    ])
    
    if not has_valid_data:
        return None
    
    # Extraer atributos
    attributes = {}
    if data.get('attributes_dict'):
        attributes = data['attributes_dict']
    elif data.get('attributes'):
        if isinstance(data['attributes'], dict):
            attributes = data['attributes']
        elif isinstance(data['attributes'], list):
            for attr in data['attributes']:
                if isinstance(attr, dict) and 'label' in attr and 'value' in attr:
                    attributes[attr['label']] = attr['value']
    elif data.get('specifications'):
        for spec in data.get('specifications', []):
            if isinstance(spec, dict) and 'label' in spec and 'value' in spec:
                attributes[spec['label']] = spec['value']
    
    # Formatear precio
    price = data.get('price', 0)
    if isinstance(price, str):
        try:
            price = float(price.replace('€', '').replace(',', '.').strip())
        except:
            price = 0.0
    
    price_formatted = data.get('price_formatted', '')
    if not price_formatted and price:
        price_formatted = f"{price:.2f}€"
    
    return ProductData(
        legacy_id=data.get('legacy_id', legacy_id) or legacy_id or '',
        product_id=data.get('product_id', ''),
        name=data.get('title', data.get('name', data.get('simplified_name', ''))),
        brand=data.get('brand_name', data.get('brand', '')),
        price=float(price) if price else 0.0,
        price_formatted=price_formatted,
        description=data.get('description', ''),
        attributes=attributes,
        images=data.get('images', []),
        url=data.get('url', product_url) or product_url,
        available=data.get('available', data.get('hasValidData', True)),
        category=data.get('category', data.get('family_name', '')),
    )


# ============================================================================
# MÉTODO 2: API CATÁLOGO DIRECTA (requiere product_id UUID)
# ============================================================================

def fetch_product_via_catalog_api(
    product_id: str,
    api_token: str = None,
    timeout: int = 15
) -> Tuple[bool, Optional[ProductData], str]:
    """
    Obtiene datos del producto directamente de la API del catálogo.
    
    NOTA: La API requiere el UUID (product_id), no el legacy_id.
    
    Args:
        product_id: UUID del producto
        api_token: Bearer token (usa default si no se proporciona)
        timeout: Timeout en segundos
        
    Returns:
        Tuple[success, ProductData, error_message]
    """
    if not product_id:
        return False, None, "Se requiere product_id (UUID)"
    
    token = api_token or DEFAULT_CATALOG_TOKEN
    url = f"{CATALOG_API_BASE}/{product_id}"
    
    headers = {
        "Authorization": token if token.startswith("Bearer") else f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=timeout)
        
        if response.status_code == 200:
            data = response.json()
            
            # Parsear atributos
            attributes = {}
            for attr in data.get('attributeValues', []):
                attr_name = attr.get('attribute', {}).get('name', '')
                attr_value = attr.get('enumOption', {}).get('name', attr.get('value', ''))
                if attr_name and attr_value:
                    attributes[attr_name] = attr_value
            
            product = ProductData(
                legacy_id=data.get('legacyId', ''),
                product_id=product_id,
                name=data.get('name', ''),
                brand=data.get('brand', {}).get('name', ''),
                price=0.0,  # API catálogo no incluye precio
                price_formatted='',
                description=data.get('description', ''),
                attributes=attributes,
                images=[img.get('url', '') for img in data.get('images', [])],
                url=f"https://www.pccomponentes.com/producto/{data.get('legacyId', '')}",
                available=data.get('status') == 'enabled',
                category=data.get('family', {}).get('name', ''),
            )
            
            return True, product, ""
        else:
            return False, None, f"Error HTTP {response.status_code}: {response.text[:200]}"
            
    except requests.exceptions.Timeout:
        return False, None, f"Timeout después de {timeout}s"
    except Exception as e:
        return False, None, f"Error: {str(e)}"


# ============================================================================
# FUNCIÓN PRINCIPAL
# ============================================================================

def get_product_data(
    url_or_id: str,
    n8n_webhook_url: Optional[str] = None,
    catalog_api_token: Optional[str] = None,
    verify_ssl: bool = True,
) -> Tuple[bool, Optional[ProductData], str]:
    """
    Obtiene datos del producto usando el método disponible.
    
    Args:
        url_or_id: URL del producto o legacy_id directo
        n8n_webhook_url: URL del webhook de n8n
        catalog_api_token: Token para API catálogo (opcional)
        verify_ssl: Si False, no verifica certificado SSL
        
    Returns:
        Tuple[success, ProductData, error_message]
    """
    # Determinar URL y legacy_id
    product_url = ""
    legacy_id = ""
    
    if url_or_id.startswith('http'):
        product_url = url_or_id
        legacy_id = extract_legacy_id_from_url(url_or_id)
        if not legacy_id:
            slug = url_or_id.split('/')[-1].split('?')[0]
            legacy_id = extract_legacy_id_from_slug(slug)
    else:
        # Es un ID directo
        legacy_id = url_or_id
    
    # Intentar con webhook de n8n
    if n8n_webhook_url:
        success, product, error = fetch_product_via_n8n_webhook(
            legacy_id=legacy_id,
            product_url=product_url,
            webhook_url=n8n_webhook_url,
            verify_ssl=verify_ssl
        )
        if success:
            return success, product, error
        logger.warning(f"Webhook n8n falló: {error}")
    
    # Si no hay webhook configurado
    if not n8n_webhook_url:
        return False, None, "Configuración requerida: N8N_WEBHOOK_URL en secrets [n8n]"
    
    return False, None, "No se pudo obtener datos del producto"


# ============================================================================
# FUNCIÓN PARA STREAMLIT
# ============================================================================

def fetch_product_for_streamlit(
    url: str,
    secrets: Optional[Dict] = None,
    manual_id: Optional[str] = None
) -> Tuple[bool, Dict[str, Any], str]:
    """
    Función wrapper para uso en Streamlit.
    
    Args:
        url: URL del producto (se guarda para enlazar en el contenido)
        secrets: st.secrets o dict con configuración
        manual_id: ID del producto introducido manualmente (opcional)
        
    Returns:
        Tuple[success, product_dict, error_message]
    """
    # Obtener configuración de secrets
    webhook_url = None
    api_token = None
    verify_ssl = True  # Por defecto verificar SSL
    
    if secrets:
        # Buscar N8N_WEBHOOK_URL en múltiples ubicaciones posibles
        webhook_url = (
            secrets.get('N8N_WEBHOOK_URL') or
            secrets.get('n8n_webhook_url') or
            secrets.get('n8n', {}).get('N8N_WEBHOOK_URL') or
            secrets.get('n8n', {}).get('webhook_url') or
            secrets.get('n8n', {}).get('url')
        )
        api_token = (
            secrets.get('CATALOG_API_TOKEN') or
            secrets.get('catalog', {}).get('api_token') or
            secrets.get('n8n', {}).get('CATALOG_API_TOKEN')
        )
        # Opción para deshabilitar verificación SSL (servidores internos)
        verify_ssl_setting = (
            secrets.get('n8n', {}).get('verify_ssl') or
            secrets.get('n8n', {}).get('VERIFY_SSL') or
            secrets.get('VERIFY_SSL')
        )
        # Si está explícitamente en False, deshabilitar
        if verify_ssl_setting is False or str(verify_ssl_setting).lower() == 'false':
            verify_ssl = False
    
    if not webhook_url:
        return False, {}, "Configuración requerida: N8N_WEBHOOK_URL en secrets de Streamlit (sección [n8n])"
    
    # Determinar qué usar: manual_id o URL
    url_or_id = manual_id if manual_id else url
    
    success, product, error = get_product_data(
        url_or_id=url_or_id,
        n8n_webhook_url=webhook_url,
        catalog_api_token=api_token,
        verify_ssl=verify_ssl
    )
    
    if success and product:
        product_dict = product.to_dict()
        # Asegurar que la URL original esté presente
        if url and not product_dict.get('url'):
            product_dict['url'] = url
        return True, product_dict, ""
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
    'fetch_product_via_n8n_webhook',
    'fetch_product_via_catalog_api',
    'get_product_data',
    'fetch_product_for_streamlit',
]
