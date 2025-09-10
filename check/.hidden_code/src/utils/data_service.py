"""
Serviço para carregamento de dados em background
"""

import threading
import time
from data.lime_api import LimeSurveyAPI
from utils.data_cache import DataCache
import pandas as pd

class DataLoaderService:
    """Serviço para carregar dados dos formulários em background"""
    
    def __init__(self):
        self.cache = DataCache()
        self.lime_api = LimeSurveyAPI()
        self.loading_thread = None
    
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
    
    def _load_all_data(self):
        """Carrega todos os dados dos formulários"""
        try:
            print("📡 Conectando à API do LimeSurvey...")
            
            if not self.lime_api.get_session_key():
                raise Exception("Falha na conexão com LimeSurvey")
            
            all_data = {}
            
            print("📥 Baixando dados de processo...")
            # Baixar dados de processo
            processo_dfs = []
            for survey_id in self.lime_api.survey_ids['processo']:
                print(f"  📋 Baixando survey {survey_id}...")
                df = self.lime_api.download_survey_data(survey_id)
                if not df.empty:
                    processo_dfs.append(df)
            
            if processo_dfs:
                all_data['processo'] = pd.concat(processo_dfs, ignore_index=True)
                print(f"✅ Processo: {len(all_data['processo'])} respostas")
            
            print("📥 Baixando dados de réu...")
            # Baixar dados de réu
            reu_dfs = []
            for survey_id in self.lime_api.survey_ids['reu']:
                print(f"  📋 Baixando survey {survey_id}...")
                df = self.lime_api.download_survey_data(survey_id)
                if not df.empty:
                    reu_dfs.append(df)
            
            if reu_dfs:
                all_data['reu'] = pd.concat(reu_dfs, ignore_index=True)
                print(f"✅ Réu: {len(all_data['reu'])} respostas")
            
            print("📥 Baixando dados de vítima...")
            # Baixar dados de vítima
            for survey_id in self.lime_api.survey_ids['vitima']:
                print(f"  📋 Baixando survey {survey_id}...")
                df = self.lime_api.download_survey_data(survey_id)
                if not df.empty:
                    all_data['vitima'] = df
                    print(f"✅ Vítima: {len(df)} respostas")
            
            print("📥 Baixando dados de provas...")
            # Baixar dados de provas
            for survey_id in self.lime_api.survey_ids['provas']:
                print(f"  📋 Baixando survey {survey_id}...")
                df = self.lime_api.download_survey_data(survey_id)
                if not df.empty:
                    all_data['provas'] = df
                    print(f"✅ Provas: {len(df)} respostas")
            
            # Armazenar no cache
            self.cache.set_data(all_data)
            self.cache.set_loading(False)
            
            total_respostas = sum(len(df) for df in all_data.values())
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
