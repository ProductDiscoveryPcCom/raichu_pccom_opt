"""
Definición de arquetipos de contenido - PcComponentes
Versión 4.1.1

Este módulo contiene los 18 arquetipos de contenido con sus campos específicos.
Cada arquetipo define:
- Información básica (code, name, description)
- Embudo de conversión (funnel)
- Longitud por defecto
- Casos de uso
- Campos específicos para el formulario
"""

from typing import Dict, List, Optional


# ============================================================================
# ARQUETIPOS COMPLETOS CON CAMPOS ESPECÍFICOS
# ============================================================================

ARQUETIPOS = {
    "ARQ-1": {
        "code": "ARQ-1",
        "name": "📰 Noticia / Actualidad",
        "description": "Noticia sobre lanzamiento, actualización o evento relevante",
        "funnel": "Top",
        "default_length": 1200,
        "use_case": "Lanzamientos, actualizaciones, eventos, anuncios oficiales",
        "campos_especificos": {
            "noticia_principal": {
                "label": "¿Qué ha pasado? (noticia principal)",
                "type": "textarea",
                "placeholder": "Ej: Xiaomi lanza nuevo robot aspirador E5 Pro con mapeo láser y autovaciado por 199€",
                "help": "Resumen de la noticia en 1-2 frases"
            },
            "fecha_evento": {
                "label": "Fecha del evento/lanzamiento",
                "type": "text",
                "placeholder": "Ej: 25 de noviembre de 2025",
                "help": "Fecha exacta si está disponible"
            },
            "fuente_oficial": {
                "label": "Fuente oficial",
                "type": "text",
                "placeholder": "Ej: Comunicado oficial de Xiaomi, evento de prensa",
                "help": "De dónde viene la información"
            },
            "contexto_previo": {
                "label": "Contexto previo relevante",
                "type": "textarea",
                "placeholder": "Ej: El modelo anterior E5 fue bestseller en 2024 con más de 50.000 unidades vendidas",
                "help": "Información de fondo que da contexto"
            },
            "impacto_usuario": {
                "label": "Impacto para el usuario",
                "type": "textarea",
                "placeholder": "Ej: Los usuarios actuales del E5 podrán actualizar el firmware para activar nuevas funciones",
                "help": "Qué significa esto para los lectores"
            }
        }
    },
    
    "ARQ-2": {
        "code": "ARQ-2",
        "name": "📖 Guía Paso a Paso",
        "description": "Tutorial detallado para realizar una tarea o configuración",
        "funnel": "Middle",
        "default_length": 1800,
        "use_case": "Configuraciones, instalaciones, resolución de problemas",
        "campos_especificos": {
            "tarea_objetivo": {
                "label": "¿Qué tarea se va a explicar?",
                "type": "text",
                "placeholder": "Ej: Configurar el robot aspirador Xiaomi E5 para limpieza programada",
                "help": "Objetivo claro que el usuario quiere conseguir"
            },
            "requisitos_previos": {
                "label": "Requisitos previos",
                "type": "textarea",
                "placeholder": "Ej: Tener la app Xiaomi Home instalada, WiFi 2.4GHz configurado, robot cargado al 100%",
                "help": "Qué necesita el usuario antes de empezar"
            },
            "tiempo_estimado": {
                "label": "Tiempo estimado",
                "type": "text",
                "placeholder": "Ej: 10-15 minutos",
                "help": "Cuánto tardará el proceso"
            },
            "dificultad": {
                "label": "Nivel de dificultad",
                "type": "text",
                "placeholder": "Ej: Principiante / Intermedio / Avanzado",
                "help": "Para qué nivel de usuario está pensado"
            },
            "puntos_criticos": {
                "label": "Puntos críticos o errores comunes",
                "type": "textarea",
                "placeholder": "Ej: Asegúrate de conectar al WiFi 2.4GHz y NO 5GHz. Si no aparece el robot, reinicia la app",
                "help": "Problemas típicos y cómo evitarlos"
            }
        }
    },
    
    "ARQ-3": {
        "code": "ARQ-3",
        "name": "💡 Explicación / Educativo",
        "description": "Explica conceptos técnicos o funcionamiento de tecnología",
        "funnel": "Top",
        "default_length": 1600,
        "use_case": "Educar sobre tecnologías, conceptos, diferencias técnicas",
        "campos_especificos": {
            "concepto_principal": {
                "label": "Concepto a explicar",
                "type": "text",
                "placeholder": "Ej: Navegación láser vs giroscopio en robots aspiradores",
                "help": "Qué se va a explicar"
            },
            "nivel_tecnico": {
                "label": "Nivel técnico del público",
                "type": "text",
                "placeholder": "Ej: Usuario general sin conocimientos técnicos",
                "help": "Define cuánto tecnicismo usar"
            },
            "analogias_utiles": {
                "label": "Analogías o ejemplos útiles",
                "type": "textarea",
                "placeholder": "Ej: La navegación láser es como un GPS que mapea tu casa; el giroscopio es como conducir con brújula",
                "help": "Comparaciones que faciliten la comprensión"
            },
            "aplicacion_practica": {
                "label": "Aplicación práctica",
                "type": "textarea",
                "placeholder": "Ej: Con láser puedes limpiar solo la cocina; con giroscopio limpia toda la casa sin seleccionar",
                "help": "Por qué es importante este concepto en la práctica"
            }
        }
    },
    
    "ARQ-4": {
        "code": "ARQ-4",
        "name": "⭐ Review / Análisis",
        "description": "Análisis profundo de producto único con pros, contras y veredicto",
        "funnel": "Middle",
        "default_length": 1800,
        "use_case": "Producto único destacado - Black Friday, lanzamientos, ofertas especiales",
        "campos_especificos": {
            "tiempo_uso": {
                "label": "Tiempo de uso/prueba",
                "type": "text",
                "placeholder": "Ej: 2 semanas de uso intensivo",
                "help": "Cuánto tiempo se ha probado el producto"
            },
            "escenarios_prueba": {
                "label": "Escenarios de prueba",
                "type": "textarea",
                "placeholder": "Ej: Piso 75m², 2 adultos + perro, suelos de parquet y baldosa, limpieza diaria",
                "help": "En qué contexto se ha probado"
            },
            "competencia_directa": {
                "label": "Competencia directa",
                "type": "text",
                "placeholder": "Ej: Roborock Q7, Conga 3490, iRobot Roomba i3",
                "help": "Productos similares para comparar"
            },
            "punto_fuerte_principal": {
                "label": "Principal punto fuerte",
                "type": "text",
                "placeholder": "Ej: Relación calidad-precio imbatible en su rango",
                "help": "Lo que más destaca del producto"
            },
            "limitacion_principal": {
                "label": "Principal limitación",
                "type": "text",
                "placeholder": "Ej: No tiene mapeo por habitaciones",
                "help": "Limitación más importante a mencionar (en positivo)"
            }
        }
    },
    
    "ARQ-5": {
        "code": "ARQ-5",
        "name": "⚖️ Comparativa A vs B",
        "description": "Comparación directa entre 2-3 productos similares",
        "funnel": "Middle",
        "default_length": 1600,
        "use_case": "Ayudar a elegir entre alternativas directas",
        "campos_especificos": {
            "producto_a_nombre": {
                "label": "Producto A - Nombre",
                "type": "text",
                "placeholder": "Ej: Xiaomi Robot Vacuum E5",
                "help": "Primer producto a comparar"
            },
            "producto_a_caracteristicas": {
                "label": "Producto A - Características clave",
                "type": "textarea",
                "placeholder": "Ej: 2000Pa succión, 110 min autonomía, WiFi, fregado básico, 59€",
                "help": "Specs principales del producto A"
            },
            "producto_a_mejor_para": {
                "label": "Producto A - Mejor para casos de uso",
                "type": "textarea",
                "placeholder": "Ej: Presupuesto ajustado, pisos pequeños-medianos, mantenimiento diario básico",
                "help": "Cuándo elegir el producto A"
            },
            "producto_b_nombre": {
                "label": "Producto B - Nombre",
                "type": "text",
                "placeholder": "Ej: Roborock Q7",
                "help": "Segundo producto a comparar"
            },
            "producto_b_caracteristicas": {
                "label": "Producto B - Características clave",
                "type": "textarea",
                "placeholder": "Ej: 2700Pa succión, 180 min autonomía, mapeo láser, fregado inteligente, 99€",
                "help": "Specs principales del producto B"
            },
            "producto_b_mejor_para": {
                "label": "Producto B - Mejor para casos de uso",
                "type": "textarea",
                "placeholder": "Ej: Casas grandes, necesidad de mapeo por habitaciones, presupuesto medio",
                "help": "Cuándo elegir el producto B"
            },
            "criterios_comparacion": {
                "label": "Criterios principales de comparación",
                "type": "textarea",
                "placeholder": "Ej: Potencia de succión, autonomía, navegación, fregado, precio, app móvil",
                "help": "En qué aspectos se van a comparar"
            }
        }
    },
    
    "ARQ-6": {
        "code": "ARQ-6",
        "name": "🔥 Deal Alert / Chollo",
        "description": "Alerta de oferta destacada con urgencia",
        "funnel": "Bottom",
        "default_length": 1000,
        "use_case": "Ofertas flash, chollos limitados, precio histórico",
        "campos_especificos": {
            "precio_actual": {
                "label": "Precio actual",
                "type": "text",
                "placeholder": "Ej: 59€",
                "help": "Precio de la oferta"
            },
            "precio_habitual": {
                "label": "Precio habitual",
                "type": "text",
                "placeholder": "Ej: 89€",
                "help": "Precio normal sin oferta"
            },
            "ahorro_total": {
                "label": "Ahorro total",
                "type": "text",
                "placeholder": "Ej: 30€ (-34%)",
                "help": "Cuánto se ahorra"
            },
            "duracion_oferta": {
                "label": "Duración de la oferta",
                "type": "text",
                "placeholder": "Ej: Solo hasta medianoche / Mientras duren existencias / 72 horas",
                "help": "Cuánto tiempo estará disponible"
            },
            "stock_disponible": {
                "label": "Stock o unidades disponibles",
                "type": "text",
                "placeholder": "Ej: Quedan menos de 20 unidades / Stock limitado",
                "help": "Información de disponibilidad para urgencia"
            },
            "precio_historico": {
                "label": "¿Es precio mínimo histórico?",
                "type": "text",
                "placeholder": "Ej: Sí, primera vez por debajo de 60€ / No, pero mejor precio del mes",
                "help": "Contexto histórico del precio"
            },
            "por_que_oferta": {
                "label": "¿Por qué está en oferta?",
                "type": "text",
                "placeholder": "Ej: Black Friday / Nuevo modelo próximo a salir / Liquidación stock",
                "help": "Razón de la oferta (si se conoce)"
            }
        }
    },
    
    "ARQ-7": {
        "code": "ARQ-7",
        "name": "🏆 Roundup / Mejores X",
        "description": "Top X productos en una categoría",
        "funnel": "Middle",
        "default_length": 2200,
        "use_case": "Lista categoría - Black Friday, guías de compra",
        "campos_especificos": {
            "numero_productos": {
                "label": "Número de productos en el top",
                "type": "text",
                "placeholder": "Ej: 5",
                "help": "Cuántos productos incluir (3-10 recomendado)"
            },
            "criterios_seleccion": {
                "label": "Criterios de selección",
                "type": "textarea",
                "placeholder": "Ej: Probados personalmente, más vendidos del año, mejor valorados, diferentes rangos de precio",
                "help": "Por qué estos productos y no otros"
            },
            "rango_precios": {
                "label": "Rango de precios",
                "type": "text",
                "placeholder": "Ej: De 59€ a 299€",
                "help": "Desde el más barato al más caro"
            },
            "categoria_especifica": {
                "label": "Categoría específica",
                "type": "text",
                "placeholder": "Ej: Robots aspiradores con fregado / Monitores gaming 1440p / Portátiles <600€",
                "help": "Define bien la categoría para el título"
            },
            "ganador_absoluto": {
                "label": "Ganador absoluto (si lo hay)",
                "type": "text",
                "placeholder": "Ej: Roborock S7+ es nuestra elección premium / Xiaomi E5 mejor calidad-precio",
                "help": "Producto destacado del top (opcional)"
            }
        }
    },
    
    "ARQ-8": {
        "code": "ARQ-8",
        "name": "💰 Por presupuesto",
        "description": "Mejores productos por menos de X€",
        "funnel": "Bottom",
        "default_length": 1600,
        "use_case": "Chollos en rango de precio específico",
        "campos_especificos": {
            "presupuesto_limite": {
                "label": "Presupuesto límite",
                "type": "text",
                "placeholder": "Ej: 100€ / 500€ / 1000€",
                "help": "Precio máximo del rango"
            },
            "que_esperar": {
                "label": "Qué se puede esperar en este rango",
                "type": "textarea",
                "placeholder": "Ej: Por menos de 100€ puedes conseguir robots básicos sin mapeo pero con buena succión y app móvil",
                "help": "Expectativas realistas del presupuesto"
            },
            "que_sacrificas": {
                "label": "Qué características se sacrifican",
                "type": "textarea",
                "placeholder": "Ej: No tendrás mapeo láser ni autovaciado, pero la limpieza básica es efectiva",
                "help": "Qué no esperar en este rango (en positivo)"
            },
            "mejor_opcion": {
                "label": "Mejor opción en el rango",
                "type": "text",
                "placeholder": "Ej: Xiaomi E5 a 59€ es imbatible en calidad-precio",
                "help": "Producto destacado del presupuesto"
            }
        }
    },
    
    "ARQ-9": {
        "code": "ARQ-9",
        "name": "🥊 Versus Detallado",
        "description": "Enfrentamiento profundo producto a producto con ganador claro",
        "funnel": "Bottom",
        "default_length": 2000,
        "use_case": "Decisión de compra entre dos modelos muy similares",
        "campos_especificos": {
            "producto_1": {
                "label": "Producto 1",
                "type": "text",
                "placeholder": "Ej: Xiaomi Robot Vacuum E5",
                "help": "Primer contendiente"
            },
            "producto_2": {
                "label": "Producto 2",
                "type": "text",
                "placeholder": "Ej: Roborock Q7",
                "help": "Segundo contendiente"
            },
            "categorias_versus": {
                "label": "Categorías de enfrentamiento",
                "type": "textarea",
                "placeholder": "Ej: Potencia de succión, Autonomía, Navegación, Fregado, App móvil, Precio, Ruido",
                "help": "Aspectos específicos a comparar (separa por comas o líneas)"
            },
            "ganador_categorias": {
                "label": "Ganadores por categoría",
                "type": "textarea",
                "placeholder": "Ej: Succión: Roborock +700Pa | Autonomía: Roborock +70min | Precio: Xiaomi -40€",
                "help": "Quién gana en cada categoría"
            },
            "ganador_global": {
                "label": "Ganador global y por qué",
                "type": "textarea",
                "placeholder": "Ej: Xiaomi gana por precio y suficiencia; Roborock solo vale la pena si necesitas mapeo láser",
                "help": "Veredicto final del versus"
            }
        }
    },
    
    "ARQ-10": {
        "code": "ARQ-10",
        "name": "👤 Por perfil de usuario",
        "description": "Productos perfectos para un tipo específico de usuario",
        "funnel": "Middle",
        "default_length": 1800,
        "use_case": "Segmentación por audiencia (gamers, estudiantes, profesionales)",
        "campos_especificos": {
            "perfil_usuario": {
                "label": "Perfil de usuario",
                "type": "text",
                "placeholder": "Ej: Estudiante universitario / Gamer competitivo / Profesional teletrabajo",
                "help": "Define el tipo de usuario objetivo"
            },
            "necesidades_especificas": {
                "label": "Necesidades específicas del perfil",
                "type": "textarea",
                "placeholder": "Ej: Portabilidad, batería larga, presupuesto <600€, Office y navegación",
                "help": "Qué necesita este usuario específicamente"
            },
            "prioridades": {
                "label": "Prioridades del perfil",
                "type": "textarea",
                "placeholder": "Ej: 1. Precio, 2. Batería, 3. Peso, 4. Pantalla de calidad",
                "help": "Orden de importancia de características"
            },
            "no_necesita": {
                "label": "Qué NO necesita este perfil",
                "type": "textarea",
                "placeholder": "Ej: No necesita GPU dedicada, ni pantalla 4K, ni más de 16GB RAM",
                "help": "Características por las que no vale pagar más"
            }
        }
    },
    
    "ARQ-11": {
        "code": "ARQ-11",
        "name": "🔮 Tendencias / Predicciones",
        "description": "Análisis de tendencias del mercado o predicciones",
        "funnel": "Top",
        "default_length": 1400,
        "use_case": "Contenido de autoridad, análisis de mercado, tendencias tech",
        "campos_especificos": {
            "tendencia_principal": {
                "label": "Tendencia principal",
                "type": "text",
                "placeholder": "Ej: Robots aspiradores con IA y autovaciado se están volviendo accesibles",
                "help": "Qué tendencia se está observando"
            },
            "datos_soporte": {
                "label": "Datos que soportan la tendencia",
                "type": "textarea",
                "placeholder": "Ej: Ventas de modelos con autovaciado +150% vs 2023, precios han bajado 40% en 2 años",
                "help": "Números, stats, datos concretos"
            },
            "prediccion": {
                "label": "Predicción o evolución futura",
                "type": "textarea",
                "placeholder": "Ej: En 2026, los modelos básicos incluirán mapeo láser como estándar",
                "help": "Hacia dónde va el mercado"
            },
            "impacto_consumidor": {
                "label": "Impacto para el consumidor",
                "type": "textarea",
                "placeholder": "Ej: Mejor momento para comprar - más funciones por menos dinero que nunca",
                "help": "Qué significa para el usuario final"
            }
        }
    },
    
    "ARQ-12": {
        "code": "ARQ-12",
        "name": "📦 Unboxing / Primera impresión",
        "description": "Experiencia de unboxing y primeras horas con el producto",
        "funnel": "Top/Middle",
        "default_length": 1200,
        "use_case": "Lanzamientos, primeras impresiones, experiencia inicial",
        "campos_especificos": {
            "contenido_caja": {
                "label": "Contenido de la caja",
                "type": "textarea",
                "placeholder": "Ej: Robot, base de carga, mopa x2, cepillo extra, filtro adicional, manual",
                "help": "Qué viene incluido"
            },
            "primera_impresion_build": {
                "label": "Primera impresión - Construcción",
                "type": "textarea",
                "placeholder": "Ej: Plástico de calidad media-alta, peso 3kg, acabados limpios, botones físicos táctiles",
                "help": "Calidad de construcción al tacto"
            },
            "sorpresas_positivas": {
                "label": "Sorpresas positivas",
                "type": "textarea",
                "placeholder": "Ej: Incluye 2 mopas de repuesto y filtro extra, embalaje sostenible",
                "help": "Qué ha superado expectativas"
            },
            "sorpresas_negativas": {
                "label": "Decepciones o sorpresas negativas",
                "type": "textarea",
                "placeholder": "Ej: Manual solo en inglés, depósito de agua más pequeño de lo esperado",
                "help": "Qué ha decepcionado (en tono neutral)"
            },
            "setup_inicial": {
                "label": "Configuración inicial",
                "type": "text",
                "placeholder": "Ej: 5 minutos, muy sencillo, app intuitiva",
                "help": "Experiencia del primer uso"
            }
        }
    },
    
    "ARQ-13": {
        "code": "ARQ-13",
        "name": "❓ FAQ / Preguntas Frecuentes",
        "description": "Respuestas a las preguntas más comunes sobre un producto o categoría",
        "funnel": "Middle",
        "default_length": 1400,
        "use_case": "Resolver dudas comunes, SEO de long-tail queries",
        "campos_especificos": {
            "producto_categoria": {
                "label": "Producto o categoría",
                "type": "text",
                "placeholder": "Ej: Robots aspiradores / Xiaomi Robot Vacuum E5",
                "help": "Sobre qué trata el FAQ"
            },
            "preguntas_principales": {
                "label": "Preguntas principales (una por línea)",
                "type": "textarea",
                "placeholder": "¿Cuánto dura la batería?\n¿Se puede usar en alfombras?\n¿Necesita WiFi?",
                "help": "Preguntas más comunes"
            },
            "audiencia": {
                "label": "Audiencia objetivo",
                "type": "text",
                "placeholder": "Ej: Usuarios primerizos / Personas considerando compra",
                "help": "Para quién va dirigido"
            }
        }
    },
    
    "ARQ-14": {
        "code": "ARQ-14",
        "name": "🎯 Caso de Uso Específico",
        "description": "Soluciones para un problema o caso de uso muy concreto",
        "funnel": "Bottom",
        "default_length": 1600,
        "use_case": "Nichos específicos (mascotas, pisos pequeños, etc.)",
        "campos_especificos": {
            "problema_especifico": {
                "label": "Problema o caso de uso",
                "type": "text",
                "placeholder": "Ej: Limpieza efectiva con perros que sueltan mucho pelo",
                "help": "Qué problema resuelve"
            },
            "contexto_detallado": {
                "label": "Contexto detallado",
                "type": "textarea",
                "placeholder": "Ej: Dos perros labradores, piso 90m², suelos parquet y alfombras, pelo diario abundante",
                "help": "Situación específica del usuario"
            },
            "caracteristicas_criticas": {
                "label": "Características críticas para este caso",
                "type": "textarea",
                "placeholder": "Ej: Cepillo anti-enredo, depósito grande, succión 2500Pa+, app con alertas",
                "help": "Qué debe tener sí o sí"
            },
            "productos_recomendados": {
                "label": "Productos recomendados",
                "type": "text",
                "placeholder": "Ej: Roborock S7+ (premium), Conga 4690 (gama media), Xiaomi E10 (económico)",
                "help": "Productos que mejor funcionan"
            }
        }
    },
    
    "ARQ-15": {
        "code": "ARQ-15",
        "name": "⚠️ Errores Comunes",
        "description": "Errores típicos al comprar o usar un producto",
        "funnel": "Middle",
        "default_length": 1400,
        "use_case": "Educar para evitar frustraciones post-compra",
        "campos_especificos": {
            "categoria_producto": {
                "label": "Categoría o producto",
                "type": "text",
                "placeholder": "Ej: Robots aspiradores / Portátiles gaming",
                "help": "Sobre qué trata"
            },
            "errores_principales": {
                "label": "Errores principales (uno por línea)",
                "type": "textarea",
                "placeholder": "No considerar la altura del robot\nElegir por precio solo\nIgnorar tipo de suelos",
                "help": "Errores más comunes"
            },
            "consecuencias": {
                "label": "Consecuencias de cada error",
                "type": "textarea",
                "placeholder": "No puede limpiar debajo de muebles\nRenunciando a funciones esenciales\nRendimiento pobre en alfombras",
                "help": "Qué pasa si se comete cada error"
            }
        }
    },
    
    "ARQ-16": {
        "code": "ARQ-16",
        "name": "🆚 X vs Y - Cuál elegir",
        "description": "Dilema entre dos opciones con recomendación clara según perfil",
        "funnel": "Bottom",
        "default_length": 1600,
        "use_case": "Ayudar a decidir entre dos alternativas populares",
        "campos_especificos": {
            "opcion_a": {
                "label": "Opción A",
                "type": "text",
                "placeholder": "Ej: Xiaomi Robot Vacuum E5",
                "help": "Primera opción"
            },
            "opcion_b": {
                "label": "Opción B",
                "type": "text",
                "placeholder": "Ej: Roborock Q7",
                "help": "Segunda opción"
            },
            "perfiles_usuario": {
                "label": "Perfiles de usuario",
                "type": "textarea",
                "placeholder": "Perfil 1: Presupuesto ajustado\nPerfil 2: Necesita mapeo\nPerfil 3: Casa grande",
                "help": "Diferentes tipos de usuarios"
            },
            "recomendacion_por_perfil": {
                "label": "Recomendación por perfil",
                "type": "textarea",
                "placeholder": "Perfil 1 → Xiaomi E5\nPerfil 2 → Roborock Q7\nPerfil 3 → Roborock Q7",
                "help": "Cuál elegir según perfil"
            }
        }
    },
    
    "ARQ-17": {
        "code": "ARQ-17",
        "name": "📊 Comparativa Tabla",
        "description": "Comparación visual de múltiples productos en tabla",
        "funnel": "Middle",
        "default_length": 1200,
        "use_case": "Comparar 3-5 productos visualmente",
        "campos_especificos": {
            "productos_comparar": {
                "label": "Productos a comparar (uno por línea)",
                "type": "textarea",
                "placeholder": "Xiaomi E5\nRoborock Q7\nConga 4690\niRobot Roomba i3",
                "help": "Lista de productos"
            },
            "criterios_tabla": {
                "label": "Criterios de comparación (columnas)",
                "type": "textarea",
                "placeholder": "Precio\nPotencia succión\nAutonomía\nMapeo\nFregado\nApp",
                "help": "Qué aspectos comparar"
            },
            "destacar_ganador": {
                "label": "¿Destacar ganador por criterio?",
                "type": "text",
                "placeholder": "Sí / No",
                "help": "Marcar el mejor en cada categoría"
            }
        }
    },
    
    "ARQ-18": {
        "code": "ARQ-18",
        "name": "🎁 Regalo Perfecto",
        "description": "Guía de regalo para ocasión o persona específica",
        "funnel": "Top/Middle",
        "default_length": 1400,
        "use_case": "Navidad, cumpleaños, ocasiones especiales",
        "campos_especificos": {
            "ocasion": {
                "label": "Ocasión",
                "type": "text",
                "placeholder": "Ej: Navidad / Cumpleaños papá / Día de la madre",
                "help": "Para qué ocasión"
            },
            "perfil_receptor": {
                "label": "Perfil del receptor",
                "type": "textarea",
                "placeholder": "Ej: Persona mayor, no muy tech-savvy, vive en piso pequeño, le gusta la limpieza",
                "help": "Cómo es la persona que recibe el regalo"
            },
            "presupuesto_regalo": {
                "label": "Presupuesto",
                "type": "text",
                "placeholder": "Ej: 50-100€ / 100-200€ / Sin límite",
                "help": "Rango de precio del regalo"
            },
            "opciones_regalo": {
                "label": "Opciones de regalo (una por línea)",
                "type": "textarea",
                "placeholder": "Xiaomi E5 (económico)\nRoborock Q7 (gama media)\nRoborock S7+ (premium)",
                "help": "Productos recomendados"
            },
            "por_que_perfecto": {
                "label": "Por qué es perfecto para esta ocasión",
                "type": "textarea",
                "placeholder": "Ej: Regalar tiempo libre, producto útil que se usa a diario, tecnología accesible",
                "help": "Justificación del regalo"
            }
        }
    }
}


# ============================================================================
# FUNCIONES DE UTILIDAD
# ============================================================================

def get_arquetipo(code: str) -> Optional[Dict]:
    """
    Obtiene un arquetipo por su código
    
    Args:
        code: Código del arquetipo (ej: "ARQ-1")
        
    Returns:
        Dict con datos del arquetipo o None si no existe
    """
    return ARQUETIPOS.get(code)


def list_arquetipos() -> List[str]:
    """
    Lista todos los códigos de arquetipos disponibles
    
    Returns:
        Lista de códigos (ej: ["ARQ-1", "ARQ-2", ...])
    """
    return list(ARQUETIPOS.keys())


def get_arquetipos_by_funnel(funnel: str) -> List[Dict]:
    """
    Obtiene arquetipos filtrados por embudo de conversión
    
    Args:
        funnel: "Top", "Middle" o "Bottom"
        
    Returns:
        Lista de arquetipos que pertenecen a ese embudo
    """
    return [arq for arq in ARQUETIPOS.values() if arq['funnel'] == funnel]


def get_arquetipo_by_use_case(search_term: str) -> List[Dict]:
    """
    Busca arquetipos por término en su caso de uso
    
    Args:
        search_term: Término a buscar (ej: "Black Friday")
        
    Returns:
        Lista de arquetipos que coinciden
    """
    search_term_lower = search_term.lower()
    return [
        arq for arq in ARQUETIPOS.values() 
        if search_term_lower in arq['use_case'].lower()
    ]


def validate_arquetipo_code(code: str) -> bool:
    """
    Valida si un código de arquetipo existe
    
    Args:
        code: Código a validar
        
    Returns:
        True si existe, False si no
    """
    return code in ARQUETIPOS


def get_arquetipo_count() -> int:
    """
    Obtiene el número total de arquetipos
    
    Returns:
        Número de arquetipos disponibles
    """
    return len(ARQUETIPOS)
