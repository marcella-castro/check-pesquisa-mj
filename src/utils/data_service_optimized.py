"""
Serviço para carregamento de dados em background - Versão Otimizada
"""

import threading
import time
from data.lime_api import LimeSurveyAPI
from utils.data_cache import DataCache
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed

class DataLoaderService:
    """Serviço para carregar dados dos formulários em background"""
    
    def __init__(self):
        self.cache = DataCache()
        self.lime_api = LimeSurveyAPI()
        self.loading_thread = None
        self.max_workers = 4  # Limite de workers paralelos
    
    def start_background_loading(self):
        """Inicia carregamento em background se necessário"""
        if self.cache.is_loading:
            print("📡 Carregamento já em andamento...")
            return
        
        if self.cache.is_cache_valid():
            print("✅ Cache válido, usando dados existentes")
            return
        
        print("🚀 Iniciando carregamento dos dados...")
        self.cache.set_loading(True)
        
        # Executar em thread separada para não bloquear a aplicação
        self.loading_thread = threading.Thread(target=self._load_all_data)
        self.loading_thread.daemon = True
        self.loading_thread.start()
    
    def _download_survey(self, survey_id: str, categoria: str) -> tuple:
        """Baixa dados de um survey específico"""
        try:
            df = self.lime_api.download_survey_data(survey_id)
            if not df.empty:
                print(f"✅ {categoria} - Survey {survey_id}: {len(df)} respostas")
                return categoria, survey_id, df
            return categoria, survey_id, pd.DataFrame()
        except Exception as e:
            print(f"❌ Erro ao baixar survey {survey_id}: {str(e)}")
            return categoria, survey_id, pd.DataFrame()
    
    def _load_all_data(self):
        """Carrega todos os dados dos formulários de forma paralela"""
        try:
            print("📡 Conectando à API do LimeSurvey...")
            
            if not self.lime_api.get_session_key():
                raise Exception("Falha na conexão com LimeSurvey")
            
            all_data = {
                'processo': [],
                'reu': [],
                'vitima': pd.DataFrame(),
                'provas': pd.DataFrame()
            }
            
            # Preparar lista de todos os surveys para download paralelo
            survey_tasks = []
            for categoria, survey_ids in self.lime_api.survey_ids.items():
                if isinstance(survey_ids, list):
                    for survey_id in survey_ids:
                        survey_tasks.append((survey_id, categoria))
                else:
                    survey_tasks.append((survey_ids, categoria))
            
            print(f"📥 Baixando {len(survey_tasks)} surveys em paralelo...")
            
            # Executar downloads em paralelo com número limitado de workers
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                futures = {
                    executor.submit(self._download_survey, survey_id, categoria): (survey_id, categoria)
                    for survey_id, categoria in survey_tasks
                }
                
                for future in as_completed(futures):
                    categoria, survey_id, df = future.result()
                    if not df.empty:
                        if categoria in ['processo', 'reu']:
                            all_data[categoria].append(df)
                        else:
                            all_data[categoria] = df
            
            # Concatenar resultados de processo e réu
            if all_data['processo']:
                all_data['processo'] = pd.concat(all_data['processo'], ignore_index=True)
                print(f"✅ Processo: {len(all_data['processo'])} respostas total")
            
            if all_data['reu']:
                all_data['reu'] = pd.concat(all_data['reu'], ignore_index=True)
                print(f"✅ Réu: {len(all_data['reu'])} respostas total")
            
            # Limpar listas vazias
            all_data = {k: v for k, v in all_data.items() if not (isinstance(v, list) and len(v) == 0)}
            
            # Armazenar no cache
            self.cache.set_data(all_data)
            self.cache.set_loading(False)
            
            total_respostas = sum(len(df) for df in all_data.values() if isinstance(df, pd.DataFrame))
            print(f"🎉 Carregamento concluído! Total: {total_respostas} respostas")
            
        except Exception as e:
            error_msg = f"Erro no carregamento: {str(e)}"
            print(f"❌ {error_msg}")
            self.cache.set_error(error_msg)
        finally:
            self.lime_api.release_session_key()
    
    def get_cached_data(self) -> dict:
        """Retorna dados do cache com informações de status"""
        return {
            'data': self.cache.get_data(),
            'is_loading': self.cache.is_loading,
            'last_update': self.cache.last_update,
            'error': self.cache.load_error,
            'is_valid': self.cache.is_cache_valid()
        }
    
    def force_reload(self):
        """Força recarregamento dos dados"""
        self.cache.clear_cache()
        self.start_background_loading()
    
    def filter_by_processo(self, processo_numero: str) -> dict:
        """
        Filtra dados pelo número do processo usando os nomes de colunas reais
        
        Args:
            processo_numero: Número do processo a filtrar
            
        Returns:
            Dicionário com dados filtrados por categoria
        """
        all_data = self.cache.get_data()
        
        if not all_data:
            return {}
        
        # Definir nomes das colunas de processo para cada categoria
        processo_columns = {
            'processo': 'P0Q2. Número do Processo:',
            'reu': 'P0Q2. Número do Processo (Formato: 0000000-00.0000.0.00.0000):',
            'vitima': 'P0Q2. Número do Processo (Formato: 0000000-00.0000.0.00.0000):',
            'provas': 'P0Q2. Número do Processo (Formato: 0000000-00.0000.0.00.0000):'
        }
        
        filtered_data = {}
        lista_processos = [processo_numero]  # Para usar com .isin()
        
        for categoria, df in all_data.items():
            if df.empty:
                continue
            
            col_processo = processo_columns.get(categoria)
            
            if col_processo and col_processo in df.columns:
                # Filtrar usando o mesmo método que você usa
                filtered_df = df[df[col_processo].isin(lista_processos)]
                
                if not filtered_df.empty:
                    filtered_data[categoria] = filtered_df
                    print(f"✅ {categoria}: {len(filtered_df)} respostas encontradas")
                else:
                    print(f"⚠️ {categoria}: Nenhuma resposta encontrada para processo {processo_numero}")
            else:
                # Se não encontrou a coluna específica, tentar busca genérica
                processo_cols = [col for col in df.columns if any(word in col.lower() for word in ['processo', 'número', 'numero'])]
                
                if processo_cols:
                    col_found = processo_cols[0]
                    filtered_df = df[df[col_found].astype(str).str.contains(str(processo_numero), na=False, case=False)]
                    
                    if not filtered_df.empty:
                        filtered_data[categoria] = filtered_df
                        print(f"✅ {categoria}: {len(filtered_df)} respostas encontradas (busca genérica)")
        
        return filtered_data

# Instância global do serviço
data_service = DataLoaderService()