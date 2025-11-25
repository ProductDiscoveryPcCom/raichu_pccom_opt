"""
UI de Google Search Console - PcComponentes Content Generator
Versión 4.1.1

Componente de interfaz para verificación de keywords en Google Search Console.
Muestra si la keyword ya rankea, análisis de canibalización, y recomendaciones.

Autor: PcComponentes - Product Discovery & Content
"""

import streamlit as st
from typing import Optional
import pandas as pd

# Importar utilidades GSC
from utils.gsc_utils import (
    load_gsc_data,
    get_dataset_age,
    get_recommended_update_date,
    analyze_keyword_coverage,
    RECOMMENDATION_MESSAGES,
    RISK_LEVEL_COLORS,
    MATCH_TYPE_DESCRIPTIONS
)


# ============================================================================
# FUNCIÓN PRINCIPAL
# ============================================================================

def render_gsc_verification_section(
    keyword: str,
    csv_path: str = "gsc_keywords.csv",
    show_disclaimer: bool = True
) -> Optional[dict]:
    """
    Renderiza la sección completa de verificación GSC.
    
    Args:
        keyword: Keyword principal a verificar
        csv_path: Ruta al CSV de GSC
        show_disclaimer: Si mostrar el disclaimer de freshness
        
    Returns:
        Dict con resultado del análisis o None si no hay datos
        
    Notes:
        - Carga automáticamente el CSV
        - Muestra disclaimer de freshness
        - Analiza keyword y muestra resultados
        - Incluye recomendaciones accionables
    """
    
    st.markdown("### 🔍 Verificación en Google Search Console")
    
    st.info("""
    **¿Para qué sirve esto?**
    
    Verifica si ya tienes contenido rankeando para esta keyword (o variaciones similares) 
    para evitar **canibalización de keywords** - cuando múltiples URLs de tu sitio compiten 
    por la misma búsqueda, diluyendo tu autoridad.
    """)
    
    # Cargar datos de GSC
    df = load_gsc_data(csv_path)
    
    if df is None or df.empty:
        st.warning("⚠️ No se pudieron cargar los datos de Google Search Console. La verificación no está disponible.")
        return None
    
    # Mostrar disclaimer de freshness
    if show_disclaimer:
        render_dataset_freshness_warning()
    
    # Si no hay keyword, no hacer nada más
    if not keyword or len(keyword.strip()) < 3:
        st.info("👆 Introduce una keyword principal arriba para verificar si ya rankeas para ella.")
        return None
    
    # Analizar keyword
    with st.spinner(f"🔍 Verificando '{keyword}' en Google Search Console..."):
        analysis = analyze_keyword_coverage(keyword, df)
    
    # Mostrar resultados
    if analysis['has_matches']:
        render_matches_found(keyword, analysis)
    else:
        render_no_matches(keyword)
    
    # Guardar en session state
    st.session_state['gsc_analysis'] = analysis
    
    return analysis


# ============================================================================
# DISCLAIMER DE FRESHNESS
# ============================================================================

def render_dataset_freshness_warning() -> None:
    """
    Muestra un disclaimer sobre la antigüedad de los datos de GSC.
    
    Alerta si los datos tienen más de 30 días y son críticos si >60 días.
    """
    
    freshness = get_dataset_age()
    
    # Determinar tipo de alerta
    if freshness['is_critical']:
        alert_type = st.error
    elif freshness['needs_update']:
        alert_type = st.warning
    else:
        alert_type = st.success
    
    # Mostrar alerta
    with st.expander("📅 Información del Dataset de GSC", expanded=freshness['needs_update']):
        alert_type(freshness['warning_message'])
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Período del Dataset",
                freshness['dataset_period']
            )
        
        with col2:
            st.metric(
                "Antigüedad",
                f"{freshness['days_since_end']} días"
            )
        
        with col3:
            update_date = get_recommended_update_date()
            st.metric(
                "Próxima Actualización",
                update_date
            )
        
        if freshness['needs_update']:
            st.markdown("---")
            st.markdown("""
            **📋 Cómo actualizar el dataset:**
            
            1. Accede a [Google Search Console](https://search.google.com/search-console)
            2. Ve a **Rendimiento** > período de 30 días
            3. Exporta datos con filtros:
               - Posiciones ≤ 50
               - Impresiones ≥ 10
               - Excluir queries con 'pccomponentes', 'pccom'
               - Keywords ≤ 100 caracteres
            4. Reemplaza `gsc_keywords.csv` con el nuevo archivo
            5. Actualiza las fechas en `utils/gsc_utils.py`:
```python
               DATASET_START_DATE = datetime(YYYY, MM, DD)
               DATASET_END_DATE = datetime(YYYY, MM, DD)
```
            """)


# ============================================================================
# RESULTADOS: MATCHES ENCONTRADOS
# ============================================================================

def render_matches_found(keyword: str, analysis: dict) -> None:
    """
    Renderiza los resultados cuando se encuentran matches.
    
    Args:
        keyword: Keyword buscada
        analysis: Dict con el análisis completo
    """
    
    st.markdown("---")
    st.markdown("#### 📊 Resultados de la Verificación")
    
    # Métricas principales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "URLs Encontradas",
            len(set(m['url'] for m in analysis['matches']))
        )
    
    with col2:
        st.metric(
            "Mejor Posición",
            f"#{analysis['best_position']}"
        )
    
    with col3:
        st.metric(
            "Total Clics",
            f"{analysis['total_clicks']:,}"
        )
    
    with col4:
        risk_level = analysis['cannibalization']['level']
        risk_emoji = {
            'none': '✅',
            'low': '🟢',
            'medium': '🟡',
            'high': '🔴'
        }.get(risk_level, '❓')
        
        st.metric(
            "Riesgo Canibalización",
            f"{risk_emoji} {risk_level.upper()}"
        )
    
    # Recomendación
    recommendation = analysis['recommendation']
    rec_message = RECOMMENDATION_MESSAGES.get(recommendation, '')
    
    if 'already_ranking' in recommendation:
        st.warning(rec_message)
    elif 'consolidate' in recommendation:
        st.error(rec_message)
    elif 'create_new' in recommendation:
        st.success(rec_message)
    else:
        st.info(rec_message)
    
    # Análisis de canibalización
    if analysis['cannibalization']['has_risk']:
        render_cannibalization_warning(analysis['cannibalization'])
    
    # Tabla de matches
    render_matches_table(analysis['matches'])


def render_cannibalization_warning(cannibalization: dict) -> None:
    """
    Muestra warning de canibalización si aplica.
    
    Args:
        cannibalization: Dict con info de canibalización
    """
    
    risk_level = cannibalization['level']
    affected_urls = cannibalization['affected_urls']
    
    if not cannibalization['has_risk']:
        return
    
    # Color según nivel de riesgo
    if risk_level == 'high':
        alert_func = st.error
        icon = "🔴"
    elif risk_level == 'medium':
        alert_func = st.warning
        icon = "🟡"
    else:
        alert_func = st.info
        icon = "🟢"
    
    with st.expander(f"{icon} Detalle de Canibalización ({risk_level.upper()})", expanded=(risk_level in ['high', 'medium'])):
        alert_func(f"""
        **Múltiples URLs compitiendo por la misma keyword**
        
        Tienes {len(affected_urls)} URLs rankeando para esta keyword o variaciones similares.
        Esto puede estar diluyendo tu autoridad y dificultando que una página rankee bien.
        """)
        
        st.markdown("**URLs afectadas:**")
        for i, url in enumerate(affected_urls, 1):
            st.markdown(f"{i}. [{url}]({url})")
        
        st.markdown("---")
        st.markdown("""
        **💡 Recomendación:**
        
        - **Opción 1**: Consolidar todo en la mejor URL y redirigir las demás (301)
        - **Opción 2**: Diferenciar claramente cada URL para distintas intenciones de búsqueda
        - **Opción 3**: Evaluar si realmente necesitas nuevo contenido o mejorar el existente
        """)


def render_matches_table(matches: list) -> None:
    """
    Renderiza tabla con todos los matches encontrados.
    
    Args:
        matches: Lista de matches del análisis
    """
    
    with st.expander("📋 Ver Todas las URLs Rankeando", expanded=False):
        # Preparar datos para la tabla
        table_data = []
        
        for match in matches:
            table_data.append({
                'Query': match['query'],
                'Match': MATCH_TYPE_DESCRIPTIONS.get(match['match_type'], match['match_type']),
                'URL': match['url'],
                'Posición': f"#{match['position']}",
                'Clics': match['clicks'],
                'Impresiones': f"{match['impressions']:,}",
                'CTR': f"{match['ctr']:.2%}"
            })
        
        # Mostrar tabla
        df_matches = pd.DataFrame(table_data)
        
        st.dataframe(
            df_matches,
            use_container_width=True,
            hide_index=True,
            column_config={
                'URL': st.column_config.LinkColumn('URL'),
                'Posición': st.column_config.TextColumn('Posición'),
                'Clics': st.column_config.NumberColumn('Clics', format="%d"),
                'Impresiones': st.column_config.TextColumn('Impresiones'),
                'CTR': st.column_config.TextColumn('CTR')
            }
        )
        
        # Estadísticas
        st.markdown("---")
        st.markdown("**Estadísticas:**")
        
        stat_col1, stat_col2, stat_col3 = st.columns(3)
        
        with stat_col1:
            total_clicks = sum(m['clicks'] for m in matches)
            st.metric("Total Clics", f"{total_clicks:,}")
        
        with stat_col2:
            total_impressions = sum(m['impressions'] for m in matches)
            st.metric("Total Impresiones", f"{total_impressions:,}")
        
        with stat_col3:
            avg_position = sum(m['position'] for m in matches) / len(matches)
            st.metric("Posición Promedio", f"#{avg_position:.1f}")


# ============================================================================
# RESULTADOS: NO SE ENCONTRARON MATCHES
# ============================================================================

def render_no_matches(keyword: str) -> None:
    """
    Renderiza mensaje cuando no se encuentran matches.
    
    Args:
        keyword: Keyword buscada
    """
    
    st.markdown("---")
    st.success(f"""
    ✅ **No se encontró contenido rankeando para "{keyword}"**
    
    **Esto es bueno:** Puedes crear contenido nuevo sin riesgo de canibalización.
    
    💡 **Recomendación:** Procede con la generación de contenido para esta keyword.
    """)


# ============================================================================
# UTILIDADES
# ============================================================================

def get_gsc_summary_for_session_state(analysis: Optional[dict]) -> dict:
    """
    Prepara resumen de GSC para guardar en session state.
    
    Args:
        analysis: Resultado del análisis GSC
        
    Returns:
        Dict con resumen simplificado
    """
    
    if not analysis or not analysis['has_matches']:
        return {
            'has_matches': False,
            'can_proceed': True,
            'warning': None
        }
    
    # Determinar si se puede proceder
    can_proceed = analysis['recommendation'] != 'already_ranking_well'
    
    # Warning si hay canibalización alta
    warning = None
    if analysis['cannibalization']['level'] == 'high':
        warning = 'high_cannibalization'
    elif analysis['recommendation'] == 'already_ranking_well':
        warning = 'already_ranking_well'
    
    return {
        'has_matches': True,
        'can_proceed': can_proceed,
        'warning': warning,
        'best_position': analysis['best_position'],
        'total_urls': len(set(m['url'] for m in analysis['matches']))
    }


# ============================================================================
# CONSTANTES Y CONFIGURACIÓN
# ============================================================================

# Versión del módulo
__version__ = "4.1.1"
