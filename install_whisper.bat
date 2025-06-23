@echo off
echo.
echo ========================================
echo   INSTALADOR WHISPER PRO TRANSCRIBER
echo ========================================
echo.

REM Verificar se Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo ERRO: Python nao encontrado!
    echo Por favor, instale Python 3.8+ primeiro.
    echo Download: https://python.org/downloads
    pause
    exit /b 1
)

echo Python encontrado! Continuando...
echo.

REM Criar ambiente virtual se não existir
if not exist "venv" (
    echo Criando ambiente virtual...
    python -m venv venv
    if errorlevel 1 (
        echo ERRO: Falha ao criar ambiente virtual!
        pause
        exit /b 1
    )
    echo Ambiente virtual criado!
) else (
    echo Ambiente virtual ja existe.
)

echo.
echo Ativando ambiente virtual...
call venv\Scripts\activate.bat

REM Atualizar pip
echo.
echo Atualizando pip...
python -m pip install --upgrade pip

REM Instalar dependências uma por uma
echo.
echo ==========================================
echo Instalando dependencias (pode demorar)...
echo ==========================================

echo.
echo [1/6] Instalando wheel...
pip install wheel
if errorlevel 1 echo AVISO: Falha ao instalar wheel

echo.
echo [2/6] Instalando NumPy...
pip install "numpy>=1.24.0"
if errorlevel 1 (
    echo ERRO: Falha ao instalar NumPy!
    pause
    exit /b 1
)

echo.
echo [3/6] Instalando PyTorch (CPU)...
pip install torch>=2.0.0 --index-url https://download.pytorch.org/whl/cpu
if errorlevel 1 (
    echo ERRO: Falha ao instalar PyTorch!
    pause
    exit /b 1
)

echo.
echo [4/6] Instalando OpenAI Whisper...
pip install openai-whisper
if errorlevel 1 (
    echo Tentando instalacao alternativa...
    pip install git+https://github.com/openai/whisper.git
    if errorlevel 1 (
        echo ERRO: Falha ao instalar Whisper!
        pause
        exit /b 1
    )
)

echo.
echo [5/6] Instalando Streamlit...
pip install "streamlit>=1.28.0"
if errorlevel 1 (
    echo ERRO: Falha ao instalar Streamlit!
    pause
    exit /b 1
)

echo.
echo [6/6] Instalando dependencias extras...
pip install "pandas>=1.5.0" "ffmpeg-python>=0.2.0" "scipy>=1.10.0"
if errorlevel 1 echo AVISO: Algumas dependencias extras falharam

REM Testar instalação
echo.
echo ==========================================
echo Testando instalacao...
echo ==========================================

echo.
echo Testando importacoes...
python -c "import streamlit; print('✓ Streamlit OK')"
if errorlevel 1 (
    echo ERRO: Streamlit nao funciona!
    pause
    exit /b 1
)

python -c "import whisper; print('✓ Whisper OK')"
if errorlevel 1 (
    echo ERRO: Whisper nao funciona!
    pause
    exit /b 1
)

python -c "import torch; print('✓ PyTorch OK')"
if errorlevel 1 (
    echo ERRO: PyTorch nao funciona!
    pause
    exit /b 1
)

echo.
echo Testando modelo Whisper...
python -c "import whisper; whisper.load_model('tiny'); print('✓ Modelo carregado!')"
if errorlevel 1 (
    echo AVISO: Problema ao carregar modelo, mas pode funcionar.
)

REM Criar script de execução
echo.
echo Criando script de execucao...
echo @echo off > start_transcriber.bat
echo echo Iniciando Whisper Pro Transcriber... >> start_transcriber.bat
echo call venv\Scripts\activate.bat >> start_transcriber.bat
echo streamlit run main.py >> start_transcriber.bat
echo pause >> start_transcriber.bat

REM Criar versão simples também
echo @echo off > start_simple.bat
echo echo Iniciando versao simples... >> start_simple.bat
echo call venv\Scripts\activate.bat >> start_simple.bat
echo streamlit run main_simple.py >> start_simple.bat
echo pause >> start_simple.bat

echo.
echo ==========================================
echo        INSTALACAO CONCLUIDA!
echo ==========================================
echo.
echo Para executar a aplicacao:
echo.
echo   1. VERSAO COMPLETA:
echo      start_transcriber.bat
echo.
echo   2. VERSAO SIMPLES:
echo      start_simple.bat
echo.
echo   3. MANUAL:
echo      call venv\Scripts\activate.bat
echo      streamlit run main.py
echo.
echo Acesse: http://localhost:8501
echo.
echo ==========================================

pause