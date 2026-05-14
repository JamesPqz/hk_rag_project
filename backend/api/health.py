# backend/api/health.py
from fastapi import APIRouter, Depends
from sqlalchemy import text

from backend.db.milvus_client import milvus_client
from backend.db.session import SessionLocal
from backend.cache.redis_client import redis_client
import requests

router = APIRouter(prefix="/health", tags=["health"])


@router.get("")
async def health_check():
    # PostgreSQL检查
    db_status = "ok"
    try:
        with SessionLocal() as db:
            db.execute(text('SELECT 1'))
    except Exception as e:
        db_status = str(e)

    # Redis 检查
    redis_status = "ok"
    try:
        redis_client.set('test', 'ok', ttl=1)
        redis_client.get('test')
    except Exception as e:
        redis_status = str(e)

    # Milvus/Zilliz 检查
    milvus_status = "ok"
    try:
        if not milvus_client.is_healthy():
            milvus_status = "not configured or disconnected"
    except Exception as e:
        milvus_status = str(e)

    # Qdrant 检查
    qdrant_status = "not configured"
    try:
        from backend.utils.config_handler import vector_config
        qdrant_config = vector_config.get('qdrant', {})
        host = qdrant_config.get('host', 'localhost')
        port = qdrant_config.get('port', 6333)
        resp = requests.get(f"http://{host}:{port}/collections", timeout=2)
        if resp.status_code == 200:
            qdrant_status = "ok"
        else:
            qdrant_status = "error"
    except Exception as e:
        qdrant_status = str(e)

    return {
        "status": "healthy" if db_status == "ok" and redis_status == "ok"
                               and milvus_status == "ok" and qdrant_status == "ok" else "unhealthy",
        "database": db_status,
        "redis": redis_status,
        "milvus": milvus_status,
        "qdrant": qdrant_status
    }