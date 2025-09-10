@echo off
REM run_app.bat - Clique duplo neste arquivo no Windows para criar/ativar .venv e iniciar o app via launcher/start_local.py

SETLOCAL ENABLEDELAYEDEXPANSION

REM Mudar para a pasta pai do diretório deste script (raiz do projeto)
PUSHD "%~dp0.."

REM Caminho absoluto para o script de lançamento
SET "START_SCRIPT=%CD%\launcher\start_local.py"

IF NOT EXIST "%START_SCRIPT%" (
	echo Arquivo nao encontrado: "%START_SCRIPT%"
	echo Verifique se este .bat esta dentro da pasta "launcher" do repositorio.
	pause
	POPD
	ENDLOCAL
	EXIT /B 1
)

REM Tentar usar o launcher py (recomendado no Windows), senao tentar python
where py >nul 2>&1
IF %ERRORLEVEL%==0 (
	py -3 "%START_SCRIPT%"
) ELSE (
	where python >nul 2>&1
	IF %ERRORLEVEL%==0 (
		python "%START_SCRIPT%"
	) ELSE (
		echo Nenhum interpretador Python (py ou python) encontrado no PATH.
		echo Instale o Python 3 e habilite o launcher "py" ou adicione "python" ao PATH.
		pause
		POPD
		ENDLOCAL
		EXIT /B 1
	)
)

REM Manter janela aberta para ver mensagens de erro
echo.
echo Processo terminado. Pressione qualquer tecla para fechar.
pause

POPD
ENDLOCAL
