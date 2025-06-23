#!/usr/bin/env python3
"""
Corrige problemas de ambiente virtual corrompido no Windows.
Este script detecta e corrige o problema do Python executável não encontrado.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
import platform

def print_header():
    """Exibe cabeçalho"""
    print("🔧 CORRETOR DE AMBIENTE VIRTUAL CORROMPIDO")
    print("=" * 60)
    print()

def detect_python_executable():
    """Detecta o executável Python válido"""
    print("🔍 Detectando Python válido...")
    
    # Possíveis locais do Python no Windows
    python_candidates = [
        sys.executable,  # Python atual
        "python",
        "python3",
        "py",
        "py -3",
    ]
    
    # Adicionar locais comuns no Windows
    if platform.system().lower() == "windows":
        import winreg
        try:
            # Buscar no registro do Windows
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Python\PythonCore") as key:
                for i in range(winreg.QueryInfoKey(key)[0]):
                    version = winreg.EnumKey(key, i)
                    try:
                        with winreg.OpenKey(key, f"{version}\\InstallPath") as install_key:
                            install_path = winreg.QueryValue(install_key, "")
                            python_exe = os.path.join(install_path, "python.exe")
                            if os.path.exists(python_exe):
                                python_candidates.append(python_exe)
                    except:
                        continue
        except:
            pass
        
        # Locais comuns adicionais
        common_paths = [
            r"C:\Python313\python.exe",
            r"C:\Python312\python.exe", 
            r"C:\Python311\python.exe",
            r"C:\Python310\python.exe",
            r"C:\Python39\python.exe",
            r"C:\Python38\python.exe",
            os.path.expanduser(r"~\AppData\Local\Programs\Python\Python313\python.exe"),
            os.path.expanduser(r"~\AppData\Local\Programs\Python\Python312\python.exe"),
            os.path.expanduser(r"~\AppData\Local\Programs\Python\Python311\python.exe"),
            os.path.expanduser(r"~\AppData\Local\Programs\Python\Python310\python.exe"),
        ]
        python_candidates.extend(common_paths)
    
    # Testar cada candidato
    valid_python = None
    for candidate in python_candidates:
        try:
            if candidate.startswith("py "):
                # Comando especial do Windows
                result = subprocess.run(candidate.split() + ["--version"], 
                                      capture_output=True, text=True, timeout=10)
            else:
                result = subprocess.run([candidate, "--version"], 
                                      capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                print(f"✅ Python encontrado: {candidate}")
                print(f"   Versão: {result.stdout.strip()}")
                valid_python = candidate
                break
                
        except Exception as e:
            continue
    
    if not valid_python:
        print("❌ Nenhum Python válido encontrado!")
        return None
    
    return valid_python

def remove_corrupted_venv():
    """Remove ambiente virtual corrompido"""
    venv_path = Path("venv")
    
    if venv_path.exists():
        print(f"🗑️  Removendo ambiente virtual corrompido...")
        try:
            shutil.rmtree(venv_path)
            print("✅ Ambiente virtual removido!")
            return True
        except Exception as e:
            print(f"❌ Erro ao remover venv: {e}")
            return False
    else:
        print("📁 Nenhum ambiente virtual encontrado.")
        return True

def create_new_venv(python_exe):
    """Cria novo ambiente virtual"""
    print(f"📦 Criando novo ambiente virtual com {python_exe}...")
    
    try:
        if python_exe.startswith("py "):
            # Comando especial do Windows
            cmd = python_exe.split() + ["-m", "venv", "venv"]
        else:
            cmd = [python_exe, "-m", "venv", "venv"]
        
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ Novo ambiente virtual criado!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao criar venv: {e}")
        print(f"   stderr: {e.stderr}")
        return False

def get_venv_python():
    """Retorna o caminho para o Python do venv"""
    system = platform.system().lower()
    
    if system == "windows":
        return Path("venv") / "Scripts" / "python.exe"
    else:
        return Path("venv") / "bin" / "python"

def get_venv_pip():
    """Retorna o caminho para o pip do venv"""
    system = platform.system().lower()
    
    if system == "windows":
        return Path("venv") / "Scripts" / "pip.exe"
    else:
        return Path("venv") / "bin" / "pip"

def install_essential_packages():
    """Instala pacotes essenciais"""
    print("\n📚 Instalando pacotes essenciais...")
    
    pip_path = get_venv_pip()
    
    if not pip_path.exists():
        print(f"❌ pip não encontrado em: {pip_path}")
        return False
    
    # Pacotes essenciais
    packages = [
        "wheel",
        "setuptools",
        "--upgrade pip",
        "torch>=2.0.0 --index-url https://download.pytorch.org/whl/cpu",
        "openai-whisper",
        "streamlit>=1.28.0",
        "numpy>=1.24.0",
        "pandas>=1.5.0",
        "ffmpeg-python>=0.2.0"
    ]
    
    for package in packages:
        print(f"   📦 Instalando {package}...")
        try:
            if package.startswith("--upgrade"):
                cmd = [str(pip_path), "install"] + package.split()
            else:
                cmd = [str(pip_path), "install"] + package.split()
            
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            print(f"   ✅ {package.split()[0]} instalado!")
            
        except subprocess.CalledProcessError as e:
            print(f"   ❌ Erro ao instalar {package}: {e}")
            # Continuar com outros pacotes
    
    return True

def test_installation():
    """Testa a instalação"""
    print("\n🧪 Testando instalação...")
    
    python_path = get_venv_python()
    
    if not python_path.exists():
        print(f"❌ Python do venv não encontrado: {python_path}")
        return False
    
    # Testar importações
    tests = [
        ("streamlit", "import streamlit; print('Streamlit OK')"),
        ("whisper", "import whisper; print('Whisper OK')"),
        ("torch", "import torch; print('PyTorch OK')"),
    ]
    
    all_passed = True
    
    for name, test_code in tests:
        try:
            result = subprocess.run([str(python_path), "-c", test_code], 
                                  capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                print(f"✅ {name}: {result.stdout.strip()}")
            else:
                print(f"❌ {name}: {result.stderr.strip()}")
                all_passed = False
                
        except subprocess.TimeoutExpired:
            print(f"❌ {name}: Timeout")
            all_passed = False
        except Exception as e:
            print(f"❌ {name}: {e}")
            all_passed = False
    
    return all_passed

def create_activation_scripts():
    """Cria scripts de ativação"""
    print("\n📝 Criando scripts de ativação...")
    
    # Script para Windows
    activate_bat = """@echo off
echo 🎙️ Ativando ambiente Whisper...
call venv\\Scripts\\activate.bat
echo ✅ Ambiente ativado!
echo.
echo Para executar:
echo   streamlit run main.py
echo   streamlit run main_simple.py
echo.
cmd /k
"""
    
    with open("activate.bat", "w", encoding="utf-8") as f:
        f.write(activate_bat)
    
    # Script de execução
    start_bat = """@echo off
echo 🎙️ Iniciando Whisper Pro Transcriber...
call venv\\Scripts\\activate.bat
streamlit run main_simple.py
pause
"""
    
    with open("start.bat", "w", encoding="utf-8") as f:
        f.write(start_bat)
    
    print("✅ Scripts criados:")
    print("   - activate.bat (ativar ambiente)")
    print("   - start.bat (executar aplicação)")

def main():
    """Função principal"""
    print_header()
    
    print("Este script irá corrigir seu ambiente virtual corrompido.\n")
    
    # Detectar Python válido
    python_exe = detect_python_executable()
    if not python_exe:
        print("\n💡 SOLUÇÕES:")
        print("1. Instale Python do site oficial: https://python.org/downloads")
        print("2. Certifique-se de marcar 'Add Python to PATH' na instalação")
        print("3. Reinicie o terminal após a instalação")
        input("\nPressione Enter para sair...")
        return
    
    # Remover venv corrompido
    if not remove_corrupted_venv():
        print("❌ Não foi possível remover o ambiente virtual corrompido.")
        print("Tente remover manualmente a pasta 'venv' e execute novamente.")
        input("\nPressione Enter para sair...")
        return
    
    # Criar novo venv
    if not create_new_venv(python_exe):
        print("❌ Não foi possível criar novo ambiente virtual.")
        input("\nPressione Enter para sair...")
        return
    
    # Instalar pacotes
    install_essential_packages()
    
    # Testar
    installation_ok = test_installation()
    
    # Criar scripts
    create_activation_scripts()
    
    # Relatório final
    print(f"\n{'=' * 60}")
    print("📋 RELATÓRIO FINAL")
    print(f"{'=' * 60}")
    
    if installation_ok:
        print("🎉 SUCESSO! Ambiente virtual corrigido!")
        print("\n🚀 Para usar:")
        print("   1. Execute: start.bat")
        print("   2. Ou: activate.bat, depois: streamlit run main_simple.py")
        print("   3. Acesse: http://localhost:8501")
    else:
        print("⚠️  PARCIALMENTE CORRIGIDO")
        print("Ambiente criado, mas alguns pacotes podem ter problemas.")
        print("\n🔧 Tente manualmente:")
        print("   activate.bat")
        print("   pip install openai-whisper streamlit")
    
    print(f"\n{'=' * 60}")
    input("\nPressione Enter para sair...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️  Operação cancelada.")
    except Exception as e:
        print(f"\n\n💥 Erro inesperado: {e}")
        input("Pressione Enter para sair...")