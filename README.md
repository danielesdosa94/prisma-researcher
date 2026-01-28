# PRISMA - Investigación Automatizada

![Version](https://img.shields.io/badge/version-2.0.0-violet)
![Python](https://img.shields.io/badge/python-3.12+-blue)
![Flet](https://img.shields.io/badge/flet-0.21+-green)

**PRISMA** es una herramienta de escritorio para investigadores y creadores de contenido que necesitan procesar grandes cantidades de información web rápidamente.

## 🚀 Características

- **Scraping Web Inteligente**: Extrae contenido de múltiples URLs y lo convierte a Markdown limpio
- **Análisis con IA Local**: Procesa y sintetiza información usando un modelo de lenguaje local (Qwen 2.5 3B)
- **Privacy First**: Todo se ejecuta localmente, sin envío de datos a la nube
- **Interfaz Moderna**: Dark mode con estética "hacker-chic"

## 📦 Instalación

```bash
# Clonar repositorio
git clone https://github.com/your-repo/prisma.git
cd prisma

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# o: venv\Scripts\activate  # Windows

# Instalar dependencias
pip install -r requirements.txt

# Instalar Playwright browsers
playwright install chromium
```

## 🎮 Uso

```bash
# Ejecutar aplicación
python main.py
```

### Flujo de Trabajo

1. **Arrastra archivos** `.txt` o `.docx` con URLs, o pega URLs directamente
2. **Activa el switch** "Análisis con IA" si deseas generar un informe inteligente
3. **Presiona** "EJECUTAR INVESTIGACIÓN"
4. **Revisa** los resultados en la carpeta `output/`

## 🏗️ Estructura del Proyecto

```
prisma/
├── main.py                 # Punto de entrada
├── requirements.txt        # Dependencias
├── src/
│   ├── ui/
│   │   ├── theme.py       # Sistema de diseño (colores, tipografía)
│   │   └── app_layout.py  # Componentes de interfaz
│   ├── core/
│   │   ├── scraper.py     # Motor de web scraping
│   │   ├── analyzer.py    # Motor de análisis IA
│   │   └── downloader.py  # Descargador de modelo
│   └── utils/
│       ├── logger.py      # Sistema de logging
│       └── url_parser.py  # Utilidades de URLs
├── assets/
│   └── models/            # Modelos de IA (descargados bajo demanda)
└── output/                # Archivos generados
```

## 🎨 Tema Visual

| Elemento | Color |
|----------|-------|
| Background | `#0F1115` |
| Surface | `#1E2129` |
| Primary (Violeta) | `#8B5CF6` |
| Success | `#10B981` |
| Text | `#F1F5F9` |

## 📝 Notas Técnicas

### Arquitectura UI (Flet)

El proyecto sigue un patrón de **inyección de dependencias** para el `FilePicker`:

```python
# ❌ INCORRECTO - Causa "Red Box Error"
page.add(Column([
    FilePicker(),  # NO incluir en el árbol visual
    OtherContent(),
]))

# ✅ CORRECTO - FilePicker en overlay
file_picker = FilePicker()
page.overlay.append(file_picker)  # Agregar a overlay PRIMERO
layout = build_ui(file_picker)     # Pasar referencia
page.add(layout)
```

### Dimensiones Seguras

Para evitar "Gray Box" por colapso de layout:

- Usar `width=X` fijo en secciones laterales
- Solo usar `expand=True` en el contenedor que debe crecer
- Los componentes fijos (header, footer) tienen `height=X` explícito

## 🔧 Desarrollo

```bash
# Ejecutar en modo desarrollo con hot reload
flet run main.py -d

# Empaquetar como ejecutable
pyinstaller --onefile --windowed main.py
```

## 📄 Licencia

MIT License - Ver archivo `LICENSE` para más detalles.

---

Hecho con 💜 por el equipo Polígono Studio (Daniel Domínguez)