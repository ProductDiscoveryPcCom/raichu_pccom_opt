# -*- coding: utf-8 -*-
"""
Arquetipos de Contenido - PcComponentes Content Generator
Versión 4.4.0

Define los 34 arquetipos de contenido SEO para PcComponentes.
Cada arquetipo incluye preguntas guía derivadas del brief oficial.

Autor: PcComponentes - Product Discovery & Content
Actualizado: 2025
"""

from typing import Dict, List, Optional, Any

__version__ = "4.4.0"

# ============================================================================
# DEFINICIÓN DE ARQUETIPOS (34 TIPOS)
# Basado en: 2025_PcComponentes_Arquetipos_Contenidos_Placeholders
# ============================================================================

ARQUETIPOS: Dict[str, Dict[str, Any]] = {
    
    # -------------------------------------------------------------------------
    # ARQ-1: Review / Análisis de producto
    # -------------------------------------------------------------------------
    "ARQ-1": {
        "code": "ARQ-1",
        "name": "Review / Análisis de producto",
        "description": "Evaluación profunda de un modelo específico con veredicto de compra basado en uso real",
        "default_length": 1500,
        "min_length": 1000,
        "max_length": 2500,
        "tone": "experto y honesto",
        "structure": ["intro_diferenciador", "fortalezas", "limitaciones", "uso_30_dias", "precio_historico", "veredicto", "alternativas"],
        "keywords_density": 0.02,
        "internal_links_min": 3,
        "internal_links_max": 10,
        "guiding_questions": [
            "¿Cuál es el diferenciador clave frente a la competencia directa?",
            "Indica 3 fortalezas MEDIBLES del producto (fps, dB, horas batería, temperaturas, etc.)",
            "Indica 2 limitaciones REALES con evidencia concreta",
            "¿Cuántos días llevas usando el producto? ¿Hay algo que notes 'después de 30 días'?",
            "¿Cuál es el precio actual vs el mínimo histórico? ¿Se espera bajada próximamente?",
            "Define 3 perfiles de 'es ideal si...' y 2 de 'considera otras opciones si...'",
            "¿Qué 2 alternativas del catálogo mencionarías y por qué característica/precio?"
        ]
    },
    
    # -------------------------------------------------------------------------
    # ARQ-2: Comparativa A vs B
    # -------------------------------------------------------------------------
    "ARQ-2": {
        "code": "ARQ-2",
        "name": "Comparativa A vs B",
        "description": "Enfrentamiento directo entre dos modelos para decisión binaria de compra",
        "default_length": 1800,
        "min_length": 1200,
        "max_length": 3000,
        "tone": "analítico y objetivo",
        "structure": ["intro", "experiencia_uso", "casos_uso", "precio_rendimiento", "veredicto_por_perfil"],
        "keywords_density": 0.018,
        "internal_links_min": 6,
        "internal_links_max": 15,
        "guiding_questions": [
            "¿Cuáles son los dos modelos exactos a comparar?",
            "Más allá de specs: ¿cómo es el ruido real, temps bajo carga, autonomía en uso real?",
            "Define casos de uso concretos (gaming 1080p, oficina silenciosa, edición 4K) y quién gana en cada uno",
            "¿Cuál es la diferencia de precio? Cuantifica: 'X fps/€ más por Y€ extra'",
            "¿Cómo ha evolucionado el precio de ambos en los últimos 90 días?",
            "¿Cuál es el punto de inflexión donde merece pagar más por uno u otro?",
            "¿Para qué perfil de usuario recomendarías cada uno?"
        ]
    },
    
    # -------------------------------------------------------------------------
    # ARQ-3: Comparativa multimodelo (3-5 productos)
    # -------------------------------------------------------------------------
    "ARQ-3": {
        "code": "ARQ-3",
        "name": "Comparativa multimodelo",
        "description": "Análisis paralelo de 3-5 candidatos para identificar mejor opción por criterio",
        "default_length": 2200,
        "min_length": 1500,
        "max_length": 3500,
        "tone": "exhaustivo y sistemático",
        "structure": ["intro", "rangos_precio", "matriz_decision", "badges", "timeline_lanzamientos", "veredicto"],
        "keywords_density": 0.015,
        "internal_links_min": 10,
        "internal_links_max": 25,
        "guiding_questions": [
            "Lista los 3-5 productos exactos a comparar",
            "¿Cómo los agrupas por rango de precio? (<500€, 500-800€, >800€)",
            "Define los 5 criterios de tu matriz de decisión y su peso relativo (%)",
            "¿Cuál merece badge 'mejor global'? ¿Con qué métrica lo justificas?",
            "¿Cuál es 'mejor calidad/precio'? Indica €/fps o €/hora batería",
            "Si hay empate entre dos, ¿cuál es el factor de desempate? (disponibilidad, garantía, ecosistema)",
            "¿Hay lanzamientos próximos que podrían cambiar esta recomendación?"
        ]
    },
    
    # -------------------------------------------------------------------------
    # ARQ-4: Roundup / Mejores X
    # -------------------------------------------------------------------------
    "ARQ-4": {
        "code": "ARQ-4",
        "name": "Roundup / Mejores X",
        "description": "Ranking curado y actualizable de productos top por categoría con filtros dinámicos",
        "default_length": 2000,
        "min_length": 1500,
        "max_length": 3500,
        "tone": "dinámico y actualizado",
        "structure": ["intro_metodologia", "ranking", "filtro_rapido", "recomendacion_editor", "checklist_60seg"],
        "keywords_density": 0.015,
        "internal_links_min": 8,
        "internal_links_max": 20,
        "guiding_questions": [
            "¿Qué categoría exacta cubre este ranking?",
            "Define tu metodología: ¿qué peso das a precio, rendimiento, garantía, disponibilidad?",
            "¿Qué filtros rápidos ofreces? (presupuesto, uso, marca)",
            "¿Cuál es TU recomendación personal como editor y por qué?",
            "¿Hay algún modelo de 2023 o anterior que siga siendo el mejor? Justifica con datos",
            "¿Cada cuánto te comprometes a actualizar este ranking?",
            "Crea un checklist de 'elige en 60 segundos' para el lector"
        ]
    },
    
    # -------------------------------------------------------------------------
    # ARQ-5: Guía / How-to
    # -------------------------------------------------------------------------
    "ARQ-5": {
        "code": "ARQ-5",
        "name": "Guía / How-to",
        "description": "Tutorial paso a paso para tarea técnica con verificación de éxito y troubleshooting",
        "default_length": 1400,
        "min_length": 1000,
        "max_length": 2200,
        "tone": "didáctico y práctico",
        "structure": ["intro_requisitos", "pasos", "checkpoints", "errores_comunes", "verificacion", "rollback"],
        "keywords_density": 0.02,
        "internal_links_min": 4,
        "internal_links_max": 12,
        "guiding_questions": [
            "¿Qué tarea específica enseña este tutorial?",
            "Lista herramientas, prerequisitos y tiempo estimado",
            "¿Hay riesgos? (pérdida de garantía, datos, etc.) Indícalos claramente",
            "¿Cuáles son los 3 errores más comunes y su fix rápido?",
            "Define checkpoints: 'si no ves X, no continúes'",
            "¿Hay ruta básica (GUI) y avanzada (terminal)?",
            "¿Cómo verifica el usuario que todo salió bien? ¿Qué hacer si falla (rollback)?",
            "¿Qué productos del catálogo simplifican este proceso?"
        ]
    },
    
    # -------------------------------------------------------------------------
    # ARQ-6: Troubleshooting / Solución de problemas
    # -------------------------------------------------------------------------
    "ARQ-6": {
        "code": "ARQ-6",
        "name": "Troubleshooting",
        "description": "Árbol de decisión diagnóstico para resolver problema específico preservando garantía",
        "default_length": 1300,
        "min_length": 900,
        "max_length": 2000,
        "tone": "útil y solucionador",
        "structure": ["sintomas", "flowchart_diagnostico", "soluciones_ordenadas", "garantia", "cuando_rma"],
        "keywords_density": 0.02,
        "internal_links_min": 4,
        "internal_links_max": 12,
        "guiding_questions": [
            "¿Cuál es el problema/síntoma principal? ¿Con qué frecuencia ocurre?",
            "Ordena las soluciones por probabilidad de éxito Y coste (gratis > barato > RMA)",
            "¿Qué acciones invalidan la garantía? Márcalas claramente",
            "¿Puedes ofrecer ruta corta (5 min, usuario básico) vs profunda (30 min, técnico)?",
            "¿Cuándo debe el usuario 'tirar la toalla' y pedir RMA?",
            "Si la solución requiere compra, ¿qué productos en stock con envío 24h recomiendas?"
        ]
    },
    
    # -------------------------------------------------------------------------
    # ARQ-7: Noticia / Explicador
    # -------------------------------------------------------------------------
    "ARQ-7": {
        "code": "ARQ-7",
        "name": "Noticia / Explicador",
        "description": "Traducción de anuncio técnico a impacto real en decisión de compra",
        "default_length": 1000,
        "min_length": 600,
        "max_length": 1500,
        "tone": "informativo y contextual",
        "structure": ["lead_impacto", "que_se_anuncio", "por_que_importa", "timeline", "acciones"],
        "keywords_density": 0.02,
        "internal_links_min": 3,
        "internal_links_max": 8,
        "guiding_questions": [
            "¿Qué se anunció exactamente? ¿Es confirmado, rumor o leak?",
            "En 1 frase: ¿qué cambia para el comprador vs ayer?",
            "Traduce specs a beneficio tangible (ej: '40% más ray tracing = 60fps estables en Cyberpunk')",
            "¿Cuándo llega a tienda? ¿Precio esperado? ¿Disponibilidad real?",
            "Define 3 acciones: 'espera si...', 'compra ya si...', 'ignora si...'",
            "¿Qué productos actuales del catálogo bajan de precio por este anuncio?"
        ]
    },
    
    # -------------------------------------------------------------------------
    # ARQ-8: Guía de compra por perfil
    # -------------------------------------------------------------------------
    "ARQ-8": {
        "code": "ARQ-8",
        "name": "Guía de compra por perfil",
        "description": "Configuraciones completas recomendadas según tipo de usuario con alternativas",
        "default_length": 1800,
        "min_length": 1200,
        "max_length": 2800,
        "tone": "consultivo y personalizado",
        "structure": ["intro", "perfiles", "builds_por_perfil", "dilemas_frecuentes", "alternativas_presupuesto"],
        "keywords_density": 0.018,
        "internal_links_min": 10,
        "internal_links_max": 25,
        "guiding_questions": [
            "Define 5-6 perfiles con nombre memorable (Gamer casual, Creador de contenido, Teletrabajador, Estudiante ingeniería...)",
            "Para cada perfil: ¿presupuesto típico?",
            "Para cada perfil: ¿requisitos mínimos vs recomendados?",
            "Para cada perfil: ¿qué software usará principalmente?",
            "¿Cuál es el 'dilema frecuente' de cada perfil? (ej: ¿16 vs 32GB RAM?) Da respuesta pragmática",
            "¿Qué alternativa ofreces con +20% presupuesto y qué mejora?",
            "¿Hasta qué fecha son válidos los precios mostrados?"
        ]
    },
    
    # -------------------------------------------------------------------------
    # ARQ-9: Build completa / Configuración PC
    # -------------------------------------------------------------------------
    "ARQ-9": {
        "code": "ARQ-9",
        "name": "Build completa / Config PC",
        "description": "Lista de componentes optimizada con justificación técnica y plan de montaje",
        "default_length": 1600,
        "min_length": 1100,
        "max_length": 2400,
        "tone": "técnico y justificado",
        "structure": ["objetivo", "tabla_componentes", "compatibilidad", "bottlenecks", "plan_b", "upgrades"],
        "keywords_density": 0.02,
        "internal_links_min": 8,
        "internal_links_max": 18,
        "guiding_questions": [
            "¿Objetivo claro? (1440p 144Hz, workstation silenciosa, mini-ITX portable...)",
            "¿Presupuesto máximo?",
            "Para cada componente: ¿por qué ESA elección específica?",
            "¿Validaste compatibilidad física? (GPU clearance, RAM height)",
            "¿Validaste compatibilidad eléctrica? (PSU watts con 20% margen)",
            "¿Identificaste cuellos de botella? ¿Qué % de pérdida?",
            "¿Plan B si hay rotura de stock? ¿Variante con +10%/-10% presupuesto?",
            "¿Rendimiento esperado en 5 juegos/apps populares?",
            "¿Roadmap de upgrades a 1 y 2 años?"
        ]
    },
    
    # -------------------------------------------------------------------------
    # ARQ-10: Matrices de compatibilidad / Ecosistema
    # -------------------------------------------------------------------------
    "ARQ-10": {
        "code": "ARQ-10",
        "name": "Matrices compatibilidad",
        "description": "Validación rápida de interoperabilidad entre componentes con alternativas seguras",
        "default_length": 1200,
        "min_length": 800,
        "max_length": 1800,
        "tone": "preciso y técnico",
        "structure": ["intro", "tabla_compatibilidad", "verificacion_2pasos", "limitaciones_ocultas", "combinacion_segura"],
        "keywords_density": 0.018,
        "internal_links_min": 6,
        "internal_links_max": 15,
        "guiding_questions": [
            "¿Qué componentes/productos se validan?",
            "¿Cómo verificar en 2 pasos? (modelo exacto + versión firmware)",
            "Lista incompatibilidades conocidas con ❌ y parciales con ⚠️",
            "¿Limitaciones no obvias? (lanes compartidos, USB-C sin video, RAM speed cap)",
            "¿Cuál es la combinación 'a prueba de fallos' del catálogo?",
            "¿Qué cosas 'el fabricante no dice' pero son quirks reales?"
        ]
    },
    
    # -------------------------------------------------------------------------
    # ARQ-11: Benchmarks y pruebas
    # -------------------------------------------------------------------------
    "ARQ-11": {
        "code": "ARQ-11",
        "name": "Benchmarks y pruebas",
        "description": "Resultados de rendimiento traducidos a decisiones de compra con metodología transparente",
        "default_length": 1400,
        "min_length": 1000,
        "max_length": 2200,
        "tone": "técnico y transparente",
        "structure": ["metodologia", "resultados_casos_uso", "consumo_ruido", "precio_rendimiento", "punto_dulce"],
        "keywords_density": 0.02,
        "internal_links_min": 5,
        "internal_links_max": 12,
        "guiding_questions": [
            "Declara metodología completa: hardware de prueba, drivers, versiones, ambiente",
            "¿Resultados en casos de uso REALES, no solo sintéticos?",
            "¿Consumo real vs TDP? ¿Ruido vs temps?",
            "Diferencias <5% márcalas como 'imperceptibles en uso real'",
            "¿Cuál es el punto dulce de precio/rendimiento?",
            "¿Es mejora generacional REAL o solo marketing?"
        ]
    },
    
    # -------------------------------------------------------------------------
    # ARQ-12: Precio & Disponibilidad (Price Watch)
    # -------------------------------------------------------------------------
    "ARQ-12": {
        "code": "ARQ-12",
        "name": "Price Watch",
        "description": "Monitorización de precio actual con contexto histórico y predicción de tendencia",
        "default_length": 800,
        "min_length": 500,
        "max_length": 1200,
        "tone": "informativo y actualizado",
        "structure": ["precio_actual", "historico_6m", "prediccion_4sem", "precio_objetivo", "alternativas_stock"],
        "keywords_density": 0.02,
        "internal_links_min": 3,
        "internal_links_max": 8,
        "guiding_questions": [
            "¿Precio actual vs PVP vs mínimo histórico vs media 90 días?",
            "¿Es oferta real o precio ancla inflado?",
            "¿Evolución últimos 6 meses con eventos clave (lanzamientos, Black Friday)?",
            "¿Predicción próximas 4 semanas?",
            "¿'Precio objetivo' de compra recomendada?",
            "Si hay rotura de stock: ¿estimación reposición? ¿2 alternativas con trade-offs?"
        ]
    },
    
    # -------------------------------------------------------------------------
    # ARQ-13: Ofertas / Chollos curados
    # -------------------------------------------------------------------------
    "ARQ-13": {
        "code": "ARQ-13",
        "name": "Ofertas / Chollos",
        "description": "Selección verificada de descuentos reales con análisis de valor y urgencia",
        "default_length": 1000,
        "min_length": 600,
        "max_length": 1500,
        "tone": "directo y urgente",
        "structure": ["intro", "ofertas_verificadas", "factor_urgencia", "para_quien_si_no"],
        "keywords_density": 0.02,
        "internal_links_min": 5,
        "internal_links_max": 12,
        "guiding_questions": [
            "¿Verificaste que es mínimo 15% dto REAL sobre precio habitual (no PVP inflado)?",
            "Para cada oferta: precio anterior, actual, mínimo histórico",
            "¿Fecha/hora fin? ¿Stock estimado?",
            "¿Para quién SÍ conviene? ¿Para quién NO?",
            "¿'Factor urgencia' del 1-10?",
            "¿Esta oferta volverá antes del próximo Black Friday? Marca con 🔥 si no"
        ]
    },
    
    # -------------------------------------------------------------------------
    # ARQ-14: Stock Watch / Reabastecimiento
    # -------------------------------------------------------------------------
    "ARQ-14": {
        "code": "ARQ-14",
        "name": "Stock Watch",
        "description": "Seguimiento de disponibilidad con predicciones y alternativas equivalentes",
        "default_length": 800,
        "min_length": 500,
        "max_length": 1200,
        "tone": "informativo y práctico",
        "structure": ["estado_actual", "historial_roturas", "prediccion_restock", "alternativas", "scalping"],
        "keywords_density": 0.02,
        "internal_links_min": 3,
        "internal_links_max": 8,
        "guiding_questions": [
            "¿Estado actual? (en stock, pocas unidades, agotado, próximamente)",
            "¿Historial de roturas y tiempo medio de reposición?",
            "¿Hay scalping? Precio retail vs reventa. ¿Precio máximo aceptable?",
            "¿3 alternativas en stock ordenadas por similitud? Explica qué se gana/pierde",
            "¿Es paper launch o hay stock real?"
        ]
    },
    
    # -------------------------------------------------------------------------
    # ARQ-15: Accesorios y complementos esenciales
    # -------------------------------------------------------------------------
    "ARQ-15": {
        "code": "ARQ-15",
        "name": "Accesorios esenciales",
        "description": "Ecosistema de productos compatibles diferenciando imprescindible vs nice-to-have",
        "default_length": 1200,
        "min_length": 800,
        "max_length": 1800,
        "tone": "práctico y preventivo",
        "structure": ["kit_dia1", "imprescindible", "recomendado", "opcional", "matriz_uso", "bundles"],
        "keywords_density": 0.02,
        "internal_links_min": 8,
        "internal_links_max": 20,
        "guiding_questions": [
            "¿Para qué producto principal son estos accesorios?",
            "¿'Kit día 1' con lo absolutamente necesario para funcionar?",
            "Separa en 3 niveles: imprescindible / recomendado / opcional",
            "¿Validaste compatibilidad técnica? (watts cargador, versión HDMI, medidas funda)",
            "¿Algún accesorio barato compromete garantía o seguridad?",
            "¿Precio total del setup completo?",
            "¿Hay bundles que ahorren vs compra individual?"
        ]
    },
    
    # -------------------------------------------------------------------------
    # ARQ-16: Onboarding / Puesta a punto
    # -------------------------------------------------------------------------
    "ARQ-16": {
        "code": "ARQ-16",
        "name": "Onboarding / Puesta a punto",
        "description": "Configuración inicial optimizada para máximo rendimiento desde el día 1",
        "default_length": 1300,
        "min_length": 900,
        "max_length": 2000,
        "tone": "metódico y claro",
        "structure": ["checklist_7pasos", "tiempos", "hazlo_ahora_vs_despues", "tests_verificacion", "productos"],
        "keywords_density": 0.02,
        "internal_links_min": 4,
        "internal_links_max": 10,
        "guiding_questions": [
            "¿Para qué producto/dispositivo es este onboarding?",
            "Checklist de 7 pasos ordenados: actualización, config crítica, optimización, personalización, backup, verificación, mantenimiento",
            "¿Tiempo estimado por paso?",
            "¿Qué es 'hazlo ahora' vs 'puedes hacerlo después'?",
            "¿Tests de verificación? (benchmark antes/después, temps, estabilidad)",
            "¿Opciones que parecen buena idea pero NO lo son?",
            "¿Productos del catálogo que automatizan el proceso?"
        ]
    },
    
    # -------------------------------------------------------------------------
    # ARQ-17: Mantenimiento y cuidado
    # -------------------------------------------------------------------------
    "ARQ-17": {
        "code": "ARQ-17",
        "name": "Mantenimiento y cuidado",
        "description": "Calendario de mantenimiento preventivo para maximizar vida útil y rendimiento",
        "default_length": 1100,
        "min_length": 700,
        "max_length": 1600,
        "tone": "preventivo y práctico",
        "structure": ["calendario", "herramientas", "evidencia_antes_despues", "usuario_vs_tecnico", "productos"],
        "keywords_density": 0.02,
        "internal_links_min": 4,
        "internal_links_max": 10,
        "guiding_questions": [
            "¿Para qué producto/dispositivo es este mantenimiento?",
            "Calendario: diario (5 seg), mensual (5 min), trimestral (20 min), anual (1 hora)",
            "¿Herramientas y materiales ESPECÍFICOS necesarios?",
            "¿Evidencia antes/después que justifique el esfuerzo? (temps, ruido, fps)",
            "¿Qué mantenimiento puede hacer el usuario vs servicio técnico?",
            "¿Síntomas de que necesita mantenimiento YA?",
            "¿'Lo que mata tu equipo sin que lo sepas'?"
        ]
    },
    
    # -------------------------------------------------------------------------
    # ARQ-18: Seguridad y privacidad
    # -------------------------------------------------------------------------
    "ARQ-18": {
        "code": "ARQ-18",
        "name": "Seguridad y privacidad",
        "description": "Alertas de vulnerabilidades con guías de mitigación y verificación de parches",
        "default_length": 1000,
        "min_length": 600,
        "max_length": 1500,
        "tone": "urgente pero claro",
        "structure": ["vulnerabilidad_humana", "severidad", "solucion_oficial", "mitigacion", "verificacion"],
        "keywords_density": 0.02,
        "internal_links_min": 3,
        "internal_links_max": 8,
        "guiding_questions": [
            "Explica la vulnerabilidad en términos humanos: ¿qué puede pasar?",
            "¿Probabilidad? ¿Severidad? ¿Quién está en riesgo?",
            "¿Solución oficial (parche)? Link directo y verificación post-instalación",
            "Si no hay parche: ¿mitigación temporal con trade-offs claros?",
            "¿Productos del catálogo que NO son vulnerables o incluyen protección?"
        ]
    },
    
    # -------------------------------------------------------------------------
    # ARQ-19: Mitos vs realidad
    # -------------------------------------------------------------------------
    "ARQ-19": {
        "code": "ARQ-19",
        "name": "Mitos vs realidad",
        "description": "Fact-checking de creencias populares que frenan decisiones de compra",
        "default_length": 1000,
        "min_length": 600,
        "max_length": 1500,
        "tone": "desmitificador y equilibrado",
        "structure": ["mito_textual", "evidencia", "por_que_persiste", "matices", "regla_practica"],
        "keywords_density": 0.02,
        "internal_links_min": 3,
        "internal_links_max": 8,
        "guiding_questions": [
            "¿Cuál es el mito EXACTAMENTE como la gente lo dice?",
            "¿Evidencia medible que lo confirma o desmiente? (test, estudio, spec oficial)",
            "¿Por qué persiste? (marketing, época donde era cierto, mala interpretación)",
            "¿Matices? 'Cierto si... pero falso si...'",
            "¿Regla de decisión práctica final para el comprador?"
        ]
    },
    
    # -------------------------------------------------------------------------
    # ARQ-20: Sostenibilidad y consumo energético
    # -------------------------------------------------------------------------
    "ARQ-20": {
        "code": "ARQ-20",
        "name": "Sostenibilidad y consumo",
        "description": "Optimización de consumo sin sacrificar rendimiento con cálculo de ahorro real",
        "default_length": 1100,
        "min_length": 700,
        "max_length": 1600,
        "tone": "práctico y honesto",
        "structure": ["consumo_real", "escenarios", "optimizaciones_3niveles", "roi", "productos_eficientes"],
        "keywords_density": 0.02,
        "internal_links_min": 4,
        "internal_links_max": 10,
        "guiding_questions": [
            "¿Consumo REAL (no TDP) traducido a €/año con tarifa actual?",
            "¿Escenarios? (idle, navegación, gaming, renderizado)",
            "Optimización fácil (0€, 5min, -10%), media (50€, 1h, -25%), avanzada (200€+, -40%)",
            "¿ROI: cuándo recuperas la inversión en ahorro?",
            "Si el ahorro es <5€/año, ¿lo dices claramente sin greenwashing?"
        ]
    },
    
    # -------------------------------------------------------------------------
    # ARQ-21: Reacondicionados / Segunda mano
    # -------------------------------------------------------------------------
    "ARQ-21": {
        "code": "ARQ-21",
        "name": "Reacondicionados / Segunda mano",
        "description": "Guía de compra de productos usados con evaluación de riesgo/beneficio",
        "default_length": 1200,
        "min_length": 800,
        "max_length": 1800,
        "tone": "cauteloso y práctico",
        "structure": ["grades_fotos", "checklist_10puntos", "que_si_que_no", "precio_maximo", "sanitizacion"],
        "keywords_density": 0.02,
        "internal_links_min": 5,
        "internal_links_max": 12,
        "guiding_questions": [
            "Explica grades (A/B/C) con fotos REALES de cada condición",
            "Checklist de 10 puntos de inspección con red flags (ciclos batería >500, píxeles muertos, coil whine)",
            "¿Ahorro real vs nuevo considerando garantía reducida?",
            "¿Qué productos SÍ conviene usados? (GPUs minería post-limpieza)",
            "¿Qué productos NO conviene usados? (SSDs, fuentes)",
            "¿'Precio máximo recomendado' como % del nuevo?"
        ]
    },
    
    # -------------------------------------------------------------------------
    # ARQ-22: Roadmap / Calendario de actualizaciones
    # -------------------------------------------------------------------------
    "ARQ-22": {
        "code": "ARQ-22",
        "name": "Roadmap / Calendario",
        "description": "Timeline de actualizaciones confirmadas con impacto en decisiones de compra",
        "default_length": 1000,
        "min_length": 600,
        "max_length": 1500,
        "tone": "informativo y predictivo",
        "structure": ["confirmado_fecha", "confirmado_sin_fecha", "rumor", "impacto", "compra_vs_espera"],
        "keywords_density": 0.02,
        "internal_links_min": 4,
        "internal_links_max": 10,
        "guiding_questions": [
            "Separa: confirmado con fecha / confirmado sin fecha / rumor creíble / especulación",
            "Para cada actualización: ¿qué cambia? ¿Quién se beneficia? ¿Riesgos early adoption?",
            "¿Qué hitos alteran valor de productos actuales?",
            "¿'Compra ya' vs 'espera 2 meses'? Justificación económica",
            "¿Historial de cumplimiento de roadmaps anteriores del fabricante?"
        ]
    },
    
    # -------------------------------------------------------------------------
    # ARQ-23: Casos de uso profesional
    # -------------------------------------------------------------------------
    "ARQ-23": {
        "code": "ARQ-23",
        "name": "Casos uso profesional",
        "description": "Hardware optimizado para software/workflow específico con ROI calculado",
        "default_length": 1400,
        "min_length": 1000,
        "max_length": 2200,
        "tone": "profesional y orientado a ROI",
        "structure": ["software_version", "requisitos_3niveles", "benchmarks_reales", "roi", "config_ejemplo"],
        "keywords_density": 0.02,
        "internal_links_min": 6,
        "internal_links_max": 15,
        "guiding_questions": [
            "¿Software principal y versión específica? (Premiere Pro 2024, AutoCAD 2025, TensorFlow 2.x)",
            "¿Requisitos mínimos vs recomendados vs óptimos?",
            "¿Benchmarks en el software REAL, no sintéticos?",
            "¿ROI calculado? (tiempo ahorrado × tarifa hora = retorno inversión)",
            "¿Qué hardware NO mejora este workflow? (evitar sobregasto)",
            "¿Certificaciones profesionales (ISV, drivers estables)?",
            "¿Config ejemplo con precio y alternativa -30% presupuesto?"
        ]
    },
    
    # -------------------------------------------------------------------------
    # ARQ-24: Playbooks por escenario
    # -------------------------------------------------------------------------
    "ARQ-24": {
        "code": "ARQ-24",
        "name": "Playbooks por escenario",
        "description": "Solución completa empaquetada para contexto específico con todo incluido",
        "default_length": 1500,
        "min_length": 1000,
        "max_length": 2300,
        "tone": "completo y contextual",
        "structure": ["contexto_detallado", "kit_completo", "setup_orden", "problemas_prevencion", "versiones"],
        "keywords_density": 0.02,
        "internal_links_min": 8,
        "internal_links_max": 18,
        "guiding_questions": [
            "¿Contexto detallado? (espacio disponible, presupuesto, limitaciones ruido/portabilidad)",
            "¿Objetivo principal?",
            "¿Kit completo con TODO necesario, nada más? Justifica cada elemento",
            "¿Setup en orden correcto con tiempo estimado?",
            "¿3 problemas típicos del escenario y su prevención?",
            "¿Versión premium (+30%) y budget (-30%)?",
            "¿Coste total de propiedad a 2 años?",
            "¿Fotos de setups REALES, no renders?"
        ]
    },
    
    # -------------------------------------------------------------------------
    # ARQ-25: Listados / Índices exhaustivos
    # -------------------------------------------------------------------------
    "ARQ-25": {
        "code": "ARQ-25",
        "name": "Listados / Índices",
        "description": "Recopilación completa y actualizable para consulta rápida sin opinión",
        "default_length": 1000,
        "min_length": 600,
        "max_length": 1800,
        "tone": "neutro y exhaustivo",
        "structure": ["alcance", "estructura_consistente", "filtros", "actualizacion", "descargable"],
        "keywords_density": 0.015,
        "internal_links_min": 10,
        "internal_links_max": 30,
        "guiding_questions": [
            "¿Alcance preciso? (solo anuncios oficiales, ventana temporal, región)",
            "¿Estructura consistente de cada entrada? (título, fabricante, categoría, fecha, precio, fuente)",
            "¿Sistema de filtros y búsqueda?",
            "¿Compromiso de actualización? (diario para eventos, semanal general)",
            "¿Versión descargable (CSV/PDF)?",
            "¿Evitas CUALQUIER valoración? Solo datos verificables"
        ]
    },
    
    # -------------------------------------------------------------------------
    # ARQ-26: Calculadoras / Herramientas interactivas
    # -------------------------------------------------------------------------
    "ARQ-26": {
        "code": "ARQ-26",
        "name": "Calculadoras / Herramientas",
        "description": "Utilidades web funcionales que dimensionan necesidades antes de comprar",
        "default_length": 800,
        "min_length": 500,
        "max_length": 1200,
        "tone": "funcional y explicativo",
        "structure": ["inputs", "calculo_visible", "resultado_3niveles", "productos_sugeridos", "compartir"],
        "keywords_density": 0.02,
        "internal_links_min": 5,
        "internal_links_max": 12,
        "guiding_questions": [
            "¿Qué calcula esta herramienta?",
            "¿Inputs claros con valores por defecto sensatos y tooltips?",
            "¿Fórmula visible?",
            "¿Margen de seguridad 20%? Explica por qué",
            "¿Resultado incluye: mínimo, recomendado, future-proof?",
            "¿3-5 productos del catálogo que cumplen el requisito?",
            "¿Casos ejemplo para novatos? ¿Compartir/exportar?"
        ]
    },
    
    # -------------------------------------------------------------------------
    # ARQ-27: Unboxing / Primera impresión
    # -------------------------------------------------------------------------
    "ARQ-27": {
        "code": "ARQ-27",
        "name": "Unboxing / Primera impresión",
        "description": "Experiencia de desempaquetado y primeras 24 horas con el producto",
        "default_length": 1000,
        "min_length": 600,
        "max_length": 1500,
        "tone": "honesto y sensorial",
        "structure": ["contenido_caja", "setup_fricciones", "impresiones_sensoriales", "sorpresas_decepciones", "accesorios_semana1"],
        "keywords_density": 0.02,
        "internal_links_min": 4,
        "internal_links_max": 10,
        "guiding_questions": [
            "¿Qué viene en la caja vs qué necesitas comprar aparte? (fotos de todo)",
            "¿Setup cronometrado con fricciones honestas? ('cable muy corto', 'manual solo en inglés')",
            "¿Impresiones sensoriales? (peso real vs esperado, calidad materiales, ruido reposo)",
            "¿Test rápido de función principal sin config avanzada?",
            "¿3 cosas que sorprendieron positivamente tras 24h?",
            "¿2 cosas que decepcionaron?",
            "¿Accesorios que necesitarás en primera semana?",
            "¿Prometes follow-up a 30 días?"
        ]
    },
    
    # -------------------------------------------------------------------------
    # ARQ-28: Upgrade paths / Rutas de actualización
    # -------------------------------------------------------------------------
    "ARQ-28": {
        "code": "ARQ-28",
        "name": "Upgrade paths",
        "description": "Secuencia optimizada de mejoras para hardware existente maximizando valor",
        "default_length": 1400,
        "min_length": 1000,
        "max_length": 2200,
        "tone": "estratégico y progresivo",
        "structure": ["configs_tipicas", "objetivo", "upgrades_por_presupuesto", "dependencias", "punto_inflexion"],
        "keywords_density": 0.02,
        "internal_links_min": 8,
        "internal_links_max": 18,
        "guiding_questions": [
            "¿Configs típicas de partida? (PC 2020 gama media, laptop 2022 básico...)",
            "¿Objetivo concreto? (+50% fps, edición 4K fluida)",
            "¿3 presupuestos escalonados? (200€, 500€, 1000€)",
            "¿Orden de upgrades por ratio impacto/euro con % mejora esperada?",
            "¿Dependencias? (nueva GPU requiere fuente más potente)",
            "¿Incompatibilidades ocultas?",
            "¿Benchmarks antes/después por escalón?",
            "¿Punto de inflexión donde es mejor build nueva?"
        ]
    },
    
    # -------------------------------------------------------------------------
    # ARQ-29: "Tu primer..." / Guías para principiantes absolutos
    # -------------------------------------------------------------------------
    "ARQ-29": {
        "code": "ARQ-29",
        "name": "Tu primer... (principiantes)",
        "description": "Onboarding completo para primera compra sin conocimiento previo",
        "default_length": 1300,
        "min_length": 900,
        "max_length": 2000,
        "tone": "accesible y empático",
        "structure": ["que_es_que_no", "kit_inicio", "errores_novato", "mitos", "glosario", "roadmap_aprendizaje"],
        "keywords_density": 0.02,
        "internal_links_min": 6,
        "internal_links_max": 15,
        "guiding_questions": [
            "¿Qué ES y qué NO ES el producto? (analogías con cosas conocidas)",
            "¿5 cosas que el 90% olvida comprar la primera vez?",
            "¿3 errores de novato CAROS y cómo evitarlos con ejemplos reales?",
            "¿3 mitos que complican la decisión innecesariamente?",
            "¿Kit de inicio con presupuesto cerrado incluyendo TODO?",
            "¿Qué podrás hacer y qué NO con esta config inicial?",
            "¿Glosario visual de 10 términos que verás en todas las reviews?",
            "¿Roadmap de aprendizaje: qué aprender primero?"
        ]
    },
    
    # -------------------------------------------------------------------------
    # ARQ-30: Alertas de obsolescencia / End of Life
    # -------------------------------------------------------------------------
    "ARQ-30": {
        "code": "ARQ-30",
        "name": "Alertas EOL / Obsolescencia",
        "description": "Avisos sobre productos próximos a perder soporte con alternativas modernas",
        "default_length": 1000,
        "min_length": 600,
        "max_length": 1500,
        "tone": "preventivo y práctico",
        "structure": ["producto_eol", "impacto_fechas", "coste_mantenimiento", "alternativa", "sintomas"],
        "keywords_density": 0.02,
        "internal_links_min": 4,
        "internal_links_max": 10,
        "guiding_questions": [
            "¿Producto con EOL oficial o inferido? (GPU con 2 generaciones nuevas encima)",
            "¿Impacto real con fechas? Sin drivers (fecha), sin garantía (fecha), sin repuestos (estimado)",
            "¿Coste de mantenimiento post-EOL vs reemplazo?",
            "¿Aún conviene comprarlo con 60% dto? ¿Para quién? (servidor casero, PC secundario)",
            "¿Alternativa moderna con mejor soporte a precio similar?",
            "¿'Síntomas de que tu hardware está en EOL' aunque no sea oficial?"
        ]
    },
    
    # -------------------------------------------------------------------------
    # ARQ-31: Requisitos / ¿Me funcionará?
    # -------------------------------------------------------------------------
    "ARQ-31": {
        "code": "ARQ-31",
        "name": "Requisitos / ¿Me funcionará?",
        "description": "Análisis de requisitos de software/juegos con verificación de compatibilidad",
        "default_length": 1400,
        "min_length": 1000,
        "max_length": 2200,
        "tone": "práctico y verificable",
        "structure": ["4niveles_requisitos", "realidad_vs_publisher", "requisitos_ocultos", "equivalencias", "optimizacion"],
        "keywords_density": 0.02,
        "internal_links_min": 6,
        "internal_links_max": 15,
        "guiding_questions": [
            "¿Para qué software/juego son estos requisitos?",
            "¿4 niveles? Mínimo absoluto (abre pero injugable), mínimo jugable (30fps low), recomendado (60fps high), óptimo (144fps ultra)",
            "¿Qué significan REALMENTE los 'mínimos' del publisher?",
            "¿Requisitos ocultos? (espacio post-instalación, RAM dual channel, DirectX features)",
            "¿Tabla equivalencias para GPUs/CPUs no listadas?",
            "¿Bottlenecks típicos y solución económica?",
            "¿FPS esperados en 3 resoluciones × 3 presets?",
            "¿Trucos optimización para rozar mínimos?"
        ]
    },
    
    # -------------------------------------------------------------------------
    # ARQ-32: Drops / Lanzamientos en vivo
    # -------------------------------------------------------------------------
    "ARQ-32": {
        "code": "ARQ-32",
        "name": "Drops / Lanzamientos vivo",
        "description": "Cobertura en tiempo real de lanzamientos con disponibilidad y pricing dinámico",
        "default_length": 800,
        "min_length": 500,
        "max_length": 1200,
        "tone": "urgente y actualizado",
        "structure": ["countdown", "enlaces_tiendas", "precios_vivo", "tacticas", "alternativas_dia1"],
        "keywords_density": 0.02,
        "internal_links_min": 5,
        "internal_links_max": 12,
        "guiding_questions": [
            "¿Producto y fecha/hora exacta de apertura ventas?",
            "¿Enlaces directos a TODAS las tiendas con stock checker?",
            "¿Precio en cada retailer vs MSRP actualizado al minuto?",
            "¿Tácticas para maximizar probabilidad? (múltiples pestañas, métodos pago preparados)",
            "¿Historial drops anteriores para predecir duración stock?",
            "¿Alternativas si no consigues unidad día 1?",
            "¿Habrá post-mortem del lanzamiento?"
        ]
    },
    
    # -------------------------------------------------------------------------
    # ARQ-33: Diagnóstico / ¿Qué componente falla?
    # -------------------------------------------------------------------------
    "ARQ-33": {
        "code": "ARQ-33",
        "name": "Diagnóstico / ¿Qué falla?",
        "description": "Herramienta interactiva de diagnóstico para identificar qué pieza necesita reemplazo",
        "default_length": 1200,
        "min_length": 800,
        "max_length": 1800,
        "tone": "diagnóstico y sistemático",
        "structure": ["wizard_preguntas", "tests_usuario", "probabilidades", "verificar_antes_comprar", "reparar_vs_reemplazar"],
        "keywords_density": 0.02,
        "internal_links_min": 6,
        "internal_links_max": 15,
        "guiding_questions": [
            "¿Preguntas binarias del wizard? (¿enciende LED?, ¿suena ventilador?)",
            "¿Tests que puede ejecutar el usuario? (memtest, furmark) con interpretación",
            "Para cada síntoma: ¿% probabilidad de qué componente falla?",
            "¿Diferencia entre fallo vs mal rendimiento vs incompatibilidad?",
            "¿Videos/audio mostrando cómo suena/se ve cada tipo de fallo?",
            "¿Cómo verificar ANTES de comprar el reemplazo?",
            "¿Merece reparar vs reemplazar según antigüedad?"
        ]
    },
    
    # -------------------------------------------------------------------------
    # ARQ-34: Batalla de specs / Decodificador de marketing
    # -------------------------------------------------------------------------
    "ARQ-34": {
        "code": "ARQ-34",
        "name": "Batalla specs / Decodificador",
        "description": "Traducción de specs de marketing a rendimiento real con explicación de qué importa",
        "default_length": 1100,
        "min_length": 700,
        "max_length": 1600,
        "tone": "desmitificador y técnico",
        "structure": ["specs_anunciadas", "realidad", "trucos_marketing", "lo_que_importa", "lo_que_no_dicen"],
        "keywords_density": 0.02,
        "internal_links_min": 4,
        "internal_links_max": 10,
        "guiding_questions": [
            "¿Specs promocionadas del producto?",
            "¿Qué significan REALMENTE para el usuario?",
            "¿Trucos de marketing? (TDP vs consumo real, boost vs sostenida, contraste dinámico vs nativo)",
            "¿Specs puro marketing? (millones de colores)",
            "¿Specs que SÍ impactan? (tiempo respuesta REAL)",
            "¿Specs que NO mencionan pero deberías preguntar? (PWM monitores, coil whine GPUs)",
            "¿Casos donde la spec inferior es MEJOR?"
        ]
    },
}


# ============================================================================
# FUNCIONES DE ACCESO
# ============================================================================

def get_arquetipo(code: str) -> Optional[Dict[str, Any]]:
    """Obtiene un arquetipo por su código."""
    return ARQUETIPOS.get(code)


def get_arquetipo_by_name(name: str) -> Optional[Dict[str, Any]]:
    """Obtiene un arquetipo por su nombre (búsqueda parcial, case-insensitive)."""
    name_lower = name.lower()
    for arq in ARQUETIPOS.values():
        if name_lower in arq["name"].lower():
            return arq
    return None


def get_all_arquetipos() -> Dict[str, Dict[str, Any]]:
    """Retorna todos los arquetipos."""
    return ARQUETIPOS


def list_arquetipos() -> List[Dict[str, Any]]:
    """Retorna lista de arquetipos (para compatibilidad)."""
    return list(ARQUETIPOS.values())


def get_arquetipo_names() -> Dict[str, str]:
    """Retorna diccionario {código: nombre} para selectores."""
    return {code: data['name'] for code, data in ARQUETIPOS.items()}


def get_arquetipo_codes() -> List[str]:
    """Retorna lista de códigos de arquetipos."""
    return list(ARQUETIPOS.keys())


# Alias para compatibilidad con versiones anteriores
get_all_codes = get_arquetipo_codes


def get_guiding_questions(code: str) -> List[str]:
    """Obtiene las preguntas guía de un arquetipo."""
    arq = ARQUETIPOS.get(code)
    if arq:
        return arq.get("guiding_questions", [])
    return []


def get_arquetipo_description(code: str) -> str:
    """Obtiene la descripción de un arquetipo."""
    arq = ARQUETIPOS.get(code)
    if arq:
        return arq.get("description", "")
    return ""


def get_default_length(code: str) -> int:
    """Obtiene la longitud por defecto de un arquetipo."""
    arq = ARQUETIPOS.get(code)
    if arq:
        return arq.get("default_length", 1200)
    return 1200


def get_length_range(code: str) -> tuple:
    """Obtiene el rango de longitud (min, max) de un arquetipo."""
    arq = ARQUETIPOS.get(code)
    if arq:
        return (arq.get("min_length", 500), arq.get("max_length", 3000))
    return (500, 3000)


def get_links_range(code: str) -> tuple:
    """Obtiene el rango de enlaces (min, max) de un arquetipo."""
    arq = ARQUETIPOS.get(code)
    if arq:
        return (arq.get("internal_links_min", 3), arq.get("internal_links_max", 15))
    return (3, 15)


def validate_arquetipo_code(code: str) -> bool:
    """Valida si un código de arquetipo existe."""
    return code in ARQUETIPOS


def format_arquetipo_for_prompt(code: str) -> str:
    """Formatea la información del arquetipo para incluir en el prompt."""
    arq = ARQUETIPOS.get(code)
    if not arq:
        return ""
    
    sections = []
    sections.append(f"**Arquetipo:** {arq['name']} ({code})")
    sections.append(f"**Descripción:** {arq['description']}")
    sections.append(f"**Tono:** {arq['tone']}")
    sections.append(f"**Estructura:** {' → '.join(arq['structure'])}")
    sections.append(f"**Longitud objetivo:** {arq['default_length']} palabras ({arq['min_length']}-{arq['max_length']})")
    sections.append(f"**Densidad keywords:** {arq['keywords_density']*100:.1f}%")
    sections.append(f"**Enlaces internos:** {arq['internal_links_min']}-{arq['internal_links_max']}")
    
    return "\n".join(sections)


def format_guiding_questions_for_display(code: str) -> str:
    """Formatea las preguntas guía para mostrar en UI."""
    questions = get_guiding_questions(code)
    if not questions:
        return ""
    
    lines = [f"{i+1}. {q}" for i, q in enumerate(questions)]
    return "\n".join(lines)


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    # Versión
    "__version__",
    # Datos
    "ARQUETIPOS",
    # Funciones de acceso
    "get_arquetipo",
    "get_arquetipo_by_name",
    "get_all_arquetipos",
    "list_arquetipos",
    "get_arquetipo_names",
    "get_arquetipo_codes",
    "get_all_codes",  # Alias para compatibilidad
    "get_guiding_questions",
    "get_arquetipo_description",
    "get_default_length",
    "get_length_range",
    "get_links_range",
    "validate_arquetipo_code",
    "format_arquetipo_for_prompt",
    "format_guiding_questions_for_display",
]
