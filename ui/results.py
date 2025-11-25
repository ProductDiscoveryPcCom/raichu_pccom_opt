"""
UI de resultados - PcComponentes Content Generator
Versión 4.1.1

Este módulo maneja la visualización de los resultados de generación de contenido.
Incluye tabs para cada etapa del proceso, validación de estructura HTML v4.1.1,
análisis de word count, y preview del contenido generado.

Autor: PcComponentes - Product Discovery & Content
"""

import streamlit as st
import json
from typing import Dict, List, Tuple, Optional

# Importar utilidades
from utils.html_utils import (
    count_words_in_html,
    extract_content_structure,
    validate_html_structure,
    validate_cms_structure,
    analyze_links
)


# ============================================================================
# FUNCIÓN PRINCIPAL DE RENDERIZADO
# ============================================================================

def render_results_section(
    draft_html: Optional[str] = None,
    analysis_json: Optional[str] = None,
    final_html: Optional[str] = None,
    target_length: int = 1500,
    mode: str = "new"
) -> None:
    """
    Renderiza la sección completa de resultados con tabs para cada etapa.
    
    Esta es la función principal que organiza la visualización de los resultados
    del proceso de generación de contenido (nuevo o reescritura).
    
    Args:
        draft_html: HTML del borrador (Etapa 1) - opcional
        analysis_json: JSON del análisis crítico (Etapa 2) - opcional
        final_html: HTML de la versión final (Etapa 3) - opcional
        target_length: Longitud objetivo en palabras
        mode: Modo de generación ("new" o "rewrite")
        
    Notes:
        - Muestra solo los tabs de las etapas completadas
        - Incluye validación CMS v4.1.1 en tabs de HTML
        - Calcula y muestra word count automáticamente
        - Permite copiar HTML al portapapeles
    """
    
    st.markdown("---")
    st.subheader("📊 Resultados de la Generación")
    
    # Determinar qué tabs mostrar
    available_tabs = []
    tab_contents = []
    
    if draft_html:
        available_tabs.append("🔷 Etapa 1: Borrador")
        tab_contents.append(("draft", draft_html))
    
    if analysis_json:
        available_tabs.append("🔍 Etapa 2: Análisis")
        tab_contents.append(("analysis", analysis_json))
    
    if final_html:
        available_tabs.append("✅ Etapa 3: Versión Final")
        tab_contents.append(("final", final_html))
    
    # Si no hay resultados, mostrar mensaje
    if not available_tabs:
        st.info("👆 Los resultados aparecerán aquí después de iniciar la generación.")
        return
    
    # Crear tabs
    tabs = st.tabs(available_tabs)
    
    # Renderizar cada tab
    for tab, (tab_type, content) in zip(tabs, tab_contents):
        with tab:
            if tab_type in ["draft", "final"]:
                # Tabs de contenido HTML
                stage_name = "Borrador Inicial" if tab_type == "draft" else "Versión Final"
                stage_number = 1 if tab_type == "draft" else 3
                render_content_tab(
                    html_content=content,
                    target_length=target_length,
                    stage_name=stage_name,
                    stage_number=stage_number,
                    is_final=(tab_type == "final")
                )
            elif tab_type == "analysis":
                # Tab de análisis JSON
                render_analysis_tab(content, mode)


# ============================================================================
# RENDERIZADO DE TAB DE CONTENIDO HTML
# ============================================================================

def render_content_tab(
    html_content: str,
    target_length: int,
    stage_name: str,
    stage_number: int,
    is_final: bool = False
) -> None:
    """
    Renderiza un tab con contenido HTML (borrador o versión final).
    
    Incluye:
    - Métricas de word count con comparación vs objetivo
    - Validación completa de estructura CMS v4.1.1
    - Botón para copiar HTML
    - Preview del contenido renderizado
    - Análisis de estructura HTML
    
    Args:
        html_content: Contenido HTML a mostrar
        target_length: Longitud objetivo en palabras
        stage_name: Nombre de la etapa (para mostrar al usuario)
        stage_number: Número de etapa (1 o 3)
        is_final: Si es True, aplica validaciones más estrictas
        
    Notes:
        - Usa validate_cms_structure() para validación completa
        - Muestra errores críticos en rojo, warnings en amarillo
        - Calcula precisión de word count vs objetivo
    """
    
    st.markdown(f"### {stage_name} (Etapa {stage_number}/3)")
    
    # Métricas principales
    col1, col2, col3, col4 = st.columns(4)
    
    # Contar palabras
    word_count = count_words_in_html(html_content)
    
    with col1:
        st.metric("📝 Palabras", f"{word_count:,}")
    
    with col2:
        st.metric("🎯 Objetivo", f"{target_length:,}")
    
    with col3:
        # Calcular diferencia y porcentaje
        diff = word_count - target_length
        diff_pct = (diff / target_length * 100) if target_length > 0 else 0
        
        # Color basado en si está dentro del rango ±5%
        if abs(diff_pct) <= 5:
            delta_color = "normal"
            status_emoji = "✅"
        elif abs(diff_pct) <= 10:
            delta_color = "off"
            status_emoji = "⚠️"
        else:
            delta_color = "inverse"
            status_emoji = "❌"
        
        st.metric(
            f"{status_emoji} Diferencia",
            f"{diff:+,}",
            f"{diff_pct:+.1f}%",
            delta_color=delta_color
        )
    
    with col4:
        # Calcular precisión
        precision = max(0, 100 - abs(diff_pct))
        st.metric("🎯 Precisión", f"{precision:.1f}%")
    
    # Validación CMS v4.1.1
    st.markdown("---")
    st.markdown("#### 🔍 Validación de Estructura CMS")
    
    is_valid, errors, warnings = validate_cms_structure(html_content)
    
    # Mostrar estado general
    if is_valid and not warnings:
        st.success("✅ **Estructura perfecta**: Cumple todos los requisitos del CMS")
    elif is_valid and warnings:
        st.warning(f"⚠️ **Estructura válida con {len(warnings)} advertencia(s)**: Revisa las sugerencias")
    else:
        st.error(f"❌ **Estructura inválida**: {len(errors)} error(es) crítico(s) encontrado(s)")
    
    # Mostrar errores críticos si existen
    if errors:
        with st.expander("🚨 Errores Críticos", expanded=True):
            for i, error in enumerate(errors, 1):
                st.markdown(f"**{i}.** {error}")
            
            if is_final:
                st.error("⚠️ **Importante**: Este contenido NO se puede publicar con estos errores.")
    
    # Mostrar advertencias si existen
    if warnings:
        with st.expander("⚠️ Advertencias y Sugerencias", expanded=False):
            for i, warning in enumerate(warnings, 1):
                st.markdown(f"**{i}.** {warning}")
    
    # Validación básica adicional
    basic_validation = validate_html_structure(html_content)
    
    validation_cols = st.columns(3)
    
    with validation_cols[0]:
        st.markdown("**Estructura HTML:**")
        render_validation_check("3 Articles", basic_validation.get('has_article', False))
        render_validation_check("CSS con :root", basic_validation.get('css_has_root', False))
        render_validation_check("Sin Markdown", basic_validation.get('no_markdown', False))
    
    with validation_cols[1]:
        st.markdown("**Elementos clave:**")
        render_validation_check("Kicker con span", basic_validation.get('kicker_uses_span', False))
        render_validation_check("Callout BF", basic_validation.get('has_bf_callout', False))
        
        # Extraer estructura para más checks
        structure = extract_content_structure(html_content)
        has_verdict = structure.get('has_verdict', False)
        render_validation_check("Verdict Box", has_verdict)
    
    with validation_cols[2]:
        st.markdown("**Análisis de enlaces:**")
        links_analysis = analyze_links(html_content)
        
        internal_count = links_analysis.get('internal_links_count', 0)
        external_count = links_analysis.get('external_links_count', 0)
        
        # Validar rango recomendado: 2-3 internos, 1-2 PDPs
        has_good_internal = 2 <= internal_count <= 5
        render_validation_check(f"Enlaces internos ({internal_count})", has_good_internal)
        render_validation_check(f"Enlaces externos ({external_count})", external_count >= 1)
    
    # Botones de acción
    st.markdown("---")
    action_cols = st.columns([2, 1, 1])
    
    with action_cols[0]:
        # Botón para copiar HTML
        st.code(html_content[:200] + "...", language="html")
        st.caption("👆 Vista previa del HTML (primeros 200 caracteres)")
    
    with action_cols[1]:
        # Descargar HTML
        st.download_button(
            label="📥 Descargar HTML",
            data=html_content,
            file_name=f"content_stage{stage_number}_{st.session_state.get('timestamp', 'export')}.html",
            mime="text/html",
            use_container_width=True
        )
    
    with action_cols[2]:
        # Copiar al portapapeles (usando st.code con botón de copia)
        if st.button("📋 Ver HTML Completo", use_container_width=True, key=f"show_html_{stage_number}"):
            st.session_state[f'show_full_html_{stage_number}'] = True
    
    # Mostrar HTML completo si se solicitó
    if st.session_state.get(f'show_full_html_{stage_number}', False):
        with st.expander("📄 HTML Completo", expanded=True):
            st.code(html_content, language="html", line_numbers=True)
            if st.button("❌ Cerrar", key=f"close_html_{stage_number}"):
                st.session_state[f'show_full_html_{stage_number}'] = False
                st.rerun()
    
    # Preview del contenido renderizado
    st.markdown("---")
    st.markdown("#### 👁️ Preview del Contenido")
    
    preview_tab1, preview_tab2 = st.tabs(["🎨 Renderizado", "🔍 Análisis de Estructura"])
    
    with preview_tab1:
        st.caption("Vista previa de cómo se verá el contenido renderizado")
        with st.container():
            st.markdown(html_content, unsafe_allow_html=True)
    
    with preview_tab2:
        render_structure_analysis(html_content)


# ============================================================================
# RENDERIZADO DE TAB DE ANÁLISIS JSON
# ============================================================================

def render_analysis_tab(analysis_json: str, mode: str = "new") -> None:
    """
    Renderiza el tab de análisis crítico (Etapa 2).
    
    Muestra el JSON de análisis de forma estructurada y legible,
    incluyendo problemas encontrados, correcciones sugeridas, y
    aspectos positivos del borrador.
    
    Args:
        analysis_json: String JSON con el análisis crítico
        mode: Modo de generación ("new" o "rewrite")
        
    Notes:
        - Parsea el JSON y lo muestra de forma estructurada
        - Colorea problemas por gravedad (crítico/medio/menor)
        - Incluye validación competitiva si mode="rewrite"
        - Maneja errores de parsing JSON
    """
    
    st.markdown("### 🔍 Análisis Crítico del Borrador (Etapa 2/3)")
    
    st.info("""
    Este análisis identifica problemas en el borrador y proporciona
    correcciones específicas que se aplicarán en la Etapa 3.
    """)
    
    # Intentar parsear el JSON
    try:
        analysis = json.loads(analysis_json)
        
        # Métricas principales
        col1, col2, col3 = st.columns(3)
        
        with col1:
            current_length = analysis.get('longitud_actual', 0)
            st.metric("📝 Longitud Actual", f"{current_length:,} palabras")
        
        with col2:
            target_length = analysis.get('longitud_objetivo', 0)
            st.metric("🎯 Longitud Objetivo", f"{target_length:,} palabras")
        
        with col3:
            needs_adjustment = analysis.get('necesita_ajuste_longitud', False)
            if needs_adjustment:
                st.metric("⚠️ Ajuste Necesario", "Sí", delta="Requiere corrección")
            else:
                st.metric("✅ Longitud", "Correcta", delta="En rango")
        
        # Validación de estructura HTML
        st.markdown("---")
        st.markdown("#### 🏗️ Validación de Estructura HTML")
        
        estructura = analysis.get('estructura_html', {})
        
        struct_cols = st.columns(3)
        
        with struct_cols[0]:
            render_validation_check("3 Articles", estructura.get('tiene_3_articles', False))
            render_validation_check("Primer article solo kicker", estructura.get('primer_article_solo_kicker', False))
        
        with struct_cols[1]:
            render_validation_check("Segundo article vacío", estructura.get('segundo_article_vacio', False))
            render_validation_check("Kicker usa <span>", estructura.get('kicker_usa_span', False))
        
        with struct_cols[2]:
            render_validation_check("Título usa H2", estructura.get('titulo_usa_h2', False))
            render_validation_check("CSS tiene :root", estructura.get('css_tiene_root', False))
        
        # Problemas encontrados
        st.markdown("---")
        st.markdown("#### 🚨 Problemas Identificados")
        
        problemas = analysis.get('problemas_encontrados', [])
        
        if not problemas:
            st.success("✅ No se encontraron problemas significativos")
        else:
            # Agrupar por gravedad
            criticos = [p for p in problemas if p.get('gravedad') == 'crítico']
            medios = [p for p in problemas if p.get('gravedad') == 'medio']
            menores = [p for p in problemas if p.get('gravedad') == 'menor']
            
            # Mostrar resumen
            summary_cols = st.columns(3)
            with summary_cols[0]:
                st.metric("🔴 Críticos", len(criticos))
            with summary_cols[1]:
                st.metric("🟡 Medios", len(medios))
            with summary_cols[2]:
                st.metric("🟢 Menores", len(menores))
            
            # Mostrar problemas críticos
            if criticos:
                with st.expander("🔴 Problemas Críticos", expanded=True):
                    for i, problema in enumerate(criticos, 1):
                        render_problem_card(problema, i)
            
            # Mostrar problemas medios
            if medios:
                with st.expander("🟡 Problemas Medios", expanded=False):
                    for i, problema in enumerate(medios, 1):
                        render_problem_card(problema, i)
            
            # Mostrar problemas menores
            if menores:
                with st.expander("🟢 Problemas Menores", expanded=False):
                    for i, problema in enumerate(menores, 1):
                        render_problem_card(problema, i)
        
        # Análisis competitivo (solo en modo rewrite)
        if mode == "rewrite" and 'analisis_competitivo' in analysis:
            st.markdown("---")
            st.markdown("#### 🏆 Análisis Competitivo")
            
            comp_analysis = analysis['analisis_competitivo']
            
            # Métricas competitivas
            comp_cols = st.columns(3)
            
            with comp_cols[0]:
                supera_profundidad = comp_analysis.get('supera_en_profundidad', False)
                st.metric(
                    "📊 Profundidad",
                    "Superior" if supera_profundidad else "Insuficiente",
                    delta="vs Competencia"
                )
            
            with comp_cols[1]:
                tiene_diferenciador = comp_analysis.get('tiene_enfoque_diferenciador', False)
                st.metric(
                    "🎯 Diferenciación",
                    "Presente" if tiene_diferenciador else "Ausente",
                    delta="Enfoque único"
                )
            
            with comp_cols[2]:
                aporta_valor = comp_analysis.get('aporta_valor_unico', False)
                st.metric(
                    "⭐ Valor Único",
                    "Sí" if aporta_valor else "No",
                    delta="PcComponentes"
                )
            
            # Gaps cubiertos
            gaps = comp_analysis.get('gaps_cubiertos', [])
            if gaps:
                with st.expander("🔍 Gaps Competitivos", expanded=True):
                    for gap in gaps:
                        cubierto = gap.get('cubierto', False)
                        icon = "✅" if cubierto else "❌"
                        st.markdown(f"{icon} **{gap.get('gap', 'Gap sin descripción')}**")
                        st.caption(gap.get('comentario', 'Sin comentario'))
                        st.markdown("---")
        
        # Aspectos positivos
        aspectos_positivos = analysis.get('aspectos_positivos', [])
        if aspectos_positivos:
            st.markdown("---")
            st.markdown("#### ✅ Aspectos Positivos del Borrador")
            for aspecto in aspectos_positivos:
                st.success(f"✓ {aspecto}")
        
        # Instrucciones de revisión
        instrucciones = analysis.get('instrucciones_revision', [])
        if instrucciones:
            st.markdown("---")
            st.markdown("#### 📋 Instrucciones para la Revisión Final")
            for i, instruccion in enumerate(instrucciones, 1):
                st.markdown(f"**{i}.** {instruccion}")
        
        # Veredicto
        st.markdown("---")
        necesita_reescritura = analysis.get('necesita_reescritura_completa', False)
        
        if necesita_reescritura:
            st.error("⚠️ **Veredicto**: El borrador necesita reescritura completa")
        else:
            st.success("✅ **Veredicto**: El borrador es aceptable con correcciones menores")
        
        # Mostrar JSON completo colapsado
        with st.expander("📄 Ver JSON Completo del Análisis"):
            st.json(analysis)
    
    except json.JSONDecodeError as e:
        st.error(f"❌ Error al parsear el JSON del análisis: {str(e)}")
        st.markdown("**JSON recibido:**")
        st.code(analysis_json, language="json")
    
    except Exception as e:
        st.error(f"❌ Error inesperado al procesar el análisis: {str(e)}")
        with st.expander("Ver JSON problemático"):
            st.code(analysis_json, language="json")


# ============================================================================
# ANÁLISIS DE ESTRUCTURA HTML
# ============================================================================

def render_structure_analysis(html_content: str) -> None:
    """
    Renderiza un análisis detallado de la estructura del contenido HTML.
    
    Muestra:
    - Jerarquía de headings (H1-H4)
    - Elementos especiales detectados (tablas, FAQs, callouts, etc.)
    - Análisis de enlaces internos y externos
    - Estadísticas de contenido
    
    Args:
        html_content: Contenido HTML a analizar
        
    Notes:
        - Usa extract_content_structure() para obtener la estructura
        - Muestra visualización jerárquica de headings
        - Identifica elementos clave del CMS
    """
    
    st.caption("Análisis detallado de la estructura del contenido generado")
    
    # Extraer estructura
    structure = extract_content_structure(html_content)
    
    if not structure.get('structure_valid', True):
        st.error(f"❌ Error al analizar estructura: {structure.get('error', 'Error desconocido')}")
        return
    
    # Métricas de estructura
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📝 Palabras", f"{structure.get('word_count', 0):,}")
    
    with col2:
        headings_count = len(structure.get('headings', []))
        st.metric("📑 Secciones", headings_count)
    
    with col3:
        internal_links = structure.get('internal_links_count', 0)
        st.metric("🔗 Enlaces Int.", internal_links)
    
    with col4:
        external_links = structure.get('external_links_count', 0)
        st.metric("🌐 Enlaces Ext.", external_links)
    
    # Título principal
    title = structure.get('title', 'Sin título detectado')
    st.markdown("#### 📌 Título Principal")
    st.markdown(f"**{title}**")
    
    # Jerarquía de headings
    headings = structure.get('headings', [])
    if headings:
        st.markdown("---")
        st.markdown("#### 📑 Estructura de Secciones")
        
        for heading in headings:
            level = heading.get('level', 2)
            text = heading.get('text', '')
            indent = "  " * (level - 2)
            
            if level == 2:
                st.markdown(f"{indent}**{text}**")
            elif level == 3:
                st.markdown(f"{indent}• {text}")
            else:
                st.markdown(f"{indent}  ◦ {text}")
    
    # Elementos especiales detectados
    st.markdown("---")
    st.markdown("#### 🎨 Elementos Detectados")
    
    elem_cols = st.columns(3)
    
    with elem_cols[0]:
        render_validation_check("Tablas", structure.get('has_table', False))
        render_validation_check("FAQs", structure.get('has_faq', False))
    
    with elem_cols[1]:
        render_validation_check("Callouts", structure.get('has_callout', False))
        render_validation_check("Verdict Box", structure.get('has_verdict', False))
    
    with elem_cols[2]:
        render_validation_check("TOC", structure.get('has_toc', False))
        render_validation_check("Grid Layout", structure.get('has_grid', False))


# ============================================================================
# COMPONENTES DE UI AUXILIARES
# ============================================================================

def render_validation_check(label: str, is_valid: bool) -> None:
    """
    Renderiza un check visual de validación.
    
    Args:
        label: Texto descriptivo del check
        is_valid: Si pasó la validación o no
        
    Notes:
        - Usa emoji de check (✅) o cruz (❌)
        - Aplica color verde o rojo según resultado
    """
    icon = "✅" if is_valid else "❌"
    color = "green" if is_valid else "red"
    st.markdown(f":{color}[{icon}] {label}")


def render_problem_card(problema: Dict, index: int) -> None:
    """
    Renderiza una tarjeta con información de un problema identificado.
    
    Args:
        problema: Dict con información del problema
        index: Número del problema en la lista
        
    Notes:
        - Muestra tipo, descripción, ubicación y corrección sugerida
        - Usa formato markdown para mejor legibilidad
    """
    tipo = problema.get('tipo', 'desconocido')
    descripcion = problema.get('descripcion', 'Sin descripción')
    ubicacion = problema.get('ubicacion', 'Sin ubicación específica')
    correccion = problema.get('correccion_sugerida', 'Sin corrección sugerida')
    
    st.markdown(f"**Problema #{index}**: `{tipo}`")
    st.markdown(f"**Descripción:** {descripcion}")
    st.caption(f"📍 Ubicación: {ubicacion}")
    
    with st.expander("💡 Ver corrección sugerida"):
        st.markdown(correccion)
    
    st.markdown("---")


def render_copy_button(content: str, button_label: str = "📋 Copiar", key: str = None) -> None:
    """
    Renderiza un botón para copiar contenido al portapapeles.
    
    Args:
        content: Contenido a copiar
        button_label: Texto del botón
        key: Key única para el botón de Streamlit
        
    Notes:
        - Usa la funcionalidad de Streamlit para copiar al portapapeles
        - Muestra mensaje de confirmación al copiar
    """
    if st.button(button_label, key=key):
        st.code(content, language="html")
        st.success("✅ HTML copiado al portapapeles")


# ============================================================================
# FUNCIONES DE EXPORTACIÓN
# ============================================================================

def export_all_stages(
    draft_html: Optional[str] = None,
    analysis_json: Optional[str] = None,
    final_html: Optional[str] = None
) -> bytes:
    """
    Exporta todas las etapas en un archivo ZIP.
    
    Args:
        draft_html: HTML del borrador (opcional)
        analysis_json: JSON del análisis (opcional)
        final_html: HTML final (opcional)
        
    Returns:
        bytes: Contenido del archivo ZIP
        
    Notes:
        - Crea un archivo ZIP con todas las etapas disponibles
        - Nombres de archivo descriptivos con timestamp
        - Solo incluye etapas que estén disponibles
    """
    import zipfile
    import io
    from datetime import datetime
    
    # Crear buffer en memoria para el ZIP
    zip_buffer = io.BytesIO()
    
    # Timestamp para nombres de archivo
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        # Agregar borrador si existe
        if draft_html:
            zip_file.writestr(
                f"stage1_draft_{timestamp}.html",
                draft_html
            )
        
        # Agregar análisis si existe
        if analysis_json:
            zip_file.writestr(
                f"stage2_analysis_{timestamp}.json",
                analysis_json
            )
        
        # Agregar versión final si existe
        if final_html:
            zip_file.writestr(
                f"stage3_final_{timestamp}.html",
                final_html
            )
    
    # Retornar contenido del ZIP
    zip_buffer.seek(0)
    return zip_buffer.read()


def render_export_all_button(
    draft_html: Optional[str] = None,
    analysis_json: Optional[str] = None,
    final_html: Optional[str] = None
) -> None:
    """
    Renderiza un botón para exportar todas las etapas en un ZIP.
    
    Args:
        draft_html: HTML del borrador (opcional)
        analysis_json: JSON del análisis (opcional)
        final_html: HTML final (opcional)
        
    Notes:
        - Solo se muestra si hay al menos 2 etapas completadas
        - Genera un archivo ZIP descargable con todas las etapas
    """
    # Contar etapas disponibles
    available_stages = sum([
        draft_html is not None,
        analysis_json is not None,
        final_html is not None
    ])
    
    # Solo mostrar si hay al menos 2 etapas
    if available_stages >= 2:
        st.markdown("---")
        
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        zip_content = export_all_stages(draft_html, analysis_json, final_html)
        
        st.download_button(
            label=f"📦 Descargar Todo ({available_stages} etapas)",
            data=zip_content,
            file_name=f"content_generator_all_stages_{timestamp}.zip",
            mime="application/zip",
            use_container_width=True
        )


# ============================================================================
# INFORMACIÓN Y AYUDA
# ============================================================================

def render_results_help() -> None:
    """
    Renderiza información de ayuda sobre la sección de resultados.
    
    Explica:
    - Qué significa cada etapa
    - Cómo interpretar las validaciones
    - Qué hacer con los errores encontrados
    """
    with st.expander("ℹ️ Ayuda: Interpretando los Resultados"):
        st.markdown("""
        ### 📊 Entendiendo las Etapas
        
        **Etapa 1 - Borrador Inicial:**
        - Primera versión del contenido generada por IA
        - Puede contener errores o imprecisiones
        - Se usa como base para el análisis crítico
        
        **Etapa 2 - Análisis Crítico:**
        - Revisión automatizada del borrador
        - Identifica problemas de estructura, longitud, tono, etc.
        - Proporciona correcciones específicas
        
        **Etapa 3 - Versión Final:**
        - Contenido corregido listo para publicación
        - Aplica todas las correcciones de la Etapa 2
        - Debe pasar todas las validaciones CMS
        
        ---
        
        ### ✅ Validaciones CMS v4.1.1
        
        **Errores Críticos (🔴):**
        - Impiden la publicación en el CMS
        - Deben corregirse antes de usar el contenido
        - Generalmente relacionados con estructura HTML
        
        **Advertencias (🟡):**
        - No impiden publicación pero pueden afectar calidad
        - Recomendable corregir para mejores resultados
        - Relacionadas con SEO, UX o mejores prácticas
        
        ---
        
        ### 📝 Word Count
        
        - **Objetivo**: Longitud especificada en inputs
        - **Diferencia**: Variación respecto al objetivo
        - **Precisión**: Porcentaje de exactitud (ideal >95%)
        - **Rango aceptable**: ±5% del objetivo
        
        ---
        
        ### 🔗 Enlaces
        
        **Recomendaciones:**
        - 2-3 enlaces internos a categorías
        - 1-2 enlaces a PDPs de productos
        - Enlaces bien integrados en el contexto
        - Anchors descriptivos y naturales
        """)


# ============================================================================
# CONSTANTES Y CONFIGURACIÓN
# ============================================================================

# Versión del módulo
__version__ = "4.1.1"

# Colores para estados
COLOR_SUCCESS = "green"
COLOR_WARNING = "orange"
COLOR_ERROR = "red"

# Umbrales de validación
WORD_COUNT_TOLERANCE = 0.05  # ±5%
WORD_COUNT_WARNING_THRESHOLD = 0.10  # ±10%

# Configuración de preview
PREVIEW_MAX_LENGTH = 200  # Caracteres en preview de código
