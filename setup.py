#!/usr/bin/env python3
"""
Script de setup e instalação do Whisper Pro Transcriber.
Automatiza a configuração inicial do projeto.
"""

import os
import sys
import subprocess
import platform
from pathlib import Path
import shutil
import urllib.request

def print_banner():
    """Exibe banner de boas-vindas"""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║               🎙️  WHISPER PRO TRANSCRIBER  🎙️                ║
    ║                                                              ║
    ║                    Setup & Installation                      ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def check_python_version():
    """Verifica se a versão do Python é compatível"""
    print("🐍 Verificando versão do Python...")
    
    min_version = (3, 8)
    current_version = sys.version_info[:2]
    
    if current_version < min_version:
        print(f"❌ Python {min_version[0]}.{min_version[1]}+ é necessário.")
        print(f"   Versão atual: {current_version[0]}.{current_version[1]}")
        print("   Por favor, atualize o Python e tente novamente.")
        return False
    
    print(f"✅ Python {current_version[0]}.{current_version[1]} detectado - OK!")
    return True

def check_ffmpeg():
    """Verifica se FFmpeg está instalado"""
    print("\n🎬 Verificando FFmpeg...")
    
    try:
        result = subprocess.run(['ffmpeg', '-version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            version = result.stdout.split('\n')[0]
            print(f"✅ FFmpeg encontrado: {version}")
            return True
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    
    print("❌ FFmpeg não encontrado!")
    print_ffmpeg_installation_guide()
    return False

def print_ffmpeg_installation_guide():
    """Exibe guia de instalação do FFmpeg"""
    system = platform.system().lower()
    
    print("\n📋 Como instalar FFmpeg:")
    
    if system == "windows":
        print("""
        Windows:
        1. Acesse: https://ffmpeg.org/download.html#build-windows
        2. Baixe a versão 'release builds'
        3. Extraia o arquivo ZIP
        4. Adicione a pasta 'bin' ao PATH do sistema
        5. Reinicie o terminal
        
        Ou use o Chocolatey:
        choco install ffmpeg
        """)
    
    elif system == "darwin":  # macOS
        print("""
        macOS:
        brew install ffmpeg
        """)
    
    else:  # Linux
        print("""
        Ubuntu/Debian:
        sudo apt update
        sudo apt install ffmpeg
        
        CentOS/RHEL:
        sudo yum install epel-release
        sudo yum install ffmpeg
        
        Arch Linux:
        sudo pacman -S ffmpeg
        """)

def create_virtual_environment():
    """Cria ambiente virtual Python"""
    venv_path = Path("venv")
    
    if venv_path.exists():
        print("📦 Ambiente virtual já existe.")
        response = input("   Recriar? (s/N): ").lower().strip()
        if response in ['s', 'sim', 'y', 'yes']:
            print("🗑️  Removendo ambiente virtual existente...")
            shutil.rmtree(venv_path)
        else:
            return True
    
    print("📦 Criando ambiente virtual...")
    
    try:
        subprocess.run([sys.executable, '-m', 'venv', 'venv'], check=True)
        print("✅ Ambiente virtual criado com sucesso!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao criar ambiente virtual: {e}")
        return False

def get_venv_python():
    """Retorna o caminho para o Python do ambiente virtual"""
    system = platform.system().lower()
    
    if system == "windows":
        return Path("venv") / "Scripts" / "python.exe"
    else:
        return Path("venv") / "bin" / "python"

def get_venv_pip():
    """Retorna o caminho para o pip do ambiente virtual"""
    system = platform.system().lower()
    
    if system == "windows":
        return Path("venv") / "Scripts" / "pip.exe"
    else:
        return Path("venv") / "bin" / "pip"

def install_requirements():
    """Instala dependências do requirements.txt"""
    print("\n📚 Instalando dependências...")
    
    pip_path = get_venv_pip()
    
    if not pip_path.exists():
        print("❌ pip não encontrado no ambiente virtual!")
        return False
    
    # Atualizar pip primeiro
    print("   Atualizando pip...")
    try:
        subprocess.run([str(pip_path), 'install', '--upgrade', 'pip'], 
                      check=True, capture_output=True)
    except subprocess.CalledProcessError:
        print("⚠️  Aviso: Não foi possível atualizar o pip")
    
    # Instalar wheel para compilação mais rápida
    print("   Instalando wheel...")
    try:
        subprocess.run([str(pip_path), 'install', 'wheel'], 
                      check=True, capture_output=True)
    except subprocess.CalledProcessError:
        print("⚠️  Aviso: Não foi possível instalar wheel")
    
    # Instalar dependências principais
    requirements_file = Path("requirements.txt")
    
    if not requirements_file.exists():
        print("❌ Arquivo requirements.txt não encontrado!")
        return False
    
    print("   Instalando pacotes (isso pode demorar alguns minutos)...")
    
    try:
        # Instalar PyTorch primeiro (pode ser necessário para evitar conflitos)
        print("   📦 Instalando PyTorch...")
        subprocess.run([str(pip_path), 'install', 'torch>=2.0.0'], 
                      check=True, capture_output=True)
        
        # Instalar outras dependências
        print("   📦 Instalando outras dependências...")
        subprocess.run([str(pip_path), 'install', '-r', str(requirements_file)], 
                      check=True)
        
        print("✅ Dependências instaladas com sucesso!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro na instalação: {e}")
        print("\n🔧 Tentativas de solução:")
        print("   1. Verifique sua conexão com a internet")
        print("   2. Tente executar: pip install --upgrade pip")
        print("   3. Execute novamente este script")
        return False

def setup_directories():
    """Cria diretórios necessários"""
    print("\n📁 Criando diretórios...")
    
    directories = [
        "temp",
        "uploads", 
        "outputs",
        "logs",
        "data",
        "models"
    ]
    
    for directory in directories:
        dir_path = Path(directory)
        dir_path.mkdir(exist_ok=True)
        print(f"   ✅ {directory}/")
    
    # Criar arquivo .gitkeep para manter diretórios no git
    for directory in directories:
        gitkeep_file = Path(directory) / ".gitkeep"
        gitkeep_file.touch()

def check_gpu_support():
    """Verifica suporte a GPU"""
    print("\n🖥️  Verificando suporte a GPU...")
    
    python_path = get_venv_python()
    
    try:
        # Script para verificar CUDA
        check_script = """
import torch
print(f"PyTorch version: {torch.__version__}")
print(f"CUDA available: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"CUDA version: {torch.version.cuda}")
    print(f"GPU count: {torch.cuda.device_count()}")
    for i in range(torch.cuda.device_count()):
        print(f"GPU {i}: {torch.cuda.get_device_name(i)}")
        props = torch.cuda.get_device_properties(i)
        print(f"  Memory: {props.total_memory / 1024**3:.1f} GB")
else:
    print("GPU não detectada - usando CPU")
"""
        
        result = subprocess.run([str(python_path), '-c', check_script], 
                              capture_output=True, text=True, timeout=30)
        
        print(result.stdout)
        
        if "CUDA available: True" in result.stdout:
            print("🎯 GPU CUDA detectada! Processamento será acelerado.")
        else:
            print("🐌 Apenas CPU detectada. Processamento será mais lento.")
            print("   Para usar GPU, instale CUDA: https://developer.nvidia.com/cuda-downloads")
            
    except (subprocess.TimeoutExpired, subprocess.CalledProcessError) as e:
        print(f"❌ Erro ao verificar GPU: {e}")

def test_installation():
    """Testa a instalação executando verificações básicas"""
    print("\n🧪 Testando instalação...")
    
    python_path = get_venv_python()
    
    # Teste 1: Importar módulos principais
    print("   📦 Testando importações...")
    test_script = """
try:
    import streamlit
    import torch
    import whisper
    import numpy
    print("✅ Todos os módulos importados com sucesso!")
    
    # Testar carregamento do modelo tiny
    print("🔄 Testando carregamento do modelo Whisper...")
    model = whisper.load_model("tiny")
    print("✅ Modelo Whisper carregado com sucesso!")
    
except Exception as e:
    print(f"❌ Erro: {e}")
    exit(1)
"""
    
    try:
        result = subprocess.run([str(python_path), '-c', test_script], 
                              capture_output=True, text=True, timeout=120)
        
        if result.returncode == 0:
            print(result.stdout)
            print("✅ Teste de instalação passou!")
            return True
        else:
            print(f"❌ Teste falhou: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Teste demorou muito (timeout)")
        return False

def create_launch_script():
    """Cria script para iniciar a aplicação"""
    print("\n🚀 Criando script de inicialização...")
    
    system = platform.system().lower()
    
    if system == "windows":
        # Script batch para Windows
        script_content = """@echo off
echo 🎙️ Iniciando Whisper Pro Transcriber...
call venv\\Scripts\\activate
streamlit run main.py
pause
"""
        script_file = "start_whisper.bat"
    else:
        # Script shell para Unix/Linux/macOS
        script_content = """#!/bin/bash
echo "🎙️ Iniciando Whisper Pro Transcriber..."
source venv/bin/activate
streamlit run main.py
"""
        script_file = "start_whisper.sh"
    
    with open(script_file, 'w', encoding='utf-8') as f:
        f.write(script_content)
    
    # Tornar executável no Unix
    if system != "windows":
        os.chmod(script_file, 0o755)
    
    print(f"✅ Script criado: {script_file}")

def main():
    """Função principal do setup"""
    print_banner()
    
    print("Este script irá configurar o Whisper Pro Transcriber automaticamente.\n")
    
    # Verificações preliminares
    if not check_python_version():
        sys.exit(1)
    
    # FFmpeg é opcional, mas recomendado
    ffmpeg_ok = check_ffmpeg()
    if not ffmpeg_ok:
        response = input("\nContinuar sem FFmpeg? (s/N): ").lower().strip()
        if response not in ['s', 'sim', 'y', 'yes']:
            print("Por favor, instale FFmpeg e execute novamente.")
            sys.exit(1)
    
    # Configuração do ambiente
    steps = [
        ("Criando ambiente virtual", create_virtual_environment),
        ("Criando diretórios", setup_directories),
        ("Instalando dependências", install_requirements),
        ("Verificando GPU", check_gpu_support),
        ("Testando instalação", test_installation),
        ("Criando script de inicialização", create_launch_script)
    ]
    
    failed_steps = []
    
    for step_name, step_function in steps:
        print(f"\n{'='*60}")
        print(f"📋 {step_name}...")
        
        try:
            success = step_function()
            if success is False:
                failed_steps.append(step_name)
        except Exception as e:
            print(f"❌ Erro em '{step_name}': {e}")
            failed_steps.append(step_name)
    
    # Relatório final
    print(f"\n{'='*60}")
    print("🎉 SETUP CONCLUÍDO!")
    print(f"{'='*60}")
    
    if failed_steps:
        print("\n⚠️  Alguns passos falharam:")
        for step in failed_steps:
            print(f"   - {step}")
        print("\nVocê pode tentar executar novamente ou corrigir manualmente.")
    else:
        print("\n✅ Todos os passos foram executados com sucesso!")
    
    print("\n🚀 Para iniciar a aplicação:")
    
    system = platform.system().lower()
    if system == "windows":
        print("   - Execute: start_whisper.bat")
        print("   - Ou: venv\\Scripts\\activate && streamlit run main.py")
    else:
        print("   - Execute: ./start_whisper.sh")
        print("   - Ou: source venv/bin/activate && streamlit run main.py")
    
    print("\n📚 Documentação completa no README.md")
    print("🐛 Problemas? Abra uma issue no GitHub")
    
    print(f"\n{'='*60}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️  Setup cancelado pelo usuário.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n💥 Erro inesperado: {e}")
        print("Por favor, reporte este erro no GitHub.")
        sys.exit(1)