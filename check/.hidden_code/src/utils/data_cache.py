"""
Sistema de cache para dados dos formulários
"""

import pandas as pd
from typing import Dict, Optional
import threading
from datetime import datetime, timedelta

class DataCache:
    """Singleton para cache dos dados dos formulários"""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(DataCache, cls).__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, '_initialized') or not self._initialized:
            self.cached_data = {}
            self.last_update = None
            self.is_loading = False
            self.load_error = None
            self.cache_timeout = timedelta(minutes=30)  # Cache válido por 30 minutos
            # Cache para resultados por número de processo (TTL curto para evitar recarregamentos)
            self.process_results = {}  # chave -> (timestamp, data)
            self.process_ttl = timedelta(seconds=60)  # TTL padrão para resultados por processo
            self._initialized = True
    
    def get_data(self) -> Dict[str, pd.DataFrame]:
        """Retorna os dados em cache"""
        return self.cached_data.copy()
    
    def set_data(self, data: Dict[str, pd.DataFrame]):
        """Armazena dados no cache"""
        self.cached_data = data
        self.last_update = datetime.now()
        self.load_error = None
    
    def is_cache_valid(self) -> bool:
        """Verifica se o cache ainda é válido"""
        if not self.last_update:
            return False
        return datetime.now() - self.last_update < self.cache_timeout
    
    def set_loading(self, loading: bool):
        """Define status de carregamento"""
        self.is_loading = loading
    
    def set_error(self, error: str):
        """Define erro de carregamento"""
        self.load_error = error
        self.is_loading = False
    
    def clear_cache(self):
        """Limpa o cache"""
        self.cached_data = {}
        self.last_update = None
        self.load_error = None
        self.process_results = {}

    # ---- process-level cache helpers ----
    def get_process_cache(self, key: str):
        """Retorna resultado em cache para a chave do processo se ainda válido."""
        entry = self.process_results.get(key)
        if not entry:
            return None
        ts, data = entry
        if datetime.now() - ts < self.process_ttl:
            return data
        # expirado
        del self.process_results[key]
        return None

    def set_process_cache(self, key: str, data):
        """Armazena resultado de busca por processo com timestamp atual."""
        self.process_results[key] = (datetime.now(), data)
