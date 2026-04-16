import os
from dotenv import load_dotenv

load_dotenv()

class Setting:
    #api key
    DASHSCOPE_API_KEY:str = os.getenv("DASHSCOPE_API_KEY", "")

    #model
    LLM_MODEL:str = "qwen-max"
    EMBEDDING_MODEL: str = 'text-embedding-v4'

    #chromadb
    CHROME_DB_DIR = "data/chroma_db"

    #redis
    REDIS_HOST: str = os.getenv("REDIS_HOST","local_host")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", 6379))

    #postgre sql
    PG_HOST:str = os.getenv("PG_HOST","localhost")
    PG_PORT:int = int(os.getenv("PG_PORT",5432))
    PG_USER:str = os.getenv("PG_USER","postgres")
    PG_PASSWORD:str = os.getenv("PG_PASSWORD","postgres")
    PG_DATABASE:str = os.getenv("PG_DATABASE","rag_system")

    #rag
    CHUNK_SIZE:int = 500
    CHUNK_OVERLAP:int = 50
    TOP_K:int = 4
    SIMILARITY_THRESHOLD:float = 0.7

setting = Setting()


