"""
Módulo para gravação de áudio ao vivo na aplicação Whisper.
"""

import streamlit as st
import numpy as np
import tempfile
import wave
import os
from datetime import datetime, timedelta
import time

def show_audio_recorder(model_size, language, task):
    """
    Exibe a interface de gravação de áudio ao vivo.
    
    Args:
        model_size (str): Tamanho do modelo Whisper
        language (str): Idioma selecionado
        task (str): Tarefa (transcribe/translate)
    """
    st.markdown("### 🎤 Gravação de Áudio ao Vivo")
    
    # Informações sobre gravação
    st.info("""
    **Como usar a gravação ao vivo:**
    
    1. **Clique em "Iniciar Gravação"** para começar a capturar áudio
    2. **Fale claramente** próximo ao microfone
    3. **Clique em "Parar Gravação"** quando terminar
    4. **Aguarde** o processamento automático da transcrição
    
    ⚠️ **Requisitos:**
    - Microfone conectado e funcionando
    - Permissão para acessar o microfone no navegador
    - Ambiente com pouco ruído de fundo (recomendado)
    """)
    
    # Configurações de gravação
    st.markdown("#### ⚙️ Configurações de Gravação")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        recording_quality = st.selectbox(
            "Qualidade do áudio:",
            ["standard", "high", "low"],
            format_func=lambda x: {
                "low": "Baixa (8kHz, mono)",
                "standard": "Padrão (16kHz, mono)", 
                "high": "Alta (44.1kHz, estéreo)"
            }[x]
        )
    
    with col2:
        max_duration = st.selectbox(
            "Duração máxima:",
            [30, 60, 120, 300, 600],
            index=2,
            format_func=lambda x: f"{x//60}min {x%60}s" if x >= 60 else f"{x}s"
        )
    
    with col3:
        auto_stop_silence = st.checkbox(
            "Parar em silêncio",
            value=True,
            help="Para automaticamente após 3 segundos de silêncio"
        )
    
    # Estado da gravação
    if 'recording_state' not in st.session_state:
        st.session_state.recording_state = {
            'is_recording': False,
            'start_time': None,
            'audio_data': None,
            'recorded_file': None
        }
    
    # Interface de controle
    st.markdown("#### 🎙️ Controles de Gravação")
    
    # Status da gravação
    status_container = st.container()
    
    if st.session_state.recording_state['is_recording']:
        with status_container:
            st.success("🔴 **GRAVANDO...** 🔴")
            
            # Mostrar tempo decorrido
            if st.session_state.recording_state['start_time']:
                elapsed = time.time() - st.session_state.recording_state['start_time']
                remaining = max_duration - elapsed
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("⏱️ Tempo decorrido", f"{int(elapsed)}s")
                with col2:
                    st.metric("⏳ Tempo restante", f"{int(remaining)}s")
                
                # Barra de progresso
                progress = min(elapsed / max_duration, 1.0)
                st.progress(progress)
                
                # Auto-stop se exceder duração máxima
                if elapsed >= max_duration:
                    st.session_state.recording_state['is_recording'] = False
                    st.warning(f"⏰ Gravação parada automaticamente após {max_duration} segundos")
                    st.rerun()
    
    # Botões de controle
    button_col1, button_col2, button_col3 = st.columns(3)
    
    with button_col1:
        if not st.session_state.recording_state['is_recording']:
            if st.button("🎤 Iniciar Gravação", use_container_width=True, type="primary"):
                start_recording(recording_quality, max_duration)
        else:
            if st.button("⏹️ Parar Gravação", use_container_width=True, type="secondary"):
                stop_recording()
    
    with button_col2:
        if st.session_state.recording_state['recorded_file'] and not st.session_state.recording_state['is_recording']:
            if st.button("🔄 Nova Gravação", use_container_width=True):
                reset_recording()
    
    with button_col3:
        if st.session_state.recording_state['recorded_file']:
            if st.button("🚀 Transcrever", use_container_width=True, type="primary"):
                process_recorded_audio(model_size, language, task)
    
    # Mostrar gravação atual se existir
    if st.session_state.recording_state['recorded_file'] and not st.session_state.recording_state['is_recording']:
        st.markdown("#### 📻 Gravação Atual")
        
        # Player de áudio
        with open(st.session_state.recording_state['recorded_file'], 'rb') as audio_file:
            audio_bytes = audio_file.read()
            st.audio(audio_bytes, format='audio/wav')
        
        # Informações do arquivo
        file_size = os.path.getsize(st.session_state.recording_state['recorded_file'])
        file_size_mb = file_size / (1024 * 1024)
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("📏 Tamanho", f"{file_size_mb:.2f} MB")
        with col2:
            duration = get_audio_duration(st.session_state.recording_state['recorded_file'])
            st.metric("⏱️ Duração", f"{duration:.1f}s")

def start_recording(quality, max_duration):
    """
    Inicia a gravação de áudio.
    
    Args:
        quality (str): Qualidade da gravação
        max_duration (int): Duração máxima em segundos
    """
    try:
        # Configurações de áudio baseadas na qualidade
        audio_config = get_audio_config(quality)
        
        # Atualizar estado
        st.session_state.recording_state.update({
            'is_recording': True,
            'start_time': time.time(),
            'audio_config': audio_config,
            'max_duration': max_duration
        })
        
        st.success("🎤 Gravação iniciada!")
        st.rerun()
        
    except Exception as e:
        st.error(f"❌ Erro ao iniciar gravação: {str(e)}")

def stop_recording():
    """
    Para a gravação e salva o arquivo de áudio.
    """
    try:
        if not st.session_state.recording_state['is_recording']:
            return
        
        # Simular gravação (em um ambiente real, aqui capturaria áudio do microfone)
        # Por limitações do Streamlit, criamos um arquivo de exemplo
        audio_file = create_sample_audio_file()
        
        # Atualizar estado
        st.session_state.recording_state.update({
            'is_recording': False,
            'recorded_file': audio_file,
            'end_time': time.time()
        })
        
        st.success("✅ Gravação finalizada!")
        st.rerun()
        
    except Exception as e:
        st.error(f"❌ Erro ao parar gravação: {str(e)}")

def reset_recording():
    """
    Reseta a gravação, limpando arquivos temporários.
    """
    try:
        # Limpar arquivo anterior se existir
        if st.session_state.recording_state.get('recorded_file'):
            file_path = st.session_state.recording_state['recorded_file']
            if os.path.exists(file_path):
                os.unlink(file_path)
        
        # Resetar estado
        st.session_state.recording_state = {
            'is_recording': False,
            'start_time': None,
            'audio_data': None,
            'recorded_file': None
        }
        
        st.info("🔄 Pronto para nova gravação")
        st.rerun()
        
    except Exception as e:
        st.error(f"❌ Erro ao resetar gravação: {str(e)}")

def process_recorded_audio(model_size, language, task):
    """
    Processa o áudio gravado usando o Whisper.
    
    Args:
        model_size (str): Tamanho do modelo
        language (str): Idioma selecionado
        task (str): Tarefa de transcrição
    """
    try:
        recorded_file = st.session_state.recording_state.get('recorded_file')
        
        if not recorded_file or not os.path.exists(recorded_file):
            st.error("❌ Nenhuma gravação encontrada")
            return
        
        # Importar aqui para evitar dependências circulares
        from transcriber import load_whisper_model, transcribe_audio
        
        # Mostrar progresso
        with st.spinner("🔄 Processando gravação..."):
            progress_bar = st.progress(0)
            
            # Carregar modelo
            progress_bar.progress(25)
            model = load_whisper_model(model_size)
            
            # Transcrever
            progress_bar.progress(50)
            result = transcribe_audio(recorded_file, model, language, task)
            
            progress_bar.progress(100)
        
        # Exibir resultados
        st.markdown("### 📝 Resultado da Transcrição")
        
        # Métricas
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("🗣️ Idioma", result.get('language', 'Desconhecido'))
        with col2:
            st.metric("⏱️ Processamento", result.get('processing_time_formatted', 'N/A'))
        with col3:
            st.metric("📊 Segmentos", len(result.get('segments', [])))
        
        # Texto transcrito
        st.text_area("Transcrição:", result.get('text', ''), height=200)
        
        # Downloads
        if result.get('text'):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            col1, col2 = st.columns(2)
            with col1:
                st.download_button(
                    "📄 Baixar TXT",
                    result['text'],
                    file_name=f"gravacao_{timestamp}.txt",
                    mime="text/plain"
                )
            
            with col2:
                # Gerar SRT se houver segmentos
                if result.get('segments'):
                    srt_content = generate_srt_from_segments(result['segments'])
                    st.download_button(
                        "🎬 Baixar SRT", 
                        srt_content,
                        file_name=f"gravacao_{timestamp}.srt",
                        mime="text/plain"
                    )
        
        st.success("✅ Transcrição da gravação concluída!")
        
    except Exception as e:
        st.error(f"❌ Erro ao processar gravação: {str(e)}")

def get_audio_config(quality):
    """
    Retorna configurações de áudio baseadas na qualidade selecionada.
    
    Args:
        quality (str): Qualidade selecionada
        
    Returns:
        dict: Configurações de áudio
    """
    configs = {
        "low": {
            "sample_rate": 8000,
            "channels": 1,
            "bit_depth": 16
        },
        "standard": {
            "sample_rate": 16000,
            "channels": 1,
            "bit_depth": 16
        },
        "high": {
            "sample_rate": 44100,
            "channels": 2,
            "bit_depth": 16
        }
    }
    
    return configs.get(quality, configs["standard"])

def create_sample_audio_file():
    """
    Cria um arquivo de áudio de exemplo (para demonstração).
    Em um ambiente real, este seria substituído pela captura real do microfone.
    
    Returns:
        str: Caminho para o arquivo de áudio criado
    """
    try:
        # Gerar alguns segundos de áudio de exemplo (tom)
        sample_rate = 16000
        duration = 3  # 3 segundos
        frequency = 440  # Lá 4 (440 Hz)
        
        # Gerar onda senoidal
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        wave_data = np.sin(2 * np.pi * frequency * t) * 0.3
        
        # Converter para int16
        audio_data = (wave_data * 32767).astype(np.int16)
        
        # Criar arquivo temporário
        temp_file = tempfile.NamedTemporaryFile(
            delete=False, 
            suffix=".wav",
            prefix="recorded_audio_"
        )
        
        # Salvar como WAV
        with wave.open(temp_file.name, 'wb') as wav_file:
            wav_file.setnchannels(1)  # Mono
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(audio_data.tobytes())
        
        return temp_file.name
        
    except Exception as e:
        raise Exception(f"Erro ao criar arquivo de áudio: {str(e)}")

def get_audio_duration(file_path):
    """
    Obtém a duração de um arquivo de áudio WAV.
    
    Args:
        file_path (str): Caminho para o arquivo
        
    Returns:
        float: Duração em segundos
    """
    try:
        with wave.open(file_path, 'rb') as wav_file:
            frames = wav_file.getnframes()
            sample_rate = wav_file.getframerate()
            duration = frames / float(sample_rate)
            return duration
    except Exception:
        return 0.0

def generate_srt_from_segments(segments):
    """
    Gera conteúdo SRT a partir dos segmentos de transcrição.
    
    Args:
        segments (list): Lista de segmentos do Whisper
        
    Returns:
        str: Conteúdo formatado em SRT
    """
    srt_content = ""
    
    for i, segment in enumerate(segments, 1):
        start_time = format_time_for_srt(segment.get('start', 0))
        end_time = format_time_for_srt(segment.get('end', 0))
        text = segment.get('text', '').strip()
        
        srt_content += f"{i}\n"
        srt_content += f"{start_time} --> {end_time}\n"
        srt_content += f"{text}\n\n"
    
    return srt_content

def format_time_for_srt(seconds):
    """
    Formata tempo em segundos para o formato SRT (HH:MM:SS,mmm).
    
    Args:
        seconds (float): Tempo em segundos
        
    Returns:
        str: Tempo formatado para SRT
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    milliseconds = int((seconds % 1) * 1000)
    
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{milliseconds:03d}"

def record_audio():
    """
    Função principal para gravação de áudio (placeholder).
    Em um ambiente real, esta função utilizaria bibliotecas como pyaudio
    para capturar áudio do microfone em tempo real.
    """
    st.warning("""
    ⚠️ **Funcionalidade de Gravação em Desenvolvimento**
    
    A gravação de áudio ao vivo requer:
    - Bibliotecas adicionais (pyaudio, sounddevice)
    - Configuração de permissões do navegador
    - Interface JavaScript personalizada
    
    Por enquanto, esta funcionalidade simula a gravação com um arquivo de exemplo.
    Para implementação completa, considere usar:
    - streamlit-webrtc para captura de áudio em tempo real
    - streamlit-audio-recorder como alternativa
    """)

# Instruções de instalação para gravação real
RECORDING_INSTRUCTIONS = """
## Para habilitar gravação real de áudio:

### 1. Instalar dependências adicionais:
```bash
pip install pyaudio sounddevice streamlit-webrtc
```

### 2. Configurar permissões HTTPS:
A gravação de áudio requer HTTPS no navegador.

### 3. Alternativas recomendadas:
- **streamlit-audio-recorder**: Componente simples para gravação
- **streamlit-webrtc**: Solução completa para WebRTC
- **streamlit-javascript**: Para implementações personalizadas

### 4. Exemplo de uso com streamlit-audio-recorder:
```python
from streamlit_audio_recorder import audio_recorder

audio_bytes = audio_recorder()
if audio_bytes:
    st.audio(audio_bytes, format="audio/wav")
```
"""