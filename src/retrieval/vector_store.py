import logging
import os
from typing import List, Optional, Tuple

from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from src.models.factory import embedding_model

from utils.config_handler import chroma_config as cfg
from utils.file_handler import list_dir_with_allowed_type, get_file_md5_hex, get_file_docs
from utils.md5_handler import check_md5_hex, save_md5
from utils.path_tool import get_abs_path

logger = logging.getLogger(__name__)

class VectorStore:
    def __init__(self, persist_dir:Optional[str] = None):
        self.persist_dir = get_abs_path(persist_dir or cfg['chrome_db_dir'])
        self.embeddings = embedding_model
        self.vector_store:Optional[Chroma] = None
        self.load()

    # def _init_embeddings(self):
    #     if os.getenv("DASHSCOPE_API_KEY"):
    #         from langchain_community.embeddings import DashScopeEmbeddings
    #         return DashScopeEmbeddings(
    #             model='text-embedding-v1',
    #             dashscope_api_key=os.getenv("DASHSCOPE_API_KEY")
    #         )
    #     return HuggingFaceEmbeddings(
    #         model_name="BAAI/bge-small-zh-v1.5",
    #         model_kwargs={"device": "mps"},
    #         encode_kwargs={"normalize_embeddings": True}
    #     )

    # def create_from_documents(self,documents: List[Document]) -> Chroma:
    #     self.vector_store = Chroma.from_documents(
    #         embedding=self.embeddings,
    #         persist_directory=self.persist_dir,
    #         documents=documents,
    #         collection_metadata={"hnsw:space": "cosine"}
    #     )
    #     logger.info(f"create vector store success:{self.persist_dir}")
    #     return self.vector_store

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
        for file in files:
            md5_hex = get_file_md5_hex(file)

            if check_md5_hex(md5_hex):
                logger.info(f"md5 exists:{file}")
                continue

            try:
                docs:List[Document] = doc_loader.process(file)

                self.vector_store.add_documents(docs)
                save_md5(md5_hex)
                logger.info(f"load knowledge {file} success")
            except Exception as e:
                logger.error(f"load knowledge error:{e}")
                raise e

        return self.vector_store

    def get_retriever(self):
        return self.vector_store.as_retriever(search_kwargs=cfg['top_k'])

    def similarity_search(self, query:str, k:int = cfg['top_k']) -> List[Document]:
        # if not self.vector_store:
        #     self.load()
        return self.vector_store.similarity_search(query, k)

    def similar_search_with_score(self, query:str, k:int = cfg['top_k']) -> List[Tuple[Document,float]]:
        # if not self.vector_store:
        #     self.load()
        return self.vector_store.similarity_search_with_score(query,k)

    # def add_documents(self, documents:List[Document]):
    #     if not self.vector_store:
    #         self.load()
    #     self.vector_store.add_documents(documents)
    #     self.vector_store.persist()
    #     logger.info(f"add {len(documents)} documents")

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    from src.loaders.document_loader import DocumentLoader, doc_loader

    # loader = DocumentLoader()
    # chunks = loader.process('../../data/raw/test_doc.txt')

    vs = VectorStore()

    query='香港金管局职能是啥'
    results = vs.similar_search_with_score(query, 8)

    for doc, score in results:
        print(f"similarity score:{score:.4f}")
        print(f"content:{doc.page_content}")
