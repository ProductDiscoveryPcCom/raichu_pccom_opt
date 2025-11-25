"""
Gestión centralizada del estado de Streamlit
"""
import streamlit as st
from dataclasses import dataclass, asdict
from typing import Optional, List, Dict, Any
import json

@dataclass
class CompetitorData:
    """Datos de un competidor scrapeado"""
    url: str
    title: Optional[str] = None
    word_count: Optional[int] = None
    headings: List[dict] = None
    paragraphs: List[str] = None
    scraped: bool = False
    error: Optional[str] = None
    
    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class GenerationMetadata:
    """Metadata de una generación"""
    product_id: str
    arquetipo: str
    objetivo: str
    keyword_principal: str
    keywords_secundarias: str
    longitud_objetivo: int
    longitud_real: int
    timestamp: str
    campos_arquetipo: Dict = None
    
    def to_dict(self) -> dict:
        return asdict(self)


class StateManager:
    """Gestor centralizado del estado de la aplicación"""
    
    @staticmethod
    def get_competitor(index: int) -> Optional[CompetitorData]:
        """Obtiene datos de un competidor"""
        key = f'competitor_{index}_data'
        if key in st.session_state:
            data = st.session_state[key]
            return CompetitorData(**data) if isinstance(data, dict) else data
        return None
    
    @staticmethod
    def set_competitor(index: int, data: CompetitorData):
        """Guarda datos de un competidor"""
        st.session_state[f'competitor_{index}_data'] = data.to_dict()
    
    @staticmethod
    def get_all_competitors() -> List[CompetitorData]:
        """Obtiene todos los competidores"""
        competitors = []
        for i in range(3):
            comp = StateManager.get_competitor(i)
            if comp:
                competitors.append(comp)
        return competitors
    
    @staticmethod
    def clear_competitors():
        """Limpia datos de competidores"""
        for i in range(3):
            key = f'competitor_{i}_data'
            if key in st.session_state:
                del st.session_state[key]
    
    @staticmethod
    def get_gsc_results() -> Optional[dict]:
        """Obtiene resultados de GSC"""
        return st.session_state.get('gsc_check_results')
    
    @staticmethod
    def set_gsc_results(results: dict):
        """Guarda resultados de GSC"""
        st.session_state['gsc_check_results'] = results
    
    @staticmethod
    def get_generation_results() -> Optional[dict]:
        """Obtiene resultados de generación"""
        return st.session_state.get('results')
    
    @staticmethod
    def set_generation_results(results: dict):
        """Guarda resultados de generación"""
        st.session_state['results'] = results
    
    @staticmethod
    def clear_generation():
        """Limpia resultados de generación"""
        keys_to_clear = ['gsc_check_results', 'last_checked_keyword', 
                         'confirm_new_content', 'results']
        for key in keys_to_clear:
            if key in st.session_state:
                del st.session_state[key]
