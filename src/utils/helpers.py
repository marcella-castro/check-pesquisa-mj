"""
Funções auxiliares e utilitários gerais
"""

import pandas as pd
import re
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, timedelta

def is_valid_processo_numero(numero: str) -> bool:
    """
    Verifica se um número de processo é válido
    
    Args:
        numero: Número do processo
        
    Returns:
        True se válido, False caso contrário
    """
    if not numero:
        return False
    
    # Remover caracteres não numéricos
    digits_only = re.sub(r'[^\d]', '', str(numero))
    
    # Deve ter pelo menos 7 dígitos
    if len(digits_only) < 7:
        return False
    
    # Se tem 20 dígitos, validar formato CNJ
    if len(digits_only) == 20:
        return validate_cnj_number(digits_only)
    
    return True

def validate_cnj_number(numero: str) -> bool:
    """
    Valida número CNJ usando algoritmo de dígito verificador
    
    Args:
        numero: Número CNJ com 20 dígitos
        
    Returns:
        True se válido, False caso contrário
    """
    if len(numero) != 20:
        return False
    
    try:
        # Extrair partes
        sequencial = numero[:7]
        dv = numero[7:9]
        ano = numero[9:13]
        segmento = numero[13:14]
        tribunal = numero[14:18]
        origem = numero[18:20]
        
        # Calcular dígito verificador
        numero_sem_dv = sequencial + ano + segmento + tribunal + origem
        resto = int(numero_sem_dv) % 97
        dv_calculado = 98 - resto
        
        return int(dv) == dv_calculado
    except:
        return False

def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Limpa um DataFrame removendo dados inconsistentes
    
    Args:
        df: DataFrame a ser limpo
        
    Returns:
        DataFrame limpo
    """
    if df.empty:
        return df
    
    df_clean = df.copy()
    
    # Remover linhas completamente vazias
    df_clean = df_clean.dropna(how='all')
    
    # Limpar strings
    for col in df_clean.select_dtypes(include=['object']).columns:
        df_clean[col] = df_clean[col].astype(str)
        df_clean[col] = df_clean[col].str.strip()
        df_clean[col] = df_clean[col].replace(['', 'nan', 'None', 'null'], pd.NA)
    
    return df_clean

def get_age_from_birth_year(birth_year: int, reference_year: Optional[int] = None) -> int:
    """
    Calcula idade baseada no ano de nascimento
    
    Args:
        birth_year: Ano de nascimento
        reference_year: Ano de referência (padrão: ano atual)
        
    Returns:
        Idade calculada
    """
    if not reference_year:
        reference_year = datetime.now().year
    
    return reference_year - birth_year

def validate_age(age: Union[int, float, str]) -> bool:
    """
    Valida se uma idade é razoável
    
    Args:
        age: Idade a ser validada
        
    Returns:
        True se válida, False caso contrário
    """
    try:
        age_int = int(float(age))
        return 0 <= age_int <= 120
    except:
        return False

def extract_numbers_from_text(text: str) -> List[str]:
    """
    Extrai números de um texto
    
    Args:
        text: Texto de entrada
        
    Returns:
        Lista de números encontrados
    """
    if not text:
        return []
    
    return re.findall(r'\d+', str(text))

def is_valid_name(name: str) -> bool:
    """
    Valida se um nome é válido
    
    Args:
        name: Nome a ser validado
        
    Returns:
        True se válido, False caso contrário
    """
    if not name or pd.isna(name):
        return False
    
    name_str = str(name).strip()
    
    # Deve ter pelo menos 2 caracteres
    if len(name_str) < 2:
        return False
    
    # Deve conter apenas letras, espaços e hífens
    if not re.match(r'^[a-zA-ZÀ-ÿ\s\-\'\.]+$', name_str):
        return False
    
    return True

def calculate_data_quality_score(df: pd.DataFrame, required_fields: List[str]) -> Dict[str, float]:
    """
    Calcula pontuação de qualidade dos dados
    
    Args:
        df: DataFrame com os dados
        required_fields: Lista de campos obrigatórios
        
    Returns:
        Dicionário com métricas de qualidade
    """
    if df.empty:
        return {
            'completeness': 0.0,
            'consistency': 0.0,
            'overall_score': 0.0
        }
    
    total_fields = len(df.columns)
    total_rows = len(df)
    
    # Calcular completude
    filled_cells = df.notna().sum().sum()
    total_cells = total_fields * total_rows
    completeness = (filled_cells / total_cells * 100) if total_cells > 0 else 0
    
    # Calcular completude dos campos obrigatórios
    required_completeness = 100.0
    if required_fields:
        required_filled = 0
        required_total = 0
        
        for field in required_fields:
            if field in df.columns:
                required_filled += df[field].notna().sum()
                required_total += total_rows
        
        required_completeness = (required_filled / required_total * 100) if required_total > 0 else 0
    
    # Pontuação geral (média ponderada)
    overall_score = (completeness * 0.4 + required_completeness * 0.6)
    
    return {
        'completeness': round(completeness, 2),
        'required_completeness': round(required_completeness, 2),
        'overall_score': round(overall_score, 2)
    }

def get_duplicate_rows(df: pd.DataFrame, subset: Optional[List[str]] = None) -> pd.DataFrame:
    """
    Identifica linhas duplicadas no DataFrame
    
    Args:
        df: DataFrame a ser analisado
        subset: Colunas a considerar para duplicação
        
    Returns:
        DataFrame com apenas as linhas duplicadas
    """
    if df.empty:
        return df
    
    if subset:
        # Considerar apenas colunas que existem
        existing_subset = [col for col in subset if col in df.columns]
        if existing_subset:
            return df[df.duplicated(subset=existing_subset, keep=False)]
    
    return df[df.duplicated(keep=False)]

def format_error_message(error_type: str, field: str, value: Any, details: str = "") -> str:
    """
    Formata mensagem de erro padronizada
    
    Args:
        error_type: Tipo do erro
        field: Campo com erro
        value: Valor problemático
        details: Detalhes adicionais
        
    Returns:
        Mensagem de erro formatada
    """
    base_msg = f"{error_type} no campo '{field}'"
    
    if value is not None and not pd.isna(value):
        base_msg += f": {value}"
    
    if details:
        base_msg += f" ({details})"
    
    return base_msg

def get_missing_required_fields(df: pd.DataFrame, required_fields: List[str]) -> Dict[str, int]:
    """
    Identifica campos obrigatórios não preenchidos
    
    Args:
        df: DataFrame com os dados
        required_fields: Lista de campos obrigatórios
        
    Returns:
        Dicionário com campo e quantidade de valores ausentes
    """
    missing_data = {}
    
    for field in required_fields:
        if field in df.columns:
            missing_count = df[field].isna().sum()
            if missing_count > 0:
                missing_data[field] = missing_count
        else:
            missing_data[field] = len(df)  # Campo não existe
    
    return missing_data

def create_summary_statistics(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Cria estatísticas resumidas do DataFrame
    
    Args:
        df: DataFrame com os dados
        
    Returns:
        Dicionário com estatísticas
    """
    if df.empty:
        return {
            'total_rows': 0,
            'total_columns': 0,
            'missing_values': 0,
            'completeness_percentage': 0
        }
    
    total_rows = len(df)
    total_columns = len(df.columns)
    total_cells = total_rows * total_columns
    missing_values = df.isna().sum().sum()
    
    return {
        'total_rows': total_rows,
        'total_columns': total_columns,
        'total_cells': total_cells,
        'missing_values': missing_values,
        'filled_values': total_cells - missing_values,
        'completeness_percentage': round(((total_cells - missing_values) / total_cells * 100), 2) if total_cells > 0 else 0
    }
