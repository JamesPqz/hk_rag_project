from abc import ABC, abstractmethod
from typing import List, Tuple

from langchain_core.documents import Document

class BaseVectorStore(ABC):

    @abstractmethod
    def similarity_search(self, query:str, k:int) -> List[Document]:
        pass

    @abstractmethod
    def similar_search_with_score(self, query:str, k:int) -> List[Tuple[Document,float]]:
        pass

    @abstractmethod
    def add_documents(self, documents:List[Document]):
        pass

    @abstractmethod
    def load(self):
        pass
