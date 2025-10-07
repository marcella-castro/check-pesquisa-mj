"""
Configurações da aplicação
"""

import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

class Config:
    # Configurações da API LimeSurvey
    LIME_API_URL = os.getenv('LIME_API_URL', '')
    LIME_USERNAME = os.getenv('LIME_USERNAME', '')
    LIME_PASSWORD = os.getenv('LIME_PASSWORD', '')
    
    # Validação das configurações obrigatórias
    @classmethod
    def validate_config(cls):
        """Valida se as configurações obrigatórias estão presentes"""
        missing_configs = []
        
        if not cls.LIME_API_URL:
            missing_configs.append('LIME_API_URL')
        if not cls.LIME_USERNAME:
            missing_configs.append('LIME_USERNAME')
        if not cls.LIME_PASSWORD:
            missing_configs.append('LIME_PASSWORD')
            
        return missing_configs
    
    @classmethod
    def is_configured(cls):
        """Verifica se todas as configurações obrigatórias estão presentes"""
        return len(cls.validate_config()) == 0
    
    # IDs dos surveys por categoria
    SURVEY_IDS = {
        'processo': ['917441', '245785', '117563'],
        'vitima': ['345978'],
        'provas': ['389137'],
        'reu': ['653817', '284222', '357387']
    }
    
    # Configurações da aplicação
    DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', 8050))
    
    # Configurações de cache
    CACHE_TIMEOUT = int(os.getenv('CACHE_TIMEOUT', 600))  # 10 minutos
    
    # Configurações de validação
    CAMPOS_OBRIGATORIOS = [
        'processo_numero',
        'processo_ano',
        'tribunal',
        'classe_processual'
    ]
