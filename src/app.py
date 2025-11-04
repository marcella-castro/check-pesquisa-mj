"""
Aplicação Dash para verificação de erros em pesquisa MJ
"""

import dash
from dash import html, dcc
from layouts.main_layout import create_main_layout
from callbacks.main_callbacks import register_callbacks
from utils.data_service_optimized import data_service
from config.settings import Config

# Inicializar a aplicação Dash
app = dash.Dash(
    __name__,
    external_stylesheets=[
        'https://codepen.io/chriddyp/pen/bWLwgP.css',
        'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css'
    ],
    suppress_callback_exceptions=True
)

app.title = "Verificador de Pesquisa MJ"

# Iniciar carregamento dos dados em background
print("🚀 Iniciando carregamento dos dados dos formulários...")
data_service.start_background_loading()

# Definir o layout principal
app.layout = create_main_layout()

# Registrar callbacks
register_callbacks(app)

if __name__ == '__main__':
    # Usar configurações do ambiente (útil em deploy)
    # Desabilitar o reloader em produção para evitar forks e exit codes inesperados
    app.run(debug=Config.DEBUG, host=Config.HOST, port=Config.PORT, use_reloader=False)
