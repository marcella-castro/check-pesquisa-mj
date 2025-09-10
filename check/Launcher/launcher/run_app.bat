@echo off
REM Clique duplo neste arquivo no Windows para criar/ativar .venv e iniciar o app via launcher/start_local.py
cd /d %~dp0\..

REM Use o python do sistema para executar o lançador, que criará/ativará .venv e iniciará a aplicação
python launcher\start_local.py
pause
