"""
Layout principal da aplicação
"""

from dash import html, dcc
from components.search_form import create_search_form, create_search_results_placeholder

def create_main_layout():
    """
    Cria o layout principal da aplicação
    
    Returns:
        Layout principal do Dash
    """
    return html.Div([
        # Header da aplicação
        html.Div([
            html.H1([
                "Sistema de Verificação - Pesquisa 'Mensurando o tempo do Processo de Homicídio'"
            ], style={
                "textAlign": "center",
                "color": "#0e5327",
                "marginBottom": "10px",
                "fontSize": "28px"
            }),
            html.P(
                "Ferramenta para validação de dados coletados nos formulários dos bolsistas",
                style={
                    "textAlign": "center",
                    "color": "#6d957e",
                    "fontSize": "16px",
                    "marginBottom": "0"
                }
            )
        ], style={
            "backgroundColor": "#ecf0f1",
            "padding": "30px 20px",
            "marginBottom": "30px",
            "borderBottom": "3px solid #3498db"
        }),
        
        # Status de carregamento dos dados
        html.Div(id="data-status", style={"marginBottom": "20px"}),
        
        # Container principal
        html.Div([
            # Formulário de busca
            create_search_form(),
            
            # Resultados da busca
            create_search_results_placeholder()
            
        ], style={
            "maxWidth": "1200px",
            "margin": "0 auto",
            "padding": "0 20px"
        }),
        
        
        # Interval para atualizar status
        dcc.Interval(
            id='status-interval',
            interval=2000,  # Atualiza a cada 2 segundos
            n_intervals=0
        )
        
    ], style={
        "fontFamily": "Arial, sans-serif",
        "backgroundColor": "#ffffff",
        "minHeight": "100vh"
    })
