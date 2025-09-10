#!/bin/zsh
# Clique duplo neste arquivo no macOS para criar/ativar .venv e iniciar o app via launcher/start_local.py
# Se o mac bloquear ao abrir, clique com o botão direito -> "Abrir" e confirme.
set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR/.."

# Chama o lançador Python (usa o Python do sistema para criar o venv e iniciar a app dentro dele)
python3 launcher/start_local.py
