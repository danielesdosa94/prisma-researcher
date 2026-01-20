# 🔮 PRISMA - Automated Research Desktop App

> **Desktop First, Privacy First** - Una herramienta de investigación automatizada que funciona completamente offline.

![Version](https://img.shields.io/badge/version-1.0.0-violet)
![Python](https://img.shields.io/badge/python-3.12+-blue)
![License](https://img.shields.io/badge/license-MIT-green)

## 📋 Descripción

PRISMA es una aplicación de escritorio diseñada para investigadores y creadores de contenido que necesitan procesar grandes cantidades de información web rápidamente.

### Core Loop
1. **Input**: Arrastra URLs o archivos `.txt`/`.docx`
2. **Scraping**: Extrae contenido limpio en formato Markdown
3. **Análisis IA**: Una IA local analiza y sintetiza la información
4. **Output**: Genera un informe profesional

### Características
- ✅ 100% Offline después de la configuración inicial
- ✅ Sin suscripciones ni envío de datos a la nube
- ✅ IA local con modelo Qwen 2.5 3B
- ✅ Interfaz moderna Dark/Violet
- ✅ Descarga de IA bajo demanda (Lazy Loading)

## 🚀 Instalación

### Requisitos
- Python 3.12+
- Windows 10/11 (probado), Linux, macOS
- ~4GB RAM mínimo (~8GB recomendado para IA)
- ~2GB espacio en disco (con modelo IA)

### Pasos de Instalación

```bash
# 1. Clonar o descargar el proyecto
git clone <repo-url>
cd researcher_app

# 2. Crear entorno virtual
python -m venv venv

# 3. Activar entorno virtual
# Windows (Git Bash):
source venv/Scripts/activate
# Windows (CMD):
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# 4. Instalar dependencias
pip install -r requirements.txt

# 5. Instalar Playwright browsers
playwright install chromium

# 6. Ejecutar la aplicación
python main.py
```

## 🎨 Uso

### Modo Básico (Solo Scraping)
1. Abre PRISMA
2. Arrastra un archivo `.txt` con URLs o pégalas directamente
3. Selecciona "Solo Scraping (.md)"
4. Clic en **EJECUTAR INVESTIGACIÓN**
5. Los archivos `.md` se guardan en `/output`

### Modo Avanzado (Scraping + IA)
1. Selecciona "Scraping + Análisis IA"
2. Si es la primera vez, se descargará el modelo (~1.8 GB)
3. La IA analizará el contenido y generará un informe completo

## 📁 Estructura del Proyecto

```
researcher_app/
├── main.py                 # Punto de entrada
├── requirements.txt        # Dependencias
├── README.md              # Esta documentación
│
├── assets/
│   └── models/            # Modelo IA (se descarga bajo demanda)
│
├── src/
│   ├── ui/                # Interfaz de usuario (Flet)
│   │   ├── theme.py       # Colores, tipografía, espaciado
│   │   ├── components.py  # Componentes reutilizables
│   │   └── layout.py      # Layout principal
│   │
│   ├── core/              # Lógica de negocio
│   │   ├── scraper.py     # Motor de scraping (Playwright)
│   │   ├── analyzer.py    # Análisis IA (llama.cpp)
│   │   └── downloader.py  # Descarga del modelo
│   │
│   └── utils/             # Utilidades
│       ├── logger.py      # Sistema de logs
│       ├── file_manager.py # Gestión de archivos
│       └── url_parser.py  # Parsing de URLs
│
└── output/                # Resultados generados
```

## 🛠️ Stack Tecnológico

| Componente | Tecnología | Propósito |
|------------|------------|-----------|
| GUI | **Flet** | UI reactiva basada en Flutter |
| Scraping | **Playwright** | Renderizado JS, automatización browser |
| Conversión | **html2text** | HTML → Markdown |
| IA | **llama-cpp-python** | Inferencia LLM local |
| Modelo | **Qwen 2.5 3B** | LLM compacto y potente |

## 🎨 Sistema de Diseño

### Paleta de Colores

| Color | Hex | Uso |
|-------|-----|-----|
| Background | `#0F1115` | Fondo principal |
| Surface | `#1E2129` | Tarjetas, inputs |
| Primary | `#8B5CF6` | Acento (Electric Violet) |
| Success | `#10B981` | Estados exitosos |
| Text | `#F1F5F9` | Texto principal |

### Tipografía
- **UI**: Inter / Roboto
- **Código/Logs**: JetBrains Mono

## 📦 Empaquetado (Distribución)

Para crear un ejecutable standalone:

```bash
# Instalar PyInstaller
pip install pyinstaller

# Crear ejecutable
pyinstaller --onefile --windowed --icon=assets/icon.ico --name=PRISMA main.py
```

El ejecutable estará en `dist/PRISMA.exe`

## 🔧 Configuración Avanzada

### Cambiar modelo de IA

Edita `src/core/downloader.py`:

```python
@dataclass
class ModelInfo:
    repo_id: str = "TuRepo/TuModelo"
    filename: str = "modelo.gguf"
    size_gb: float = X.X
```

### Ajustar parámetros de scraping

Edita `src/core/scraper.py`:

```python
@dataclass
class ScraperConfig:
    timeout: int = 30000        # Timeout en ms
    delay_between_requests: float = 1.0  # Delay entre requests
    max_concurrent: int = 3     # Requests simultáneos
```

## 🐛 Solución de Problemas

### "Playwright no encuentra el browser"
```bash
playwright install chromium
```

### "Error de memoria al cargar modelo"
- Asegúrate de tener al menos 4GB de RAM disponibles
- Cierra otras aplicaciones pesadas

### "El scraping falla en ciertas páginas"
- Algunas páginas bloquean scrapers
- Incrementa el `timeout` en la configuración
- Verifica que la URL sea accesible manualmente

## 📄 Licencia

MIT License - Libre para uso personal y comercial.

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:
1. Fork el repositorio
2. Crea una rama para tu feature
3. Envía un Pull Request

---

**PRISMA** - Investigación inteligente, privacidad garantizada. 🔮
