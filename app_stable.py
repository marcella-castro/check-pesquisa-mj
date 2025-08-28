"""
Aplicação Dash estável para produção - versão completa
"""

import dash
from dash import html, dcc
import os

# Configuração estável para produção
app = dash.Dash(
    __name__,
    external_stylesheets=[
        'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css'
    ],
    suppress_callback_exceptions=True,
    prevent_initial_callbacks=True
)

app.title = "Verificador de Pesquisa MJ"

# Verificar configurações de forma segura
config_available = False
try:
    from config.settings import Config
    missing_configs = Config.validate_config()
    if missing_configs:
        print(f"⚠️  Configurações ausentes: {', '.join(missing_configs)}")
    else:
        config_available = True
        print("✅ Configurações carregadas com sucesso")
except Exception as e:
    print(f"⚠️  Erro ao carregar configurações: {e}")

# Importar layout e callbacks apenas se necessário
try:
    from layouts.main_layout import create_main_layout
    from callbacks.main_callbacks import register_callbacks
    
    # Layout principal
    app.layout = create_main_layout()
    
    # Registrar callbacks
    register_callbacks(app)
    
    print("✅ Layout e callbacks carregados com sucesso")
    
except Exception as e:
    print(f"❌ Erro ao carregar layout/callbacks: {e}")
    # Layout de fallback
    app.layout = html.Div([
        html.H1("⚠️ Sistema em Manutenção"),
        html.P(f"Erro de configuração: {str(e)}")
    ])

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8050))
    host = os.environ.get('HOST', '0.0.0.0')
    app.run_server(debug=False, host=host, port=port)
