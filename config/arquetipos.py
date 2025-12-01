# -*- coding: utf-8 -*-
"""
Arquetipos de Contenido - PcComponentes Content Generator
Versión 4.5.0

Define los 34 arquetipos de contenido SEO disponibles para la generación.
Cada arquetipo incluye: estructura, tono, keywords, preguntas guía,
rangos de longitud y campos específicos.

NOTA: Este archivo usa la ortografía correcta en español "arquetipos" (con 'qu').
Si encuentras referencias a "archetipos" (con 'ch'), deben actualizarse.

Autor: PcComponentes - Product Discovery & Content
"""

from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

__version__ = "4.5.0"


# ============================================================================
# CONSTANTES DE LONGITUD
# ============================================================================

DEFAULT_MIN_LENGTH = 800
DEFAULT_MAX_LENGTH = 2500
DEFAULT_CONTENT_LENGTH = 1500


# ============================================================================
# DEFINICIÓN DE ARQUETIPOS
# ============================================================================

ARQUETIPOS: Dict[str, Dict[str, Any]] = {
    
    # -------------------------------------------------------------------------
    # ARQ-1 a ARQ-5: Arquetipos Fundamentales
    # -------------------------------------------------------------------------
    
    "ARQ-1": {
        "code": "ARQ-1",
        "name": "Artículos SEO con Enlaces Internos",
        "description": "Artículo optimizado para SEO con estructura de enlaces internos estratégicos hacia categorías y productos relevantes.",
        "tone": "Informativo, profesional y orientado a la conversión",
        "keywords": ["seo", "enlaces internos", "categorías", "productos"],
        "structure": [
            "Introducción con keyword principal",
            "Desarrollo con H2/H3 estructurados",
            "Secciones con enlaces internos contextuales",
            "Tabla comparativa (opcional)",
            "FAQs con schema markup",
            "Veredicto final con CTA"
        ],
        "guiding_questions": [
            "¿Cuál es el objetivo principal del artículo?",
            "¿A qué categorías de productos debe enlazar?",
            "¿Qué productos específicos deben destacarse?",
            "¿Hay ofertas o promociones actuales a mencionar?"
        ],
        "default_length": 1500,
        "min_length": 1000,
        "max_length": 2500,
        "visual_elements": ["toc", "table", "callout", "verdict_box"],
        "campos_especificos": ["categoria_principal", "productos_destacados"]
    },
    
    "ARQ-2": {
        "code": "ARQ-2",
        "name": "Guía Paso a Paso",
        "description": "Tutorial detallado que guía al usuario a través de un proceso con pasos numerados y claros.",
        "tone": "Didáctico, claro y accesible",
        "keywords": ["guía", "tutorial", "paso a paso", "cómo"],
        "structure": [
            "Introducción: qué aprenderá el lector",
            "Requisitos previos (si aplica)",
            "Pasos numerados con instrucciones detalladas",
            "Tips y advertencias en callouts",
            "Resumen de pasos",
            "FAQs sobre el proceso",
            "Conclusión con siguientes pasos"
        ],
        "guiding_questions": [
            "¿Qué nivel de experiencia tiene el usuario objetivo?",
            "¿Cuántos pasos principales tiene el proceso?",
            "¿Qué herramientas o materiales se necesitan?",
            "¿Cuáles son los errores comunes a evitar?"
        ],
        "default_length": 1800,
        "min_length": 1200,
        "max_length": 3000,
        "visual_elements": ["toc", "callout", "numbered_list"],
        "campos_especificos": ["nivel_dificultad", "tiempo_estimado", "herramientas"]
    },
    
    "ARQ-3": {
        "code": "ARQ-3",
        "name": "Explicación / Educativo",
        "description": "Contenido educativo que explica conceptos, tecnologías o temas complejos de forma accesible.",
        "tone": "Educativo, claro y profundo",
        "keywords": ["qué es", "explicación", "guía", "entender"],
        "structure": [
            "Definición clara del concepto",
            "Contexto histórico o técnico",
            "Cómo funciona (explicación detallada)",
            "Ejemplos prácticos",
            "Ventajas y desventajas",
            "Casos de uso",
            "FAQs",
            "Conclusión y recursos adicionales"
        ],
        "guiding_questions": [
            "¿Qué concepto o tecnología se va a explicar?",
            "¿Qué nivel de profundidad técnica es apropiado?",
            "¿Hay analogías o ejemplos cotidianos útiles?",
            "¿Qué conceptos relacionados deben mencionarse?"
        ],
        "default_length": 1600,
        "min_length": 1000,
        "max_length": 2500,
        "visual_elements": ["toc", "callout", "table"],
        "campos_especificos": ["concepto_principal", "nivel_tecnico"]
    },
    
    "ARQ-4": {
        "code": "ARQ-4",
        "name": "Review / Análisis de Producto",
        "description": "Análisis detallado de un producto con especificaciones, pruebas, pros/contras y veredicto.",
        "tone": "Experto, objetivo y detallado",
        "keywords": ["review", "análisis", "opinión", "prueba"],
        "structure": [
            "Introducción y primeras impresiones",
            "Especificaciones técnicas (tabla)",
            "Diseño y construcción",
            "Rendimiento en pruebas",
            "Características destacadas",
            "Puntos fuertes y débiles",
            "Comparación con alternativas",
            "FAQs del producto",
            "Veredicto final con puntuación"
        ],
        "guiding_questions": [
            "¿Qué producto específico se analiza?",
            "¿Cuáles son sus especificaciones clave?",
            "¿Contra qué productos compite directamente?",
            "¿Para qué tipo de usuario es ideal?",
            "¿Hay datos de pruebas o benchmarks disponibles?"
        ],
        "default_length": 2000,
        "min_length": 1500,
        "max_length": 3500,
        "visual_elements": ["toc", "table", "verdict_box", "callout"],
        "campos_especificos": ["producto_url", "precio", "competidores"]
    },
    
    "ARQ-5": {
        "code": "ARQ-5",
        "name": "Comparativa A vs B",
        "description": "Comparación directa entre dos productos o tecnologías, analizando diferencias y ayudando en la decisión.",
        "tone": "Objetivo, analítico y útil para la decisión",
        "keywords": ["vs", "comparativa", "diferencias", "cuál elegir"],
        "structure": [
            "Introducción a ambas opciones",
            "Tabla comparativa de especificaciones",
            "Comparación por categorías (rendimiento, precio, etc.)",
            "¿Cuándo elegir la opción A?",
            "¿Cuándo elegir la opción B?",
            "FAQs sobre la comparativa",
            "Veredicto: cuál recomendamos y por qué"
        ],
        "guiding_questions": [
            "¿Qué dos productos/tecnologías se comparan?",
            "¿Cuáles son las diferencias clave?",
            "¿Qué criterios son más importantes para el usuario?",
            "¿Hay un claro ganador o depende del caso de uso?"
        ],
        "default_length": 1800,
        "min_length": 1200,
        "max_length": 2800,
        "visual_elements": ["toc", "table", "verdict_box"],
        "campos_especificos": ["producto_a", "producto_b", "criterios_comparacion"]
    },
    
    # -------------------------------------------------------------------------
    # ARQ-6 a ARQ-10: Arquetipos de Listas y Selección
    # -------------------------------------------------------------------------
    
    "ARQ-6": {
        "code": "ARQ-6",
        "name": "Guía de Compra",
        "description": "Guía completa para ayudar al usuario a elegir el producto adecuado según sus necesidades.",
        "tone": "Consultivo, experto y orientado a la ayuda",
        "keywords": ["guía de compra", "cómo elegir", "qué buscar"],
        "structure": [
            "Por qué necesitas una guía de compra",
            "Factores clave a considerar",
            "Tipos de productos disponibles",
            "Rangos de precio y qué esperar",
            "Errores comunes al comprar",
            "Nuestra selección recomendada",
            "FAQs de compra",
            "Conclusión y recomendación final"
        ],
        "guiding_questions": [
            "¿Qué categoría de producto cubre la guía?",
            "¿Cuáles son los factores de decisión más importantes?",
            "¿Qué rangos de precio existen?",
            "¿Hay marcas o modelos especialmente recomendados?"
        ],
        "default_length": 2000,
        "min_length": 1500,
        "max_length": 3000,
        "visual_elements": ["toc", "table", "callout", "verdict_box"],
        "campos_especificos": ["categoria", "rango_precios", "marcas_recomendadas"]
    },
    
    "ARQ-7": {
        "code": "ARQ-7",
        "name": "Roundup / Mejores X",
        "description": "Lista curada de los mejores productos en una categoría, con análisis individual y comparativa.",
        "tone": "Experto, curador y orientado a la selección",
        "keywords": ["mejores", "top", "ranking", "selección"],
        "structure": [
            "Introducción y criterios de selección",
            "Tabla resumen de productos",
            "Análisis individual de cada producto",
            "Comparativa general",
            "¿Cuál elegir según tu caso?",
            "FAQs sobre la categoría",
            "Veredicto y mejor opción global"
        ],
        "guiding_questions": [
            "¿Qué categoría de productos se cubre?",
            "¿Cuántos productos incluir en el ranking?",
            "¿Qué criterios definen 'mejor'?",
            "¿Hay un producto claramente superior?"
        ],
        "default_length": 2200,
        "min_length": 1500,
        "max_length": 4000,
        "visual_elements": ["toc", "table", "grid", "verdict_box"],
        "campos_especificos": ["categoria", "num_productos", "criterios_ranking"]
    },
    
    "ARQ-8": {
        "code": "ARQ-8",
        "name": "Lista de Recomendaciones",
        "description": "Lista de productos o recursos recomendados para un propósito específico.",
        "tone": "Amigable, útil y directo",
        "keywords": ["recomendaciones", "lista", "sugerencias", "opciones"],
        "structure": [
            "Introducción al tema",
            "Criterios de selección",
            "Lista de recomendaciones con descripción",
            "Tips para elegir",
            "FAQs",
            "Conclusión"
        ],
        "guiding_questions": [
            "¿Para qué propósito son las recomendaciones?",
            "¿Cuántos items incluir?",
            "¿Hay diferentes rangos de precio?",
            "¿Qué diferencia cada recomendación?"
        ],
        "default_length": 1400,
        "min_length": 800,
        "max_length": 2200,
        "visual_elements": ["toc", "callout"],
        "campos_especificos": ["proposito", "num_items"]
    },
    
    "ARQ-9": {
        "code": "ARQ-9",
        "name": "Mejores Productos por Precio",
        "description": "Selección de los mejores productos organizados por rangos de precio.",
        "tone": "Práctico, orientado al presupuesto",
        "keywords": ["mejor calidad precio", "por menos de", "económico", "presupuesto"],
        "structure": [
            "Introducción y rangos de precio",
            "Mejor opción económica",
            "Mejor opción gama media",
            "Mejor opción premium",
            "Tabla comparativa por precio",
            "¿Cuánto invertir según tu uso?",
            "FAQs sobre precios",
            "Conclusión"
        ],
        "guiding_questions": [
            "¿Qué rangos de precio cubrir?",
            "¿Cuál es el mejor producto en cada rango?",
            "¿Hay ofertas o descuentos actuales?",
            "¿Merece la pena pagar más?"
        ],
        "default_length": 1600,
        "min_length": 1000,
        "max_length": 2500,
        "visual_elements": ["toc", "table", "callout"],
        "campos_especificos": ["rangos_precio", "productos_por_rango"]
    },
    
    "ARQ-10": {
        "code": "ARQ-10",
        "name": "Productos para Perfil Específico",
        "description": "Selección de productos ideales para un perfil de usuario concreto (gamers, profesionales, etc.).",
        "tone": "Personalizado, empático y especializado",
        "keywords": ["para gamers", "para profesionales", "para estudiantes", "ideal para"],
        "structure": [
            "Introducción al perfil de usuario",
            "Necesidades específicas del perfil",
            "Productos recomendados",
            "Setup o configuración ideal",
            "Errores a evitar",
            "FAQs del perfil",
            "Conclusión y kit recomendado"
        ],
        "guiding_questions": [
            "¿Qué perfil de usuario es el objetivo?",
            "¿Cuáles son sus necesidades principales?",
            "¿Qué presupuesto típico tienen?",
            "¿Hay productos imprescindibles para este perfil?"
        ],
        "default_length": 1700,
        "min_length": 1200,
        "max_length": 2600,
        "visual_elements": ["toc", "callout", "grid"],
        "campos_especificos": ["perfil_usuario", "necesidades", "presupuesto_tipico"]
    },
    
    # -------------------------------------------------------------------------
    # ARQ-11 a ARQ-15: Arquetipos Técnicos y de Problema/Solución
    # -------------------------------------------------------------------------
    
    "ARQ-11": {
        "code": "ARQ-11",
        "name": "Solución de Problemas / Troubleshooting",
        "description": "Guía para diagnosticar y resolver problemas técnicos comunes.",
        "tone": "Técnico, metódico y orientado a soluciones",
        "keywords": ["problema", "solución", "error", "no funciona", "cómo arreglar"],
        "structure": [
            "Descripción del problema",
            "Causas comunes",
            "Diagnóstico paso a paso",
            "Soluciones ordenadas por probabilidad",
            "Cuándo buscar ayuda profesional",
            "FAQs relacionadas",
            "Prevención futura"
        ],
        "guiding_questions": [
            "¿Qué problema específico se aborda?",
            "¿Cuáles son las causas más frecuentes?",
            "¿Qué nivel técnico requiere la solución?",
            "¿Hay riesgos al intentar solucionarlo?"
        ],
        "default_length": 1500,
        "min_length": 1000,
        "max_length": 2200,
        "visual_elements": ["toc", "callout", "numbered_list"],
        "campos_especificos": ["problema", "causas", "nivel_tecnico"]
    },
    
    "ARQ-12": {
        "code": "ARQ-12",
        "name": "Especificaciones Técnicas Explicadas",
        "description": "Explicación de especificaciones técnicas de forma accesible para el usuario.",
        "tone": "Técnico pero accesible, educativo",
        "keywords": ["especificaciones", "qué significa", "explicación técnica"],
        "structure": [
            "Introducción a las especificaciones",
            "Glosario de términos",
            "Explicación de cada especificación",
            "Cómo afecta al rendimiento",
            "Valores recomendados según uso",
            "FAQs técnicas",
            "Conclusión"
        ],
        "guiding_questions": [
            "¿Qué tipo de producto o tecnología?",
            "¿Cuáles son las specs más confusas?",
            "¿Qué valores son buenos/malos/excelentes?",
            "¿Hay mitos o malentendidos comunes?"
        ],
        "default_length": 1600,
        "min_length": 1000,
        "max_length": 2500,
        "visual_elements": ["toc", "table", "callout"],
        "campos_especificos": ["tipo_producto", "specs_principales"]
    },
    
    "ARQ-13": {
        "code": "ARQ-13",
        "name": "Configuración y Setup",
        "description": "Guía de configuración inicial o setup de un producto o sistema.",
        "tone": "Práctico, detallado y paso a paso",
        "keywords": ["configurar", "setup", "instalación", "primeros pasos"],
        "structure": [
            "Qué necesitas antes de empezar",
            "Unboxing y contenido",
            "Instalación física/software",
            "Configuración inicial",
            "Configuración avanzada (opcional)",
            "Prueba de funcionamiento",
            "Solución de problemas comunes",
            "FAQs de configuración"
        ],
        "guiding_questions": [
            "¿Qué producto o sistema se configura?",
            "¿Qué conocimientos previos se necesitan?",
            "¿Cuánto tiempo lleva la configuración?",
            "¿Cuáles son los errores más comunes?"
        ],
        "default_length": 1800,
        "min_length": 1200,
        "max_length": 2800,
        "visual_elements": ["toc", "numbered_list", "callout"],
        "campos_especificos": ["producto", "tiempo_setup", "requisitos"]
    },
    
    "ARQ-14": {
        "code": "ARQ-14",
        "name": "Optimización y Mejora",
        "description": "Guía para optimizar el rendimiento o mejorar un producto/sistema existente.",
        "tone": "Experto, orientado a resultados",
        "keywords": ["optimizar", "mejorar", "rendimiento", "tips"],
        "structure": [
            "Estado actual vs potencial",
            "Diagnóstico de rendimiento",
            "Optimizaciones rápidas",
            "Mejoras intermedias",
            "Mejoras avanzadas",
            "Medición de resultados",
            "FAQs de optimización",
            "Conclusión y mantenimiento"
        ],
        "guiding_questions": [
            "¿Qué se quiere optimizar?",
            "¿Cuál es el problema de rendimiento actual?",
            "¿Qué nivel de mejora es realista?",
            "¿Requiere inversión adicional?"
        ],
        "default_length": 1700,
        "min_length": 1200,
        "max_length": 2600,
        "visual_elements": ["toc", "callout", "table"],
        "campos_especificos": ["objetivo_optimizacion", "metricas"]
    },
    
    "ARQ-15": {
        "code": "ARQ-15",
        "name": "Mantenimiento y Cuidados",
        "description": "Guía de mantenimiento preventivo y cuidados para alargar la vida útil de productos.",
        "tone": "Práctico, preventivo y cuidadoso",
        "keywords": ["mantenimiento", "cuidados", "limpieza", "vida útil"],
        "structure": [
            "Importancia del mantenimiento",
            "Mantenimiento diario/semanal",
            "Mantenimiento mensual",
            "Mantenimiento anual",
            "Señales de problemas",
            "Productos de limpieza recomendados",
            "FAQs de mantenimiento",
            "Calendario de mantenimiento"
        ],
        "guiding_questions": [
            "¿Qué producto requiere mantenimiento?",
            "¿Con qué frecuencia debe hacerse?",
            "¿Qué herramientas o productos se necesitan?",
            "¿Qué señales indican problemas?"
        ],
        "default_length": 1400,
        "min_length": 900,
        "max_length": 2000,
        "visual_elements": ["toc", "callout", "table"],
        "campos_especificos": ["producto", "frecuencia_mantenimiento"]
    },
    
    # -------------------------------------------------------------------------
    # ARQ-16 a ARQ-20: Arquetipos de Tendencias y Actualidad
    # -------------------------------------------------------------------------
    
    "ARQ-16": {
        "code": "ARQ-16",
        "name": "Novedades y Lanzamientos",
        "description": "Cobertura de nuevos productos, lanzamientos o actualizaciones importantes.",
        "tone": "Entusiasta, informativo y actualizado",
        "keywords": ["nuevo", "lanzamiento", "2025", "última versión"],
        "structure": [
            "Anuncio del lanzamiento",
            "Características principales",
            "Comparación con versión anterior",
            "Precio y disponibilidad",
            "Primeras impresiones",
            "¿Merece la pena actualizar?",
            "FAQs del lanzamiento",
            "Conclusión"
        ],
        "guiding_questions": [
            "¿Qué producto se ha lanzado?",
            "¿Cuáles son las novedades principales?",
            "¿Cuándo estará disponible y a qué precio?",
            "¿Merece la pena frente al modelo anterior?"
        ],
        "default_length": 1500,
        "min_length": 1000,
        "max_length": 2200,
        "visual_elements": ["toc", "table", "callout"],
        "campos_especificos": ["producto_nuevo", "fecha_lanzamiento", "precio"]
    },
    
    "ARQ-17": {
        "code": "ARQ-17",
        "name": "Tendencias del Sector",
        "description": "Análisis de tendencias actuales y futuras en el sector tecnológico.",
        "tone": "Analítico, visionario e informado",
        "keywords": ["tendencias", "futuro", "2025", "hacia dónde va"],
        "structure": [
            "Estado actual del sector",
            "Tendencias emergentes",
            "Tecnologías a vigilar",
            "Impacto en el consumidor",
            "Predicciones a corto/medio plazo",
            "Cómo prepararse",
            "FAQs sobre tendencias",
            "Conclusión"
        ],
        "guiding_questions": [
            "¿Qué sector o tecnología se analiza?",
            "¿Cuáles son las tendencias más relevantes?",
            "¿Qué impacto tendrán en el usuario?",
            "¿Hay productos actuales que ya incorporan estas tendencias?"
        ],
        "default_length": 1600,
        "min_length": 1000,
        "max_length": 2400,
        "visual_elements": ["toc", "callout"],
        "campos_especificos": ["sector", "tendencias_principales"]
    },
    
    "ARQ-18": {
        "code": "ARQ-18",
        "name": "Eventos y Ferias Tech",
        "description": "Cobertura de eventos tecnológicos, ferias y presentaciones importantes.",
        "tone": "Periodístico, informativo y emocionante",
        "keywords": ["CES", "MWC", "evento", "feria", "presentación"],
        "structure": [
            "Qué es el evento",
            "Novedades más destacadas",
            "Análisis por categoría",
            "Sorpresas y decepciones",
            "Impacto para el consumidor",
            "Cuándo llegarán los productos",
            "FAQs del evento",
            "Resumen final"
        ],
        "guiding_questions": [
            "¿Qué evento se cubre?",
            "¿Cuáles fueron los anuncios más importantes?",
            "¿Qué productos llegarán al mercado español?",
            "¿Hay exclusivas o novedades de PcComponentes?"
        ],
        "default_length": 1800,
        "min_length": 1200,
        "max_length": 3000,
        "visual_elements": ["toc", "grid", "callout"],
        "campos_especificos": ["evento", "fecha", "marcas_destacadas"]
    },
    
    "ARQ-19": {
        "code": "ARQ-19",
        "name": "Ofertas y Promociones",
        "description": "Contenido sobre ofertas, descuentos y promociones especiales.",
        "tone": "Urgente, atractivo y orientado a la acción",
        "keywords": ["oferta", "descuento", "promoción", "Black Friday", "rebajas"],
        "structure": [
            "Resumen de la promoción",
            "Mejores ofertas destacadas",
            "Ofertas por categoría",
            "Cómo aprovechar al máximo",
            "Productos que merece la pena comprar",
            "Fechas y condiciones",
            "FAQs de la promoción",
            "Conclusión y llamada a la acción"
        ],
        "guiding_questions": [
            "¿Qué promoción o evento de ofertas es?",
            "¿Cuáles son las ofertas más destacadas?",
            "¿Cuánto duran las ofertas?",
            "¿Hay códigos de descuento adicionales?"
        ],
        "default_length": 1500,
        "min_length": 1000,
        "max_length": 2500,
        "visual_elements": ["toc", "callout_bf", "grid", "table"],
        "campos_especificos": ["tipo_promocion", "fechas", "mejores_ofertas"]
    },
    
    "ARQ-20": {
        "code": "ARQ-20",
        "name": "Black Friday / Cyber Monday",
        "description": "Contenido especializado para las campañas de Black Friday y Cyber Monday.",
        "tone": "Urgente, emocionante y orientado a ofertas",
        "keywords": ["Black Friday", "Cyber Monday", "ofertas", "descuentos"],
        "structure": [
            "Fechas y horarios importantes",
            "Cómo prepararse",
            "Top ofertas destacadas",
            "Mejores ofertas por categoría",
            "Ofertas flash y exclusivas",
            "Consejos para comprar",
            "FAQs Black Friday",
            "Actualización en tiempo real"
        ],
        "guiding_questions": [
            "¿Qué ofertas exclusivas hay en PcComponentes?",
            "¿Cuáles son los productos estrella?",
            "¿Hay ofertas flash programadas?",
            "¿Qué categorías tienen mejores descuentos?"
        ],
        "default_length": 2000,
        "min_length": 1500,
        "max_length": 4000,
        "visual_elements": ["toc", "callout_bf", "grid", "table", "verdict_box"],
        "campos_especificos": ["ofertas_estrella", "categorias_destacadas", "ofertas_flash"]
    },
    
    # -------------------------------------------------------------------------
    # ARQ-21 a ARQ-25: Arquetipos de Gaming y Entretenimiento
    # -------------------------------------------------------------------------
    
    "ARQ-21": {
        "code": "ARQ-21",
        "name": "Setup Gaming Completo",
        "description": "Guía para montar un setup gaming completo con todos los componentes necesarios.",
        "tone": "Gamer, entusiasta y detallado",
        "keywords": ["setup gaming", "PC gaming", "configuración gamer"],
        "structure": [
            "Objetivos del setup",
            "Presupuesto y prioridades",
            "Componentes esenciales",
            "Periféricos recomendados",
            "Setup de escritorio y ergonomía",
            "Configuración de software",
            "Upgrades futuros",
            "FAQs de setup gaming",
            "Setup final recomendado"
        ],
        "guiding_questions": [
            "¿Qué presupuesto hay disponible?",
            "¿Qué juegos o uso principal tendrá?",
            "¿Qué resolución y FPS objetivo?",
            "¿Hay componentes que ya tenga el usuario?"
        ],
        "default_length": 2200,
        "min_length": 1500,
        "max_length": 3500,
        "visual_elements": ["toc", "table", "grid", "callout"],
        "campos_especificos": ["presupuesto", "juegos_objetivo", "resolucion"]
    },
    
    "ARQ-22": {
        "code": "ARQ-22",
        "name": "Requisitos de Videojuegos",
        "description": "Análisis de requisitos de hardware para videojuegos específicos.",
        "tone": "Técnico, práctico y gamer",
        "keywords": ["requisitos", "specs mínimas", "recomendados", "fps"],
        "structure": [
            "Sobre el juego",
            "Requisitos mínimos oficiales",
            "Requisitos recomendados",
            "Requisitos para 4K/Ultra",
            "Configuraciones de hardware probadas",
            "Optimización de ajustes gráficos",
            "FAQs de rendimiento",
            "Hardware recomendado"
        ],
        "guiding_questions": [
            "¿Qué juego se analiza?",
            "¿Cuáles son los requisitos oficiales?",
            "¿Qué hardware real consigue 60fps estables?",
            "¿Hay problemas de optimización conocidos?"
        ],
        "default_length": 1400,
        "min_length": 900,
        "max_length": 2000,
        "visual_elements": ["toc", "table", "callout"],
        "campos_especificos": ["juego", "requisitos_minimos", "requisitos_recomendados"]
    },
    
    "ARQ-23": {
        "code": "ARQ-23",
        "name": "Streaming y Creación de Contenido",
        "description": "Guía para equipamiento de streaming y creación de contenido digital.",
        "tone": "Creativo, técnico y práctico",
        "keywords": ["streaming", "YouTube", "Twitch", "creador de contenido"],
        "structure": [
            "Tipos de creación de contenido",
            "Equipamiento esencial",
            "Software recomendado",
            "Configuración de OBS/streaming",
            "Iluminación y sonido",
            "Upgrades según crecimiento",
            "FAQs para streamers",
            "Kit recomendado por nivel"
        ],
        "guiding_questions": [
            "¿Qué tipo de contenido se va a crear?",
            "¿Qué plataforma principal?",
            "¿Cuál es el presupuesto inicial?",
            "¿Es principiante o ya tiene experiencia?"
        ],
        "default_length": 1800,
        "min_length": 1200,
        "max_length": 2800,
        "visual_elements": ["toc", "callout", "grid"],
        "campos_especificos": ["tipo_contenido", "plataforma", "presupuesto"]
    },
    
    "ARQ-24": {
        "code": "ARQ-24",
        "name": "Periféricos Gaming",
        "description": "Guía especializada en periféricos gaming: teclados, ratones, auriculares, etc.",
        "tone": "Gamer experto, detallado",
        "keywords": ["teclado gaming", "ratón gaming", "auriculares gaming", "periféricos"],
        "structure": [
            "Importancia de los periféricos",
            "Tipos de periféricos",
            "Características clave por periférico",
            "Mejores opciones por presupuesto",
            "Combinaciones recomendadas",
            "FAQs de periféricos",
            "Setup recomendado"
        ],
        "guiding_questions": [
            "¿Qué periférico específico se cubre?",
            "¿Qué características son más importantes para gaming?",
            "¿Hay tecnologías específicas a destacar?",
            "¿Cuál es la mejor relación calidad-precio?"
        ],
        "default_length": 1600,
        "min_length": 1000,
        "max_length": 2400,
        "visual_elements": ["toc", "table", "callout"],
        "campos_especificos": ["tipo_periferico", "caracteristicas_clave"]
    },
    
    "ARQ-25": {
        "code": "ARQ-25",
        "name": "Consolas y Gaming Portátil",
        "description": "Contenido sobre consolas de videojuegos y gaming portátil.",
        "tone": "Gamer, comparativo y actualizado",
        "keywords": ["PS5", "Xbox", "Nintendo Switch", "Steam Deck", "consola"],
        "structure": [
            "Panorama actual de consolas",
            "Comparativa de consolas",
            "Juegos exclusivos",
            "Accesorios recomendados",
            "Gaming portátil",
            "¿Qué consola elegir?",
            "FAQs de consolas",
            "Recomendación final"
        ],
        "guiding_questions": [
            "¿Qué consolas se comparan?",
            "¿Cuáles son los juegos más relevantes?",
            "¿Qué accesorios son imprescindibles?",
            "¿Para qué tipo de jugador es cada opción?"
        ],
        "default_length": 1700,
        "min_length": 1100,
        "max_length": 2600,
        "visual_elements": ["toc", "table", "verdict_box"],
        "campos_especificos": ["consolas", "juegos_exclusivos"]
    },
    
    # -------------------------------------------------------------------------
    # ARQ-26 a ARQ-30: Arquetipos Profesionales y de Productividad
    # -------------------------------------------------------------------------
    
    "ARQ-26": {
        "code": "ARQ-26",
        "name": "Workstation Profesional",
        "description": "Guía para configurar estaciones de trabajo profesionales.",
        "tone": "Profesional, técnico y orientado a productividad",
        "keywords": ["workstation", "profesional", "edición", "renderizado", "CAD"],
        "structure": [
            "Tipos de trabajo profesional",
            "Requisitos por disciplina",
            "Componentes clave",
            "Configuraciones recomendadas",
            "Software y optimización",
            "Ergonomía y espacio de trabajo",
            "FAQs profesionales",
            "Setup recomendado por disciplina"
        ],
        "guiding_questions": [
            "¿Qué tipo de trabajo profesional se realizará?",
            "¿Qué software se utilizará principalmente?",
            "¿Cuál es el presupuesto disponible?",
            "¿Hay requisitos específicos del sector?"
        ],
        "default_length": 2000,
        "min_length": 1400,
        "max_length": 3000,
        "visual_elements": ["toc", "table", "callout"],
        "campos_especificos": ["disciplina", "software_principal", "presupuesto"]
    },
    
    "ARQ-27": {
        "code": "ARQ-27",
        "name": "Teletrabajo y Home Office",
        "description": "Guía para equipar un espacio de teletrabajo productivo.",
        "tone": "Práctico, ergonómico y orientado al bienestar",
        "keywords": ["teletrabajo", "home office", "trabajo desde casa", "oficina en casa"],
        "structure": [
            "Importancia de un buen setup",
            "Espacio y mobiliario",
            "Tecnología esencial",
            "Conectividad y red",
            "Ergonomía y salud",
            "Productividad y organización",
            "FAQs de home office",
            "Kit recomendado por presupuesto"
        ],
        "guiding_questions": [
            "¿Cuántas horas al día se trabaja desde casa?",
            "¿Qué tipo de trabajo se realiza?",
            "¿Cuál es el espacio disponible?",
            "¿Hay requisitos de videoconferencias?"
        ],
        "default_length": 1600,
        "min_length": 1000,
        "max_length": 2400,
        "visual_elements": ["toc", "callout", "grid"],
        "campos_especificos": ["tipo_trabajo", "espacio_disponible"]
    },
    
    "ARQ-28": {
        "code": "ARQ-28",
        "name": "Productividad y Software",
        "description": "Guías de software y herramientas para mejorar la productividad.",
        "tone": "Práctico, orientado a resultados",
        "keywords": ["productividad", "software", "herramientas", "aplicaciones"],
        "structure": [
            "Objetivos de productividad",
            "Categorías de herramientas",
            "Software recomendado por categoría",
            "Integraciones útiles",
            "Tips de productividad",
            "FAQs de software",
            "Stack recomendado"
        ],
        "guiding_questions": [
            "¿Qué área de productividad se cubre?",
            "¿Qué herramientas se comparan?",
            "¿Hay opciones gratuitas y de pago?",
            "¿Qué integraciones son importantes?"
        ],
        "default_length": 1500,
        "min_length": 900,
        "max_length": 2200,
        "visual_elements": ["toc", "table", "callout"],
        "campos_especificos": ["area_productividad", "herramientas"]
    },
    
    "ARQ-29": {
        "code": "ARQ-29",
        "name": "Seguridad y Privacidad",
        "description": "Guías sobre seguridad informática, privacidad y protección de datos.",
        "tone": "Serio, informativo y orientado a la protección",
        "keywords": ["seguridad", "privacidad", "antivirus", "protección", "backup"],
        "structure": [
            "Importancia de la seguridad",
            "Amenazas actuales",
            "Medidas básicas de protección",
            "Herramientas de seguridad",
            "Configuración de privacidad",
            "Backup y recuperación",
            "FAQs de seguridad",
            "Checklist de seguridad"
        ],
        "guiding_questions": [
            "¿Qué aspecto de seguridad se aborda?",
            "¿Para usuario doméstico o empresa?",
            "¿Qué amenazas son más relevantes?",
            "¿Hay productos específicos a recomendar?"
        ],
        "default_length": 1600,
        "min_length": 1000,
        "max_length": 2400,
        "visual_elements": ["toc", "callout", "table"],
        "campos_especificos": ["aspecto_seguridad", "nivel_usuario"]
    },
    
    "ARQ-30": {
        "code": "ARQ-30",
        "name": "Redes y Conectividad",
        "description": "Guías sobre redes domésticas, WiFi, NAS y conectividad.",
        "tone": "Técnico accesible, práctico",
        "keywords": ["WiFi", "router", "red", "NAS", "conectividad"],
        "structure": [
            "Fundamentos de redes domésticas",
            "Tipos de conexión",
            "Equipamiento necesario",
            "Configuración paso a paso",
            "Optimización de la red",
            "Solución de problemas comunes",
            "FAQs de redes",
            "Setup recomendado"
        ],
        "guiding_questions": [
            "¿Qué aspecto de redes se cubre?",
            "¿Tamaño del hogar/oficina?",
            "¿Cuántos dispositivos se conectarán?",
            "¿Hay requisitos específicos (gaming, streaming, etc.)?"
        ],
        "default_length": 1700,
        "min_length": 1100,
        "max_length": 2600,
        "visual_elements": ["toc", "callout", "table"],
        "campos_especificos": ["tipo_red", "tamano_espacio", "num_dispositivos"]
    },
    
    # -------------------------------------------------------------------------
    # ARQ-31 a ARQ-34: Arquetipos Especiales y de Nicho
    # -------------------------------------------------------------------------
    
    "ARQ-31": {
        "code": "ARQ-31",
        "name": "Hogar Inteligente / Smart Home",
        "description": "Guías sobre domótica, dispositivos inteligentes y automatización del hogar.",
        "tone": "Moderno, práctico y orientado al futuro",
        "keywords": ["smart home", "domótica", "hogar inteligente", "automatización"],
        "structure": [
            "Qué es un hogar inteligente",
            "Ecosistemas disponibles",
            "Dispositivos esenciales",
            "Configuración e integración",
            "Automatizaciones útiles",
            "Seguridad del smart home",
            "FAQs de domótica",
            "Kit de inicio recomendado"
        ],
        "guiding_questions": [
            "¿Qué ecosistema usa el usuario (Alexa, Google, HomeKit)?",
            "¿Qué aspectos del hogar quiere automatizar?",
            "¿Cuál es el presupuesto inicial?",
            "¿Hay requisitos de compatibilidad?"
        ],
        "default_length": 1800,
        "min_length": 1200,
        "max_length": 2800,
        "visual_elements": ["toc", "callout", "grid"],
        "campos_especificos": ["ecosistema", "areas_automatizar", "presupuesto"]
    },
    
    "ARQ-32": {
        "code": "ARQ-32",
        "name": "Fotografía y Vídeo",
        "description": "Guías sobre equipamiento fotográfico, cámaras y producción de vídeo.",
        "tone": "Creativo, técnico y visual",
        "keywords": ["cámara", "fotografía", "vídeo", "objetivos", "accesorios foto"],
        "structure": [
            "Tipos de fotografía/vídeo",
            "Equipamiento por nivel",
            "Cámaras recomendadas",
            "Objetivos y accesorios",
            "Iluminación y sonido",
            "Post-producción",
            "FAQs de foto/vídeo",
            "Kit recomendado"
        ],
        "guiding_questions": [
            "¿Fotografía, vídeo o ambos?",
            "¿Nivel principiante, aficionado o profesional?",
            "¿Qué tipo de contenido se creará?",
            "¿Presupuesto disponible?"
        ],
        "default_length": 1800,
        "min_length": 1200,
        "max_length": 2800,
        "visual_elements": ["toc", "table", "callout"],
        "campos_especificos": ["tipo_contenido", "nivel", "presupuesto"]
    },
    
    "ARQ-33": {
        "code": "ARQ-33",
        "name": "Movilidad y Gadgets",
        "description": "Guías sobre smartphones, tablets, wearables y gadgets tecnológicos.",
        "tone": "Moderno, práctico y orientado a tendencias",
        "keywords": ["smartphone", "tablet", "smartwatch", "gadgets", "wearables"],
        "structure": [
            "Panorama actual del mercado",
            "Tipos de dispositivos",
            "Características clave",
            "Comparativa de opciones",
            "Accesorios recomendados",
            "Integración con otros dispositivos",
            "FAQs de movilidad",
            "Recomendaciones finales"
        ],
        "guiding_questions": [
            "¿Qué tipo de dispositivo móvil?",
            "¿Ecosistema preferido (iOS, Android)?",
            "¿Uso principal del dispositivo?",
            "¿Rango de precio?"
        ],
        "default_length": 1600,
        "min_length": 1000,
        "max_length": 2400,
        "visual_elements": ["toc", "table", "verdict_box"],
        "campos_especificos": ["tipo_dispositivo", "ecosistema", "uso_principal"]
    },
    
    "ARQ-34": {
        "code": "ARQ-34",
        "name": "Sostenibilidad y Eficiencia Energética",
        "description": "Contenido sobre tecnología sostenible, eficiencia energética y eco-friendly.",
        "tone": "Consciente, informativo y orientado al impacto positivo",
        "keywords": ["sostenible", "eficiencia energética", "eco-friendly", "consumo"],
        "structure": [
            "Importancia de la sostenibilidad tech",
            "Consumo energético de dispositivos",
            "Productos eficientes recomendados",
            "Tips para reducir consumo",
            "Reciclaje y segunda vida",
            "Certificaciones a buscar",
            "FAQs de sostenibilidad",
            "Conclusión y compromiso"
        ],
        "guiding_questions": [
            "¿Qué aspecto de sostenibilidad se aborda?",
            "¿Qué categoría de productos?",
            "¿Hay datos de consumo energético?",
            "¿Qué alternativas sostenibles existen?"
        ],
        "default_length": 1500,
        "min_length": 1000,
        "max_length": 2200,
        "visual_elements": ["toc", "callout", "table"],
        "campos_especificos": ["aspecto_sostenibilidad", "categoria_productos"]
    },
}


# ============================================================================
# FUNCIONES DE ACCESO
# ============================================================================

def get_arquetipo(code: str) -> Optional[Dict[str, Any]]:
    """
    Obtiene los datos completos de un arquetipo por su código.
    
    Args:
        code: Código del arquetipo (ej: "ARQ-1")
        
    Returns:
        Dict con todos los datos del arquetipo o None si no existe
    """
    return ARQUETIPOS.get(code)


def get_arquetipo_names() -> Dict[str, str]:
    """
    Obtiene un diccionario de código -> nombre para todos los arquetipos.
    
    Útil para selectores y dropdowns.
    
    Returns:
        Dict con {código: nombre} de todos los arquetipos
    """
    return {code: data["name"] for code, data in ARQUETIPOS.items()}


def get_arquetipo_by_name(name: str) -> Optional[Dict[str, Any]]:
    """
    Busca un arquetipo por su nombre (búsqueda parcial).
    
    Args:
        name: Nombre o parte del nombre del arquetipo
        
    Returns:
        Dict con datos del arquetipo o None si no se encuentra
    """
    name_lower = name.lower()
    for code, data in ARQUETIPOS.items():
        if name_lower in data["name"].lower():
            return data
    return None


def get_guiding_questions(code: str) -> List[str]:
    """
    Obtiene las preguntas guía de un arquetipo.
    
    Args:
        code: Código del arquetipo
        
    Returns:
        Lista de preguntas guía o lista vacía si no existe
    """
    arquetipo = ARQUETIPOS.get(code)
    if arquetipo:
        return arquetipo.get("guiding_questions", [])
    return []


def get_structure(code: str) -> List[str]:
    """
    Obtiene la estructura recomendada de un arquetipo.
    
    Args:
        code: Código del arquetipo
        
    Returns:
        Lista de secciones de la estructura o lista vacía
    """
    arquetipo = ARQUETIPOS.get(code)
    if arquetipo:
        return arquetipo.get("structure", [])
    return []


def get_default_length(code: str) -> int:
    """
    Obtiene la longitud por defecto de un arquetipo.
    
    Args:
        code: Código del arquetipo
        
    Returns:
        Longitud por defecto en palabras
    """
    arquetipo = ARQUETIPOS.get(code)
    if arquetipo:
        return arquetipo.get("default_length", DEFAULT_CONTENT_LENGTH)
    return DEFAULT_CONTENT_LENGTH


def get_length_range(code: str) -> Tuple[int, int]:
    """
    Obtiene el rango de longitud permitido para un arquetipo.
    
    Args:
        code: Código del arquetipo
        
    Returns:
        Tuple (min_length, max_length)
    """
    arquetipo = ARQUETIPOS.get(code)
    if arquetipo:
        min_len = arquetipo.get("min_length", DEFAULT_MIN_LENGTH)
        max_len = arquetipo.get("max_length", DEFAULT_MAX_LENGTH)
        return (min_len, max_len)
    return (DEFAULT_MIN_LENGTH, DEFAULT_MAX_LENGTH)


def get_visual_elements(code: str) -> List[str]:
    """
    Obtiene los elementos visuales recomendados para un arquetipo.
    
    Args:
        code: Código del arquetipo
        
    Returns:
        Lista de identificadores de elementos visuales
    """
    arquetipo = ARQUETIPOS.get(code)
    if arquetipo:
        return arquetipo.get("visual_elements", [])
    return []


def get_campos_especificos(code: str) -> List[str]:
    """
    Obtiene los campos específicos requeridos por un arquetipo.
    
    Args:
        code: Código del arquetipo
        
    Returns:
        Lista de nombres de campos específicos
    """
    arquetipo = ARQUETIPOS.get(code)
    if arquetipo:
        return arquetipo.get("campos_especificos", [])
    return []


def get_tone(code: str) -> str:
    """
    Obtiene el tono recomendado para un arquetipo.
    
    Args:
        code: Código del arquetipo
        
    Returns:
        Descripción del tono
    """
    arquetipo = ARQUETIPOS.get(code)
    if arquetipo:
        return arquetipo.get("tone", "")
    return ""


def get_keywords(code: str) -> List[str]:
    """
    Obtiene las keywords asociadas a un arquetipo.
    
    Args:
        code: Código del arquetipo
        
    Returns:
        Lista de keywords del arquetipo
    """
    arquetipo = ARQUETIPOS.get(code)
    if arquetipo:
        return arquetipo.get("keywords", [])
    return []


# ============================================================================
# FUNCIONES DE UTILIDAD
# ============================================================================

def get_all_arquetipo_codes() -> List[str]:
    """
    Obtiene lista de todos los códigos de arquetipos.
    
    Returns:
        Lista ordenada de códigos
    """
    return sorted(ARQUETIPOS.keys())


def get_arquetipos_by_category(category_keywords: List[str]) -> List[Dict[str, Any]]:
    """
    Filtra arquetipos que contengan ciertas keywords.
    
    Args:
        category_keywords: Lista de keywords para filtrar
        
    Returns:
        Lista de arquetipos que coinciden
    """
    results = []
    category_lower = [kw.lower() for kw in category_keywords]
    
    for code, data in ARQUETIPOS.items():
        arquetipos_keywords = [kw.lower() for kw in data.get("keywords", [])]
        name_lower = data.get("name", "").lower()
        
        # Buscar coincidencias
        if any(cat_kw in name_lower or cat_kw in arquetipos_keywords 
               for cat_kw in category_lower):
            results.append(data)
    
    return results


def format_arquetipo_for_prompt(code: str) -> str:
    """
    Formatea la información de un arquetipo para incluir en prompts.
    
    Args:
        code: Código del arquetipo
        
    Returns:
        String formateado con información del arquetipo
    """
    arquetipo = ARQUETIPOS.get(code)
    if not arquetipo:
        return f"Arquetipo {code} no encontrado."
    
    lines = [
        f"**Arquetipo**: {arquetipo['name']} ({code})",
        f"**Descripción**: {arquetipo.get('description', '')}",
        f"**Tono**: {arquetipo.get('tone', '')}",
        f"**Longitud objetivo**: {arquetipo.get('default_length', DEFAULT_CONTENT_LENGTH)} palabras",
        "",
        "**Estructura recomendada**:"
    ]
    
    for i, section in enumerate(arquetipo.get("structure", []), 1):
        lines.append(f"  {i}. {section}")
    
    if arquetipo.get("visual_elements"):
        lines.append("")
        lines.append(f"**Elementos visuales**: {', '.join(arquetipo['visual_elements'])}")
    
    return "\n".join(lines)


def validate_arquetipo_code(code: str) -> bool:
    """
    Valida que un código de arquetipo sea válido.
    
    Args:
        code: Código a validar
        
    Returns:
        True si es válido
    """
    return code in ARQUETIPOS


def get_arquetipo_summary(code: str) -> Dict[str, Any]:
    """
    Obtiene un resumen compacto de un arquetipo.
    
    Args:
        code: Código del arquetipo
        
    Returns:
        Dict con resumen del arquetipo
    """
    arquetipo = ARQUETIPOS.get(code)
    if not arquetipo:
        return {"error": f"Arquetipo {code} no encontrado"}
    
    return {
        "code": code,
        "name": arquetipo["name"],
        "tone": arquetipo.get("tone", ""),
        "default_length": arquetipo.get("default_length", DEFAULT_CONTENT_LENGTH),
        "min_length": arquetipo.get("min_length", DEFAULT_MIN_LENGTH),
        "max_length": arquetipo.get("max_length", DEFAULT_MAX_LENGTH),
        "num_sections": len(arquetipo.get("structure", [])),
        "num_questions": len(arquetipo.get("guiding_questions", [])),
        "visual_elements": arquetipo.get("visual_elements", []),
    }


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    # Versión
    '__version__',
    
    # Constantes
    'DEFAULT_MIN_LENGTH',
    'DEFAULT_MAX_LENGTH', 
    'DEFAULT_CONTENT_LENGTH',
    
    # Datos principales
    'ARQUETIPOS',
    
    # Funciones de acceso
    'get_arquetipo',
    'get_arquetipo_names',
    'get_arquetipo_by_name',
    'get_guiding_questions',
    'get_structure',
    'get_default_length',
    'get_length_range',
    'get_visual_elements',
    'get_campos_especificos',
    'get_tone',
    'get_keywords',
    
    # Funciones de utilidad
    'get_all_arquetipo_codes',
    'get_arquetipos_by_category',
    'format_arquetipo_for_prompt',
    'validate_arquetipo_code',
    'get_arquetipo_summary',
]
