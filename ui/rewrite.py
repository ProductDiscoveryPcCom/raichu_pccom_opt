# -*- coding: utf-8 -*-
"""
UI de Reescritura - PcComponentes Content Generator
Versión 4.5.0

Este módulo maneja la interfaz de usuario para el modo REESCRITURA,
que analiza contenido competidor y genera una versión mejorada.

Incluye:
- Campo para pegar HTML del artículo a reescribir
- Integración con SEMrush API para datos reales de competidores
- Fallback a entrada manual si SEMrush no está disponible
- Verificación GSC para evitar canibalización

Flujo:
1. Input de keyword principal
2. Verificación GSC (opcional)
3. Contenido HTML a reescribir (NUEVO)
4. Obtención de competidores (SEMrush API o manual)
5. Análisis competitivo de contenido
6. Configuración de parámetros adicionales
7. Generación del contenido mejorado en 3 etapas

Autor: PcComponentes - Product Discovery & Content
"""

import streamlit as st
from typing import Dict, List, Optional, Tuple
import json
from datetime import datetime
import re

# Importar utilidades
from utils.html_utils import count_words_in_html

# Importar configuración
from config.settings import (
    GSC_VERIFICATION_ENABLED,
    SEMRUSH_ENABLED,
    SEMRUSH_API_KEY
)

# Importar sección GSC (con manejo de errores)
try:
    from ui.gsc_section import render_gsc_verification_section
    GSC_AVAILABLE = True
except ImportError:
    GSC_AVAILABLE = False

# Importar cliente SEMrush
try:
    from core.semrush import (
        SEMrushClient,
        SEMrushResponse,
        CompetitorData,
        format_competitors_for_display,
        is_semrush_available
    )
    SEMRUSH_MODULE_AVAILABLE = True
except ImportError:
    SEMRUSH_MODULE_AVAILABLE = False


# ============================================================================
# VERSIÓN Y CONSTANTES
# ============================================================================

__version__ = "4.5.0"

MAX_COMPETITORS = 10
DEFAULT_REWRITE_LENGTH = 1600
COMPETITION_BEAT_FACTOR = 1.2


# ============================================================================
# FUNCIÓN PRINCIPAL DE RENDERIZADO
# ============================================================================

def render_rewrite_section() -> Tuple[bool, Dict]:
    """
    Renderiza la sección completa del modo reescritura.
    
    Esta función gestiona toda la interfaz del modo reescritura, incluyendo:
    - Input de keyword y configuración
    - Verificación GSC
    - Campo HTML para pegar contenido a reescribir
    - Obtención de competidores (SEMrush o manual)
    - Análisis competitivo
    - Configuración de parámetros de generación
    - Botón de inicio de generación
    
    Returns:
        Tuple[bool, Dict]: (debe_generar, config_dict)
        - debe_generar: True si el usuario quiere iniciar la generación
        - config_dict: Diccionario con toda la configuración necesaria
    """
    
    st.markdown("## 🔄 Modo: Reescritura Competitiva")
    
    # Determinar método de obtención de competidores
    semrush_available = SEMRUSH_MODULE_AVAILABLE and is_semrush_available()
    
    # Info box según disponibilidad
    if semrush_available:
        st.success("""
        **✅ SEMrush API Conectada**
        
        1. 🔍 Verifica si ya rankeas para esta keyword (GSC)
        2. 📄 Opcionalmente, pega el HTML del artículo a mejorar
        3. 📊 Obtiene los **top 5 resultados reales** de Google vía SEMrush
        4. 🔍 Scrapea y analiza el contenido de cada competidor
        5. 📈 Identifica **gaps de contenido** y oportunidades
        6. ✍️ Genera contenido **superior** que cubre todos los gaps
        """)
    else:
        st.info("""
        **📝 Modo Manual** (SEMrush no configurado)
        
        1. 🔍 Verifica si ya rankeas para esta keyword (GSC)
        2. 📄 Opcionalmente, pega el HTML del artículo a mejorar
        3. ✏️ Introduce manualmente las URLs de competidores a analizar
        4. 🔍 Scrapea y analiza el contenido de cada URL
        5. 📈 Identifica **gaps de contenido** y oportunidades
        6. ✍️ Genera contenido **superior** que cubre todos los gaps
        
        💡 **Tip**: Configura SEMrush API en Settings para obtener competidores automáticamente.
        """)
    
    # Inicializar estado si no existe
    _initialize_rewrite_state()
    
    # =========================================================================
    # PASO 1: Keyword y verificación GSC
    # =========================================================================
    st.markdown("---")
    st.markdown("### 🎯 Paso 1: Keyword Principal")
    
    keyword, should_search = render_keyword_input()
    
    # Verificación GSC (si está habilitada y hay keyword)
    gsc_analysis = None
    if GSC_VERIFICATION_ENABLED and GSC_AVAILABLE and keyword and len(keyword.strip()) >= 3:
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
    
    # =========================================================================
    # PASO 2: Contenido HTML a reescribir (NUEVO)
    # =========================================================================
    st.markdown("---")
    st.markdown("### 📄 Paso 2: Contenido a Reescribir (Opcional)")
    
    html_to_rewrite = render_html_content_input()
    
    # =========================================================================
    # PASO 3: Obtener competidores
    # =========================================================================
    st.markdown("---")
    st.markdown("### 🏆 Paso 3: Análisis de Competidores")
    
    if semrush_available:
        # Modo SEMrush automático
        if should_search and keyword:
            _fetch_competitors_semrush(keyword, gsc_analysis)
    else:
        # Modo manual
        render_manual_competitors_input(keyword)
    
    # Mostrar competidores si existen
    if st.session_state.rewrite_competitors_data:
        render_competitors_summary(st.session_state.rewrite_competitors_data)
    
    # =========================================================================
    # PASO 4: Configuración de parámetros
    # =========================================================================
    st.markdown("---")
    st.markdown("### ⚙️ Paso 4: Configuración del Contenido")
    
    rewrite_config = render_rewrite_configuration(keyword)
    
    # Validar que todo esté listo para generar
    can_generate = validate_rewrite_inputs(
        keyword,
        st.session_state.rewrite_competitors_data,
        rewrite_config,
        gsc_analysis,
        html_to_rewrite
    )
    
    # Botón de generación
    st.markdown("---")
    
    if not can_generate:
        st.warning("⚠️ Completa todos los pasos anteriores para poder generar el contenido.")
        return False, {}
    
    # Mostrar resumen antes de generar
    render_generation_summary(keyword, rewrite_config, gsc_analysis, html_to_rewrite)
    
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
            gsc_analysis=gsc_analysis,
            html_to_rewrite=html_to_rewrite
        )
        return True, full_config
    
    return False, {}


# ============================================================================
# INICIALIZACIÓN DE ESTADO
# ============================================================================

def _initialize_rewrite_state() -> None:
    """Inicializa variables de estado para el modo rewrite."""
    
    if 'rewrite_competitors_data' not in st.session_state:
        st.session_state.rewrite_competitors_data = None
    if 'rewrite_analysis' not in st.session_state:
        st.session_state.rewrite_analysis = None
    if 'rewrite_gsc_analysis' not in st.session_state:
        st.session_state.rewrite_gsc_analysis = None
    if 'last_rewrite_keyword' not in st.session_state:
        st.session_state.last_rewrite_keyword = ''
    if 'manual_urls_input' not in st.session_state:
        st.session_state.manual_urls_input = ''
    if 'semrush_response' not in st.session_state:
        st.session_state.semrush_response = None
    if 'html_to_rewrite' not in st.session_state:
        st.session_state.html_to_rewrite = ''


# ============================================================================
# INPUT DE CONTENIDO HTML A REESCRIBIR (NUEVO)
# ============================================================================

def render_html_content_input() -> str:
    """
    Renderiza el campo para pegar HTML del artículo a reescribir.
    
    Returns:
        str: Contenido HTML pegado por el usuario (puede estar vacío)
    """
    
    st.markdown("""
    Si tienes un artículo existente que quieres mejorar, pega aquí su código HTML.
    Esto ayudará a mantener la estructura y mejorar el contenido existente.
    """)
    
    # Checkbox para mostrar/ocultar el campo
    use_existing = st.checkbox(
        "Tengo un artículo existente para reescribir",
        value=bool(st.session_state.get('html_to_rewrite', '')),
        help="Activa esta opción si quieres mejorar un artículo existente"
    )
    
    html_content = ""
    
    if use_existing:
        html_content = st.text_area(
            "Código HTML del artículo original",
            value=st.session_state.get('html_to_rewrite', ''),
            height=200,
            key="html_rewrite_input",
            placeholder="""<article>
  <h1>Título del artículo existente...</h1>
  <p>Contenido del primer párrafo...</p>
  <h2>Subtítulo...</h2>
  <p>Más contenido...</p>
</article>""",
            help="Pega el código HTML completo del artículo que quieres mejorar"
        )
        
        # Guardar en session state
        st.session_state.html_to_rewrite = html_content
        
        # Mostrar estadísticas si hay contenido
        if html_content and html_content.strip():
            # Extraer texto para contar palabras
            text_content = _strip_html_tags(html_content)
            word_count = len(text_content.split())
            char_count = len(html_content)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("📝 Palabras", f"{word_count:,}")
            with col2:
                st.metric("📊 Caracteres", f"{char_count:,}")
            with col3:
                # Detectar estructura básica
                h1_count = html_content.lower().count('<h1')
                h2_count = html_content.lower().count('<h2')
                st.metric("📑 Encabezados", f"{h1_count} H1, {h2_count} H2")
            
            # Advertencia si el contenido es muy corto
            if word_count < 100:
                st.warning("⚠️ El contenido parece muy corto. Asegúrate de haber pegado el artículo completo.")
            elif word_count > 50:
                st.success(f"✅ Contenido detectado: {word_count} palabras")
        
        # Tips
        with st.expander("💡 Tips para pegar el HTML"):
            st.markdown("""
            **¿De dónde obtener el HTML?**
            
            1. **Desde el CMS**: Usa la vista "HTML" o "Código fuente" del editor
            2. **Desde el navegador**: Click derecho > "Ver código fuente" > Copiar sección del artículo
            3. **Desde DevTools**: F12 > Elements > Copiar el `<article>` o `<main>`
            
            **¿Qué incluir?**
            - ✅ El contenido del artículo (títulos, párrafos, listas)
            - ✅ Enlaces internos existentes
            - ❌ No incluyas header/footer del sitio
            - ❌ No incluyas scripts o estilos
            """)
    else:
        # Limpiar si se desactiva
        st.session_state.html_to_rewrite = ''
        st.caption("💡 Si no tienes contenido existente, generaremos uno nuevo desde cero basado en el análisis competitivo.")
    
    return html_content


def _strip_html_tags(html: str) -> str:
    """Elimina tags HTML y retorna texto plano."""
    # Eliminar tags
    text = re.sub(r'<[^>]+>', ' ', html)
    # Limpiar espacios múltiples
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


# ============================================================================
# INPUT DE KEYWORD Y BÚSQUEDA
# ============================================================================

def render_keyword_input() -> Tuple[str, bool]:
    """
    Renderiza el input de keyword principal y botón de búsqueda.
    
    Returns:
        Tuple[str, bool]: (keyword, should_search)
    """
    
    st.markdown("""
    Introduce la **keyword principal** para la que quieres rankear.
    """)
    
    # Determinar si SEMrush está disponible
    semrush_available = SEMRUSH_MODULE_AVAILABLE and is_semrush_available()
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        current_keyword = st.text_input(
            "Keyword principal *",
            placeholder="Ej: mejor portátil gaming 2025",
            help="Keyword específica para la que quieres crear/mejorar contenido",
            key="rewrite_keyword_input"
        )
    
    with col2:
        # Botón de búsqueda (solo si hay SEMrush)
        if semrush_available:
            search_disabled = not current_keyword or len(current_keyword.strip()) < 3
            search_button = st.button(
                "🔍 Buscar Competidores",
                disabled=search_disabled,
                use_container_width=True,
                type="primary"
            )
        else:
            search_button = False
            st.caption("💡 Introduce URLs manualmente abajo")
    
    # Detectar si cambió la keyword para limpiar datos
    if 'last_rewrite_keyword' in st.session_state:
        if st.session_state.last_rewrite_keyword != current_keyword:
            # Limpiar datos de búsqueda anterior
            st.session_state.rewrite_competitors_data = None
            st.session_state.rewrite_analysis = None
            st.session_state.rewrite_gsc_analysis = None
            st.session_state.semrush_response = None
    
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
        """)
    
    return current_keyword, search_button


# ============================================================================
# OBTENCIÓN DE COMPETIDORES - SEMRUSH
# ============================================================================

def _fetch_competitors_semrush(keyword: str, gsc_analysis: Optional[Dict]) -> None:
    """
    Obtiene competidores usando SEMrush API.
    
    Args:
        keyword: Keyword a buscar
        gsc_analysis: Análisis de GSC (para advertencias)
    """
    
    # Advertencia si ya rankea
    if gsc_analysis and gsc_analysis.get('has_matches'):
        st.info("💡 Procederemos a analizar competidores. Recuerda que ya tienes contenido rankeando.")
    
    with st.spinner("🔍 Consultando SEMrush y analizando competidores..."):
        try:
            # Obtener cliente SEMrush
            client = SEMrushClient(
                api_key=SEMRUSH_API_KEY,
                database='es'  # España
            )
            
            # Consultar API
            response = client.get_organic_competitors(
                keyword=keyword,
                num_results=5,
                scrape_content=True,
                exclude_domains=['pccomponentes.com', 'pccomponentes.pt']
            )
            
            # Guardar respuesta completa
            st.session_state.semrush_response = response
            
            if response.success and response.competitors:
                # Formatear para uso en la app
                competitors_data = format_competitors_for_display(response.competitors)
                st.session_state.rewrite_competitors_data = competitors_data
                
                # Métricas de éxito
                scraped_ok = sum(1 for c in competitors_data if c.get('scrape_success', False))
                
                st.success(f"""
                ✅ **SEMrush**: {len(competitors_data)} competidores encontrados
                
                📊 Contenido scrapeado: {scraped_ok}/{len(competitors_data)} URLs
                """)
            else:
                # Error de SEMrush
                st.error(f"""
                ❌ **Error de SEMrush**: {response.error_message}
                
                Puedes introducir las URLs manualmente abajo.
                """)
                
                # Mostrar opción manual como fallback
                _show_manual_fallback()
        
        except Exception as e:
            st.error(f"""
            ❌ **Error inesperado**: {str(e)}
            
            Puedes introducir las URLs manualmente abajo.
            """)
            _show_manual_fallback()
        
        st.rerun()


def _show_manual_fallback() -> None:
    """Muestra la opción de entrada manual como fallback."""
    st.session_state['show_manual_fallback'] = True


# ============================================================================
# OBTENCIÓN DE COMPETIDORES - MANUAL
# ============================================================================

def render_manual_competitors_input(keyword: str) -> None:
    """
    Renderiza el input manual para URLs de competidores.
    
    Args:
        keyword: Keyword principal (para contexto)
    """
    
    st.markdown("""
    **Introduce las URLs de los competidores** que quieres analizar.
    
    💡 **Tip**: Busca tu keyword en Google y copia las URLs de los primeros resultados.
    """)
    
    # Text area para URLs
    urls_input = st.text_area(
        "URLs de competidores (una por línea) *",
        value=st.session_state.get('manual_urls_input', ''),
        placeholder="""https://competitor1.com/article
https://competitor2.com/guide
https://competitor3.com/review""",
        height=150,
        help="Introduce las URLs de los competidores que rankean para tu keyword"
    )
    
    st.session_state.manual_urls_input = urls_input
    
    # Botón para analizar
    col1, col2 = st.columns([1, 3])
    
    with col1:
        analyze_btn = st.button(
            "🔍 Analizar URLs",
            disabled=not urls_input.strip(),
            type="primary"
        )
    
    with col2:
        if urls_input:
            urls = [u.strip() for u in urls_input.split('\n') if u.strip() and u.startswith('http')]
            st.caption(f"📋 {len(urls)} URLs detectadas")
    
    if analyze_btn and urls_input:
        _scrape_manual_urls(urls_input, keyword)


def _scrape_manual_urls(urls_input: str, keyword: str) -> None:
    """
    Scrapea las URLs introducidas manualmente.
    
    Args:
        urls_input: Texto con URLs separadas por líneas
        keyword: Keyword principal
    """
    
    # Parsear URLs
    urls = [u.strip() for u in urls_input.split('\n') if u.strip() and u.startswith('http')]
    
    if not urls:
        st.error("❌ No se encontraron URLs válidas. Asegúrate de que empiecen con http:// o https://")
        return
    
    if len(urls) > 10:
        st.warning("⚠️ Máximo 10 URLs. Solo se procesarán las primeras 10.")
        urls = urls[:10]
    
    with st.spinner(f"🔍 Analizando {len(urls)} URLs..."):
        competitors_data = []
        
        for i, url in enumerate(urls, 1):
            try:
                # Scrape de contenido
                content_data = _scrape_single_url(url, i)
                competitors_data.append(content_data)
                
            except Exception as e:
                competitors_data.append({
                    'url': url,
                    'title': 'Error al scrapear',
                    'domain': _extract_domain(url),
                    'position': i,
                    'ranking_position': i,
                    'content': '',
                    'word_count': 0,
                    'scrape_success': False,
                    'error': str(e)[:100]
                })
        
        # Guardar resultados
        st.session_state.rewrite_competitors_data = competitors_data
        
        # Mostrar resumen
        success_count = sum(1 for c in competitors_data if c.get('scrape_success', False))
        
        if success_count > 0:
            st.success(f"✅ Contenido analizado: {success_count}/{len(competitors_data)} URLs")
        else:
            st.error("❌ No se pudo scrapear ninguna URL. Verifica que sean accesibles.")
        
        st.rerun()


def _scrape_single_url(url: str, position: int) -> Dict:
    """
    Scrapea una URL individual.
    
    Args:
        url: URL a scrapear
        position: Posición en la lista
        
    Returns:
        Dict con datos del competidor
    """
    import requests
    from bs4 import BeautifulSoup
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml',
        'Accept-Language': 'es-ES,es;q=0.9',
    }
    
    response = requests.get(url, headers=headers, timeout=15)
    
    if response.status_code != 200:
        raise Exception(f"HTTP {response.status_code}")
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Extraer título
    title_tag = soup.find('title')
    title = title_tag.get_text(strip=True) if title_tag else ''
    
    # Extraer meta description
    meta_desc = soup.find('meta', attrs={'name': 'description'})
    description = meta_desc.get('content', '') if meta_desc else ''
    
    # Extraer contenido principal
    # Eliminar scripts, styles, nav, footer
    for element in soup(['script', 'style', 'nav', 'footer', 'header', 'aside']):
        element.decompose()
    
    # Buscar contenido principal
    main = soup.find('main') or soup.find('article') or soup.find('body')
    content = main.get_text(' ', strip=True) if main else ''
    
    # Limpiar espacios
    content = re.sub(r'\s+', ' ', content).strip()
    
    # Limitar longitud
    if len(content) > 8000:
        content = content[:8000] + "..."
    
    return {
        'url': url,
        'title': title[:200] if title else 'Sin título',
        'domain': _extract_domain(url),
        'position': position,
        'ranking_position': position,
        'content': content,
        'word_count': len(content.split()),
        'meta_description': description[:300] if description else '',
        'scrape_success': True,
        'error': None
    }


def _extract_domain(url: str) -> str:
    """Extrae el dominio de una URL."""
    try:
        from urllib.parse import urlparse
        parsed = urlparse(url)
        return parsed.netloc.replace('www.', '')
    except Exception:
        return url


# ============================================================================
# RESUMEN DE COMPETIDORES
# ============================================================================

def render_competitors_summary(competitors_data: List[Dict]) -> None:
    """
    Renderiza un resumen de los competidores analizados.
    
    Args:
        competitors_data: Lista de dicts con datos de competidores
    """
    
    st.markdown("#### 📊 Competidores Analizados")
    
    # Métricas generales
    col1, col2, col3 = st.columns(3)
    
    scraped_ok = [c for c in competitors_data if c.get('scrape_success', False)]
    
    with col1:
        st.metric("📊 Total URLs", len(competitors_data))
    
    with col2:
        if scraped_ok:
            avg_words = sum(c.get('word_count', 0) for c in scraped_ok) / len(scraped_ok)
            st.metric("📝 Promedio palabras", f"{int(avg_words):,}")
        else:
            st.metric("📝 Promedio palabras", "N/A")
    
    with col3:
        st.metric("✅ Scrapeados", f"{len(scraped_ok)}/{len(competitors_data)}")
    
    # Tabla de competidores
    st.markdown("**URLs Analizadas:**")
    
    for i, comp in enumerate(competitors_data, 1):
        position = comp.get('ranking_position', comp.get('position', i))
        title = comp.get('title', 'Sin título')[:60]
        
        # Icono según estado
        if comp.get('scrape_success', False):
            icon = "✅"
            status = f"{comp.get('word_count', 0):,} palabras"
        else:
            icon = "❌"
            status = comp.get('error', 'Error')[:30]
        
        with st.expander(f"{icon} #{position} - {title}", expanded=False):
            col_a, col_b = st.columns([3, 1])
            
            with col_a:
                st.markdown(f"**URL:** [{comp.get('url', 'N/A')}]({comp.get('url', '#')})")
                st.markdown(f"**Dominio:** {comp.get('domain', 'N/A')}")
                
                if comp.get('meta_description'):
                    st.caption(f"📝 {comp['meta_description'][:150]}...")
            
            with col_b:
                st.metric("Posición", f"#{position}")
            
            # Preview del contenido si hay
            if comp.get('content') and comp.get('scrape_success'):
                content_preview = comp['content'][:400] + "..."
                st.text_area(
                    "Preview del contenido",
                    content_preview,
                    height=100,
                    disabled=True,
                    key=f"preview_comp_{i}"
                )
            elif not comp.get('scrape_success'):
                st.error(f"Error: {comp.get('error', 'No se pudo scrapear')}")


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
            scraped = [c for c in st.session_state.rewrite_competitors_data if c.get('scrape_success')]
            if scraped:
                avg_competitor_length = int(
                    sum(c.get('word_count', 0) for c in scraped) / len(scraped)
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
    
    # Enlaces - Múltiples
    st.markdown("#### 🔗 Enlaces a Incluir")
    
    # Inicializar lista de enlaces en session_state si no existe
    if 'rewrite_links' not in st.session_state:
        st.session_state.rewrite_links = [{'url': '', 'text': ''}]
    
    # Mostrar cada enlace
    links_to_remove = []
    
    for i, link in enumerate(st.session_state.rewrite_links):
        col_url, col_text, col_remove = st.columns([5, 4, 1])
        
        with col_url:
            new_url = st.text_input(
                f"URL del enlace {i+1}",
                value=link.get('url', ''),
                placeholder="https://www.pccomponentes.com/categoria",
                key=f"rewrite_link_url_{i}",
                help="URL del enlace a incluir"
            )
            st.session_state.rewrite_links[i]['url'] = new_url
        
        with col_text:
            new_text = st.text_input(
                f"Texto anchor {i+1}",
                value=link.get('text', ''),
                placeholder="Ej: portátiles gaming",
                key=f"rewrite_link_text_{i}",
                help="Texto del enlace (natural y descriptivo)"
            )
            st.session_state.rewrite_links[i]['text'] = new_text
        
        with col_remove:
            st.markdown("<br>", unsafe_allow_html=True)  # Espaciado
            if len(st.session_state.rewrite_links) > 1:
                if st.button("🗑️", key=f"remove_rewrite_link_{i}", help="Eliminar enlace"):
                    links_to_remove.append(i)
    
    # Eliminar enlaces marcados
    for idx in sorted(links_to_remove, reverse=True):
        st.session_state.rewrite_links.pop(idx)
        st.rerun()
    
    # Botón para añadir más enlaces
    col_add, col_info = st.columns([1, 3])
    with col_add:
        if st.button("➕ Añadir enlace", key="add_rewrite_link"):
            st.session_state.rewrite_links.append({'url': '', 'text': ''})
            st.rerun()
    
    with col_info:
        st.caption(f"📊 {len(st.session_state.rewrite_links)} enlace(s) configurado(s)")
    
    # Guardar enlaces válidos en config
    config['enlaces'] = [
        {'url': link['url'], 'text': link['text']}
        for link in st.session_state.rewrite_links
        if link.get('url', '').strip()
    ]
    
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
    gsc_analysis: Optional[Dict],
    html_to_rewrite: str = ""
) -> bool:
    """
    Valida que todos los inputs necesarios estén completos.
    
    Args:
        keyword: Keyword principal
        competitors_data: Datos de competidores
        config: Configuración del usuario
        gsc_analysis: Análisis de GSC (opcional)
        html_to_rewrite: HTML del artículo a reescribir (opcional)
        
    Returns:
        bool: True si todos los inputs necesarios están completos
    """
    
    missing = []
    
    # Validar keyword
    if not keyword or len(keyword.strip()) < 3:
        missing.append("Keyword principal")
    
    # Validar que haya competidores analizados O contenido a reescribir
    has_competitors = competitors_data and len(competitors_data) > 0
    has_html = html_to_rewrite and len(html_to_rewrite.strip()) > 100
    
    if not has_competitors and not has_html:
        missing.append("Análisis de competidores O contenido HTML a reescribir")
    elif has_competitors:
        # Verificar que al menos uno tenga contenido
        has_content = any(c.get('scrape_success', False) for c in competitors_data)
        if not has_content and not has_html:
            missing.append("Al menos un competidor con contenido scrapeado O HTML a reescribir")
    
    # Validar objetivo
    if not config.get('objetivo') or len(config['objetivo'].strip()) < 10:
        missing.append("Objetivo del contenido")
    
    # Validar longitud
    if not config.get('target_length') or config['target_length'] < 800:
        missing.append("Longitud objetivo válida (mínimo 800 palabras)")
    
    # Si falta algo, mostrar en formato compacto
    if missing:
        error_html = "<div style='background-color:#fff3cd;border:1px solid #ffc107;border-radius:5px;padding:10px;margin:10px 0;'>"
        error_html += "<span style='color:#856404;font-weight:bold;font-size:14px;'>⚠️ Campos pendientes:</span>"
        error_html += "<ul style='margin:5px 0;padding-left:20px;color:#856404;font-size:13px;'>"
        for m in missing:
            error_html += f"<li>{m}</li>"
        error_html += "</ul></div>"
        st.markdown(error_html, unsafe_allow_html=True)
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

def render_generation_summary(
    keyword: str, 
    config: Dict, 
    gsc_analysis: Optional[Dict],
    html_to_rewrite: str = ""
) -> None:
    """
    Muestra un resumen de la configuración antes de generar.
    
    Args:
        keyword: Keyword principal
        config: Configuración del usuario
        gsc_analysis: Análisis de GSC (opcional)
        html_to_rewrite: HTML del artículo a reescribir
    """
    
    st.markdown("### 📋 Resumen de Generación")
    
    with st.container():
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Configuración básica:**")
            st.markdown(f"- 🎯 Keyword: `{keyword}`")
            st.markdown(f"- 📝 Longitud: `{config['target_length']:,}` palabras")
            st.markdown(f"- 🔑 Keywords adicionales: `{len(config.get('keywords', [])) - 1}`")
            
            # Indicar si hay HTML a reescribir
            if html_to_rewrite and len(html_to_rewrite.strip()) > 100:
                word_count = len(_strip_html_tags(html_to_rewrite).split())
                st.markdown(f"- 📄 HTML original: `{word_count}` palabras")
        
        with col2:
            st.markdown("**Análisis competitivo:**")
            if st.session_state.rewrite_competitors_data:
                scraped = [c for c in st.session_state.rewrite_competitors_data if c.get('scrape_success')]
                n_comp = len(st.session_state.rewrite_competitors_data)
                st.markdown(f"- 🏆 Competidores: `{len(scraped)}/{n_comp}` con contenido")
                
                if scraped:
                    avg_words = sum(c.get('word_count', 0) for c in scraped) / len(scraped)
                    st.markdown(f"- 📊 Promedio competencia: `{int(avg_words):,}`")
                    
                    diff = config['target_length'] - avg_words
                    pct = (diff / avg_words * 100) if avg_words > 0 else 0
                    st.markdown(f"- 📈 Nuestro diferencial: `{pct:+.0f}%`")
            elif html_to_rewrite:
                st.markdown("- 📄 Modo: **Mejora de contenido existente**")
            
            # Info de GSC si existe
            if gsc_analysis and gsc_analysis.get('has_matches'):
                st.markdown(f"- ⚠️ GSC: `{len(set(m['url'] for m in gsc_analysis['matches']))} URLs rankeando`")
    
    st.info("""
    ✅ Todo listo para generar. El proceso tomará unos minutos e incluirá:
    1. Análisis competitivo detallado
    2. Generación del borrador mejorado
    3. Análisis crítico
    4. Versión final optimizada
    """)


# ============================================================================
# PREPARACIÓN DE CONFIGURACIÓN FINAL
# ============================================================================

def prepare_rewrite_config(
    keyword: str,
    competitors_data: List[Dict],
    rewrite_config: Dict,
    gsc_analysis: Optional[Dict],
    html_to_rewrite: str = ""
) -> Dict:
    """
    Prepara la configuración completa para el proceso de generación.
    
    Args:
        keyword: Keyword principal
        competitors_data: Datos de competidores
        rewrite_config: Configuración del usuario
        gsc_analysis: Análisis de GSC (opcional)
        html_to_rewrite: HTML del artículo a reescribir
        
    Returns:
        Dict con toda la configuración necesaria para generar
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
    
    # HTML a reescribir (NUEVO)
    config['html_to_rewrite'] = html_to_rewrite if html_to_rewrite else None
    
    # Enlaces - Ahora es una lista de múltiples enlaces
    enlaces_list = rewrite_config.get('enlaces', [])
    
    # Convertir a formato compatible con prompts/rewrite.py
    config['links'] = [
        {
            'url': enlace.get('url', ''),
            'text': enlace.get('text', ''),
            'anchor': enlace.get('text', ''),  # Alias para compatibilidad
            'type': 'interno'
        }
        for enlace in enlaces_list
        if enlace.get('url', '').strip()
    ]
    
    # Producto alternativo
    config['producto_alternativo'] = {
        'url': rewrite_config.get('producto_alternativo_url', ''),
        'text': rewrite_config.get('producto_alternativo_text', '')
    }
    
    # Datos de competidores (solo los scrapeados con éxito)
    if competitors_data:
        config['competitors_data'] = [
            c for c in competitors_data if c.get('scrape_success', False)
        ]
    else:
        config['competitors_data'] = []
    
    # Análisis de GSC
    config['gsc_analysis'] = gsc_analysis
    
    # Arquetipo de referencia (opcional)
    config['arquetipo_codigo'] = rewrite_config.get('arquetipo_codigo')
    
    # PDP data (no aplica en modo rewrite típicamente)
    config['pdp_data'] = None
    
    # Campos específicos de arquetipo (no aplica en modo rewrite)
    config['campos_arquetipo'] = {}
    
    # Timestamp para tracking
    config['timestamp'] = datetime.now().isoformat()
    
    # Info de fuente de datos
    config['data_source'] = 'semrush' if SEMRUSH_ENABLED else 'manual'
    
    return config


# ============================================================================
# HELP Y DOCUMENTACIÓN
# ============================================================================

def render_rewrite_help() -> None:
    """Renderiza información de ayuda sobre el modo reescritura."""
    
    with st.expander("ℹ️ Ayuda: Modo Reescritura"):
        st.markdown("""
        ### 🔄 ¿Cómo funciona el modo Reescritura?
        
        **1. Verificación GSC:**
        - Verifica si ya rankeas para la keyword
        - Detecta riesgo de canibalización
        
        **2. Contenido a Reescribir (Nuevo):**
        - Opcionalmente, pega el HTML de un artículo existente
        - El sistema lo usará como base para mejorar
        
        **3. Análisis Competitivo:**
        - **Con SEMrush**: Obtiene automáticamente top 5 URLs de Google
        - **Manual**: Introduces las URLs que quieres analizar
        - Scrapea y analiza el contenido de cada competidor
        
        **4. Generación Mejorada:**
        - Crea contenido que cubre TODOS los gaps identificados
        - Profundiza más que la competencia
        - Aporta valor único de PcComponentes
        
        ---
        
        ### 🔧 Configuración de SEMrush
        
        Para usar SEMrush automático, configura tu API key en:
        - **Streamlit Cloud**: Settings > Secrets
        - **Local**: Archivo `.env`
        
        ```toml
        [semrush]
        api_key = "tu-api-key"
        ```
        """)


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    '__version__',
    'render_rewrite_section',
    'render_keyword_input',
    'render_html_content_input',
    'render_manual_competitors_input',
    'render_competitors_summary',
    'render_rewrite_configuration',
    'validate_rewrite_inputs',
    'render_generation_summary',
    'prepare_rewrite_config',
    'render_rewrite_help',
    'MAX_COMPETITORS',
    'DEFAULT_REWRITE_LENGTH',
    'COMPETITION_BEAT_FACTOR',
]
