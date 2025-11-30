"""
Product JSON Utils - PcComponentes Content Generator
Versión 1.0.0

Utilidades para parsear y formatear JSON de productos desde n8n.
Proporciona funciones para validar, extraer y formatear datos de productos.

Autor: PcComponentes - Product Discovery & Content
"""

import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)

__version__ = "1.0.0"

# URL del workflow n8n para generar JSON
N8N_PRODUCT_JSON_WORKFLOW = "https://n8n.prod.pccomponentes.com/workflow/jsjhKAdZFBSM5XFV/d6c3eb"


# ============================================================================
# DATA CLASSES
# ============================================================================

@dataclass
class ProductData:
    """Datos estructurados de un producto."""
    product_id: str
    legacy_id: str
    title: str
    description: str
    brand_name: str
    family_name: str
    attributes: Dict[str, str]
    images: List[str]
    features: Optional[Any]
    total_comments: int
    advantages: str
    disadvantages: str
    comments: List[Dict[str, str]]
    
    @property
    def main_image(self) -> Optional[str]:
        """Primera imagen del producto."""
        return self.images[0] if self.images else None
    
    @property
    def has_reviews(self) -> bool:
        """Indica si tiene reseñas."""
        return self.total_comments > 0
    
    @property
    def key_attributes(self) -> List[Tuple[str, str]]:
        """Atributos principales como lista de tuplas."""
        return list(self.attributes.items())


# ============================================================================
# PARSEO DE JSON
# ============================================================================

def parse_product_json(json_data: str) -> Optional[ProductData]:
    """
    Parsea JSON de producto desde n8n.
    
    Args:
        json_data: String con JSON del producto
        
    Returns:
        ProductData si es válido, None si hay error
    """
    try:
        data = json.loads(json_data)
        
        # El JSON viene como array con un elemento
        if isinstance(data, list) and len(data) > 0:
            product = data[0]
        elif isinstance(data, dict):
            product = data
        else:
            logger.error("Formato de JSON inválido - debe ser dict o array")
            return None
        
        # Validar campos requeridos
        required_fields = ['product_id', 'title', 'description']
        missing = [f for f in required_fields if f not in product]
        if missing:
            logger.error(f"Faltan campos requeridos: {missing}")
            return None
        
        # Crear objeto ProductData
        return ProductData(
            product_id=product.get('product_id', ''),
            legacy_id=product.get('legacy_id', ''),
            title=product.get('title', ''),
            description=product.get('description', ''),
            brand_name=product.get('brand_name', ''),
            family_name=product.get('family_name', ''),
            attributes=product.get('attributes', {}),
            images=product.get('images', []),
            features=product.get('features'),
            total_comments=product.get('totalComments', 0),
            advantages=product.get('advantages', ''),
            disadvantages=product.get('disadvantages', ''),
            comments=product.get('comments', [])
        )
        
    except json.JSONDecodeError as e:
        logger.error(f"Error al parsear JSON: {e}")
        return None
    except Exception as e:
        logger.error(f"Error inesperado al parsear JSON: {e}")
        return None


def validate_product_json(json_data: str) -> Tuple[bool, Optional[str]]:
    """
    Valida que el JSON tenga la estructura correcta.
    
    Args:
        json_data: String con JSON a validar
        
    Returns:
        Tuple (is_valid, error_message)
    """
    try:
        data = json.loads(json_data)
        
        # Verificar que sea array o dict
        if isinstance(data, list):
            if len(data) == 0:
                return False, "El array está vacío"
            product = data[0]
        elif isinstance(data, dict):
            product = data
        else:
            return False, "El JSON debe ser un objeto o un array"
        
        # Verificar campos requeridos
        required = ['product_id', 'title', 'description']
        missing = [f for f in required if f not in product]
        
        if missing:
            return False, f"Faltan campos requeridos: {', '.join(missing)}"
        
        return True, None
        
    except json.JSONDecodeError as e:
        return False, f"JSON inválido: {str(e)}"
    except Exception as e:
        return False, f"Error: {str(e)}"


# ============================================================================
# FORMATEO PARA PROMPTS
# ============================================================================

def format_product_for_prompt(product: ProductData, include_reviews: bool = True) -> str:
    """
    Formatea datos de producto para incluir en prompts de Claude.
    
    Args:
        product: Datos del producto
        include_reviews: Si incluir reseñas (pueden ser muy largas)
        
    Returns:
        String formateado para prompt
    """
    sections = []
    
    # Información básica
    sections.append(f"**PRODUCTO: {product.title}**")
    sections.append(f"ID: {product.product_id}")
    
    if product.brand_name:
        sections.append(f"Marca: {product.brand_name}")
    
    if product.family_name:
        sections.append(f"Familia: {product.family_name}")
    
    # Atributos principales
    if product.attributes:
        sections.append("\n**Características principales:**")
        for key, value in product.key_attributes:
            sections.append(f"- {key}: {value}")
    
    # Descripción
    if product.description:
        sections.append(f"\n**Descripción del producto:**")
        sections.append(product.description)
    
    # Ventajas y desventajas de usuarios
    if product.has_reviews:
        sections.append(f"\n**Basado en {product.total_comments} opiniones de usuarios:**")
        
        if product.advantages:
            sections.append("\n**Ventajas mencionadas por usuarios:**")
            # Limitar longitud de ventajas
            advantages = product.advantages[:1000] + "..." if len(product.advantages) > 1000 else product.advantages
            sections.append(advantages)
        
        if product.disadvantages:
            sections.append("\n**Aspectos a mejorar mencionados por usuarios:**")
            # Limitar longitud de desventajas
            disadvantages = product.disadvantages[:1000] + "..." if len(product.disadvantages) > 1000 else product.disadvantages
            sections.append(disadvantages)
    
    # Reseñas destacadas (opcional)
    if include_reviews and product.comments:
        sections.append("\n**Opiniones destacadas de usuarios:**")
        # Solo incluir primeras 3-5 opiniones más relevantes
        for i, comment in enumerate(product.comments[:3], 1):
            opinion = comment.get('opinion', '')
            if opinion:
                # Limitar longitud de cada opinión
                opinion_short = opinion[:300] + "..." if len(opinion) > 300 else opinion
                sections.append(f"{i}. {opinion_short}")
    
    # Imágenes disponibles
    if product.images:
        sections.append(f"\n**Imágenes del producto:** {len(product.images)} imágenes disponibles")
        if product.main_image:
            sections.append(f"Imagen principal: {product.main_image}")
    
    return "\n".join(sections)


def format_product_brief(product: ProductData) -> str:
    """
    Formatea versión breve del producto (para listas de enlaces).
    
    Args:
        product: Datos del producto
        
    Returns:
        String breve formateado
    """
    parts = [product.title]
    
    if product.brand_name:
        parts.append(f"({product.brand_name})")
    
    # Añadir 1-2 características clave
    key_attrs = []
    for key, value in list(product.key_attributes)[:2]:
        key_attrs.append(f"{key}: {value}")
    
    if key_attrs:
        parts.append("- " + ", ".join(key_attrs))
    
    return " ".join(parts)


def extract_key_features(product: ProductData, max_features: int = 5) -> List[str]:
    """
    Extrae características clave del producto.
    
    Args:
        product: Datos del producto
        max_features: Máximo de características a extraer
        
    Returns:
        Lista de características clave
    """
    features = []
    
    # Atributos principales
    for key, value in product.key_attributes[:max_features]:
        features.append(f"{key}: {value}")
    
    return features


# ============================================================================
# HELPERS PARA UI
# ============================================================================

def create_product_summary(product: ProductData) -> Dict[str, Any]:
    """
    Crea resumen del producto para mostrar en UI.
    
    Args:
        product: Datos del producto
        
    Returns:
        Dict con datos resumidos para UI
    """
    return {
        'title': product.title,
        'brand': product.brand_name,
        'family': product.family_name,
        'product_id': product.product_id,
        'has_reviews': product.has_reviews,
        'total_comments': product.total_comments,
        'attributes_count': len(product.attributes),
        'images_count': len(product.images),
        'main_image': product.main_image,
        'key_features': extract_key_features(product, 3)
    }


def get_n8n_workflow_url() -> str:
    """
    Retorna URL del workflow n8n para generar JSON.
    
    Returns:
        URL completa del workflow
    """
    return N8N_PRODUCT_JSON_WORKFLOW


# ============================================================================
# PROCESAMIENTO DE MÚLTIPLES PRODUCTOS
# ============================================================================

def parse_multiple_products(json_data: str) -> List[ProductData]:
    """
    Parsea múltiples productos desde JSON.
    
    Args:
        json_data: String con JSON (puede ser array de productos)
        
    Returns:
        Lista de ProductData
    """
    try:
        data = json.loads(json_data)
        
        products = []
        
        if isinstance(data, list):
            for item in data:
                if isinstance(item, dict):
                    # Crear ProductData temporal para validar
                    try:
                        product = ProductData(
                            product_id=item.get('product_id', ''),
                            legacy_id=item.get('legacy_id', ''),
                            title=item.get('title', ''),
                            description=item.get('description', ''),
                            brand_name=item.get('brand_name', ''),
                            family_name=item.get('family_name', ''),
                            attributes=item.get('attributes', {}),
                            images=item.get('images', []),
                            features=item.get('features'),
                            total_comments=item.get('totalComments', 0),
                            advantages=item.get('advantages', ''),
                            disadvantages=item.get('disadvantages', ''),
                            comments=item.get('comments', [])
                        )
                        products.append(product)
                    except Exception as e:
                        logger.warning(f"Error al parsear producto: {e}")
                        continue
        
        return products
        
    except json.JSONDecodeError:
        return []
    except Exception as e:
        logger.error(f"Error al parsear múltiples productos: {e}")
        return []


def format_multiple_products_for_prompt(
    products: List[ProductData],
    include_reviews: bool = False
) -> str:
    """
    Formatea múltiples productos para prompt.
    
    Args:
        products: Lista de productos
        include_reviews: Si incluir reseñas (puede ser muy largo)
        
    Returns:
        String formateado
    """
    if not products:
        return ""
    
    sections = [f"**INFORMACIÓN DE {len(products)} PRODUCTO(S):**\n"]
    
    for i, product in enumerate(products, 1):
        sections.append(f"\n--- PRODUCTO {i} ---")
        sections.append(format_product_for_prompt(product, include_reviews=include_reviews))
    
    return "\n".join(sections)


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    # Versión
    '__version__',
    
    # Data classes
    'ProductData',
    
    # Parseo
    'parse_product_json',
    'validate_product_json',
    'parse_multiple_products',
    
    # Formateo
    'format_product_for_prompt',
    'format_product_brief',
    'format_multiple_products_for_prompt',
    'extract_key_features',
    
    # UI helpers
    'create_product_summary',
    'get_n8n_workflow_url',
    
    # Constantes
    'N8N_PRODUCT_JSON_WORKFLOW',
]
