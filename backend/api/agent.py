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
    context: Optional[Dict[str, Any]] = None

class AgentResponse(BaseModel):
    answer:str
    sources:List[str]
    tools: List[str]

@router.post('/chat', response_model=AgentResponse)
async def agent_chat(req: AgentRequest,session_id: str):
    cache = QueryCache.get(req.query)
    if cache:
        answer, sources = cache
        return AgentResponse(answer=answer, sources=sources)

    answer, sources, all_tools = run_agent(req.query,session_id, req.context)
    return AgentResponse(answer=answer, sources=sources, tools=all_tools)


@router.post("/chat/stream")
async def agent_chat_stream(request: AgentRequest, session_id:str):
    cache = QueryCache.get(request.query)
    if cache:
        answer, sources = cache

        async def stream_from_cache():
            for char in answer:
                yield char

        headers = {"X-Sources": ",".join(sources)}
        return StreamingResponse(stream_from_cache(), media_type="text/plain", headers=headers)


    generator, sources, all_tools = run_agent(request.query, session_id, request.context, True)
    # 将 sources, tools 放入响应头
    headers = {"X-Sources": ",".join(sources), "X-Tools": ",".join(all_tools)}
    return StreamingResponse(generator, media_type="text/plain", headers=headers)