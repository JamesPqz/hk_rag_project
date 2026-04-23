from typing import Tuple, List, Dict, Any, Optional

from langchain_core.documents import Document

from backend.retrieval.reranker import Reranker
from backend.retrieval.vector_factory import get_vector_store
from backend.utils.logger_handler import logger

class RetrievalService:

    @staticmethod
    def retrieve(query:str, k:Optional[int] = None) -> Tuple[List[Document], List[str]]:
        vs = get_vector_store()
        result = vs.hybrid_search(query, k)

        if not result:
            return [],[]

        reranker = Reranker()
        result = reranker.rerank(query, result, k)

        docs = [doc for doc,_ in result]
        sources = list(set([doc.metadata.get('sources', 'unknown') for doc in docs]))

        return docs, sources

    @staticmethod
    def get_context(query:str, k: Optional[int] = None, context:Dict = None) -> str:
        result = RetrievalService.retrieve_with_citation(query, k)
        content, sources = result
        if sources:
            context['sources'] = sources
        return content

    @staticmethod
    def retrieve_with_citation(query:str, k:Optional[int]) -> Dict[str, Any]:
        vs = get_vector_store()
        result = vs.hybrid_search(query, k)

        if not result:
            return {
                "context": "",
                "sources":[]
            }

        reranker = Reranker()
        result = reranker.rerank(query, result, k)

        context_parts = []
        sources = []

        for doc, score in result:
            source = doc.metadata.get("source", "unknown")
            context_parts.append(doc.page_content)
            if source:
                sources.append(source)

        logger.info(f"retrieve {len(result)} infos for query: {query[:50]}")

        return {
            "context": "\n\n".join(context_parts),
            "sources":list(set(sources))
        }