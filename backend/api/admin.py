from fastapi import APIRouter

from backend.retrieval.vector_factory import get_vector_store
from backend.services.query_cache import QueryCache
from backend.utils.logger_handler import logger
from backend.utils.md5_handler import clear_md5_records

router = APIRouter(prefix='/admin', tags=['admin'])

@router.delete('/cache')
async def clear_cache():
    """清除所有问答缓存"""
    try:
        QueryCache.invalidate_by_pattern("qa:*")
        logger.info("Cache cleared by admin request")
        return {"status": "success", "message": "所有缓存已清除"}
    except Exception as e:
        logger.error(f"Failed to clear cache: {e}")
        return {"status": "error", "message": str(e)}

@router.delete('/md5')
async def clear_md5():
    """清空 MD5 记录文件"""
    try:
        # 1. 清空向量库
        vs = get_vector_store()

        if hasattr(vs, 'get_all_ids'):
            all_ids = vs.get_all_ids()
        elif hasattr(vs, 'collection'):
            # Chroma 方式
            all_ids = vs.collection.get()['ids']
        else:
            # pgvector 方式：查询所有 id
            from ..db.session import SessionLocal
            from ..db.schema import DocumentVector
            with SessionLocal() as session:
                all_ids = [str(row[0]) for row in session.query(DocumentVector.id).all()]

        if all_ids:
            vs.delete(all_ids)
            logger.info(f"Deleted {len(all_ids)} vectors from vector store")

        clear_md5_records()
        logger.info("MD5 records cleared by admin request")
        return {"status": "success", "message": "MD5记录已清空"}
    except Exception as e:
        logger.error(f"Failed to clear MD5: {e}")
        return {"status": "error", "message": str(e)}
