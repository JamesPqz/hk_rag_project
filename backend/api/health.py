# backend/api/health.py
from fastapi import APIRouter, Depends
from sqlalchemy import text
from backend.db.session import SessionLocal
from backend.cache.redis_client import redis_client

router = APIRouter(prefix="/health", tags=["health"])


@router.get("")
async def health_check():
    # 数据库检查
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

    return {
        "status": "healthy" if db_status == "ok" and redis_status == "ok" else "unhealthy",
        "database": db_status,
        "redis": redis_status
    }