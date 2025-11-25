"""
SEMrush API Integration - PcComponentes Content Generator
Versión 4.1.1

Integración con SEMrush API para:
- Obtener top resultados orgánicos
- Volumen de búsquedas
- Dificultad de keyword
- Análisis competitivo

Documentación API: https://developer.semrush.com/api/

Autor: PcComponentes - Product Discovery & Content
"""

import requests
from typing import Dict, List, Optional, Tuple
import streamlit as st

from config.settings import SEMRUSH_API_KEY


# ============================================================================
# CONFIGURACIÓN
# ============================================================================

SEMRUSH_BASE_URL = "https://api.semrush.com/"

# Database para España
DEFAULT_DATABASE = "es"

# Límites
MAX_ORGANIC_RESULTS = 10


# ============================================================================
# FUNCIONES PRINCIPALES
# ============================================================================

def get_keyword_overview(keyword: str, database: str = DEFAULT_DATABASE) -> Optional[Dict]:
    """
    Obtiene métricas de una keyword: volumen, dificultad, CPC.
    
    API: phrase_this
    Docs: https://developer.semrush.com/api/v3/analytics/keyword-reports/
    
    Args:
        keyword: Keyword a analizar
        database: Base de datos regional (es, us, uk, etc.)
        
    Returns:
        Dict con métricas o None si falla
        {
            'keyword': str,
            'volume': int,           # Volumen mensual
            'difficulty': float,     # KD 0-100
            'cpc': float,           # CPC en USD
            'competition': float,    # Competencia 0-1
            'trend': list           # Tendencia 12 meses
        }
    """
    
    if not SEMRUSH_API_KEY:
        return None
    
    try:
        params = {
            'type': 'phrase_this',
            'key': SEMRUSH_API_KEY,
            'phrase': keyword,
            'database': database,
            'export_columns': 'Ph,Nq,Kd,Cp,Co,Nr,Td'
        }
        
        response = requests.get(SEMRUSH_BASE_URL, params=params, timeout=30)
        
        if response.status_code != 200:
            return None
        
        # Parsear respuesta (formato CSV)
        lines = response.text.strip().split('\n')
        if len(lines) < 2:
            return None
        
        # Primera línea: headers, segunda: datos
        headers = lines[0].split(';')
        values = lines[1].split(';')
        
        data = dict(zip(headers, values))
        
        return {
            'keyword': keyword,
            'volume': int(data.get('Search Volume', 0) or 0),
            'difficulty': float(data.get('Keyword Difficulty', 0) or 0),
            'cpc': float(data.get('CPC', 0) or 0),
            'competition': float(data.get('Competition', 0) or 0),
            'results': int(data.get('Number of Results', 0) or 0)
        }
    
    except Exception as e:
        st.warning(f"⚠️ Error en SEMrush API: {str(e)}")
        return None


def get_organic_results(keyword: str, database: str = DEFAULT_DATABASE, limit: int = 10) -> Optional[List[Dict]]:
    """
    Obtiene los top resultados orgánicos para una keyword.
    
    API: phrase_organic
    
    Args:
        keyword: Keyword a buscar
        database: Base de datos regional
        limit: Número de resultados (max 100)
        
    Returns:
        Lista de dicts con resultados orgánicos o None si falla
        [
            {
                'position': int,
                'url': str,
                'title': str,
                'domain': str,
                'traffic_percent': float
            }
        ]
    """
    
    if not SEMRUSH_API_KEY:
        return None
    
    try:
        params = {
            'type': 'phrase_organic',
            'key': SEMRUSH_API_KEY,
            'phrase': keyword,
            'database': database,
            'display_limit': min(limit, 100),
            'export_columns': 'Dn,Ur,Tt,Po,Tg'
        }
        
        response = requests.get(SEMRUSH_BASE_URL, params=params, timeout=30)
        
        if response.status_code != 200:
            return None
        
        # Parsear respuesta
        lines = response.text.strip().split('\n')
        if len(lines) < 2:
            return []
        
        headers = lines[0].split(';')
        results = []
        
        for line in lines[1:limit+1]:
            values = line.split(';')
            if len(values) >= len(headers):
                data = dict(zip(headers, values))
                results.append({
                    'position': int(data.get('Position', 0) or 0),
                    'url': data.get('Url', ''),
                    'title': data.get('Title', ''),
                    'domain': data.get('Domain', ''),
                    'traffic_percent': float(data.get('Traffic (%)', 0) or 0)
                })
        
        return results
    
    except Exception as e:
        st.warning(f"⚠️ Error obteniendo resultados orgánicos: {str(e)}")
        return None


def get_competitor_analysis(keyword: str, database: str = DEFAULT_DATABASE) -> Optional[Dict]:
    """
    Análisis completo de competidores para una keyword.
    
    Combina keyword overview + organic results.
    
    Args:
        keyword: Keyword objetivo
        database: Base de datos regional
        
    Returns:
        Dict con análisis completo o None si falla
    """
    
    # Obtener métricas de keyword
    keyword_data = get_keyword_overview(keyword, database)
    
    # Obtener resultados orgánicos
    organic_results = get_organic_results(keyword, database, limit=10)
    
    if not keyword_data and not organic_results:
        return None
    
    return {
        'keyword': keyword,
        'metrics': keyword_data or {},
        'organic_results': organic_results or [],
        'top_5_urls': [r['url'] for r in (organic_results or [])[:5]],
        'has_data': bool(keyword_data or organic_results)
    }


# ============================================================================
# SCRAPING DE CONTENIDO DE URLs
# ============================================================================

def scrape_competitor_content(url: str) -> Optional[Dict]:
    """
    Scrapea el contenido de una URL competidora.
    
    Args:
        url: URL a scrapear
        
    Returns:
        Dict con contenido o None si falla
    """
    
    from bs4 import BeautifulSoup
    from config.settings import USER_AGENT, ZENROWS_API_KEY
    
    headers = {
        'User-Agent': USER_AGENT,
        'Accept': 'text/html,application/xhtml+xml',
        'Accept-Language': 'es-ES,es;q=0.9'
    }
    
    try:
        # Intentar con Zenrows si está configurado (mejor para JS)
        if ZENROWS_API_KEY:
            zenrows_url = f"https://api.zenrows.com/v1/?apikey={ZENROWS_API_KEY}&url={url}&js_render=true"
            response = requests.get(zenrows_url, timeout=60)
        else:
            # Fallback a requests directo
            response = requests.get(url, headers=headers, timeout=30)
        
        if response.status_code != 200:
            return None
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extraer título
        title = ""
        title_tag = soup.find('title')
        if title_tag:
            title = title_tag.get_text(strip=True)
        
        # Extraer contenido principal
        # Intentar varios selectores comunes
        content = ""
        for selector in ['article', 'main', '.content', '.post-content', '#content', '.entry-content']:
            element = soup.select_one(selector)
            if element:
                content = element.get_text(' ', strip=True)
                break
        
        # Fallback: todo el body
        if not content:
            body = soup.find('body')
            if body:
                # Eliminar scripts, styles, nav, footer
                for tag in body(['script', 'style', 'nav', 'footer', 'header', 'aside']):
                    tag.decompose()
                content = body.get_text(' ', strip=True)
        
        # Contar palabras
        word_count = len(content.split()) if content else 0
        
        return {
            'url': url,
            'title': title,
            'content': content[:5000],  # Limitar a 5000 chars
            'word_count': word_count
        }
    
    except Exception as e:
        return {
            'url': url,
            'title': 'Error al scrapear',
            'content': f'No se pudo acceder: {str(e)}',
            'word_count': 0,
            'error': True
        }


def fetch_competitors_with_content(keyword: str, database: str = DEFAULT_DATABASE) -> Tuple[Optional[Dict], List[Dict]]:
    """
    Obtiene análisis de keyword + contenido scrapeado de top 5 competidores.
    
    Args:
        keyword: Keyword objetivo
        database: Base de datos regional
        
    Returns:
        Tuple: (keyword_analysis, competitors_with_content)
    """
    
    # Obtener análisis de SEMrush
    analysis = get_competitor_analysis(keyword, database)
    
    if not analysis or not analysis.get('top_5_urls'):
        return analysis, []
    
    # Scrapear contenido de cada URL
    competitors_content = []
    
    for i, url in enumerate(analysis['top_5_urls'][:5], 1):
        with st.spinner(f"Scrapeando competidor {i}/5: {url[:50]}..."):
            content_data = scrape_competitor_content(url)
            
            if content_data:
                # Añadir datos de posición de SEMrush
                organic_data = next(
                    (r for r in analysis['organic_results'] if r['url'] == url), 
                    {}
                )
                content_data['ranking_position'] = organic_data.get('position', i)
                content_data['traffic_percent'] = organic_data.get('traffic_percent', 0)
                
                competitors_content.append(content_data)
    
    return analysis, competitors_content


# ============================================================================
# CÁLCULO DE POTENCIAL
# ============================================================================

def calculate_keyword_potential(
    semrush_data: Optional[Dict],
    gsc_analysis: Optional[Dict]
) -> Dict:
    """
    Calcula el potencial de una keyword combinando SEMrush + GSC.
    
    Métricas:
    - opportunity_score: 0-100, qué tan buena es la oportunidad
    - traffic_potential: Tráfico mensual estimado si rankeas #1
    - difficulty_assessment: Evaluación de dificultad
    - recommendation: Recomendación de acción
    
    Args:
        semrush_data: Datos de SEMrush (keyword overview)
        gsc_analysis: Análisis de GSC (si ya rankeamos)
        
    Returns:
        Dict con métricas de potencial
    """
    
    result = {
        'opportunity_score': 0,
        'traffic_potential': 0,
        'current_traffic': 0,
        'growth_potential': 0,
        'difficulty': 'unknown',
        'recommendation': 'insufficient_data',
        'details': {}
    }
    
    # Si no hay datos de SEMrush
    if not semrush_data or not semrush_data.get('metrics'):
        return result
    
    metrics = semrush_data['metrics']
    volume = metrics.get('volume', 0)
    kd = metrics.get('difficulty', 50)
    
    # Tráfico potencial (CTR estimado por posición)
    # Posición 1: ~30% CTR, Posición 2: ~15%, etc.
    ctr_by_position = {1: 0.30, 2: 0.15, 3: 0.10, 4: 0.07, 5: 0.05}
    
    # Calcular tráfico potencial si alcanzamos posición 1
    result['traffic_potential'] = int(volume * 0.30)
    
    # Si ya rankeamos (datos de GSC)
    if gsc_analysis and gsc_analysis.get('has_matches'):
        current_position = gsc_analysis.get('best_position', 50)
        current_clicks = gsc_analysis.get('total_clicks', 0)
        
        result['current_traffic'] = current_clicks
        result['current_position'] = current_position
        
        # Calcular potencial de crecimiento
        current_ctr = ctr_by_position.get(int(current_position), 0.02)
        potential_ctr = 0.30  # Si llegamos a posición 1
        
        result['growth_potential'] = int(volume * (potential_ctr - current_ctr))
    else:
        result['growth_potential'] = result['traffic_potential']
    
    # Evaluar dificultad
    if kd < 30:
        result['difficulty'] = 'easy'
        difficulty_score = 90
    elif kd < 50:
        result['difficulty'] = 'medium'
        difficulty_score = 70
    elif kd < 70:
        result['difficulty'] = 'hard'
        difficulty_score = 40
    else:
        result['difficulty'] = 'very_hard'
        difficulty_score = 20
    
    # Calcular opportunity score
    # Factores: volumen (40%), dificultad (40%), competencia (20%)
    volume_score = min(100, (volume / 1000) * 100) if volume < 10000 else 100
    
    result['opportunity_score'] = int(
        volume_score * 0.4 +
        difficulty_score * 0.4 +
        (100 - metrics.get('competition', 0.5) * 100) * 0.2
    )
    
    # Generar recomendación
    if result['opportunity_score'] >= 70 and kd < 50:
        result['recommendation'] = 'high_priority'
        result['recommendation_text'] = '🟢 Alta prioridad: Buen volumen y dificultad manejable'
    elif result['opportunity_score'] >= 50:
        result['recommendation'] = 'medium_priority'
        result['recommendation_text'] = '🟡 Prioridad media: Evaluar competencia antes de invertir'
    elif volume > 500:
        result['recommendation'] = 'long_term'
        result['recommendation_text'] = '🔵 Largo plazo: Alto volumen pero difícil, requiere estrategia'
    else:
        result['recommendation'] = 'low_priority'
        result['recommendation_text'] = '⚪ Baja prioridad: Poco volumen o muy difícil'
    
    # Detalles adicionales
    result['details'] = {
        'monthly_volume': volume,
        'keyword_difficulty': kd,
        'cpc': metrics.get('cpc', 0),
        'competition': metrics.get('competition', 0)
    }
    
    return result


# ============================================================================
# VALIDACIÓN DE API KEY
# ============================================================================

def validate_semrush_api_key() -> bool:
    """
    Valida que la API key de SEMrush funcione.
    
    Returns:
        bool: True si la API key es válida
    """
    
    if not SEMRUSH_API_KEY:
        return False
    
    try:
        # Hacer una petición simple de prueba
        params = {
            'type': 'phrase_this',
            'key': SEMRUSH_API_KEY,
            'phrase': 'test',
            'database': 'us',
            'export_columns': 'Ph'
        }
        
        response = requests.get(SEMRUSH_BASE_URL, params=params, timeout=10)
        
        # Si devuelve error de API key
        if 'ERROR' in response.text and 'API key' in response.text:
            return False
        
        return response.status_code == 200
    
    except:
        return False


# ============================================================================
# CONSTANTES
# ============================================================================

__version__ = "4.1.1"

# Mapeo de dificultad a texto
DIFFICULTY_LABELS = {
    'easy': '🟢 Fácil (KD < 30)',
    'medium': '🟡 Media (KD 30-50)',
    'hard': '🟠 Difícil (KD 50-70)',
    'very_hard': '🔴 Muy difícil (KD > 70)',
    'unknown': '⚪ Desconocida'
}

# Mapeo de recomendación a color
RECOMMENDATION_COLORS = {
    'high_priority': 'green',
    'medium_priority': 'orange',
    'long_term': 'blue',
    'low_priority': 'gray',
    'insufficient_data': 'gray'
}
