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
        erros.extend(self._validate_provas_datas(df))
        
        return erros

    def _validate_provas_datas(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Valida datas relacionadas aos laudos periciais listados em P1Q0[SQ...].
        Se a prova estiver marcada como 'Sim', espera-se que as colunas de
        data de solicitação e data de juntada contenham dd/mm/aaaa ou 'NI'.
        """
        erros: List[Dict[str, Any]] = []

        perguntas_dict =  {
            'P1Q0[SQ001]': ('Exame em local de crime', 'P1Q1[SQ001_SQ002]', 'P1Q1[SQ001_SQ003]'),
            'P1Q0[SQ002]': ('Exame em arma de fogo', 'P1Q1[SQ002_SQ002]', 'P1Q1[SQ002_SQ003]'),
            'P1Q0[SQ003]': ('Exame em arma branca', 'P1Q1[SQ003_SQ002]', 'P1Q1[SQ003_SQ003]'),
            'P1Q0[SQ004]': ('Exame em documentos (ex.: grafotécnico)', 'P1Q1[SQ004_SQ002]', 'P1Q1[SQ004_SQ003]'),
            'P1Q0[57481]': ('Exame em poeiras, pós e cinzas', 'P1Q1[SQ005_SQ002]', 'P1Q1[SQ005_SQ003]'),
            'P1Q0[SQ005]': ('Exame em peças de vestuários, acessórios e pertences', 'P1Q1[SQ006_SQ002]', 'P1Q1[SQ006_SQ003]'),
            'P1Q0[SQ006]': ('Exame em outros tipos de vestígios físicos', 'P1Q1[SQ007_SQ002]', 'P1Q1[SQ007_SQ003]'),
            'P1Q0[SQ007]': ('Exame em computadores ou tablets', 'P1Q1[SQ008_SQ002]', 'P1Q1[SQ008_SQ003]'),
            'P1Q0[SQ008]': ('Exame em aparelhos celulares', 'P1Q1[SQ009_SQ002]', 'P1Q1[SQ009_SQ003]'),
            'P1Q0[SQ009]': ('Exame em arquivos de vídeo/imagens/áudio', 'P1Q1[SQ010_SQ002]', 'P1Q1[SQ010_SQ003]'),
            'P1Q0[SQ012]': ('Exame em outros tipos de dispositivos digitais', 'P1Q1[SQ011_SQ002]', 'P1Q1[SQ011_SQ003]' ),
            'P1Q0[SQ011]': ('Exame em marcas de mordidas ou impressões labiais', 'P1Q1[SQ012_SQ002]', 'P1Q1[SQ012_SQ003]'),
            'P1Q0[SQ010]': ('Exame em impressões papiloscópicas (impressão digital)', 'P1Q1[SQ013_SQ002]', 'P1Q1[SQ013_SQ003]'),
            'P1Q0[SQ013]': ('Exame em outros tipos de vestígios morfológicos', 'P1Q1[SQ014_SQ002]', 'P1Q1[SQ014_SQ003]'),
            'P1Q0[SQ014]': ('Exame de corpo de delito do acusado', 'P1Q1[SQ015_SQ002]', 'P1Q1[SQ015_SQ003]'),
            'P1Q0[SQ018]': ('Exame de corpo de delito da vítima', 'P1Q1[SQ016_SQ002]', 'P1Q1[SQ016_SQ003]'),
            'P1Q0[79893]': ('Exame toxicológico do acusado', 'P1Q1[SQ019_SQ002]', 'P1Q1[SQ019_SQ003]'),
            'P1Q0[SQ017]': ('Exame toxicológico da vítima','P1Q1[SQ018_SQ002]', 'P1Q1[SQ018_SQ003]'),
            'P1Q0[SQ016]': ('Exame em sangue (outros tipos)', 'P1Q1[SQ017_SQ002]', 'P1Q1[SQ017_SQ003]'),
            'P1Q0[SQ015]': ('Exame em sêmen', 'P1Q1[SQ020_SQ002]', 'P1Q1[SQ020_SQ003]'),
            'P1Q0[SQ019]': ('Exame em dentes','P1Q1[SQ024_SQ002]', 'P1Q1[SQ024_SQ003]'),
            'P1Q0[SQ023]': ('Exame psicológico/psiquiátrico do acusado', 'P1Q1[SQ023_SQ002]', 'P1Q1[SQ023_SQ003]'),
            'P1Q0[SQ022]': ('Exame psicológico/psiquiátrico da vítima','P1Q1[SQ022_SQ002]', 'P1Q1[SQ022_SQ003]'),
            'P1Q0[SQ021]': ('Exame em outros tipos de vestígios biológicos', 'P1Q1[SQ021_SQ002]', 'P1Q1[SQ021_SQ003]'),
            'P1Q0[66635]': ('Exame em drogas lícitas', 'P1Q1[SQ025_SQ002]', 'P1Q1[SQ025_SQ003]'),
            'P1Q0[SQ020]': ('Exame em drogas ilícitas', 'P1Q1[SQ028_SQ002]', 'P1Q1[SQ028_SQ003]'),
            'P1Q0[SQ024]': ('Exame em outros tipos de vestígios químicos (ex.: líquidos, combustíveis, bebidas, metais, etc)', 'P1Q1[SQ027_SQ002]', 'P1Q1[SQ027_SQ003]'),
            'P1Q0[SQ025]': ('Exame de necropsia', 'P1Q1[SQ026_SQ002]', 'P1Q1[SQ026_SQ003]'),
            'P1Q0[SQ026]': ('Exame em fragmentos veiculares', 'P1Q1[SQ029_SQ002]', 'P1Q1[SQ029_SQ003]'),
            'P1Q0[SQ027]': ('Exame em componentes veiculares', 'P1Q1[SQ030_SQ002]', 'P1Q1[SQ030_SQ003]')
        }

        padrao_data = re.compile(r'^\d{2}/\d{2}/\d{4}$')

        def valor_valido(valor):
            if pd.isna(valor):
                return False
            valor_str = str(valor).strip()
            return bool(padrao_data.match(valor_str)) or valor_str.upper() == "NI"

        for chave, valores in perguntas_dict.items():
            coluna_prova = chave
            prova = valores[0]
            coluna_data_solicitacao = valores[1]
            coluna_data_juntada = valores[2]

            # pular se as colunas não existirem
            if coluna_prova not in df.columns:
                continue
            if coluna_data_solicitacao not in df.columns or coluna_data_juntada not in df.columns:
                continue

            # Filtrar linhas com erro
            linhas_com_erro = df[
                (df[coluna_prova] == "Sim") &
                (
                    (~df[coluna_data_solicitacao].apply(valor_valido)) |
                    (~df[coluna_data_juntada].apply(valor_valido))
                )
            ]

            # Criar o log dos erros
            for _, row in linhas_com_erro.iterrows():
                erro = {
                    'Formulário': f"Provas {row.get('form_origem', 'N/A')}",
                    'ID da Resposta': row.get('id', 'N/A'),
                    'Nº Processo': row.get('P0Q2. Número do Processo (Formato: 0000000-00.0000.0.00.0000):', 'N/A'),
                    'Nº de Controle': row.get('P0Q1. Número de controle (dado pela equipe)', 'N/A'),
                    'Bolsista': row.get('P0Q0. Pesquisador responsável pelo preenchimento:', 'Desconhecido'),
                    'Campo': f"Tipo de prova: {prova} - {coluna_data_solicitacao} ou {coluna_data_juntada}",
                    'Tipo de Erro': f'Data inválida ou ausente para [{prova}]',
                    'Valor Encontrado': f"Valores de data para pergunta [{prova}]: {row.get(coluna_data_solicitacao)} / {row.get(coluna_data_juntada)}",
                    'Regra Violada / Esperado': 'Para provas marcadas presentes ("Sim"), espera-se data de juntada e solicitação ou NI',
                    'Categoria': 'provas'
                }
                erros.append(erro)

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
    
