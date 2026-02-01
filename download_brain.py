import sys
import os
import asyncio

# Configurar path
current_dir = os.getcwd()
sys.path.append(current_dir)

try:
    from src.core.downloader import ModelDownloader
    from src.utils.logger import PrismaLogger
except ImportError as e:
    print(f"❌ Error de importación: {e}")
    sys.exit(1)

# Logger simple para ver progreso
logger = PrismaLogger("DOWNLOADER")

def progress_hook(progress: float, message: str):
    """Muestra una barra de progreso simple en la terminal"""
    bar_length = 30
    filled_length = int(bar_length * progress)
    bar = '█' * filled_length + '-' * (bar_length - filled_length)
    percent = progress * 100
    # Usamos \r para sobreescribir la línea
    sys.stdout.write(f'\r⬇️  {message} |{bar}| {percent:.1f}%')
    sys.stdout.flush()

async def download_brain():
    print("\n" + "="*50)
    print("🧠 DESCARGANDO MODELO DE IA (Qwen 2.5 3B)")
    print("="*50)
    print("⚠️  Esto descargará aprox. 1.8 GB.")
    print("☕  Ve por un café, esto dependerá de tu internet.\n")
    
    downloader = ModelDownloader()
    
    # Configurar callback visual
    downloader.set_progress_callback(progress_hook)
    
    success = await downloader.download_model()
    
    print("\n") # Salto de línea al final
    if success:
        print("✅ ¡Descarga completada exitosamente!")
        print("El modelo está listo en la carpeta 'assets/models'.")
    else:
        print("❌ La descarga falló.")

if __name__ == "__main__":
    try:
        asyncio.run(download_brain())
    except KeyboardInterrupt:
        print("\n\n🛑 Descarga cancelada por el usuario.")