"""
Componente para exibir relatório de erros
"""

from dash import html, dash_table
import pandas as pd
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
    
    color = severity_colors.get(severidade, '#6c757d')
    
    cards = []
    
    # Card principal de status
    cards.append(html.Div([
        html.H4("📊 Resumo da Validação", style={"marginBottom": "15px"}),
        html.Div([
            html.Div([
                html.H3(str(total_erros), style={"margin": "0", "fontSize": "2.5em"}),
                html.P("Erros Encontrados", style={"margin": "5px 0 0 0", "fontSize": "14px"})
            ], style={
                "textAlign": "center",
                "color": color,
                "backgroundColor": "white",
                "padding": "20px",
                "borderRadius": "8px",
                "border": f"2px solid {color}",
                "flex": "1",
                "marginRight": "15px"
            }),
            
            html.Div([
                html.H3(severidade, style={"margin": "0", "fontSize": "1.8em"}),
                html.P("Severidade", style={"margin": "5px 0 0 0", "fontSize": "14px"})
            ], style={
                "textAlign": "center",
                "color": color,
                "backgroundColor": "white",
                "padding": "20px",
                "borderRadius": "8px",
                "border": f"2px solid {color}",
                "flex": "1"
            })
        ], style={"display": "flex", "alignItems": "stretch"})
    ], style={
        "backgroundColor": "#f8f9fa",
        "padding": "20px",
        "borderRadius": "8px",
        "marginBottom": "20px"
    }))
    
    # Cards por categoria
    if 'categorias' in summary:
        categoria_cards = []
        categorias_info = {
            'processo': {'name': 'Processo', 'icon': '📄', 'color': '#007bff'},
            'vitima': {'name': 'Vítima', 'icon': '👤', 'color': '#28a745'},
            'reu': {'name': 'Réu', 'icon': '⚖️', 'color': '#ffc107'},
            'provas': {'name': 'Provas', 'icon': '📁', 'color': '#dc3545'},
            'gerais': {'name': 'Gerais', 'icon': '🔧', 'color': '#6c757d'}
        }
        
        for categoria, count in summary['categorias'].items():
            if count > 0:
                info = categorias_info.get(categoria, {'name': categoria.title(), 'icon': '❗', 'color': '#666'})
                categoria_cards.append(html.Div([
                    html.Div([
                        html.Span(info['icon'], style={"fontSize": "24px", "marginBottom": "10px"}),
                        html.H4(str(count), style={"margin": "0", "fontSize": "1.5em"}),
                        html.P(info['name'], style={"margin": "5px 0 0 0", "fontSize": "12px"})
                    ])
                ], style={
                    "textAlign": "center",
                    "color": info['color'],
                    "backgroundColor": "white",
                    "padding": "15px",
                    "borderRadius": "8px",
                    "border": f"1px solid {info['color']}",
                    "flex": "1",
                    "margin": "0 5px"
                }))
        
        if categoria_cards:
            cards.append(html.Div([
                html.H5("Erros por Categoria", style={"marginBottom": "15px"}),
                html.Div(categoria_cards, style={"display": "flex", "flexWrap": "wrap"})
            ], style={
                "backgroundColor": "#f8f9fa",
                "padding": "20px",
                "borderRadius": "8px",
                "marginBottom": "20px"
            }))
    
    return html.Div(cards)

def create_detailed_errors(erros: Dict):
    """Cria seção detalhada dos erros"""
    if not erros:
        return html.Div()
    
    error_sections = []
    
    for categoria, lista_erros in erros.items():
        if not lista_erros:
            continue
        
        # Diferentes formatos para erros gerais vs específicos
        if categoria == 'gerais':
            error_sections.append(create_general_errors_section(lista_erros))
        else:
            error_sections.append(create_category_errors_section(categoria, lista_erros))
    
    if not error_sections:
        return create_no_errors_found()
    
    return html.Div([
        html.H4("📋 Detalhes por Categoria", style={"marginTop": "30px", "marginBottom": "20px"}),
        *error_sections
    ])

def create_category_errors_section(categoria: str, erros_lista: list):
    """Cria seção de erros para uma categoria específica usando tabela"""
    if not erros_lista:
        return html.Div()
    
    categoria_names = {
        'processo': 'Processo',
        'vitima': 'Vítima', 
        'reu': 'Réu',
        'provas': 'Provas'
    }
    
    categoria_icons = {
        'processo': '📄',
        'vitima': '👤',
        'reu': '⚖️',
        'provas': '📁'
    }
    
    titulo = categoria_names.get(categoria, categoria.title())
    icon = categoria_icons.get(categoria, '❗')
    
    # Converter erros para DataFrame para usar dash_table
    if erros_lista and isinstance(erros_lista[0], dict):
        df_erros = pd.DataFrame(erros_lista)
        
        # Selecionar e renomear colunas para exibição
        colunas_exibir = ['Formulário', 'Campo', 'Tipo de Erro', 'Valor Encontrado', 'Regra Violada / Esperado', 'Bolsista']
        colunas_existentes = [col for col in colunas_exibir if col in df_erros.columns]
        
        if colunas_existentes:
            df_display = df_erros[colunas_existentes].copy()
            
            # Limitar tamanho dos valores para melhor exibição
            for col in df_display.columns:
                df_display[col] = df_display[col].astype(str).apply(lambda x: x[:100] + '...' if len(str(x)) > 100 else str(x))
            
            table = dash_table.DataTable(
                data=df_display.to_dict('records'),
                columns=[{"name": col, "id": col} for col in df_display.columns],
                style_table={'overflowX': 'auto'},
                style_cell={
                    'textAlign': 'left',
                    'padding': '10px',
                    'fontFamily': 'Arial, sans-serif',
                    'fontSize': '12px',
                    'whiteSpace': 'normal',
                    'height': 'auto',
                },
                style_header={
                    'backgroundColor': '#f8f9fa',
                    'fontWeight': 'bold',
                    'border': '1px solid #dee2e6'
                },
                style_data={
                    'border': '1px solid #dee2e6'
                },
                style_data_conditional=[
                    {
                        'if': {'row_index': i},
                        'backgroundColor': '#fff5f5' if i % 2 == 0 else '#ffffff'
                    } for i in range(len(df_display))
                ]
            )
        else:
            table = html.P("Dados de erro não puderam ser formatados para exibição.")
    else:
        # Fallback para erros que não são dicionários
        table = html.Ul([
            html.Li(str(erro)) for erro in erros_lista
        ])
    
    return html.Div([
        html.H5([
            html.Span(icon, style={"marginRight": "10px", "fontSize": "20px"}),
            f"{titulo} ({len(erros_lista)} erro{'s' if len(erros_lista) > 1 else ''})"
        ], style={"color": "#dc3545", "marginBottom": "15px"}),
        
        table
        
    ], style={
        "backgroundColor": "#fff5f5",
        "padding": "20px",
        "borderRadius": "8px",
        "border": "1px solid #fed7d7",
        "marginBottom": "20px"
    })

def create_general_errors_section(erros_lista: list):
    """Cria seção de erros gerais"""
    if not erros_lista:
        return html.Div()
    
    error_items = []
    for idx, erro in enumerate(erros_lista, 1):
        error_items.append(html.Li([
            html.Span(f"#{idx}", style={
                "backgroundColor": "#6c757d",
                "color": "white",
                "padding": "2px 6px",
                "borderRadius": "10px",
                "fontSize": "11px",
                "marginRight": "8px",
                "fontWeight": "bold"
            }),
            str(erro)
        ], style={"marginBottom": "8px"}))
    
    return html.Div([
        html.H5([
            html.Span("🔧", style={"marginRight": "10px", "fontSize": "20px"}),
            f"Erros Gerais ({len(erros_lista)} erro{'s' if len(erros_lista) > 1 else ''})"
        ], style={"color": "#dc3545", "marginBottom": "15px"}),
        
        html.Ul(error_items, style={"listStyleType": "none", "paddingLeft": "0"})
        
    ], style={
        "backgroundColor": "#fff5f5",
        "padding": "20px",
        "borderRadius": "8px",
        "border": "1px solid #fed7d7",
        "marginBottom": "20px"
    })

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
