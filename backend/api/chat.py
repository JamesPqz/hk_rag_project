from typing import Optional, List

from fastapi import APIRouter
from pydantic import BaseModel

from backend.retrieval.vector_factory import get_vector_store

router = APIRouter(prefix='/chat', tags=['chat'])

class Question(BaseModel):
    query:str
    k:Optional[int] = 4

class Answer(BaseModel):
    answer:str
    sources:List[str]

@router.post('/ask', response_model=Answer)
async def ask(question:Question):
    vs = get_vector_store()
    result = vs.similar_search_with_score(question.query, question.k)

    sources = [doc.metadata.get('source','unknown') for doc,_ in result]
    context = '\n'.join([doc.page_content for doc,_ in result])

    return Answer(
        answer=f"基于检索到的{len(result)}个片段：\n{context}",
        sources = list(set(sources))
    )
