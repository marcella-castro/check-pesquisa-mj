#!/usr/bin/env python3
"""
Script principal para executar a aplicação
"""

import os
import sys
from pathlib import Path

# Adicionar o diretório src ao path do Python
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

# Verificar se as dependências estão instaladas
try:
    import dash
    import pandas as pd
    import requests
except ImportError as e:
    print("❌ Erro: Dependências não instaladas")
    print(f"   {e}")
    print()
    print("Execute primeiro:")
    print("   python setup.py")
    print("   ou")
    print("   pip install -r requirements.txt")
    sys.exit(1)

# Verificar se arquivo .env existe
env_file = current_dir / ".env"
if not env_file.exists():
    print("⚠️  Arquivo .env não encontrado")
    print("   Copie o arquivo .env.example para .env e configure as variáveis")
    print()

if __name__ == "__main__":
    try:
        # Importar e executar a aplicação
        from app import app
        
        print("🚀 Iniciando aplicação...")
        print("   Acesse: http://localhost:8050")
        print("   Pressione Ctrl+C para parar")
        print()
        
        app.run(debug=True, host='0.0.0.0', port=8050)
        
    except KeyboardInterrupt:
        print("\n👋 Aplicação encerrada pelo usuário")
    except Exception as e:
        print(f"❌ Erro ao executar aplicação: {e}")
        sys.exit(1)
