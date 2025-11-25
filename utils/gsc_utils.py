"""
Utilidades de Google Search Console - PcComponentes Content Generator
Versión 4.1.1

Funciones para procesar y analizar datos de GSC desde CSV.
Incluye detección de keywords existentes, análisis de canibalización,
y validación de freshness de datos.

Autor: PcComponentes - Product Discovery & Content
"""

import pandas as pd
import streamlit as st
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import re
from difflib import SequenceMatcher


# ============================================================================
# CONFIGURACIÓN
# ============================================================================

# Ruta al CSV de GSC (puede configurarse en settings.py)
DEFAULT_GSC_CSV_PATH = "gsc_keywords.csv"

# Período del dataset actual
DATASET_START_DATE = datetime(2025, 10, 18)
DATASET_END_DATE = datetime(2025, 11, 17)

# Umbrales de alerta
DAYS_WARNING_THRESHOLD = 30  # Avisar si datos tienen más de 30 días
DAYS_CRITICAL_THRESHOLD = 60  # Crítico si más de 60 días

# Umbrales de matching
EXACT_MATCH_THRESHOLD = 1.0  # Match exacto
HIGH_SIMILARITY_THRESHOLD = 0.85  # Muy similar
MEDIUM_SIMILARITY_THRESHOLD = 0.70  # Similar
CONTAINS_MATCH = True  # También buscar si keyword está contenida


# ============================================================================
# CARGA Y PROCESAMIENTO DEL CSV
# ============================================================================

@st.cache_data(ttl=3600)  # Cache por 1 hora
def load_gsc_data(csv_path: str = DEFAULT_GSC_CSV_PATH) -> Optional[pd.DataFrame]:
    """
    Carga el CSV de datos de Google Search Console.
    
    Args:
        csv_path: Ruta al archivo CSV
        
    Returns:
        DataFrame con los datos o None si falla
        
    Notes:
        - Usa cache de Streamlit para evitar recargas
        - Valida estructura del CSV
        - Filtra y limpia datos según criterios
    """
    
    try:
        # Cargar CSV
        df = pd.read_csv(csv_path, sep=None, engine='python')
        
        # Validar columnas requeridas
        required_columns = ['page', 'query', 'clicks', 'impressions', 'ctr', 'position']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            st.error(f"❌ Columnas faltantes en CSV: {', '.join(missing_columns)}")
            return None
        
        # Convertir tipos
        df['clicks'] = pd.to_numeric(df['clicks'], errors='coerce')
        df['impressions'] = pd.to_numeric(df['impressions'], errors='coerce')
        df['position'] = pd.to_numeric(df['position'], errors='coerce')
        df['ctr'] = pd.to_numeric(df['ctr'], errors='coerce')
        
        # Eliminar filas con valores nulos en columnas críticas
        df = df.dropna(subset=['page', 'query', 'position', 'impressions'])
        
        # Ya viene filtrado del CSV, pero por si acaso validamos
        df = df[
            (df['position'] <= 50) &
            (df['impressions'] >= 10) &
            (~df['query'].str.contains('pccomponentes|pccom', case=False, na=False)) &
            (df['query'].str.len() <= 100)
        ]
        
        # Ordenar por clics descendente
        df = df.sort_values('clicks', ascending=False)
        
        return df
    
    except FileNotFoundError:
        st.error(f"❌ No se encontró el archivo CSV: {csv_path}")
        return None
    
    except Exception as e:
        st.error(f"❌ Error al cargar CSV de GSC: {str(e)}")
        return None


def get_top_query_by_url(df: pd.DataFrame) -> Dict[str, Dict]:
    """
    Obtiene la top query para cada URL (la que más clics genera).
    
    Args:
        df: DataFrame con datos de GSC
        
    Returns:
        Dict con URL como key y dict con info de top query
        
    Example:
        {
            'https://example.com/page': {
                'query': 'mejor producto',
                'clicks': 150,
                'impressions': 5000,
                'position': 5.2,
                'ctr': 0.03
            }
        }
    """
    
    top_queries = {}
    
    # Agrupar por página y obtener la query con más clics
    for page in df['page'].unique():
        page_data = df[df['page'] == page].sort_values('clicks', ascending=False).iloc[0]
        
        top_queries[page] = {
            'query': page_data['query'],
            'clicks': int(page_data['clicks']),
            'impressions': int(page_data['impressions']),
            'position': round(float(page_data['position']), 1),
            'ctr': round(float(page_data['ctr']), 4)
        }
    
    return top_queries


# ============================================================================
# BÚSQUEDA Y MATCHING DE KEYWORDS
# ============================================================================

def calculate_similarity(str1: str, str2: str) -> float:
    """
    Calcula la similitud entre dos strings.
    
    Args:
        str1: Primera string
        str2: Segunda string
        
    Returns:
        float: Similitud entre 0.0 y 1.0
        
    Notes:
        - Usa SequenceMatcher para similitud
        - Normaliza a lowercase
        - Ignora espacios extras
    """
    
    # Normalizar
    s1 = ' '.join(str1.lower().strip().split())
    s2 = ' '.join(str2.lower().strip().split())
    
    return SequenceMatcher(None, s1, s2).ratio()


def find_keyword_matches(
    keyword: str,
    df: pd.DataFrame,
    include_variations: bool = True
) -> List[Dict]:
    """
    Busca matches de una keyword en el dataset de GSC.
    
    Args:
        keyword: Keyword a buscar
        df: DataFrame con datos de GSC
        include_variations: Si True, incluye variaciones similares
        
    Returns:
        Lista de dicts con matches encontrados, ordenados por relevancia
        
    Notes:
        - Match exacto tiene prioridad máxima
        - Luego matches por similitud
        - Finalmente matches por contención
    """
    
    matches = []
    keyword_norm = keyword.lower().strip()
    
    # Iterar sobre queries únicas
    for query in df['query'].unique():
        query_norm = query.lower().strip()
        
        # Tipo de match
        match_type = None
        similarity = 0.0
        
        # 1. Match exacto
        if query_norm == keyword_norm:
            match_type = 'exact'
            similarity = 1.0
        
        # 2. Match por similitud alta (si está habilitado)
        elif include_variations:
            similarity = calculate_similarity(keyword_norm, query_norm)
            
            if similarity >= HIGH_SIMILARITY_THRESHOLD:
                match_type = 'high_similarity'
            elif similarity >= MEDIUM_SIMILARITY_THRESHOLD:
                match_type = 'medium_similarity'
        
        # 3. Match por contención (si está habilitado)
        if match_type is None and include_variations and CONTAINS_MATCH:
            if keyword_norm in query_norm or query_norm in keyword_norm:
                match_type = 'contains'
                similarity = 0.6  # Similitud base para contención
        
        # Si hay match, agregar a resultados
        if match_type:
            # Obtener todas las URLs que rankean para esta query
            query_data = df[df['query'] == query].sort_values('position')
            
            for _, row in query_data.iterrows():
                matches.append({
                    'query': query,
                    'url': row['page'],
                    'match_type': match_type,
                    'similarity': similarity,
                    'position': round(float(row['position']), 1),
                    'clicks': int(row['clicks']),
                    'impressions': int(row['impressions']),
                    'ctr': round(float(row['ctr']), 4)
                })
    
    # Ordenar por relevancia: tipo de match > posición > clics
    match_priority = {
        'exact': 4,
        'high_similarity': 3,
        'medium_similarity': 2,
        'contains': 1
    }
    
    matches.sort(
        key=lambda x: (
            match_priority.get(x['match_type'], 0),
            -x['clicks'],  # Más clics primero
            x['position']  # Mejor posición primero
        ),
        reverse=True
    )
    
    return matches


def check_cannibalization_risk(matches: List[Dict]) -> Tuple[bool, str, List[str]]:
    """
    Analiza si hay riesgo de canibalización de keywords.
    
    Args:
        matches: Lista de matches encontrados
        
    Returns:
        Tuple: (hay_riesgo, nivel_riesgo, urls_afectadas)
        - hay_riesgo: bool
        - nivel_riesgo: 'none', 'low', 'medium', 'high'
        - urls_afectadas: lista de URLs que compiten
        
    Notes:
        - Riesgo alto: 3+ URLs en top 20
        - Riesgo medio: 2+ URLs en top 30
        - Riesgo bajo: 2+ URLs en top 50
    """
    
    if not matches:
        return False, 'none', []
    
    # Contar URLs únicas que rankean
    urls_by_position = {}
    
    for match in matches:
        pos = match['position']
        url = match['url']
        
        if url not in urls_by_position:
            urls_by_position[url] = pos
    
    # Analizar distribución
    urls_top_20 = [url for url, pos in urls_by_position.items() if pos <= 20]
    urls_top_30 = [url for url, pos in urls_by_position.items() if pos <= 30]
    urls_top_50 = [url for url, pos in urls_by_position.items() if pos <= 50]
    
    # Determinar nivel de riesgo
    if len(urls_top_20) >= 3:
        return True, 'high', urls_top_20
    elif len(urls_top_30) >= 2:
        return True, 'medium', urls_top_30
    elif len(urls_top_50) >= 2:
        return True, 'low', urls_top_50
    
    return False, 'none', []


# ============================================================================
# VALIDACIÓN DE FRESHNESS DE DATOS
# ============================================================================

def get_dataset_age() -> Dict:
    """
    Calcula la antigüedad del dataset de GSC.
    
    Returns:
        Dict con información de freshness:
        - days_since_end: días desde el fin del período
        - is_fresh: bool (< 30 días)
        - needs_update: bool (> 30 días)
        - is_critical: bool (> 60 días)
        - warning_message: mensaje descriptivo
        - dataset_period: string con el período
        
    Notes:
        - Dataset actual: 18 oct - 17 nov 2025
        - Warning a partir de 30 días
        - Crítico a partir de 60 días
    """
    
    today = datetime.now()
    days_since_end = (today - DATASET_END_DATE).days
    
    # Determinar estado
    is_fresh = days_since_end <= DAYS_WARNING_THRESHOLD
    needs_update = days_since_end > DAYS_WARNING_THRESHOLD
    is_critical = days_since_end > DAYS_CRITICAL_THRESHOLD
    
    # Mensaje de warning
    if is_critical:
        warning_message = (
            f"⚠️ **DATOS CRÍTICOS**: El dataset tiene {days_since_end} días de antigüedad. "
            f"Se recomienda encarecidamente actualizar los datos de GSC."
        )
    elif needs_update:
        warning_message = (
            f"⚠️ **ACTUALIZACIÓN RECOMENDADA**: El dataset tiene {days_since_end} días de antigüedad. "
            f"Considera actualizar los datos de GSC para mayor precisión."
        )
    else:
        warning_message = (
            f"✅ **DATOS ACTUALIZADOS**: El dataset tiene {days_since_end} días de antigüedad. "
            f"Los datos son recientes y confiables."
        )
    
    # Formatear período
    period_str = f"{DATASET_START_DATE.strftime('%d %b %Y')} - {DATASET_END_DATE.strftime('%d %b %Y')}"
    
    return {
        'days_since_end': days_since_end,
        'is_fresh': is_fresh,
        'needs_update': needs_update,
        'is_critical': is_critical,
        'warning_message': warning_message,
        'dataset_period': period_str,
        'dataset_start': DATASET_START_DATE,
        'dataset_end': DATASET_END_DATE
    }


def get_recommended_update_date() -> str:
    """
    Calcula la fecha recomendada para actualizar el dataset.
    
    Returns:
        String con la fecha recomendada
        
    Notes:
        - Recomendación: actualizar cada 30 días
    """
    
    recommended_date = DATASET_END_DATE + timedelta(days=DAYS_WARNING_THRESHOLD)
    
    if datetime.now() > recommended_date:
        return f"**Vencida** (debería haberse actualizado el {recommended_date.strftime('%d/%m/%Y')})"
    else:
        return recommended_date.strftime('%d/%m/%Y')


# ============================================================================
# FUNCIONES DE ANÁLISIS
# ============================================================================

def analyze_keyword_coverage(keyword: str, df: pd.DataFrame) -> Dict:
    """
    Análisis completo de cobertura de una keyword en GSC.
    
    Args:
        keyword: Keyword a analizar
        df: DataFrame con datos de GSC
        
    Returns:
        Dict con análisis completo:
        - has_matches: bool
        - matches: lista de matches
        - best_ranking_url: mejor URL rankeando
        - best_position: mejor posición
        - total_clicks: total de clics para esta keyword
        - cannibalization: info de canibalización
        - recommendation: recomendación de acción
    """
    
    matches = find_keyword_matches(keyword, df, include_variations=True)
    
    if not matches:
        return {
            'has_matches': False,
            'matches': [],
            'best_ranking_url': None,
            'best_position': None,
            'total_clicks': 0,
            'cannibalization': {
                'has_risk': False,
                'level': 'none',
                'affected_urls': []
            },
            'recommendation': 'create_new'
        }
    
    # Mejor ranking
    best_match = matches[0]
    
    # Total de clics
    total_clicks = sum(m['clicks'] for m in matches)
    
    # Análisis de canibalización
    has_risk, risk_level, affected_urls = check_cannibalization_risk(matches)
    
    # Recomendación
    if best_match['match_type'] == 'exact' and best_match['position'] <= 10:
        recommendation = 'already_ranking_well'
    elif has_risk and risk_level in ['high', 'medium']:
        recommendation = 'consolidate_content'
    elif best_match['position'] > 30:
        recommendation = 'improve_existing_or_create_new'
    else:
        recommendation = 'improve_existing'
    
    return {
        'has_matches': True,
        'matches': matches,
        'best_ranking_url': best_match['url'],
        'best_position': best_match['position'],
        'total_clicks': total_clicks,
        'cannibalization': {
            'has_risk': has_risk,
            'level': risk_level,
            'affected_urls': affected_urls
        },
        'recommendation': recommendation
    }


# ============================================================================
# CONSTANTES Y CONFIGURACIÓN
# ============================================================================

# Versión del módulo
__version__ = "4.1.1"

# Mapeo de recomendaciones a mensajes
RECOMMENDATION_MESSAGES = {
    'create_new': '✅ **Crear contenido nuevo**: No hay contenido rankeando para esta keyword.',
    'already_ranking_well': '⚠️ **Ya rankeas bien**: Tienes contenido en top 10. Considera si realmente necesitas nuevo contenido.',
    'consolidate_content': '⚠️ **Consolidar contenido**: Múltiples URLs compiten. Considera consolidar en una sola página.',
    'improve_existing': '💡 **Mejorar existente**: Tienes contenido rankeando pero puede mejorarse.',
    'improve_existing_or_create_new': '💡 **Mejorar o crear**: El contenido actual rankea bajo. Evalúa si mejorar o crear nuevo.'
}

# Mapeo de niveles de riesgo a colores
RISK_LEVEL_COLORS = {
    'none': 'green',
    'low': 'blue',
    'medium': 'orange',
    'high': 'red'
}

# Mapeo de tipos de match a descripciones
MATCH_TYPE_DESCRIPTIONS = {
    'exact': '🎯 Match Exacto',
    'high_similarity': '🔸 Muy Similar',
    'medium_similarity': '🔹 Similar',
    'contains': '📝 Contenida'
}
