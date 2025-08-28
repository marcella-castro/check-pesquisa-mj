"""
Aplicação Dash para verificação de erros em pesquisa MJ
"""

import dash
from dash import html, dcc
from layouts.main_layout import create_main_layout
from callbacks.main_callbacks import register_callbacks
from utils.data_service import data_service

# Verificar configurações antes de iniciar
try:
    from config.settings import Config
    missing_configs = Config.validate_config()
    if missing_configs:
        print("\n⚠️  ATENÇÃO: Configurações ausentes!")
        print(f"   Variáveis de ambiente não configuradas: {', '.join(missing_configs)}")
        print("   Configure estas variáveis no seu provedor de deploy ou arquivo .env")
        print("   A aplicação funcionará em modo limitado.\n")
    config_available = Config.is_configured()
except Exception as e:
    print(f"⚠️  Erro ao carregar configurações: {e}")
    print("   A aplicação funcionará em modo limitado.\n")
    config_available = False

# Inicializar a aplicação Dash
app = dash.Dash(
    __name__,
    external_stylesheets=[
        'https://codepen.io/chriddyp/pen/bWLwgP.css',
        'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css'
    ],
    suppress_callback_exceptions=True,
    prevent_initial_callbacks=True  # Evita callbacks na inicialização
)

app.title = "Verificador de Pesquisa MJ"

# Iniciar carregamento dos dados em background apenas se configurado
if config_available:
    print("🚀 Iniciando carregamento de dados em background...")
    data_service.start_background_loading()
else:
    print("⚠️  API não configurada - dados não serão carregados automaticamente")

# Definir o layout principal
app.layout = create_main_layout()

# Registrar callbacks
register_callbacks(app)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8050)
