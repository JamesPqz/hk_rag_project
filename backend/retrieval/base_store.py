from abc import ABC, abstractmethod
from typing import List, Tuple, Optional

from langchain_core.documents import Document

from backend.retrieval.reranker import Reranker


class BaseVectorStore(ABC):
    def __init__(self, cfg:dict):
        self.cfg = cfg
        self.top_k = cfg.get('top_k', 4)

    @abstractmethod
    def _search_impl(self, query:str, k:int, with_score:bool) -> List[Tuple[Document, float]]:
        pass

    def similarity_search(self, query: str, k: Optional[int]) -> List[Document]:
        k = k or self.top_k
        rlt = self._search_impl(query, k, False)
        return list([doc for doc,_ in rlt])

    def similar_search_with_score(self, query:str, k:Optional[int]) -> List[Tuple[Document,float]]:
        k = k or self.top_k
        return self._search_impl(query, k , True)

    def hybrid_search(self, query:str, k:Optional[int], alpha:int = 0.5) -> List[Tuple[Document,float]]:
        k = k or self.top_k
        return self.similar_search_with_score(query, k)

    @abstractmethod
    def add_documents(self, documents:List[Document]):
        pass

    @abstractmethod
    def load(self):
        pass

    @abstractmethod
    def delete(self, ids: List[str]):
        pass

    def rerank(self, query:str, docs: List[Tuple[Document, float]], k: int) -> List[Tuple[Document, float]]:
        reranker = Reranker()
        return reranker.rerank(query, docs, k)
