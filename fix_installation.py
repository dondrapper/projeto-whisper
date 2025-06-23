#!/usr/bin/env python3
"""
Script para corrigir problemas de instalação do Whisper Pro Transcriber.
Execute este script quando encontrar erros de módulos não encontrados.
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def print_header():
    """Exibe cabeçalho do script"""
    print("🔧 CORRETOR DE PROBLEMAS - Whisper Pro Transcriber")
    print("=" * 60)
    print()

def check_python_environment():
    """Verifica se está em um ambiente virtual"""
    print("🐍 Verificando ambiente Python...")
    
    # Verificar se está em venv
    in_venv = hasattr(sys, 'real_prefix') or (
        hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
    )
    
    print(f"   Versão Python: {sys.version}")
    print(f"   Ambiente virtual: {'✅ Sim' if in_venv else '❌ Não'}")
    print(f"   Executável: {sys.executable}")
    
    if not in_venv:
        print("\n⚠️  ATENÇÃO: Você não está em um ambiente virtual!")
        print("   Recomendado usar ambiente virtual para evitar conflitos.")
        
        response = input("\nContinuar mesmo assim? (s/N): ").lower().strip()
        if response not in ['s', 'sim', 'y', 'yes']:
            print("Criando ambiente virtual...")
            create_and_activate_venv()
            return False
    
    return True

def create_and_activate_venv():
    """Cria e ativa ambiente virtual"""
    print("\n📦 Criando ambiente virtual...")
    
    try:
        # Criar venv
        subprocess.run([sys.executable, '-m', 'venv', 'venv'], check=True)
        print("✅ Ambiente virtual criado!")
        
        # Instruções para ativar
        system = platform.system().lower()
        if system == "windows":
            activate_cmd = "venv\\Scripts\\activate"
        else:
            activate_cmd = "source venv/bin/activate"
        
        print(f"\n🔄 Para ativar o ambiente virtual, execute:")
        print(f"   {activate_cmd}")
        print(f"\n🔄 Depois execute novamente:")
        print(f"   python fix_installation.py")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao criar ambiente virtual: {e}")

def get_pip_command():
    """Retorna o comando pip apropriado"""
    # Tentar diferentes variações do pip
    pip_commands = ['pip', 'pip3', sys.executable + ' -m pip']
    
    for cmd in pip_commands:
        try:
            result = subprocess.run(
                cmd.split() + ['--version'], 
                capture_output=True, 
                text=True, 
                timeout=10
            )
            if result.returncode == 0:
                return cmd.split()
        except (subprocess.TimeoutExpired, FileNotFoundError):
            continue
    
    return [sys.executable, '-m', 'pip']

def install_package(package_name, pip_cmd, extra_args=None):
    """Instala um pacote específico"""
    print(f"📦 Instalando {package_name}...")
    
    cmd = pip_cmd + ['install']
    if extra_args:
        cmd.extend(extra_args)
    cmd.append(package_name)
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"✅ {package_name} instalado com sucesso!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao instalar {package_name}:")
        print(f"   {e.stderr}")
        return False

def fix_pytorch_installation():
    """Corrige problemas específicos do PyTorch"""
    print("\n🔥 Corrigindo instalação do PyTorch...")
    
    pip_cmd = get_pip_command()
    
    # Desinstalar versões problemáticas
    print("   Removendo versões antigas...")
    try:
        subprocess.run(pip_cmd + ['uninstall', 'torch', 'torchvision', 'torchaudio', '-y'], 
                      capture_output=True)
    except:
        pass
    
    # Instalar versão estável do PyTorch
    system = platform.system().lower()
    
    if system == "windows":
        # Windows - versão CPU estável
        torch_cmd = "torch>=2.0.0 --index-url https://download.pytorch.org/whl/cpu"
    else:
        # Linux/Mac - versão padrão
        torch_cmd = "torch>=2.0.0"
    
    return install_package(torch_cmd, pip_cmd)

def fix_whisper_installation():
    """Corrige problemas específicos do Whisper"""
    print("\n🎙️ Corrigindo instalação do Whisper...")
    
    pip_cmd = get_pip_command()
    
    # Tentar diferentes métodos de instalação
    whisper_sources = [
        "openai-whisper",  # Pacote oficial
        "git+https://github.com/openai/whisper.git",  # Direto do GitHub
    ]
    
    for source in whisper_sources:
        print(f"   Tentando instalar de: {source}")
        if install_package(source, pip_cmd):
            return True
        print(f"   Falhou, tentando próximo método...")
    
    return False

def install_core_dependencies():
    """Instala dependências essenciais"""
    print("\n📚 Instalando dependências essenciais...")
    
    pip_cmd = get_pip_command()
    
    # Atualizar pip primeiro
    print("   Atualizando pip...")
    try:
        subprocess.run(pip_cmd + ['install', '--upgrade', 'pip'], 
                      capture_output=True, check=True)
        print("✅ pip atualizado!")
    except:
        print("⚠️  Aviso: Não foi possível atualizar pip")
    
    # Dependências essenciais em ordem específica
    essential_packages = [
        "wheel",
        "setuptools",
        "numpy>=1.24.0",
        "streamlit>=1.28.0",
    ]
    
    success_count = 0
    for package in essential_packages:
        if install_package(package, pip_cmd):
            success_count += 1
    
    return success_count == len(essential_packages)

def install_audio_dependencies():
    """Instala dependências de áudio"""
    print("\n🎵 Instalando dependências de áudio...")
    
    pip_cmd = get_pip_command()
    
    audio_packages = [
        "ffmpeg-python>=0.2.0",
        "scipy>=1.10.0",
        "pandas>=1.5.0"
    ]
    
    success_count = 0
    for package in audio_packages:
        if install_package(package, pip_cmd):
            success_count += 1
    
    return success_count >= len(audio_packages) - 1  # Permitir 1 falha

def test_installation():
    """Testa se a instalação está funcionando"""
    print("\n🧪 Testando instalação...")
    
    # Testes de importação
    tests = [
        ("streamlit", "Streamlit"),
        ("torch", "PyTorch"),
        ("whisper", "OpenAI Whisper"),
        ("numpy", "NumPy"),
        ("pandas", "Pandas")
    ]
    
    failed_imports = []
    
    for module, name in tests:
        try:
            __import__(module)
            print(f"✅ {name} - OK")
        except ImportError as e:
            print(f"❌ {name} - FALHOU: {e}")
            failed_imports.append((module, name))
    
    if not failed_imports:
        print("\n🎉 Todos os testes passaram!")
        return True
    else:
        print(f"\n❌ {len(failed_imports)} módulo(s) com problema:")
        for module, name in failed_imports:
            print(f"   - {name} ({module})")
        return False

def test_whisper_model():
    """Testa carregamento do modelo Whisper"""
    print("\n🎯 Testando modelo Whisper...")
    
    try:
        import whisper
        print("   Carregando modelo 'tiny' para teste...")
        model = whisper.load_model("tiny")
        print("✅ Modelo Whisper carregado com sucesso!")
        return True
    except Exception as e:
        print(f"❌ Erro ao carregar modelo: {e}")
        return False

def create_simple_requirements():
    """Cria um arquivo requirements.txt simplificado"""
    print("\n📝 Criando requirements.txt simplificado...")
    
    simple_requirements = """# Dependências essenciais do Whisper Pro Transcriber
streamlit>=1.28.0
openai-whisper
torch>=2.0.0
numpy>=1.24.0
ffmpeg-python>=0.2.0
pandas>=1.5.0
scipy>=1.10.0
"""
    
    with open("requirements_simple.txt", "w", encoding="utf-8") as f:
        f.write(simple_requirements)
    
    print("✅ Arquivo 'requirements_simple.txt' criado!")
    print("   Use: pip install -r requirements_simple.txt")

def main():
    """Função principal"""
    print_header()
    
    # Verificar ambiente
    if not check_python_environment():
        return
    
    print("\n🔧 Iniciando correção de problemas...")
    
    # Sequência de correções
    steps = [
        ("Dependências essenciais", install_core_dependencies),
        ("PyTorch", fix_pytorch_installation),
        ("OpenAI Whisper", fix_whisper_installation),
        ("Dependências de áudio", install_audio_dependencies),
    ]
    
    failed_steps = []
    
    for step_name, step_function in steps:
        print(f"\n{'─' * 40}")
        print(f"🔄 {step_name}...")
        
        try:
            success = step_function()
            if not success:
                failed_steps.append(step_name)
        except Exception as e:
            print(f"❌ Erro em '{step_name}': {e}")
            failed_steps.append(step_name)
    
    # Testes finais
    print(f"\n{'═' * 50}")
    print("🧪 TESTES FINAIS")
    print(f"{'═' * 50}")
    
    installation_ok = test_installation()
    
    if installation_ok:
        whisper_ok = test_whisper_model()
    else:
        whisper_ok = False
    
    # Relatório final
    print(f"\n{'═' * 50}")
    print("📋 RELATÓRIO FINAL")
    print(f"{'═' * 50}")
    
    if installation_ok and whisper_ok:
        print("🎉 SUCESSO! Todos os problemas foram corrigidos!")
        print("\n🚀 Para executar a aplicação:")
        print("   streamlit run main.py")
    
    elif installation_ok and not whisper_ok:
        print("⚠️  PARCIAL: Módulos instalados, mas modelo Whisper com problema")
        print("\n🔧 Tente:")
        print("   pip uninstall openai-whisper")
        print("   pip install openai-whisper")
    
    else:
        print("❌ PROBLEMAS PERSISTEM")
        
        if failed_steps:
            print(f"\n❌ Etapas que falharam:")
            for step in failed_steps:
                print(f"   - {step}")
        
        print(f"\n🆘 Soluções alternativas:")
        print("1. Criar ambiente virtual limpo:")
        print("   python -m venv novo_venv")
        print("   # Ativar o ambiente")
        print("   pip install streamlit openai-whisper torch")
        
        print("\n2. Instalar manualmente:")
        print("   pip install --upgrade pip")
        print("   pip install torch --index-url https://download.pytorch.org/whl/cpu")
        print("   pip install openai-whisper")
        print("   pip install streamlit")
        
        print("\n3. Usar requirements simplificado:")
        create_simple_requirements()
    
    print(f"\n{'═' * 50}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️  Operação cancelada pelo usuário.")
    except Exception as e:
        print(f"\n\n💥 Erro inesperado: {e}")
        print("Por favor, execute novamente ou instale manualmente.")