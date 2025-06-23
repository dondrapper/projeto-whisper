"""
Configurações centralizadas da aplicação Whisper Pro Transcriber.
"""

import os
from pathlib import Path
from typing import Dict, List, Any

# Diretório base do projeto
BASE_DIR = Path(__file__).parent

# Configurações de ambiente
ENV = os.getenv("ENVIRONMENT", "development")
DEBUG = os.getenv("DEBUG", "True").lower() == "true"

class AppConfig:
    """Configurações principais da aplicação"""
    
    # Informações da aplicação
    APP_NAME = "Whisper Pro Transcriber"
    APP_VERSION = "2.0.0"
    APP_DESCRIPTION = "Transcrição de áudio profissional com OpenAI Whisper"
    
    # Configurações de interface
    PAGE_TITLE = "🎙️ Whisper Pro Transcriber"
    PAGE_ICON = "🎙️"
    LAYOUT = "wide"
    SIDEBAR_STATE = "expanded"
    
    # Tema e estilo
    THEME = {
        "primaryColor": "#1f4037",
        "backgroundColor": "#ffffff", 
        "secondaryBackgroundColor": "#f0f2f6",
        "textColor": "#262730"
    }

class FileConfig:
    """Configurações de arquivos e uploads"""
    
    # Limites de arquivo
    MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", 500))
    MIN_FILE_SIZE_KB = 1
    MAX_BATCH_FILES = int(os.getenv("MAX_BATCH_FILES", 20))
    
    # Tipos de arquivo suportados
    SUPPORTED_AUDIO_EXTENSIONS = [
        ".mp3", ".wav", ".m4a", ".aac", ".ogg", 
        ".flac", ".webm", ".wma"
    ]
    
    SUPPORTED_VIDEO_EXTENSIONS = [
        ".mp4", ".avi", ".mov", ".mkv", ".webm",
        ".mpeg", ".mpg", ".wmv", ".flv"
    ]
    
    SUPPORTED_MIME_TYPES = {
        "audio/mpeg": [".mp3"],
        "audio/wav": [".wav"],
        "audio/x-wav": [".wav"],
        "audio/mp4": [".m4a"],
        "audio/x-m4a": [".m4a"],
        "audio/aac": [".aac"],
        "audio/ogg": [".ogg"],
        "audio/flac": [".flac"],
        "audio/webm": [".webm"],
        "video/mp4": [".mp4"],
        "video/mpeg": [".mpeg", ".mpg"],
        "video/quicktime": [".mov"],
        "video/webm": [".webm"],
        "video/x-msvideo": [".avi"]
    }
    
    # Diretórios
    TEMP_DIR = Path(os.getenv("TEMP_DIR", BASE_DIR / "temp"))
    UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", BASE_DIR / "uploads"))
    OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", BASE_DIR / "outputs"))
    
    # Criação automática de diretórios
    @classmethod
    def ensure_directories(cls):
        """Cria diretórios necessários se não existirem"""
        for directory in [cls.TEMP_DIR, cls.UPLOAD_DIR, cls.OUTPUT_DIR]:
            directory.mkdir(parents=True, exist_ok=True)

class WhisperConfig:
    """Configurações específicas do Whisper"""
    
    # Modelos disponíveis
    MODELS = {
        "tiny": {
            "description": "Mais rápido, menos preciso",
            "memory": "1GB",
            "speed": "⚡⚡⚡⚡⚡",
            "accuracy": "⭐⭐",
            "languages": "🌍 Limitado",
            "parameters": "39M"
        },
        "base": {
            "description": "Rápido, precisão razoável", 
            "memory": "1GB",
            "speed": "⚡⚡⚡⚡",
            "accuracy": "⭐⭐⭐",
            "languages": "🌍 Bom",
            "parameters": "74M"
        },
        "small": {
            "description": "Bom equilíbrio velocidade/precisão",
            "memory": "2GB", 
            "speed": "⚡⚡⚡",
            "accuracy": "⭐⭐⭐⭐",
            "languages": "🌍 Muito Bom",
            "parameters": "244M"
        },
        "medium": {
            "description": "Mais preciso, menos rápido",
            "memory": "5GB",
            "speed": "⚡⚡",
            "accuracy": "⭐⭐⭐⭐⭐",
            "languages": "🌍 Excelente",
            "parameters": "769M"
        },
        "large-v2": {
            "description": "Máxima precisão, multilíngue",
            "memory": "10GB",
            "speed": "⚡",
            "accuracy": "⭐⭐⭐⭐⭐",
            "languages": "🌍 Perfeito",
            "parameters": "1550M"
        }
    }
    
    # Idiomas suportados
    LANGUAGES = {
        "auto": "🔍 Detecção automática",
        "pt": "🇧🇷 Português", 
        "en": "🇺🇸 Inglês",
        "es": "🇪🇸 Espanhol",
        "fr": "🇫🇷 Francês",
        "de": "🇩🇪 Alemão",
        "it": "🇮🇹 Italiano",
        "ja": "🇯🇵 Japonês",
        "zh": "🇨🇳 Chinês",
        "ru": "🇷🇺 Russo",
        "ko": "🇰🇷 Coreano",
        "ar": "🇸🇦 Árabe",
        "hi": "🇮🇳 Hindi",
        "nl": "🇳🇱 Holandês",
        "pl": "🇵🇱 Polonês",
        "sv": "🇸🇪 Sueco",
        "no": "🇳🇴 Norueguês",
        "da": "🇩🇰 Dinamarquês",
        "fi": "🇫🇮 Finlandês",
        "tr": "🇹🇷 Turco",
        "uk": "🇺🇦 Ucraniano",
        "cs": "🇨🇿 Tcheco",
        "hu": "🇭🇺 Húngaro",
        "th": "🇹🇭 Tailandês",
        "vi": "🇻🇳 Vietnamita",
        "he": "🇮🇱 Hebraico"
    }
    
    # Presets de qualidade
    QUALITY_PRESETS = {
        "fast": {
            "beam_size": 1,
            "best_of": 1,
            "temperature": 0.0,
            "compression_ratio_threshold": 2.4,
            "logprob_threshold": -1.0,
            "no_speech_threshold": 0.6,
            "description": "Processamento mais rápido"
        },
        "balanced": {
            "beam_size": 3,
            "best_of": 3,
            "temperature": 0.0,
            "compression_ratio_threshold": 2.0,
            "logprob_threshold": -0.5,
            "no_speech_threshold": 0.5,
            "description": "Equilibrio entre velocidade e qualidade"
        },
        "high_quality": {
            "beam_size": 5,
            "best_of": 5,
            "temperature": 0.0,
            "compression_ratio_threshold": 1.8,
            "logprob_threshold": -0.3,
            "no_speech_threshold": 0.4,
            "description": "Máxima qualidade, mais lento"
        }
    }
    
    # Configurações padrão
    DEFAULT_MODEL = "base"
    DEFAULT_LANGUAGE = "auto"
    DEFAULT_TASK = "transcribe"
    DEFAULT_QUALITY_PRESET = "balanced"

class RecordingConfig:
    """Configurações de gravação de áudio"""
    
    # Qualidades de gravação
    AUDIO_QUALITIES = {
        "low": {
            "sample_rate": 8000,
            "channels": 1,
            "bit_depth": 16,
            "description": "Baixa qualidade (8kHz, mono)"
        },
        "standard": {
            "sample_rate": 16000,
            "channels": 1,
            "bit_depth": 16,
            "description": "Qualidade padrão (16kHz, mono)"
        },
        "high": {
            "sample_rate": 44100,
            "channels": 2,
            "bit_depth": 16,
            "description": "Alta qualidade (44.1kHz, estéreo)"
        }
    }
    
    # Configurações padrão
    DEFAULT_QUALITY = "standard"
    MAX_DURATION_SECONDS = 600  # 10 minutos
    AUTO_STOP_SILENCE_SECONDS = 3
    
    # Formatos de saída
    OUTPUT_FORMAT = "wav"
    CHUNK_SIZE = 1024

class PerformanceConfig:
    """Configurações de performance"""
    
    # Cache
    ENABLE_MODEL_CACHE = True
    CACHE_TTL_SECONDS = 3600  # 1 hora
    MAX_CACHE_SIZE_MB = 1000
    
    # Processamento
    MAX_CONCURRENT_JOBS = int(os.getenv("MAX_CONCURRENT_JOBS", 2))
    PROCESSING_TIMEOUT_SECONDS = 3600  # 1 hora
    
    # Limpeza automática
    AUTO_CLEANUP_TEMP_FILES = True
    TEMP_FILE_MAX_AGE_HOURS = 24
    
    # Estimativas de performance por hardware
    PERFORMANCE_ESTIMATES = {
        "cpu_basic": {
            "multiplier": 8.0,
            "max_file_size_mb": 50,
            "recommended_models": ["tiny", "base"]
        },
        "cpu_powerful": {
            "multiplier": 4.0,
            "max_file_size_mb": 200,
            "recommended_models": ["base", "small"]
        },
        "gpu_4gb": {
            "multiplier": 1.0,
            "max_file_size_mb": 500,
            "recommended_models": ["small", "medium"]
        },
        "gpu_8gb_plus": {
            "multiplier": 0.5,
            "max_file_size_mb": 2000,
            "recommended_models": ["medium", "large-v2"]
        }
    }

class DatabaseConfig:
    """Configurações de banco de dados (futuro)"""
    
    # SQLite para histórico local
    SQLITE_PATH = BASE_DIR / "data" / "transcriptions.db"
    
    # Redis para cache (opcional)
    REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
    REDIS_DB = int(os.getenv("REDIS_DB", 0))
    REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")

class SecurityConfig:
    """Configurações de segurança"""
    
    # Validação de arquivos
    SCAN_UPLOADED_FILES = True
    MAX_FILENAME_LENGTH = 255
    FORBIDDEN_EXTENSIONS = [
        ".exe", ".bat", ".sh", ".scr", ".com", ".pif",
        ".vbs", ".js", ".jar", ".app", ".deb", ".rpm"
    ]
    
    # Rate limiting (futuro)
    RATE_LIMIT_REQUESTS_PER_MINUTE = 60
    RATE_LIMIT_UPLOADS_PER_HOUR = 100
    
    # Logs de segurança
    LOG_SECURITY_EVENTS = True

class LoggingConfig:
    """Configurações de logging"""
    
    # Níveis de log
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    # Arquivos de log
    LOG_DIR = BASE_DIR / "logs"
    APP_LOG_FILE = LOG_DIR / "app.log"
    ERROR_LOG_FILE = LOG_DIR / "error.log"
    SECURITY_LOG_FILE = LOG_DIR / "security.log"
    
    # Rotação de logs
    MAX_LOG_SIZE_MB = 10
    MAX_LOG_FILES = 5
    
    # Formato
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# Configuração principal que exporta todas as outras
class Config:
    """Classe principal de configuração que agrega todas as configurações"""
    
    App = AppConfig
    File = FileConfig
    Whisper = WhisperConfig
    Recording = RecordingConfig
    Performance = PerformanceConfig
    Database = DatabaseConfig
    Security = SecurityConfig
    Logging = LoggingConfig
    
    @classmethod
    def initialize(cls):
        """Inicializa configurações necessárias"""
        # Criar diretórios
        cls.File.ensure_directories()
        
        # Criar diretório de logs
        cls.Logging.LOG_DIR.mkdir(parents=True, exist_ok=True)
        
        # Criar diretório de dados
        cls.Database.SQLITE_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def get_device_config(cls, device_type: str, memory_gb: float = None) -> Dict[str, Any]:
        """
        Retorna configuração otimizada baseada no dispositivo.
        
        Args:
            device_type: "cpu" ou "cuda"
            memory_gb: Memória disponível em GB
            
        Returns:
            Configuração otimizada
        """
        if device_type == "cpu":
            if memory_gb and memory_gb > 8:
                return cls.Performance.PERFORMANCE_ESTIMATES["cpu_powerful"]
            else:
                return cls.Performance.PERFORMANCE_ESTIMATES["cpu_basic"]
        else:  # CUDA
            if memory_gb and memory_gb >= 8:
                return cls.Performance.PERFORMANCE_ESTIMATES["gpu_8gb_plus"]
            else:
                return cls.Performance.PERFORMANCE_ESTIMATES["gpu_4gb"]

# Inicializar configurações ao importar
Config.initialize()

# Funções utilitárias para configuração
def get_config() -> Config:
    """Retorna a instância de configuração principal"""
    return Config

def load_user_config(config_file: str = "config.local.py"):
    """
    Carrega configurações personalizadas do usuário.
    
    Args:
        config_file: Caminho para arquivo de configuração local
    """
    config_path = BASE_DIR / config_file
    if config_path.exists():
        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location("user_config", config_path)
            user_config = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(user_config)
            
            # Aplicar configurações do usuário
            for attr_name in dir(user_config):
                if not attr_name.startswith("_"):
                    attr_value = getattr(user_config, attr_name)
                    if hasattr(Config, attr_name):
                        setattr(Config, attr_name, attr_value)
                        
        except Exception as e:
            print(f"Erro ao carregar configuração do usuário: {e}")

# Carregar configurações do usuário se existirem
load_user_config()