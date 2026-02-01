import streamlit as st
import asyncio
import sys
import os
import nest_asyncio
from pathlib import Path

# --- CONFIGURACIÓN CRÍTICA PARA WINDOWS + PLAYWRIGHT ---
# Windows necesita 'ProactorEventLoop' para lanzar subprocesos (el navegador).
# Streamlit a veces usa 'SelectorEventLoop' por defecto, lo que causa el error "NotImplementedError".
if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

# Aplicar parche para permitir bucles anidados (necesario para Streamlit)
nest_asyncio.apply()
# -------------------------------------------------------

# --- CONFIGURACIÓN DE PATH ---
# Truco para que encuentre tus módulos de backend
current_dir = Path(__file__).parent.parent.parent if "src" in str(Path(__file__)) else Path(__file__).parent
sys.path.append(str(current_dir))

try:
    from src.core.scraper import create_scraper
    from src.core.analyzer import create_analyzer
    from src.core.downloader import ensure_model_available
    from src.utils.logger import PrismaLogger
except ImportError as e:
    st.error(f"Error importando backend: {e}")
    st.stop()

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="PRISMA - Investigador AI",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS personalizados (Modo Oscuro/Violeta)
st.markdown("""
<style>
    .stApp {
        background-color: #0F1115;
        color: #F1F5F9;
    }
    .stButton>button {
        background-color: #8B5CF6;
        color: white;
        border-radius: 8px;
        border: none;
    }
    .stButton>button:hover {
        background-color: #7C3AED;
    }
    div[data-testid="stMarkdownContainer"] p {
        font-size: 1.1em;
    }
</style>
""", unsafe_allow_html=True)

# --- ESTADO DE LA APLICACIÓN ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "scraped_content" not in st.session_state:
    st.session_state.scraped_content = None

# --- FUNCIONES ASÍNCRONAS ---
async def run_investigation(url):
    """Ejecuta el pipeline completo: Scraping -> Análisis"""
    status_container = st.status("🔍 Iniciando investigación...", expanded=True)
    
    try:
        # 1. Scraping
        status_container.write("📡 Conectando al sitio web...")
        scraper = create_scraper(headless=True)
        result = await scraper.scrape_url(url)
        await scraper.close()
        
        if not result.success:
            status_container.update(label="Error en scraping", state="error")
            st.error(f"No se pudo leer el sitio: {result.error}")
            return

        status_container.write(f"✅ Contenido extraído ({len(result.markdown)} caracteres)")
        st.session_state.scraped_content = result.markdown
        
        # 2. Verificar Modelo
        status_container.write("🧠 Verificando motor de IA...")
        model_ready = await ensure_model_available()
        
        if not model_ready:
            status_container.update(label="Modelo no encontrado", state="error")
            st.error("El modelo de IA no está descargado. Ejecuta 'python download_brain.py' primero.")
            return

        # 3. Análisis
        status_container.write("🤖 Analizando y sintetizando información...")
        analyzer = create_analyzer()
        await analyzer.load_model()
        
        analysis = await analyzer.analyze_content(result.markdown)
        
        if analysis.success:
            status_container.update(label="¡Investigación Completada!", state="complete", expanded=False)
            return analysis.summary
        else:
            st.error(f"Error en análisis: {analysis.error}")
            
    except Exception as e:
        status_container.update(label="Error crítico", state="error")
        st.error(f"Ocurrió un error inesperado: {e}")

# --- INTERFAZ ---
def main():
    st.title("🔍 PRISMA")
    st.caption("Plataforma de Investigación Sintetizada mediante Modelos Avanzados")

    with st.sidebar:
        st.header("Configuración")
        url_input = st.text_input("URL Objetivo", placeholder="https://es.wikipedia.org/wiki/...")
        
        start_btn = st.button("🚀 Iniciar Investigación", use_container_width=True)
        
        st.divider()
        st.info("Backend: v2.1.4 (Stable)\nFrontend: Streamlit")

    # Área principal
    if start_btn and url_input:
        with st.spinner("Procesando..."):
            # Ejecutar loop asíncrono
            summary = asyncio.run(run_investigation(url_input))
            
            if summary:
                st.session_state.messages.append({"role": "assistant", "content": summary})

    # Mostrar resultados
    if st.session_state.scraped_content:
        with st.expander("Ver contenido crudo extraído (Markdown)", expanded=False):
            st.text(st.session_state.scraped_content[:2000] + "...")

    # Chat / Reporte
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

if __name__ == "__main__":
    main()