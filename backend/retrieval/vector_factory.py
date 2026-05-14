from backend.utils.config_handler import vector_config
from backend.utils.logger_handler import logger

def get_vector_store():
    active = vector_config['active']

    if active == 'chromadb':
        from backend.retrieval.chroma_store import ChromaVectorStore
        return ChromaVectorStore()
    if active == 'pgvector':
        from backend.retrieval.pg_store import PgVectorStore
        return PgVectorStore()
    elif active == 'milvus':
        from backend.retrieval.milvus_store import MilvusVectorStore
        return MilvusVectorStore()
    elif active == 'qdrant':
        from backend.retrieval.qdrant_store import QdrantVectorStore
        return QdrantVectorStore()

    raise ValueError(f"unknown vector store type:{active}")