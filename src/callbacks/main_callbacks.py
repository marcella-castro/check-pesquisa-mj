"""
Callbacks principais da aplicação
"""

from dash import Input, Output, State, html, callback_context
import pandas as pd
from data.data_processor import DataProcessor
from validation.conjunto_validator import ConjuntoValidator
from components.process_summary import create_process_summary
from components.error_report import create_error_report
from utils.formatters import formatar_cnj
from datetime import datetime, timedelta
from utils.data_service_optimized import data_service

def register_callbacks(app):
    """
    Registra todos os callbacks da aplicação
    
    Args:
        app: Instância da aplicação Dash
    """
    
    @app.callback(
        [Output('search-results', 'children'),
         Output('loading-indicator', 'style')],
        [Input('btn-buscar', 'n_clicks')],
        [State('input-processo-numero', 'value')]
    )
    def handle_search(n_clicks, processo_numero):
        """
        Callback principal para busca e validação de processo
        
        Args:
            n_clicks: Número de cliques no botão
            processo_numero: Número do processo digitado
            
        Returns:
            Tuple com resultados da busca e estilo do loading
        """
        # Se não houve clique, retornar estado inicial
        if n_clicks == 0:
            return create_initial_state(), {"display": "none"}
        
        # Validar entrada
        if not processo_numero or not processo_numero.strip():
            return create_error_message("Por favor, digite um número de processo válido."), {"display": "none"}
        
        try:
            # Mostrar loading
            loading_style = {"display": "block"}
            
            # Processar dados
            data_processor = DataProcessor()
            all_data = data_processor.get_processo_data(processo_numero.strip())
            
            # Se não encontrou dados
            if not all_data:
                return create_no_data_message(processo_numero), {"display": "none"}
            
            # Obter resumo do processo
            processo_summary = data_processor.get_processo_summary(all_data)
            
            # Executar validações
            validator = ConjuntoValidator()
            erros = validator.validate_all(all_data)
            validation_summary = validator.get_validation_summary(erros)
            
            # Criar componentes de resultado
            results = create_search_results(
                processo_summary, 
                all_data, 
                erros, 
                validation_summary
            )
            
            return results, {"display": "none"}
            
        except Exception as e:
            error_msg = f"Erro ao processar dados: {str(e)}"
            return create_error_message(error_msg), {"display": "none"}
    
    @app.callback(
        Output('loading-indicator', 'style', allow_duplicate=True),
        [Input('btn-buscar', 'n_clicks')],
        prevent_initial_call=True
    )
    def show_loading(n_clicks):
        """
        Callback para mostrar indicador de loading
        """
        if n_clicks > 0:
            return {"display": "block"}
        return {"display": "none"}
    
    @app.callback(
        Output('data-status', 'children'),
        [Input('status-interval', 'n_intervals')]
    )
    def update_data_status(n_intervals):
        """
        Callback para atualizar o status do carregamento dos dados
        
        Args:
            n_intervals: Número de intervalos passados
            
        Returns:
            Componente com status dos dados
        """
        try:
            data_processor = DataProcessor()
            status = data_processor.get_cache_status()

            # Se o cache expirou e não está carregando, iniciar reload em background
            if not status.get('is_valid') and not status.get('is_loading'):
                try:
                    data_service.start_background_loading()
                    # Refletir novo estado imediatamente
                    status['is_loading'] = True
                except Exception as e:
                    # Se falhar ao iniciar reload, registrar e mostrar erro no status
                    return create_data_status_error(f"Falha ao iniciar recarregamento: {e}")

            return create_data_status_component(status)
            
        except Exception as e:
            return create_data_status_error(str(e))
    
    @app.callback(
        Output('input-processo-numero', 'value'),
        [Input('input-processo-numero', 'value')],
        prevent_initial_call=True
    )
    def format_cnj_input(value):
        """
        Callback para formatar automaticamente o número CNJ conforme o usuário digita
        
        Args:
            value: Valor atual do input
            
        Returns:
            Valor formatado segundo o padrão CNJ
        """
        if not value:
            return value
        
        try:
            # Aplicar formatação CNJ
            formatted_value = formatar_cnj(value)
            
            # Só retorna se o valor formatado for diferente do original
            # Isso evita loops infinitos
            if formatted_value != value:
                return formatted_value
            return value
        except Exception:
            # Se der erro na formatação, retorna o valor original
            return value

def create_search_results(processo_summary, all_data, erros, validation_summary):
    """
    Cria os componentes de resultado da busca
    
    Args:
        processo_summary: Resumo dos dados do processo
        all_data: Dicionário com DataFrames por categoria
        erros: Dicionário com erros encontrados
        validation_summary: Resumo das validações
        
    Returns:
        Componentes Dash com resultados
    """
    return html.Div([
        # Resumo do processo
        create_process_summary(processo_summary, all_data),
        
        html.Hr(style={"margin": "30px 0"}),
        
        # Relatório de erros
        create_error_report(erros, validation_summary),
        
        html.Hr(style={"margin": "30px 0"}),
        
        # Ações adicionais
        create_action_buttons(processo_summary.get('processo_numero', ''))
        
    ], style={"marginTop": "20px"})

def create_action_buttons(processo_numero):
    """Cria botões de ação adicionais"""
    return html.Div([
        html.H4("🔧 Ações", style={"marginBottom": "15px"}),
        html.Div([
            html.Button([
                html.I(className="fas fa-download", style={"marginRight": "8px"}),
                "Baixar Relatório"
            ], 
            id="btn-download",
            className="btn-secondary",
            style={
                "padding": "10px 20px",
                "marginRight": "10px",
                "backgroundColor": "#6c757d",
                "color": "white",
                "border": "none",
                "borderRadius": "5px",
                "cursor": "pointer"
            }),
            
            html.Button([
                html.I(className="fas fa-sync", style={"marginRight": "8px"}),
                "Atualizar Dados"
            ], 
            id="btn-refresh",
            className="btn-info",
            style={
                "padding": "10px 20px",
                "backgroundColor": "#17a2b8",
                "color": "white",
                "border": "none",
                "borderRadius": "5px",
                "cursor": "pointer"
            })
        ])
    ], style={
        "backgroundColor": "#f8f9fa",
        "padding": "20px",
        "borderRadius": "8px",
        "border": "1px solid #e9ecef"
    })

def create_initial_state():
    """Cria o estado inicial da página"""
    return html.Div([
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

def create_error_message(message):
    """Cria mensagem de erro"""
    return html.Div([
        html.I(className="fas fa-exclamation-triangle", 
               style={"fontSize": "48px", "color": "#dc3545"}),
        html.H4("Erro", style={"color": "#dc3545", "marginTop": "15px"}),
        html.P(message, style={"color": "#666"})
    ], style={
        "textAlign": "center",
        "padding": "60px 20px",
        "backgroundColor": "#f8d7da",
        "borderRadius": "8px",
        "border": "1px solid #f5c6cb"
    })

def create_no_data_message(processo_numero):
    """Cria mensagem quando não encontra dados"""
    return html.Div([
        html.I(className="fas fa-folder-open", 
               style={"fontSize": "48px", "color": "#ffc107"}),
        html.H4("Nenhum dado encontrado", style={"color": "#856404", "marginTop": "15px"}),
        html.P(f"Não foram encontradas respostas para o processo: {processo_numero}", 
               style={"color": "#666"}),
        html.P("Verifique se o número está correto ou se existem dados cadastrados para este processo.", 
               style={"color": "#999", "fontSize": "14px"})
    ], style={
        "textAlign": "center",
        "padding": "60px 20px",
        "backgroundColor": "#fff3cd",
        "borderRadius": "8px",
        "border": "1px solid #ffeeba"
    })

def create_data_status_component(status):
    """
    Cria componente de status dos dados
    
    Args:
        status: Dicionário com informações de status
        
    Returns:
        Componente Dash com status
    """
    if status.get('error'):
        return create_data_status_error(status['error'])
    
    # Se temos dados e não está carregando, mostrar sucesso
    if status.get('has_data') and not status.get('is_loading'):
        return create_data_status_success(status)
    
    # Se está carregando, mostrar loading
    if status.get('is_loading'):
        return create_data_status_loading()
    
    # Se não tem dados mas o cache é válido, mostrar aguardando
    if status.get('is_valid'):
        return create_data_status_waiting()
    
    # Em outros casos, mostrar loading
    return create_data_status_loading()

def create_data_status_loading():
    """Cria status de carregamento"""
    return html.Div([
        html.Div([
            html.I(className="fas fa-spinner fa-spin", 
                   style={"fontSize": "18px", "marginRight": "10px", "color": "#007bff"}),
            html.Span("Carregando dados dos formulários...", 
                     style={"color": "#007bff", "fontWeight": "500"})
        ])
    ], style={
        "backgroundColor": "#d1ecf1",
        "color": "#0c5460",
        "padding": "15px 20px",
        "borderRadius": "5px",
        "border": "1px solid #bee5eb",
        "marginBottom": "20px",
        "textAlign": "center"
    })

def create_data_status_success(status):
    """Cria status de sucesso"""
    categorias_text = []
    for categoria, count in status.get('categorias', {}).items():
        if count > 0:  # Só mostrar categorias com dados
            categorias_text.append(f"{categoria.title()}: {count}")
    
    last_update = status.get('last_update')
    next_update = None
    
    if last_update:
        try:
            # Converter para datetime se for string
            if isinstance(last_update, str):
                last_update = datetime.fromisoformat(last_update.replace('Z', '+00:00'))
            
            # Calcular próxima atualização (12 horas depois)
            next_update = last_update + timedelta(hours=12)
            
            # Formatar textos de atualização
            update_text = f"Última atualização: {last_update.strftime('%H:%M:%S')}"
            next_update_text = f"Próxima atualização: {next_update.strftime('%H:%M:%S')}"
        except Exception:
            update_text = f"Última atualização: {last_update}"
            next_update_text = "Próxima atualização: em 12 horas"
    
    return html.Div([
        html.Div([
            # Ícone e título
            html.I(className="fas fa-check-circle", 
                   style={"fontSize": "24px", "marginRight": "10px", "color": "#28a745"}),
            html.Span(f"Dados carregados com sucesso!", 
                     style={"color": "#155724", "fontWeight": "bold", "fontSize": "18px"}),
            
            # Informações principais
            html.Div([
                html.Span(f"Total: {status.get('total_respostas', 0)} respostas", 
                         style={"fontWeight": "500"}),
                html.Br(),
                html.Span(update_text),
                html.Br(),
                html.Span(next_update_text, style={"color": "#666"})
            ], style={"marginTop": "10px"}),
            
            # Detalhes por categoria
            html.Div(
                [html.Span(text, style={"marginRight": "15px"}) for text in categorias_text],
                style={"marginTop": "5px", "color": "#6c757d", "fontSize": "14px"}
            )
        ])
    ], style={
        "backgroundColor": "#d4edda",
        "color": "#155724",
        "padding": "15px 20px",
        "borderRadius": "5px",
        "border": "1px solid #c3e6cb",
        "marginBottom": "20px",
        "textAlign": "center"
    })

def create_data_status_error(error_msg):
    """Cria status de erro"""
    return html.Div([
        html.Div([
            html.I(className="fas fa-exclamation-triangle", 
                   style={"fontSize": "18px", "marginRight": "10px", "color": "#dc3545"}),
            html.Span(f"Erro ao carregar dados: {error_msg}", 
                     style={"color": "#721c24", "fontWeight": "500"})
        ])
    ], style={
        "backgroundColor": "#f8d7da",
        "color": "#721c24",
        "padding": "15px 20px",
        "borderRadius": "5px",
        "border": "1px solid #f5c6cb",
        "marginBottom": "20px",
        "textAlign": "center"
    })

def create_data_status_waiting():
    """Cria status de aguardando"""
    return html.Div([
        html.Div([
            html.I(className="fas fa-clock", 
                   style={"fontSize": "18px", "marginRight": "10px", "color": "#6c757d"}),
            html.Span("Aguardando carregamento dos dados...", 
                     style={"color": "#6c757d", "fontWeight": "500"})
        ])
    ], style={
        "backgroundColor": "#e2e3e5",
        "color": "#383d41",
        "padding": "15px 20px",
        "borderRadius": "5px",
        "border": "1px solid #d6d8db",
        "marginBottom": "20px",
        "textAlign": "center"
    })
