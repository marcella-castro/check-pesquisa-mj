"""
Componente de formulário de busca por processo
"""

from dash import html, dcc

def create_search_form():
    """
    Cria o formulário de busca por número de processo
    
    Returns:
        Componente Dash com o formulário
    """
    return html.Div([
        html.Div([
            html.H2("🔍 Verificador de erros", className="header-title"),
            html.P("Digite o número do processo (apenas números) para verificar erros nas respostas dos formulários", 
                   className="header-subtitle"),
            html.P("💡 A formatação CNJ será aplicada automaticamente conforme você digita", 
                   style={"fontSize": "14px", "color": "#28a745", "marginTop": "5px", "fontStyle": "italic"})
        ], className="header-section"),
        
        html.Div([
            html.Div([
                html.Label("Número do Processo:", className="input-label"),
                dcc.Input(
                    id="input-processo-numero",
                    type="text",
                    placeholder="Digite apenas números - Ex: 12345678901234567890",
                    className="form-input",
                    style={"width": "100%", "padding": "12px", "fontSize": "16px"}
                )
            ], className="input-group"),
            
            html.Div([
                html.Button(
                    "Buscar Processo",
                    id="btn-buscar",
                    n_clicks=0,
                    className="btn-primary",
                    style={
                        "padding": "10px 10px",
                        "marginBottom": "10px",
                        "fontSize": "14px",
                        "backgroundColor": "#188e44",
                        "color": "white",
                        "border": "none",
                        "borderRadius": "5px",
                        "cursor": "pointer",
                        "width": "100%"
                    }
                )
            ], className="button-group", style={"marginTop": "10px"})
        ], className="search-form"),
        
        html.Div(id="loading-indicator", children=[
            html.Div([
                html.I(className="fas fa-spinner fa-spin"),
                html.Span(" Carregando dados...", style={"marginLeft": "10px"})
            ], style={
                "textAlign": "center",
                "padding": "20px",
                "fontSize": "16px",
                "color": "#6d957e"
            })
        ], style={"display": "none"}),
        
        html.Hr(style={"margin": "30px 0"})
    ], className="search-container")

def create_search_results_placeholder():
    """
    Cria um placeholder para os resultados da busca
    
    Returns:
        Componente Dash vazio para os resultados
    """
    return html.Div(id="search-results", children=[
        html.Div([
            html.I(className="fas fa-search", style={"fontSize": "48px", "color": "#ccc"}),
            html.H4("Nenhuma busca realizada", style={"color": "#666", "marginTop": "15px"}),
            html.P("Digite um número de processo e clique em 'Buscar' para ver os resultados", 
                   style={"color": "#999"})
        ], style={
            "textAlign": "center",
            "padding": "60px 20px",
            "backgroundColor": "#f8f9fa",
            "borderRadius": "8px",
            "border": "1px solid #e9ecef"
        })
    ])
