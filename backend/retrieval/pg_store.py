from typing import List, Tuple
from langchain_core.documents import Document
from .base_store import BaseVectorStore


class PgVectorStore(BaseVectorStore):
    def __init__(self):
        # TODO: 实现 pgvector 初始化
        pass

    def load(self):
        # TODO: 实现加载逻辑
        pass

    def similarity_search(self, query: str, k: int) -> List[Document]:
        # TODO: 实现相似度搜索
        pass

    def similar_search_with_score(self, query: str, k: int) -> List[Tuple[Document, float]]:
        # TODO: 实现带分数的搜索
        pass

    def add_documents(self, docs: List[Document]):
        # TODO: 实现添加文档
        pass