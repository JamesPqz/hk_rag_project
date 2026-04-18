from typing import List, Tuple
import jieba
from rank_bm25 import BM25Okapi

from langchain_core.documents import Document

from backend.retrieval.chroma_store import VectorStore
from backend.utils.config_handler import chroma_config as cfg

from backend.utils.logger_handler import logger

class HybridSearch:
    def __init__(self, vector_store:VectorStore):
        self.vector_store = vector_store
        self.bm25 = None
        docs = vector_store.vector_store.similarity_search("", 1000)
        self.chunks = docs
        print(len(self.chunks))
        self.index_documents(self.chunks)

    def index_documents(self, documents:List[Document]):
        self.chunks = documents
        tokenized_docs = [list(jieba.cut(doc.page_content)) for doc in documents]
        self.bm25 = BM25Okapi(tokenized_docs)
        logger.info(f"build bm25 index,doc size:{len(documents)}")

    def search(self,query:str, k:int = cfg['top_k']) -> List[Tuple[Document, float]]:
        vector_rlt = self.vector_store.similar_search_with_score(query,k*2)

        tokenized_query = list(jieba.cut(query))
        print(f"tokenized_query->{tokenized_query}")
        bm25_score = self.bm25.get_scores(tokenized_query)
        print(f"bm25_score:{bm25_score}")
        bm25_indices = sorted(range(len(bm25_score)), key=lambda i:bm25_score[i], reverse=True)[:k*2]

        combined = {}
        for doc,score in vector_rlt:
            combined[doc.page_content] = combined.get(doc.page_content, 0) + 0.6 * (1 - score)

        max_score = max(bm25_score)
        min_score = min(bm25_score)
        for idx in bm25_indices:
            doc = self.chunks[idx]

            if max_score != min_score:
                score = (bm25_score[idx] - min_score) / (max_score - min_score)
            else:
                score = 0
            combined[doc.page_content] = combined.get(doc.page_content, 0) + 0.4 * score

        sort_rlt = sorted(combined.items(), key=lambda x:x[1], reverse=True)[:k]

        rlt_docs = []
        for content,score in sort_rlt:
            for doc in self.chunks:
                if content == doc.page_content:
                    rlt_docs.append((doc,score))
                    break

        return rlt_docs

if __name__ == '__main__':

    vs = VectorStore()

    hs = HybridSearch(vs)

    query = '香港金融管理局的主要职能包括什么'
    rlt = hs.search(query)

    for doc, score in rlt:
        print(f"hybrid score:{score}")
        print(f"content:{doc.page_content}")