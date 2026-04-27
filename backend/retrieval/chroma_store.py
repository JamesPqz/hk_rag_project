import os
from typing import List, Optional, Tuple

from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document

from backend.models.factory import embedding_model
from backend.loaders.document_loader import doc_loader
from backend.retrieval.base_store import BaseVectorStore
from backend.retrieval.hybrid_search import HybridSearch
from backend.utils.config_handler import chroma_config as cfg
from backend.utils.file_handler import list_dir_with_allowed_type, get_file_md5_hex
from backend.utils.md5_handler import check_md5_hex, save_md5
from backend.utils.path_tool import get_abs_path

from backend.utils.logger_handler import logger

class ChromaVectorStore(BaseVectorStore):
    def __init__(self, persist_dir:Optional[str] = None):
        super().__init__(cfg)
        self.persist_dir = get_abs_path(persist_dir or cfg['chrome_db_dir'])
        os.makedirs(self.persist_dir, exist_ok=True)
        self.embeddings = embedding_model
        self.vector_store:Optional[Chroma] = None
        self.hybrid_searcher = None
        self.load()

    def _search_impl(self, query: str, k: int, with_score: bool) -> List[Tuple[Document, float]]:
        if with_score:
            return self.vector_store.similarity_search_with_score(query, k)
        rlt = self.vector_store.similarity_search(query,k)
        return [(doc, 1.0) for doc in rlt]

    def hybrid_search(self, query: str, k: Optional[int] = None, alpha: float = None) -> List[Tuple[Document, float]]:
        """Chroma 的混合检索实现"""
        if not self.hybrid_searcher:
            return self.similar_search_with_score(query, k)
        return self.hybrid_searcher.search(query, k, alpha)

    def load(self) -> Chroma:
        self.vector_store = Chroma(
            embedding_function=self.embeddings,
            persist_directory=self.persist_dir,
            collection_metadata={"hnsw:space": "cosine"}
        )
        logger.info(f"create vector store success:{self.persist_dir}")

        files = list_dir_with_allowed_type(
            get_abs_path(cfg['data_path']),
            tuple(cfg['allow_types'])
        )

        all_docs = []
        for file in files:
            md5_hex = get_file_md5_hex(file)

            if check_md5_hex(md5_hex):
                logger.info(f"md5 exists:{file}")
                continue

            try:
                docs:List[Document] = doc_loader.process(file)

                self.vector_store.add_documents(docs)
                save_md5(md5_hex)
                all_docs.extend(docs)
                logger.info(f"load knowledge {file} success")
            except Exception as e:
                logger.error(f"load knowledge error:{e}")
                raise e

        if all_docs:
            self.hybrid_searcher = HybridSearch(self)
            self.hybrid_searcher.index_documents(all_docs)

        return self.vector_store

    def get_retriever(self):
        return self.vector_store.as_retriever(search_kwargs=cfg['top_k'])

    # def similarity_search(self, query:str, k:int = cfg['top_k']) -> List[Document]:
    #     # if not self.vector_store:
    #     #     self.load()
    #     return self.vector_store.similarity_search(query, k)
    #
    # def similar_search_with_score(self, query:str, k:int = cfg['top_k']) -> List[Tuple[Document,float]]:
    #     # if not self.vector_store:
    #     #     self.load()
    #     return self.vector_store.similarity_search_with_score(query,k)

    def add_documents(self, documents:List[Document]):
        self.vector_store.add_documents(documents)
        self.vector_store.persist()
        logger.info(f"add {len(documents)} documents")

    def delete(self, ids: List[str]):
        self.vector_store.delete(ids)
        logger.info(f"Deleted {len(ids)} documents")

    def get_all_ids(self) -> List[str]:
        return self.vector_store.get()['ids']

if __name__ == '__main__':

    # loader = DocumentLoader()
    # chunks = loader.process('../../data/raw/test_doc.txt')

    vs = ChromaVectorStore()

    query='香港金管局职能是啥'
    results = vs.similar_search_with_score(query, 8)

    for doc, score in results:
        print(f"similarity score:{score:.4f}")
        print(f"content:{doc.page_content}")
