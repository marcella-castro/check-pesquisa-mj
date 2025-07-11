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
    CACHE_TIMEOUT = int(os.getenv('CACHE_TIMEOUT', 300))  # 5 minutos
    
    # Configurações de validação
    CAMPOS_OBRIGATORIOS = [
        'processo_numero',
        'processo_ano',
        'tribunal',
        'classe_processual'
    ]
