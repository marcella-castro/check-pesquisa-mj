"""
Aplicação Dash para verificação de erros em pesquisa MJ
"""

import dash
from dash import html, dcc
from layouts.main_layout import create_main_layout
from callbacks.main_callbacks import register_callbacks
from utils.data_service import data_service

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
    app.run(debug=True, host='0.0.0.0', port=8050)
