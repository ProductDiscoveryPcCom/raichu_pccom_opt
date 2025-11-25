"""
Funciones de scraping: PDPs y competidores
"""
import requests
from bs4 import BeautifulSoup
from typing import Dict, Optional
import streamlit as st

from config.settings import N8N_WEBHOOK_URL


def scrape_pdp_n8n(product_id: str, timeout: int = 30) -> Optional[Dict]:
    """
    Scrapea PDP usando webhook n8n
    
    Args:
        product_id: ID del producto
        timeout: Timeout en segundos
        
    Returns:
        Dict con datos del producto o None si error
    """
    try:
        response = requests.post(
            N8N_WEBHOOK_URL,
            json={"productId": product_id},
            timeout=timeout
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error en webhook: {response.status_code}")
            return None
            
    except requests.exceptions.ConnectionError:
        st.error("No se puede conectar al webhook. Conecta a la VPN")
        return None
    except Exception as e:
        st.error(f"Error scrapeando PDP: {str(e)}")
        return None


def get_mock_pdp_data(product_id: str) -> Dict:
    """
    Datos mock para testing sin VPN
    
    Args:
        product_id: ID del producto
        
    Returns:
        Dict con datos mock del producto
    """
    return {
        "productId": product_id,
        "nombre": "Xiaomi Robot Vacuum E5 Robot con Función de Aspiración y Fregado",
        "precio_actual": "59.99",
        "precio_anterior": "64.99",
        "descuento": "-7%",
        "valoracion": "4.1",
        "num_opiniones": "112",
        "badges": ["Precio mínimo histórico"],
        "url_producto": f"https://www.pccomponentes.com/producto/{product_id}",
        "especificaciones": {
            "potencia_succion": "2000Pa",
            "navegacion": "Giroscopio + sensores IR",
            "bateria": "2600 mAh",
            "autonomia": "110 minutos",
            "deposito_polvo": "400 ml",
            "deposito_agua": "90 ml",
            "altura": "70 mm",
            "conectividad": "WiFi 2.4GHz",
            "control_voz": "Alexa, Google Assistant",
            "fregado": "Sí (mopa incluida)"
        },
        "descripcion": "Olvida la limpieza manual: aspira y friega con eficiencia...",
        "opiniones_resumen": [
            "Calidad-precio de 10...",
            "Aspira muy bien...",
            "El perfil bajo de 70mm...",
            "No mapea por habitaciones..."
        ]
    }


def scrape_competitor_content(url: str, timeout: int = 15) -> Dict:
    """
    Scrapea el contenido de un competidor orgánico
    
    Args:
        url: URL del competidor
        timeout: Timeout en segundos
        
    Returns:
        Dict con contenido scrapeado o error
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Eliminar elementos no deseados
        for element in soup(['script', 'style', 'nav', 'header', 'footer', 
                            'aside', 'form', 'iframe', 'noscript']):
            element.decompose()
        
        # Buscar el contenido principal
        article = _find_main_content(soup)
        
        if article:
            return _extract_article_data(article, url)
        
        return {
            'url': url,
            'error': 'No se encontró contenido principal',
            'scraped': False
        }
        
    except requests.exceptions.Timeout:
        return {'url': url, 'error': 'Timeout al cargar la página', 'scraped': False}
    except requests.exceptions.RequestException as e:
        return {'url': url, 'error': f'Error de conexión: {str(e)}', 'scraped': False}
    except Exception as e:
        return {'url': url, 'error': f'Error procesando: {str(e)}', 'scraped': False}


def _find_main_content(soup):
    """Encuentra el contenido principal del artículo"""
    selectors = [
        'article',
        '[role="main"]',
        'main',
        '.article-content',
        '.post-content',
        '.entry-content',
        '.content-area',
        '#content',
        '.main-content'
    ]
    
    for selector in selectors:
        article = soup.select_one(selector)
        if article:
            return article
    
    return soup.body


def _extract_article_data(article, url: str) -> Dict:
    """Extrae datos del artículo"""
    # Extraer título
    title = ""
    h1 = article.find('h1')
    if h1:
        title = h1.get_text(strip=True)
    
    # Extraer subtítulos
    headings = []
    for h in article.find_all(['h2', 'h3']):
        headings.append({
            'level': h.name,
            'text': h.get_text(strip=True)
        })
    
    # Extraer párrafos
    paragraphs = []
    for p in article.find_all('p'):
        text = p.get_text(strip=True)
        if len(text) > 30:
            paragraphs.append(text)
    
    # Extraer listas
    lists = []
    for ul in article.find_all(['ul', 'ol']):
        items = [li.get_text(strip=True) for li in ul.find_all('li')]
        if items:
            lists.append(items)
    
    # Calcular estadísticas
    full_text = article.get_text(' ', strip=True)
    word_count = len(full_text.split())
    
    return {
        'url': url,
        'title': title,
        'headings': headings,
        'paragraphs': paragraphs[:20],
        'lists': lists[:10],
        'word_count': word_count,
        'scraped': True,
        'html_snippet': str(article)[:5000]
    }
