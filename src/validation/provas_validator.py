"""
Validador para dados de provas
"""

import pandas as pd
import re
from typing import List, Dict, Any

class ProvasValidator:
    def __init__(self):
        # Padrões de validação
        self.padrao_controle = re.compile(r'^\d{1,4}$')
        self.padrao_processo = re.compile(r'^\d{7}-\d{2}\.\d{4}\.\d{1}\.\d{2}\.\d{4}$')
    
    def validate(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Valida dados de provas
        
        Args:
            df: DataFrame com dados de provas
            
        Returns:
            Lista de erros encontrados em formato de dicionário
        """
        erros = []
        
        # P0Q1 - Validar número de controle
        erros.extend(self._validate_numero_controle(df))
        
        
        # Validações específicas de provas
        erros.extend(self._validate_campos_obrigatorios(df))
        
        return erros
    
    def _validate_numero_controle(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        P0Q1. Número de controle (dado pela equipe) - Teste por padrão de resposta
        Padrão esperado: até 4 dígitos + R/V + 0 + 1 dígito (ex: 123R01, 1V09)
        """
        erros = []
        coluna_controle = 'P0Q1. Número de controle (dado pela equipe)'
        
        if coluna_controle not in df.columns:
            return erros
        
        # Filtrar linhas com erro
        linhas_com_erro = df[~df[coluna_controle].astype(str).str.match(self.padrao_controle, na=False)]
        
        # Criar o log dos erros
        for _, row in linhas_com_erro.iterrows():
            erro = {
                'Formulário': f"Provas {row.get('form_origem', 'N/A')}",
                'ID da Resposta': row.get('id', 'N/A'),
                'Nº Processo': row.get('P0Q2. Número do Processo (Formato: 0000000-00.0000.0.00.0000):', 'N/A'),
                'Nº de Controle': row.get(coluna_controle, 'N/A'),
                'Bolsista': row.get('P0Q0. Pesquisador responsável pelo preenchimento:', 'Desconhecido'),
                'Campo': coluna_controle,
                'Tipo de Erro': 'Formato Inválido',
                'Valor Encontrado': row.get(coluna_controle, 'N/A'),
                'Regra Violada / Esperado': 'Padrão: até 4 dígitos + [R/V] + 0 + 1 dígito (ex: 123R01, 45V09)',
                'Categoria': 'provas'
            }
            erros.append(erro)
        
        return erros
    
    
    def _validate_campos_obrigatorios(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Valida campos obrigatórios básicos
        """
        erros = []
        
        campos_obrigatorios = [
            'P0Q0. Pesquisador responsável pelo preenchimento:',
            'P0Q1. Número de controle (dado pela equipe)',
            'P0Q2. Número do Processo (Formato: 0000000-00.0000.0.00.0000):'
        ]
        
        for campo in campos_obrigatorios:
            if campo not in df.columns:
                continue
                
            # Verificar campos vazios ou nulos
            linhas_vazias = df[df[campo].isna() | (df[campo].astype(str).str.strip() == '')]
            
            for _, row in linhas_vazias.iterrows():
                erro = {
                    'Formulário': f"Provas {row.get('form_origem', 'N/A')}",
                    'ID da Resposta': row.get('id', 'N/A'),
                    'Nº Processo': row.get('P0Q2. Número do Processo (Formato: 0000000-00.0000.0.00.0000):', 'N/A'),
                    'Nº de Controle': row.get('P0Q1. Número de controle (dado pela equipe)', 'N/A'),
                    'Bolsista': row.get('P0Q0. Pesquisador responsável pelo preenchimento:', 'Desconhecido'),
                    'Campo': campo,
                    'Tipo de Erro': 'Campo Obrigatório Vazio',
                    'Valor Encontrado': 'Vazio/Nulo',
                    'Regra Violada / Esperado': 'Campo deve ser preenchido',
                    'Categoria': 'provas'
                }
                erros.append(erro)
        
        return erros
    
