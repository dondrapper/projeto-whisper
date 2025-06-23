"""
Versão simplificada do Whisper Pro Transcriber.
Use esta versão se tiver problemas com a instalação completa.
"""

import streamlit as st
import os
import tempfile
import time
from datetime import datetime

# Configuração da página
st.set_page_config(
    page_title="Whisper Transcriber - Simples",
    page_icon="🎙️",
    layout="wide"
)

def check_dependencies():
    """Verifica se as dependências estão instaladas"""
    missing_deps = []
    
    try:
        import whisper
        whisper_ok = True
    except ImportError:
        whisper_ok = False
        missing_deps.append("openai-whisper")
    
    try:
        import torch
        torch_ok = True
    except ImportError:
        torch_ok = False
        missing_deps.append("torch")
    
    return whisper_ok and torch_ok, missing_deps

def format_time(seconds):
    """Formata tempo em HH:MM:SS"""
    if seconds < 0:
        return "00:00:00"
    
    hours, remainder = divmod(int(seconds), 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

def save_uploaded_file(uploaded_file):
    """Salva arquivo carregado temporariamente"""
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            return tmp_file.name
    except Exception as e:
        st.error(f"Erro ao salvar arquivo: {e}")
        return None

def transcribe_file(file_path, model_name="base", language="auto"):
    """Transcreve um arquivo de áudio"""
    try:
        import whisper
        
        # Carregar modelo
        with st.spinner(f"Carregando modelo {model_name}..."):
            model = whisper.load_model(model_name)
        
        # Transcrever
        with st.spinner("Transcrevendo áudio..."):
            start_time = time.time()
            
            options = {"language": language if language != "auto" else None}
            result = model.transcribe(file_path, **options)
            
            processing_time = time.time() - start_time
        
        # Adicionar metadados
        result["processing_time"] = processing_time
        result["processing_time_formatted"] = format_time(processing_time)
        
        return result
        
    except Exception as e:
        st.error(f"Erro na transcrição: {e}")
        return None

def generate_srt(segments):
    """Gera conteúdo SRT"""
    srt_content = ""
    for i, segment in enumerate(segments, 1):
        start = format_time_srt(segment["start"])
        end = format_time_srt(segment["end"])
        text = segment["text"].strip()
        
        srt_content += f"{i}\n{start} --> {end}\n{text}\n\n"
    
    return srt_content

def format_time_srt(seconds):
    """Formata tempo para SRT"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    milliseconds = int((seconds % 1) * 1000)
    
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{milliseconds:03d}"

def main():
    """Função principal da aplicação"""
    
    # Título
    st.title("🎙️ Whisper Transcriber - Versão Simples")
    st.markdown("Transcrição de áudio usando OpenAI Whisper (versão simplificada)")
    
    # Verificar dependências
    deps_ok, missing_deps = check_dependencies()
    
    if not deps_ok:
        st.error("❌ Dependências em falta!")
        st.markdown("**Para corrigir, execute:**")
        
        for dep in missing_deps:
            st.code(f"pip install {dep}")
        
        st.markdown("**Ou execute o corretor automático:**")
        st.code("python fix_installation.py")
        
        st.stop()
    
    # Interface principal
    st.success("✅ Todas as dependências instaladas!")
    
    # Configurações na sidebar
    st.sidebar.header("⚙️ Configurações")
    
    # Modelo
    model_options = {
        "tiny": "Tiny - Mais rápido, menos preciso",
        "base": "Base - Equilibrado (recomendado)",
        "small": "Small - Mais preciso",
        "medium": "Medium - Alta precisão", 
        "large": "Large - Máxima precisão"
    }
    
    selected_model = st.sidebar.selectbox(
        "Modelo Whisper:",
        list(model_options.keys()),
        index=1,  # base
        format_func=lambda x: model_options[x]
    )
    
    # Idioma
    language_options = {
        "auto": "🔍 Detecção automática",
        "pt": "🇧🇷 Português",
        "en": "🇺🇸 Inglês",
        "es": "🇪🇸 Espanhol",
        "fr": "🇫🇷 Francês",
        "de": "🇩🇪 Alemão",
        "it": "🇮🇹 Italiano",
        "ja": "🇯🇵 Japonês",
        "zh": "🇨🇳 Chinês"
    }
    
    selected_language = st.sidebar.selectbox(
        "Idioma:",
        list(language_options.keys()),
        format_func=lambda x: language_options[x]
    )
    
    # Upload de arquivo
    st.header("📁 Upload de Arquivo")
    
    uploaded_file = st.file_uploader(
        "Escolha um arquivo de áudio ou vídeo",
        type=["mp3", "wav", "m4a", "mp4", "mpeg", "mpga", "webm", "ogg", "flac"]
    )
    
    if uploaded_file is not None:
        # Mostrar informações do arquivo
        file_details = f"**Nome:** {uploaded_file.name}  \n**Tamanho:** {uploaded_file.size / 1024 / 1024:.1f} MB"
        st.markdown(file_details)
        
        # Player de áudio
        st.audio(uploaded_file)
        
        # Botão de transcrição
        if st.button("🚀 Transcrever Arquivo", type="primary"):
            # Salvar arquivo temporariamente
            temp_path = save_uploaded_file(uploaded_file)
            
            if temp_path:
                try:
                    # Transcrever
                    result = transcribe_file(temp_path, selected_model, selected_language)
                    
                    if result:
                        # Exibir resultados
                        st.success(f"✅ Transcrição concluída em {result['processing_time_formatted']}")
                        
                        # Métricas
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("🗣️ Idioma", result.get('language', 'Desconhecido').upper())
                        with col2:
                            st.metric("⏱️ Tempo", result['processing_time_formatted'])
                        with col3:
                            st.metric("📊 Segmentos", len(result.get('segments', [])))
                        
                        # Texto transcrito
                        st.subheader("📝 Transcrição")
                        st.text_area("Texto completo:", result["text"], height=250)
                        
                        # Downloads
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        filename_base = uploaded_file.name.split('.')[0]
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            # Download TXT
                            st.download_button(
                                "📄 Baixar TXT",
                                result["text"],
                                file_name=f"{filename_base}_{timestamp}.txt",
                                mime="text/plain"
                            )
                        
                        with col2:
                            # Download SRT
                            if result.get("segments"):
                                srt_content = generate_srt(result["segments"])
                                st.download_button(
                                    "🎬 Baixar SRT",
                                    srt_content,
                                    file_name=f"{filename_base}_{timestamp}.srt",
                                    mime="text/plain"
                                )
                        
                        # Segmentos detalhados (opcional)
                        if st.checkbox("📋 Mostrar segmentos detalhados"):
                            st.subheader("🕐 Segmentos com Timestamps")
                            
                            for i, segment in enumerate(result.get("segments", []), 1):
                                start_time = format_time(segment["start"])
                                end_time = format_time(segment["end"])
                                text = segment["text"].strip()
                                
                                st.markdown(f"**{i}.** `{start_time} - {end_time}` {text}")
                
                finally:
                    # Limpar arquivo temporário
                    try:
                        os.unlink(temp_path)
                    except:
                        pass
    
    else:
        # Instruções
        st.info("👆 Faça upload de um arquivo de áudio ou vídeo para começar")
        
        st.markdown("""
        ### 📋 Como usar:
        1. Selecione o modelo e idioma na barra lateral
        2. Faça upload do seu arquivo de áudio/vídeo
        3. Clique em "Transcrever Arquivo"
        4. Aguarde o processamento
        5. Baixe os resultados em TXT ou SRT
        
        ### 🎵 Formatos suportados:
        MP3, WAV, M4A, MP4, OGG, FLAC, WEBM e outros
        
        ### ⚡ Dicas:
        - **Modelo Base**: Melhor equilíbrio para a maioria dos casos
        - **Detecção Automática**: Deixe o Whisper detectar o idioma
        - **Arquivos Menores**: Processamento mais rápido
        """)
    
    # Rodapé
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center">
        <p><strong>🎙️ Whisper Transcriber Simples</strong> | 
        Powered by <a href="https://github.com/openai/whisper">OpenAI Whisper</a></p>
        <p><em>Processamento 100% local - seus arquivos não saem do computador</em></p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()