"""
Generador de contenido con Claude
"""
import anthropic
import streamlit as st
from typing import Optional, Tuple, Callable

from prompts.new_content import (
    build_generation_prompt_stage1_draft,
    build_correction_prompt_stage2,
    build_final_generation_prompt_stage3
)
from prompts.rewrite import (
    build_rewrite_prompt_stage1_analysis,
    build_rewrite_prompt_stage2_draft,
    build_rewrite_prompt_stage3_final
)


class ContentGenerator:
    """Generador con flujo de 3 etapas + modo reescritura"""
    
    def __init__(self, api_key: str, model: str = "claude-sonnet-4-20250514"):
        """
        Args:
            api_key: Anthropic API key
            model: Modelo de Claude a usar
        """
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model
    
    def generate_stage(self, prompt: str, max_tokens: int = 10000, 
                      stage_name: str = "") -> Optional[str]:
        """
        Llama a Claude API para una etapa
        
        Args:
            prompt: Prompt para la etapa
            max_tokens: Máximo de tokens
            stage_name: Nombre de la etapa (para logging)
            
        Returns:
            Texto generado o None si error
        """
        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                messages=[{"role": "user", "content": prompt}]
            )
            result = message.content[0].text
            return result
        except Exception as e:
            st.error(f"Error en {stage_name}: {str(e)}")
            return None
    
    def generate_new_content(self, 
                            pdp_data: dict,
                            arquetipo: dict,
                            target_length: int,
                            keywords: list,
                            context: str,
                            links: dict,
                            objetivo: str,
                            producto_alternativo: dict,
                            casos_uso: list,
                            campos_arquetipo: dict,
                            progress_callback: Optional[Callable] = None
                            ) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """
        Flujo completo de generación en 3 etapas - MODO NUEVO
        
        Returns:
            Tuple de (draft, corrections_json, final_content)
        """
        # ETAPA 1: Borrador inicial
        if progress_callback:
            progress_callback(0, "📝 Etapa 1/3: Generando borrador inicial...")
        
        prompt_draft = build_generation_prompt_stage1_draft(
            pdp_data, arquetipo, target_length, keywords, context, links,
            objetivo, producto_alternativo, casos_uso, campos_arquetipo
        )
        
        draft_content = self.generate_stage(
            prompt_draft, max_tokens=12000, stage_name="Borrador"
        )
        
        if not draft_content:
            return None, None, None
        
        # ETAPA 2: Análisis crítico
        if progress_callback:
            progress_callback(33, "🔍 Etapa 2/3: Análisis crítico y correcciones...")
        
        prompt_correction = build_correction_prompt_stage2(
            draft_content, target_length, arquetipo, objetivo
        )
        
        corrections_json = self.generate_stage(
            prompt_correction, max_tokens=4000, stage_name="Análisis"
        )
        
        if not corrections_json:
            return draft_content, None, None
        
        # ETAPA 3: Versión final
        if progress_callback:
            progress_callback(66, "✨ Etapa 3/3: Generando versión final...")
        
        prompt_final = build_final_generation_prompt_stage3(
            draft_content, corrections_json, target_length
        )
        
        final_content = self.generate_stage(
            prompt_final, max_tokens=12000, stage_name="Versión Final"
        )
        
        if progress_callback:
            progress_callback(100, "✅ Generación completada")
        
        return draft_content, corrections_json, final_content
    
    def rewrite_content(self,
                       current_content: str,
                       current_structure: dict,
                       competitors_data: list,
                       arquetipo: dict,
                       target_length: int,
                       keywords: list,
                       context: str,
                       links: dict,
                       objetivo: str,
                       producto_alternativo: dict,
                       casos_uso: list,
                       campos_arquetipo: dict,
                       user_notes: str = "",
                       progress_callback: Optional[Callable] = None
                       ) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """
        Flujo completo de REESCRITURA en 3 etapas
        
        Returns:
            Tuple de (analysis_json, rewritten_draft, final_content)
        """
        # ETAPA 1: Análisis competitivo
        if progress_callback:
            progress_callback(0, "🔍 Etapa 1/3: Analizando contenido actual vs competencia...")
        
        prompt_analysis = build_rewrite_prompt_stage1_analysis(
            current_content, current_structure, competitors_data,
            arquetipo, target_length, keywords, objetivo, user_notes
        )
        
        analysis_json = self.generate_stage(
            prompt_analysis, max_tokens=6000, stage_name="Análisis Competitivo"
        )
        
        if not analysis_json:
            return None, None, None
        
        # ETAPA 2: Reescritura optimizada
        if progress_callback:
            progress_callback(33, "📝 Etapa 2/3: Reescribiendo contenido optimizado...")
        
        prompt_rewrite = build_rewrite_prompt_stage2_draft(
            current_content, analysis_json, arquetipo, target_length,
            keywords, context, links, objetivo, producto_alternativo,
            casos_uso, campos_arquetipo, user_notes
        )
        
        rewritten_draft = self.generate_stage(
            prompt_rewrite, max_tokens=12000, stage_name="Reescritura"
        )
        
        if not rewritten_draft:
            return analysis_json, None, None
        
        # ETAPA 3: Revisión final
        if progress_callback:
            progress_callback(66, "✨ Etapa 3/3: Revisión final y pulido...")
        
        prompt_final = build_rewrite_prompt_stage3_final(
            rewritten_draft, analysis_json, target_length, objetivo, user_notes
        )
        
        final_content = self.generate_stage(
            prompt_final, max_tokens=12000, stage_name="Versión Final"
        )
        
        if progress_callback:
            progress_callback(100, "✅ Reescritura completada")
        
        return analysis_json, rewritten_draft, final_content
