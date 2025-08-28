#!/usr/bin/env python3
"""
Deploy de emergência - versão ultra-simplificada
"""

import os
import sys
from pathlib import Path

# Forçar produção
os.environ['DEBUG'] = 'False'
os.environ['HOST'] = '0.0.0.0'
os.environ.setdefault('PORT', '8050')

if __name__ == "__main__":
    print("🚨 Deploy de emergência - versão simplificada")
    
    try:
        from app_simple import app
        
        port = int(os.environ.get('PORT', 8050))
        host = os.environ.get('HOST', '0.0.0.0')
        
        print(f"Rodando em: {host}:{port}")
        app.run_server(debug=False, host=host, port=port)
        
    except Exception as e:
        print(f"Erro: {e}")
        sys.exit(1)
