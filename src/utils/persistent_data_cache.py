"""
Sistema de cache persistente para dados dos formulários
"""

import json
import pandas as pd
from typing import Dict, Optional
import threading
from datetime import datetime, timedelta
import os
from pathlib import Path
import logging
from config.settings import Config

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

class PersistentDataCache:
    """Cache persistente para dados dos formulários"""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(PersistentDataCache, cls).__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, '_initialized') or not self._initialized:
            # Configurações básicas
            self.cache_dir = Path("data_cache")
            self.cache_file = self.cache_dir / "surveys_cache.json"
            self.backup_file = self.cache_dir / "surveys_cache.backup.json"
            self.metadata_file = self.cache_dir / "cache_metadata.json"
            self.log_file = self.cache_dir / "cache.log"
            
            # Cache em memória
            self.cached_data = {}
            self.last_update = None
            self.is_loading = False
            self.load_error = None
            
            # Tempo de cache (12 horas em produção, 5 minutos em desenvolvimento)
            self.cache_timeout = timedelta(hours=12) if not Config.DEBUG else timedelta(minutes=5)
            
            # Criar diretório de cache se não existir
            self._setup_cache_directory()
            
            # Carregar cache do disco se existir
            self._load_from_disk()
            
            self._initialized = True
            
            logger.info(f"Cache inicializado - Modo: {'Debug' if Config.DEBUG else 'Produção'}")
    
    def _setup_cache_directory(self):
        """Configura diretório de cache e logging"""
        self.cache_dir.mkdir(exist_ok=True)
        
        # Configurar arquivo de log
        file_handler = logging.FileHandler(self.log_file)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        ))
        logger.addHandler(file_handler)
    
    def _serialize_dataframe(self, df: pd.DataFrame) -> dict:
        """Serializa DataFrame para formato JSON"""
        if df is None or df.empty:
            return {}
        return {
            'data': df.to_json(orient='split'),
            'columns': df.columns.tolist()
        }
    
    def _deserialize_dataframe(self, data: dict) -> pd.DataFrame:
        """Deserializa DataFrame do formato JSON"""
        if not data:
            return pd.DataFrame()
        try:
            return pd.read_json(data['data'], orient='split')
        except Exception as e:
            logger.error(f"Erro ao deserializar DataFrame: {e}")
            return pd.DataFrame()
    
    def _save_to_disk(self):
        """Salva cache no disco com backup"""
        try:
            # Criar backup do cache atual se existir
            if self.cache_file.exists():
                self.cache_file.rename(self.backup_file)
            
            # Serializar dados
            cache_data = {}
            for category, df in self.cached_data.items():
                if isinstance(df, list):
                    cache_data[category] = [
                        self._serialize_dataframe(frame) for frame in df
                    ]
                else:
                    cache_data[category] = self._serialize_dataframe(df)
            
            # Salvar novo cache
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
            
            # Salvar metadata
            metadata = {
                'last_update': self.last_update.isoformat() if self.last_update else None,
                'next_update': (datetime.now() + self.cache_timeout).isoformat(),
                'entries': len(self.cached_data),
                'size': os.path.getsize(self.cache_file)
            }
            
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Cache salvo em disco - Próxima atualização: {metadata['next_update']}")
            
        except Exception as e:
            logger.error(f"Erro ao salvar cache: {e}")
            # Restaurar backup se houver erro
            if self.backup_file.exists():
                self.backup_file.rename(self.cache_file)
    
    def _load_from_disk(self):
        """Carrega cache do disco"""
        try:
            if not self.cache_file.exists():
                logger.info("Cache não encontrado em disco")
                return
            
            # Carregar metadata primeiro
            if self.metadata_file.exists():
                with open(self.metadata_file, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                    
                last_update = datetime.fromisoformat(metadata['last_update']) if metadata.get('last_update') else None
                next_update = datetime.fromisoformat(metadata['next_update'])
                
                # Se cache ainda é válido
                if last_update and datetime.now() < next_update:
                    # Carregar dados do cache
                    with open(self.cache_file, 'r', encoding='utf-8') as f:
                        cache_data = json.load(f)
                    
                    # Deserializar dados
                    for category, data in cache_data.items():
                        if isinstance(data, list):
                            self.cached_data[category] = [
                                self._deserialize_dataframe(frame_data)
                                for frame_data in data
                            ]
                        else:
                            self.cached_data[category] = self._deserialize_dataframe(data)
                    
                    self.last_update = last_update
                    logger.info(f"Cache carregado do disco - Última atualização: {last_update}")
                else:
                    logger.info("Cache expirado, será atualizado na próxima requisição")
            
        except Exception as e:
            logger.error(f"Erro ao carregar cache: {e}")
            self.cached_data = {}
            self.last_update = None
    
    def get_data(self) -> Dict[str, pd.DataFrame]:
        """Retorna os dados em cache"""
        return self.cached_data.copy()
    
    def set_data(self, data: Dict[str, pd.DataFrame]):
        """Armazena dados no cache e persiste em disco"""
        self.cached_data = data
        self.last_update = datetime.now()
        self.load_error = None
        
        # Salvar em disco
        self._save_to_disk()
        
        logger.info(f"Cache atualizado - {len(data)} categorias de dados")
    
    def is_cache_valid(self) -> bool:
        """Verifica se o cache ainda é válido"""
        if not self.last_update:
            return False
        return datetime.now() - self.last_update < self.cache_timeout
    
    def set_loading(self, loading: bool):
        """Define status de carregamento"""
        self.is_loading = loading
        if loading:
            logger.info("Iniciando carregamento de dados")
        else:
            logger.info("Carregamento de dados finalizado")
    
    def set_error(self, error: str):
        """Define erro de carregamento"""
        self.load_error = error
        self.is_loading = False
        logger.error(f"Erro no cache: {error}")
    
    def clear_cache(self):
        """Limpa o cache em memória e em disco"""
        self.cached_data = {}
        self.last_update = None
        self.load_error = None
        
        # Remover arquivos de cache
        for file in [self.cache_file, self.backup_file, self.metadata_file]:
            if file.exists():
                file.unlink()
        
        logger.info("Cache limpo completamente")