"""
GSC Utils - PcComponentes Content Generator
Versión 4.2.0

Utilidades para Google Search Console (GSC).
Incluye sistema de caché robusto con TTL, invalidación automática y manual,
límite de tamaño, y manejo de datos de GSC.

Este módulo proporciona:
- Sistema de caché con TTL configurable
- Funciones para cargar y procesar datos de GSC
- Análisis de keywords y métricas
- Integración con el flujo de generación de contenido

Autor: PcComponentes - Product Discovery & Content
"""

import os
import csv
import json
import hashlib
import logging
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Callable, TypeVar, Union
from dataclasses import dataclass, field
from functools import wraps
from collections import OrderedDict

# Configurar logging
logger = logging.getLogger(__name__)

# ============================================================================
# IMPORTS CON MANEJO DE ERRORES
# ============================================================================

try:
    import pandas as pd
    _pandas_available = True
except ImportError:
    logger.warning("pandas no disponible - funcionalidad limitada")
    _pandas_available = False

try:
    from config.settings import DATA_DIR, GSC_DATA_FILE
except ImportError:
    DATA_DIR = Path("./data")
    GSC_DATA_FILE = DATA_DIR / "gsc_data.csv"


# ============================================================================
# VERSIÓN Y CONSTANTES
# ============================================================================

__version__ = "4.2.0"

# Configuración de caché por defecto
DEFAULT_CACHE_TTL = 3600  # 1 hora en segundos
DEFAULT_CACHE_MAX_SIZE = 100  # Máximo de entradas en caché
MIN_CACHE_TTL = 60  # Mínimo 1 minuto
MAX_CACHE_TTL = 86400  # Máximo 24 horas

# Configuración de GSC
GSC_DEFAULT_COLUMNS = [
    'query', 'page', 'clicks', 'impressions', 'ctr', 'position'
]
GSC_METRICS = ['clicks', 'impressions', 'ctr', 'position']


# ============================================================================
# EXCEPCIONES PERSONALIZADAS
# ============================================================================

class GSCError(Exception):
    """Excepción base para errores de GSC."""
    
    def __init__(self, message: str, details: Optional[Dict] = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}


class GSCFileError(GSCError):
    """Error al leer archivo de GSC."""
    pass


class GSCParseError(GSCError):
    """Error al parsear datos de GSC."""
    pass


class CacheError(GSCError):
    """Error relacionado con el caché."""
    pass


# ============================================================================
# SISTEMA DE CACHÉ CON TTL
# ============================================================================

@dataclass
class CacheEntry:
    """Entrada individual en el caché."""
    key: str
    value: Any
    created_at: datetime
    expires_at: datetime
    hits: int = 0
    last_accessed: datetime = field(default_factory=datetime.now)
    
    def is_expired(self) -> bool:
        """Verifica si la entrada ha expirado."""
        return datetime.now() > self.expires_at
    
    def time_to_live(self) -> float:
        """Retorna segundos restantes de vida."""
        remaining = (self.expires_at - datetime.now()).total_seconds()
        return max(0, remaining)
    
    def touch(self) -> None:
        """Actualiza tiempo de acceso y contador de hits."""
        self.last_accessed = datetime.now()
        self.hits += 1


class TTLCache:
    """
    Caché con Time-To-Live (TTL) y límite de tamaño.
    
    Características:
    - TTL configurable por entrada o global
    - Límite máximo de entradas (LRU eviction)
    - Invalidación automática de entradas expiradas
    - Invalidación manual por clave o patrón
    - Thread-safe con locks
    - Estadísticas de uso
    
    Example:
        >>> cache = TTLCache(ttl=3600, max_size=100)
        >>> cache.set('key1', 'value1')
        >>> value = cache.get('key1')
        >>> cache.invalidate('key1')
    """
    
    def __init__(
        self,
        ttl: int = DEFAULT_CACHE_TTL,
        max_size: int = DEFAULT_CACHE_MAX_SIZE,
        name: str = "default"
    ):
        """
        Inicializa el caché.
        
        Args:
            ttl: Time-to-live en segundos (default: 3600)
            max_size: Número máximo de entradas (default: 100)
            name: Nombre del caché para logging
        """
        self._ttl = max(MIN_CACHE_TTL, min(ttl, MAX_CACHE_TTL))
        self._max_size = max(1, max_size)
        self._name = name
        self._cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self._lock = threading.RLock()
        
        # Estadísticas
        self._stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0,
            'expirations': 0,
            'invalidations': 0,
        }
        
        logger.info(f"Caché '{name}' inicializado: TTL={self._ttl}s, max_size={self._max_size}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Obtiene un valor del caché.
        
        Args:
            key: Clave a buscar
            default: Valor por defecto si no existe o expiró
            
        Returns:
            Valor almacenado o default
        """
        with self._lock:
            entry = self._cache.get(key)
            
            if entry is None:
                self._stats['misses'] += 1
                return default
            
            if entry.is_expired():
                self._remove_entry(key)
                self._stats['expirations'] += 1
                self._stats['misses'] += 1
                return default
            
            # Mover al final (más reciente) y actualizar stats
            self._cache.move_to_end(key)
            entry.touch()
            self._stats['hits'] += 1
            
            return entry.value
    
    def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None
    ) -> None:
        """
        Almacena un valor en el caché.
        
        Args:
            key: Clave para almacenar
            value: Valor a almacenar
            ttl: TTL específico para esta entrada (opcional)
        """
        with self._lock:
            # Limpiar entradas expiradas periódicamente
            self._cleanup_expired()
            
            # Verificar límite de tamaño
            while len(self._cache) >= self._max_size:
                self._evict_oldest()
            
            # Calcular expiración
            entry_ttl = ttl if ttl is not None else self._ttl
            entry_ttl = max(MIN_CACHE_TTL, min(entry_ttl, MAX_CACHE_TTL))
            
            now = datetime.now()
            expires_at = now + timedelta(seconds=entry_ttl)
            
            # Crear entrada
            entry = CacheEntry(
                key=key,
                value=value,
                created_at=now,
                expires_at=expires_at,
                last_accessed=now
            )
            
            # Almacenar
            self._cache[key] = entry
            self._cache.move_to_end(key)
            
            logger.debug(f"Caché '{self._name}': SET {key} (TTL={entry_ttl}s)")
    
    def invalidate(self, key: str) -> bool:
        """
        Invalida (elimina) una entrada específica.
        
        Args:
            key: Clave a invalidar
            
        Returns:
            True si se eliminó, False si no existía
        """
        with self._lock:
            if key in self._cache:
                self._remove_entry(key)
                self._stats['invalidations'] += 1
                logger.debug(f"Caché '{self._name}': INVALIDATE {key}")
                return True
            return False
    
    def invalidate_pattern(self, pattern: str) -> int:
        """
        Invalida todas las entradas que coincidan con un patrón.
        
        Args:
            pattern: Patrón a buscar (substring)
            
        Returns:
            Número de entradas invalidadas
        """
        with self._lock:
            keys_to_remove = [
                key for key in self._cache.keys()
                if pattern in key
            ]
            
            for key in keys_to_remove:
                self._remove_entry(key)
                self._stats['invalidations'] += 1
            
            if keys_to_remove:
                logger.info(
                    f"Caché '{self._name}': INVALIDATE_PATTERN '{pattern}' "
                    f"({len(keys_to_remove)} entradas)"
                )
            
            return len(keys_to_remove)
    
    def invalidate_all(self) -> int:
        """
        Invalida todas las entradas del caché.
        
        Returns:
            Número de entradas invalidadas
        """
        with self._lock:
            count = len(self._cache)
            self._cache.clear()
            self._stats['invalidations'] += count
            logger.info(f"Caché '{self._name}': INVALIDATE_ALL ({count} entradas)")
            return count
    
    def invalidate_expired(self) -> int:
        """
        Invalida solo las entradas expiradas.
        
        Returns:
            Número de entradas invalidadas
        """
        with self._lock:
            return self._cleanup_expired()
    
    def contains(self, key: str) -> bool:
        """
        Verifica si una clave existe y no ha expirado.
        
        Args:
            key: Clave a verificar
            
        Returns:
            True si existe y es válida
        """
        with self._lock:
            entry = self._cache.get(key)
            if entry is None:
                return False
            if entry.is_expired():
                self._remove_entry(key)
                return False
            return True
    
    def get_ttl(self, key: str) -> Optional[float]:
        """
        Obtiene el TTL restante de una entrada.
        
        Args:
            key: Clave a consultar
            
        Returns:
            Segundos restantes o None si no existe
        """
        with self._lock:
            entry = self._cache.get(key)
            if entry is None or entry.is_expired():
                return None
            return entry.time_to_live()
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas del caché.
        
        Returns:
            Dict con estadísticas de uso
        """
        with self._lock:
            total_requests = self._stats['hits'] + self._stats['misses']
            hit_rate = (
                self._stats['hits'] / total_requests * 100
                if total_requests > 0 else 0
            )
            
            return {
                'name': self._name,
                'size': len(self._cache),
                'max_size': self._max_size,
                'ttl': self._ttl,
                'hits': self._stats['hits'],
                'misses': self._stats['misses'],
                'hit_rate': f"{hit_rate:.1f}%",
                'evictions': self._stats['evictions'],
                'expirations': self._stats['expirations'],
                'invalidations': self._stats['invalidations'],
            }
    
    def _remove_entry(self, key: str) -> None:
        """Elimina una entrada del caché (interno)."""
        if key in self._cache:
            del self._cache[key]
    
    def _evict_oldest(self) -> None:
        """Elimina la entrada más antigua (LRU)."""
        if self._cache:
            oldest_key = next(iter(self._cache))
            self._remove_entry(oldest_key)
            self._stats['evictions'] += 1
            logger.debug(f"Caché '{self._name}': EVICT {oldest_key}")
    
    def _cleanup_expired(self) -> int:
        """Limpia entradas expiradas (interno)."""
        expired_keys = [
            key for key, entry in self._cache.items()
            if entry.is_expired()
        ]
        
        for key in expired_keys:
            self._remove_entry(key)
            self._stats['expirations'] += 1
        
        return len(expired_keys)
    
    def __len__(self) -> int:
        """Retorna número de entradas en caché."""
        return len(self._cache)
    
    def __contains__(self, key: str) -> bool:
        """Permite usar 'in' operator."""
        return self.contains(key)


# ============================================================================
# CACHÉ GLOBAL PARA GSC
# ============================================================================

# Instancia global del caché para datos GSC
_gsc_cache = TTLCache(
    ttl=DEFAULT_CACHE_TTL,
    max_size=DEFAULT_CACHE_MAX_SIZE,
    name="gsc"
)


def get_gsc_cache() -> TTLCache:
    """Obtiene la instancia global del caché GSC."""
    return _gsc_cache


def reset_gsc_cache(
    ttl: Optional[int] = None,
    max_size: Optional[int] = None
) -> TTLCache:
    """
    Resetea el caché GSC con nueva configuración.
    
    Args:
        ttl: Nuevo TTL (opcional)
        max_size: Nuevo tamaño máximo (opcional)
        
    Returns:
        Nueva instancia del caché
    """
    global _gsc_cache
    
    _gsc_cache = TTLCache(
        ttl=ttl or DEFAULT_CACHE_TTL,
        max_size=max_size or DEFAULT_CACHE_MAX_SIZE,
        name="gsc"
    )
    
    return _gsc_cache


# ============================================================================
# DECORADOR DE CACHÉ
# ============================================================================

T = TypeVar('T')


def cached(
    ttl: Optional[int] = None,
    key_prefix: str = "",
    cache_instance: Optional[TTLCache] = None
) -> Callable:
    """
    Decorador para cachear resultados de funciones.
    
    Args:
        ttl: TTL específico (usa el del caché si no se especifica)
        key_prefix: Prefijo para las claves de caché
        cache_instance: Instancia de caché a usar (usa global si no se especifica)
        
    Returns:
        Decorador configurado
        
    Example:
        >>> @cached(ttl=1800, key_prefix="gsc_query")
        ... def get_keywords(url: str) -> List[str]:
        ...     # Lógica costosa
        ...     return keywords
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            cache = cache_instance or _gsc_cache
            
            # Generar clave única basada en argumentos
            key_parts = [key_prefix or func.__name__]
            
            for arg in args:
                key_parts.append(str(arg))
            
            for k, v in sorted(kwargs.items()):
                key_parts.append(f"{k}={v}")
            
            cache_key = hashlib.md5(
                ":".join(key_parts).encode()
            ).hexdigest()
            
            # Intentar obtener del caché
            cached_value = cache.get(cache_key)
            
            if cached_value is not None:
                logger.debug(f"Cache HIT: {func.__name__}")
                return cached_value
            
            # Ejecutar función y cachear resultado
            logger.debug(f"Cache MISS: {func.__name__}")
            result = func(*args, **kwargs)
            
            if result is not None:
                cache.set(cache_key, result, ttl=ttl)
            
            return result
        
        # Añadir método para invalidar caché de esta función
        def invalidate_cache(*args, **kwargs) -> bool:
            cache = cache_instance or _gsc_cache
            
            key_parts = [key_prefix or func.__name__]
            for arg in args:
                key_parts.append(str(arg))
            for k, v in sorted(kwargs.items()):
                key_parts.append(f"{k}={v}")
            
            cache_key = hashlib.md5(
                ":".join(key_parts).encode()
            ).hexdigest()
            
            return cache.invalidate(cache_key)
        
        wrapper.invalidate = invalidate_cache
        wrapper.invalidate_all = lambda: (cache_instance or _gsc_cache).invalidate_pattern(
            key_prefix or func.__name__
        )
        
        return wrapper
    
    return decorator


# ============================================================================
# FUNCIONES DE CARGA DE DATOS GSC
# ============================================================================

@cached(ttl=3600, key_prefix="gsc_file")
def load_gsc_data(
    file_path: Optional[Union[str, Path]] = None,
    encoding: str = 'utf-8'
) -> Optional[Dict[str, Any]]:
    """
    Carga datos de GSC desde un archivo CSV.
    
    Args:
        file_path: Ruta al archivo CSV (usa default si no se especifica)
        encoding: Codificación del archivo
        
    Returns:
        Dict con datos procesados o None si hay error
        
    Raises:
        GSCFileError: Si no se puede leer el archivo
        GSCParseError: Si no se puede parsear el contenido
    """
    file_path = Path(file_path) if file_path else GSC_DATA_FILE
    
    if not file_path.exists():
        logger.warning(f"Archivo GSC no encontrado: {file_path}")
        return None
    
    try:
        if _pandas_available:
            return _load_gsc_with_pandas(file_path, encoding)
        else:
            return _load_gsc_with_csv(file_path, encoding)
            
    except UnicodeDecodeError as e:
        logger.error(f"Error de codificación al leer {file_path}: {e}")
        raise GSCFileError(
            f"Error de codificación en archivo GSC",
            {"file": str(file_path), "encoding": encoding, "error": str(e)}
        )
    
    except PermissionError as e:
        logger.error(f"Sin permisos para leer {file_path}: {e}")
        raise GSCFileError(
            f"Sin permisos para leer archivo GSC",
            {"file": str(file_path), "error": str(e)}
        )
    
    except Exception as e:
        logger.error(f"Error inesperado al cargar GSC: {e}")
        raise GSCFileError(
            f"Error al cargar archivo GSC: {type(e).__name__}",
            {"file": str(file_path), "error": str(e)}
        )


def _load_gsc_with_pandas(
    file_path: Path,
    encoding: str
) -> Dict[str, Any]:
    """Carga GSC usando pandas (más eficiente)."""
    df = pd.read_csv(file_path, encoding=encoding)
    
    # Normalizar nombres de columnas
    df.columns = df.columns.str.lower().str.strip()
    
    # Verificar columnas requeridas
    required = ['query']
    missing = [col for col in required if col not in df.columns]
    
    if missing:
        raise GSCParseError(
            f"Columnas requeridas no encontradas: {missing}",
            {"columns_found": list(df.columns)}
        )
    
    # Procesar métricas numéricas
    for metric in ['clicks', 'impressions', 'position']:
        if metric in df.columns:
            df[metric] = pd.to_numeric(df[metric], errors='coerce').fillna(0)
    
    # CTR especial (puede venir como porcentaje)
    if 'ctr' in df.columns:
        df['ctr'] = df['ctr'].apply(_parse_ctr)
    
    return {
        'data': df.to_dict('records'),
        'columns': list(df.columns),
        'row_count': len(df),
        'file_path': str(file_path),
        'loaded_at': datetime.now().isoformat(),
        'source': 'pandas'
    }


def _load_gsc_with_csv(
    file_path: Path,
    encoding: str
) -> Dict[str, Any]:
    """Carga GSC usando módulo csv estándar."""
    rows = []
    
    with open(file_path, 'r', encoding=encoding) as f:
        reader = csv.DictReader(f)
        
        # Normalizar nombres de columnas
        if reader.fieldnames:
            fieldnames = [col.lower().strip() for col in reader.fieldnames]
        else:
            raise GSCParseError("Archivo CSV sin cabeceras")
        
        for row in reader:
            # Normalizar claves
            normalized_row = {}
            for key, value in row.items():
                norm_key = key.lower().strip()
                
                # Convertir valores numéricos
                if norm_key in ['clicks', 'impressions']:
                    try:
                        normalized_row[norm_key] = int(value) if value else 0
                    except ValueError:
                        normalized_row[norm_key] = 0
                elif norm_key == 'position':
                    try:
                        normalized_row[norm_key] = float(value) if value else 0.0
                    except ValueError:
                        normalized_row[norm_key] = 0.0
                elif norm_key == 'ctr':
                    normalized_row[norm_key] = _parse_ctr(value)
                else:
                    normalized_row[norm_key] = value
                    
            rows.append(normalized_row)
    
    return {
        'data': rows,
        'columns': fieldnames,
        'row_count': len(rows),
        'file_path': str(file_path),
        'loaded_at': datetime.now().isoformat(),
        'source': 'csv'
    }


def _parse_ctr(value: Any) -> float:
    """Parsea valor de CTR (puede venir como %, decimal, etc.)."""
    if value is None or value == '':
        return 0.0
    
    try:
        if isinstance(value, (int, float)):
            # Si es mayor que 1, probablemente es porcentaje
            return value / 100 if value > 1 else value
        
        value_str = str(value).strip()
        
        # Remover símbolo de porcentaje
        if '%' in value_str:
            value_str = value_str.replace('%', '').strip()
            return float(value_str) / 100
        
        value_float = float(value_str)
        return value_float / 100 if value_float > 1 else value_float
        
    except (ValueError, TypeError):
        return 0.0


# ============================================================================
# FUNCIONES DE ANÁLISIS DE DATOS GSC
# ============================================================================

@cached(ttl=1800, key_prefix="gsc_keywords")
def get_keywords_for_url(
    url: str,
    min_clicks: int = 0,
    min_impressions: int = 0,
    limit: int = 50
) -> List[Dict[str, Any]]:
    """
    Obtiene keywords que llevan tráfico a una URL específica.
    
    Args:
        url: URL a analizar
        min_clicks: Mínimo de clicks requerido
        min_impressions: Mínimo de impresiones requerido
        limit: Número máximo de resultados
        
    Returns:
        Lista de keywords con métricas, ordenadas por clicks
    """
    gsc_data = load_gsc_data()
    
    if not gsc_data or not gsc_data.get('data'):
        return []
    
    # Filtrar por URL
    results = []
    
    for row in gsc_data['data']:
        page = row.get('page', '')
        
        # Verificar si la URL coincide
        if url.lower() not in page.lower():
            continue
        
        clicks = row.get('clicks', 0)
        impressions = row.get('impressions', 0)
        
        # Aplicar filtros
        if clicks < min_clicks:
            continue
        if impressions < min_impressions:
            continue
        
        results.append({
            'query': row.get('query', ''),
            'clicks': clicks,
            'impressions': impressions,
            'ctr': row.get('ctr', 0),
            'position': row.get('position', 0),
        })
    
    # Ordenar por clicks descendente
    results.sort(key=lambda x: x['clicks'], reverse=True)
    
    return results[:limit]


@cached(ttl=1800, key_prefix="gsc_top")
def get_top_keywords(
    limit: int = 100,
    min_clicks: int = 1
) -> List[Dict[str, Any]]:
    """
    Obtiene las keywords con más clicks.
    
    Args:
        limit: Número máximo de resultados
        min_clicks: Mínimo de clicks requerido
        
    Returns:
        Lista de keywords ordenadas por clicks
    """
    gsc_data = load_gsc_data()
    
    if not gsc_data or not gsc_data.get('data'):
        return []
    
    # Filtrar y agregar por query
    query_stats: Dict[str, Dict] = {}
    
    for row in gsc_data['data']:
        query = row.get('query', '').strip().lower()
        
        if not query:
            continue
        
        if query not in query_stats:
            query_stats[query] = {
                'query': row.get('query', ''),
                'clicks': 0,
                'impressions': 0,
                'ctr_sum': 0,
                'position_sum': 0,
                'count': 0
            }
        
        stats = query_stats[query]
        stats['clicks'] += row.get('clicks', 0)
        stats['impressions'] += row.get('impressions', 0)
        stats['ctr_sum'] += row.get('ctr', 0)
        stats['position_sum'] += row.get('position', 0)
        stats['count'] += 1
    
    # Calcular promedios y filtrar
    results = []
    
    for query, stats in query_stats.items():
        if stats['clicks'] < min_clicks:
            continue
        
        results.append({
            'query': stats['query'],
            'clicks': stats['clicks'],
            'impressions': stats['impressions'],
            'ctr': stats['ctr_sum'] / stats['count'] if stats['count'] > 0 else 0,
            'position': stats['position_sum'] / stats['count'] if stats['count'] > 0 else 0,
        })
    
    # Ordenar por clicks
    results.sort(key=lambda x: x['clicks'], reverse=True)
    
    return results[:limit]


@cached(ttl=1800, key_prefix="gsc_related")
def get_related_keywords(
    keyword: str,
    limit: int = 20
) -> List[Dict[str, Any]]:
    """
    Encuentra keywords relacionadas con una keyword dada.
    
    Args:
        keyword: Keyword base para buscar relacionadas
        limit: Número máximo de resultados
        
    Returns:
        Lista de keywords relacionadas
    """
    gsc_data = load_gsc_data()
    
    if not gsc_data or not gsc_data.get('data'):
        return []
    
    keyword_lower = keyword.lower().strip()
    keyword_words = set(keyword_lower.split())
    
    results = []
    seen_queries = set()
    
    for row in gsc_data['data']:
        query = row.get('query', '').strip()
        query_lower = query.lower()
        
        # Evitar duplicados
        if query_lower in seen_queries:
            continue
        
        # Evitar la misma keyword
        if query_lower == keyword_lower:
            continue
        
        # Verificar relación (contiene la keyword o palabras comunes)
        query_words = set(query_lower.split())
        common_words = keyword_words.intersection(query_words)
        
        if keyword_lower in query_lower or len(common_words) >= 1:
            results.append({
                'query': query,
                'clicks': row.get('clicks', 0),
                'impressions': row.get('impressions', 0),
                'ctr': row.get('ctr', 0),
                'position': row.get('position', 0),
                'relevance': len(common_words) / len(keyword_words) if keyword_words else 0
            })
            seen_queries.add(query_lower)
    
    # Ordenar por relevancia y clicks
    results.sort(key=lambda x: (x['relevance'], x['clicks']), reverse=True)
    
    return results[:limit]


@cached(ttl=3600, key_prefix="gsc_summary")
def get_gsc_summary() -> Dict[str, Any]:
    """
    Obtiene un resumen de los datos de GSC.
    
    Returns:
        Dict con estadísticas resumidas
    """
    gsc_data = load_gsc_data()
    
    if not gsc_data or not gsc_data.get('data'):
        return {
            'available': False,
            'error': 'No hay datos de GSC disponibles'
        }
    
    data = gsc_data['data']
    
    total_clicks = sum(row.get('clicks', 0) for row in data)
    total_impressions = sum(row.get('impressions', 0) for row in data)
    unique_queries = len(set(row.get('query', '').lower() for row in data if row.get('query')))
    unique_pages = len(set(row.get('page', '').lower() for row in data if row.get('page')))
    
    avg_position = (
        sum(row.get('position', 0) for row in data) / len(data)
        if data else 0
    )
    
    avg_ctr = total_clicks / total_impressions if total_impressions > 0 else 0
    
    return {
        'available': True,
        'total_rows': len(data),
        'unique_queries': unique_queries,
        'unique_pages': unique_pages,
        'total_clicks': total_clicks,
        'total_impressions': total_impressions,
        'avg_position': round(avg_position, 2),
        'avg_ctr': round(avg_ctr * 100, 2),
        'file_path': gsc_data.get('file_path'),
        'loaded_at': gsc_data.get('loaded_at'),
    }


# ============================================================================
# FUNCIONES DE INVALIDACIÓN ESPECÍFICAS
# ============================================================================

def invalidate_gsc_cache() -> int:
    """
    Invalida todo el caché de GSC.
    
    Returns:
        Número de entradas invalidadas
    """
    return _gsc_cache.invalidate_all()


def invalidate_url_cache(url: str) -> int:
    """
    Invalida caché relacionado con una URL específica.
    
    Args:
        url: URL para invalidar
        
    Returns:
        Número de entradas invalidadas
    """
    # Generar hash de la URL para buscar en caché
    url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
    return _gsc_cache.invalidate_pattern(url_hash)


def invalidate_keyword_cache(keyword: str) -> int:
    """
    Invalida caché relacionado con una keyword específica.
    
    Args:
        keyword: Keyword para invalidar
        
    Returns:
        Número de entradas invalidadas
    """
    keyword_hash = hashlib.md5(keyword.encode()).hexdigest()[:8]
    return _gsc_cache.invalidate_pattern(keyword_hash)


def refresh_gsc_data() -> Optional[Dict[str, Any]]:
    """
    Fuerza recarga de datos GSC invalidando caché.
    
    Returns:
        Datos frescos de GSC
    """
    # Invalidar caché de archivo
    _gsc_cache.invalidate_pattern("gsc_file")
    
    # Recargar
    return load_gsc_data()


# ============================================================================
# FUNCIONES DE UTILIDAD
# ============================================================================

def is_gsc_available() -> bool:
    """
    Verifica si hay datos de GSC disponibles.
    
    Returns:
        True si hay datos disponibles
    """
    file_path = GSC_DATA_FILE
    return file_path.exists() and file_path.stat().st_size > 0


def get_cache_stats() -> Dict[str, Any]:
    """
    Obtiene estadísticas del caché GSC.
    
    Returns:
        Dict con estadísticas
    """
    return _gsc_cache.get_stats()


def format_gsc_for_prompt(
    keywords: List[Dict[str, Any]],
    max_keywords: int = 10
) -> str:
    """
    Formatea keywords de GSC para incluir en un prompt.
    
    Args:
        keywords: Lista de keywords con métricas
        max_keywords: Máximo de keywords a incluir
        
    Returns:
        String formateado para prompt
    """
    if not keywords:
        return "No hay datos de GSC disponibles."
    
    lines = ["Keywords de Google Search Console:"]
    
    for i, kw in enumerate(keywords[:max_keywords], 1):
        query = kw.get('query', '')
        clicks = kw.get('clicks', 0)
        impressions = kw.get('impressions', 0)
        position = kw.get('position', 0)
        
        lines.append(
            f"{i}. \"{query}\" - "
            f"Clicks: {clicks}, Impresiones: {impressions}, "
            f"Posición: {position:.1f}"
        )
    
    return "\n".join(lines)


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    # Versión
    '__version__',
    
    # Excepciones
    'GSCError',
    'GSCFileError',
    'GSCParseError',
    'CacheError',
    
    # Clases
    'CacheEntry',
    'TTLCache',
    
    # Caché global
    'get_gsc_cache',
    'reset_gsc_cache',
    
    # Decorador
    'cached',
    
    # Carga de datos
    'load_gsc_data',
    
    # Análisis
    'get_keywords_for_url',
    'get_top_keywords',
    'get_related_keywords',
    'get_gsc_summary',
    
    # Invalidación
    'invalidate_gsc_cache',
    'invalidate_url_cache',
    'invalidate_keyword_cache',
    'refresh_gsc_data',
    
    # Utilidades
    'is_gsc_available',
    'get_cache_stats',
    'format_gsc_for_prompt',
    
    # Constantes
    'DEFAULT_CACHE_TTL',
    'DEFAULT_CACHE_MAX_SIZE',
]
