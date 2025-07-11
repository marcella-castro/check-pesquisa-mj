#!/usr/bin/env python3
"""
Script de inicialização da aplicação Pesquisa MJ
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def print_header():
    """Imprime cabeçalho do script"""
    print("=" * 60)
    print("🔧 CONFIGURAÇÃO - Sistema Verificação Pesquisa MJ")
    print("=" * 60)
    print()

def check_python_version():
    """Verifica versão do Python"""
    print("📋 Verificando versão do Python...")
    
    if sys.version_info < (3, 8):
        print("❌ Erro: Python 3.8 ou superior é necessário")
        print(f"   Versão atual: {sys.version}")
        return False
    
    print(f"✅ Python {sys.version.split()[0]} detectado")
    return True

def check_pip():
    """Verifica se pip está disponível"""
    print("📋 Verificando pip...")
    
    try:
        subprocess.run([sys.executable, "-m", "pip", "--version"], 
                      check=True, capture_output=True)
        print("✅ pip está disponível")
        return True
    except subprocess.CalledProcessError:
        print("❌ Erro: pip não encontrado")
        return False

def create_virtual_environment():
    """Cria ambiente virtual se não existir"""
    print("📋 Verificando ambiente virtual...")
    
    venv_path = Path("venv")
    
    if venv_path.exists():
        print("✅ Ambiente virtual já existe")
        return True
    
    print("📦 Criando ambiente virtual...")
    try:
        subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
        print("✅ Ambiente virtual criado com sucesso")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao criar ambiente virtual: {e}")
        return False

def get_venv_python():
    """Retorna caminho para o Python do ambiente virtual"""
    if os.name == 'nt':  # Windows
        return Path("venv/Scripts/python.exe")
    else:  # macOS/Linux
        return Path("venv/bin/python")

def install_dependencies():
    """Instala dependências do requirements.txt"""
    print("📋 Instalando dependências...")
    
    venv_python = get_venv_python()
    
    if not venv_python.exists():
        print("❌ Erro: Python do ambiente virtual não encontrado")
        return False
    
    try:
        subprocess.run([
            str(venv_python), "-m", "pip", "install", "--upgrade", "pip"
        ], check=True)
        
        subprocess.run([
            str(venv_python), "-m", "pip", "install", "-r", "requirements.txt"
        ], check=True)
        
        print("✅ Dependências instaladas com sucesso")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao instalar dependências: {e}")
        return False

def setup_environment_file():
    """Configura arquivo de ambiente"""
    print("📋 Configurando arquivo de ambiente...")
    
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if env_file.exists():
        print("✅ Arquivo .env já existe")
        return True
    
    if env_example.exists():
        shutil.copy(env_example, env_file)
        print("✅ Arquivo .env criado a partir do exemplo")
        print("⚠️  ATENÇÃO: Configure as variáveis no arquivo .env antes de executar")
        return True
    else:
        print("❌ Arquivo .env.example não encontrado")
        return False

def print_next_steps():
    """Imprime próximos passos"""
    print()
    print("=" * 60)
    print("🎉 CONFIGURAÇÃO CONCLUÍDA!")
    print("=" * 60)
    print()
    print("📝 Próximos passos:")
    print()
    print("1. Configure o arquivo .env com suas credenciais:")
    print("   - LIME_API_URL: URL da sua instância LimeSurvey")
    print("   - LIME_USERNAME: Seu usuário")
    print("   - LIME_PASSWORD: Sua senha")
    print("   - SURVEY_ID: ID do seu survey")
    print()
    print("2. Ative o ambiente virtual:")
    if os.name == 'nt':  # Windows
        print("   venv\\Scripts\\activate")
    else:  # macOS/Linux
        print("   source venv/bin/activate")
    print()
    print("3. Execute a aplicação:")
    print("   python src/app.py")
    print()
    print("4. Acesse no navegador:")
    print("   http://localhost:8050")
    print()

def main():
    """Função principal"""
    print_header()
    
    # Verificações iniciais
    if not check_python_version():
        sys.exit(1)
    
    if not check_pip():
        sys.exit(1)
    
    # Configuração do ambiente
    if not create_virtual_environment():
        sys.exit(1)
    
    if not install_dependencies():
        sys.exit(1)
    
    if not setup_environment_file():
        sys.exit(1)
    
    print_next_steps()

if __name__ == "__main__":
    main()
