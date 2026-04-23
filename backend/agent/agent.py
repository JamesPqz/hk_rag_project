import re
from typing import Optional, Dict, Any, List

from fastapi import APIRouter
from pydantic import BaseModel
from starlette.responses import StreamingResponse

from backend.agent.graph import run_agent
from backend.services.query_cache import QueryCache

router = APIRouter(prefix='/agent', tags=['agent'])

class AgentRequest(BaseModel):
    query: str
    session_id:str
    context: Optional[Dict[str, Any]] = None

class AgentResponse(BaseModel):
    answer:str
    sources:List[str]

@router.post('/chat', response_model=AgentResponse)
async def agent_chat(req: AgentRequest):
    cache = QueryCache.get(req.query)
    if cache:
        answer, sources = cache
        return AgentResponse(answer=answer, sources=sources)

    answer, sources = run_agent(req.query,req.session_id, req.context)
    return AgentResponse(answer=answer, sources=sources)


@router.post("/chat/stream")
async def agent_chat_stream(request: AgentRequest):
    cache = QueryCache.get(request.query)
    if cache:
        answer, sources = cache

        async def stream_from_cache():
            full_answer = ""
            for char in answer:
                yield char

        headers = {"X-Sources": ",".join(sources)}
        return StreamingResponse(stream_from_cache(), media_type="text/plain", headers=headers)


    generate, sources = run_agent(request.query, request.session_id, None, True)
    # 将 sources 放入响应头
    headers = {"X-Sources": ",".join(sources)}
    return StreamingResponse(generate(), media_type="text/plain", headers=headers)