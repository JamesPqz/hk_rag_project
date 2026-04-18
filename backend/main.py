import logging

from fastapi import FastAPI,Request
from backend.api import documents, chat

app = FastAPI()

app.include_router(documents.router)
app.include_router(chat.router)

@app.middleware("http")
async def log_errors(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception as e:
        logging.exception("Request failed")
        raise

@app.get('/')
def root():
    return {"message:RAG System API"}
