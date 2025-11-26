"""
Brand Configuration - PcComponentes Content Generator
Versión 4.2.0

Configuración de marca: CSS del CMS, tono de voz, colores y guías de estilo.
Basado en el Manual de Tono de Marca oficial de PcComponentes.

Este módulo contiene:
- CSS_CMS_COMPATIBLE: Estilos completos para el CMS
- BRAND_TONE: Directrices de tono de voz
- BRAND_COLORS: Paleta de colores corporativos
- BRAND_VOICE_GUIDELINES: Guía detallada de comunicación

Autor: PcComponentes - Product Discovery & Content
"""

from typing import Dict, List

# ============================================================================
# VERSIÓN DEL MÓDULO
# ============================================================================

__version__ = "4.2.0"

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
# CSS COMPLETO COMPATIBLE CON CMS - v4.2.0
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
}

.card:hover {
  border-color: var(--orange-300);
  box-shadow: var(--shadow-md);
}

.card h4 {
  margin-top: 0;
  color: var(--blue-m-900);
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
.faqs .q{font-weight:700;color:var(--blue-m-900);padding:12px 0 8px 0;border-bottom:2px solid var(--orange-900);}
.faqs .a{padding:8px 0 16px 0;border-bottom:1px solid var(--gray-200);}
.verdict-box{background:var(--blue-m-900);color:var(--white);padding:24px;border-radius:12px;margin:32px 0;}
.verdict-box h3{color:#FFA366;margin-top:0;}
.verdict-box a{color:#FFC299;}
.note{font-size:14px;color:var(--gray-700);font-style:italic;margin-top:24px;padding-top:12px;border-top:1px solid var(--gray-200);}
</style>
"""


# ============================================================================
# TONO DE MARCA - BASADO EN MANUAL OFICIAL v2024
# ============================================================================

BRAND_TONE = """
# TONO DE MARCA PCCOMPONENTES

## MISIÓN
"Ofrecer la mejor experiencia de recomendación y compra para productos y servicios tecnológicos."

En PcComponentes NO vendemos productos, CREAMOS EXPERIENCIAS. Esta misión es una promesa en cada interacción:
- Cada persona que nos escribe, nos llama o compra, debe sentir que importa.
- No es un número de pedido. No es un "cliente más".
- Es alguien que nos elige y merece una experiencia diferente.

## NUESTRA PERSONALIDAD

### 🧠 Expertos sin ser pedantes
- Sabemos de lo que hablamos, pero no necesitamos demostrarlo con tecnicismos.
- No vamos de "listillos". Vamos de "te lo explico para que lo entiendas".
- Podemos hablar con un techie de tú a tú o con alguien que no sabe lo que es una RAM.
- Ejemplo: "Este monitor tiene 144Hz. Traducción gamer: partidas más fluidas que un combo bien hecho."

### 🧡 Frikis sin vergüenza
- Venimos de ahí. Y nos encanta.
- Nos flipan los gadgets, los memes tech, el humor de internet, los foros, los cables.
- No nos da miedo sonar diferentes. Porque lo somos.
- Ejemplo: "Comparado con este, tu portátil es Internet Explorer intentando cargar un vídeo en 2005."

### ⚡ Rápidos sin ser fríos
- Somos ágiles en atención, logística, resolución. Pero sin sonar como una centralita automática.
- Cada mensaje, por breve que sea, tiene intención. Tiene persona.
- Ejemplo: "Tu pedido ya va en camino. Y no vamos a negarlo: nos hace casi tanta ilusión como a ti."

### 😈 Canallas con sentido común
- No nos tomamos todo demasiado en serio. Pero sabemos cuándo sí hay que ponerse serios.
- Tenemos chispa, picamos con humor, nos permitimos un punto rebelde.
- Pero nunca a costa de un cliente, de una promesa o de una experiencia.
- Ejemplo: "No lo llamamos ofertón. Lo llamamos 'después no digas que no te hemos avisado'."

### 🤝 Honestos, pero no aburridos
- Somos transparentes. Sin letras pequeñas. Sin drama. Sin frases que suenan a copy legal.
- Pero no por eso hablamos como robots. La sinceridad también puede ser entretenida.
- Ejemplo: "No es el más potente del mundo, pero para clase, LoL y tu serie favorita, va más que sobrado."

### 🙋 Cercanos, pero no falsamente coleguillas
- No usamos diminutivos tipo "envíito" ni emojis a lo loco.
- No forzamos un tono que no va con nosotros.
- Somos naturales, cálidos y humanos. Como cuando hablas con alguien que quiere ayudarte de verdad.
- Ejemplo: "Si te cuadra, adelante. Si no, seguimos buscando. Lo bueno es que opciones hay, y estamos contigo."

## AXIOMAS DE COMUNICACIÓN

| Axioma | Cómo se traduce |
|--------|-----------------|
| Asesoramiento experto sin complicaciones | No usamos jerga si no hace falta. Damos respuestas útiles, personalizadas y con empatía. Hablamos con la misma naturalidad con la que recomendaríamos algo a un amigo. |
| Lo que buscas, al mejor precio | No basamos todo nuestro mensaje en el precio. El valor está en todo lo que hay alrededor: confianza, experiencia, agilidad. Somos honestos: ni promesas vacías ni letras pequeñas. |
| Recíbelo antes de que lo eches de menos | Somos proactivos. Si hay un retraso, avisamos. Si hay duda, resolvemos. Si algo cambia, lo contamos antes de que el cliente tenga que preguntar. |
| Cero problemas, solo soluciones | No escondemos el teléfono. No pedimos disculpas de manual. Damos soluciones reales. Hablamos con la responsabilidad de quien se hace cargo. |

## PRINCIPIOS PRÁCTICOS

| Principio | Qué significa | Ejemplo |
|-----------|---------------|---------|
| Hablamos claro | No adornamos lo que podemos explicar fácil | "12GB de gráfica dan para mucho. Si vas a jugar en 4K o editar vídeo como un pro, esta es tu aliada." |
| No vendemos humo | Preferimos ser honestos que sonar geniales | "No es gaming, pero para tareas del día a día, docs y maratones de Netflix, va sobrado." |
| Nos ponemos en su lugar | Pensamos en qué espera la persona al leer | "Sabemos que no era lo que esperabas. Por eso vamos a darte una solución cuanto antes." |
| Sumamos valor | Siempre dejamos al cliente mejor de lo que llegó | "Además del cambio, te activamos un descuento para tu próxima compra." |
| Humanizamos los canales | Cada canal debe sentirse vivo | En redes: agilidad y humor. En email: cuidado y precisión. En soporte: responsabilidad. |

## LO QUE SÍ HACEMOS ✅

- Hablamos como una persona real (no como una máquina de texto)
- Escribimos con empatía y cercanía, incluso si la situación es tensa
- Adaptamos el lenguaje según el nivel del usuario
- Sumamos siempre un plus: contexto, ayuda o calidez
- Añadimos un toque humano, incluso si usamos plantillas

## LO QUE EVITAMOS ❌

- Tono plano, impersonal, institucional o frío
- Automatismos que se notan (y desconectan)
- Explicaciones tipo "esto es lo que hay"
- Lenguaje excesivamente técnico si no lo necesita
- Mensajes que podrían ser intercambiables con cualquier otra tienda

## PARA CONTENIDO SEO/EDITORIAL

### Enfoque aspiracional
- Usar "Perfecto si..." en lugar de "Evita si..."
- Presentar beneficios, no limitaciones
- Ser honestos sin ser negativos

### Estructura recomendada
- Empezar con gancho que conecte con el usuario
- Desarrollar con información práctica y útil
- Cerrar con veredicto claro y accionable

### Lenguaje
- Tutear al lector
- Usar frases cortas y directas
- Incluir analogías tech cuando aporten valor
- Evitar repetición excesiva de keywords (naturalidad > SEO mecánico)
"""


# ============================================================================
# GUÍAS DETALLADAS DE VOZ DE MARCA
# ============================================================================

BRAND_VOICE_GUIDELINES: Dict[str, any] = {
    'mission': "Ofrecer la mejor experiencia de recomendación y compra para productos y servicios tecnológicos.",
    
    'personality_traits': [
        {
            'trait': 'Expertos sin ser pedantes',
            'emoji': '🧠',
            'description': 'Sabemos de lo que hablamos, pero no necesitamos demostrarlo con tecnicismos.',
            'example': 'Este monitor tiene 144Hz. Traducción gamer: partidas más fluidas que un combo bien hecho.'
        },
        {
            'trait': 'Frikis sin vergüenza',
            'emoji': '🧡',
            'description': 'Nos flipan los gadgets, los memes tech, el humor de internet. Y lo llevamos con orgullo.',
            'example': 'Comparado con este, tu portátil es Internet Explorer intentando cargar un vídeo en 2005.'
        },
        {
            'trait': 'Rápidos sin ser fríos',
            'emoji': '⚡',
            'description': 'Somos ágiles pero sin sonar como una centralita automática.',
            'example': 'Tu pedido ya va en camino. Y no vamos a negarlo: nos hace casi tanta ilusión como a ti.'
        },
        {
            'trait': 'Canallas con sentido común',
            'emoji': '😈',
            'description': 'Tenemos chispa, picamos con humor, pero nunca a costa del cliente.',
            'example': "No lo llamamos ofertón. Lo llamamos 'después no digas que no te hemos avisado'."
        },
        {
            'trait': 'Honestos, pero no aburridos',
            'emoji': '🤝',
            'description': 'Somos transparentes. Sin letras pequeñas. Pero la sinceridad también puede ser entretenida.',
            'example': 'No es el más potente del mundo, pero para clase, LoL y tu serie favorita, va más que sobrado.'
        },
        {
            'trait': 'Cercanos, pero no falsamente coleguillas',
            'emoji': '🙋',
            'description': 'No usamos diminutivos forzados. Somos naturales, cálidos y humanos.',
            'example': 'Si te cuadra, adelante. Si no, seguimos buscando. Lo bueno es que opciones hay, y estamos contigo.'
        },
    ],
    
    'axioms': {
        'expert_advice': {
            'title': 'Asesoramiento experto sin complicaciones',
            'tagline': 'Te recomendamos justo lo que necesitas, sin que tengas que entenderlo todo.',
            'application': 'No usamos jerga si no hace falta. Damos respuestas útiles, personalizadas y con empatía.'
        },
        'best_price': {
            'title': 'Lo que buscas, al mejor precio',
            'tagline': 'Los buenos precios no son nuestro diferencial, son un básico que cumplimos con nota.',
            'application': 'No basamos todo en el precio. El valor está en confianza, experiencia, agilidad.'
        },
        'fast_delivery': {
            'title': 'Recíbelo antes de que lo eches de menos',
            'tagline': 'Rápidos sí, pero sobre todo claros, flexibles y sin letra pequeña.',
            'application': 'Somos proactivos. Si hay un retraso, avisamos antes de que pregunten.'
        },
        'zero_problems': {
            'title': 'Cero problemas, solo soluciones',
            'tagline': 'Si algo va mal, lo resolvemos. Sin excusas, sin rodeos, sin complicaciones.',
            'application': 'No escondemos el teléfono. Damos soluciones reales con responsabilidad.'
        },
    },
    
    'do_list': [
        'Hablar como una persona real (no como una máquina de texto)',
        'Escribir con empatía y cercanía, incluso si la situación es tensa',
        'Adaptar el lenguaje según el nivel del usuario',
        'Sumar siempre un plus: contexto, ayuda o calidez',
        'Añadir un toque humano, incluso si usamos plantillas',
    ],
    
    'dont_list': [
        'Tono plano, impersonal, institucional o frío',
        'Automatismos que se notan (y desconectan)',
        'Explicaciones tipo "esto es lo que hay"',
        'Lenguaje excesivamente técnico si no lo necesita',
        'Mensajes que podrían ser intercambiables con cualquier otra tienda',
    ],
    
    'practical_principles': [
        {
            'principle': 'Hablamos claro',
            'meaning': 'No adornamos lo que podemos explicar fácil',
            'example': '12GB de gráfica dan para mucho. Si vas a jugar en 4K o editar vídeo como un pro, esta es tu aliada.'
        },
        {
            'principle': 'No vendemos humo',
            'meaning': 'Preferimos ser honestos que sonar geniales',
            'example': 'No es gaming, pero para tareas del día a día, docs y maratones de Netflix, va sobrado.'
        },
        {
            'principle': 'Nos ponemos en su lugar',
            'meaning': 'Pensamos en qué espera la persona al leer',
            'example': 'Sabemos que no era lo que esperabas. Por eso vamos a darte una solución cuanto antes.'
        },
        {
            'principle': 'Sumamos valor',
            'meaning': 'Siempre dejamos al cliente mejor de lo que llegó',
            'example': 'Además del cambio, te activamos un descuento para tu próxima compra.'
        },
        {
            'principle': 'Humanizamos los canales',
            'meaning': 'Cada canal debe sentirse vivo',
            'example': 'En redes: agilidad y humor. En email: cuidado y precisión. En soporte: responsabilidad.'
        },
    ],
    
    'seo_content_guidelines': {
        'approach': 'aspiracional',
        'use_instead_of': {
            'positive': 'Perfecto si...',
            'negative': 'Evita si...',
        },
        'structure': [
            'Empezar con gancho que conecte con el usuario',
            'Desarrollar con información práctica y útil',
            'Cerrar con veredicto claro y accionable',
        ],
        'language': [
            'Tutear al lector',
            'Usar frases cortas y directas',
            'Incluir analogías tech cuando aporten valor',
            'Evitar repetición excesiva de keywords (naturalidad > SEO mecánico)',
        ],
    },
}


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
]
