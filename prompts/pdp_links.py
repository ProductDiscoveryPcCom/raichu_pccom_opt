# -*- coding: utf-8 -*-
"""
PDP Links Module - PcComponentes Content Generator
Versión 2.2.0

Módulo para manejo de enlaces a PDPs con datos de producto de n8n.

=============================================================================
ESQUEMA DE TIPOS DEL JSON DE N8N
=============================================================================

| Campo           | Tipo Python       | Tipo JSON         | Requerido | Descripción                    |
|-----------------|-------------------|-------------------|-----------|--------------------------------|
| product_id      | str               | string (UUID)     | No        | UUID del producto              |
| legacy_id       | str               | string            | No        | ID numérico legacy             |
| title           | str               | string            | SÍ        | Nombre del producto            |
| description     | str               | string (HTML)     | No        | Descripción técnica            |
| brand_name      | str               | string            | No        | Marca del producto             |
| family_name     | str               | string            | No        | Familia/categoría              |
| attributes      | Dict[str,str]     | object            | No        | {clave: valor}                 |
| images          | List[str]         | array[string]     | No        | URLs de imágenes               |
| features        | None/List         | null/array        | No        | Características (ignorado)     |
| totalComments   | int               | number            | No        | Total de opiniones             |
| advantages      | str               | string            | No        | Ventajas (\\n\\n separadas)    |
| disadvantages   | str               | string            | No        | Desventajas (\\n\\n separadas) |
| comments        | List[Dict]        | array[{opinion}]  | No        | Array de opiniones             |

=============================================================================

URL workflow n8n: https://n8n.prod.pccomponentes.com/workflow/jsjhKAdZFBSM5XFV

Autor: PcComponentes - Product Discovery & Content
"""

import streamlit as st
import json
import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)

__version__ = "2.2.0"

N8N_WORKFLOW_URL = "https://n8n.prod.pccomponentes.com/workflow/jsjhKAdZFBSM5XFV"


# ============================================================================
# ENUMS
# ============================================================================

class PDPInputMethod(Enum):
    """Métodos de entrada para datos de PDP."""
    URL = "url"      # No disponible
    ID = "id"        # No disponible
    JSON = "json"    # Disponible


# ============================================================================
# DATACLASS: PDPProductData
# ============================================================================

@dataclass
class PDPProductData:
    """
    Datos de un producto extraídos del JSON de n8n.
    
    Campos para prompts:
    - title, brand_name, family_name: Contexto básico
    - attributes: Especificaciones técnicas
    - total_comments: Credibilidad (N valoraciones)
    - advantages: Ventajas de usuarios → argumentar
    - disadvantages: Desventajas → honestidad (tono marca)
    - user_comments: Opiniones → lenguaje natural
    """
    # Identificadores (string)
    product_id: str = ""
    legacy_id: str = ""
    
    # Info básica (string) - title es REQUERIDO
    title: str = ""
    description: str = ""
    brand_name: str = ""
    family_name: str = ""
    
    # Especificaciones (Dict[str, str])
    attributes: Dict[str, str] = field(default_factory=dict)
    
    # Media (List[str])
    images: List[str] = field(default_factory=list)
    
    # Feedback usuarios
    total_comments: int = 0
    advantages: str = ""        # string con \n\n como separador
    disadvantages: str = ""     # string con \n\n como separador
    user_comments: List[str] = field(default_factory=list)
    
    def has_user_feedback(self) -> bool:
        """Indica si hay datos de feedback de usuarios."""
        return bool(self.advantages or self.disadvantages or self.user_comments)
    
    def get_advantages_list(self, max_items: int = 10) -> List[str]:
        """Parsea ventajas a lista limpia."""
        return self._parse_multiline_text(self.advantages, max_items)
    
    def get_disadvantages_list(self, max_items: int = 8) -> List[str]:
        """Parsea desventajas a lista limpia."""
        return self._parse_multiline_text(self.disadvantages, max_items)
    
    @staticmethod
    def _parse_multiline_text(text: str, max_items: int) -> List[str]:
        """Parsea texto con saltos de línea a lista."""
        if not text:
            return []
        # Normalizar separadores
        normalized = text.replace('\n\n', '\n')
        items = [item.strip() for item in normalized.split('\n')]
        # Filtrar vacíos, muy cortos, y los que dicen "ninguno/nada"
        filtered = []
        skip_words = ['ninguno', 'nada', 'ninguna', 'n/a', '-']
        for item in items:
            if not item or len(item) < 8:
                continue
            if item.lower().strip() in skip_words:
                continue
            filtered.append(item)
        return filtered[:max_items]
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convierte a diccionario para uso en prompts.
        
        Incluye tanto datos raw como procesados.
        """
        adv_list = self.get_advantages_list(12)
        dis_list = self.get_disadvantages_list(8)
        
        return {
            # Identificadores
            'product_id': self.product_id,
            'legacy_id': self.legacy_id,
            
            # Info básica
            'title': self.title,
            'name': self.title,  # alias
            'description': self.description,
            'brand_name': self.brand_name,
            'brand': self.brand_name,  # alias
            'family_name': self.family_name,
            'family': self.family_name,  # alias
            
            # Técnico
            'attributes': self.attributes,
            'images': self.images,
            
            # Feedback raw
            'total_comments': self.total_comments,
            'advantages': self.advantages,
            'disadvantages': self.disadvantages,
            'user_comments': self.user_comments,
            
            # Feedback procesado (listas limpias)
            'advantages_list': adv_list,
            'disadvantages_list': dis_list,
            'top_comments': self.user_comments[:5],
            
            # Contadores
            'advantages_count': len(adv_list),
            'disadvantages_count': len(dis_list),
            'comments_count': len(self.user_comments),
            
            # Flags
            'has_user_feedback': self.has_user_feedback(),
            'has_advantages': bool(adv_list),
            'has_disadvantages': bool(dis_list),
            'has_comments': bool(self.user_comments),
        }


# ============================================================================
# DATACLASS: PDPLinkData
# ============================================================================

@dataclass
class PDPLinkData:
    """Datos de un enlace PDP con información del producto."""
    url: str
    anchor: str
    product_data: Optional[PDPProductData] = None
    input_method: str = "json"
    
    def to_dict(self) -> Dict:
        """Convierte a formato para prompts."""
        return {
            'url': self.url,
            'anchor': self.anchor,
            'type': 'pdp',
            'product_data': self.product_data.to_dict() if self.product_data else None,
            'input_method': self.input_method,
        }


# ============================================================================
# FUNCIONES DE PARSEO
# ============================================================================

def parse_n8n_product_json(json_str: str) -> Tuple[bool, Optional[PDPProductData], str]:
    """
    Parsea el JSON del workflow de n8n.
    
    Args:
        json_str: String JSON pegado por el usuario
        
    Returns:
        Tuple[success: bool, data: PDPProductData | None, error_msg: str]
    """
    if not json_str or not json_str.strip():
        return False, None, "JSON vacío"
    
    try:
        data = json.loads(json_str.strip())
        
        # Si es array, tomar primer elemento
        if isinstance(data, list):
            if len(data) == 0:
                return False, None, "Lista JSON vacía"
            data = data[0]
        
        # Debe ser objeto/dict
        if not isinstance(data, dict):
            return False, None, "El JSON debe ser un objeto o array de objetos"
        
        # ===== EXTRACCIÓN DE CAMPOS =====
        
        # title (REQUERIDO)
        title = _get_str(data, 'title') or _get_str(data, 'name')
        if not title:
            return False, None, "El JSON debe contener 'title' o 'name'"
        
        # Construir objeto con todos los campos
        product = PDPProductData(
            product_id=_get_str(data, 'product_id'),
            legacy_id=_get_str(data, 'legacy_id'),
            title=title,
            description=_get_str(data, 'description'),
            brand_name=_get_str(data, 'brand_name') or _get_str(data, 'brand'),
            family_name=_get_str(data, 'family_name') or _get_str(data, 'family'),
            attributes=_get_attributes(data.get('attributes')),
            images=_get_str_list(data.get('images')),
            total_comments=_get_int(data, 'totalComments'),
            advantages=_get_str(data, 'advantages'),
            disadvantages=_get_str(data, 'disadvantages'),
            user_comments=_get_comments(data.get('comments')),
        )
        
        logger.info(f"Parseado: {title} ({product.brand_name}) - {product.total_comments} opiniones")
        return True, product, ""
        
    except json.JSONDecodeError as e:
        return False, None, f"JSON inválido: {str(e)}"
    except Exception as e:
        logger.error(f"Error parseando JSON: {e}")
        return False, None, f"Error: {str(e)}"


def _get_str(data: Dict, key: str) -> str:
    """Extrae string de forma segura."""
    val = data.get(key)
    if val is None:
        return ""
    return str(val).strip() if not isinstance(val, str) else val.strip()


def _get_int(data: Dict, key: str) -> int:
    """Extrae int de forma segura."""
    val = data.get(key)
    if val is None:
        return 0
    try:
        return int(val)
    except (ValueError, TypeError):
        return 0


def _get_attributes(attrs: Any) -> Dict[str, str]:
    """Extrae atributos (object {string: string})."""
    if not attrs:
        return {}
    
    result = {}
    if isinstance(attrs, dict):
        for k, v in attrs.items():
            if k and v is not None:
                result[str(k)] = str(v)
    elif isinstance(attrs, list):
        # Formato alternativo: [{label, value}]
        for item in attrs:
            if isinstance(item, dict):
                label = item.get('label') or item.get('key')
                value = item.get('value')
                if label and value is not None:
                    result[str(label)] = str(value)
    return result


def _get_str_list(arr: Any) -> List[str]:
    """Extrae lista de strings."""
    if not arr or not isinstance(arr, list):
        return []
    return [str(x).strip() for x in arr if x and isinstance(x, str)]


def _get_comments(comments: Any) -> List[str]:
    """Extrae comentarios (array[{opinion: string}])."""
    if not comments or not isinstance(comments, list):
        return []
    
    result = []
    for item in comments:
        if isinstance(item, dict):
            text = item.get('opinion') or item.get('text') or item.get('content')
            if text and isinstance(text, str) and len(text) >= 15:
                result.append(text.strip())
        elif isinstance(item, str) and len(item) >= 15:
            result.append(item.strip())
    return result


# ============================================================================
# FORMATEAR PARA PROMPTS
# ============================================================================

def format_product_for_prompt(product: PDPProductData) -> str:
    """
    Formatea datos del producto para incluir en prompts.
    
    Genera texto estructurado con:
    - Info básica
    - Especificaciones
    - Ventajas (🟢) para argumentar
    - Desventajas (🟡) para honestidad
    - Opiniones (💬) para lenguaje natural
    """
    lines = []
    
    # Cabecera
    lines.append("=" * 60)
    lines.append("DATOS DEL PRODUCTO (del JSON de n8n)")
    lines.append("=" * 60)
    
    # Info básica
    lines.append(f"\n**Producto:** {product.title}")
    if product.brand_name:
        lines.append(f"**Marca:** {product.brand_name}")
    if product.family_name:
        lines.append(f"**Categoría:** {product.family_name}")
    
    # Especificaciones
    if product.attributes:
        lines.append("\n**📋 ESPECIFICACIONES:**")
        for i, (k, v) in enumerate(product.attributes.items()):
            if i >= 8:
                lines.append(f"  ... (+{len(product.attributes) - 8} más)")
                break
            lines.append(f"  • {k}: {v}")
    
    # Credibilidad
    if product.total_comments > 0:
        lines.append(f"\n**⭐ VALORACIONES:** {product.total_comments} opiniones de compradores")
    
    # Ventajas
    advs = product.get_advantages_list(10)
    if advs:
        lines.append("\n**🟢 LO QUE VALORAN LOS USUARIOS (usa para argumentar):**")
        for adv in advs[:8]:
            lines.append(f"  ✓ {adv}")
    
    # Desventajas
    disadvs = product.get_disadvantages_list(6)
    if disadvs:
        lines.append("\n**🟡 PUNTOS A CONSIDERAR (menciona con honestidad):**")
        for dis in disadvs[:5]:
            lines.append(f"  • {dis}")
    
    # Opiniones
    if product.user_comments:
        lines.append("\n**💬 ASÍ HABLAN LOS USUARIOS (inspírate):**")
        for i, comment in enumerate(product.user_comments[:3]):
            short = comment[:250] + "..." if len(comment) > 250 else comment
            lines.append(f'\n  [{i+1}] "{short}"')
    
    lines.append("\n" + "=" * 60)
    return "\n".join(lines)


# ============================================================================
# UI COMPONENTS
# ============================================================================

def render_pdp_input_with_options(
    key_prefix: str,
    index: int,
    show_delete: bool = True
) -> Tuple[Optional[PDPLinkData], bool]:
    """
    Renderiza input de PDP con selector de método.
    
    Returns:
        Tuple[PDPLinkData | None, should_delete: bool]
    """
    should_delete = False
    
    # Keys
    method_key = f"{key_prefix}_method_{index}"
    json_key = f"{key_prefix}_json_{index}"
    anchor_key = f"{key_prefix}_anchor_{index}"
    
    if method_key not in st.session_state:
        st.session_state[method_key] = "json"
    
    st.markdown(f"##### Enlace PDP #{index + 1}")
    
    col_method, col_del = st.columns([5, 1])
    
    with col_method:
        method = st.radio(
            "Método",
            ["json", "url", "id"],
            format_func=lambda x: {
                "url": "🔴 URL (No disponible)",
                "id": "🔴 ID (No disponible)",
                "json": "🟢 JSON desde n8n"
            }[x],
            index=0,
            key=f"{method_key}_radio",
            horizontal=True,
            label_visibility="collapsed"
        )
    
    with col_del:
        if show_delete:
            if st.button("🗑️", key=f"{key_prefix}_del_{index}"):
                should_delete = True
    
    product_data = None
    
    if method == "json":
        st.info(f"📋 Pega el JSON del [workflow n8n]({N8N_WORKFLOW_URL})")
        
        json_input = st.text_area(
            "JSON del producto",
            key=json_key,
            height=100,
            placeholder='[{"title": "...", "brand_name": "...", ...}]'
        )
        
        if json_input:
            ok, parsed, err = parse_n8n_product_json(json_input)
            if ok and parsed:
                product_data = parsed
                st.success(f"✅ **{parsed.title}** ({parsed.brand_name})")
                
                with st.expander("📦 Datos capturados", expanded=False):
                    c1, c2 = st.columns(2)
                    with c1:
                        st.write(f"**Título:** {parsed.title}")
                        st.write(f"**Marca:** {parsed.brand_name}")
                        st.write(f"**Categoría:** {parsed.family_name}")
                    with c2:
                        st.write(f"**ID:** {parsed.legacy_id}")
                        st.write(f"**Opiniones:** {parsed.total_comments}")
                        st.write(f"**Atributos:** {len(parsed.attributes)}")
                    
                    if parsed.has_user_feedback():
                        st.divider()
                        advs = len(parsed.get_advantages_list())
                        disadvs = len(parsed.get_disadvantages_list())
                        st.write(f"**Feedback:** {advs} ventajas, {disadvs} desventajas, {len(parsed.user_comments)} opiniones")
            else:
                st.error(f"❌ {err}")
    else:
        st.warning("⚠️ Método no disponible. Usa JSON desde n8n.")
    
    # Anchor text
    default_anchor = product_data.title if product_data else ""
    anchor = st.text_input(
        "Texto del enlace (anchor)",
        key=anchor_key,
        placeholder=f"Ej: {default_anchor[:40]}..." if default_anchor else "Texto del enlace"
    )
    
    st.divider()
    
    # Construir resultado
    if product_data:
        url = ""
        if product_data.legacy_id:
            url = f"https://www.pccomponentes.com/producto/{product_data.legacy_id}"
        
        return PDPLinkData(
            url=url,
            anchor=anchor or product_data.title,
            product_data=product_data,
            input_method=method
        ), should_delete
    
    return None, should_delete


def render_pdp_links_section(
    key_prefix: str = "pdp_links",
    label: str = "🛒 Enlaces a PDPs",
    max_links: int = 5,
    expanded: bool = False
) -> List[PDPLinkData]:
    """Renderiza sección completa de enlaces PDP."""
    
    count_key = f"{key_prefix}_count"
    delete_key = f"{key_prefix}_delete_idx"
    
    if count_key not in st.session_state:
        st.session_state[count_key] = 1
    if delete_key not in st.session_state:
        st.session_state[delete_key] = None
    
    # Procesar eliminación pendiente
    if st.session_state[delete_key] is not None:
        idx = st.session_state[delete_key]
        curr = st.session_state[count_key]
        if 0 <= idx < curr:
            # Shift state keys
            for j in range(idx, curr - 1):
                for suf in ['_method_', '_json_', '_anchor_']:
                    nk = f"{key_prefix}{suf}{j+1}"
                    ck = f"{key_prefix}{suf}{j}"
                    if nk in st.session_state:
                        st.session_state[ck] = st.session_state[nk]
            # Delete last
            for suf in ['_method_', '_json_', '_anchor_']:
                lk = f"{key_prefix}{suf}{curr-1}"
                if lk in st.session_state:
                    del st.session_state[lk]
            st.session_state[count_key] = max(1, curr - 1)
        st.session_state[delete_key] = None
        st.rerun()
    
    links = []
    
    with st.expander(label, expanded=expanded):
        st.caption(f"Máximo {max_links} enlaces. [Abrir n8n]({N8N_WORKFLOW_URL})")
        
        for i in range(st.session_state[count_key]):
            pdp, should_del = render_pdp_input_with_options(
                key_prefix, i,
                show_delete=(st.session_state[count_key] > 1)
            )
            
            if should_del:
                st.session_state[delete_key] = i
                st.rerun()
            
            if pdp:
                links.append(pdp)
        
        if st.session_state[count_key] < max_links:
            if st.button("➕ Añadir enlace PDP", key=f"{key_prefix}_add"):
                st.session_state[count_key] += 1
                st.rerun()
        
        if links:
            st.success(f"✅ {len(links)} enlace(s) con datos de producto")
    
    return links


def render_general_links_section(
    key_prefix: str = "general_links",
    label: str = "🔗 Enlaces Generales (PLPs/Blog)",
    max_links: int = 10,
    expanded: bool = False
) -> List[Dict[str, str]]:
    """Renderiza sección de enlaces generales."""
    
    count_key = f"{key_prefix}_count"
    delete_key = f"{key_prefix}_delete_idx"
    
    if count_key not in st.session_state:
        st.session_state[count_key] = 1
    if delete_key not in st.session_state:
        st.session_state[delete_key] = None
    
    # Procesar eliminación
    if st.session_state[delete_key] is not None:
        idx = st.session_state[delete_key]
        curr = st.session_state[count_key]
        if 0 <= idx < curr:
            for j in range(idx, curr - 1):
                for suf in ['_url_', '_anchor_']:
                    nk = f"{key_prefix}{suf}{j+1}"
                    ck = f"{key_prefix}{suf}{j}"
                    if nk in st.session_state:
                        st.session_state[ck] = st.session_state[nk]
            for suf in ['_url_', '_anchor_']:
                lk = f"{key_prefix}{suf}{curr-1}"
                if lk in st.session_state:
                    del st.session_state[lk]
            st.session_state[count_key] = max(1, curr - 1)
        st.session_state[delete_key] = None
        st.rerun()
    
    links = []
    
    with st.expander(label, expanded=expanded):
        st.caption(f"Máximo {max_links} enlaces.")
        
        for i in range(st.session_state[count_key]):
            c1, c2, c3 = st.columns([5, 4, 1])
            
            with c1:
                url = st.text_input(
                    f"URL {i+1}",
                    key=f"{key_prefix}_url_{i}",
                    placeholder="https://...",
                    label_visibility="collapsed"
                )
            with c2:
                anchor = st.text_input(
                    f"Anchor {i+1}",
                    key=f"{key_prefix}_anchor_{i}",
                    placeholder="Texto del enlace",
                    label_visibility="collapsed"
                )
            with c3:
                if st.session_state[count_key] > 1:
                    if st.button("🗑️", key=f"{key_prefix}_del_{i}"):
                        st.session_state[delete_key] = i
                        st.rerun()
            
            if url and url.strip():
                links.append({
                    'url': url.strip(),
                    'anchor': anchor.strip() if anchor else '',
                    'type': 'general'
                })
        
        if st.session_state[count_key] < max_links:
            if st.button("➕ Añadir enlace", key=f"{key_prefix}_add"):
                st.session_state[count_key] += 1
                st.rerun()
        
        if links:
            st.caption(f"📊 {len(links)} enlace(s)")
    
    return links


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    '__version__',
    'N8N_WORKFLOW_URL',
    'PDPInputMethod',
    'PDPProductData',
    'PDPLinkData',
    'parse_n8n_product_json',
    'format_product_for_prompt',
    'render_pdp_input_with_options',
    'render_pdp_links_section',
    'render_general_links_section',
]
