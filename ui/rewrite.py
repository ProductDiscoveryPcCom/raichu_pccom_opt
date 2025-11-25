"""
UI de Reescritura - PcComponentes Content Generator
Versión 4.1.1

Este módulo maneja la interfaz de usuario para el modo REESCRITURA,
que analiza contenido competidor y genera una versión mejorada.
Incluye verificación GSC para evitar canibalización.

Flujo:
1. Input de keyword principal
2. Verificación GSC (nuevo)
3. Scraping automático de top 5 URLs competidoras
4. Análisis competitivo de contenido
5. Configuración de parámetros adicionales
6. Generación del contenido mejorado en 3 etapas

Autor: PcComponentes - Product Discovery & Content
"""

import streamlit as st
from typing import Dict, List, Optional, Tuple
import json

# Importar utilidades
from utils.html_utils import count_words_in_html

# Importar configuración
from config.settings import GSC_VERIFICATION_ENABLED

# Importar sección GSC
from ui.gsc_section import render_gsc_verification_section


# ============================================================================
# FUNCIÓN PRINCIPAL DE RENDERIZADO
# ============================================================================

def render_rewrite_section() -> Tuple[bool, Dict]:
    """
    Renderiza la sección completa del modo reescritura.
    
    Esta función gestiona toda la interfaz del modo reescritura, incluyendo:
    - Input de keyword y configuración
    - Verificación GSC
    - Scraping de URLs competidoras
    - Análisis competitivo
    - Configuración de parámetros de generación
    - Botón de inicio de generación
    
    Returns:
        Tuple[bool, Dict]: (debe_generar, config_dict)
        - debe_generar: True si el usuario quiere iniciar la generación
        - config_dict: Diccionario con toda la configuración necesaria
        
    Notes:
        - Usa st.session_state para mantener estado entre reruns
        - El scraping de competidores se hace automáticamente
        - Valida inputs antes de permitir generación
        - Incluye verificación GSC antes del scraping
    """
    
    st.markdown("## 🔄 Modo: Reescritura Competitiva")
    
    st.info("""
    **¿Qué hace el modo reescritura?**
    
    1. 🔍 Verifica si ya rankeas para esta keyword (GSC)
    2. 🔍 Analiza el contenido de los **top 5 resultados** que rankean para tu keyword
    3. 📊 Identifica **gaps de contenido** y oportunidades de mejora
    4. ✍️ Genera contenido **superior** que cubre todos los gaps
    5. 🎯 Te ayuda a **superar a la competencia** en Google
    
    Perfecto para: mejorar artículos existentes, crear contenido para keywords competitivas,
    superar contenido de competidores.
    """)
    
    # Inicializar estado si no existe
    if 'rewrite_competitors_data' not in st.session_state:
        st.session_state.rewrite_competitors_data = None
    if 'rewrite_analysis' not in st.session_state:
        st.session_state.rewrite_analysis = None
    if 'rewrite_gsc_analysis' not in st.session_state:
        st.session_state.rewrite_gsc_analysis = None
    
    # Paso 1: Keyword y verificación GSC
    st.markdown("---")
    st.markdown("### 🎯 Paso 1: Keyword Principal")
    
    keyword, should_search = render_keyword_input()
    
    # Verificación GSC (si está habilitada y hay keyword)
    gsc_analysis = None
    if GSC_VERIFICATION_ENABLED and keyword and len(keyword.strip()) >= 3:
        st.markdown("---")
        gsc_analysis = render_gsc_verification_section(
            keyword=keyword,
            show_disclaimer=True
        )
        st.session_state.rewrite_gsc_analysis = gsc_analysis
        
        # Advertencia si ya rankea bien
        if gsc_analysis and gsc_analysis.get('has_matches'):
            if gsc_analysis.get('recommendation') == 'already_ranking_well':
                st.warning("""
                ⚠️ **Precaución**: Ya rankeas en top 10 para esta keyword.
                
                Considera si realmente necesitas crear contenido nuevo o si deberías 
                mejorar el contenido existente.
                """)
    
    # Si hay que hacer búsqueda de competidores, ejecutar
    if should_search and keyword:
        # Advertencia final antes de scrapear
        if gsc_analysis and gsc_analysis.get('has_matches'):
            st.info("💡 Procederemos a analizar competidores. Recuerda que ya tienes contenido rankeando.")
        
        with st.spinner("🔍 Buscando y analizando competidores..."):
            competitors_data = fetch_competitors_content(keyword)
            st.session_state.rewrite_competitors_data = competitors_data
            
            if competitors_data:
                st.success(f"✅ Se analizaron {len(competitors_data)} competidores")
                st.rerun()
    
    # Mostrar competidores si existen
    if st.session_state.rewrite_competitors_data:
        st.markdown("---")
        render_competitors_summary(st.session_state.rewrite_competitors_data)
    
    # Paso 2: Configuración de parámetros
    st.markdown("---")
    st.markdown("### ⚙️ Paso 2: Configuración del Contenido")
    
    rewrite_config = render_rewrite_configuration(keyword)
    
    # Validar que todo esté listo para generar
    can_generate = validate_rewrite_inputs(
        keyword,
        st.session_state.rewrite_competitors_data,
        rewrite_config,
        gsc_analysis
    )
    
    # Botón de generación
    st.markdown("---")
    
    if not can_generate:
        st.warning("⚠️ Completa todos los pasos anteriores para poder generar el contenido.")
        return False, {}
    
    # Mostrar resumen antes de generar
    render_generation_summary(keyword, rewrite_config, gsc_analysis)
    
    # Botón grande de generación
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        start_generation = st.button(
            "🚀 Generar Contenido Mejorado",
            type="primary",
            use_container_width=True
        )
    
    if start_generation:
        # Preparar configuración completa
        full_config = prepare_rewrite_config(
            keyword=keyword,
            competitors_data=st.session_state.rewrite_competitors_data,
            rewrite_config=rewrite_config,
            gsc_analysis=gsc_analysis
        )
        return True, full_config
    
    return False, {}


# ============================================================================
# INPUT DE KEYWORD Y BÚSQUEDA
# ============================================================================

def render_keyword_input() -> Tuple[str, bool]:
    """
    Renderiza el input de keyword principal y botón de búsqueda.
    
    Returns:
        Tuple[str, bool]: (keyword, should_search)
        - keyword: Keyword introducida por el usuario
        - should_search: True si se debe ejecutar la búsqueda
        
    Notes:
        - Valida que la keyword no esté vacía
        - Detecta cambios en la keyword para limpiar datos previos
        - Sugiere keywords específicas para mejores resultados
    """
    
    st.markdown("""
    Introduce la **keyword principal** para la que quieres rankear.
    Buscaremos automáticamente los top 5 resultados y los analizaremos.
    """)
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        current_keyword = st.text_input(
            "Keyword principal *",
            placeholder="Ej: mejor portátil gaming 2025",
            help="Keyword específica para la que quieres crear/mejorar contenido",
            key="rewrite_keyword_input"
        )
    
    with col2:
        # Botón de búsqueda
        search_disabled = not current_keyword or len(current_keyword.strip()) < 3
        search_button = st.button(
            "🔍 Buscar Competidores",
            disabled=search_disabled,
            use_container_width=True,
            type="primary"
        )
    
    # Detectar si cambió la keyword para limpiar datos
    if 'last_rewrite_keyword' in st.session_state:
        if st.session_state.last_rewrite_keyword != current_keyword:
            # Limpiar datos de búsqueda anterior
            st.session_state.rewrite_competitors_data = None
            st.session_state.rewrite_analysis = None
            st.session_state.rewrite_gsc_analysis = None
    
    st.session_state.last_rewrite_keyword = current_keyword
    
    # Tips de keywords
    with st.expander("💡 Tips para elegir una buena keyword"):
        st.markdown("""
        **Keywords efectivas son:**
        - ✅ Específicas: "mejor portátil gaming 1000 euros" > "portátiles"
        - ✅ Con intención clara: "cómo elegir" o "mejor" > términos genéricos
        - ✅ Con volumen de búsqueda: Que la gente realmente busque
        - ✅ Relevantes para PcComponentes: Tecnología, productos, guías
        
        **Ejemplos buenos:**
        - "mejor ssd nvme calidad precio"
        - "portátil para edición de vídeo 2025"
        - "diferencias rtx 4070 vs 4080"
        - "cómo elegir monitor gaming"
        
        **⚠️ Importante:**
        - Verifica primero en GSC si ya rankeas para esta keyword
        - Evita canibalización creando contenido duplicado
        """)
    
    return current_keyword, search_button


# ============================================================================
# SCRAPING DE COMPETIDORES
# ============================================================================

def fetch_competitors_content(keyword: str) -> Optional[List[Dict]]:
    """
    Obtiene y analiza el contenido de los top 5 competidores para una keyword.
    
    Args:
        keyword: Keyword para buscar competidores
        
    Returns:
        Lista de dicts con datos de competidores o None si falla
        Cada dict contiene: url, title, content, word_count
        
    Notes:
        - Usa Google Custom Search API o similar
        - Scrapea contenido de cada URL (máximo 5)
        - Extrae título, contenido principal y word count
        - Maneja errores de scraping gracefully
    """
    
    try:
        # IMPORTANTE: Esta es una implementación simulada
        # En producción, deberías usar:
        # 1. Google Custom Search API para obtener URLs
        # 2. Beautiful Soup / Scrapy para scraping de contenido
        # 3. Zenrows o similar para JavaScript rendering
        
        st.warning("""
        ⚠️ **Nota de implementación**: Esta es una versión simulada.
        
        En producción, integrar con:
        - Google Custom Search API para obtener top URLs
        - Sistema de scraping robusto (Zenrows/BeautifulSoup)
        - Caché de resultados para evitar scraping repetido
        """)
        
        # Datos simulados de ejemplo
        competitors = [
            {
                'url': f'https://competitor1.com/article-about-{keyword.replace(" ", "-")}',
                'title': f'Guía Completa: {keyword.title()}',
                'content': generate_mock_competitor_content(keyword, 1500),
                'word_count': 1500,
                'ranking_position': 1
            },
            {
                'url': f'https://competitor2.com/{keyword.replace(" ", "-")}-review',
                'title': f'Review: {keyword.title()} - Análisis Detallado',
                'content': generate_mock_competitor_content(keyword, 1200),
                'word_count': 1200,
                'ranking_position': 2
            },
            {
                'url': f'https://competitor3.com/best-{keyword.replace(" ", "-")}',
                'title': f'Los Mejores {keyword.title()} de 2025',
                'content': generate_mock_competitor_content(keyword, 1800),
                'word_count': 1800,
                'ranking_position': 3
            },
            {
                'url': f'https://competitor4.com/{keyword.replace(" ", "-")}-guide',
                'title': f'{keyword.title()}: Guía de Compra',
                'content': generate_mock_competitor_content(keyword, 1400),
                'word_count': 1400,
                'ranking_position': 4
            },
            {
                'url': f'https://competitor5.com/choosing-{keyword.replace(" ", "-")}',
                'title': f'Cómo Elegir {keyword.title()}',
                'content': generate_mock_competitor_content(keyword, 1100),
                'word_count': 1100,
                'ranking_position': 5
            }
        ]
        
        return competitors
        
    except Exception as e:
        st.error(f"❌ Error al obtener competidores: {str(e)}")
        return None


def generate_mock_competitor_content(keyword: str, word_count: int) -> str:
    """
    Genera contenido mock de competidor para testing.
    
    Esta función es temporal y debe reemplazarse con scraping real.
    
    Args:
        keyword: Keyword del contenido
        word_count: Número aproximado de palabras a generar
        
    Returns:
        str: Contenido mock en texto plano
    """
    
    # Contenido genérico de ejemplo
    intro = f"En este artículo analizamos todo sobre {keyword}. "
    body = f"Cuando hablamos de {keyword}, es importante considerar varios factores. "
    body += "La calidad, el precio, las características y el rendimiento son aspectos clave. "
    body += f"Los mejores {keyword} del mercado ofrecen un equilibrio entre estas variables. "
    
    # Repetir hasta alcanzar word count aproximado
    content = intro
    words = len(content.split())
    
    while words < word_count:
        content += body
        words = len(content.split())
    
    return content[:word_count * 6]  # Aproximación por caracteres


# ============================================================================
# RESUMEN DE COMPETIDORES
# ============================================================================

def render_competitors_summary(competitors_data: List[Dict]) -> None:
    """
    Renderiza un resumen de los competidores analizados.
    
    Muestra:
    - Número de competidores analizados
    - Lista de URLs con títulos
    - Word count de cada competidor
    - Posición de ranking
    
    Args:
        competitors_data: Lista de dicts con datos de competidores
        
    Notes:
        - Muestra en formato tabla para fácil visualización
        - Incluye enlaces clickeables a las URLs
        - Destaca métricas clave
    """
    
    st.markdown("### 🏆 Competidores Analizados")
    
    # Métricas generales
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("📊 Competidores", len(competitors_data))
    
    with col2:
        avg_words = sum(c.get('word_count', 0) for c in competitors_data) / len(competitors_data)
        st.metric("📝 Promedio palabras", f"{int(avg_words):,}")
    
    with col3:
        total_words = sum(c.get('word_count', 0) for c in competitors_data)
        st.metric("💬 Total palabras", f"{total_words:,}")
    
    # Tabla de competidores
    st.markdown("**URLs Analizadas:**")
    
    for i, comp in enumerate(competitors_data, 1):
        with st.expander(f"#{comp.get('ranking_position', i)} - {comp.get('title', 'Sin título')}", expanded=False):
            col_a, col_b = st.columns([3, 1])
            
            with col_a:
                st.markdown(f"**URL:** [{comp.get('url', 'N/A')}]({comp.get('url', '#')})")
                st.caption(f"Contenido: {comp.get('word_count', 0):,} palabras")
            
            with col_b:
                st.metric("Posición", f"#{comp.get('ranking_position', i)}")
            
            # Preview del contenido
            content_preview = comp.get('content', '')[:300] + "..."
            st.text_area(
                "Preview del contenido",
                content_preview,
                height=100,
                disabled=True,
                key=f"preview_comp_{i}"
            )


# ============================================================================
# CONFIGURACIÓN DE REESCRITURA
# ============================================================================

def render_rewrite_configuration(keyword: str) -> Dict:
    """
    Renderiza los controles de configuración para la reescritura.
    
    Args:
        keyword: Keyword principal
        
    Returns:
        Dict con la configuración elegida por el usuario
        
    Notes:
        - Incluye inputs similares al modo nuevo pero simplificados
        - Arquetipo es opcional (se usa como referencia)
        - Algunos campos se auto-completan basándose en análisis
    """
    
    config = {}
    
    # Objetivo del contenido
    st.markdown("#### 📝 Información Básica")
    
    config['objetivo'] = st.text_area(
        "Objetivo del contenido *",
        placeholder="Ej: Crear la guía más completa sobre este tema para rankear #1 en Google",
        help="¿Qué quieres lograr con este contenido?",
        height=100
    )
    
    # Longitud objetivo
    col1, col2 = st.columns(2)
    
    with col1:
        config['target_length'] = st.number_input(
            "Longitud objetivo (palabras) *",
            min_value=800,
            max_value=3000,
            value=1600,
            step=100,
            help="Basado en el análisis competitivo, sugiere una longitud adecuada"
        )
    
    with col2:
        # Sugerencia basada en competidores
        if st.session_state.rewrite_competitors_data:
            avg_competitor_length = int(
                sum(c.get('word_count', 0) for c in st.session_state.rewrite_competitors_data) 
                / len(st.session_state.rewrite_competitors_data)
            )
            suggested = int(avg_competitor_length * 1.2)  # 20% más que el promedio
            
            st.info(f"💡 **Sugerencia**: ~{suggested:,} palabras\n\n"
                   f"(20% más que el promedio competidor: {avg_competitor_length:,})")
    
    # Keywords adicionales
    st.markdown("#### 🔑 Keywords SEO Adicionales")
    
    keywords_input = st.text_area(
        "Keywords secundarias (una por línea)",
        placeholder=f"{keyword}\nkeyword relacionada 1\nkeyword relacionada 2",
        help="Lista de keywords a integrar naturalmente en el contenido",
        height=100
    )
    
    config['keywords'] = [keyword] + [
        k.strip() for k in keywords_input.split('\n') 
        if k.strip() and k.strip() != keyword
    ]
    
    # Contexto adicional
    st.markdown("#### 📋 Contexto Adicional")
    
    config['context'] = st.text_area(
        "Contexto o información adicional (opcional)",
        placeholder="Información específica, datos internos, perspectiva única de PcComponentes...",
        help="Cualquier información adicional que ayude a mejorar el contenido",
        height=100
    )
    
    # Enlaces
    st.markdown("#### 🔗 Enlaces a Incluir")
    
    col_link1, col_link2 = st.columns(2)
    
    with col_link1:
        config['link_principal_url'] = st.text_input(
            "URL del enlace principal",
            placeholder="https://www.pccomponentes.com/categoria",
            help="Enlace principal a incluir en primeros párrafos"
        )
    
    with col_link2:
        config['link_principal_text'] = st.text_input(
            "Texto anchor del enlace",
            placeholder="Ej: portátiles gaming",
            help="Texto del enlace (debe ser natural y descriptivo)"
        )
    
    # Producto alternativo (opcional)
    st.markdown("#### 🎯 Producto Alternativo (opcional)")
    
    col_alt1, col_alt2 = st.columns(2)
    
    with col_alt1:
        config['producto_alternativo_url'] = st.text_input(
            "URL del producto alternativo",
            placeholder="https://www.pccomponentes.com/producto",
            help="Producto alternativo a mencionar en veredicto"
        )
    
    with col_alt2:
        config['producto_alternativo_text'] = st.text_input(
            "Texto del producto",
            placeholder="Nombre del producto",
            help="Nombre del producto alternativo"
        )
    
    # Arquetipo de referencia (opcional)
    st.markdown("#### 📚 Arquetipo de Referencia (opcional)")
    
    st.info("""
    En modo reescritura, el arquetipo es **opcional** y se usa solo como referencia estructural.
    El análisis competitivo tiene prioridad sobre el arquetipo.
    """)
    
    use_arquetipo = st.checkbox(
        "Usar arquetipo como referencia estructural",
        value=False,
        help="Si se activa, el arquetipo guiará la estructura básica"
    )
    
    if use_arquetipo:
        # Aquí deberías importar y usar la función de arquetipos
        # Por ahora, lista simplificada
        arquetipos_nombres = [
            "ARQ-4: Review/Análisis",
            "ARQ-7: Roundup/Mejores X",
            "ARQ-2: Guía Paso a Paso",
            "ARQ-3: Explicación/Educativo",
            "ARQ-5: Comparativa A vs B"
        ]
        
        config['arquetipo_codigo'] = st.selectbox(
            "Seleccionar arquetipo de referencia",
            arquetipos_nombres,
            help="Estructura base para organizar el contenido"
        )
    else:
        config['arquetipo_codigo'] = None
    
    return config


# ============================================================================
# VALIDACIÓN DE INPUTS
# ============================================================================

def validate_rewrite_inputs(
    keyword: str,
    competitors_data: Optional[List[Dict]],
    config: Dict,
    gsc_analysis: Optional[Dict]
) -> bool:
    """
    Valida que todos los inputs necesarios estén completos.
    
    Args:
        keyword: Keyword principal
        competitors_data: Datos de competidores scrapeados
        config: Configuración del usuario
        gsc_analysis: Análisis de GSC (opcional)
        
    Returns:
        bool: True si todos los inputs necesarios están completos
        
    Notes:
        - Valida campos obligatorios marcados con *
        - Muestra mensajes específicos de qué falta
        - Incluye warnings de GSC si aplica
    """
    
    missing = []
    
    # Validar keyword
    if not keyword or len(keyword.strip()) < 3:
        missing.append("Keyword principal")
    
    # Validar que se haya buscado competidores
    if not competitors_data or len(competitors_data) == 0:
        missing.append("Análisis de competidores (presiona 'Buscar Competidores')")
    
    # Validar objetivo
    if not config.get('objetivo') or len(config['objetivo'].strip()) < 10:
        missing.append("Objetivo del contenido")
    
    # Validar longitud
    if not config.get('target_length') or config['target_length'] < 800:
        missing.append("Longitud objetivo válida (mínimo 800 palabras)")
    
    # Si falta algo, mostrar
    if missing:
        st.warning(f"⚠️ **Faltan campos obligatorios:**\n\n" + "\n".join([f"- {m}" for m in missing]))
        return False
    
    # Warning de GSC (no bloquea, solo advierte)
    if gsc_analysis and gsc_analysis.get('has_matches'):
        if gsc_analysis.get('recommendation') == 'already_ranking_well':
            st.info("""
            💡 **Recuerda**: Ya rankeas en top 10 para esta keyword. 
            Evalúa si es mejor mejorar el contenido existente que crear uno nuevo.
            """)
    
    return True


# ============================================================================
# RESUMEN ANTES DE GENERAR
# ============================================================================

def render_generation_summary(keyword: str, config: Dict, gsc_analysis: Optional[Dict]) -> None:
    """
    Muestra un resumen de la configuración antes de generar.
    
    Args:
        keyword: Keyword principal
        config: Configuración del usuario
        gsc_analysis: Análisis de GSC (opcional)
        
    Notes:
        - Permite al usuario revisar todo antes de generar
        - Muestra los parámetros clave de forma visual
        - Incluye alertas de GSC si aplica
    """
    
    st.markdown("### 📋 Resumen de Generación")
    
    with st.container():
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Configuración básica:**")
            st.markdown(f"- 🎯 Keyword: `{keyword}`")
            st.markdown(f"- 📝 Longitud: `{config['target_length']:,}` palabras")
            st.markdown(f"- 🔑 Keywords adicionales: `{len(config.get('keywords', [])) - 1}`")
        
        with col2:
            st.markdown("**Análisis competitivo:**")
            if st.session_state.rewrite_competitors_data:
                n_comp = len(st.session_state.rewrite_competitors_data)
                st.markdown(f"- 🏆 Competidores analizados: `{n_comp}`")
                
                avg_words = sum(c.get('word_count', 0) for c in st.session_state.rewrite_competitors_data) / n_comp
                st.markdown(f"- 📊 Longitud promedio competencia: `{int(avg_words):,}`")
                
                diff = config['target_length'] - avg_words
                pct = (diff / avg_words * 100) if avg_words > 0 else 0
                st.markdown(f"- 📈 Nuestro diferencial: `{pct:+.0f}%`")
            
            # Info de GSC si existe
            if gsc_analysis and gsc_analysis.get('has_matches'):
                st.markdown(f"- ⚠️ GSC: `{len(set(m['url'] for m in gsc_analysis['matches']))} URLs rankeando`")
    
    st.info("""
    ✅ Todo listo para generar. El proceso tomará unos minutos e incluirá:
    1. Análisis competitivo detallado
    2. Generación del borrador mejorado
    3. Análisis crítico
    4. Versión final optimizada que supera a la competencia
    """)


# ============================================================================
# PREPARACIÓN DE CONFIGURACIÓN FINAL
# ============================================================================

def prepare_rewrite_config(
    keyword: str,
    competitors_data: List[Dict],
    rewrite_config: Dict,
    gsc_analysis: Optional[Dict]
) -> Dict:
    """
    Prepara la configuración completa para el proceso de generación.
    
    Args:
        keyword: Keyword principal
        competitors_data: Datos de competidores
        rewrite_config: Configuración del usuario
        gsc_analysis: Análisis de GSC (opcional)
        
    Returns:
        Dict con toda la configuración necesaria para generar
        
    Notes:
        - Combina todos los datos en un dict estructurado
        - Incluye referencias al análisis competitivo
        - Incluye análisis de GSC si existe
        - Listo para pasar al generador
    """
    
    # Configuración base
    config = {
        'mode': 'rewrite',
        'keyword': keyword,
        'target_length': rewrite_config['target_length'],
        'objetivo': rewrite_config['objetivo'],
        'keywords': rewrite_config.get('keywords', [keyword]),
        'context': rewrite_config.get('context', ''),
    }
    
    # Enlaces
    config['links'] = {
        'principal': {
            'url': rewrite_config.get('link_principal_url', ''),
            'text': rewrite_config.get('link_principal_text', '')
        },
        'secundarios': []  # Se pueden añadir más si se implementa
    }
    
    # Producto alternativo
    config['producto_alternativo'] = {
        'url': rewrite_config.get('producto_alternativo_url', ''),
        'text': rewrite_config.get('producto_alternativo_text', '')
    }
    
    # Datos de competidores
    config['competitors_data'] = competitors_data
    
    # Análisis de GSC
    config['gsc_analysis'] = gsc_analysis
    
    # Arquetipo de referencia (opcional)
    config['arquetipo_codigo'] = rewrite_config.get('arquetipo_codigo')
    
    # PDP data (no aplica en modo rewrite típicamente)
    config['pdp_data'] = None
    
    # Campos específicos de arquetipo (no aplica en modo rewrite)
    config['campos_arquetipo'] = {}
    
    # Timestamp para tracking
    from datetime import datetime
    config['timestamp'] = datetime.now().isoformat()
    
    return config


# ============================================================================
# FUNCIONES AUXILIARES
# ============================================================================

def get_competitor_summary_stats(competitors_data: List[Dict]) -> Dict:
    """
    Calcula estadísticas resumen de los competidores.
    
    Args:
        competitors_data: Lista de dicts con datos de competidores
        
    Returns:
        Dict con estadísticas: avg_words, max_words, min_words, total_words
    """
    
    if not competitors_data:
        return {
            'avg_words': 0,
            'max_words': 0,
            'min_words': 0,
            'total_words': 0
        }
    
    word_counts = [c.get('word_count', 0) for c in competitors_data]
    
    return {
        'avg_words': sum(word_counts) / len(word_counts),
        'max_words': max(word_counts),
        'min_words': min(word_counts),
        'total_words': sum(word_counts)
    }


def suggest_optimal_length(competitors_data: List[Dict]) -> int:
    """
    Sugiere una longitud óptima basada en el análisis competitivo.
    
    Args:
        competitors_data: Lista de dicts con datos de competidores
        
    Returns:
        int: Longitud sugerida en palabras
        
    Notes:
        - Usa estrategia de "superar al promedio en 20%"
        - Considera el rango de la competencia
        - Límites: mínimo 800, máximo 3000
    """
    
    if not competitors_data:
        return 1600  # Default
    
    stats = get_competitor_summary_stats(competitors_data)
    
    # Estrategia: 20% más que el promedio
    suggested = int(stats['avg_words'] * 1.2)
    
    # Aplicar límites
    suggested = max(800, min(3000, suggested))
    
    return suggested


def format_competitors_for_prompt(competitors_data: List[Dict]) -> List[Dict[str, str]]:
    """
    Formatea los datos de competidores para incluir en el prompt.
    
    Args:
        competitors_data: Lista de dicts con datos crudos
        
    Returns:
        Lista de dicts formateados con 'url', 'title', 'content'
        
    Notes:
        - Limita contenido a longitud razonable
        - Limpia HTML si es necesario
        - Incluye solo campos relevantes
    """
    
    formatted = []
    
    for comp in competitors_data[:5]:  # Máximo 5
        formatted.append({
            'url': comp.get('url', ''),
            'title': comp.get('title', ''),
            'content': comp.get('content', '')[:3000]  # Limitar a 3000 chars
        })
    
    return formatted


# ============================================================================
# HELP Y DOCUMENTACIÓN
# ============================================================================

def render_rewrite_help() -> None:
    """
    Renderiza información de ayuda sobre el modo reescritura.
    """
    
    with st.expander("ℹ️ Ayuda: Modo Reescritura"):
        st.markdown("""
        ### 🔄 ¿Cómo funciona el modo Reescritura?
        
        **1. Verificación GSC (Nuevo):**
        - Verifica si ya rankeas para la keyword
        - Detecta riesgo de canibalización
        - Sugiere si crear nuevo o mejorar existente
        
        **2. Análisis Competitivo:**
        - Buscamos automáticamente las top 5 URLs que rankean para tu keyword
        - Scrapeamos y analizamos el contenido de cada competidor
        - Identificamos qué temas cubren y cómo los estructuran
        
        **3. Identificación de Gaps:**
        - Detectamos información que falta en el contenido competidor
        - Encontramos oportunidades de profundización
        - Identificamos aspectos donde podemos diferenciarnos
        
        **4. Generación Mejorada:**
        - Creamos contenido que cubre TODOS los gaps identificados
        - Profundizamos más que la competencia en temas clave
        - Aportamos el valor único de PcComponentes
        
        ---
        
        ### ✅ Mejores Prácticas
        
        **Para obtener mejores resultados:**
        
        1. **Verifica GSC primero**: Evita crear contenido duplicado
        2. **Keyword específica**: Más específica = análisis más preciso
        3. **Objetivo claro**: Define qué quieres lograr
        4. **Longitud adecuada**: Supera al promedio competidor en ~20%
        5. **Contexto único**: Aporta información que solo tú tienes
        6. **Enlaces estratégicos**: Guía al usuario a productos relevantes
        
        ---
        
        ### 🎯 Casos de Uso Ideales
        
        - **Mejorar artículos existentes**: Actualiza y supera tu propio contenido
        - **Entrar en keywords competitivas**: Análisis te da ventaja táctica
        - **Crear contenido diferenciado**: Identifica ángulos únicos
        - **Superar a competidores específicos**: Análisis detallado de sus debilidades
        
        ---
        
        ### ⚠️ Limitaciones y Precauciones
        
        - **GSC es tu aliado**: Si ya rankeas bien, considera mejorar en lugar de crear nuevo
        - **Canibalización**: Evita tener múltiples URLs compitiendo por la misma keyword
        - **Scraping**: Puede fallar en sitios con protección anti-bot
        - **JavaScript**: Sitios complejos pueden requerir rendering especial
        - **Calidad**: El análisis es tan bueno como la calidad del contenido scrapeado
        """)


# ============================================================================
# CONSTANTES Y CONFIGURACIÓN
# ============================================================================

# Versión del módulo
__version__ = "4.1.1"

# Número máximo de competidores a analizar
MAX_COMPETITORS = 5

# Longitud por defecto sugerida
DEFAULT_REWRITE_LENGTH = 1600

# Factor de superación vs competencia
COMPETITION_BEAT_FACTOR = 1.2  # 20% más que el promedio
