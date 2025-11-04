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

# Verificar se as variáveis essenciais estão definidas no ambiente
essential_vars = ["LIME_API_URL", "LIME_USERNAME", "LIME_PASSWORD"]
missing = [v for v in essential_vars if not os.getenv(v)]
if missing:
    # Se o provider de deploy (ex: DigitalOcean/Oceangate) já injeta variáveis
    # no ambiente, não precisamos do arquivo .env. Avisamos somente se nenhuma
    # das variáveis essenciais estiver presente.
    if not any(os.getenv(v) for v in essential_vars):
        print("⚠️  Arquivo .env não encontrado e variáveis essenciais não estão definidas no ambiente")
        print("   Copie o arquivo .env.example para .env e configure as variáveis ou configure os secrets no provedor de deploy")
        print()

if __name__ == "__main__":
    try:
        # Importar e executar a aplicação
        from app import app
        
        print("🚀 Iniciando aplicação...")
        print("   Acesse: http://localhost:8050")
        print("   Pressione Ctrl+C para parar")
        print()
        
        # Usar configurações do ambiente definidas em Config
        from config.settings import Config
        app.run(debug=Config.DEBUG, host=Config.HOST, port=Config.PORT)
        
    except KeyboardInterrupt:
        print("\n👋 Aplicação encerrada pelo usuário")
    except Exception as e:
        print(f"❌ Erro ao executar aplicação: {e}")
        sys.exit(1)
