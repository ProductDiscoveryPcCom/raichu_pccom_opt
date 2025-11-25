"""
Tests básicos para validar la modularización
"""
import sys
sys.path.insert(0, '..')

def test_imports():
    """Verifica que todos los módulos se importan correctamente"""
    try:
        from config.settings import ANTHROPIC_API_KEY
        from config.archetipos import ARQUETIPOS, get_arquetipo
        from core.generator import ContentGenerator
        from core.scraper import scrape_pdp_n8n
        from utils.html_utils import count_words_in_html
        from utils.state_manager import StateManager
        print("✅ Todos los imports funcionan")
        return True
    except Exception as e:
        print(f"❌ Error en imports: {e}")
        return False

def test_archetipos():
    """Verifica que los arquetipos están bien definidos"""
    from config.archetipos import ARQUETIPOS, get_arquetipo
    
    assert len(ARQUETIPOS) == 18, "Deben haber 18 arquetipos"
    
    arq1 = get_arquetipo("ARQ-1")
    assert arq1 is not None
    assert arq1['code'] == "ARQ-1"
    assert 'name' in arq1
    assert 'default_length' in arq1
    
    print("✅ Arquetipos válidos")
    return True

def test_html_utils():
    """Verifica utilidades HTML"""
    from utils.html_utils import count_words_in_html, validate_html_structure
    
    html = "<article><h1>Test</h1><p>This is a test with ten words here</p></article>"
    words = count_words_in_html(html)
    assert words == 9, f"Expected 9 words, got {words}"
    
    validation = validate_html_structure(html)
    assert validation['has_article'] == True
    
    print("✅ HTML utils funcionan")
    return True

if __name__ == "__main__":
    tests = [
        test_imports,
        test_archetipos,
        test_html_utils
    ]
    
    passed = sum(1 for test in tests if test())
    total = len(tests)
    
    print(f"\n{'='*50}")
    print(f"Tests: {passed}/{total} passed")
    print(f"{'='*50}")
