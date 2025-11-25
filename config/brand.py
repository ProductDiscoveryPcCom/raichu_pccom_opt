"""
Tono de marca y CSS del CMS
"""

BRAND_TONE = """
# Manual de Tono - PcComponentes

## TONO ASPIRACIONAL (NO NEGATIVO)
...
"""

# Cargar CSS desde archivo
from pathlib import Path

def load_css() -> str:
    """Carga el CSS compatible con CMS"""
    css_path = Path(__file__).parent / "cms_compatible.css"
    if css_path.exists():
        return css_path.read_text()
    # Fallback al CSS embebido si no existe el archivo
    return """<style>
:root{
  --orange-900:#FF6000;...
"""

CSS_CMS_COMPATIBLE = load_css()
