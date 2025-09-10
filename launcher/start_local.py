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

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
VENV_DIR = os.path.join(ROOT, '.venv')
REQ_FILE = os.path.join(ROOT, 'requirements.txt')

# Possíveis entrypoints — a função tentará encontrá-los nesta ordem
POSSIBLE_ENTRYPOINTS = [
    'run.py',
    'app.py',
    'app_simple.py',
    'run_production.py',
    os.path.join('src', 'app.py'),
    # Entrypoints do layout usado neste repositório
    os.path.join('check', '.hidden_code', 'run.py'),
    os.path.join('check', '.hidden_code', 'src', 'run.py'),
]


def detect_entrypoint():
    # Allow override via variável de ambiente CHECK_ENTRYPOINT (ex: "check/.hidden_code/run.py")
    env_ep = os.environ.get('CHECK_ENTRYPOINT')
    if env_ep:
        candidate = os.path.join(ROOT, env_ep) if not os.path.isabs(env_ep) else env_ep
        if os.path.exists(candidate):
            return candidate
        else:
            print(f'Variavel CHECK_ENTRYPOINT definida mas arquivo nao encontrado: {candidate}')

    # Prefer explicit run.py se presente
    preferred = os.path.join(ROOT, 'run.py')
    if os.path.exists(preferred):
        return preferred

    # Verificar candidatos conhecidos
    for p in POSSIBLE_ENTRYPOINTS:
        candidate = os.path.join(ROOT, p)
        if os.path.exists(candidate):
            return candidate

    # Se solicitado, imprimir diagnóstico detalhado para ajudar debugging
    if os.environ.get('CHECK_LAUNCHER_DEBUG'):
        print('\n[DEBUG] Launcher diagnostics:')
        print(f'  ROOT = {ROOT}')
        print('  Checando candidatos:')
        for p in POSSIBLE_ENTRYPOINTS:
            candidate = os.path.join(ROOT, p)
            try:
                exists = os.path.exists(candidate)
            except Exception:
                exists = False
            print(f'    {candidate} -> exists={exists}')
        # também checar local comum dentro de check/.hidden_code
        extra = os.path.join(ROOT, 'check', '.hidden_code', 'run.py')
        print(f'    Extra check: {extra} -> exists={os.path.exists(extra)}')

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
        os.chdir(ROOT)
        if not os.path.exists(VENV_DIR):
            print('Criando ambiente virtual em .venv ...')
            venv.create(VENV_DIR, with_pip=True)

        # Usar o python do venv e invocar pip via "python -m pip" para evitar dependência
        # em scripts de wrapper que podem não existir (ex: pip, pip3)
        python_exe = path_bin('python')
        pip_cmd = [python_exe, '-m', 'pip']

        # Atualizar pip usando o python do venv
        print('Atualizando pip (usando python -m pip)...')
        try:
            subprocess.check_call(pip_cmd + ['install', '--upgrade', 'pip'])
        except FileNotFoundError:
            # Se o binario do python não existir no venv (algo deu errado na criacao)
            print('Erro: python do ambiente virtual nao encontrado em:', python_exe)
            print('Verifique permissões e se o venv foi criado corretamente.')
            input('Pressione Enter para sair...')
            return
        except subprocess.CalledProcessError:
            # Tentar fallback para pip3 script
            pip3_script = path_bin('pip3')
            if os.path.exists(pip3_script):
                print('Tentando usar pip3 diretamente...')
                subprocess.check_call([pip3_script, 'install', '--upgrade', 'pip'])
            else:
                # Tentar ensurepip
                print('pip nao instalado no venv; tentando ensurepip...')
                try:
                    subprocess.check_call([python_exe, '-m', 'ensurepip', '--upgrade'])
                except Exception as e:
                    print('Falha ao tentar instalar pip dentro do venv:', e)
                    input('Pressione Enter para sair...')
                    return

        if os.path.exists(REQ_FILE):
            print('Instalando dependências de requirements.txt (usando python -m pip)...')
            try:
                subprocess.check_call(pip_cmd + ['install', '-r', REQ_FILE])
            except subprocess.CalledProcessError as e:
                print('Erro ao instalar dependencias:', e)
                input('Pressione Enter para sair...')
                return
        else:
            print('Nenhum requirements.txt encontrado; pulando instalação de dependências.')

        ENTRY = detect_entrypoint()
        if not ENTRY:
            print('\nNenhum entrypoint conhecido foi encontrado no projeto.')
            print('Verifique se existe `run.py`, `app.py`, `app_simple.py`, `run_production.py` ou `src/app.py`.')
            input('Pressione Enter para sair...')
            return

        print(f'Usando entrypoint detectado: {os.path.relpath(ENTRY, ROOT)}')
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
