"""
PRISMA - AI Analyzer
====================
Local LLM inference engine using llama-cpp-python.
Provides analysis and synthesis of scraped content.
"""

import asyncio
from typing import List, Optional, Callable
from dataclasses import dataclass
from pathlib import Path

try:
    from src.utils.logger import PrismaLogger
    from src.core.downloader import ModelDownloader
except ImportError:
    # Fallback for direct module testing
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))
    from src.utils.logger import PrismaLogger
    from src.core.downloader import ModelDownloader

logger = PrismaLogger("Analyzer")


@dataclass
class AnalysisConfig:
    """Configuration for the AI analyzer."""
    
    # Model parameters
    n_ctx: int = 4096          # Context window size
    n_threads: int = 4         # CPU threads to use
    n_gpu_layers: int = -1      # GPU layers (If there is a GPU available use it)
    
    # Generation parameters
    max_tokens: int = 2048     # Max output tokens
    temperature: float = 0.7   # Creativity (0.0 = deterministic)
    top_p: float = 0.9         # Nucleus sampling
    top_k: int = 40            # Top-k sampling
    repeat_penalty: float = 1.1  # Repetition penalty


@dataclass
class AnalysisResult:
    """Result of AI analysis."""
    
    success: bool
    summary: str = ""
    key_insights: List[str] = None
    recommendations: List[str] = None
    error: str = ""
    tokens_used: int = 0
    
    def __post_init__(self):
        if self.key_insights is None:
            self.key_insights = []
        if self.recommendations is None:
            self.recommendations = []


# System prompt for research analysis
ANALYSIS_SYSTEM_PROMPT = """Eres PRISMA, un asistente de investigación profesional. Tu tarea es analizar contenido web y generar informes claros y útiles.

INSTRUCCIONES:
1. Analiza el contenido proporcionado de forma objetiva
2. Identifica los puntos clave y hallazgos principales
3. Sintetiza la información en un resumen ejecutivo
4. Proporciona insights accionables cuando sea posible
5. Mantén un tono profesional y conciso

FORMATO DE RESPUESTA:
- Usa Markdown para estructurar tu respuesta
- Incluye secciones claras: Resumen, Puntos Clave, Conclusiones
- Cita fuentes específicas cuando sea relevante
- No inventes información que no esté en el contenido"""


class AIAnalyzer:
    """
    AI-powered content analyzer using local LLM.
    Provides summarization, insight extraction, and report generation.
    """
    
    def __init__(
        self,
        model_path: Optional[Path] = None,
        config: Optional[AnalysisConfig] = None
    ):
        """
        Initialize the analyzer.
        
        Args:
            model_path: Path to GGUF model file
            config: Analysis configuration
        """
        self.config = config or AnalysisConfig()
        self.model_path = model_path
        self._model = None
        self._is_loaded = False
        self._progress_callback: Optional[Callable[[str], None]] = None
    
    @property
    def is_loaded(self) -> bool:
        """Check if model is loaded in memory."""
        return self._is_loaded
    
    def set_progress_callback(
        self,
        callback: Callable[[str], None]
    ) -> None:
        """Set callback for progress updates."""
        self._progress_callback = callback
    
    def _notify(self, message: str) -> None:
        """Send progress notification."""
        if self._progress_callback:
            self._progress_callback(message)
    
    async def load_model(self, model_path: Optional[Path] = None) -> bool:
        """
        Load the LLM model into memory.
        
        Args:
            model_path: Path to model file (uses default if None)
        
        Returns:
            True if model loaded successfully
        """
        if self._is_loaded:
            logger.info("Model already loaded")
            return True
        
        path = model_path or self.model_path
        if path is None:
            # Try default location
            downloader = ModelDownloader()
            if not downloader.is_model_available():
                logger.error("Model not found. Please download first.")
                return False
            path = downloader.model_path
        
        self.model_path = path
        
        logger.info(f"Loading model: {path.name}")
        self._notify("Cargando modelo en memoria...")
        
        try:
            # Import here to avoid loading if not needed
            from llama_cpp import Llama
            
            # Load model in thread pool
            loop = asyncio.get_event_loop()
            
            def load_sync():
                return Llama(
                    model_path=str(path),
                    n_ctx=self.config.n_ctx,
                    n_threads=self.config.n_threads,
                    n_gpu_layers=self.config.n_gpu_layers,
                    verbose=False,
                )
            
            self._model = await loop.run_in_executor(None, load_sync)
            self._is_loaded = True
            
            logger.success("Model loaded successfully")
            self._notify("Modelo listo para análisis")
            return True
            
        except ImportError:
            logger.error("llama-cpp-python not installed")
            self._notify("Error: librería llama-cpp no instalada")
            return False
            
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            self._notify(f"Error: {str(e)[:50]}")
            return False
    
    def unload_model(self) -> None:
        """Unload model from memory."""
        if self._model:
            del self._model
            self._model = None
            self._is_loaded = False
            logger.info("Model unloaded")
    
    async def analyze_content(
        self,
        content: str,
        custom_prompt: Optional[str] = None
    ) -> AnalysisResult:
        """
        Analyze content using the LLM with smart truncation to fit context window.
        
        Args:
            content: Text content to analyze
            custom_prompt: Optional custom analysis prompt instructions
        
        Returns:
            AnalysisResult with summary and insights
        """
        if not self._is_loaded:
            logger.error("Model not loaded")
            return AnalysisResult(
                success=False,
                error="Model not loaded. Call load_model() first."
            )
        
        # --- LÓGICA DE RECORTE SEGURA (DINÁMICA) ---
        total_ctx = self.config.n_ctx          # Ej: 4096
        max_output = self.config.max_tokens    # Ej: 2048
        safety_margin = 200                    # Para wrappers y system prompt
        
        # 1. Calcular espacio disponible para entrada
        available_input_tokens = total_ctx - max_output - safety_margin
        
        # 2. Balancear si el espacio de entrada es muy pequeño
        # Si queda menos de 1000 tokens para leer, sacrificamos tokens de salida para permitir lectura
        if available_input_tokens < 1000:
            logger.warning("Configuración desbalanceada: Reduciendo max_tokens para permitir más entrada.")
            # Aseguramos al menos 2500 tokens para entrada
            target_input = min(2500, total_ctx - safety_margin - 500) 
            max_output = total_ctx - target_input - safety_margin
            available_input_tokens = target_input
            
        # 3. Convertir a caracteres (estimación conservadora: 1 token ≈ 3 chars para español/código)
        max_content_chars = int(available_input_tokens * 3)
        
        # 4. Truncar contenido
        if len(content) > max_content_chars:
            logger.warning(f"Contenido extenso ({len(content)} chars). Recortando a {max_content_chars} chars para ajustar a memoria.")
            # Mantenemos el inicio, que suele ser la introducción/resumen
            content = content[:max_content_chars] + "\n\n...[CONTENIDO TRUNCADO POR LÍMITE DE MEMORIA DEL MODELO]..."
        # -----------------------------------------------------------
        
        # Build prompt: Instructions + Content
        base_instruction = custom_prompt or "Analiza el siguiente contenido de investigación y genera un informe estructurado:"
        
        user_prompt = f"""{base_instruction}

---
CONTENIDO A ANALIZAR:
{content}
---"""
        
        messages = [
            {"role": "system", "content": ANALYSIS_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ]
        
        logger.ai(f"Starting analysis (Input ~{len(content)} chars, Max Output {max_output} tokens)...")
        self._notify("Generando análisis...")
        
        try:
            # Run inference in thread pool
            loop = asyncio.get_event_loop()
            
            def generate_sync():
                return self._model.create_chat_completion(
                    messages=messages,
                    max_tokens=max_output, # Usamos el valor ajustado dinámicamente
                    temperature=self.config.temperature,
                    top_p=self.config.top_p,
                    top_k=self.config.top_k,
                    repeat_penalty=self.config.repeat_penalty,
                )
            
            response = await loop.run_in_executor(None, generate_sync)
            
            # Extract response
            output = response["choices"][0]["message"]["content"]
            tokens_used = response.get("usage", {}).get("total_tokens", 0)
            
            logger.success(f"Analysis complete ({tokens_used} tokens)")
            self._notify("Análisis completado")
            
            return AnalysisResult(
                success=True,
                summary=output,
                tokens_used=tokens_used,
            )
            
        except Exception as e:
            # Captura específica para errores de contexto
            error_msg = str(e)
            if "exceed context window" in error_msg:
                 logger.error("Context window exceeded.")
                 return AnalysisResult(
                    success=False,
                    error="El contenido es demasiado extenso incluso tras el recorte. Intenta con un texto más corto o aumenta n_ctx si el modelo lo soporta.",
                )

            logger.error(f"Analysis failed: {e}")
            return AnalysisResult(
                success=False,
                error=str(e),
            )
    
    async def generate_research_report(
        self,
        scraped_contents: List[str],
        topic: str = "Research"
    ) -> AnalysisResult:
        """
        Generate a comprehensive research report from multiple sources.
        
        Args:
            scraped_contents: List of scraped markdown contents
            topic: Research topic for context
        
        Returns:
            AnalysisResult with full report
        """
        if not scraped_contents:
            return AnalysisResult(
                success=False,
                error="No content provided for analysis"
            )
        
        # Combine contents with source markers
        combined = f"# Investigación: {topic}\n\n"
        for i, content in enumerate(scraped_contents, 1):
            # Limit each source to prevent context overflow
            truncated = content[:3000] if len(content) > 3000 else content
            combined += f"\n## Fuente {i}\n{truncated}\n"
        
        # Generate report instructions (Content is passed separately now)
        custom_prompt = f"""Eres un investigador profesional. Analiza las {len(scraped_contents)} fuentes proporcionadas sobre "{topic}" y genera un informe de investigación completo.

GENERA UN INFORME CON:
1. **Resumen Ejecutivo**: Síntesis de 2-3 párrafos de los hallazgos principales
2. **Puntos Clave**: Lista numerada de los 7-10 puntos más importantes
3. **Análisis Comparativo**: Si hay diferentes perspectivas, compáralas
4. **Conclusiones**: Síntesis final y observaciones
5. **Recomendaciones**: Acciones sugeridas basadas en la investigación

Usa formato Markdown. Sé objetivo y cita las fuentes cuando corresponda."""
        
        return await self.analyze_content(combined, custom_prompt)


# Factory function
def create_analyzer(
    n_threads: int = 4,
    n_ctx: int = 4096,
) -> AIAnalyzer:
    """
    Create a configured AIAnalyzer instance.
    
    Args:
        n_threads: Number of CPU threads
        n_ctx: Context window size
    
    Returns:
        Configured AIAnalyzer
    """
    config = AnalysisConfig(
        n_threads=n_threads,
        n_ctx=n_ctx,
    )
    return AIAnalyzer(config=config)