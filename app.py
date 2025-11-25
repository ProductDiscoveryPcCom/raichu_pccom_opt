"""
PcComponentes Content Generator - Aplicación Principal
Versión 4.1.1

Aplicación Streamlit para generación de contenido SEO optimizado.
Soporta dos modos:
- Nuevo: Creación de contenido desde cero
- Reescritura: Mejora de contenido basado en análisis competitivo

Flujo de generación (3 etapas):
1. Borrador inicial
2. Análisis crítico
3. Versión final con correcciones

Autor: PcComponentes - Product Discovery & Content
"""

import streamlit as st
import json
from datetime import datetime
from typing import Dict, Optional, Tuple
import time

# Importar configuración
from config.settings import (
    CLAUDE_API_KEY,
    CLAUDE_MODEL,
    MAX_TOKENS,
    TEMPERATURE,
    APP_TITLE,
    APP_VERSION,
    PAGE_ICON
)
from config.archetipos import get_arquetipo, list_arquetipos

# Importar core
from core.generator import ContentGenerator
from core.scraper import scrape_pdp_data

# Importar prompts
from prompts import new_content, rewrite

# Importar UI components
from ui.sidebar import render_sidebar
from ui.inputs import render_content_inputs
from ui.results import render_results_section, render_export_all_button
from ui.rewrite import render_rewrite_section

# Importar utilidades
from utils.state_manager import (
    initialize_session_state,
    clear_generation_state,
    save_generation_to_state
)
from utils.html_utils import count_words_in_html, validate_cms_structure


# ============================================================================
# CONFIGURACIÓN DE LA PÁGINA
# ============================================================================

st.set_page_config(
    page_title=APP_TITLE,
    page_icon=PAGE_ICON,
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/tu-repo/content-generator',
        'Report a bug': "https://github.com/tu-repo/content-generator/issues",
        'About': f"# {APP_TITLE}\n\nVersión {APP_VERSION}\n\nGenerador de contenido SEO para PcComponentes"
    }
)


# ============================================================================
# INICIALIZACIÓN
# ============================================================================

def initialize_app() -> None:
    """
    Inicializa la aplicación y el estado de sesión.
    
    Configura:
    - Session state inicial
    - Variables de control
    - Estado de generación
    
    Notes:
        - Se ejecuta una sola vez al inicio de la sesión
        - Usa st.session_state para persistencia entre reruns
    """
    
    # Inicializar estado si no existe
    initialize_session_state()
    
    # Variables de control de la app
    if 'app_initialized' not in st.session_state:
        st.session_state.app_initialized = True
        st.session_state.current_mode = 'new'  # 'new' o 'rewrite'
        st.session_state.generation_in_progress = False
        st.session_state.current_stage = 0  # 0, 1, 2, 3


# ============================================================================
# HEADER DE LA APLICACIÓN
# ============================================================================

def render_app_header() -> None:
    """
    Renderiza el header principal de la aplicación.
    
    Incluye:
    - Título y versión
    - Selector de modo (Nuevo vs Reescritura)
    - Indicador de estado de generación
    """
    
    col1, col2, col3 = st.columns([3, 2, 1])
    
    with col1:
        st.title(f"{PAGE_ICON} {APP_TITLE}")
        st.caption(f"Versión {APP_VERSION} | PcComponentes Product Discovery & Content")
    
    with col2:
        # Selector de modo
        mode = st.radio(
            "Modo de generación",
            options=['new', 'rewrite'],
            format_func=lambda x: "📝 Crear Nuevo" if x == 'new' else "🔄 Reescribir",
            horizontal=True,
            key='mode_selector'
        )
        
        # Actualizar modo en session state
        if mode != st.session_state.current_mode:
            st.session_state.current_mode = mode
            clear_generation_state()
            st.rerun()
    
    with col3:
        # Indicador de estado
        if st.session_state.generation_in_progress:
            st.info(f"⏳ Etapa {st.session_state.current_stage}/3")
        else:
            st.success("✅ Listo")


# ============================================================================
# MAIN - MODO NUEVO
# ============================================================================

def render_new_content_mode() -> None:
    """
    Renderiza la interfaz para el modo de creación de contenido nuevo.
    
    Flujo:
    1. Sidebar con configuración API
    2. Inputs de contenido (arquetipo, producto, keywords, etc.)
    3. Botón de generación
    4. Proceso de 3 etapas
    5. Resultados
    """
    
    # Sidebar
    render_sidebar()
    
    # Contenido principal
    st.markdown("## 📝 Crear Contenido Nuevo")
    
    st.info("""
    **Modo Creación**: Genera contenido SEO optimizado desde cero.
    
    Perfecto para: artículos nuevos, reviews de productos, guías, comparativas,
    y cualquier tipo de contenido original basado en arquetipos predefinidos.
    """)
    
    # Inputs de contenido
    st.markdown("---")
    should_generate, inputs_config = render_content_inputs()
    
    # Si hay que generar, ejecutar el proceso
    if should_generate:
        execute_generation_pipeline(inputs_config, mode='new')
    
    # Mostrar resultados si existen
    if any([
        st.session_state.get('draft_html'),
        st.session_state.get('analysis_json'),
        st.session_state.get('final_html')
    ]):
        render_results_section(
            draft_html=st.session_state.get('draft_html'),
            analysis_json=st.session_state.get('analysis_json'),
            final_html=st.session_state.get('final_html'),
            target_length=st.session_state.get('target_length', 1500),
            mode='new'
        )
        
        # Botón de exportación
        render_export_all_button(
            draft_html=st.session_state.get('draft_html'),
            analysis_json=st.session_state.get('analysis_json'),
            final_html=st.session_state.get('final_html')
        )


# ============================================================================
# MAIN - MODO REESCRITURA
# ============================================================================

def render_rewrite_mode() -> None:
    """
    Renderiza la interfaz para el modo de reescritura competitiva.
    
    Flujo:
    1. Sidebar con configuración API
    2. Input de keyword y análisis competitivo
    3. Configuración de parámetros
    4. Botón de generación
    5. Proceso de análisis + 3 etapas
    6. Resultados
    """
    
    # Sidebar
    render_sidebar()
    
    # Sección de reescritura
    should_generate, rewrite_config = render_rewrite_section()
    
    # Si hay que generar, ejecutar el proceso
    if should_generate:
        execute_generation_pipeline(rewrite_config, mode='rewrite')
    
    # Mostrar resultados si existen
    if any([
        st.session_state.get('draft_html'),
        st.session_state.get('analysis_json'),
        st.session_state.get('final_html')
    ]):
        render_results_section(
            draft_html=st.session_state.get('draft_html'),
            analysis_json=st.session_state.get('analysis_json'),
            final_html=st.session_state.get('final_html'),
            target_length=st.session_state.get('target_length', 1600),
            mode='rewrite'
        )
        
        # Botón de exportación
        render_export_all_button(
            draft_html=st.session_state.get('draft_html'),
            analysis_json=st.session_state.get('analysis_json'),
            final_html=st.session_state.get('final_html')
        )


# ============================================================================
# PIPELINE DE GENERACIÓN (3 ETAPAS)
# ============================================================================

def execute_generation_pipeline(config: Dict, mode: str = 'new') -> None:
    """
    Ejecuta el pipeline completo de generación en 3 etapas.
    
    Pipeline:
    - Modo 'new':
        1. Generar borrador inicial
        2. Análisis crítico del borrador
        3. Versión final con correcciones
    
    - Modo 'rewrite':
        0. Análisis competitivo (si no existe)
        1. Generar borrador mejorado
        2. Análisis crítico + validación competitiva
        3. Versión final con correcciones
    
    Args:
        config: Diccionario con toda la configuración necesaria
        mode: 'new' o 'rewrite'
        
    Notes:
        - Usa st.spinner para feedback visual
        - Guarda resultados en session_state después de cada etapa
        - Maneja errores y muestra mensajes apropiados
    """
    
    # Marcar generación en progreso
    st.session_state.generation_in_progress = True
    
    # Inicializar generador
    generator = ContentGenerator(
        api_key=CLAUDE_API_KEY,
        model=CLAUDE_MODEL,
        max_tokens=MAX_TOKENS,
        temperature=TEMPERATURE
    )
    
    # Contenedor para el progreso
    progress_container = st.container()
    
    try:
        # ====================================================================
        # ETAPA 0: ANÁLISIS COMPETITIVO (solo en modo rewrite)
        # ====================================================================
        
        if mode == 'rewrite':
            if not st.session_state.get('rewrite_analysis'):
                with progress_container:
                    st.markdown("### 🔍 Análisis Competitivo")
                    
                    with st.spinner("Analizando contenido de competidores..."):
                        # Construir prompt de análisis
                        analysis_prompt = rewrite.build_competitor_analysis_prompt(
                            keyword=config['keyword'],
                            competitor_contents=rewrite.format_competitors_for_prompt(
                                config['competitors_data']
                            ),
                            target_length=config['target_length']
                        )
                        
                        # Ejecutar análisis
                        analysis_result = generator.generate(analysis_prompt)
                        
                        # Guardar en session state
                        st.session_state.rewrite_analysis = analysis_result
                        
                        st.success("✅ Análisis competitivo completado")
                        time.sleep(1)
        
        # ====================================================================
        # ETAPA 1: BORRADOR INICIAL
        # ====================================================================
        
        with progress_container:
            st.markdown("### 📝 Etapa 1/3: Generando Borrador Inicial")
            st.session_state.current_stage = 1
            
            with st.spinner("Claude está escribiendo el borrador inicial..."):
                # Construir prompt según el modo
                if mode == 'new':
                    # Obtener arquetipo
                    arquetipo = get_arquetipo(config['arquetipo_codigo'])
                    
                    stage1_prompt = new_content.build_generation_prompt_stage1_draft(
                        pdp_data=config.get('pdp_data'),
                        arquetipo=arquetipo,
                        target_length=config['target_length'],
                        keywords=config['keywords'],
                        context=config['context'],
                        links=config['links'],
                        objetivo=config['objetivo'],
                        producto_alternativo=config['producto_alternativo'],
                        casos_uso=config.get('casos_uso', []),
                        campos_arquetipo=config.get('campos_arquetipo', {})
                    )
                else:  # mode == 'rewrite'
                    # Obtener arquetipo si está configurado
                    arquetipo = None
                    if config.get('arquetipo_codigo'):
                        # Extraer código del formato "ARQ-X: Nombre"
                        arq_code = config['arquetipo_codigo'].split(':')[0].strip()
                        arquetipo = get_arquetipo(arq_code)
                    
                    stage1_prompt = rewrite.build_rewrite_prompt_stage1_draft(
                        keyword=config['keyword'],
                        competitor_analysis=st.session_state.rewrite_analysis,
                        pdp_data=config.get('pdp_data'),
                        target_length=config['target_length'],
                        keywords=config['keywords'],
                        context=config['context'],
                        links=config['links'],
                        objetivo=config['objetivo'],
                        producto_alternativo=config['producto_alternativo'],
                        arquetipo=arquetipo
                    )
                
                # Generar borrador
                draft_html = generator.generate(stage1_prompt)
                
                # Guardar en session state
                st.session_state.draft_html = draft_html
                st.session_state.target_length = config['target_length']
                
                # Mostrar métricas rápidas
                word_count = count_words_in_html(draft_html)
                st.success(f"✅ Borrador generado: {word_count:,} palabras")
                time.sleep(1)
        
        # ====================================================================
        # ETAPA 2: ANÁLISIS CRÍTICO
        # ====================================================================
        
        with progress_container:
            st.markdown("### 🔍 Etapa 2/3: Análisis Crítico")
            st.session_state.current_stage = 2
            
            with st.spinner("Claude está analizando el borrador y detectando problemas..."):
                # Construir prompt de análisis según el modo
                if mode == 'new':
                    arquetipo = get_arquetipo(config['arquetipo_codigo'])
                    
                    stage2_prompt = new_content.build_correction_prompt_stage2(
                        draft_content=st.session_state.draft_html,
                        target_length=config['target_length'],
                        arquetipo=arquetipo,
                        objetivo=config['objetivo']
                    )
                else:  # mode == 'rewrite'
                    stage2_prompt = rewrite.build_rewrite_correction_prompt_stage2(
                        draft_content=st.session_state.draft_html,
                        target_length=config['target_length'],
                        keyword=config['keyword'],
                        competitor_analysis=st.session_state.rewrite_analysis,
                        objetivo=config['objetivo']
                    )
                
                # Ejecutar análisis
                analysis_json = generator.generate(stage2_prompt)
                
                # Guardar en session state
                st.session_state.analysis_json = analysis_json
                
                # Parsear JSON para mostrar resumen
                try:
                    analysis = json.loads(analysis_json)
                    num_problems = len(analysis.get('problemas_encontrados', []))
                    st.success(f"✅ Análisis completado: {num_problems} problemas identificados")
                except:
                    st.success("✅ Análisis completado")
                
                time.sleep(1)
        
        # ====================================================================
        # ETAPA 3: VERSIÓN FINAL
        # ====================================================================
        
        with progress_container:
            st.markdown("### ✅ Etapa 3/3: Generando Versión Final")
            st.session_state.current_stage = 3
            
            with st.spinner("Claude está aplicando correcciones y generando la versión final..."):
                # Construir prompt de versión final (igual para ambos modos)
                if mode == 'new':
                    stage3_prompt = new_content.build_final_generation_prompt_stage3(
                        draft_content=st.session_state.draft_html,
                        corrections_json=st.session_state.analysis_json,
                        target_length=config['target_length']
                    )
                else:  # mode == 'rewrite'
                    stage3_prompt = rewrite.build_rewrite_final_prompt_stage3(
                        draft_content=st.session_state.draft_html,
                        corrections_json=st.session_state.analysis_json,
                        target_length=config['target_length'],
                        keyword=config['keyword']
                    )
                
                # Generar versión final
                final_html = generator.generate(stage3_prompt)
                
                # Guardar en session state
                st.session_state.final_html = final_html
                
                # Validar estructura CMS
                is_valid, errors, warnings = validate_cms_structure(final_html)
                
                # Mostrar resultado
                word_count = count_words_in_html(final_html)
                
                if is_valid and not warnings:
                    st.success(f"✅ Versión final generada: {word_count:,} palabras | Estructura CMS válida")
                elif is_valid:
                    st.warning(f"⚠️ Versión final generada: {word_count:,} palabras | {len(warnings)} advertencias")
                else:
                    st.error(f"❌ Versión final generada: {word_count:,} palabras | {len(errors)} errores críticos")
                
                time.sleep(1)
        
        # ====================================================================
        # FINALIZACIÓN
        # ====================================================================
        
        # Guardar metadata de la generación
        save_generation_to_state({
            'mode': mode,
            'timestamp': datetime.now().isoformat(),
            'config': config,
            'word_count': count_words_in_html(st.session_state.final_html),
            'is_valid': is_valid
        })
        
        # Marcar como completado
        st.session_state.generation_in_progress = False
        st.session_state.current_stage = 0
        
        # Mostrar mensaje de éxito
        st.success("🎉 ¡Generación completada! Revisa los resultados a continuación.")
        
        # Forzar rerun para mostrar resultados
        time.sleep(1)
        st.rerun()
    
    except Exception as e:
        # Manejo de errores
        st.session_state.generation_in_progress = False
        st.session_state.current_stage = 0
        
        st.error(f"❌ Error durante la generación: {str(e)}")
        
        # Mostrar detalles del error en expander
        with st.expander("🔍 Ver detalles del error"):
            st.code(str(e))
            
            # Si hay algún resultado parcial, mostrarlo
            if st.session_state.get('draft_html'):
                st.warning("Se guardó el borrador parcial antes del error.")
        
        # Log del error (en producción, enviar a sistema de logging)
        import traceback
        print(f"ERROR EN GENERACIÓN: {traceback.format_exc()}")


# ============================================================================
# FUNCIÓN PRINCIPAL
# ============================================================================

def main() -> None:
    """
    Función principal de la aplicación.
    
    Orquesta:
    - Inicialización
    - Header
    - Routing entre modos (nuevo vs reescritura)
    - Footer
    """
    
    # Inicializar app
    initialize_app()
    
    # Render header
    render_app_header()
    
    st.markdown("---")
    
    # Routing según modo
    if st.session_state.current_mode == 'new':
        render_new_content_mode()
    else:  # mode == 'rewrite'
        render_rewrite_mode()
    
    # Footer
    render_footer()


# ============================================================================
# FOOTER
# ============================================================================

def render_footer() -> None:
    """
    Renderiza el footer de la aplicación.
    """
    
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.caption(f"🏢 **PcComponentes** | Product Discovery & Content")
    
    with col2:
        st.caption(f"📦 Versión {APP_VERSION} | Streamlit + Claude Sonnet 4")
    
    with col3:
        # Botón de limpiar estado
        if st.button("🗑️ Limpiar Todo", help="Reinicia la aplicación y borra todos los datos"):
            clear_generation_state()
            st.rerun()


# ============================================================================
# UTILIDADES DE DEBUG (SOLO EN DESARROLLO)
# ============================================================================

def render_debug_panel() -> None:
    """
    Panel de debug para desarrollo (oculto por defecto).
    
    Muestra:
    - Estado actual de session_state
    - Variables de configuración
    - Logs de generación
    
    Notes:
        - Solo se muestra si DEBUG_MODE=True en settings
        - Útil para troubleshooting durante desarrollo
    """
    
    from config.settings import DEBUG_MODE
    
    if not DEBUG_MODE:
        return
    
    with st.sidebar.expander("🐛 Debug Panel", expanded=False):
        st.markdown("### Session State")
        
        # Mostrar variables clave de session state
        debug_keys = [
            'current_mode',
            'generation_in_progress',
            'current_stage',
            'target_length',
            'app_initialized'
        ]
        
        for key in debug_keys:
            value = st.session_state.get(key, 'Not set')
            st.text(f"{key}: {value}")
        
        st.markdown("---")
        
        # Botón para ver todo el session state
        if st.button("Ver Session State Completo"):
            st.json(dict(st.session_state))
        
        # Botón para forzar rerun
        if st.button("🔄 Force Rerun"):
            st.rerun()


# ============================================================================
# PUNTO DE ENTRADA
# ============================================================================

if __name__ == "__main__":
    # Renderizar panel de debug si está habilitado
    render_debug_panel()
    
    # Ejecutar app principal
    main()
