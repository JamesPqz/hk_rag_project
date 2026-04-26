import logging

from fastapi import FastAPI,Request

from backend.api import documents, chat, admin, agent
from backend.api import health

app = FastAPI()

app.include_router(documents.router)
app.include_router(chat.router)
app.include_router(health.router)
app.include_router(agent.router)
app.include_router(admin.router)


@app.middleware("http")
async def log_middleware(request: Request, call_next):
    import time
    start_time = time.time()

    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        logging.info(f"{request.method} {request.url.path} - {response.status_code} - {process_time:.3f}s")
        return response
    except Exception as e:
        logging.exception("Request failed")
        raise

@app.get('/')
def root():
    return {"message:RAG System API"}
