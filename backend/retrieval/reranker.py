from typing import List, Tuple

import requests
import torch
from langchain_core.documents import Document
from sentence_transformers import CrossEncoder
from backend.utils.config_handler import chroma_config as cfg

from backend.utils.logger_handler import logger

import os
os.environ['HF_HUB_OFFLINE'] = '1'  # 强制离线
os.environ['TRANSFORMERS_OFFLINE'] = '1'

class Reranker:
    _instance = None
    _model = None  # 共享模型实例

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        self.api_key = os.getenv('DASHSCOPE_API_KEY')
        if not self.api_key:
            logger.warning("DASHSCOPE_API_KEY not set, rerank will use original order")

        self.api_url = "https://dashscope.aliyuncs.com/api/v1/services/rerank/text-rerank/text-rerank"
        # if torch.backends.mps.is_available():
        #     device = "mps"
        # elif torch.cuda.is_available():
        #     device = "cuda"
        # else:
        #     device = "cpu"
        #
        # if self._model is not None:
        #     return
        # self._model = CrossEncoder(
        #     'BAAI/bge-reranker-base',
        #     device=device,
        #     local_files_only=True
        # )

    def rerank(self, query:str, docs:List[Tuple[Document, float]], top_k:int = cfg['top_k']) -> List[Tuple[Document, float]]:
        if not docs:
            return []

        # pairs = [[query, doc.page_content] for doc,_ in docs]
        # scores = self._model.predict(pairs)
        # reranked = [(doc, float(score)) for (doc, _), score in zip(docs, scores) if score >= cfg['similarity_threshold']]
        # reranked.sort(key=lambda x:x[1], reverse=True)
        #
        # logger.info(f"rerank success.return {top_k} results.")
        # return reranked[:top_k]

        if not self.api_key:
            logger.warning("No API key, returning original docs")
            return docs[:top_k]

        documents = [doc.page_content for doc, _ in docs]

        request_body = {
            "model": "gte-rerank-v2",
            "input": {
                "query": query,
                "documents": documents
            },
            "parameters": {
                "top_n": top_k * 2,
                "return_documents": False
            }
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        try:
            response = requests.post(
                self.api_url,
                headers=headers,
                json=request_body,
                timeout=30
            )
            response.raise_for_status()

            result = response.json()

            reranked = []
            for item in result.get('output', {}).get('results', []):
                original_doc, original_score = docs[item['index']]
                reranked.append((original_doc, item['relevance_score']))

            reranked.sort(key=lambda x: x[1], reverse=True)

            logger.info(f"ali rerank success. return {top_k} results.")
            return reranked[:top_k]

        except Exception as e:
            logger.error(f"Rerank API call failed: {e}")
            return docs[:top_k]

if __name__ == '__main__':

    from backend.retrieval.chroma_store import VectorStore
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
