"""
Módulo para processamento e limpeza dos dados
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from utils.data_service import data_service

class DataProcessor:
    def __init__(self):
        # Não precisa mais do lime_api, usa o data_service
        pass
    
    def get_processo_data(self, processo_numero: str) -> Dict[str, pd.DataFrame]:
        """
        Obtém todos os dados relacionados a um número de processo específico
        
        Args:
            processo_numero: Número do processo a ser pesquisado
            
        Returns:
            Dicionário com DataFrames por categoria (processo, vitima, reu, provas)
        """
        # Usar o serviço de dados para filtrar pelos dados em cache
        filtered_data = data_service.filter_by_processo(processo_numero)
        
        if not filtered_data:
            return {}
        
        # Limpar e processar os dados de cada categoria
        cleaned_data = {}
        for categoria, df in filtered_data.items():
            if not df.empty:
                cleaned_data[categoria] = self.clean_data(df)
        
        return cleaned_data
    
    def get_cache_status(self) -> Dict:
        """
        Retorna informações sobre o status do cache
        
        Returns:
            Dicionário com status do carregamento
        """
        cache_info = data_service.get_cached_data()
        
        total_respostas = 0
        categorias_info = {}
        
        if cache_info['data']:
            for categoria, df in cache_info['data'].items():
                count = len(df) if not df.empty else 0
                categorias_info[categoria] = count
                total_respostas += count
        
        return {
            'is_loading': cache_info['is_loading'],
            'last_update': cache_info['last_update'],
            'error': cache_info['error'],
            'is_valid': cache_info['is_valid'],
            'total_respostas': total_respostas,
            'categorias': categorias_info
        }
    
    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Limpa e processa os dados obtidos da API
        
        Args:
            df: DataFrame bruto da API
            
        Returns:
            DataFrame limpo e processado
        """
        if df.empty:
            return df
        
        df_clean = df.copy()
        
        # Remover respostas incompletas
        df_clean = df_clean[df_clean['lastpage'].notna()]
        
        # Converter tipos de dados
        df_clean = self._convert_data_types(df_clean)
        
        # Limpar campos de texto
        df_clean = self._clean_text_fields(df_clean)
        
        # Padronizar dados
        df_clean = self._standardize_data(df_clean)
        
        return df_clean
    
    def _convert_data_types(self, df: pd.DataFrame) -> pd.DataFrame:
        """Converte tipos de dados apropriados"""
        df_converted = df.copy()
        
        # Converter datas
        date_columns = ['submitdate', 'datestamp']
        for col in date_columns:
            if col in df_converted.columns:
                df_converted[col] = pd.to_datetime(df_converted[col], errors='coerce')
        
        # Converter números
        numeric_columns = ['processo_ano', 'vitima_idade', 'reu_idade']
        for col in numeric_columns:
            if col in df_converted.columns:
                df_converted[col] = pd.to_numeric(df_converted[col], errors='coerce')
        
        return df_converted
    
    def _clean_text_fields(self, df: pd.DataFrame) -> pd.DataFrame:
        """Limpa campos de texto"""
        df_clean = df.copy()
        
        text_columns = ['processo_numero', 'vitima_nome', 'reu_nome', 'tribunal']
        
        for col in text_columns:
            if col in df_clean.columns:
                # Remover espaços extras e converter para string
                df_clean[col] = df_clean[col].astype(str).str.strip()
                
                # Remover valores vazios/nulos
                df_clean[col] = df_clean[col].replace(['', 'nan', 'None'], np.nan)
        
        return df_clean
    
    def _standardize_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Padroniza formatos de dados"""
        df_std = df.copy()
        
        # Padronizar número do processo (remover caracteres especiais)
        if 'processo_numero' in df_std.columns:
            df_std['processo_numero'] = df_std['processo_numero'].str.replace(r'[^\d]', '', regex=True)
        
        # Padronizar tribunal (converter para maiúsculas)
        if 'tribunal' in df_std.columns:
            df_std['tribunal'] = df_std['tribunal'].str.upper()
        
        # Padronizar gênero
        gender_columns = ['vitima_genero', 'reu_genero']
        for col in gender_columns:
            if col in df_std.columns:
                df_std[col] = self._standardize_gender(df_std[col])
        
        return df_std
    
    def _standardize_gender(self, gender_series: pd.Series) -> pd.Series:
        """Padroniza valores de gênero"""
        gender_mapping = {
            'M': 'Masculino',
            'F': 'Feminino',
            'MASC': 'Masculino',
            'FEM': 'Feminino',
            'MASCULINO': 'Masculino',
            'FEMININO': 'Feminino'
        }
        
        return gender_series.str.upper().map(gender_mapping).fillna(gender_series)
    
    def get_processo_summary(self, all_data: Dict[str, pd.DataFrame]) -> Dict:
        """
        Gera um resumo dos dados do processo
        
        Args:
            all_data: Dicionário com DataFrames por categoria
            
        Returns:
            Dicionário com resumo dos dados
        """
        if not all_data:
            return {
                'total_respostas': 0,
                'processo_numero': '',
                'tribunal': '',
                'ultima_atualizacao': None,
                'categorias': {}
            }
        
        # Tentar encontrar número do processo
        processo_numero = ''
        tribunal = ''
        ultima_atualizacao = None
        
        # Procurar nos dados de processo primeiro
        if 'processo' in all_data and not all_data['processo'].empty:
            df_processo = all_data['processo']
            
            # Buscar coluna com número do processo
            processo_cols = [col for col in df_processo.columns if any(word in col.lower() for word in ['processo', 'número', 'numero'])]
            if processo_cols:
                processo_numero = str(df_processo[processo_cols[0]].iloc[0]) if not df_processo[processo_cols[0]].isna().all() else ''
            
            # Buscar coluna com tribunal
            tribunal_cols = [col for col in df_processo.columns if 'tribunal' in col.lower()]
            if tribunal_cols:
                tribunal = str(df_processo[tribunal_cols[0]].iloc[0]) if not df_processo[tribunal_cols[0]].isna().all() else ''
            
            # Buscar data de submissão
            if 'submitdate' in df_processo.columns:
                ultima_atualizacao = pd.to_datetime(df_processo['submitdate'], errors='coerce').max()
        
        # Contar respostas por categoria
        categorias_info = {}
        total_respostas = 0
        
        for categoria, df in all_data.items():
            if not df.empty:
                count = len(df)
                categorias_info[categoria] = {
                    'total_respostas': count,
                    'campos_preenchidos': self._get_filled_fields_stats(df)
                }
                total_respostas += count
        
        summary = {
            'total_respostas': total_respostas,
            'processo_numero': processo_numero,
            'tribunal': tribunal,
            'ultima_atualizacao': ultima_atualizacao,
            'categorias': categorias_info
        }
        
        return summary
    
    def _get_responses_by_date(self, df: pd.DataFrame) -> Dict:
        """Agrupa respostas por data de submissão"""
        if 'submitdate' not in df.columns:
            return {}
        
        df_date = df.copy()
        df_date['data'] = df_date['submitdate'].dt.date
        
        return df_date.groupby('data').size().to_dict()
    
    def _get_filled_fields_stats(self, df: pd.DataFrame) -> Dict:
        """Calcula estatísticas de campos preenchidos"""
        stats = {}
        
        for col in df.columns:
            if col not in ['id', 'submitdate', 'lastpage', 'startlanguage', 'datestamp']:
                total = len(df)
                filled = df[col].notna().sum()
                stats[col] = {
                    'total': total,
                    'preenchidos': filled,
                    'percentual': round((filled / total * 100), 2) if total > 0 else 0
                }
        
        return stats
