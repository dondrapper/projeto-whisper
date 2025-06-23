@echo off
echo.
echo ============================================
echo    CORREÇÃO EMERGENCIAL - VENV CORROMPIDO
echo ============================================
echo.

echo 🔍 Detectando o problema...
echo Seu ambiente virtual está corrompido!
echo Vamos criar um novo ambiente limpo.
echo.

REM Sair do ambiente virtual se estiver ativo
if defined VIRTUAL_ENV (
    echo 🚪 Saindo do ambiente virtual corrompido...
    deactivate 2>nul
)

REM Remover ambiente virtual corrompido
if exist "venv" (
    echo 🗑️  Removendo ambiente virtual corrompido...
    rmdir /s /q venv
    if errorlevel 1 (
        echo ❌ Erro ao remover venv. Tente remover manualmente a pasta 'venv'
        pause
        exit /b 1
    )
    echo ✅ Ambiente corrompido removido!
)

REM Verificar se Python funciona
echo.
echo 🐍 Verificando Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python não encontrado!
    echo.
    echo 💡 SOLUÇÕES:
    echo 1. Instale Python: https://python.org/downloads
    echo 2. Marque "Add Python to PATH" na instalação
    echo 3. Reinicie o terminal
    echo.
    pause
    exit /b 1
)

echo ✅ Python encontrado!
python --version

echo.
echo 📦 Criando novo ambiente virtual...
python -m venv venv
if errorlevel 1 (
    echo ❌ Erro ao criar ambiente virtual!
    echo Tente executar como administrador.
    pause
    exit /b 1
)

echo ✅ Novo ambiente virtual criado!

echo.
echo 🔄 Ativando novo ambiente...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ❌ Erro ao ativar ambiente!
    pause
    exit /b 1
)

echo ✅ Ambiente ativado!

echo.
echo 📚 Instalando pacotes essenciais...
echo.

echo [1/5] Atualizando pip...
python -m pip install --upgrade pip
if errorlevel 1 echo ⚠️  Aviso: pip não atualizado

echo.
echo [2/5] Instalando PyTorch...
pip install torch>=2.0.0 --index-url https://download.pytorch.org/whl/cpu
if errorlevel 1 (
    echo ❌ Erro ao instalar PyTorch!
    echo Tentando método alternativo...
    pip install torch
)

echo.
echo [3/5] Instalando Whisper...
pip install openai-whisper
if errorlevel 1 (
    echo ❌ Erro ao instalar Whisper!
    echo Tentando do GitHub...
    pip install git+https://github.com/openai/whisper.git
)

echo.
echo [4/5] Instalando Streamlit...
pip install streamlit>=1.28.0
if errorlevel 1 (
    echo ❌ Erro ao instalar Streamlit!
    pause
    exit /b 1
)

echo.
echo [5/5] Instalando extras...
pip install numpy pandas ffmpeg-python

echo.
echo 🧪 Testando instalação...
python -c "import streamlit; print('✅ Streamlit OK')"
if errorlevel 1 (
    echo ❌ Streamlit não funciona!
    goto :error
)

python -c "import whisper; print('✅ Whisper OK')"
if errorlevel 1 (
    echo ❌ Whisper não funciona!
    goto :error
)

python -c "import torch; print('✅ PyTorch OK')"
if errorlevel 1 (
    echo ❌ PyTorch não funciona!
    goto :error
)

echo.
echo 📝 Criando scripts de execução...

REM Script para ativar ambiente
echo @echo off > ativar.bat
echo echo 🎙️ Ativando ambiente Whisper... >> ativar.bat
echo call venv\Scripts\activate.bat >> ativar.bat
echo echo ✅ Ambiente ativado! >> ativar.bat
echo echo. >> ativar.bat
echo echo Para executar: >> ativar.bat
echo echo   streamlit run main_simple.py >> ativar.bat
echo echo. >> ativar.bat
echo cmd /k >> ativar.bat

REM Script para executar diretamente
echo @echo off > executar.bat
echo echo 🎙️ Iniciando Whisper Transcriber... >> executar.bat
echo call venv\Scripts\activate.bat >> executar.bat
echo streamlit run main_simple.py >> executar.bat
echo pause >> executar.bat

echo.
echo ============================================
echo           ✅ CORREÇÃO CONCLUÍDA!
echo ============================================
echo.
echo 🎉 Ambiente virtual corrigido com sucesso!
echo.
echo 🚀 Para usar agora:
echo.
echo   1. EXECUTAR DIRETAMENTE:
echo      executar.bat
echo.
echo   2. ATIVAR AMBIENTE:
echo      ativar.bat
echo.
echo   3. MANUAL:
echo      call venv\Scripts\activate.bat
echo      streamlit run main_simple.py
echo.
echo 🌐 Acesse: http://localhost:8501
echo.
echo ============================================

REM Perguntar se quer executar agora
echo.
set /p resposta="Executar agora? (S/n): "
if /i "%resposta%"=="n" goto :end
if /i "%resposta%"=="nao" goto :end

echo.
echo 🚀 Iniciando aplicação...
streamlit run main_simple.py
goto :end

:error
echo.
echo ❌ Houve problemas na instalação.
echo.
echo 🔧 Tente manualmente:
echo   1. ativar.bat
echo   2. pip install --upgrade pip
echo   3. pip install openai-whisper streamlit torch
echo   4. streamlit run main_simple.py
echo.

:end
pause