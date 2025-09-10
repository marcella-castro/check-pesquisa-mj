"""
Módulo para conexão com a API do LimeSurvey
"""

import requests
import pandas as pd
import json
import base64
import re
from typing import Dict, List, Optional
from config.settings import Config

def limpar_html(texto):
    """Remove tags HTML do texto"""
    if pd.isna(texto):
        return texto
    texto = str(texto)
    texto = re.sub(r'<[^>]+>', '', texto)
    return texto.strip()

class LimeSurveyAPI:
    def __init__(self):
        self.api_url = Config.LIME_API_URL
        self.username = Config.LIME_USERNAME
        self.password = Config.LIME_PASSWORD
        self.session_key = None
        
        # IDs dos surveys conforme sua configuração
        self.survey_ids = Config.SURVEY_IDS
        
    def limesurvey_api_request(self, method: str, params: List, session_key: Optional[str] = None, id_: int = 1) -> Dict:
        """Faz requisição para a API do LimeSurvey"""
        headers = {'Content-Type': 'application/json'}
        payload = {'method': method, 'params': params, 'id': id_}
        
        if session_key:
            payload['params'].insert(0, session_key)
            
        try:
            response = requests.post(self.api_url, data=json.dumps(payload), headers=headers)
            return response.json()
        except Exception as e:
            print(f"Erro na requisição API: {e}")
            return {'error': str(e)}
        
    def get_session_key(self) -> Optional[str]:
        """Obtém a chave de sessão da API"""
        try:
            login_response = self.limesurvey_api_request('get_session_key', [self.username, self.password])
            session_key = login_response.get('result')
            
            if not session_key:
                print(f"Erro ao obter chave de sessão: {login_response.get('error')}")
                return None
                
            self.session_key = session_key
            print(f'✅ Sessão iniciada com chave: {session_key}')
            return session_key
                
        except Exception as e:
            print(f"Erro na conexão com LimeSurvey: {e}")
            return None
    
    def release_session_key(self):
        """Libera a chave de sessão"""
        if self.session_key:
            try:
                self.limesurvey_api_request('release_session_key', [self.session_key])
            except Exception as e:
                print(f"Erro ao liberar session key: {e}")
    
    def download_survey_data(self, survey_id: str) -> pd.DataFrame:
        """
        Baixa dados de um survey específico
        
        Args:
            survey_id: ID do survey
            
        Returns:
            DataFrame com os dados do survey
        """
        if not self.session_key:
            self.get_session_key()
            
        if not self.session_key:
            return pd.DataFrame()
        
        try:
            # Exportar respostas do formulário
            response = self.limesurvey_api_request(
                'export_responses',
                [self.session_key, survey_id, 'json', 'pt-BR', 'complete', 'long', 'long']
            )

            if response.get('error'):
                print(f"Erro ao exportar respostas do survey {survey_id}: {response['error']}")
                return pd.DataFrame()

            # Decodificar dados
            respostas = base64.b64decode(response['result']).decode('utf-8')
            dados = json.loads(respostas)
            df = pd.DataFrame(dados['responses'])

            # Obter textos das perguntas (CÓDIGO. TEXTO COMPLETO)
            question_map = {}
            group_list = self.limesurvey_api_request('list_groups', [self.session_key, survey_id])
            
            if group_list.get('result'):
                for group in group_list['result']:
                    gid = group['gid']
                    questions = self.limesurvey_api_request('list_questions', [self.session_key, survey_id, gid, 'pt-BR'])
                    
                    if questions.get('result'):
                        for q in questions['result']:
                            code = q['title']
                            text = q['question'].replace('\n', ' ').strip()
                            full = f"{code}. {text}"
                            question_map[code] = full

            # Renomear colunas do DataFrame
            df.columns = [question_map.get(col, col) for col in df.columns]
            
            # Adicionar coluna de origem
            df['form_origem'] = survey_id
            
            # Limpeza de caracteres ocultos e tags HTML
            df.columns = df.columns.str.strip().str.replace(r'\s+', ' ', regex=True).str.replace('\xa0', '', regex=False)
            df.columns = [limpar_html(col) for col in df.columns]
            df.columns = df.columns.str.strip()
            
            print(f'Formulário {survey_id} obtido com sucesso!')
            return df
            
        except Exception as e:
            print(f"Erro ao processar survey {survey_id}: {e}")
            return pd.DataFrame()
    
    def get_all_survey_data(self, processo_numero: Optional[str] = None) -> Dict[str, pd.DataFrame]:
        """
        Obtém dados de todos os surveys organizados por categoria
        
        Args:
            processo_numero: Se fornecido, filtra apenas respostas deste processo
            
        Returns:
            Dicionário com DataFrames por categoria
        """
        if not self.get_session_key():
            return {}
        
        try:
            all_data = {}
            
            # Baixar dados de processo
            processo_dfs = []
            for survey_id in self.survey_ids['processo']:
                df = self.download_survey_data(survey_id)
                if not df.empty:
                    processo_dfs.append(df)
            
            if processo_dfs:
                all_data['processo'] = pd.concat(processo_dfs, ignore_index=True)
            
            # Baixar dados de réu
            reu_dfs = []
            for survey_id in self.survey_ids['reu']:
                df = self.download_survey_data(survey_id)
                if not df.empty:
                    reu_dfs.append(df)
            
            if reu_dfs:
                all_data['reu'] = pd.concat(reu_dfs, ignore_index=True)
            
            # Baixar dados de vítima
            for survey_id in self.survey_ids['vitima']:
                df = self.download_survey_data(survey_id)
                if not df.empty:
                    all_data['vitima'] = df
            
            # Baixar dados de provas
            for survey_id in self.survey_ids['provas']:
                df = self.download_survey_data(survey_id)
                if not df.empty:
                    all_data['provas'] = df
            
            # Filtrar por número do processo se fornecido
            if processo_numero:
                all_data = self._filter_by_processo_numero(all_data, processo_numero)
            
            return all_data
            
        except Exception as e:
            print(f"Erro ao obter dados dos surveys: {e}")
            return {}
        finally:
            self.release_session_key()
    
    def _filter_by_processo_numero(self, all_data: Dict[str, pd.DataFrame], processo_numero: str) -> Dict[str, pd.DataFrame]:
        """Filtra os dados por número do processo"""
        filtered_data = {}
        
        for categoria, df in all_data.items():
            if df.empty:
                continue
                
            # Procurar colunas que podem conter número do processo
            possible_columns = [col for col in df.columns if any(word in col.lower() for word in ['processo', 'número', 'numero'])]
            
            if possible_columns:
                # Usar a primeira coluna encontrada
                col_processo = possible_columns[0]
                mask = df[col_processo].astype(str).str.contains(str(processo_numero), na=False, case=False)
                filtered_df = df[mask]
                
                if not filtered_df.empty:
                    filtered_data[categoria] = filtered_df
            else:
                # Se não encontrou coluna específica, manter todos os dados
                filtered_data[categoria] = df
        
        return filtered_data
    
    def get_survey_info(self) -> Dict:
        """Obtém informações sobre os surveys"""
        if not self.get_session_key():
            return {}
        
        try:
            survey_info = {}
            
            for categoria, survey_list in self.survey_ids.items():
                survey_info[categoria] = []
                
                for survey_id in survey_list:
                    response = self.limesurvey_api_request('get_survey_properties', [self.session_key, survey_id])
                    
                    if response.get('result'):
                        survey_info[categoria].append({
                            'id': survey_id,
                            'title': response['result'].get('surveyls_title', f'Survey {survey_id}'),
                            'active': response['result'].get('active', 'N')
                        })
            
            return survey_info
            
        except Exception as e:
            print(f"Erro ao obter informações dos surveys: {e}")
            return {}
        finally:
            self.release_session_key()
