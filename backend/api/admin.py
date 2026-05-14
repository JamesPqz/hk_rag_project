from fastapi import APIRouter

from backend.retrieval.vector_factory import get_vector_store
from backend.services.query_cache import QueryCache
from backend.utils.config_handler import vector_config
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
    active = vector_config.get('active', 'chromadb')
    """清空 MD5 记录文件"""
    try:
        vs = get_vector_store()
        if active == 'chromadb':
            if hasattr(vs, 'collection'):
                all_ids = vs.collection.get()['ids']
                if all_ids:
                    vs.delete(all_ids)
                    logger.info(f"Deleted {len(all_ids)} vectors from Chroma")

        elif active == 'pgvector':
            from ..db.session import SessionLocal
            from ..db.schema import DocumentVector
            with SessionLocal() as session:
                results = session.query(DocumentVector.id).all()
                all_ids = [row[0] for row in results]
                if all_ids:
                    session.query(DocumentVector).filter(DocumentVector.id.in_(all_ids)).delete()
                    session.commit()
                    logger.info(f"Deleted {len(all_ids)} vectors from pgvector")

        elif active == 'milvus':
            if hasattr(vs, 'collection'):
                vs.collection.delete(expr="id >= 0")
                logger.info("Cleared Milvus collection")

        elif active == 'qdrant':
            if hasattr(vs, 'client') and hasattr(vs, 'collection_name'):
                vs.client.delete_collection(vs.collection_name)
                vs._create_collection()
                logger.info("Cleared Qdrant collection")

        clear_md5_records()
        logger.info("MD5 records cleared by admin request")
        return {"status": "success", "message": "MD5记录已清空"}
    except Exception as e:
        logger.error(f"Failed to clear MD5: {e}")
        return {"status": "error", "message": str(e)}
