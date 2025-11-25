# Changelog

Todos los cambios notables de este proyecto se documentarán en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/),
y este proyecto adhiere a [Semantic Versioning](https://semver.org/lang/es/).

## [4.1.1] - 2025-01-XX

### ✨ Añadido
- Refactorización completa a arquitectura modular
- Modo reescritura con análisis competitivo automático
- Sistema de validación CMS v4.1.1 completo
- 18 arquetipos predefinidos con campos específicos
- Exportación ZIP de todas las etapas
- Panel de debug para desarrollo
- Documentación completa en README.md

### 🔧 Modificado
- Estructura de carpetas modularizada (config, core, prompts, ui, utils)
- Prompts externalizados en módulos separados
- CSS extraído a archivo independiente
- Gestión de estado tipada y estructurada
- Mejoras en UI de resultados con tabs

### 🐛 Corregido
- Validación de estructura HTML CMS-compatible
- Uso correcto de <span> en kicker (no <div>)
- Estructura de 3 articles obligatoria
- Título principal con H2 (no H1)
- Precisión de word count mejorada

### 🗑️ Eliminado
- Código monolítico de app_backup.py (3000+ líneas)
- CSS duplicado (4 instancias → 1)
- Prompts embebidos en código Python

## [4.0.0] - 2024-11-XX

### ✨ Añadido
- Versión inicial del Content Generator
- Flujo de 3 etapas (borrador, análisis, final)
- Arquetipos básicos
- Integración con Claude API

### 🔧 Modificado
- N/A (versión inicial)

## [Unreleased]

### 🔮 Planeado
- Externalización de prompts a Jinja2 templates
- Sistema de guardado de borradores
- Historial de generaciones
- Preview en tiempo real
- Integración directa con CMS
- Tests automatizados completos
- CI/CD pipeline
```

## 12. **`LICENSE`** (si es necesario)
```
MIT License o Proprietary según prefieras
```

---

## ✅ **Checklist Final de Archivos**
```
✅ Core Application
├── ✅ app.py
├── ✅ requirements.txt
├── ✅ requirements-dev.txt
├── ✅ runtime.txt
├── ✅ packages.txt (opcional)

✅ Configuration
├── ✅ .env.example
├── ✅ .gitignore
├── ✅ README.md
├── ✅ CHANGELOG.md
├── ✅ LICENSE (opcional)

✅ Streamlit Config
├── ✅ .streamlit/config.toml
├── ✅ .streamlit/secrets.toml.example

✅ Python Packages
├── ✅ config/__init__.py
├── ✅ core/__init__.py
├── ✅ prompts/__init__.py
├── ✅ ui/__init__.py
├── ✅ utils/__init__.py

✅ Modules (ya generados antes)
├── ✅ config/settings.py
├── ✅ config/archetipos.py
├── ✅ config/brand.py
├── ✅ config/cms_compatible.css
├── ✅ core/generator.py
├── ✅ core/scraper.py
├── ✅ prompts/new_content.py
├── ✅ prompts/rewrite.py
├── ✅ ui/sidebar.py
├── ✅ ui/inputs.py
├── ✅ ui/results.py
├── ✅ ui/rewrite.py
├── ✅ utils/html_utils.py
├── ✅ utils/state_manager.py
