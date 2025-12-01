# -*- coding: utf-8 -*-
"""
Brand Configuration - PcComponentes Content Generator
Versión 4.5.0

Configuración de marca: CSS del CMS, tono de voz, colores y guías de estilo.
Basado en el Manual de Tono de Marca oficial de PcComponentes.

CAMBIOS v4.5.0:
- Tono rebalanceado: orientado a soluciones, no disuasorio
- Instrucciones alineadas con datos reales del scraping (sin ventajas/desventajas de usuarios)
- Nueva sección INSTRUCCIONES_ORIENTACION_POSITIVA
- Añadidas clases CSS faltantes (.card.destacado, .product-module, .price-tag)
- Mejorado get_system_prompt_base() con enfoque comercial

Este módulo contiene:
- CSS_CMS_COMPATIBLE: Estilos completos para el CMS
- BRAND_TONE: Directrices de tono de voz
- BRAND_COLORS: Paleta de colores corporativos
- BRAND_VOICE_GUIDELINES: Guía detallada de comunicación
- get_tone_instructions(): Función para generar instrucciones de tono
- get_system_prompt_base(): System prompt base para prompts

Autor: PcComponentes - Product Discovery & Content
"""

from typing import Dict, List

# ============================================================================
# VERSIÓN DEL MÓDULO
# ============================================================================

__version__ = "4.5.0"

# ============================================================================
# INFORMACIÓN DE MARCA
# ============================================================================

BRAND_NAME = "PcComponentes"
BRAND_DOMAIN = "www.pccomponentes.com"
BRAND_TAGLINE = "Ofrecer la mejor experiencia de recomendación y compra para productos y servicios tecnológicos."


# ============================================================================
# COLORES CORPORATIVOS
# ============================================================================

BRAND_COLORS: Dict[str, str] = {
    # Colores principales
    'orange_900': '#FF6000',
    'orange_700': '#FF8533',
    'orange_500': '#FFA366',
    'orange_300': '#FFC299',
    'orange_100': '#FFE0CC',
    
    # Azules
    'blue_m_900': '#170453',
    'blue_m_700': '#2E1A7A',
    'blue_m_500': '#4530A1',
    'blue_m_300': '#7A6BC4',
    'blue_m_100': '#C4BFE5',
    
    # Neutros
    'white': '#FFFFFF',
    'gray_100': '#F5F5F5',
    'gray_200': '#E5E5E5',
    'gray_300': '#D4D4D4',
    'gray_500': '#737373',
    'gray_700': '#404040',
    'gray_900': '#171717',
    'black': '#000000',
    
    # Estados
    'success': '#22C55E',
    'warning': '#F59E0B',
    'error': '#EF4444',
    'info': '#3B82F6',
    
    # Black Friday
    'bf_orange': '#FF6000',
    'bf_dark': '#170453',
}


# ============================================================================
# CSS COMPLETO COMPATIBLE CON CMS - v4.5.0
# Incluye clases adicionales: .card.destacado, .product-module, .price-tag
# ============================================================================

CSS_CMS_COMPATIBLE = """
<style>
:root {
  /* Colores principales */
  --orange-900: #FF6000;
  --orange-700: #FF8533;
  --orange-500: #FFA366;
  --orange-300: #FFC299;
  --orange-100: #FFE0CC;
  
  /* Azules */
  --blue-m-900: #170453;
  --blue-m-700: #2E1A7A;
  --blue-m-500: #4530A1;
  --blue-m-300: #7A6BC4;
  --blue-m-100: #C4BFE5;
  
  /* Neutros */
  --white: #FFFFFF;
  --gray-100: #F5F5F5;
  --gray-200: #E5E5E5;
  --gray-300: #D4D4D4;
  --gray-500: #737373;
  --gray-700: #404040;
  --gray-900: #171717;
  --black: #000000;
  
  /* Estados */
  --success: #22C55E;
  --warning: #F59E0B;
  --error: #EF4444;
  --info: #3B82F6;
  
  /* Espaciado */
  --space-xs: 4px;
  --space-sm: 8px;
  --space-md: 16px;
  --space-lg: 24px;
  --space-xl: 32px;
  --space-2xl: 48px;
  
  /* Tipografía */
  --font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  --font-size-xs: 12px;
  --font-size-sm: 14px;
  --font-size-md: 16px;
  --font-size-lg: 18px;
  --font-size-xl: 20px;
  --font-size-2xl: 24px;
  --font-size-3xl: 30px;
  --font-size-4xl: 36px;
  
  /* Bordes */
  --radius-sm: 4px;
  --radius-md: 8px;
  --radius-lg: 12px;
  --radius-xl: 16px;
  --radius-full: 9999px;
  
  /* Sombras */
  --shadow-sm: 0 1px 2px rgba(0,0,0,0.05);
  --shadow-md: 0 4px 6px rgba(0,0,0,0.1);
  --shadow-lg: 0 10px 15px rgba(0,0,0,0.1);
}

/* ========== RESET Y BASE ========== */
article {
  font-family: var(--font-family);
  font-size: var(--font-size-md);
  line-height: 1.7;
  color: var(--gray-900);
  max-width: 100%;
}

article * {
  box-sizing: border-box;
}

article p {
  margin: 0 0 var(--space-md) 0;
}

article a {
  color: var(--orange-900);
  text-decoration: underline;
  text-underline-offset: 2px;
  transition: color 0.2s ease;
}

article a:hover {
  color: var(--orange-700);
}

/* ========== KICKER (ETIQUETA SUPERIOR) ========== */
.kicker {
  display: inline-block;
  background: linear-gradient(135deg, var(--orange-900), var(--orange-700));
  color: var(--white);
  padding: var(--space-xs) var(--space-md);
  font-size: var(--font-size-sm);
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  border-radius: var(--radius-full);
  margin-bottom: var(--space-lg);
}

/* ========== HEADINGS ========== */
article h2 {
  font-size: var(--font-size-3xl);
  font-weight: 800;
  color: var(--blue-m-900);
  margin: var(--space-2xl) 0 var(--space-lg) 0;
  line-height: 1.2;
}

article h2:first-of-type {
  margin-top: 0;
}

article h3 {
  font-size: var(--font-size-2xl);
  font-weight: 700;
  color: var(--gray-900);
  margin: var(--space-xl) 0 var(--space-md) 0;
  line-height: 1.3;
}

article h4 {
  font-size: var(--font-size-xl);
  font-weight: 600;
  color: var(--gray-700);
  margin: var(--space-lg) 0 var(--space-sm) 0;
  line-height: 1.4;
}

/* ========== CALLOUTS ========== */
.callout {
  background: var(--gray-100);
  border-left: 4px solid var(--orange-900);
  padding: var(--space-md) var(--space-lg);
  margin: var(--space-lg) 0;
  border-radius: 0 var(--radius-md) var(--radius-md) 0;
}

.callout.accent {
  background: linear-gradient(135deg, var(--orange-100), var(--white));
  border-left-color: var(--orange-900);
}

.callout.info {
  background: #EFF6FF;
  border-left-color: var(--info);
}

.callout.success {
  background: #F0FDF4;
  border-left-color: var(--success);
}

.callout.warning {
  background: #FFFBEB;
  border-left-color: var(--warning);
}

/* ========== BLACK FRIDAY CALLOUT ========== */
.bf-callout {
  background: linear-gradient(135deg, var(--blue-m-900) 0%, #2D1B69 100%);
  color: var(--white);
  padding: var(--space-md) var(--space-lg);
  margin: var(--space-lg) 0;
  border-radius: var(--radius-lg);
  font-size: var(--font-size-md);
  position: relative;
  overflow: hidden;
}

.bf-callout::before {
  content: '';
  position: absolute;
  top: 0;
  right: 0;
  width: 100px;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255,96,0,0.2));
}

.bf-callout strong {
  color: var(--orange-500);
}

.bf-callout a {
  color: var(--orange-300);
  font-weight: 600;
}

.bf-callout a:hover {
  color: var(--orange-100);
}

/* ========== TABLA DE CONTENIDOS (TOC) ========== */
.toc {
  background: var(--gray-100);
  border: 1px solid var(--gray-200);
  border-radius: var(--radius-lg);
  padding: var(--space-lg);
  margin: var(--space-xl) 0;
}

.toc h4 {
  margin: 0 0 var(--space-md) 0;
  font-size: var(--font-size-lg);
  color: var(--blue-m-900);
}

.toc a {
  display: block;
  padding: var(--space-xs) 0;
  color: var(--gray-700);
  text-decoration: none;
  border-bottom: 1px solid var(--gray-200);
  transition: all 0.2s ease;
}

.toc a:last-child {
  border-bottom: none;
}

.toc a:hover {
  color: var(--orange-900);
  padding-left: var(--space-sm);
}

/* ========== TABLAS (.lt) ========== */
.lt {
  width: 100%;
  border-collapse: collapse;
  margin: var(--space-lg) 0;
  font-size: var(--font-size-sm);
  background: var(--white);
  border-radius: var(--radius-lg);
  overflow: hidden;
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--gray-200);
}

.lt .r {
  display: table-row;
}

.lt .r:first-child {
  background: var(--blue-m-900);
  color: var(--white);
  font-weight: 600;
}

.lt .r:first-child .c {
  padding: var(--space-md) var(--space-lg);
}

.lt .c {
  display: table-cell;
  padding: var(--space-sm) var(--space-lg);
  border-bottom: 1px solid var(--gray-200);
  vertical-align: middle;
}

.lt .r:last-child .c {
  border-bottom: none;
}

/* Tabla zebra */
.lt.zebra .r:nth-child(even) {
  background: var(--gray-100);
}

/* Columnas */
.lt.cols-2 .c { width: 50%; }
.lt.cols-3 .c { width: 33.333%; }
.lt.cols-4 .c { width: 25%; }
.lt.cols-5 .c { width: 20%; }
.lt.cols-7 .c { width: 14.285%; }

/* ========== GRID LAYOUT ========== */
.grid {
  display: grid;
  gap: var(--space-lg);
  margin: var(--space-lg) 0;
}

.grid.cols-2 {
  grid-template-columns: repeat(2, 1fr);
}

.grid.cols-3 {
  grid-template-columns: repeat(3, 1fr);
}

.grid.cols-4 {
  grid-template-columns: repeat(4, 1fr);
}

@media (max-width: 768px) {
  .grid.cols-2,
  .grid.cols-3,
  .grid.cols-4 {
    grid-template-columns: 1fr;
  }
}

/* ========== CARDS ========== */
.card {
  background: var(--white);
  border: 1px solid var(--gray-200);
  border-radius: var(--radius-lg);
  padding: var(--space-lg);
  transition: all 0.2s ease;
  display: flex;
  flex-direction: column;
  height: 100%;
}

.card:hover {
  border-color: var(--orange-300);
  box-shadow: var(--shadow-md);
}

.card h4 {
  margin-top: 0;
  color: var(--blue-m-900);
}

.card .why {
  color: var(--gray-500);
  font-size: var(--font-size-sm);
  margin: var(--space-sm) 0;
  flex-grow: 1;
}

.card .btns {
  margin-top: auto;
  padding-top: var(--space-md);
}

/* ========== CARD DESTACADO (NUEVO v4.5.0) ========== */
.card.destacado {
  border: 2px solid var(--orange-900);
  position: relative;
  box-shadow: var(--shadow-md);
}

.card.destacado::before {
  content: "⭐ RECOMENDADO";
  position: absolute;
  top: -12px;
  right: var(--space-md);
  background: var(--orange-900);
  color: var(--white);
  padding: var(--space-xs) var(--space-sm);
  font-size: var(--font-size-xs);
  font-weight: 700;
  border-radius: var(--radius-full);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

/* ========== PRODUCT MODULE (NUEVO v4.5.0) ========== */
.product-module {
  padding: var(--space-lg);
  margin: var(--space-lg) 0;
  border-radius: var(--radius-lg);
  border: 1px solid var(--gray-200);
  background: var(--white);
}

.product-module .label {
  display: block;
  font-size: var(--font-size-xs);
  font-weight: 700;
  color: var(--gray-500);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: var(--space-xs);
}

.price-tag {
  display: inline-block;
  background: var(--orange-900);
  color: var(--white);
  padding: var(--space-xs) var(--space-md);
  border-radius: var(--radius-md);
  font-weight: 700;
  font-size: var(--font-size-xl);
  margin: var(--space-sm) 0;
}

.price-tag.large {
  font-size: var(--font-size-2xl);
  padding: var(--space-sm) var(--space-lg);
}

/* ========== BADGES ========== */
.badges {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-sm);
  margin: var(--space-md) 0;
}

.badge {
  display: inline-block;
  background: var(--gray-100);
  color: var(--gray-700);
  padding: var(--space-xs) var(--space-sm);
  font-size: var(--font-size-xs);
  font-weight: 500;
  border-radius: var(--radius-full);
}

.badge.primary {
  background: var(--orange-100);
  color: var(--orange-900);
}

.badge.success {
  background: #DCFCE7;
  color: #166534;
}

.badge.info {
  background: #DBEAFE;
  color: #1E40AF;
}

/* ========== BOTONES ========== */
.btns {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-md);
  margin: var(--space-lg) 0;
}

.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: var(--space-sm) var(--space-lg);
  font-size: var(--font-size-md);
  font-weight: 600;
  text-decoration: none;
  border-radius: var(--radius-md);
  transition: all 0.2s ease;
  cursor: pointer;
  border: 2px solid transparent;
}

.btn.primary {
  background: var(--orange-900);
  color: var(--white);
}

.btn.primary:hover {
  background: var(--orange-700);
}

.btn.ghost {
  background: transparent;
  color: var(--orange-900);
  border-color: var(--orange-900);
}

.btn.ghost:hover {
  background: var(--orange-100);
}

/* ========== FAQs ========== */
.faqs {
  margin: var(--space-xl) 0;
}

.faqs .q {
  font-weight: 700;
  color: var(--blue-m-900);
  padding: var(--space-md) 0 var(--space-sm) 0;
  border-bottom: 2px solid var(--orange-900);
  margin-bottom: var(--space-sm);
}

.faqs .q::before {
  content: '❓ ';
}

.faqs .a {
  padding: var(--space-sm) 0 var(--space-lg) 0;
  color: var(--gray-700);
  border-bottom: 1px solid var(--gray-200);
}

.faqs .a:last-child {
  border-bottom: none;
}

/* ========== VERDICT BOX ========== */
.verdict-box {
  background: linear-gradient(135deg, var(--blue-m-900) 0%, #2D1B69 100%);
  color: var(--white);
  padding: var(--space-xl);
  margin: var(--space-2xl) 0;
  border-radius: var(--radius-xl);
  position: relative;
  overflow: hidden;
}

.verdict-box::before {
  content: '✅';
  position: absolute;
  top: var(--space-lg);
  right: var(--space-lg);
  font-size: 48px;
  opacity: 0.2;
}

.verdict-box h3 {
  color: var(--orange-500);
  margin-top: 0;
  font-size: var(--font-size-2xl);
}

.verdict-box ul {
  margin: var(--space-md) 0;
  padding-left: var(--space-lg);
}

.verdict-box li {
  margin-bottom: var(--space-sm);
  color: var(--gray-100);
}

.verdict-box a {
  color: var(--orange-300);
}

.verdict-box a:hover {
  color: var(--orange-100);
}

/* ========== SEPARADOR ========== */
.hr {
  border: none;
  border-top: 2px solid var(--gray-200);
  margin: var(--space-xl) 0;
}

.hr.accent {
  border-top-color: var(--orange-900);
}

/* ========== NOTA FINAL ========== */
.note {
  font-size: var(--font-size-sm);
  color: var(--gray-500);
  font-style: italic;
  margin-top: var(--space-xl);
  padding-top: var(--space-md);
  border-top: 1px solid var(--gray-200);
}

/* ========== LISTAS ========== */
article ul, article ol {
  margin: var(--space-md) 0;
  padding-left: var(--space-xl);
}

article li {
  margin-bottom: var(--space-sm);
  line-height: 1.6;
}

article ul li::marker {
  color: var(--orange-900);
}

article ol li::marker {
  color: var(--orange-900);
  font-weight: 600;
}

/* ========== IMÁGENES ========== */
article img {
  max-width: 100%;
  height: auto;
  border-radius: var(--radius-md);
  margin: var(--space-lg) 0;
}

/* ========== BLOCKQUOTE ========== */
article blockquote {
  border-left: 4px solid var(--orange-900);
  margin: var(--space-lg) 0;
  padding: var(--space-md) var(--space-lg);
  background: var(--gray-100);
  font-style: italic;
  color: var(--gray-700);
}

/* ========== CÓDIGO ========== */
article code {
  background: var(--gray-100);
  padding: 2px 6px;
  border-radius: var(--radius-sm);
  font-family: 'Fira Code', 'Consolas', monospace;
  font-size: 0.9em;
  color: var(--blue-m-700);
}

/* ========== RESPONSIVE ========== */
@media (max-width: 768px) {
  article h2 {
    font-size: var(--font-size-2xl);
  }
  
  article h3 {
    font-size: var(--font-size-xl);
  }
  
  .lt {
    display: block;
    overflow-x: auto;
  }
  
  .verdict-box {
    padding: var(--space-lg);
  }
  
  .verdict-box::before {
    font-size: 32px;
  }
  
  .card.destacado::before {
    font-size: 10px;
    padding: 3px 6px;
    top: -10px;
  }
}
</style>
"""

# CSS Fallback (versión mínima si el principal falla)
CSS_FALLBACK = """
<style>
:root{--orange-900:#FF6000;--blue-m-900:#170453;--white:#FFFFFF;--gray-100:#F5F5F5;--gray-200:#E5E5E5;--gray-700:#404040;--gray-900:#171717;}
article{font-family:system-ui,sans-serif;line-height:1.7;color:var(--gray-900);}
article h2{font-size:24px;font-weight:800;color:var(--blue-m-900);margin:32px 0 16px 0;}
article h3{font-size:20px;font-weight:700;margin:24px 0 12px 0;}
article a{color:var(--orange-900);}
.kicker{display:inline-block;background:var(--orange-900);color:var(--white);padding:4px 12px;font-size:12px;font-weight:700;text-transform:uppercase;border-radius:999px;margin-bottom:16px;}
.bf-callout{background:var(--blue-m-900);color:var(--white);padding:16px;border-radius:8px;margin:16px 0;}
.bf-callout a{color:#FFA366;}
.callout{background:var(--gray-100);border-left:4px solid var(--orange-900);padding:16px;margin:16px 0;}
.toc{background:var(--gray-100);border:1px solid var(--gray-200);border-radius:8px;padding:16px;margin:24px 0;}
.toc a{display:block;padding:4px 0;color:var(--gray-700);text-decoration:none;}
.lt{width:100%;border-collapse:collapse;margin:16px 0;border:1px solid var(--gray-200);}
.lt .r{display:table-row;}
.lt .r:first-child{background:var(--blue-m-900);color:var(--white);}
.lt .c{display:table-cell;padding:8px 16px;border-bottom:1px solid var(--gray-200);}
.card{border:1px solid var(--gray-200);border-radius:8px;padding:16px;background:#fff;display:flex;flex-direction:column;}
.card .why{color:var(--gray-700);font-size:14px;flex-grow:1;}
.card .btns{margin-top:auto;}
.card.destacado{border:2px solid var(--orange-900);position:relative;}
.card.destacado::before{content:"⭐ RECOMENDADO";position:absolute;top:-10px;right:10px;background:var(--orange-900);color:#fff;padding:4px 8px;font-size:11px;font-weight:700;border-radius:999px;}
.product-module{padding:16px;margin:16px 0;border-radius:8px;border:1px solid var(--gray-200);}
.product-module .label{font-size:11px;font-weight:700;color:var(--gray-700);text-transform:uppercase;}
.price-tag{display:inline-block;background:var(--orange-900);color:#fff;padding:4px 12px;border-radius:4px;font-weight:700;font-size:18px;}
.faqs .q{font-weight:700;color:var(--blue-m-900);padding:12px 0 8px 0;border-bottom:2px solid var(--orange-900);}
.faqs .a{padding:8px 0 16px 0;border-bottom:1px solid var(--gray-200);}
.verdict-box{background:var(--blue-m-900);color:var(--white);padding:24px;border-radius:12px;margin:32px 0;}
.verdict-box h3{color:#FFA366;margin-top:0;}
.verdict-box a{color:#FFC299;}
.note{font-size:14px;color:var(--gray-700);font-style:italic;margin-top:24px;padding-top:12px;border-top:1px solid var(--gray-200);}
</style>
"""


# ============================================================================
# TONO DE MARCA - v4.5.0 REBALANCEADO
# Orientado a SOLUCIONES, siempre con ALTERNATIVAS
# ============================================================================

BRAND_TONE = """
## NUESTRA PERSONALIDAD

### 🧠 Expertos que orientan
- Sabemos de lo que hablamos y lo usamos para AYUDAR a decidir.
- No vamos de "listillos". Vamos de "te oriento para que encuentres lo ideal".
- Podemos hablar con un techie de tú a tú o con alguien que empieza.
- Ejemplo: "Este monitor tiene 144Hz. Traducción gamer: partidas más fluidas. Perfecto para shooters y competitivo."

### 🧡 Frikis que comparten pasión
- Venimos de ahí. Y nos encanta.
- Nos flipan los gadgets, los memes tech, el humor de internet.
- Compartimos el entusiasmo del cliente por la tecnología.
- Ejemplo: "Si eres de los que disfruta montando su propio PC, este kit te va a encantar."

### ⚡ Rápidos y resolutivos
- Somos ágiles en atención, logística, resolución. Pero sin sonar como una centralita.
- Cada mensaje tiene intención: ayudar a tomar la mejor decisión.
- Ejemplo: "Tu pedido ya va en camino. Mañana lo tienes listo para estrenar."

### 😈 Con chispa, sin pasarse
- No nos tomamos todo demasiado en serio. Pero sabemos cuándo sí.
- Tenemos humor, picamos, pero nunca a costa del cliente ni del producto.
- Ejemplo: "No lo llamamos ofertón. Lo llamamos 'después no digas que no te avisamos'."

### 🤝 Honestos y constructivos
- Somos transparentes. Sin letras pequeñas. Sin drama.
- PERO siempre orientamos hacia soluciones. Si algo no encaja, ofrecemos alternativas.
- NUNCA dejamos al cliente sin opción. SIEMPRE hay algo para él en nuestro catálogo.
- Ejemplo: "Si tu prioridad es la portabilidad, este modelo de 14'' te encajará mejor."

### 🙋 Cercanos y profesionales
- No usamos diminutivos tipo "envíito" ni emojis a lo loco.
- Somos naturales, cálidos y humanos. Como cuando hablas con alguien que quiere ayudarte.
- Ejemplo: "¿No tienes claro cuál elegir? Te cuento las diferencias clave."

## PRINCIPIOS PRÁCTICOS

| Principio | Qué significa | Ejemplo |
|-----------|---------------|---------|
| Orientamos, no juzgamos | Ayudamos a encontrar la opción correcta | "Para gaming competitivo, esta gráfica te dará los fps que necesitas." |
| Siempre hay alternativa | Nunca dejamos al cliente sin camino | "Si buscas algo más económico, esta opción también es excelente." |
| Specs → Beneficios | Traducimos características a ventajas | "12GB de VRAM = juegos en 4K sin problemas." |
| Entusiasmo genuino | Compartimos la emoción por la tech | "Este lanzamiento es de los que merece la pena." |

## LO QUE SÍ HACEMOS ✅
- Orientar hacia la mejor opción para cada usuario
- Ofrecer alternativas cuando algo no encaja perfectamente
- Traducir especificaciones a beneficios prácticos
- Mostrar entusiasmo genuino por los productos
- Contextualizar el valor: por qué merece la pena
- Facilitar la decisión de compra

## LO QUE EVITAMOS ❌
- Frases que alejen de la compra ("no sirve para", "evita si", "no recomendable")
- Dejar al cliente sin alternativas
- Tono condescendiente o de "experto que juzga"
- Listar desventajas sin contexto ni solución
- Negatividad gratuita sobre productos de nuestro catálogo
- Comparaciones que desprecien opciones que vendemos
"""


# ============================================================================
# GUÍAS DETALLADAS DE VOZ DE MARCA
# ============================================================================

BRAND_VOICE_GUIDELINES: Dict[str, any] = {
    'mission': "Ofrecer la mejor experiencia de recomendación y compra para productos y servicios tecnológicos.",
    
    'personality_traits': [
        {
            'trait': 'Expertos que orientan',
            'emoji': '🧠',
            'description': 'Usamos nuestro conocimiento para ayudar, no para impresionar.',
            'example': 'Este monitor tiene 144Hz. Traducción gamer: partidas más fluidas.'
        },
        {
            'trait': 'Frikis que comparten pasión',
            'emoji': '🧡',
            'description': 'Compartimos el entusiasmo del cliente por la tecnología.',
            'example': 'Si eres de los que disfruta montando su propio PC, este kit te va a encantar.'
        },
        {
            'trait': 'Rápidos y resolutivos',
            'emoji': '⚡',
            'description': 'Cada mensaje tiene intención: ayudar a decidir.',
            'example': 'En resumen: ideal para gaming, más que suficiente para trabajo.'
        },
        {
            'trait': 'Con chispa',
            'emoji': '😈',
            'description': 'Humor y cercanía sin pasarse.',
            'example': 'Este portátil no es el más barato, pero es de los que no te arrepientes.'
        },
        {
            'trait': 'Honestos y constructivos',
            'emoji': '🤝',
            'description': 'Transparentes, pero siempre con alternativas.',
            'example': 'Si tu prioridad es portabilidad, el modelo de 14" te encajará mejor.'
        },
        {
            'trait': 'Cercanos y profesionales',
            'emoji': '🙋',
            'description': 'Como hablar con alguien que quiere ayudarte.',
            'example': '¿No tienes claro cuál elegir? Te cuento las diferencias clave.'
        },
    ],
    
    'practical_principles': [
        {
            'principle': 'Orientamos, no juzgamos',
            'meaning': 'Ayudamos a encontrar la opción correcta',
            'example': 'Para gaming competitivo, esta gráfica te dará los fps que necesitas.'
        },
        {
            'principle': 'Siempre hay alternativa',
            'meaning': 'Nunca dejamos al cliente sin camino',
            'example': 'Si buscas algo más económico, esta opción también es excelente.'
        },
        {
            'principle': 'Specs → Beneficios',
            'meaning': 'Traducimos características a ventajas',
            'example': '12GB de VRAM = juegos en 4K sin problemas.'
        },
        {
            'principle': 'Entusiasmo genuino',
            'meaning': 'Compartimos la emoción por la tech',
            'example': 'Este lanzamiento es de los que merece la pena.'
        },
    ],
    
    'do_list': [
        'Orientar hacia la mejor opción para cada usuario',
        'Ofrecer alternativas cuando algo no encaja',
        'Traducir especificaciones a beneficios prácticos',
        'Mostrar entusiasmo genuino por los productos',
        'Contextualizar el valor de cada producto',
        'Facilitar la decisión de compra',
    ],
    
    'dont_list': [
        'Frases que alejen de la compra',
        'Dejar al cliente sin alternativas',
        'Tono condescendiente',
        'Listar desventajas sin contexto',
        'Negatividad gratuita',
        'Despreciar opciones del catálogo',
    ],
}


# ============================================================================
# INSTRUCCIONES ANTI-IA (evitar signos de escritura artificial)
# ============================================================================

INSTRUCCIONES_ANTI_IA = """
## ❌ EVITAR SIGNOS DE ESCRITURA CON IA

### FRASES PROHIBIDAS (nunca las uses):
- "En el mundo actual..." / "En la era digital..."
- "Sin lugar a dudas..." / "Es importante destacar..."
- "Cabe mencionar que..." / "Es fundamental..."
- "A la hora de..." / "En lo que respecta a..."
- "Ofrece una experiencia..." / "Brinda la posibilidad..."
- "Esto se traduce en..." / "Lo que permite..."
- "Ya sea... como..." / "Tanto... como..."

### PATRONES A EVITAR:
- Adjetivos vacíos: "increíble", "revolucionario", "impresionante", "excepcional"
- Repetir la misma estructura en cada párrafo
- Listas interminables sin personalidad ni opinión
- Conclusiones que solo resumen lo dicho sin aportar nada nuevo
- Frases que podrían ser de cualquier tienda genérica
- Tono corporativo o institucional
- Empezar párrafos siempre igual

### ✅ SÍ HACER:
- Tutear al lector de forma natural
- Usar analogías tech y referencias que nuestro público entiende
- Variar la estructura de los párrafos
- Añadir detalles específicos, no generalidades
- El veredicto debe aportar valor real: recomendar, orientar, decidir
"""


# ============================================================================
# INSTRUCCIONES DE ORIENTACIÓN POSITIVA - NUEVO v4.5.0
# ============================================================================

INSTRUCCIONES_ORIENTACION_POSITIVA = """
## 🎯 PRINCIPIO CLAVE: SIEMPRE ORIENTAR, NUNCA DISUADIR

### TRANSFORMACIONES OBLIGATORIAS:

Cuando quieras mencionar una limitación, TRANSFORMA la frase:

| ❌ NUNCA escribas | ✅ SIEMPRE escribe |
|-------------------|---------------------|
| "No sirve para gaming" | "Perfecto para productividad; para gaming, explora nuestra gama gaming" |
| "No es recomendable si..." | "Ideal para X; si buscas Y, te encajará mejor [alternativa]" |
| "El problema es que..." | "Ten en cuenta que... esto lo compensa con..." |
| "Evita este producto si..." | "Este producto brilla en... Para otros usos, considera..." |
| "No vale la pena" | "Merece la pena si tu prioridad es X" |
| "Es demasiado caro" | "Es una inversión que se justifica por..." |
| "Le falta..." | "Incluye lo esencial; para funciones extra, la gama superior ofrece..." |
| "No hay opciones en este rango" | "En este rango tenemos X; para Y, te recomendamos explorar..." |

### EJEMPLOS PRÁCTICOS:

**Contexto:** Chromebook básico
- ❌ "Chrome OS no sirve para juegos ni software profesional"
- ✅ "Chrome OS es ideal para navegación, Google Workspace y streaming. Para gaming o software Windows, nuestra gama de portátiles Windows te ofrece más flexibilidad."

**Contexto:** Producto de gama entrada
- ❌ "No esperes gran rendimiento"
- ✅ "Cubre perfectamente las necesidades básicas. Si necesitas más potencia, la gama media ofrece un salto notable."

**Contexto:** Producto premium
- ❌ "Es caro y solo para profesionales"
- ✅ "Una inversión que se nota desde el primer uso. Diseñado para quienes exigen el máximo."

### REGLA DE ORO:
Cada frase debe ACERCAR al usuario a una compra en PcComponentes.
Si algo no encaja, la solución es OTRA opción de nuestro catálogo.
NUNCA dejamos al cliente sin camino hacia adelante.
"""


# ============================================================================
# INSTRUCCIONES SEGÚN DATOS DISPONIBLES - ACTUALIZADO v4.5.0
# Alineadas con datos reales del scraping (sin ventajas/desventajas de usuarios)
# ============================================================================

INSTRUCCIONES_CON_DATOS_PRODUCTO = """
## 📦 CÓMO USAR LOS DATOS DEL PRODUCTO

Tienes acceso a información REAL del producto desde el scraping de PcComponentes.

### 📋 DATOS DISPONIBLES Y CÓMO USARLOS:

**1. NOMBRE Y MARCA**
- Úsalos naturalmente, sin repetir el nombre completo constantemente
- Menciona la marca cuando aporte valor (reconocimiento, calidad)

**2. PRECIO**
- Destaca el valor: "Por solo X€ tienes..."
- Si es competitivo: "A este precio, difícil encontrar algo mejor"
- ENFOQUE POSITIVO siempre sobre el precio

**3. ESPECIFICACIONES TÉCNICAS**
- TRADUCE cada spec a un BENEFICIO práctico para el usuario
- Ejemplos de traducción:
  - "DPI 1200-7200" → "Ajustas la precisión según el juego"
  - "Interruptores mecánicos" → "Cada pulsación se siente precisa y satisfactoria"
  - "RGB" → "Personaliza la iluminación para tu setup"
  - "16GB RAM" → "Multitarea fluida incluso con muchas apps abiertas"
  - "144Hz" → "Partidas más fluidas, sin tirones"
  - "512GB SSD" → "Espacio de sobra y arranque en segundos"

**4. DESCRIPCIÓN DEL FABRICANTE**
- Úsala como BASE pero reescribe con tono PcComponentes
- Añade contexto: para quién es ideal, en qué situaciones brilla
- NUNCA copies literalmente párrafos enteros

**5. VALORACIÓN MEDIA**
- Si es 4.0 o superior: "Los usuarios lo valoran con X/5 ⭐"
- Si es inferior a 4.0: No la menciones, enfócate en características
- Usa la valoración como prueba social, no como argumento principal

### 🎯 ENFOQUE DE REDACCIÓN:

Para cada característica, responde:
1. ¿Qué ES? (la spec técnica)
2. ¿Qué SIGNIFICA? (beneficio práctico)
3. ¿Para QUIÉN es ideal? (perfil de usuario)

### 🚫 LO QUE NO DEBES HACER:
- Inventar características que no están en los datos
- Añadir "contras" o "desventajas" no mencionadas por el fabricante
- Comparar negativamente con otros productos
- Usar frases como "el único inconveniente es..." o "lo malo es que..."

### ✅ SI ALGO NO ENCAJA CON UN PERFIL:
En lugar de: "No es recomendable para gaming profesional"
Escribe: "Ideal para gaming casual y entretenimiento. Para competitivo, echa un vistazo a nuestra gama gaming pro."

SIEMPRE ofrece alternativa. NUNCA dejes al usuario sin opción.
"""

INSTRUCCIONES_SIN_DATOS_PRODUCTO = """
## 📝 CREAR CONTENIDO SIN DATOS ESPECÍFICOS

No tienes datos específicos del producto, pero puedes crear contenido excelente.

### ESTRATEGIAS:

**1. Céntrate en la KEYWORD y el ARQUETIPO**
- Son tu guía principal para estructura y enfoque
- El arquetipo define el tipo de contenido (review, guía, comparativa...)

**2. Habla de la CATEGORÍA**
- Qué busca alguien interesado en este tipo de producto
- Qué características son importantes en esta categoría
- Rangos de precio típicos y qué esperar en cada uno

**3. Da CONSEJOS PRÁCTICOS**
- Qué debería considerar el comprador
- Cómo elegir según su caso de uso
- Qué preguntas hacerse antes de comprar

**4. ORIENTA hacia nuestro catálogo**
- "En PcComponentes encontrarás opciones desde X€"
- "Nuestra selección incluye las mejores marcas"
- Enlaces a categorías relevantes

### TONO:
- Mismo tono PcComponentes: cercano, experto, con chispa
- Como si recomendaras algo a un amigo
- Entusiasmo por la tecnología

### ESTRUCTURA:
- Introduce el tema con gancho (NO "En el mundo actual...")
- Desarrolla con información útil y práctica
- Orienta hacia opciones de nuestro catálogo
- Cierra con veredicto que ayude a decidir

### SI NO SABES ALGO ESPECÍFICO:
- No lo inventes
- Usa frases como "depende de tu uso" o "según tus necesidades"
- Orienta hacia la consulta en la ficha de producto
"""


# ============================================================================
# FUNCIONES DE TONO PARA PROMPTS
# ============================================================================

def get_tone_instructions(has_product_data: bool = False) -> str:
    """
    Genera las instrucciones de tono completas para un prompt.
    
    Args:
        has_product_data: Si hay datos de producto disponibles
        
    Returns:
        String con todas las instrucciones de tono
    """
    base = f"""
# TONO DE MARCA PCCOMPONENTES

{BRAND_TONE}

{INSTRUCCIONES_ANTI_IA}

{INSTRUCCIONES_ORIENTACION_POSITIVA}
"""
    
    if has_product_data:
        return base + INSTRUCCIONES_CON_DATOS_PRODUCTO
    else:
        return base + INSTRUCCIONES_SIN_DATOS_PRODUCTO


def get_system_prompt_base() -> str:
    """Genera el system prompt base para todas las etapas."""
    return """Eres un redactor SEO experto de PcComponentes, la tienda líder de tecnología en España.

MISIÓN:
Crear contenido que AYUDE al usuario a encontrar el producto perfecto para él.
Cada palabra debe acercarle a una decisión de compra informada y satisfactoria.

TONO DE MARCA:
- Expertos que orientan: usamos conocimiento para AYUDAR, no para impresionar
- Frikis que comparten pasión: entusiasmo genuino por la tecnología
- Honestos y constructivos: transparentes, pero SIEMPRE con alternativas
- Cercanos: como hablar con alguien que quiere ayudarte de verdad

PRINCIPIOS CLAVE:
1. SIEMPRE orientar hacia soluciones, NUNCA disuadir
2. Si algo no encaja, ofrecer alternativa de nuestro catálogo
3. Traducir specs técnicas a beneficios prácticos
4. Mostrar entusiasmo por los productos

PROHIBIDO:
- "En el mundo actual...", "Sin lugar a dudas...", "Es importante destacar..."
- Frases que alejen de la compra ("no sirve para", "evita si", "no recomendable")
- Listar "contras" o "desventajas" sin ofrecer alternativas
- Dejar al usuario sin opción de compra

FORMATO:
- Genera HTML puro, NUNCA uses ```html ni marcadores markdown
- Usa las clases CSS definidas (.callout, .toc, .lt, .verdict-box, etc.)
- Estructura clara con H2/H3 para SEO
- Incluye enlaces internos a productos y categorías"""


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    # Versión
    '__version__',
    
    # Información de marca
    'BRAND_NAME',
    'BRAND_DOMAIN',
    'BRAND_TAGLINE',
    
    # Colores
    'BRAND_COLORS',
    
    # CSS
    'CSS_CMS_COMPATIBLE',
    'CSS_FALLBACK',
    
    # Tono de marca
    'BRAND_TONE',
    'BRAND_VOICE_GUIDELINES',
    
    # Instrucciones para prompts
    'INSTRUCCIONES_ANTI_IA',
    'INSTRUCCIONES_ORIENTACION_POSITIVA',
    'INSTRUCCIONES_CON_DATOS_PRODUCTO',
    'INSTRUCCIONES_SIN_DATOS_PRODUCTO',
    'get_tone_instructions',
    'get_system_prompt_base',
]
