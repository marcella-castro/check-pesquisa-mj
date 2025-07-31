"""
Componente para exibir resumo do processo
"""

from dash import html, dash_table
import pandas as pd
from typing import Dict

def create_process_summary(processo_data: Dict, all_data: Dict[str, pd.DataFrame]):
    """
    Cria o componente de resumo do processo
    
    Args:
        processo_data: Dicionário com dados resumidos do processo
        all_data: Dicionário com DataFrames por categoria
        
    Returns:
        Componente Dash com resumo do processo
    """
    if not processo_data or processo_data.get('total_respostas', 0) == 0:
        return create_no_data_found()
    
    return html.Div([
        html.H3("📋 Resumo do Processo", className="section-title"),
        
        # Cards com informações principais
        html.Div([
            create_info_card("📄 Número do Processo", get_processo_numero(all_data)),
            create_info_card("🔢 Número de Controle", get_numero_controle(all_data)),
            create_info_card("📊 Total Respostas", str(processo_data.get('total_respostas', 0))),
            create_info_card("📅 Última Atualização", 
                           format_date(processo_data.get('ultima_atualizacao')))
        ], className="info-cards-container", style={
            "display": "grid",
            "gridTemplateColumns": "repeat(auto-fit, minmax(200px, 1fr))",
            "gap": "15px",
            "marginBottom": "25px"
        }),
        
        # Resumo por categoria
        create_category_summary(processo_data.get('categorias', {})),
        
        # Tabela com preview dos dados por categoria
        create_category_data_preview(all_data),
        
        # Observações do Bolsista
        create_observacoes_bolsista(all_data)
        
    ], className="process-summary")

def create_info_card(title: str, value: str):
    """Cria um card de informação"""
    return html.Div([
        html.H4(title, style={"margin": "0 0 8px 0", "color": "#666", "fontSize": "14px"}),
        html.P(value, style={"margin": "0", "fontSize": "18px", "fontWeight": "bold", "color": "#333"})
    ], style={
        "backgroundColor": "#f8f9fa",
        "padding": "15px",
        "borderRadius": "8px",
        "border": "1px solid #e9ecef",
        "textAlign": "center"
    })

def create_fill_statistics(campos_stats: Dict):
    """Cria estatísticas de preenchimento de campos"""
    if not campos_stats:
        return html.Div()
    
    # Ordenar campos por percentual de preenchimento
    campos_ordenados = sorted(
        campos_stats.items(), 
        key=lambda x: x[1].get('percentual', 0), 
        reverse=True
    )
    
    stats_rows = []
    for campo, stats in campos_ordenados[:10]:  # Mostrar apenas top 10
        percentual = stats.get('percentual', 0)
        preenchidos = stats.get('preenchidos', 0)
        total = stats.get('total', 0)
        
        # Determinar cor baseada no percentual
        if percentual >= 80:
            color = "#28a745"  # Verde
        elif percentual >= 50:
            color = "#ffc107"  # Amarelo
        else:
            color = "#dc3545"  # Vermelho
        
        stats_rows.append(html.Tr([
            html.Td(campo, style={"fontWeight": "bold"}),
            html.Td(f"{preenchidos}/{total}", style={"textAlign": "center"}),
            html.Td([
                html.Div(style={
                    "width": f"{percentual}%",
                    "height": "20px",
                    "backgroundColor": color,
                    "borderRadius": "10px",
                    "display": "inline-block",
                    "marginRight": "10px"
                }),
                html.Span(f"{percentual}%", style={"fontSize": "12px"})
            ], style={"textAlign": "left"})
        ]))
    
    return html.Div([
        html.H4("📈 Estatísticas de Preenchimento", style={"marginBottom": "15px"}),
        html.Table([
            html.Thead([
                html.Tr([
                    html.Th("Campo"),
                    html.Th("Preenchidos", style={"textAlign": "center"}),
                    html.Th("Percentual", style={"textAlign": "center"})
                ])
            ]),
            html.Tbody(stats_rows)
        ], className="stats-table", style={
            "width": "100%",
            "borderCollapse": "collapse",
            "marginBottom": "25px"
        })
    ])

def create_category_summary(categorias_info: Dict):
    """Cria resumo por categoria"""
    if not categorias_info:
        return html.Div()
    
    categoria_icons = {
        'processo': '📄',
        'vitima': '👤', 
        'reu': '⚖️',
        'provas': '📁'
    }
    
    categoria_names = {
        'processo': 'Processo',
        'vitima': 'Vítima',
        'reu': 'Réu', 
        'provas': 'Provas'
    }
    
    cards = []
    for categoria, info in categorias_info.items():
        icon = categoria_icons.get(categoria, '📊')
        name = categoria_names.get(categoria, categoria.title())
        total = info.get('total_respostas', 0)
        
        cards.append(create_info_card(
            f"{icon} {name}",
            f"{total} resposta(s)"
        ))
    
    return html.Div([
        html.H4("📈 Respostas por Categoria", style={"marginBottom": "15px"}),
        html.Div(cards, style={
            "display": "grid",
            "gridTemplateColumns": "repeat(auto-fit, minmax(150px, 1fr))",
            "gap": "10px",
            "marginBottom": "25px"
        })
    ])

def create_category_data_preview(all_data: Dict[str, pd.DataFrame]):
    """Cria preview dos dados por categoria"""
    if not all_data:
        return html.Div()
    
    previews = []
    
    for categoria, df in all_data.items():
        if df.empty:
            continue
        
        # Definir colunas específicas para cada categoria
        if categoria == 'processo':
            preview_cols = [
                'form_origem',
                'P0Q0. Pesquisador responsável pelo preenchimento:',
                'P0Q1. Número de controle (dado pela equipe)',
                'P0Q1A. Número de controle para casos em que há mais de uma vítima:',
                'P0Q2. Número do Processo:',
                'P0Q3. Estado em que ocorreu o crime (Formato: Unidade Federativa em letra maiúscula como SP, MG)',
                'P0Q14. Número de réus no processo:',
                'P0Q014. Número de réus que tiveram decisão com trânsito em julgado neste processo', 
                'P0Q18. Qual o número de vítimas no processo?'
            ]
        elif categoria == 'vitima':
            preview_cols = [
                'form_origem',
                'P0Q0. Pesquisador responsável pelo preenchimento:',
                'P0Q1. Número de controle (dado pela equipe)',
                'P0Q2. Número do Processo (Formato: 0000000-00.0000.0.00.0000):'
            ]
        elif categoria == 'reu':
            preview_cols = [
                'form_origem',
                'P0Q0. Pesquisador responsável pelo preenchimento:',
                'P0Q1. Número de controle (dado pela equipe)',
                'P0Q2. Número do Processo (Formato: 0000000-00.0000.0.00.0000):'
            ]
        elif categoria == 'provas':
            preview_cols = [
                'form_origem',
                'P0Q0. Pesquisador responsável pelo preenchimento:',
                'P0Q1. Número de controle (dado pela equipe)',
                'P0Q2. Número do Processo (Formato: 0000000-00.0000.0.00.0000):'
            ]
        else:
            # Lógica anterior para outras categorias não especificadas
            preview_cols = []
            important_keywords = ['processo', 'numero', 'nome', 'tribunal', 'data']
            
            # Primeiro, colunas com palavras-chave importantes
            for keyword in important_keywords:
                matching_cols = [col for col in df.columns if keyword.lower() in col.lower()]
                preview_cols.extend(matching_cols[:1])  # Máximo 1 por palavra-chave
                
            # Depois, outras colunas até completar 5
            remaining_cols = [col for col in df.columns if col not in preview_cols]
            preview_cols.extend(remaining_cols[:5-len(preview_cols)])
            
            # Limitar a 5 colunas para outras categorias
            preview_cols = preview_cols[:5]
        
        # Filtrar apenas colunas que existem no DataFrame
        preview_cols = [col for col in preview_cols if col in df.columns]
        
        if preview_cols:
            df_preview = df[preview_cols].head(12)
            
            previews.append(html.Div([
                html.H5(f"Formulário de {categoria.title()}", style={"marginBottom": "10px"}),
                dash_table.DataTable(
                    data=df_preview.to_dict('records'),
                    columns=[{"name": col[:30] + "..." if len(col) > 30 else col, "id": col} for col in df_preview.columns],
                    style_cell={
                        'textAlign': 'left',
                        'padding': '8px',
                        'fontFamily': 'Arial, sans-serif',
                        'fontSize': '11px',
                        'maxWidth': '150px',
                        'overflow': 'hidden',
                        'textOverflow': 'ellipsis'
                    },
                    style_header={
                        'backgroundColor': '#f8f9fa',
                        'fontWeight': 'bold',
                        'border': '1px solid #dee2e6'
                    },
                    style_data={
                        'backgroundColor': 'white',
                        'border': '1px solid #dee2e6'
                    },
                    style_table={'overflowX': 'auto'}
                )
            ], style={"marginBottom": "20px"}))
    
    if previews:
        return html.Div([
            html.H4("📄 Preview das Respostas", style={"marginBottom": "15px"}),
            html.Div(previews)
        ])
    
    return html.Div()

def create_observacoes_bolsista(all_data: Dict[str, pd.DataFrame]):
    """Cria seção com observações do bolsista do formulário de processo"""
    if not all_data or 'processo' not in all_data or all_data['processo'].empty:
        return html.Div()
    
    df_processo = all_data['processo']
    
    # Colunas que queremos mostrar
    colunas_observacoes = [
        'id',
        'P0Q1. Número de controle (dado pela equipe)',
        'P9Q3. Este processo, por qualquer motivo, se destacou/diferenciou das demais?( *humilhação, ofensa, julgamento moral, diligência na produção de provas, relato de violência detalhado etc_ .) Se sim, por que este caso se destacou/diferenciou das demais?'
    ]
    
    # Filtrar apenas colunas que existem no DataFrame
    colunas_existentes = [col for col in colunas_observacoes if col in df_processo.columns]
    
    if not colunas_existentes:
        return html.Div()
    
    # Criar DataFrame com as colunas selecionadas
    df_observacoes = df_processo[colunas_existentes].copy()
    
    # Renomear colunas para display mais limpo
    rename_map = {
        'P0Q1. Número de controle (dado pela equipe)': 'Nº Controle',
        'P9Q3. Este processo, por qualquer motivo, se destacou/diferenciou das demais?( *humilhação, ofensa, julgamento moral, diligência na produção de provas, relato de violência detalhado etc_ .) Se sim, por que este caso se destacou/diferenciou das demais?': 'Observações do Bolsista'
    }
    
    df_observacoes = df_observacoes.rename(columns=rename_map)
    
    # Filtrar apenas linhas onde há observações (não vazias)
    col_observacoes = 'Observações do Bolsista'
    if col_observacoes in df_observacoes.columns:
        # Remover linhas onde observações estão vazias ou são apenas espaços
        mask = df_observacoes[col_observacoes].notna() & (df_observacoes[col_observacoes].astype(str).str.strip() != '')
        df_observacoes = df_observacoes[mask]
    
    # Se não há observações, não mostrar a seção
    if df_observacoes.empty:
        return html.Div()
    
    return html.Div([
        html.Hr(style={"margin": "30px 0", "borderColor": "#dee2e6"}),
        html.H4("💭 Observações do Bolsista", style={"marginBottom": "15px", "color": "#495057"}),
        html.P("Coisas que se destacaram ou diferenciaram segundo os bolsistas, incluindo comentários de erro:", 
               style={"marginBottom": "15px", "color": "#6c757d", "fontStyle": "italic"}),
        dash_table.DataTable(
            data=df_observacoes.to_dict('records'),
            columns=[col for col in [
                {"name": "ID", "id": "id", "type": "text"} if "id" in df_observacoes.columns else None,
                {"name": "Nº Controle", "id": "Nº Controle", "type": "text"} if "Nº Controle" in df_observacoes.columns else None,
                {"name": "Observações", "id": "Observações do Bolsista", "type": "text"} if "Observações do Bolsista" in df_observacoes.columns else None
            ] if col is not None],
            style_cell={
                'textAlign': 'left',
                'padding': '12px',
                'fontFamily': 'Arial, sans-serif',
                'fontSize': '12px',
                'whiteSpace': 'normal',
                'height': 'auto',
                'lineHeight': '1.4'
            },
            style_cell_conditional=[
                {
                    'if': {'column_id': 'id'},
                    'width': '80px',
                    'textAlign': 'center'
                },
                {
                    'if': {'column_id': 'Nº Controle'},
                    'width': '120px',
                    'textAlign': 'center'
                },
                {
                    'if': {'column_id': 'Observações do Bolsista'},
                    'width': '70%',
                    'maxWidth': '500px'
                }
            ],
            style_header={
                'backgroundColor': '#f8f9fa',
                'fontWeight': 'bold',
                'border': '1px solid #dee2e6',
                'textAlign': 'center'
            },
            style_data={
                'backgroundColor': 'white',
                'border': '1px solid #dee2e6',
                'whiteSpace': 'normal',
                'height': 'auto'
            },
            style_table={
                'overflowX': 'auto',
                'marginBottom': '20px'
            },
            tooltip_data=[
                {
                    column: {'value': str(row[column]), 'type': 'markdown'}
                    for column in df_observacoes.columns
                } for row in df_observacoes.to_dict('records')
            ],
            tooltip_duration=None,
            css=[{
                'selector': '.dash-table-tooltip',
                'rule': 'background-color: #f8f9fa; font-family: Arial; border: 1px solid #dee2e6; max-width: 400px;'
            }]
        )
    ], style={"marginTop": "25px"})

def create_no_data_found():
    """Cria componente quando nenhum dado é encontrado"""
    return html.Div([
        html.I(className="fas fa-exclamation-triangle", 
               style={"fontSize": "48px", "color": "#ffc107"}),
        html.H4("Nenhum dado encontrado", style={"color": "#666", "marginTop": "15px"}),
        html.P("Não foram encontradas respostas para o número de processo informado.", 
               style={"color": "#999"})
    ], style={
        "textAlign": "center",
        "padding": "60px 20px",
        "backgroundColor": "#fff3cd",
        "borderRadius": "8px",
        "border": "1px solid #ffeeba"
    })

def format_date(date_value):
    """Formata data para exibição"""
    if not date_value:
        return "N/A"
    
    try:
        if hasattr(date_value, 'strftime'):
            return date_value.strftime("%d/%m/%Y %H:%M")
        else:
            return str(date_value)
    except:
        return "N/A"

def get_processo_numero(all_data: Dict[str, pd.DataFrame]) -> str:
    """Extrai o número do processo do df_processo"""
    if 'processo' not in all_data or all_data['processo'].empty:
        return 'N/A'
    
    df_processo = all_data['processo']
    coluna_processo = 'P0Q2. Número do Processo:'
    
    if coluna_processo in df_processo.columns:
        # Pegar o primeiro valor não nulo
        valores_validos = df_processo[coluna_processo].dropna()
        if not valores_validos.empty:
            return str(valores_validos.iloc[0])
    
    return 'N/A'

def get_numero_controle(all_data: Dict[str, pd.DataFrame]) -> str:
    """Extrai o número de controle do df_processo"""
    if 'processo' not in all_data or all_data['processo'].empty:
        return 'N/A'
    
    df_processo = all_data['processo']
    coluna_controle = 'P0Q1. Número de controle (dado pela equipe)'
    
    if coluna_controle in df_processo.columns:
        # Pegar o primeiro valor não nulo
        valores_validos = df_processo[coluna_controle].dropna()
        if not valores_validos.empty:
            return str(valores_validos.iloc[0])
    
    return 'N/A'
