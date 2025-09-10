Instruções para usuários não técnicos — executar o app localmente

Arquivos fornecidos:

Como usar (macOS):
1. Abra a pasta onde esses arquivos estão. Duplo-clique em `run_app.command`.
2. Na primeira execução o mac pode pedir confirmação porque o arquivo foi baixado da internet. Use botão direito -> Abrir.
3. O script criará um ambiente virtual `.venv` na mesma pasta, instalará dependências e iniciará o app.
Observação sobre entrypoint:
O lançador prefere `run.py` como entrypoint se ele existir (este é o caso do projeto atual). Se por algum motivo seu entrypoint for outro arquivo, edite `launcher/start_local.py` e adicione o arquivo à lista `POSSIBLE_ENTRYPOINTS`.

Próximos passos opcionais:
- Posso ajustar o entrypoint automaticamente lendo o conteúdo do arquivo para detectar `app.run_server` ou `app.run`.
- Posso gerar um executável standalone (mac .app / Windows .exe) usando PyInstaller ou empacotar com Electron para uma experiência ainda mais simples (requer testes e pode aumentar tamanho do arquivo).
2. O script criará `.venv` (se não existir), instalará dependências e iniciará o app numa janela de terminal.

Observações e solução de problemas:
- Se nada acontecer ao duplo-clique no mac, selecione o arquivo e pressione Cmd+I -> Abrir com -> Terminal.app, ou use o Terminal e execute:

  chmod +x launcher/run_app.command
  ./launcher/run_app.command

- Se o Python não estiver instalado no sistema, é necessário instalar o Python 3 (https://www.python.org/downloads/).
- Se o app usa outro arquivo como entrypoint (por exemplo `app.py` ou `run_production.py`), edite `launcher/start_local.py` e os arquivos `.command/.bat` substituindo `run.py` pelo arquivo correto.
- O processo pode demorar na primeira execução porque instala dependências.

Se quiser, posso:  
- Ajustar o entrypoint automaticamente (leio `run.py` para detectar `app.run_server`),  
- Gerar um pacote standalone (mac .app / Windows .exe) usando ferramentas como PyInstaller/Electron (mais trabalho).
