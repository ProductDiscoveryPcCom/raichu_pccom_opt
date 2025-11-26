"""
Content Generator - PcComponentes Content Generator
Versión 4.2.0

Módulo de generación de contenido usando la API de Claude (Anthropic).
Incluye manejo robusto de errores, reintentos con backoff exponencial,
y validación exhaustiva de respuestas.

Este módulo proporciona:
- generate_content(): Función principal de generación
- generate_with_stages(): Generación en 3 etapas
- call_claude_api(): Llamada directa a la API con reintentos
- Manejo específico de errores de Anthropic
- Validación y extracción de contenido HTML

Autor: PcComponentes - Product Discovery & Content
"""

import re
import time
import logging
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass
from enum import Enum

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# IMPORTS DE ANTHROPIC CON MANEJO DE ERRORES
# ============================================================================

try:
    import anthropic
    from anthropic import (
        Anthropic,
        APIError,
        APIConnectionError,
        RateLimitError,
        APIStatusError,
        AuthenticationError,
        BadRequestError,
        PermissionDeniedError,
        NotFoundError,
        UnprocessableEntityError,
        InternalServerError,
    )
    _anthropic_available = True
except ImportError as e:
    logger.error(f"No se pudo importar anthropic: {e}")
    _anthropic_available = False
    
    # Definir clases placeholder para evitar errores de importación
    class APIError(Exception):
        pass
    
    class APIConnectionError(Exception):
        pass
    
    class RateLimitError(Exception):
        pass
    
    class APIStatusError(Exception):
        pass
    
    class AuthenticationError(Exception):
        pass
    
    class BadRequestError(Exception):
        pass
    
    class PermissionDeniedError(Exception):
        pass
    
    class NotFoundError(Exception):
        pass
    
    class UnprocessableEntityError(Exception):
        pass
    
    class InternalServerError(Exception):
        pass

# Importar configuración
try:
    from config.settings import (
        CLAUDE_API_KEY,
        DEFAULT_MODEL,
        MAX_TOKENS,
        DEFAULT_TEMPERATURE,
        API_MAX_RETRIES,
        API_RETRY_DELAY,
    )
except ImportError:
    import os
    CLAUDE_API_KEY = os.getenv('CLAUDE_API_KEY', '')
    DEFAULT_MODEL = 'claude-sonnet-4-20250514'
    MAX_TOKENS = 16000
    DEFAULT_TEMPERATURE = 0.7
    API_MAX_RETRIES = 3
    API_RETRY_DELAY = 1.0


# ============================================================================
# VERSIÓN Y CONSTANTES
# ============================================================================

__version__ = "4.2.0"

# Modelos disponibles
AVAILABLE_MODELS = {
    'claude-sonnet-4-20250514': 'Claude Sonnet 4',
    'claude-opus-4-20250514': 'Claude Opus 4',
    'claude-3-5-sonnet-20241022': 'Claude 3.5 Sonnet',
    'claude-3-opus-20240229': 'Claude 3 Opus',
    'claude-3-haiku-20240307': 'Claude 3 Haiku',
}

# Configuración de reintentos
DEFAULT_MAX_RETRIES = 3
DEFAULT_RETRY_DELAY = 1.0
MAX_RETRY_DELAY = 60.0
BACKOFF_MULTIPLIER = 2.0

# Límites de tokens por modelo (aproximados)
MODEL_TOKEN_LIMITS = {
    'claude-sonnet-4-20250514': 200000,
    'claude-opus-4-20250514': 200000,
    'claude-3-5-sonnet-20241022': 200000,
    'claude-3-opus-20240229': 200000,
    'claude-3-haiku-20240307': 200000,
}


# ============================================================================
# EXCEPCIONES PERSONALIZADAS
# ============================================================================

class GenerationError(Exception):
    """Excepción base para errores de generación."""
    
    def __init__(self, message: str, details: Optional[Dict] = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}
    
    def __str__(self):
        if self.details:
            return f"{self.message} | Detalles: {self.details}"
        return self.message


class TokenLimitError(GenerationError):
    """Error cuando se excede el límite de tokens."""
    pass


class APIKeyError(GenerationError):
    """Error relacionado con la API key."""
    pass


class ContentValidationError(GenerationError):
    """Error en la validación del contenido generado."""
    pass


class RetryExhaustedError(GenerationError):
    """Error cuando se agotan los reintentos."""
    pass


# ============================================================================
# ENUMS Y DATA CLASSES
# ============================================================================

class GenerationStage(Enum):
    """Etapas del proceso de generación."""
    DRAFT = 1
    ANALYSIS = 2
    FINAL = 3


@dataclass
class GenerationResult:
    """Resultado de una generación."""
    success: bool
    content: str
    stage: int
    model: str
    tokens_used: int
    generation_time: float
    error: Optional[str] = None
    metadata: Optional[Dict] = None


@dataclass
class APIResponse:
    """Respuesta parseada de la API."""
    content: str
    input_tokens: int
    output_tokens: int
    total_tokens: int
    model: str
    stop_reason: str


# ============================================================================
# CLIENTE DE ANTHROPIC (SINGLETON)
# ============================================================================

_client: Optional[Any] = None


def get_client() -> Any:
    """
    Obtiene el cliente de Anthropic (patrón singleton).
    
    Returns:
        Anthropic: Cliente configurado
        
    Raises:
        APIKeyError: Si la API key no está configurada
        ImportError: Si anthropic no está disponible
    """
    global _client
    
    if not _anthropic_available:
        raise ImportError(
            "El módulo 'anthropic' no está instalado. "
            "Instálalo con: pip install anthropic"
        )
    
    if _client is None:
        if not CLAUDE_API_KEY:
            raise APIKeyError(
                "CLAUDE_API_KEY no está configurada",
                {"hint": "Añade CLAUDE_API_KEY al archivo .env"}
            )
        
        if not CLAUDE_API_KEY.startswith('sk-ant-'):
            raise APIKeyError(
                "CLAUDE_API_KEY tiene formato inválido",
                {"hint": "La API key debe empezar con 'sk-ant-'"}
            )
        
        _client = Anthropic(api_key=CLAUDE_API_KEY)
        logger.info("Cliente de Anthropic inicializado correctamente")
    
    return _client


def reset_client() -> None:
    """Resetea el cliente (útil para tests o cambio de API key)."""
    global _client
    _client = None


# ============================================================================
# FUNCIÓN PRINCIPAL: LLAMADA A LA API CON REINTENTOS
# ============================================================================

def call_claude_api(
    prompt: str,
    model: str = DEFAULT_MODEL,
    max_tokens: int = MAX_TOKENS,
    temperature: float = DEFAULT_TEMPERATURE,
    system_prompt: Optional[str] = None,
    max_retries: int = DEFAULT_MAX_RETRIES,
    retry_delay: float = DEFAULT_RETRY_DELAY,
) -> APIResponse:
    """
    Llama a la API de Claude con manejo robusto de errores y reintentos.
    
    Esta función implementa:
    - Reintentos con backoff exponencial
    - Manejo específico de cada tipo de error de Anthropic
    - Validación de la respuesta antes de retornar
    - Logging detallado de errores y reintentos
    
    Args:
        prompt: El prompt a enviar a Claude
        model: Modelo a usar (default: claude-sonnet-4-20250514)
        max_tokens: Máximo de tokens en la respuesta
        temperature: Temperatura de generación (0.0-1.0)
        system_prompt: Prompt de sistema opcional
        max_retries: Número máximo de reintentos
        retry_delay: Delay inicial entre reintentos (segundos)
        
    Returns:
        APIResponse: Respuesta parseada con contenido y metadatos
        
    Raises:
        APIKeyError: Si hay problemas con la API key
        TokenLimitError: Si se excede el límite de tokens
        RetryExhaustedError: Si se agotan los reintentos
        GenerationError: Para otros errores de generación
        
    Example:
        >>> response = call_claude_api(
        ...     prompt="Genera un artículo sobre gaming",
        ...     model="claude-sonnet-4-20250514",
        ...     max_tokens=8000
        ... )
        >>> print(response.content[:100])
    """
    client = get_client()
    
    # Construir mensajes
    messages = [{"role": "user", "content": prompt}]
    
    # Parámetros de la llamada
    api_params = {
        "model": model,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "messages": messages,
    }
    
    # Añadir system prompt si existe
    if system_prompt:
        api_params["system"] = system_prompt
    
    # Variables para reintentos
    last_error = None
    current_delay = retry_delay
    
    for attempt in range(1, max_retries + 1):
        try:
            logger.info(f"Llamada a API (intento {attempt}/{max_retries})")
            
            # Llamada a la API
            response = client.messages.create(**api_params)
            
            # VALIDACIÓN CRÍTICA: Verificar que la respuesta tiene contenido
            if not response:
                raise GenerationError(
                    "La API retornó una respuesta vacía",
                    {"attempt": attempt}
                )
            
            if not hasattr(response, 'content'):
                raise GenerationError(
                    "La respuesta no tiene atributo 'content'",
                    {"response_type": type(response).__name__, "attempt": attempt}
                )
            
            if not response.content:
                raise GenerationError(
                    "response.content está vacío",
                    {"attempt": attempt, "stop_reason": getattr(response, 'stop_reason', 'unknown')}
                )
            
            if len(response.content) == 0:
                raise GenerationError(
                    "response.content es una lista vacía",
                    {"attempt": attempt}
                )
            
            # Verificar que el primer elemento tiene 'text'
            first_content = response.content[0]
            
            if not hasattr(first_content, 'text'):
                raise GenerationError(
                    "El contenido de la respuesta no tiene atributo 'text'",
                    {"content_type": type(first_content).__name__, "attempt": attempt}
                )
            
            content_text = first_content.text
            
            if not content_text or not content_text.strip():
                raise GenerationError(
                    "El texto de la respuesta está vacío",
                    {"attempt": attempt, "stop_reason": getattr(response, 'stop_reason', 'unknown')}
                )
            
            # Extraer información de uso de tokens
            usage = getattr(response, 'usage', None)
            input_tokens = getattr(usage, 'input_tokens', 0) if usage else 0
            output_tokens = getattr(usage, 'output_tokens', 0) if usage else 0
            
            logger.info(
                f"Respuesta recibida: {output_tokens} tokens generados, "
                f"stop_reason: {getattr(response, 'stop_reason', 'unknown')}"
            )
            
            # Construir y retornar respuesta
            return APIResponse(
                content=content_text,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                total_tokens=input_tokens + output_tokens,
                model=getattr(response, 'model', model),
                stop_reason=getattr(response, 'stop_reason', 'unknown'),
            )
        
        # ================================================================
        # MANEJO ESPECÍFICO DE ERRORES DE ANTHROPIC
        # ================================================================
        
        except AuthenticationError as e:
            # Error de autenticación - NO reintentar
            logger.error(f"Error de autenticación: {e}")
            raise APIKeyError(
                "Error de autenticación con la API de Anthropic",
                {
                    "error": str(e),
                    "hint": "Verifica que CLAUDE_API_KEY es válida y tiene permisos"
                }
            )
        
        except PermissionDeniedError as e:
            # Permiso denegado - NO reintentar
            logger.error(f"Permiso denegado: {e}")
            raise APIKeyError(
                "Permiso denegado por la API de Anthropic",
                {
                    "error": str(e),
                    "hint": "Tu API key no tiene permisos para este modelo o acción"
                }
            )
        
        except RateLimitError as e:
            # Rate limit - reintentar con backoff
            logger.warning(f"Rate limit alcanzado (intento {attempt}): {e}")
            last_error = e
            
            if attempt < max_retries:
                # Extraer tiempo de espera sugerido si está disponible
                retry_after = _extract_retry_after(e)
                wait_time = retry_after if retry_after else current_delay
                
                logger.info(f"Esperando {wait_time:.1f}s antes de reintentar...")
                time.sleep(wait_time)
                current_delay = min(current_delay * BACKOFF_MULTIPLIER, MAX_RETRY_DELAY)
                continue
            else:
                raise RetryExhaustedError(
                    f"Rate limit: reintentos agotados después de {max_retries} intentos",
                    {"last_error": str(e), "suggestion": "Espera unos minutos antes de reintentar"}
                )
        
        except BadRequestError as e:
            # Request inválido - NO reintentar (error del cliente)
            logger.error(f"Bad request: {e}")
            
            # Verificar si es error de tokens
            error_str = str(e).lower()
            if 'token' in error_str or 'context' in error_str or 'length' in error_str:
                raise TokenLimitError(
                    "El prompt excede el límite de tokens del modelo",
                    {
                        "error": str(e),
                        "model": model,
                        "hint": "Reduce la longitud del prompt o usa un modelo con mayor contexto"
                    }
                )
            
            raise GenerationError(
                "Request inválido a la API de Anthropic",
                {"error": str(e), "hint": "Revisa el formato del prompt y parámetros"}
            )
        
        except NotFoundError as e:
            # Recurso no encontrado (modelo inválido) - NO reintentar
            logger.error(f"Recurso no encontrado: {e}")
            raise GenerationError(
                f"Modelo '{model}' no encontrado o no disponible",
                {
                    "error": str(e),
                    "model": model,
                    "available_models": list(AVAILABLE_MODELS.keys())
                }
            )
        
        except UnprocessableEntityError as e:
            # Entidad no procesable - NO reintentar
            logger.error(f"Entidad no procesable: {e}")
            raise GenerationError(
                "La API no pudo procesar la solicitud",
                {"error": str(e)}
            )
        
        except InternalServerError as e:
            # Error interno del servidor - reintentar
            logger.warning(f"Error interno del servidor (intento {attempt}): {e}")
            last_error = e
            
            if attempt < max_retries:
                logger.info(f"Esperando {current_delay:.1f}s antes de reintentar...")
                time.sleep(current_delay)
                current_delay = min(current_delay * BACKOFF_MULTIPLIER, MAX_RETRY_DELAY)
                continue
            else:
                raise RetryExhaustedError(
                    f"Error del servidor: reintentos agotados después de {max_retries} intentos",
                    {"last_error": str(e)}
                )
        
        except APIConnectionError as e:
            # Error de conexión - reintentar
            logger.warning(f"Error de conexión (intento {attempt}): {e}")
            last_error = e
            
            if attempt < max_retries:
                logger.info(f"Esperando {current_delay:.1f}s antes de reintentar...")
                time.sleep(current_delay)
                current_delay = min(current_delay * BACKOFF_MULTIPLIER, MAX_RETRY_DELAY)
                continue
            else:
                raise RetryExhaustedError(
                    f"Error de conexión: reintentos agotados después de {max_retries} intentos",
                    {
                        "last_error": str(e),
                        "hint": "Verifica tu conexión a internet"
                    }
                )
        
        except APIStatusError as e:
            # Otros errores de estado HTTP
            logger.warning(f"Error de estado HTTP (intento {attempt}): {e}")
            status_code = getattr(e, 'status_code', None)
            
            # Errores 5xx son del servidor - reintentar
            if status_code and status_code >= 500:
                last_error = e
                if attempt < max_retries:
                    time.sleep(current_delay)
                    current_delay = min(current_delay * BACKOFF_MULTIPLIER, MAX_RETRY_DELAY)
                    continue
            
            # Errores 4xx son del cliente - NO reintentar
            raise GenerationError(
                f"Error de API (HTTP {status_code})",
                {"error": str(e), "status_code": status_code}
            )
        
        except APIError as e:
            # Error genérico de API - reintentar si es posible
            logger.warning(f"Error de API genérico (intento {attempt}): {e}")
            last_error = e
            
            if attempt < max_retries:
                time.sleep(current_delay)
                current_delay = min(current_delay * BACKOFF_MULTIPLIER, MAX_RETRY_DELAY)
                continue
            else:
                raise RetryExhaustedError(
                    f"Error de API: reintentos agotados después de {max_retries} intentos",
                    {"last_error": str(e)}
                )
        
        except GenerationError:
            # Re-lanzar nuestras excepciones personalizadas
            raise
        
        except Exception as e:
            # Error inesperado
            logger.error(f"Error inesperado: {type(e).__name__}: {e}")
            raise GenerationError(
                f"Error inesperado durante la generación: {type(e).__name__}",
                {"error": str(e), "type": type(e).__name__}
            )
    
    # Si llegamos aquí, se agotaron los reintentos
    raise RetryExhaustedError(
        f"Reintentos agotados después de {max_retries} intentos",
        {"last_error": str(last_error) if last_error else "Unknown"}
    )


def _extract_retry_after(error: Exception) -> Optional[float]:
    """
    Intenta extraer el tiempo de espera sugerido de un error de rate limit.
    
    Args:
        error: La excepción de rate limit
        
    Returns:
        float: Segundos a esperar, o None si no se puede determinar
    """
    try:
        # Intentar obtener de headers si están disponibles
        if hasattr(error, 'response') and hasattr(error.response, 'headers'):
            retry_after = error.response.headers.get('retry-after')
            if retry_after:
                return float(retry_after)
        
        # Intentar parsear del mensaje de error
        error_str = str(error)
        import re
        match = re.search(r'(\d+(?:\.\d+)?)\s*(?:seconds?|s)', error_str.lower())
        if match:
            return float(match.group(1))
        
    except Exception:
        pass
    
    return None


# ============================================================================
# FUNCIONES DE GENERACIÓN DE CONTENIDO
# ============================================================================

def generate_content(
    prompt: str,
    model: str = DEFAULT_MODEL,
    max_tokens: int = MAX_TOKENS,
    temperature: float = DEFAULT_TEMPERATURE,
    system_prompt: Optional[str] = None,
) -> GenerationResult:
    """
    Genera contenido usando Claude API.
    
    Función de alto nivel que wrappea call_claude_api y retorna
    un GenerationResult con toda la información de la generación.
    
    Args:
        prompt: El prompt para generar contenido
        model: Modelo de Claude a usar
        max_tokens: Máximo de tokens en la respuesta
        temperature: Temperatura de generación
        system_prompt: Prompt de sistema opcional
        
    Returns:
        GenerationResult: Resultado con contenido y metadatos
        
    Example:
        >>> result = generate_content(
        ...     prompt="Escribe sobre tarjetas gráficas",
        ...     model="claude-sonnet-4-20250514"
        ... )
        >>> if result.success:
        ...     print(result.content)
    """
    start_time = time.time()
    
    try:
        response = call_claude_api(
            prompt=prompt,
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            system_prompt=system_prompt,
        )
        
        generation_time = time.time() - start_time
        
        return GenerationResult(
            success=True,
            content=response.content,
            stage=1,
            model=response.model,
            tokens_used=response.total_tokens,
            generation_time=generation_time,
            metadata={
                "input_tokens": response.input_tokens,
                "output_tokens": response.output_tokens,
                "stop_reason": response.stop_reason,
            }
        )
    
    except GenerationError as e:
        generation_time = time.time() - start_time
        logger.error(f"Error de generación: {e}")
        
        return GenerationResult(
            success=False,
            content="",
            stage=1,
            model=model,
            tokens_used=0,
            generation_time=generation_time,
            error=str(e),
            metadata=e.details if hasattr(e, 'details') else {}
        )
    
    except Exception as e:
        generation_time = time.time() - start_time
        logger.error(f"Error inesperado: {e}")
        
        return GenerationResult(
            success=False,
            content="",
            stage=1,
            model=model,
            tokens_used=0,
            generation_time=generation_time,
            error=f"Error inesperado: {str(e)}",
        )


def generate_with_stages(
    stage1_prompt: str,
    stage2_prompt_builder: callable,
    stage3_prompt_builder: callable,
    model: str = DEFAULT_MODEL,
    max_tokens: int = MAX_TOKENS,
    temperature: float = DEFAULT_TEMPERATURE,
    system_prompt: Optional[str] = None,
    on_stage_complete: Optional[callable] = None,
) -> Tuple[GenerationResult, GenerationResult, GenerationResult]:
    """
    Genera contenido en 3 etapas (borrador, análisis, final).
    
    Este es el flujo principal de generación del Content Generator:
    1. Etapa 1: Genera el borrador inicial
    2. Etapa 2: Analiza y critica el borrador
    3. Etapa 3: Genera la versión final con correcciones
    
    Args:
        stage1_prompt: Prompt para la etapa 1 (borrador)
        stage2_prompt_builder: Función que recibe el borrador y retorna el prompt para análisis
        stage3_prompt_builder: Función que recibe borrador y análisis, retorna prompt final
        model: Modelo de Claude a usar
        max_tokens: Máximo de tokens por etapa
        temperature: Temperatura de generación
        system_prompt: Prompt de sistema opcional
        on_stage_complete: Callback opcional llamado al completar cada etapa
        
    Returns:
        Tuple[GenerationResult, GenerationResult, GenerationResult]:
            Resultados de las 3 etapas
            
    Example:
        >>> def build_stage2(draft):
        ...     return f"Analiza este borrador: {draft}"
        >>> def build_stage3(draft, analysis):
        ...     return f"Corrige: {draft}\\nSegún: {analysis}"
        >>> r1, r2, r3 = generate_with_stages(
        ...     stage1_prompt="Genera artículo...",
        ...     stage2_prompt_builder=build_stage2,
        ...     stage3_prompt_builder=build_stage3
        ... )
    """
    results = []
    
    # ============== ETAPA 1: BORRADOR ==============
    logger.info("=== ETAPA 1: Generando borrador ===")
    
    result1 = generate_content(
        prompt=stage1_prompt,
        model=model,
        max_tokens=max_tokens,
        temperature=temperature,
        system_prompt=system_prompt,
    )
    result1 = GenerationResult(
        success=result1.success,
        content=result1.content,
        stage=1,
        model=result1.model,
        tokens_used=result1.tokens_used,
        generation_time=result1.generation_time,
        error=result1.error,
        metadata=result1.metadata,
    )
    results.append(result1)
    
    if on_stage_complete:
        on_stage_complete(1, result1)
    
    if not result1.success:
        logger.error("Etapa 1 falló, abortando")
        # Retornar resultados vacíos para etapas 2 y 3
        empty_result = GenerationResult(
            success=False, content="", stage=2, model=model,
            tokens_used=0, generation_time=0, error="Etapa previa falló"
        )
        return result1, empty_result, GenerationResult(**{**empty_result.__dict__, 'stage': 3})
    
    # ============== ETAPA 2: ANÁLISIS ==============
    logger.info("=== ETAPA 2: Analizando borrador ===")
    
    stage2_prompt = stage2_prompt_builder(result1.content)
    
    result2 = generate_content(
        prompt=stage2_prompt,
        model=model,
        max_tokens=max_tokens,
        temperature=0.3,  # Menos creatividad para análisis
        system_prompt=system_prompt,
    )
    result2 = GenerationResult(
        success=result2.success,
        content=result2.content,
        stage=2,
        model=result2.model,
        tokens_used=result2.tokens_used,
        generation_time=result2.generation_time,
        error=result2.error,
        metadata=result2.metadata,
    )
    results.append(result2)
    
    if on_stage_complete:
        on_stage_complete(2, result2)
    
    if not result2.success:
        logger.error("Etapa 2 falló, abortando")
        empty_result = GenerationResult(
            success=False, content="", stage=3, model=model,
            tokens_used=0, generation_time=0, error="Etapa previa falló"
        )
        return result1, result2, empty_result
    
    # ============== ETAPA 3: VERSIÓN FINAL ==============
    logger.info("=== ETAPA 3: Generando versión final ===")
    
    stage3_prompt = stage3_prompt_builder(result1.content, result2.content)
    
    result3 = generate_content(
        prompt=stage3_prompt,
        model=model,
        max_tokens=max_tokens,
        temperature=temperature,
        system_prompt=system_prompt,
    )
    result3 = GenerationResult(
        success=result3.success,
        content=result3.content,
        stage=3,
        model=result3.model,
        tokens_used=result3.tokens_used,
        generation_time=result3.generation_time,
        error=result3.error,
        metadata=result3.metadata,
    )
    
    if on_stage_complete:
        on_stage_complete(3, result3)
    
    logger.info("=== Generación en 3 etapas completada ===")
    
    return result1, result2, result3


# ============================================================================
# FUNCIONES DE VALIDACIÓN Y EXTRACCIÓN
# ============================================================================

def validate_response(content: str) -> bool:
    """
    Valida que el contenido generado cumple requisitos mínimos.
    
    Args:
        content: Contenido HTML a validar
        
    Returns:
        bool: True si el contenido es válido
    """
    if not content or not content.strip():
        return False
    
    # Debe tener al menos algún contenido HTML básico
    has_html = bool(re.search(r'<[^>]+>', content))
    
    # Debe tener longitud mínima razonable
    min_length = 100
    
    return has_html and len(content.strip()) >= min_length


def extract_html_content(content: str) -> str:
    """
    Extrae contenido HTML limpio de la respuesta.
    
    Elimina bloques de código markdown si existen y limpia
    el contenido para obtener solo el HTML.
    
    Args:
        content: Contenido potencialmente con markdown
        
    Returns:
        str: Contenido HTML limpio
    """
    if not content:
        return ""
    
    # Eliminar bloques de código markdown
    # Patrón: ```html ... ``` o ```...```
    code_block_pattern = r'```(?:html)?\s*([\s\S]*?)\s*```'
    matches = re.findall(code_block_pattern, content)
    
    if matches:
        # Usar el contenido del bloque de código más largo
        content = max(matches, key=len)
    
    # Limpiar espacios al inicio y final
    content = content.strip()
    
    # Si empieza con <style> o <article>, es HTML válido
    if content.startswith('<style>') or content.startswith('<article>'):
        return content
    
    # Intentar encontrar el inicio del HTML
    html_start_patterns = [
        r'(<style>[\s\S]*)',
        r'(<article>[\s\S]*)',
        r'(<!DOCTYPE[\s\S]*)',
        r'(<html[\s\S]*)',
    ]
    
    for pattern in html_start_patterns:
        match = re.search(pattern, content, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    
    # Si no se encuentra patrón HTML claro, retornar el contenido limpio
    return content


def count_tokens(text: str) -> int:
    """
    Estima el número de tokens en un texto.
    
    Usa una aproximación simple basada en caracteres/palabras.
    Para conteo exacto, se debería usar el tokenizer de Anthropic.
    
    Args:
        text: Texto a contar
        
    Returns:
        int: Número estimado de tokens
    """
    if not text:
        return 0
    
    # Aproximación: ~4 caracteres por token en inglés/español
    # Esto es una estimación conservadora
    char_estimate = len(text) // 4
    
    # Alternativa basada en palabras: ~0.75 tokens por palabra
    word_count = len(text.split())
    word_estimate = int(word_count * 1.3)
    
    # Usar el mayor de los dos para ser conservadores
    return max(char_estimate, word_estimate)


def estimate_prompt_tokens(
    prompt: str,
    system_prompt: Optional[str] = None
) -> int:
    """
    Estima tokens totales de un prompt (incluyendo system prompt).
    
    Args:
        prompt: Prompt principal
        system_prompt: Prompt de sistema opcional
        
    Returns:
        int: Tokens estimados
    """
    total = count_tokens(prompt)
    
    if system_prompt:
        total += count_tokens(system_prompt)
    
    # Añadir overhead por formato de mensaje (~50 tokens)
    total += 50
    
    return total


# ============================================================================
# FUNCIONES DE UTILIDAD
# ============================================================================

def is_api_available() -> bool:
    """
    Verifica si la API de Anthropic está disponible y configurada.
    
    Returns:
        bool: True si la API está lista para usar
    """
    if not _anthropic_available:
        return False
    
    if not CLAUDE_API_KEY:
        return False
    
    if not CLAUDE_API_KEY.startswith('sk-ant-'):
        return False
    
    return True


def get_model_info(model: str) -> Dict[str, Any]:
    """
    Obtiene información sobre un modelo específico.
    
    Args:
        model: ID del modelo
        
    Returns:
        dict: Información del modelo
    """
    return {
        'id': model,
        'name': AVAILABLE_MODELS.get(model, model),
        'max_tokens': MODEL_TOKEN_LIMITS.get(model, 200000),
        'available': model in AVAILABLE_MODELS,
    }


def list_available_models() -> List[Dict[str, str]]:
    """
    Lista todos los modelos disponibles.
    
    Returns:
        list: Lista de diccionarios con info de modelos
    """
    return [
        {'id': model_id, 'name': name}
        for model_id, name in AVAILABLE_MODELS.items()
    ]


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    # Versión
    '__version__',
    
    # Excepciones
    'GenerationError',
    'TokenLimitError',
    'APIKeyError',
    'ContentValidationError',
    'RetryExhaustedError',
    
    # Clases de datos
    'GenerationStage',
    'GenerationResult',
    'APIResponse',
    
    # Re-exports de errores de Anthropic
    'APIError',
    'APIConnectionError',
    'RateLimitError',
    'APIStatusError',
    'AuthenticationError',
    'BadRequestError',
    
    # Funciones principales
    'call_claude_api',
    'generate_content',
    'generate_with_stages',
    
    # Cliente
    'get_client',
    'reset_client',
    
    # Validación y extracción
    'validate_response',
    'extract_html_content',
    'count_tokens',
    'estimate_prompt_tokens',
    
    # Utilidades
    'is_api_available',
    'get_model_info',
    'list_available_models',
    
    # Constantes
    'AVAILABLE_MODELS',
    'MODEL_TOKEN_LIMITS',
    'DEFAULT_MAX_RETRIES',
]
