"""
Validador principal para processos da pesquisa MJ
"""

import pandas as pd
from typing import Dict, List, Tuple
from validation.processo_validator import ProcessoValidator
from validation.vitima_validator import VitimaValidator
from validation.reu_validator import ReuValidator
from validation.provas_validator import ProvasValidator

class ConjuntoValidator:
    def __init__(self):
        self.processo_validator = ProcessoValidator()
        self.vitima_validator = VitimaValidator()
        self.reu_validator = ReuValidator()
        self.provas_validator = ProvasValidator()
    
    def validate_all(self, all_data: Dict[str, pd.DataFrame]) -> Dict:
        """
        Executa todas as validações nos dados
        
        Args:
            all_data: Dicionário com DataFrames por categoria
            
        Returns:
            Dicionário com todos os erros encontrados
        """
        if not all_data:
            return {'erro': 'Nenhum dado encontrado para validação'}
        
        erros = {
            'processo': [],
            'vitima': [],
            'reu': [],
            'provas': [],
            'gerais': []
        }
        
        # Validações por categoria
        if 'processo' in all_data and not all_data['processo'].empty:
            try:
                erros_processo = self.processo_validator.validate(all_data['processo'])
                erros['processo'] = erros_processo
                print(f"✅ Processo: {len(erros_processo)} erros encontrados")
            except Exception as e:
                erros['gerais'].append(f"Erro na validação de processo: {str(e)}")
        
        if 'vitima' in all_data and not all_data['vitima'].empty:
            try:
                erros_vitima = self.vitima_validator.validate(all_data['vitima'])
                erros['vitima'] = erros_vitima
                print(f"✅ Vítima: {len(erros_vitima)} erros encontrados")
            except Exception as e:
                erros['gerais'].append(f"Erro na validação de vítima: {str(e)}")
        
        if 'reu' in all_data and not all_data['reu'].empty:
            try:
                erros_reu = self.reu_validator.validate(all_data['reu'])
                erros['reu'] = erros_reu
                print(f"✅ Réu: {len(erros_reu)} erros encontrados")
            except Exception as e:
                erros['gerais'].append(f"Erro na validação de réu: {str(e)}")
        
        if 'provas' in all_data and not all_data['provas'].empty:
            try:
                erros_provas = self.provas_validator.validate(all_data['provas'])
                erros['provas'] = erros_provas
                print(f"✅ Provas: {len(erros_provas)} erros encontrados")
            except Exception as e:
                erros['gerais'].append(f"Erro na validação de provas: {str(e)}")
        
        # Validações gerais entre categorias
        erros['gerais'].extend(self._validate_consistency(all_data))
        
        return erros
    
    def _validate_consistency(self, all_data: Dict[str, pd.DataFrame]) -> List[str]:
        """Validações de consistência entre diferentes seções"""
        erros = []
        
        # Verificar se existem respostas duplicadas dentro de cada categoria
        for categoria, df in all_data.items():
            if df.empty:
                continue
                
            if len(df) > 1:
                # Procurar coluna de processo para verificar duplicatas
                processo_cols = [col for col in df.columns if any(word in col.lower() for word in ['processo', 'número', 'numero'])]
                
                if processo_cols:
                    duplicates = df.duplicated(subset=[processo_cols[0]], keep=False)
                    if duplicates.any():
                        erros.append(f"Categoria {categoria}: Encontradas {duplicates.sum()} respostas duplicadas")
        
        # Verificar consistência temporal
        for categoria, df in all_data.items():
            if 'submitdate' in df.columns:
                dates = pd.to_datetime(df['submitdate'], errors='coerce')
                if dates.notna().any():
                    date_range = dates.max() - dates.min()
                    if date_range.days > 30:
                        erros.append(f"Categoria {categoria}: Respostas com diferença temporal de {date_range.days} dias")
        
        # Verificar se há dados em todas as categorias esperadas
        categorias_esperadas = ['processo', 'vitima', 'reu', 'provas']
        categorias_faltando = [cat for cat in categorias_esperadas if cat not in all_data or all_data[cat].empty]
        
        if categorias_faltando:
            erros.append(f"Categorias sem dados: {', '.join(categorias_faltando)}")
        
        return erros
    
    def get_validation_summary(self, erros: Dict) -> Dict:
        """
        Gera um resumo das validações
        
        Args:
            erros: Dicionário com erros por categoria
            
        Returns:
            Resumo das validações
        """
        # Contar erros considerando que agora são listas de dicionários
        total_erros = 0
        categorias_count = {}
        
        for categoria, lista_erros in erros.items():
            if categoria == 'gerais':
                # Erros gerais continuam sendo lista de strings
                count = len(lista_erros) if isinstance(lista_erros, list) else 0
            else:
                # Outros erros são listas de dicionários
                count = len(lista_erros) if isinstance(lista_erros, list) else 0
            
            categorias_count[categoria] = count
            total_erros += count
        
        summary = {
            'total_erros': total_erros,
            'categorias': categorias_count,
            'status': 'ERRO' if total_erros > 0 else 'OK',
            'severidade': self._calculate_severity_new(total_erros)
        }
        
        return summary
    
    def _calculate_severity_new(self, total_erros: int) -> str:
        """Calcula a severidade dos erros encontrados"""
        if total_erros == 0:
            return 'NENHUM'
        elif total_erros <= 2:
            return 'BAIXA'
        elif total_erros <= 10:
            return 'MÉDIA'
        else:
            return 'ALTA'
