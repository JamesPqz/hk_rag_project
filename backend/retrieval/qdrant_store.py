import os
from typing import List, Optional, Tuple

from langchain_community.embeddings import DashScopeEmbeddings
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_qdrant import QdrantVectorStore as LangchainQdrantStore
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams
from backend.utils.config_handler import load_config
from backend.utils.logger_handler import logger
from backend.models.factory import embedding_model
from .base_store import BaseVectorStore


class QdrantVectorStore(BaseVectorStore):
    def __init__(self):
        config = load_config('config/qdrant.yml')
        super().__init__(config)

        self.host = os.getenv('QDRANT_HOST', 'localhost')
        self.port = int(os.getenv('QDRANT_PORT', 6333))
        # self.api_key = config.get('api_key')
        self.collection_name = config.get('collection_name', 'rag')
        self.vector_size = config.get('vector_size', 1536)

        self.client = QdrantClient(
            host=self.host,
            port=self.port,
            # api_key=self.api_key if self.api_key else None,
        )

        self._create_collection()

        self.vector_store = LangchainQdrantStore(
            client=self.client,
            collection_name=self.collection_name,
            embedding = DashScopeEmbeddings(model="text-embedding-v2")
        )
        logger.info(f"QdrantVectorStore ready, collection: {self.collection_name}")

    def _create_collection(self):
        collections = self.client.get_collections().collections
        exists = any(c.name == self.collection_name for c in collections)

        if not exists:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=self.vector_size,
                    distance=Distance.COSINE,
                ),
            )
            logger.info(f"Created collection: {self.collection_name}")

    def _search_impl(self, query: str, k: int, with_score: bool) -> List[Tuple[Document, float]]:
        results = self.vector_store.similarity_search_with_score(query, k=k)
        return results

    def add_documents(self, docs: List[Document]):
        if not docs:
            return
        self.vector_store.add_documents(docs)
        logger.info(f"Added {len(docs)} documents to Qdrant")

    def load(self):
        logger.info("QdrantVectorStore ready")
        return self

    def delete(self, ids: List[str]):
        if not ids:
            return
        self.client.delete(
            collection_name=self.collection_name,
            points_selector=ids,
        )
        logger.info(f"Deleted {len(ids)} documents")