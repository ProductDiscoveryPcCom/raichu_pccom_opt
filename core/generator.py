"""
Content Generator - PcComponentes Content Generator
Versión 4.1.1

Clase principal que orquesta la generación de contenido usando Claude API.
Maneja el flujo de 3 etapas tanto para contenido nuevo como reescritura.

Autor: PcComponentes - Product Discovery & Content
"""

import anthropic
from typing import Optional

# Importar prompts de contenido nuevo
from prompts.new_content import (
    build_generation_prompt_stage1_draft,
    build_correction_prompt_stage2,
    build_final_generation_prompt_stage3
)

# Importar prompts de reescritura - NOMBRES CORRECTOS
from prompts.rewrite import (
    build_competitor_analysis_prompt,
    build_rewrite_prompt_stage1_draft,
    build_rewrite_correction_prompt_stage2,
    build_rewrite_final_prompt_stage3
)


# ============================================================================
# CLASE PRINCIPAL
# ============================================================================

class ContentGenerator:
    """
    Generador de contenido usando Claude API.
    
    Maneja tanto la generación de contenido nuevo como la reescritura
    competitiva, con un flujo de 3 etapas para máxima calidad.
    
    Attributes:
        client: Cliente de Anthropic
        model: Modelo de Claude a usar
        max_tokens: Tokens máximos por respuesta
        temperature: Temperature para generación
        
    Example:
        >>> generator = ContentGenerator(api_key="tu-key")
        >>> result = generator.generate(prompt)
    """
    
    def __init__(
        self,
        api_key: str,
        model: str = "claude-sonnet-4-20250514",
        max_tokens: int = 8000,
        temperature: float = 0.7
    ):
        """
        Inicializa el generador de contenido.
        
        Args:
            api_key: API key de Anthropic
            model: Modelo de Claude a usar
            max_tokens: Tokens máximos por respuesta
            temperature: Temperature (0.0-1.0)
            
        Raises:
            ValueError: Si la API key está vacía
        """
        
        if not api_key:
            raise ValueError("API key de Anthropic es requerida")
        
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
    
    
    def generate(self, prompt: str) -> str:
        """
        Genera contenido usando Claude API.
        
        Args:
            prompt: Prompt completo para Claude
            
        Returns:
            str: Contenido generado por Claude
            
        Raises:
            Exception: Si hay error en la API call
            
        Notes:
            - Usa el modelo configurado en __init__
            - Maneja errores de API automáticamente
            - Retorna solo el texto generado
        """
        
        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            # Extraer el texto de la respuesta
            return message.content[0].text
        
        except anthropic.APIError as e:
            raise Exception(f"Error en API de Claude: {str(e)}")
        
        except Exception as e:
            raise Exception(f"Error inesperado al generar contenido: {str(e)}")
    
    
    def generate_with_retry(
        self,
        prompt: str,
        max_retries: int = 3
    ) -> Optional[str]:
        """
        Genera contenido con reintentos automáticos si falla.
        
        Args:
            prompt: Prompt completo para Claude
            max_retries: Número máximo de reintentos
            
        Returns:
            str: Contenido generado o None si fallan todos los intentos
            
        Notes:
            - Útil para manejar errores temporales de API
            - Espera entre reintentos
        """
        
        import time
        
        for attempt in range(max_retries):
            try:
                return self.generate(prompt)
            
            except Exception as e:
                if attempt < max_retries - 1:
                    # Esperar antes de reintentar (backoff exponencial)
                    wait_time = 2 ** attempt
                    time.sleep(wait_time)
                    continue
                else:
                    # Último intento falló
                    raise e
        
        return None


# ============================================================================
# FUNCIONES DE UTILIDAD
# ============================================================================

def validate_api_key(api_key: str) -> bool:
    """
    Valida que una API key tenga el formato correcto.
    
    Args:
        api_key: API key a validar
        
    Returns:
        bool: True si el formato es válido
        
    Notes:
        - Solo valida formato, no si la key funciona
        - API keys de Anthropic empiezan con 'sk-ant-'
    """
    
    if not api_key:
        return False
    
    # API keys de Anthropic empiezan con sk-ant-
    if not api_key.startswith('sk-ant-'):
        return False
    
    # Longitud mínima razonable
    if len(api_key) < 20:
        return False
    
    return True


def estimate_tokens(text: str) -> int:
    """
    Estima el número de tokens en un texto.
    
    Args:
        text: Texto a analizar
        
    Returns:
        int: Estimación de tokens
        
    Notes:
        - Aproximación: 1 token ≈ 4 caracteres
        - No es exacto, solo para estimaciones
    """
    
    return len(text) // 4


# ============================================================================
# CONSTANTES Y CONFIGURACIÓN
# ============================================================================

# Versión del módulo
__version__ = "4.1.1"

# Modelos disponibles
AVAILABLE_MODELS = {
    'sonnet-4': 'claude-sonnet-4-20250514',
    'opus-4': 'claude-opus-4-20250514',
    'haiku-4': 'claude-haiku-4-20250514'
}

# Límites por defecto
DEFAULT_MAX_TOKENS = 8000
DEFAULT_TEMPERATURE = 0.7

# Timeouts
API_TIMEOUT = 300  # 5 minutos
