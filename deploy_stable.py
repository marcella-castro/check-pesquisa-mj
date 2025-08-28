#!/usr/bin/env python3
"""
Deploy estável com funcionalidade completa
"""

import os
import sys
from pathlib import Path

# Adicionar src ao path
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

# Configurações de produção
os.environ['DEBUG'] = 'False'
os.environ.setdefault('HOST', '0.0.0.0')
os.environ.setdefault('PORT', '8050')

if __name__ == "__main__":
    print("🚀 Deploy estável - versão completa")
    
    try:
        from app_stable import app
        
        port = int(os.environ.get('PORT', 8050))
        host = os.environ.get('HOST', '0.0.0.0')
        
        print(f"✅ Rodando em: {host}:{port}")
        print("✅ Debug mode: OFF")
        print("✅ Modo produção ativo")
        
        app.run_server(debug=False, host=host, port=port)
        
    except Exception as e:
        print(f"❌ Erro crítico: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
