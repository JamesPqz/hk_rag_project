from backend.utils.config_handler import vector_config

def get_vector_store():
    active = vector_config['active']

    if active == 'chromadb':
        from backend.retrieval.chroma_store import ChromaVectorStore
        return ChromaVectorStore()
    if active == 'pgvector':
        from backend.retrieval.pg_store import PgVectorStore
        return PgVectorStore()
    raise ValueError(f"unknown vector store type:{active}")