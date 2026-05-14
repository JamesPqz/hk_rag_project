import os

from pymilvus import connections, utility
from backend.utils.config_handler import vector_config
from backend.utils.logger_handler import logger

class MilvusClient:
    _instance = None
    _connected = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._connected:
            return

        milvus_cfg = vector_config.get('milvus', {})
        self.uri = os.getenv('ZILLIZ_URI')
        self.token = os.getenv('ZILLIZ_TOKEN')
        self.collection_name = milvus_cfg.get('collection_name', 'rag')

        if not self.uri or not self.token:
            logger.warning("Zilliz/Milvus not configured, skipping connection")
            return

        try:
            connections.connect(
                alias="default",
                uri=self.uri,
                token=self.token,
            )
            self._connected = True
            logger.info(f"Connected to Zilliz/Milvus at {self.uri}")
        except Exception as e:
            logger.error(f"Failed to connect to Zilliz/Milvus: {e}")
            self._connected = False

    def is_healthy(self) -> bool:
        if not self._connected:
            return False
        try:
            return utility.get_server_version(using="default") is not None
        except Exception:
            return False

    def get_collection(self):
        if not self._connected:
            return None
        from pymilvus import Collection
        return Collection(self.collection_name)

    def close(self):
        if self._connected:
            connections.disconnect(alias="default")
            self._connected = False


milvus_client = MilvusClient()