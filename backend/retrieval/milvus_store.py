import os
from typing import List, Optional, Tuple
from langchain_core.documents import Document
from langchain_milvus import Zilliz
from backend.utils.config_handler import load_config
from backend.utils.logger_handler import logger
from backend.models.factory import embedding_model
from .base_store import BaseVectorStore
from ..db.milvus_client import milvus_client
from pymilvus import Collection, connections


class MilvusVectorStore(BaseVectorStore):
    def __init__(self):
        config = load_config('config/vector.yml')['milvus']
        super().__init__(config)

        self.collection_name = config.get('collection_name', 'rag')
        self.dimension = config.get('dimension', 1536)

        if not milvus_client.get_collection():
            raise ConnectionError("Milvus not connected")

        class CustomEmbedding:
            def embed_documents(self, texts):
                return [embedding_model.embed_query(text) for text in texts]

            def embed_query(self, text):
                return embedding_model.embed_query(text)

        self.collection = Collection(self.collection_name)
        self.collection.load()
        logger.info(f"MilvusVectorStore ready, collection: {self.collection_name}")

    def _search_impl(self, query: str, k: int, with_score: bool) -> List[Tuple[Document, float]]:
        query_vector = embedding_model.embed_query(query)

        search_params = {"metric_type": "COSINE", "params": {"ef": 64}}

        results = self.collection.search(
            data=[query_vector],
            anns_field="embedding",
            param=search_params,
            limit=k,
            output_fields=["content", "source"]
        )

        docs_with_scores = []
        for hits in results:
            for hit in hits:
                doc = Document(
                    page_content=hit.entity.get('content'),
                    metadata={"source": hit.entity.get('source')}
                )
                docs_with_scores.append((doc, hit.score))

        return docs_with_scores

    def add_documents(self, docs: List[Document]):
        if not docs:
            return

        embeddings = [embedding_model.embed_query(doc.page_content) for doc in docs]
        contents = [doc.page_content for doc in docs]
        sources = [doc.metadata.get('source', 'unknown') for doc in docs]

        data = [
            embeddings,
            contents,
            sources,
        ]

        self.collection.insert(data)
        self.collection.flush()
        logger.info(f"Added {len(docs)} documents to Milvus")

    def load(self):
        logger.info("MilvusVectorStore ready")
        return self

    def delete(self, ids: List[str]):
        if not ids:
            return
        expr = f"id in {ids}"
        self.collection.delete(expr)
        logger.info(f"Deleted {len(ids)} documents")