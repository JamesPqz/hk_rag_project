from fastapi import FastAPI
from backend.api import documents

app = FastAPI()

app.include_router(documents.router)

@app.get('/')
def root():
    return {"message:RAG System API"}
