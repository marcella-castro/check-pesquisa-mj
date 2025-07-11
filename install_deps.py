#!/usr/bin/env python3
"""
Script alternativo para instalação de dependências
"""

import subprocess
import sys
import os

def install_package(package_name):
    """Instala um pacote específico"""
    try:
        print(f"📦 Instalando {package_name}...")
        subprocess.run([
            sys.executable, "-m", "pip", "install", package_name
        ], check=True, capture_output=True)
        print(f"✅ {package_name} instalado com sucesso")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao instalar {package_name}: {e}")
        return False

def main():
    """Função principal"""
    print("🔧 Instalação alternativa de dependências")
    print("=" * 50)
    
    # Lista de pacotes essenciais
    packages = [
        "dash",
        "pandas", 
        "numpy",
        "requests",
        "python-dotenv",
        "plotly",
        "jsonschema"
    ]
    
    # Atualizar pip primeiro
    print("📋 Atualizando pip...")
    try:
        subprocess.run([
            sys.executable, "-m", "pip", "install", "--upgrade", "pip"
        ], check=True)
        print("✅ pip atualizado")
    except:
        print("⚠️ Aviso: Não foi possível atualizar pip")
    
    # Instalar pacotes
    failed_packages = []
    for package in packages:
        if not install_package(package):
            failed_packages.append(package)
    
    # Relatório final
    print("\n" + "=" * 50)
    if not failed_packages:
        print("🎉 Todas as dependências foram instaladas com sucesso!")
        print("\nAgora você pode executar:")
        print("python src/app.py")
    else:
        print(f"⚠️ Alguns pacotes falharam: {failed_packages}")
        print("\nTente instalá-los manualmente:")
        for pkg in failed_packages:
            print(f"pip install {pkg}")

if __name__ == "__main__":
    main()
