"""
Módulo para transcrição de áudio usando o modelo Whisper da OpenAI.
Versão melhorada com configurações avançadas e otimizações.
"""

import whisper
import torch
import streamlit as st
import os
import time
import numpy as np
from utils import format_time

# Verifica se CUDA está disponível para processamento em GPU
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# Lista de modelos disponíveis com informações detalhadas
MODELS = {
    "tiny": {
        "description": "Mais rápido, menos preciso",
        "memory": "1GB",
        "speed": "⚡⚡⚡⚡⚡",
        "accuracy": "⭐⭐",
        "languages": "🌍 Limitado"
    },
    "base": {
        "description": "Rápido, precisão razoável", 
        "memory": "1GB",
        "speed": "⚡⚡⚡⚡",
        "accuracy": "⭐⭐⭐",
        "languages": "🌍 Bom"
    },
    "small": {
        "description": "Bom equilíbrio velocidade/precisão",
        "memory": "2GB", 
        "speed": "⚡⚡⚡",
        "accuracy": "⭐⭐⭐⭐",
        "languages": "🌍 Muito Bom"
    },
    "medium": {
        "description": "Mais preciso, menos rápido",
        "memory": "5GB",
        "speed": "⚡⚡",
        "accuracy": "⭐⭐⭐⭐⭐",
        "languages": "🌍 Excelente"
    },
    "large-v2": {
        "description": "Máxima precisão, multilíngue",
        "memory": "10GB",
        "speed": "⚡",
        "accuracy": "⭐⭐⭐⭐⭐",
        "languages": "🌍 Perfeito"
    }
}

# Mapeia idiomas com códigos ISO
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
        "no_speech_threshold": 0.6
    },
    "balanced": {
        "beam_size": 3,
        "best_of": 3,
        "temperature": 0.0,
        "compression_ratio_threshold": 2.0,
        "logprob_threshold": -0.5,
        "no_speech_threshold": 0.5
    },
    "high_quality": {
        "beam_size": 5,
        "best_of": 5,
        "temperature": 0.0,
        "compression_ratio_threshold": 1.8,
        "logprob_threshold": -0.3,
        "no_speech_threshold": 0.4
    }
}

@st.cache_resource(show_spinner="🔄 Carregando modelo de transcrição...")
def load_whisper_model(model_size):
    """
    Carrega o modelo Whisper com o tamanho especificado.
    
    Args:
        model_size (str): Tamanho do modelo (tiny, base, small, medium, large-v2)
        
    Returns:
        modelo Whisper carregado
    """
    try:
        # Configurar device adequadamente
        if DEVICE == "cuda":
            torch.cuda.empty_cache()  # Limpar cache da GPU
        
        model = whisper.load_model(model_size, device=DEVICE)
        
        # Log de informações do modelo
        st.sidebar.success(f"✅ Modelo {model_size} carregado com sucesso!")
        
        return model
    except Exception as e:
        st.error(f"❌ Erro ao carregar modelo {model_size}: {str(e)}")
        # Fallback para modelo menor
        if model_size != "tiny":
            st.warning("🔄 Tentando carregar modelo 'tiny' como fallback...")
            return whisper.load_model("tiny", device=DEVICE)
        else:
            raise e

def transcribe_audio(audio_path, model, language="auto", task="transcribe", advanced_options=None):
    """
    Transcreve um arquivo de áudio usando o modelo Whisper.
    
    Args:
        audio_path (str): Caminho para o arquivo de áudio
        model: Modelo Whisper carregado
        language (str): Código do idioma ou "auto" para detecção
        task (str): "transcribe" ou "translate" (para traduzir para inglês)
        advanced_options (dict): Configurações avançadas
        
    Returns:
        dict: Resultado da transcrição com texto e metadados
    """
    start_time = time.time()
    
    # Configurações padrão
    if advanced_options is None:
        advanced_options = {}
    
    # Aplicar preset de qualidade
    quality_preset = advanced_options.get("quality_preset", "balanced")
    preset_config = QUALITY_PRESETS.get(quality_preset, QUALITY_PRESETS["balanced"])
    
    # Configuração de opções
    options = {
        "task": task,
        "fp16": DEVICE == "cuda",  # Usar fp16 apenas se tiver GPU
        "verbose": False,  # Reduzir saída desnecessária
        "word_timestamps": True,  # Habilitar timestamps de palavras
        **preset_config
    }
    
    # Aplicar configurações avançadas personalizadas
    if "temperature" in advanced_options:
        options["temperature"] = advanced_options["temperature"]
    if "beam_size" in advanced_options:
        options["beam_size"] = advanced_options["beam_size"]
    
    # Configurar idioma se especificado
    if language != "auto":
        options["language"] = language
    
    try:
        # Executar transcrição
        with torch.no_grad():  # Otimização de memória
            result = model.transcribe(audio_path, **options)
        
        # Calcular tempo de processamento
        processing_time = time.time() - start_time
        
        # Processar e enriquecer resultados
        result = enhance_transcription_result(result, processing_time, advanced_options)
        
        # Limpeza de memória
        if DEVICE == "cuda":
            torch.cuda.empty_cache()
        
        return result
        
    except Exception as e:
        # Limpeza em caso de erro
        if DEVICE == "cuda":
            torch.cuda.empty_cache()
        raise Exception(f"Erro durante a transcrição: {str(e)}")

def enhance_transcription_result(result, processing_time, advanced_options):
    """
    Enriquece o resultado da transcrição com metadados adicionais.
    
    Args:
        result (dict): Resultado bruto do Whisper
        processing_time (float): Tempo de processamento
        advanced_options (dict): Configurações utilizadas
        
    Returns:
        dict: Resultado enriquecido
    """
    # Adicionar metadados de processamento
    result["processing_time"] = processing_time
    result["processing_time_formatted"] = format_time(processing_time)
    result["advanced_options_used"] = advanced_options
    
    # Calcular estatísticas dos segmentos
    if "segments" in result:
        segments = result["segments"]
        
        # Calcular confiança média
        total_confidence = 0
        confidence_count = 0
        
        for segment in segments:
            if "words" in segment:
                for word in segment["words"]:
                    if "probability" in word:
                        total_confidence += word["probability"]
                        confidence_count += 1
        
        result["average_confidence"] = total_confidence / confidence_count if confidence_count > 0 else 0.5
        
        # Calcular duração total do áudio
        if segments:
            result["audio_duration"] = segments[-1].get("end", 0)
            result["audio_duration_formatted"] = format_time(result["audio_duration"])
        
        # Estatísticas de velocidade
        if result.get("audio_duration", 0) > 0:
            result["processing_speed_ratio"] = processing_time / result["audio_duration"]
            result["realtime_factor"] = result["audio_duration"] / processing_time
        
        # Filtrar segmentos por confiança se solicitado
        confidence_threshold = advanced_options.get("confidence_threshold", 0.0)
        if confidence_threshold > 0:
            result["segments"] = filter_segments_by_confidence(segments, confidence_threshold)
            result["filtered_segments_count"] = len(result["segments"])
    
    # Detectar características do áudio
    result["audio_characteristics"] = analyze_audio_characteristics(result)
    
    return result

def filter_segments_by_confidence(segments, threshold):
    """
    Filtra segmentos baseado no threshold de confiança.
    
    Args:
        segments (list): Lista de segmentos
        threshold (float): Threshold de confiança (0.0 a 1.0)
        
    Returns:
        list: Segmentos filtrados
    """
    filtered_segments = []
    
    for segment in segments:
        segment_confidence = 0.5  # Valor padrão
        
        if "words" in segment:
            word_confidences = [word.get("probability", 0.5) for word in segment["words"]]
            if word_confidences:
                segment_confidence = sum(word_confidences) / len(word_confidences)
        
        if segment_confidence >= threshold:
            segment["confidence"] = segment_confidence
            filtered_segments.append(segment)
    
    return filtered_segments

def analyze_audio_characteristics(result):
    """
    Analisa características do áudio baseado na transcrição.
    
    Args:
        result (dict): Resultado da transcrição
        
    Returns:
        dict: Características detectadas
    """
    characteristics = {
        "speech_rate": "normal",
        "has_silence": False,
        "language_confidence": "medium",
        "audio_quality": "good"
    }
    
    if "segments" in result and result["segments"]:
        segments = result["segments"]
        
        # Calcular taxa de fala (palavras por minuto)
        total_words = sum(len(segment.get("text", "").split()) for segment in segments)
        total_duration = result.get("audio_duration", 0)
        
        if total_duration > 0:
            words_per_minute = (total_words / total_duration) * 60
            
            if words_per_minute < 120:
                characteristics["speech_rate"] = "slow"
            elif words_per_minute > 180:
                characteristics["speech_rate"] = "fast"
            else:
                characteristics["speech_rate"] = "normal"
        
        # Detectar pausas longas (possíveis silêncios)
        for i in range(len(segments) - 1):
            gap = segments[i + 1]["start"] - segments[i]["end"]
            if gap > 3.0:  # Pausa maior que 3 segundos
                characteristics["has_silence"] = True
                break
        
        # Avaliar confiança da detecção de idioma
        avg_confidence = result.get("average_confidence", 0.5)
        if avg_confidence > 0.8:
            characteristics["language_confidence"] = "high"
        elif avg_confidence < 0.4:
            characteristics["language_confidence"] = "low"
        
        # Avaliar qualidade baseada na confiança e repetições
        if avg_confidence > 0.7:
            characteristics["audio_quality"] = "excellent"
        elif avg_confidence > 0.5:
            characteristics["audio_quality"] = "good"
        elif avg_confidence > 0.3:
            characteristics["audio_quality"] = "fair"
        else:
            characteristics["audio_quality"] = "poor"
    
    return characteristics

def get_model_recommendations(file_size_mb, device_type):
    """
    Recomenda o melhor modelo baseado no tamanho do arquivo e dispositivo.
    
    Args:
        file_size_mb (float): Tamanho do arquivo em MB
        device_type (str): Tipo de dispositivo ("cuda" ou "cpu")
        
    Returns:
        str: Modelo recomendado
    """
    if device_type == "cpu":
        if file_size_mb < 10:
            return "base"
        elif file_size_mb < 50:
            return "small"
        else:
            return "base"  # Para CPU, evitar modelos muito grandes
    else:  # GPU
        if file_size_mb < 5:
            return "small"
        elif file_size_mb < 25:
            return "medium"
        else:
            return "large-v2"

def optimize_for_device():
    """
    Otimiza configurações baseadas no dispositivo disponível.
    
    Returns:
        dict: Configurações otimizadas
    """
    config = {
        "device": DEVICE,
        "recommended_models": [],
        "max_file_size_mb": 100,
        "parallel_processing": False
    }
    
    if DEVICE == "cuda":
        # Configurações para GPU
        gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1024**3
        
        if gpu_memory >= 8:
            config["recommended_models"] = ["medium", "large-v2"]
            config["max_file_size_mb"] = 500
            config["parallel_processing"] = True
        elif gpu_memory >= 4:
            config["recommended_models"] = ["small", "medium"]
            config["max_file_size_mb"] = 250
        else:
            config["recommended_models"] = ["tiny", "base", "small"]
            config["max_file_size_mb"] = 100
    else:
        # Configurações para CPU
        config["recommended_models"] = ["tiny", "base"]
        config["max_file_size_mb"] = 50
    
    return config

# Inicializar configurações do dispositivo
DEVICE_CONFIG = optimize_for_device()