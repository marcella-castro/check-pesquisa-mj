"""
Componente para exibir relatório de erros
"""

from dash import html
from typing import Dict

def create_error_report(erros: Dict, validation_summary: Dict):
    """
    Cria o componente de relatório de erros
    
    Args:
        erros: Dicionário com erros por categoria
        validation_summary: Resumo das validações
        
    Returns:
        Componente Dash com relatório de erros
    """
    if not erros or validation_summary.get('total_erros', 0) == 0:
        return create_no_errors_found()
    
    return html.Div([
        html.H3("🔍 Relatório de Erros", className="section-title"),
        
        # Summary cards
        create_error_summary_cards(validation_summary),
        
        # Detailed errors by category
        create_detailed_errors(erros),
        
    ], className="error-report")

def create_error_summary_cards(summary: Dict):
    """Cria cards de resumo dos erros"""
    total_erros = summary.get('total_erros', 0)
    severidade = summary.get('severidade', 'NENHUM')
    status = summary.get('status', 'OK')
    
    # Determinar cores baseadas na severidade
    severity_colors = {
        'NENHUM': '#28a745',
        'BAIXA': '#28a745', 
        'MÉDIA': '#ffc107',
        'ALTA': '#dc3545'
    }
    
    status_colors = {
        'OK': '#28a745',
        'ERRO': '#dc3545'
    }
    
    return html.Div([
        create_summary_card(
            "📊 Total de Erros", 
            str(total_erros),
            status_colors.get(status, '#666')
        ),
        create_summary_card(
            "⚠️ Severidade", 
            severidade,
            severity_colors.get(severidade, '#666')
        ),
        create_summary_card(
            "✅ Status", 
            status,
            status_colors.get(status, '#666')
        )
    ], style={
        "display": "grid",
        "gridTemplateColumns": "repeat(auto-fit, minmax(200px, 1fr))",
        "gap": "15px",
        "marginBottom": "25px"
    })

def create_summary_card(title: str, value: str, color: str):
    """Cria um card de resumo"""
    return html.Div([
        html.H4(title, style={
            "margin": "0 0 8px 0", 
            "color": "#666", 
            "fontSize": "14px"
        }),
        html.P(value, style={
            "margin": "0", 
            "fontSize": "24px", 
            "fontWeight": "bold", 
            "color": color
        })
    ], style={
        "backgroundColor": "#f8f9fa",
        "padding": "20px",
        "borderRadius": "8px",
        "border": f"2px solid {color}",
        "textAlign": "center"
    })

def create_detailed_errors(erros: Dict):
    """Cria seção detalhada dos erros por categoria"""
    categorias_config = {
        'processo': {'icon': '📄', 'title': 'Erros de Processo', 'color': '#dc3545'},
        'vitima': {'icon': '👤', 'title': 'Erros de Vítima', 'color': '#fd7e14'},
        'reu': {'icon': '⚖️', 'title': 'Erros de Réu', 'color': '#6f42c1'},
        'provas': {'icon': '📁', 'title': 'Erros de Provas', 'color': '#20c997'},
        'gerais': {'icon': '🔧', 'title': 'Erros Gerais', 'color': '#6c757d'}
    }
    
    error_sections = []
    
    for categoria, lista_erros in erros.items():
        if not lista_erros:  # Pular categorias sem erros
            continue
            
        config = categorias_config.get(categoria, {
            'icon': '❗', 
            'title': f'Erros de {categoria.title()}', 
            'color': '#666'
        })
        
        error_items = []
        for i, erro in enumerate(lista_erros, 1):
            error_items.append(html.Li([
                html.Span(f"#{i}", style={
                    "backgroundColor": config['color'],
                    "color": "white",
                    "padding": "2px 6px",
                    "borderRadius": "10px",
                    "fontSize": "11px",
                    "marginRight": "8px",
                    "fontWeight": "bold"
                }),
                html.Span(erro, style={"fontSize": "14px"})
            ], style={"marginBottom": "8px", "listStyle": "none"}))
        
        error_sections.append(html.Div([
            html.H4([
                html.Span(config['icon'], style={"marginRight": "8px"}),
                config['title'],
                html.Span(f" ({len(lista_erros)})", style={
                    "backgroundColor": config['color'],
                    "color": "white",
                    "padding": "2px 8px",
                    "borderRadius": "12px",
                    "fontSize": "12px",
                    "marginLeft": "8px"
                })
            ], style={"color": config['color'], "marginBottom": "12px"}),
            
            html.Ul(error_items, style={
                "padding": "0",
                "margin": "0"
            })
        ], style={
            "backgroundColor": "#f8f9fa",
            "padding": "20px",
            "borderRadius": "8px",
            "border": f"1px solid {config['color']}",
            "marginBottom": "20px"
        }))
    
    return html.Div(error_sections)

def create_no_errors_found():
    """Cria componente quando nenhum erro é encontrado"""
    return html.Div([
        html.I(className="fas fa-check-circle", 
               style={"fontSize": "48px", "color": "#28a745"}),
        html.H4("✅ Nenhum erro encontrado!", 
                style={"color": "#28a745", "marginTop": "15px"}),
        html.P("Todas as validações passaram com sucesso. Os dados estão consistentes.", 
               style={"color": "#666"})
    ], style={
        "textAlign": "center",
        "padding": "60px 20px",
        "backgroundColor": "#d4edda",
        "borderRadius": "8px",
        "border": "1px solid #c3e6cb"
    })
