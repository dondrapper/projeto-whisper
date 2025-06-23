"""
Utilitários para a aplicação de transcrição de áudio com Whisper.
Versão melhorada com validações e otimizações.
"""

import os
import tempfile
import mimetypes
from datetime import datetime
from pathlib import Path
import streamlit as st

# Tipos de arquivo suportados
SUPPORTED_AUDIO_TYPES = {
    'audio/mpeg': ['.mp3'],
    'audio/wav': ['.wav'],
    'audio/x-wav': ['.wav'],
    'audio/mp4': ['.m4a'],
    'audio/x-m4a': ['.m4a'],
    'audio/aac': ['.aac'],
    'audio/ogg': ['.ogg'],
    'audio/flac': ['.flac'],
    'audio/webm': ['.webm'],
    'video/mp4': ['.mp4'],
    'video/mpeg': ['.mpeg', '.mpg'],
    'video/quicktime': ['.mov'],
    'video/webm': ['.webm'],
    'video/x-msvideo': ['.avi']
}

# Limites de arquivo
MAX_FILE_SIZE_MB = 500  # 500MB
MIN_FILE_SIZE_KB = 1    # 1KB

def save_uploaded_file(uploaded_file):
    """
    Salva um arquivo carregado em um local temporário e retorna o caminho.
    
    Args:
        uploaded_file: Arquivo carregado pelo Streamlit
        
    Returns:
        str: Caminho para o arquivo temporário
        
    Raises:
        Exception: Se houver erro ao salvar o arquivo
    """
    try:
        # Validar arquivo antes de salvar
        validation_result = validate_audio_file(uploaded_file)
        if not validation_result["valid"]:
            raise Exception(validation_result["error"])
        
        # Obter extensão do arquivo
        file_extension = Path(uploaded_file.name).suffix.lower()
        if not file_extension:
            file_extension = guess_extension_from_mime(uploaded_file.type)
        
        # Criar arquivo temporário
        with tempfile.NamedTemporaryFile(
            delete=False, 
            suffix=file_extension,
            prefix=f"whisper_audio_{get_timestamp()}_"
        ) as tmp_file:
            # Escrever dados em chunks para arquivos grandes
            chunk_size = 8192
            bytes_data = uploaded_file.getvalue()
            
            for i in range(0, len(bytes_data), chunk_size):
                chunk = bytes_data[i:i + chunk_size]
                tmp_file.write(chunk)
            
            temp_path = tmp_file.name
        
        # Verificar se o arquivo foi salvo corretamente
        if not os.path.exists(temp_path) or os.path.getsize(temp_path) == 0:
            raise Exception("Arquivo temporário não foi criado corretamente")
        
        return temp_path
        
    except Exception as e:
        raise Exception(f"Erro ao salvar arquivo: {str(e)}")

def validate_audio_file(uploaded_file):
    """
    Valida se o arquivo carregado é um arquivo de áudio/vídeo válido.
    
    Args:
        uploaded_file: Arquivo carregado pelo Streamlit
        
    Returns:
        dict: Resultado da validação com 'valid' e 'error' se aplicável
    """
    try:
        # Verificar se o arquivo existe
        if uploaded_file is None:
            return {"valid": False, "error": "Nenhum arquivo foi carregado"}
        
        # Verificar nome do arquivo
        if not uploaded_file.name:
            return {"valid": False, "error": "Nome do arquivo está vazio"}
        
        # Verificar tamanho do arquivo
        file_size_mb = uploaded_file.size / (1024 * 1024)
        file_size_kb = uploaded_file.size / 1024
        
        if file_size_kb < MIN_FILE_SIZE_KB:
            return {"valid": False, "error": f"Arquivo muito pequeno (mínimo: {MIN_FILE_SIZE_KB}KB)"}
        
        if file_size_mb > MAX_FILE_SIZE_MB:
            return {"valid": False, "error": f"Arquivo muito grande (máximo: {MAX_FILE_SIZE_MB}MB)"}
        
        # Verificar tipo MIME
        mime_type = uploaded_file.type
        if mime_type and mime_type not in SUPPORTED_AUDIO_TYPES:
            return {"valid": False, "error": f"Tipo de arquivo não suportado: {mime_type}"}
        
        # Verificar extensão do arquivo
        file_extension = Path(uploaded_file.name).suffix.lower()
        supported_extensions = []
        for extensions in SUPPORTED_AUDIO_TYPES.values():
            supported_extensions.extend(extensions)
        
        if file_extension and file_extension not in supported_extensions:
            return {"valid": False, "error": f"Extensão não suportada: {file_extension}"}
        
        # Validação adicional para arquivos suspeitos
        if file_extension in ['.exe', '.bat', '.sh', '.scr', '.com', '.pif']:
            return {"valid": False, "error": "Tipo de arquivo não permitido por segurança"}
        
        return {"valid": True}
        
    except Exception as e:
        return {"valid": False, "error": f"Erro na validação: {str(e)}"}

def estimate_processing_time(file_size_mb, model_size, device_type):
    """
    Estima o tempo de processamento baseado no tamanho do arquivo, modelo e dispositivo.
    
    Args:
        file_size_mb (float): Tamanho do arquivo em MB
        model_size (str): Tamanho do modelo Whisper
        device_type (str): Tipo de dispositivo ("cuda" ou "cpu")
        
    Returns:
        str: Tempo estimado formatado
    """
    try:
        # Fatores base por modelo (minutos de processamento por MB)
        model_factors = {
            "tiny": 0.1,
            "base": 0.15,
            "small": 0.25,
            "medium": 0.4,
            "large-v2": 0.6
        }
        
        # Multiplicadores por dispositivo
        device_multipliers = {
            "cuda": 1.0,      # GPU baseline
            "cpu": 4.0        # CPU é ~4x mais lento
        }
        
        base_factor = model_factors.get(model_size, 0.25)
        device_mult = device_multipliers.get(device_type, 4.0)
        
        # Calcular tempo estimado em minutos
        estimated_minutes = file_size_mb * base_factor * device_mult
        
        # Adicionar overhead fixo
        estimated_minutes += 0.5  # 30 segundos de overhead
        
        # Formatação do tempo
        if estimated_minutes < 1:
            return f"~{int(estimated_minutes * 60)}s"
        elif estimated_minutes < 60:
            return f"~{estimated_minutes:.1f}min"
        else:
            hours = int(estimated_minutes // 60)
            minutes = int(estimated_minutes % 60)
            return f"~{hours}h{minutes:02d}min"
            
    except Exception:
        return "~Calculando..."

def get_timestamp():
    """
    Retorna um timestamp formatado para uso em nomes de arquivos.
    
    Returns:
        str: Timestamp atual formatado
    """
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def format_time(seconds):
    """
    Formata segundos em formato de tempo legível (HH:MM:SS).
    
    Args:
        seconds (float): Tempo em segundos
        
    Returns:
        str: Tempo formatado
    """
    if seconds < 0:
        return "00:00:00"
    
    hours, remainder = divmod(int(seconds), 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

def guess_extension_from_mime(mime_type):
    """
    Tenta adivinhar a extensão do arquivo baseado no tipo MIME.
    
    Args:
        mime_type (str): Tipo MIME do arquivo
        
    Returns:
        str: Extensão do arquivo com ponto
    """
    if mime_type in SUPPORTED_AUDIO_TYPES:
        return SUPPORTED_AUDIO_TYPES[mime_type][0]
    
    # Fallback usando mimetypes do Python
    extension = mimetypes.guess_extension(mime_type)
    return extension if extension else ".unknown"

def clean_filename(filename):
    """
    Limpa o nome do arquivo removendo caracteres problemáticos.
    
    Args:
        filename (str): Nome original do arquivo
        
    Returns:
        str: Nome do arquivo limpo
    """
    import re
    
    # Remover extensão temporariamente
    name_part = Path(filename).stem
    extension = Path(filename).suffix
    
    # Remover caracteres não alphanúmericos (exceto - e _)
    clean_name = re.sub(r'[^\w\-_\.]', '_', name_part)
    
    # Remover underscores múltiplos
    clean_name = re.sub(r'_+', '_', clean_name)
    
    # Remover underscores do início e fim
    clean_name = clean_name.strip('_')
    
    # Garantir que não seja vazio
    if not clean_name:
        clean_name = "audio_file"
    
    return clean_name + extension

def format_file_size(size_bytes):
    """
    Formata o tamanho do arquivo em uma string legível.
    
    Args:
        size_bytes (int): Tamanho em bytes
        
    Returns:
        str: Tamanho formatado
    """
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    size = float(size_bytes)
    
    while size >= 1024.0 and i < len(size_names) - 1:
        size /= 1024.0
        i += 1
    
    return f"{size:.1f} {size_names[i]}"

def get_audio_duration_estimate(file_size_mb, bitrate_kbps=128):
    """
    Estima a duração do áudio baseada no tamanho do arquivo.
    
    Args:
        file_size_mb (float): Tamanho do arquivo em MB
        bitrate_kbps (int): Bitrate estimado em kbps
        
    Returns:
        str: Duração estimada formatada
    """
    try:
        # Conversões
        file_size_bits = file_size_mb * 1024 * 1024 * 8
        bitrate_bps = bitrate_kbps * 1000
        
        # Calcular duração em segundos
        duration_seconds = file_size_bits / bitrate_bps
        
        return format_time(duration_seconds)
        
    except Exception:
        return "Desconhecido"

def create_safe_directory(base_path, dir_name):
    """
    Cria um diretório de forma segura.
    
    Args:
        base_path (str): Caminho base
        dir_name (str): Nome do diretório
        
    Returns:
        str: Caminho completo do diretório criado
    """
    try:
        full_path = os.path.join(base_path, dir_name)
        os.makedirs(full_path, exist_ok=True)
        return full_path
    except Exception as e:
        raise Exception(f"Erro ao criar diretório: {str(e)}")

def cleanup_temp_files(temp_dir=None, max_age_hours=24):
    """
    Remove arquivos temporários antigos.
    
    Args:
        temp_dir (str): Diretório temporário (None para usar o padrão)
        max_age_hours (int): Idade máxima dos arquivos em horas
    """
    try:
        if temp_dir is None:
            temp_dir = tempfile.gettempdir()
        
        current_time = datetime.now()
        max_age_seconds = max_age_hours * 3600
        
        for filename in os.listdir(temp_dir):
            if filename.startswith("whisper_audio_"):
                file_path = os.path.join(temp_dir, filename)
                if os.path.isfile(file_path):
                    file_age = current_time - datetime.fromtimestamp(os.path.getmtime(file_path))
                    if file_age.total_seconds() > max_age_seconds:
                        try:
                            os.unlink(file_path)
                        except Exception:
                            pass  # Ignorar erros de limpeza
                            
    except Exception:
        pass  # Ignorar erros de limpeza

def validate_advanced_options(options):
    """
    Valida opções avançadas fornecidas pelo usuário.
    
    Args:
        options (dict): Opções avançadas
        
    Returns:
        dict: Opções validadas e corrigidas
    """
    validated = {}
    
    # Temperatura
    temperature = options.get("temperature", 0.0)
    validated["temperature"] = max(0.0, min(1.0, float(temperature)))
    
    # Beam size
    beam_size = options.get("beam_size", 3)
    validated["beam_size"] = max(1, min(10, int(beam_size)))
    
    # Confidence threshold
    confidence_threshold = options.get("confidence_threshold", 0.5)
    validated["confidence_threshold"] = max(0.0, min(1.0, float(confidence_threshold)))
    
    # Quality preset
    quality_preset = options.get("quality_preset", "balanced")
    if quality_preset not in ["fast", "balanced", "high_quality"]:
        validated["quality_preset"] = "balanced"
    else:
        validated["quality_preset"] = quality_preset
    
    return validated

# Executar limpeza de arquivos temporários na inicialização
cleanup_temp_files()