#!/usr/bin/env python3
"""
Script simplificado para deploy em produção
"""

import os
import sys
from pathlib import Path

# Adicionar o diretório src ao path do Python
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

# Forçar modo produção
os.environ.setdefault('DEBUG', 'False')
os.environ.setdefault('HOST', '0.0.0.0')
os.environ.setdefault('PORT', '8050')

if __name__ == "__main__":
    try:
        # Import simplificado
        print("🚀 Iniciando aplicação em modo produção...")
        
        from app import app
        
        port = int(os.environ.get('PORT', 8050))
        host = os.environ.get('HOST', '0.0.0.0')
        
        print(f"   Rodando em: {host}:{port}")
        
        # Sempre debug=False em produção
        app.run_server(debug=False, host=host, port=port)
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
