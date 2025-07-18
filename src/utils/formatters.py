"""
Formatadores e utilitários para exibição de dados
"""

import pandas as pd
import re
from typing import Any, Dict, List
from datetime import datetime

def formatar_cnj(numero):
    """
    Formata um número para o padrão CNJ
    
    Args:
        numero: Número a ser formatado (string ou int)
        
    Returns:
        Número formatado no padrão CNJ: 0000000-00.0000.0.00.0000
    """
    if not numero:
        return numero
        
    # Remove quaisquer caracteres não numéricos
    num = re.sub(r'\D', '', str(numero))
    
    # Se tem menos de 7 dígitos, não formata ainda
    if len(num) < 7:
        return num
    
    # Se o número tiver mais de 20 dígitos, remove o último dígito até ficar com 20
    while len(num) > 20:
        num = num[:-1]

    # Se não tiver exatamente 20 dígitos após o ajuste, formata parcialmente
    if len(num) < 20:
        # Formatação parcial baseada no que está disponível
        if len(num) >= 7:
            formatted = f"{num[:7]}"
            if len(num) > 7:
                formatted += f"-{num[7:min(9, len(num))]}"
            if len(num) > 9:
                formatted += f".{num[9:min(13, len(num))]}"
            if len(num) > 13:
                formatted += f".{num[13:min(14, len(num))]}"
            if len(num) > 14:
                formatted += f".{num[14:min(16, len(num))]}"
            if len(num) > 16:
                formatted += f".{num[16:min(20, len(num))]}"
            return formatted
        return num

    # Formatar: 0000000-00.0000.0.00.0000
    return f"{num[:7]}-{num[7:9]}.{num[9:13]}.{num[13]}.{num[14:16]}.{num[16:20]}"

def format_date(date_value: Any) -> str:
    """
    Formata uma data para exibição
    
    Args:
        date_value: Valor da data (pode ser string, datetime, etc.)
        
    Returns:
        Data formatada como string
    """
    if pd.isna(date_value) or not date_value:
        return "N/A"
    
    try:
        if isinstance(date_value, str):
            # Tentar converter string para datetime
            date_obj = pd.to_datetime(date_value)
        elif hasattr(date_value, 'strftime'):
            date_obj = date_value
        else:
            return str(date_value)
        
        return date_obj.strftime("%d/%m/%Y às %H:%M")
    except:
        return str(date_value)

def format_number(number: Any, decimal_places: int = 0) -> str:
    """
    Formata um número para exibição
    
    Args:
        number: Número a ser formatado
        decimal_places: Número de casas decimais
        
    Returns:
        Número formatado como string
    """
    if pd.isna(number):
        return "N/A"
    
    try:
        if decimal_places == 0:
            return f"{int(number):,}".replace(",", ".")
        else:
            return f"{float(number):,.{decimal_places}f}".replace(",", ".")
    except:
        return str(number)

def format_percentage(value: float, decimal_places: int = 1) -> str:
    """
    Formata um valor como percentual
    
    Args:
        value: Valor entre 0 e 100
        decimal_places: Casas decimais
        
    Returns:
        Percentual formatado
    """
    if pd.isna(value):
        return "0%"
    
    try:
        return f"{value:.{decimal_places}f}%"
    except:
        return "0%"

def truncate_text(text: str, max_length: int = 50) -> str:
    """
    Trunca texto longo para exibição
    
    Args:
        text: Texto a ser truncado
        max_length: Comprimento máximo
        
    Returns:
        Texto truncado
    """
    if not text or pd.isna(text):
        return ""
    
    text_str = str(text).strip()
    if len(text_str) <= max_length:
        return text_str
    
    return text_str[:max_length-3] + "..."

def format_list(items: List[str], separator: str = ", ") -> str:
    """
    Formata uma lista de itens para exibição
    
    Args:
        items: Lista de itens
        separator: Separador entre itens
        
    Returns:
        String com itens formatados
    """
    if not items:
        return "Nenhum"
    
    # Remover itens vazios ou nulos
    clean_items = [str(item).strip() for item in items if item and not pd.isna(item)]
    
    if not clean_items:
        return "Nenhum"
    
    return separator.join(clean_items)

def format_tribunal(tribunal: str) -> str:
    """
    Formata nome do tribunal para exibição
    
    Args:
        tribunal: Código ou nome do tribunal
        
    Returns:
        Nome formatado do tribunal
    """
    if not tribunal or pd.isna(tribunal):
        return "N/A"
    
    tribunal_upper = str(tribunal).upper().strip()
    
    # Mapeamento de códigos para nomes completos
    tribunais_map = {
        'STF': 'Supremo Tribunal Federal',
        'STJ': 'Superior Tribunal de Justiça',
        'TST': 'Tribunal Superior do Trabalho',
        'TSE': 'Tribunal Superior Eleitoral',
        'STM': 'Superior Tribunal Militar',
        'TRF1': 'Tribunal Regional Federal da 1ª Região',
        'TRF2': 'Tribunal Regional Federal da 2ª Região',
        'TRF3': 'Tribunal Regional Federal da 3ª Região',
        'TRF4': 'Tribunal Regional Federal da 4ª Região',
        'TRF5': 'Tribunal Regional Federal da 5ª Região',
        'TJSP': 'Tribunal de Justiça de São Paulo',
        'TJRJ': 'Tribunal de Justiça do Rio de Janeiro',
        'TJMG': 'Tribunal de Justiça de Minas Gerais',
        'TJRS': 'Tribunal de Justiça do Rio Grande do Sul',
        'TJPR': 'Tribunal de Justiça do Paraná',
        'TJSC': 'Tribunal de Justiça de Santa Catarina',
        'TJBA': 'Tribunal de Justiça da Bahia',
        'TJGO': 'Tribunal de Justiça de Goiás',
        'TJPE': 'Tribunal de Justiça de Pernambuco',
        'TJCE': 'Tribunal de Justiça do Ceará',
        'TJPA': 'Tribunal de Justiça do Pará',
        'TJMA': 'Tribunal de Justiça do Maranhão',
        'TJPB': 'Tribunal de Justiça da Paraíba',
        'TJES': 'Tribunal de Justiça do Espírito Santo',
        'TJPI': 'Tribunal de Justiça do Piauí',
        'TJAL': 'Tribunal de Justiça de Alagoas',
        'TJRN': 'Tribunal de Justiça do Rio Grande do Norte',
        'TJMT': 'Tribunal de Justiça de Mato Grosso',
        'TJMS': 'Tribunal de Justiça de Mato Grosso do Sul',
        'TJDF': 'Tribunal de Justiça do Distrito Federal',
        'TJRO': 'Tribunal de Justiça de Rondônia',
        'TJAC': 'Tribunal de Justiça do Acre',
        'TJAM': 'Tribunal de Justiça do Amazonas',
        'TJRR': 'Tribunal de Justiça de Roraima',
        'TJAP': 'Tribunal de Justiça do Amapá',
        'TJTO': 'Tribunal de Justiça do Tocantins',
        'TJSE': 'Tribunal de Justiça de Sergipe'
    }
    
    return tribunais_map.get(tribunal_upper, tribunal_upper)

def format_processo_numero(numero: str) -> str:
    """
    Formata número do processo para exibição
    
    Args:
        numero: Número do processo
        
    Returns:
        Número formatado
    """
    if not numero or pd.isna(numero):
        return "N/A"
    
    numero_str = str(numero).strip()
    
    # Se tem 20 dígitos, aplicar formatação CNJ
    digits_only = ''.join(filter(str.isdigit, numero_str))
    
    if len(digits_only) == 20:
        # Formato CNJ: NNNNNNN-DD.AAAA.J.TR.OOOO
        return f"{digits_only[:7]}-{digits_only[7:9]}.{digits_only[9:13]}.{digits_only[13:14]}.{digits_only[14:18]}.{digits_only[18:20]}"
    
    return numero_str

def clean_string(text: Any) -> str:
    """
    Limpa uma string removendo caracteres especiais e espaços extras
    
    Args:
        text: Texto a ser limpo
        
    Returns:
        Texto limpo
    """
    if pd.isna(text) or not text:
        return ""
    
    return str(text).strip().replace('\n', ' ').replace('\r', ' ')

def format_validation_severity(severity: str) -> Dict[str, str]:
    """
    Retorna formatação baseada na severidade
    
    Args:
        severity: Nível de severidade
        
    Returns:
        Dicionário com cor e ícone
    """
    severity_config = {
        'NENHUM': {'color': '#28a745', 'icon': 'fas fa-check-circle'},
        'BAIXA': {'color': '#28a745', 'icon': 'fas fa-info-circle'},
        'MÉDIA': {'color': '#ffc107', 'icon': 'fas fa-exclamation-triangle'},
        'ALTA': {'color': '#dc3545', 'icon': 'fas fa-exclamation-circle'}
    }
    
    return severity_config.get(severity, {
        'color': '#6c757d', 
        'icon': 'fas fa-question-circle'
    })
