#!/usr/bin/env python3
"""
Launcher Python para usuários não técnicos.
Cria um ambiente virtual em `.venv`, instala `requirements.txt` (se existir)
e executa `run.py` (ajuste se o entrypoint for outro).
Designed to be double-clickable on macOS/Windows (may open a terminal window).
"""

import os
import sys
import subprocess
import venv

# O lançador vive em check/Launcher/launcher; o código real foi movido para check/.hidden_code
LAUNCHER_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
HIDDEN_DIR = os.path.join(PROJECT_DIR, '.hidden_code')
VENV_DIR = os.path.join(HIDDEN_DIR, '.venv')
REQ_FILE = os.path.join(HIDDEN_DIR, 'requirements.txt')

# Possíveis entrypoints — a função tentará encontrá-los nesta ordem
POSSIBLE_ENTRYPOINTS = [
    'run.py',
    'app.py',
    'app_simple.py',
    'run_production.py',
    os.path.join('src', 'app.py')
]


def detect_entrypoint():
    # Prefer explicit run.py if presente
    # Procurar dentro de check/.hidden_code
    preferred = os.path.join(HIDDEN_DIR, 'run.py')
    if os.path.exists(preferred):
        return preferred
    for p in POSSIBLE_ENTRYPOINTS:
        candidate = os.path.join(HIDDEN_DIR, p)
        if os.path.exists(candidate):
            return candidate
    return None

def in_venv():
    return (hasattr(sys, 'real_prefix') or
            (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix))

def path_bin(*parts):
    if os.name == 'nt':
        return os.path.join(VENV_DIR, 'Scripts', *parts)
    return os.path.join(VENV_DIR, 'bin', *parts)


def main():
    try:
        # Trabalhar a partir do diretório do código escondido
        os.chdir(HIDDEN_DIR)
        if not os.path.exists(VENV_DIR):
            print('Criando ambiente virtual em .venv dentro de .hidden_code ...')
            venv.create(VENV_DIR, with_pip=True)
        pip_exe = path_bin('pip')
        python_exe = path_bin('python')

        print('Atualizando pip...')
        subprocess.check_call([pip_exe, 'install', '--upgrade', 'pip'])

        if os.path.exists(REQ_FILE):
            print('Instalando dependências de requirements.txt ...')
            subprocess.check_call([pip_exe, 'install', '-r', REQ_FILE])
        else:
            print('Nenhum requirements.txt encontrado; pulando instalação de dependências.')

        ENTRY = detect_entrypoint()
        if not ENTRY:
            print('\nNenhum entrypoint conhecido foi encontrado no projeto.')
            print('Verifique se existe `run.py`, `app.py`, `app_simple.py`, `run_production.py` ou `src/app.py`.')
            input('Pressione Enter para sair...')
            return

        print(f'Usando entrypoint detectado: {os.path.relpath(ENTRY, HIDDEN_DIR)}')
        print('\nIniciando a aplicação...\n')
        subprocess.check_call([python_exe, ENTRY])

    except subprocess.CalledProcessError as e:
        print('\nErro durante execução: ', e)
        input('Pressione Enter para fechar...')
    except Exception as e:
        print('\nErro inesperado: ', e)
        input('Pressione Enter para fechar...')

if __name__ == '__main__':
    main()
