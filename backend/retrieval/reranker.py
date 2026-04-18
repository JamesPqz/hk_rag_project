from typing import List, Tuple

from langchain_core.documents import Document
from sentence_transformers import CrossEncoder
from backend.utils.config_handler import chroma_config as cfg

from backend.utils.logger_handler import logger

class Reranker:
    def __init__(self):
        self.model = CrossEncoder(
            'BAAI/bge-reranker-base',
            device='mps'
        )

    def rerank(self, query:str, docs:List[Tuple[Document, float]], top_k:int = cfg['top_k']) -> List[Tuple[Document, float]]:
        if not docs:
            return []

        pairs = [[query, doc.page_content] for doc,_ in docs]

        scores = self.model.predict(pairs)

        reranker = [(doc, float(score)) for (doc, _), score in zip(docs, scores)]
        reranker.sort(key=lambda x:x[1], reverse=True)

        logger.info(f"rerank success.return {top_k} results.")

        return reranker[:top_k]

if __name__ == '__main__':

    from backend.retrieval.vector_store import VectorStore
    from backend.retrieval.hybrid_search import HybridSearch

    vs = VectorStore()
    hs = HybridSearch(vs)

    query = '香港金融管理局的主要职能包括什么'
    rlt1 = hs.search(query, 10)
    for doc, score in rlt1:
        print(f"score1 -> {score}")
        print(f"content1 -> {doc.page_content}")

    reranker = Reranker()
    rlt2 = reranker.rerank(query, rlt1, 3)
    for doc, score in rlt2:
        print(f"score2 -> {score}")
        print(f"content2 -> {doc.page_content}")
