#!/usr/bin/env python3
"""
Entrypoint de compatibilidade para plataformas que esperam `run.py` na raiz.
Ele apenas chama o script presente em `check/.hidden_code/run.py`.
"""
import os
import sys
import runpy

ROOT = os.path.dirname(__file__)
ENTRY = os.path.join(ROOT, 'check', '.hidden_code', 'run.py')

if not os.path.exists(ENTRY):
    print(f'Entrypoint nao encontrado: {ENTRY}')
    sys.exit(1)

# Garantir que o diretório do repo seja o cwd (import relativo dentro do run.py espera isso)
os.chdir(ROOT)

runpy.run_path(ENTRY, run_name='__main__')
