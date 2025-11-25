"""
Core package - PcComponentes Content Generator
"""

from .generator import ContentGenerator
from .scraper import scrape_pdp_data

__all__ = [
    'ContentGenerator',
    'scrape_pdp_data'
]

__version__ = "4.1.1"
