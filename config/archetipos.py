"""
Arquetipos de Contenido - PcComponentes Content Generator
Versión 4.3.0

Define los 18 arquetipos de contenido SEO para PcComponentes.

Autor: PcComponentes - Product Discovery & Content
"""

from typing import Dict, List, Optional, Any

__version__ = "4.3.0"

# ============================================================================
# DEFINICIÓN DE ARQUETIPOS
# ============================================================================

ARQUETIPOS: Dict[str, Dict[str, Any]] = {
    "ARQ-1": {
        "code": "ARQ-1",
        "name": "Guía de Compra",
        "description": "Guía completa para ayudar al usuario a elegir el mejor producto",
        "default_length": 1500,
        "min_length": 1000,
        "max_length": 2500,
        "tone": "informativo y consultivo",
        "structure": ["intro", "criterios", "comparativa", "recomendaciones", "faqs", "verdict"],
        "keywords_density": 0.02,
        "internal_links_min": 5,
        "internal_links_max": 15
    },
    "ARQ-2": {
        "code": "ARQ-2",
        "name": "Comparativa de Productos",
        "description": "Comparación detallada entre productos similares",
        "default_length": 1800,
        "min_length": 1200,
        "max_length": 3000,
        "tone": "analítico y objetivo",
        "structure": ["intro", "productos", "tabla_comparativa", "analisis", "ganador", "faqs", "verdict"],
        "keywords_density": 0.018,
        "internal_links_min": 8,
        "internal_links_max": 20
    },
    "ARQ-3": {
        "code": "ARQ-3",
        "name": "Review de Producto",
        "description": "Análisis en profundidad de un producto específico",
        "default_length": 1200,
        "min_length": 800,
        "max_length": 2000,
        "tone": "experto y detallado",
        "structure": ["intro", "especificaciones", "rendimiento", "pros_contras", "faqs", "verdict"],
        "keywords_density": 0.025,
        "internal_links_min": 3,
        "internal_links_max": 10
    },
    "ARQ-4": {
        "code": "ARQ-4",
        "name": "Tutorial / How-To",
        "description": "Guía paso a paso para realizar una tarea",
        "default_length": 1400,
        "min_length": 1000,
        "max_length": 2200,
        "tone": "didáctico y práctico",
        "structure": ["intro", "requisitos", "pasos", "consejos", "errores_comunes", "faqs", "verdict"],
        "keywords_density": 0.02,
        "internal_links_min": 4,
        "internal_links_max": 12
    },
    "ARQ-5": {
        "code": "ARQ-5",
        "name": "Listado / Top N",
        "description": "Lista de los mejores productos en una categoría",
        "default_length": 2000,
        "min_length": 1500,
        "max_length": 3500,
        "tone": "dinámico y recomendador",
        "structure": ["intro", "criterios", "listado", "tabla_resumen", "faqs", "verdict"],
        "keywords_density": 0.015,
        "internal_links_min": 10,
        "internal_links_max": 25
    },
    "ARQ-6": {
        "code": "ARQ-6",
        "name": "Guía Técnica",
        "description": "Explicación técnica de conceptos o tecnologías",
        "default_length": 1600,
        "min_length": 1200,
        "max_length": 2500,
        "tone": "técnico pero accesible",
        "structure": ["intro", "conceptos", "funcionamiento", "aplicaciones", "faqs", "verdict"],
        "keywords_density": 0.022,
        "internal_links_min": 5,
        "internal_links_max": 15
    },
    "ARQ-7": {
        "code": "ARQ-7",
        "name": "Ofertas y Promociones",
        "description": "Contenido sobre ofertas, descuentos y promociones",
        "default_length": 1000,
        "min_length": 600,
        "max_length": 1500,
        "tone": "urgente y promocional",
        "structure": ["intro", "ofertas_destacadas", "categorias", "consejos_compra", "faqs", "verdict"],
        "keywords_density": 0.02,
        "internal_links_min": 8,
        "internal_links_max": 20
    },
    "ARQ-8": {
        "code": "ARQ-8",
        "name": "Categoría / Hub",
        "description": "Página de categoría con contenido informativo",
        "default_length": 1200,
        "min_length": 800,
        "max_length": 1800,
        "tone": "organizativo e informativo",
        "structure": ["intro", "subcategorias", "productos_destacados", "guia_rapida", "faqs", "verdict"],
        "keywords_density": 0.018,
        "internal_links_min": 10,
        "internal_links_max": 30
    },
    "ARQ-9": {
        "code": "ARQ-9",
        "name": "Resolución de Problemas",
        "description": "Guía para solucionar problemas técnicos comunes",
        "default_length": 1300,
        "min_length": 900,
        "max_length": 2000,
        "tone": "útil y solucionador",
        "structure": ["intro", "problema", "causas", "soluciones", "prevencion", "faqs", "verdict"],
        "keywords_density": 0.02,
        "internal_links_min": 4,
        "internal_links_max": 12
    },
    "ARQ-10": {
        "code": "ARQ-10",
        "name": "Noticias / Lanzamientos",
        "description": "Cobertura de novedades y lanzamientos de productos",
        "default_length": 800,
        "min_length": 500,
        "max_length": 1200,
        "tone": "actual e informativo",
        "structure": ["intro", "noticia", "especificaciones", "disponibilidad", "opinion", "verdict"],
        "keywords_density": 0.025,
        "internal_links_min": 3,
        "internal_links_max": 8
    },
    "ARQ-11": {
        "code": "ARQ-11",
        "name": "Setup / Configuración",
        "description": "Guías de montaje y configuración de equipos",
        "default_length": 1500,
        "min_length": 1000,
        "max_length": 2500,
        "tone": "práctico y detallado",
        "structure": ["intro", "componentes", "pasos_montaje", "configuracion", "optimizacion", "faqs", "verdict"],
        "keywords_density": 0.018,
        "internal_links_min": 6,
        "internal_links_max": 15
    },
    "ARQ-12": {
        "code": "ARQ-12",
        "name": "Gaming / Esports",
        "description": "Contenido especializado para gamers",
        "default_length": 1400,
        "min_length": 1000,
        "max_length": 2200,
        "tone": "entusiasta y conocedor",
        "structure": ["intro", "requisitos", "rendimiento", "configuracion_optima", "faqs", "verdict"],
        "keywords_density": 0.02,
        "internal_links_min": 5,
        "internal_links_max": 15
    },
    "ARQ-13": {
        "code": "ARQ-13",
        "name": "Profesional / Workstation",
        "description": "Contenido para uso profesional y empresarial",
        "default_length": 1600,
        "min_length": 1200,
        "max_length": 2500,
        "tone": "profesional y técnico",
        "structure": ["intro", "necesidades", "soluciones", "comparativa", "roi", "faqs", "verdict"],
        "keywords_density": 0.018,
        "internal_links_min": 5,
        "internal_links_max": 15
    },
    "ARQ-14": {
        "code": "ARQ-14",
        "name": "Hogar Inteligente",
        "description": "Contenido sobre domótica y smart home",
        "default_length": 1300,
        "min_length": 900,
        "max_length": 2000,
        "tone": "moderno y práctico",
        "structure": ["intro", "ecosistemas", "productos", "instalacion", "automatizacion", "faqs", "verdict"],
        "keywords_density": 0.02,
        "internal_links_min": 5,
        "internal_links_max": 15
    },
    "ARQ-15": {
        "code": "ARQ-15",
        "name": "Presupuesto / Budget",
        "description": "Guías para diferentes rangos de presupuesto",
        "default_length": 1500,
        "min_length": 1000,
        "max_length": 2200,
        "tone": "práctico y orientado al valor",
        "structure": ["intro", "rangos_precio", "opciones", "mejor_valor", "faqs", "verdict"],
        "keywords_density": 0.018,
        "internal_links_min": 8,
        "internal_links_max": 20
    },
    "ARQ-16": {
        "code": "ARQ-16",
        "name": "Temporada / Estacional",
        "description": "Contenido para temporadas específicas (vuelta al cole, navidad, etc.)",
        "default_length": 1200,
        "min_length": 800,
        "max_length": 1800,
        "tone": "oportuno y relevante",
        "structure": ["intro", "contexto", "productos_recomendados", "ofertas", "faqs", "verdict"],
        "keywords_density": 0.02,
        "internal_links_min": 6,
        "internal_links_max": 18
    },
    "ARQ-17": {
        "code": "ARQ-17",
        "name": "Sostenibilidad / Eco",
        "description": "Contenido sobre productos ecológicos y sostenibles",
        "default_length": 1100,
        "min_length": 700,
        "max_length": 1600,
        "tone": "consciente y responsable",
        "structure": ["intro", "impacto", "alternativas", "certificaciones", "faqs", "verdict"],
        "keywords_density": 0.02,
        "internal_links_min": 4,
        "internal_links_max": 12
    },
    "ARQ-18": {
        "code": "ARQ-18",
        "name": "Genérico / Flexible",
        "description": "Arquetipo flexible para contenidos que no encajan en otros",
        "default_length": 1500,
        "min_length": 800,
        "max_length": 3000,
        "tone": "adaptable",
        "structure": ["intro", "desarrollo", "faqs", "verdict"],
        "keywords_density": 0.02,
        "internal_links_min": 5,
        "internal_links_max": 15
    }
}


# ============================================================================
# FUNCIONES DE ACCESO
# ============================================================================

def get_arquetipo(code: str) -> Optional[Dict[str, Any]]:
    """
    Obtiene un arquetipo por su código.
    
    Args:
        code: Código del arquetipo (ej: "ARQ-1")
        
    Returns:
        Dict con datos del arquetipo o None si no existe
    """
    return ARQUETIPOS.get(code)


def list_arquetipos() -> List[Dict[str, Any]]:
    """
    Retorna lista de todos los arquetipos.
    
    Returns:
        Lista de diccionarios con todos los arquetipos
    """
    return list(ARQUETIPOS.values())


def get_arquetipo_names() -> Dict[str, str]:
    """
    Retorna mapeo de código a nombre de arquetipo.
    
    Returns:
        Dict {code: name} para todos los arquetipos
    """
    return {code: data['name'] for code, data in ARQUETIPOS.items()}


def get_arquetipo_by_name(name: str) -> Optional[Dict[str, Any]]:
    """
    Busca un arquetipo por nombre.
    
    Args:
        name: Nombre del arquetipo
        
    Returns:
        Dict con datos del arquetipo o None
    """
    for arq in ARQUETIPOS.values():
        if arq['name'].lower() == name.lower():
            return arq
    return None


def get_default_length(code: str) -> int:
    """
    Obtiene la longitud por defecto de un arquetipo.
    
    Args:
        code: Código del arquetipo
        
    Returns:
        Longitud por defecto o 1500 si no existe
    """
    arq = get_arquetipo(code)
    return arq['default_length'] if arq else 1500


def validate_arquetipo_code(code: str) -> bool:
    """
    Valida si un código de arquetipo existe.
    
    Args:
        code: Código a validar
        
    Returns:
        True si el código existe
    """
    return code in ARQUETIPOS


def get_all_codes() -> List[str]:
    """
    Retorna todos los códigos de arquetipos.
    
    Returns:
        Lista de códigos (ARQ-1, ARQ-2, etc.)
    """
    return list(ARQUETIPOS.keys())


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    '__version__',
    'ARQUETIPOS',
    'get_arquetipo',
    'list_arquetipos',
    'get_arquetipo_names',
    'get_arquetipo_by_name',
    'get_default_length',
    'validate_arquetipo_code',
    'get_all_codes',
]
