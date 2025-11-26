"""
URL Validator - PcComponentes Content Generator
Versión 4.2.0

Módulo de validación exhaustiva de URLs.
Incluye sanitización, validación de seguridad, y normalización.

Este módulo proporciona:
- Validación de formato y estructura de URLs
- Detección de URLs potencialmente maliciosas
- Normalización y limpieza de URLs
- Validación específica para dominios de PcComponentes
- Sanitización contra inyección y ataques

Autor: PcComponentes - Product Discovery & Content
"""

import re
import ipaddress
import logging
from typing import Dict, List, Optional, Tuple, Any, Set
from dataclasses import dataclass
from enum import Enum
from urllib.parse import (
    urlparse,
    urlunparse,
    parse_qs,
    urlencode,
    quote,
    unquote,
    ParseResult,
)

# Configurar logging
logger = logging.getLogger(__name__)

# ============================================================================
# VERSIÓN Y CONSTANTES
# ============================================================================

__version__ = "4.2.0"

# Dominios de PcComponentes
PCCOMPONENTES_DOMAINS = [
    'pccomponentes.com',
    'www.pccomponentes.com',
    'blog.pccomponentes.com',
    'm.pccomponentes.com',
]

# Dominios de confianza adicionales
TRUSTED_DOMAINS = [
    'google.com',
    'youtube.com',
    'amazon.es',
    'amazon.com',
    'mediamarkt.es',
    'elcorteingles.es',
]

# Protocolos permitidos
ALLOWED_PROTOCOLS = ['http', 'https']

# Protocolos peligrosos
DANGEROUS_PROTOCOLS = [
    'javascript',
    'data',
    'vbscript',
    'file',
    'ftp',
]

# Extensiones de archivo peligrosas
DANGEROUS_EXTENSIONS = [
    '.exe', '.bat', '.cmd', '.msi', '.scr',
    '.vbs', '.js', '.jar', '.ps1', '.sh',
]

# Patrones sospechosos en URLs
SUSPICIOUS_PATTERNS = [
    r'<script',
    r'javascript:',
    r'data:text/html',
    r'onerror=',
    r'onload=',
    r'onclick=',
    r'eval\(',
    r'document\.',
    r'window\.',
    r'\.\./',  # Path traversal
    r'%2e%2e',  # Encoded path traversal
    r'%00',  # Null byte
    r'\x00',  # Null byte
]

# Longitudes máximas
MAX_URL_LENGTH = 2048
MAX_DOMAIN_LENGTH = 253
MAX_PATH_LENGTH = 1024
MAX_QUERY_LENGTH = 1024

# Puertos estándar
STANDARD_PORTS = {
    'http': 80,
    'https': 443,
}

# Regex para validación
URL_REGEX = re.compile(
    r'^(?:(?:https?):\/\/)?'  # Protocolo opcional
    r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,63}\.?|'  # Dominio
    r'localhost|'  # localhost
    r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # IP
    r'(?::\d+)?'  # Puerto opcional
    r'(?:/?|[/?]\S+)?$',  # Path
    re.IGNORECASE
)

DOMAIN_REGEX = re.compile(
    r'^(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)*'
    r'[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?$',
    re.IGNORECASE
)

IP_REGEX = re.compile(
    r'^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$'
)


# ============================================================================
# EXCEPCIONES
# ============================================================================

class URLValidationError(Exception):
    """Excepción base para errores de validación de URL."""
    
    def __init__(
        self,
        message: str,
        url: str = "",
        error_code: str = "UNKNOWN",
        details: Optional[Dict] = None
    ):
        super().__init__(message)
        self.message = message
        self.url = url
        self.error_code = error_code
        self.details = details or {}
    
    def __str__(self):
        return f"[{self.error_code}] {self.message}"


class InvalidURLFormatError(URLValidationError):
    """URL con formato inválido."""
    
    def __init__(self, message: str, url: str = ""):
        super().__init__(message, url, "INVALID_FORMAT")


class UnsafeURLError(URLValidationError):
    """URL potencialmente peligrosa."""
    
    def __init__(self, message: str, url: str = "", threat_type: str = ""):
        super().__init__(message, url, "UNSAFE_URL", {"threat_type": threat_type})
        self.threat_type = threat_type


class BlockedDomainError(URLValidationError):
    """Dominio bloqueado."""
    
    def __init__(self, message: str, url: str = "", domain: str = ""):
        super().__init__(message, url, "BLOCKED_DOMAIN", {"domain": domain})
        self.domain = domain


class PrivateIPError(URLValidationError):
    """URL apunta a IP privada/local."""
    
    def __init__(self, message: str, url: str = "", ip: str = ""):
        super().__init__(message, url, "PRIVATE_IP", {"ip": ip})
        self.ip = ip


# ============================================================================
# ENUMS Y DATA CLASSES
# ============================================================================

class URLStatus(Enum):
    """Estados de validación de URL."""
    VALID = "valid"
    INVALID_FORMAT = "invalid_format"
    UNSAFE = "unsafe"
    BLOCKED = "blocked"
    PRIVATE_IP = "private_ip"
    TOO_LONG = "too_long"
    SUSPICIOUS = "suspicious"


class ThreatType(Enum):
    """Tipos de amenazas detectadas."""
    NONE = "none"
    XSS = "xss"
    INJECTION = "injection"
    PATH_TRAVERSAL = "path_traversal"
    DANGEROUS_PROTOCOL = "dangerous_protocol"
    DANGEROUS_EXTENSION = "dangerous_extension"
    SSRF = "ssrf"
    MALFORMED = "malformed"


@dataclass
class ValidationResult:
    """Resultado de validación de URL."""
    is_valid: bool
    url: str
    normalized_url: Optional[str] = None
    status: URLStatus = URLStatus.VALID
    threat_type: ThreatType = ThreatType.NONE
    error: Optional[str] = None
    warnings: Optional[List[str]] = None
    details: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte a diccionario."""
        return {
            'is_valid': self.is_valid,
            'url': self.url,
            'normalized_url': self.normalized_url,
            'status': self.status.value,
            'threat_type': self.threat_type.value,
            'error': self.error,
            'warnings': self.warnings,
            'details': self.details,
        }


@dataclass
class ParsedURL:
    """URL parseada con componentes."""
    original: str
    scheme: str
    domain: str
    port: Optional[int]
    path: str
    query: str
    fragment: str
    is_ip: bool = False
    ip_address: Optional[str] = None
    
    @property
    def full_domain(self) -> str:
        """Dominio completo con puerto si no es estándar."""
        if self.port and self.port != STANDARD_PORTS.get(self.scheme):
            return f"{self.domain}:{self.port}"
        return self.domain
    
    @property
    def base_url(self) -> str:
        """URL base sin path ni query."""
        return f"{self.scheme}://{self.full_domain}"
    
    def to_url(self) -> str:
        """Reconstruye la URL."""
        port_str = f":{self.port}" if self.port and self.port != STANDARD_PORTS.get(self.scheme) else ""
        query_str = f"?{self.query}" if self.query else ""
        fragment_str = f"#{self.fragment}" if self.fragment else ""
        return f"{self.scheme}://{self.domain}{port_str}{self.path}{query_str}{fragment_str}"


# ============================================================================
# CLASE PRINCIPAL: URLValidator
# ============================================================================

class URLValidator:
    """
    Validador exhaustivo de URLs.
    
    Características:
    - Validación de formato y estructura
    - Detección de URLs maliciosas (XSS, inyección, etc.)
    - Validación de IPs privadas (prevención SSRF)
    - Lista de dominios bloqueados/permitidos
    - Normalización de URLs
    - Sanitización de parámetros
    
    Example:
        >>> validator = URLValidator()
        >>> result = validator.validate("https://example.com/page?q=test")
        >>> if result.is_valid:
        ...     print(result.normalized_url)
    """
    
    def __init__(
        self,
        allowed_domains: Optional[List[str]] = None,
        blocked_domains: Optional[List[str]] = None,
        allow_private_ips: bool = False,
        allow_localhost: bool = False,
        strict_mode: bool = True,
        max_url_length: int = MAX_URL_LENGTH
    ):
        """
        Inicializa el validador.
        
        Args:
            allowed_domains: Lista de dominios permitidos (None = todos)
            blocked_domains: Lista de dominios bloqueados
            allow_private_ips: Permitir IPs privadas
            allow_localhost: Permitir localhost
            strict_mode: Modo estricto (más validaciones)
            max_url_length: Longitud máxima de URL
        """
        self._allowed_domains: Optional[Set[str]] = set(allowed_domains) if allowed_domains else None
        self._blocked_domains: Set[str] = set(blocked_domains) if blocked_domains else set()
        self._allow_private_ips = allow_private_ips
        self._allow_localhost = allow_localhost
        self._strict_mode = strict_mode
        self._max_url_length = max_url_length
        
        # Compilar patrones sospechosos
        self._suspicious_patterns = [
            re.compile(pattern, re.IGNORECASE)
            for pattern in SUSPICIOUS_PATTERNS
        ]
        
        logger.debug(
            f"URLValidator inicializado: strict_mode={strict_mode}, "
            f"allow_private_ips={allow_private_ips}"
        )
    
    def validate(self, url: str) -> ValidationResult:
        """
        Valida una URL completamente.
        
        Args:
            url: URL a validar
            
        Returns:
            ValidationResult con el resultado de la validación
        """
        warnings = []
        
        # Verificar que no sea None o vacía
        if not url:
            return ValidationResult(
                is_valid=False,
                url="",
                status=URLStatus.INVALID_FORMAT,
                error="URL vacía"
            )
        
        # Limpiar espacios
        url = url.strip()
        
        # Verificar longitud
        if len(url) > self._max_url_length:
            return ValidationResult(
                is_valid=False,
                url=url,
                status=URLStatus.TOO_LONG,
                error=f"URL excede longitud máxima ({self._max_url_length} caracteres)"
            )
        
        # Decodificar URL si está encoded
        try:
            decoded_url = unquote(url)
        except Exception:
            decoded_url = url
        
        # Verificar patrones sospechosos
        threat = self._check_suspicious_patterns(url, decoded_url)
        if threat != ThreatType.NONE:
            return ValidationResult(
                is_valid=False,
                url=url,
                status=URLStatus.UNSAFE,
                threat_type=threat,
                error=f"URL contiene patrones sospechosos: {threat.value}"
            )
        
        # Verificar protocolo peligroso
        for proto in DANGEROUS_PROTOCOLS:
            if url.lower().startswith(f"{proto}:"):
                return ValidationResult(
                    is_valid=False,
                    url=url,
                    status=URLStatus.UNSAFE,
                    threat_type=ThreatType.DANGEROUS_PROTOCOL,
                    error=f"Protocolo peligroso: {proto}"
                )
        
        # Añadir protocolo si falta
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
            warnings.append("Se añadió protocolo HTTPS automáticamente")
        
        # Parsear URL
        try:
            parsed = self._parse_url(url)
        except Exception as e:
            return ValidationResult(
                is_valid=False,
                url=url,
                status=URLStatus.INVALID_FORMAT,
                error=f"Error al parsear URL: {str(e)}"
            )
        
        # Validar protocolo
        if parsed.scheme not in ALLOWED_PROTOCOLS:
            return ValidationResult(
                is_valid=False,
                url=url,
                status=URLStatus.INVALID_FORMAT,
                error=f"Protocolo no permitido: {parsed.scheme}"
            )
        
        # Validar dominio
        domain_result = self._validate_domain(parsed)
        if not domain_result[0]:
            return ValidationResult(
                is_valid=False,
                url=url,
                status=domain_result[1],
                error=domain_result[2]
            )
        
        # Verificar IP privada
        if parsed.is_ip:
            ip_result = self._validate_ip(parsed.ip_address)
            if not ip_result[0]:
                return ValidationResult(
                    is_valid=False,
                    url=url,
                    status=URLStatus.PRIVATE_IP,
                    threat_type=ThreatType.SSRF,
                    error=ip_result[1]
                )
        
        # Verificar localhost
        if not self._allow_localhost and self._is_localhost(parsed.domain):
            return ValidationResult(
                is_valid=False,
                url=url,
                status=URLStatus.PRIVATE_IP,
                threat_type=ThreatType.SSRF,
                error="No se permite localhost"
            )
        
        # Verificar extensiones peligrosas
        if self._strict_mode:
            ext_check = self._check_dangerous_extension(parsed.path)
            if ext_check:
                return ValidationResult(
                    is_valid=False,
                    url=url,
                    status=URLStatus.UNSAFE,
                    threat_type=ThreatType.DANGEROUS_EXTENSION,
                    error=f"Extensión de archivo peligrosa: {ext_check}"
                )
        
        # Verificar dominio permitido/bloqueado
        if self._allowed_domains and parsed.domain not in self._allowed_domains:
            # Verificar subdominios
            domain_parts = parsed.domain.split('.')
            is_allowed = False
            for i in range(len(domain_parts)):
                check_domain = '.'.join(domain_parts[i:])
                if check_domain in self._allowed_domains:
                    is_allowed = True
                    break
            
            if not is_allowed:
                return ValidationResult(
                    is_valid=False,
                    url=url,
                    status=URLStatus.BLOCKED,
                    error=f"Dominio no permitido: {parsed.domain}"
                )
        
        if parsed.domain in self._blocked_domains:
            return ValidationResult(
                is_valid=False,
                url=url,
                status=URLStatus.BLOCKED,
                error=f"Dominio bloqueado: {parsed.domain}"
            )
        
        # Normalizar URL
        normalized = self._normalize_url(parsed)
        
        # Advertencias adicionales
        if parsed.scheme == 'http':
            warnings.append("URL usa HTTP en lugar de HTTPS")
        
        return ValidationResult(
            is_valid=True,
            url=url,
            normalized_url=normalized,
            status=URLStatus.VALID,
            warnings=warnings if warnings else None,
            details={
                'domain': parsed.domain,
                'path': parsed.path,
                'is_ip': parsed.is_ip,
            }
        )
    
    def validate_batch(self, urls: List[str]) -> List[ValidationResult]:
        """
        Valida múltiples URLs.
        
        Args:
            urls: Lista de URLs a validar
            
        Returns:
            Lista de ValidationResult
        """
        return [self.validate(url) for url in urls]
    
    def is_valid(self, url: str) -> bool:
        """
        Verifica si una URL es válida (método simple).
        
        Args:
            url: URL a verificar
            
        Returns:
            True si es válida
        """
        return self.validate(url).is_valid
    
    def sanitize(self, url: str) -> Optional[str]:
        """
        Sanitiza una URL y retorna la versión limpia.
        
        Args:
            url: URL a sanitizar
            
        Returns:
            URL sanitizada o None si no es válida
        """
        result = self.validate(url)
        return result.normalized_url if result.is_valid else None
    
    def _parse_url(self, url: str) -> ParsedURL:
        """Parsea una URL en sus componentes."""
        parsed = urlparse(url)
        
        # Extraer puerto
        port = parsed.port
        
        # Verificar si es IP
        domain = parsed.netloc.split(':')[0]
        is_ip = bool(IP_REGEX.match(domain))
        ip_address = domain if is_ip else None
        
        return ParsedURL(
            original=url,
            scheme=parsed.scheme.lower(),
            domain=domain.lower(),
            port=port,
            path=parsed.path or '/',
            query=parsed.query,
            fragment=parsed.fragment,
            is_ip=is_ip,
            ip_address=ip_address
        )
    
    def _validate_domain(self, parsed: ParsedURL) -> Tuple[bool, URLStatus, str]:
        """Valida el dominio de la URL."""
        domain = parsed.domain
        
        if not domain:
            return (False, URLStatus.INVALID_FORMAT, "Dominio vacío")
        
        if len(domain) > MAX_DOMAIN_LENGTH:
            return (False, URLStatus.INVALID_FORMAT, "Dominio demasiado largo")
        
        # Verificar formato de dominio (si no es IP)
        if not parsed.is_ip:
            if not DOMAIN_REGEX.match(domain):
                return (False, URLStatus.INVALID_FORMAT, f"Formato de dominio inválido: {domain}")
            
            # Verificar TLD
            parts = domain.split('.')
            if len(parts) < 2:
                return (False, URLStatus.INVALID_FORMAT, "Dominio sin TLD válido")
            
            tld = parts[-1]
            if len(tld) < 2:
                return (False, URLStatus.INVALID_FORMAT, f"TLD inválido: {tld}")
        
        return (True, URLStatus.VALID, "")
    
    def _validate_ip(self, ip: str) -> Tuple[bool, str]:
        """Valida una dirección IP."""
        try:
            ip_obj = ipaddress.ip_address(ip)
            
            if not self._allow_private_ips:
                if ip_obj.is_private:
                    return (False, f"IP privada no permitida: {ip}")
                if ip_obj.is_loopback:
                    return (False, f"IP de loopback no permitida: {ip}")
                if ip_obj.is_link_local:
                    return (False, f"IP link-local no permitida: {ip}")
                if ip_obj.is_reserved:
                    return (False, f"IP reservada no permitida: {ip}")
            
            return (True, "")
        except ValueError:
            return (False, f"IP inválida: {ip}")
    
    def _is_localhost(self, domain: str) -> bool:
        """Verifica si el dominio es localhost."""
        localhost_aliases = [
            'localhost',
            '127.0.0.1',
            '::1',
            '0.0.0.0',
        ]
        return domain.lower() in localhost_aliases
    
    def _check_suspicious_patterns(self, url: str, decoded_url: str) -> ThreatType:
        """Verifica patrones sospechosos en la URL."""
        for pattern in self._suspicious_patterns:
            if pattern.search(url) or pattern.search(decoded_url):
                # Determinar tipo de amenaza
                pattern_str = pattern.pattern.lower()
                
                if 'script' in pattern_str or 'onerror' in pattern_str:
                    return ThreatType.XSS
                elif '..' in pattern_str or '%2e' in pattern_str:
                    return ThreatType.PATH_TRAVERSAL
                elif '%00' in pattern_str or '\\x00' in pattern_str:
                    return ThreatType.INJECTION
                else:
                    return ThreatType.INJECTION
        
        return ThreatType.NONE
    
    def _check_dangerous_extension(self, path: str) -> Optional[str]:
        """Verifica extensiones de archivo peligrosas."""
        path_lower = path.lower()
        for ext in DANGEROUS_EXTENSIONS:
            if path_lower.endswith(ext):
                return ext
        return None
    
    def _normalize_url(self, parsed: ParsedURL) -> str:
        """Normaliza una URL."""
        # Normalizar path
        path = parsed.path or '/'
        
        # Eliminar barras duplicadas
        while '//' in path:
            path = path.replace('//', '/')
        
        # Normalizar query string
        query = parsed.query
        if query:
            # Parsear y re-encodificar para normalizar
            try:
                params = parse_qs(query, keep_blank_values=True)
                # Ordenar parámetros
                sorted_params = sorted(params.items())
                query = urlencode(sorted_params, doseq=True)
            except Exception:
                pass
        
        # Reconstruir URL
        port_str = ""
        if parsed.port and parsed.port != STANDARD_PORTS.get(parsed.scheme):
            port_str = f":{parsed.port}"
        
        query_str = f"?{query}" if query else ""
        
        return f"{parsed.scheme}://{parsed.domain}{port_str}{path}{query_str}"


# ============================================================================
# INSTANCIA GLOBAL
# ============================================================================

_default_validator: Optional[URLValidator] = None


def get_validator(**kwargs) -> URLValidator:
    """
    Obtiene el validador global.
    
    Args:
        **kwargs: Argumentos para crear nuevo validador si no existe
        
    Returns:
        Instancia de URLValidator
    """
    global _default_validator
    
    if _default_validator is None:
        _default_validator = URLValidator(**kwargs)
    
    return _default_validator


def reset_validator() -> None:
    """Resetea el validador global."""
    global _default_validator
    _default_validator = None


# ============================================================================
# FUNCIONES DE CONVENIENCIA
# ============================================================================

def validate_url(url: str) -> ValidationResult:
    """
    Valida una URL usando el validador global.
    
    Args:
        url: URL a validar
        
    Returns:
        ValidationResult
    """
    return get_validator().validate(url)


def is_valid_url(url: str) -> bool:
    """
    Verifica si una URL es válida.
    
    Args:
        url: URL a verificar
        
    Returns:
        True si es válida
    """
    return get_validator().is_valid(url)


def sanitize_url(url: str) -> Optional[str]:
    """
    Sanitiza una URL.
    
    Args:
        url: URL a sanitizar
        
    Returns:
        URL sanitizada o None
    """
    return get_validator().sanitize(url)


def is_pccomponentes_url(url: str) -> bool:
    """
    Verifica si una URL es de PcComponentes.
    
    Args:
        url: URL a verificar
        
    Returns:
        True si es de PcComponentes
    """
    result = validate_url(url)
    
    if not result.is_valid:
        return False
    
    domain = result.details.get('domain', '') if result.details else ''
    
    return any(pcc in domain for pcc in PCCOMPONENTES_DOMAINS)


def is_safe_url(url: str) -> Tuple[bool, Optional[str]]:
    """
    Verifica si una URL es segura.
    
    Args:
        url: URL a verificar
        
    Returns:
        Tuple[es_segura, mensaje_error]
    """
    result = validate_url(url)
    
    if result.is_valid:
        return (True, None)
    else:
        return (False, result.error)


def normalize_url(url: str) -> Optional[str]:
    """
    Normaliza una URL.
    
    Args:
        url: URL a normalizar
        
    Returns:
        URL normalizada o None si es inválida
    """
    return sanitize_url(url)


def extract_domain(url: str) -> Optional[str]:
    """
    Extrae el dominio de una URL.
    
    Args:
        url: URL
        
    Returns:
        Dominio o None si es inválida
    """
    result = validate_url(url)
    
    if result.is_valid and result.details:
        return result.details.get('domain')
    
    return None


def validate_urls_batch(urls: List[str]) -> Dict[str, ValidationResult]:
    """
    Valida múltiples URLs y retorna resultados por URL.
    
    Args:
        urls: Lista de URLs
        
    Returns:
        Dict con URL como clave y ValidationResult como valor
    """
    validator = get_validator()
    return {url: validator.validate(url) for url in urls}


def filter_valid_urls(urls: List[str]) -> List[str]:
    """
    Filtra solo las URLs válidas.
    
    Args:
        urls: Lista de URLs
        
    Returns:
        Lista de URLs válidas
    """
    validator = get_validator()
    return [url for url in urls if validator.is_valid(url)]


def filter_safe_urls(urls: List[str]) -> List[str]:
    """
    Filtra solo las URLs seguras (válidas y sin amenazas).
    
    Args:
        urls: Lista de URLs
        
    Returns:
        Lista de URLs seguras
    """
    validator = get_validator()
    safe_urls = []
    
    for url in urls:
        result = validator.validate(url)
        if result.is_valid and result.threat_type == ThreatType.NONE:
            safe_urls.append(result.normalized_url or url)
    
    return safe_urls


# ============================================================================
# VALIDADORES ESPECÍFICOS
# ============================================================================

def create_pccomponentes_validator() -> URLValidator:
    """
    Crea un validador específico para URLs de PcComponentes.
    
    Returns:
        URLValidator configurado para PcComponentes
    """
    return URLValidator(
        allowed_domains=PCCOMPONENTES_DOMAINS,
        allow_private_ips=False,
        allow_localhost=False,
        strict_mode=True
    )


def create_competitor_validator(blocked_domains: Optional[List[str]] = None) -> URLValidator:
    """
    Crea un validador para URLs de competidores.
    
    Args:
        blocked_domains: Dominios adicionales a bloquear
        
    Returns:
        URLValidator configurado para competidores
    """
    blocked = list(PCCOMPONENTES_DOMAINS)  # Bloquear PcComponentes en competidores
    
    if blocked_domains:
        blocked.extend(blocked_domains)
    
    return URLValidator(
        blocked_domains=blocked,
        allow_private_ips=False,
        allow_localhost=False,
        strict_mode=True
    )


def create_permissive_validator() -> URLValidator:
    """
    Crea un validador permisivo (menos restricciones).
    
    Returns:
        URLValidator con menos restricciones
    """
    return URLValidator(
        allow_private_ips=False,
        allow_localhost=False,
        strict_mode=False,
        max_url_length=4096
    )


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    # Versión
    '__version__',
    
    # Excepciones
    'URLValidationError',
    'InvalidURLFormatError',
    'UnsafeURLError',
    'BlockedDomainError',
    'PrivateIPError',
    
    # Enums y Data Classes
    'URLStatus',
    'ThreatType',
    'ValidationResult',
    'ParsedURL',
    
    # Clase principal
    'URLValidator',
    
    # Instancia global
    'get_validator',
    'reset_validator',
    
    # Funciones de validación
    'validate_url',
    'is_valid_url',
    'sanitize_url',
    'is_pccomponentes_url',
    'is_safe_url',
    'normalize_url',
    'extract_domain',
    
    # Funciones batch
    'validate_urls_batch',
    'filter_valid_urls',
    'filter_safe_urls',
    
    # Validadores específicos
    'create_pccomponentes_validator',
    'create_competitor_validator',
    'create_permissive_validator',
    
    # Constantes
    'PCCOMPONENTES_DOMAINS',
    'ALLOWED_PROTOCOLS',
    'MAX_URL_LENGTH',
]
