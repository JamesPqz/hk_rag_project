from typing import Optional, List

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from backend.retrieval.reranker import Reranker
from backend.retrieval.vector_factory import get_vector_store
from backend.services.conversation_service import ConversationService
from backend.services.llm_service import LLM_Service
from backend.services.query_cache import QueryCache
from backend.services.retrieval_service import RetrievalService
from backend.utils.prompts_loader import load_sys_prompt
from backend.utils.config_handler import chroma_config

router = APIRouter(prefix='/chat', tags=['chat'])

llm_service = LLM_Service()

class Question(BaseModel):
    query:str
    k:Optional[int] = 4

class Answer(BaseModel):
    answer:str
    sources:List[str]

# def _get_context_and_sources(query:str , k:int):
#     vs = get_vector_store()
#     result = vs.hybrid_search(query, k)
#
#     reranker = Reranker()
#     result = reranker.rerank(query, result, k)
#     result = [(doc, score) for doc, score in result if score >= chroma_config['similarity_threshold']]
#
#     if not result:
#         sources = []
#         context = "there's no relevant infos in library"
#     else:
#         sources = list(set([doc.metadata.get("source", "unknown") for doc, _ in result]))
#         context = '\n'.join([doc.page_content for doc,_ in result])
#
#     return context, sources

def build_prompt(query:str, session_id: str ,k :int):
    conv_service = ConversationService(session_id)
    history = conv_service.get_history()

    history_msg = "chat history:\n" + "\n".join([f"'role': {his['role']}, 'content':{his['content']}" for his in history])

    rewrite_prompt = f"把以下问题改写成更清晰的检索查询：{query}"
    new_query = llm_service.generate(rewrite_prompt)

    context, sources = RetrievalService.retrieve(new_query, k)

    prompt = load_sys_prompt()

    prompt = prompt.format(context=context, question=query, history=history_msg)

    return prompt, sources, conv_service

@router.post('/ask', response_model=Answer)
async def ask(question:Question, session_id:str = 'default'):
    prompt, sources, conv_service = build_prompt(question.query, session_id, question.k)

    cache = QueryCache.get(question.query)
    if cache:
        answer, sources = cache
        return Answer(answer=answer, sources=sources)

    answer = llm_service.generate(prompt)

    conv_service.add_message('user', question.query)
    conv_service.add_message('assistant', answer)

    QueryCache.set(question.query, answer, list(set(sources)))

    return Answer(
        answer=answer,
        sources = list(set(sources))
    )

@router.post('/ask/stream')
async def ask_stream(question:Question, session_id:str = 'default'):
    cache = QueryCache.get(question.query)
    if cache:
        answer, sources = cache
        async def stream_from_cache():
            full_answer = ""
            for char in answer:
                yield char

        headers = {"X-Sources": ",".join(sources)}
        return StreamingResponse(stream_from_cache(), media_type="text/plain", headers=headers)

    prompt, sources, conv_service = build_prompt(question.query, session_id, question.k)

    async def generate():
        full_answer = ""
        async for chunk in llm_service.stream(prompt):
            full_answer += chunk
            yield chunk.encode('utf-8')

        conv_service.add_message("user", question.query)
        conv_service.add_message("assistant", full_answer)

        QueryCache.set(question.query, answer=full_answer, sources=sources)

    # 将 sources 放入响应头
    headers = {"X-Sources": ",".join(sources)}
    return StreamingResponse(generate(), media_type="text/plain", headers=headers)
