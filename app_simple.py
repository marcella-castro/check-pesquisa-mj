"""
Aplicação Dash simplificada para produção
"""

import dash
from dash import html, dcc

# App minimalista
app = dash.Dash(
    __name__,
    external_stylesheets=[
        'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css'
    ],
    suppress_callback_exceptions=True,
    prevent_initial_callbacks=True
)

app.title = "Verificador de Pesquisa MJ"

# Layout ultra-simples para teste
app.layout = html.Div([
    html.H1("🔍 Verificador de Erros - Pesquisa MJ", style={"textAlign": "center", "color": "#0e5327"}),
    html.P("Sistema em manutenção - Deploy em andamento", style={"textAlign": "center", "marginTop": "50px"}),
    html.Div([
        html.Button("Teste de Deploy", id="test-btn", style={
            "padding": "10px 20px",
            "backgroundColor": "#188e44",
            "color": "white",
            "border": "none",
            "borderRadius": "5px"
        }),
        html.Div(id="test-output", style={"marginTop": "20px", "textAlign": "center"})
    ], style={"textAlign": "center", "marginTop": "30px"})
], style={
    "fontFamily": "Arial, sans-serif",
    "padding": "50px",
    "maxWidth": "800px",
    "margin": "0 auto"
})

# Callback simples para teste
@app.callback(
    dash.dependencies.Output('test-output', 'children'),
    [dash.dependencies.Input('test-btn', 'n_clicks')],
    prevent_initial_call=True
)
def test_callback(n_clicks):
    if n_clicks:
        return html.P(f"✅ Deploy funcionando! Cliques: {n_clicks}", style={"color": "green"})
    return ""

if __name__ == '__main__':
    app.run_server(debug=False, host='0.0.0.0', port=8050)
