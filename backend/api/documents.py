from pathlib import Path

from fastapi import APIRouter, UploadFile, File
from langgraph_sdk.auth.exceptions import HTTPException

from backend.retrieval.vector_factory import get_vector_store
from backend.services.query_cache import QueryCache
from backend.utils.config_handler import chroma_config
from backend.utils.file_handler import get_file_docs, get_file_md5_hex
from backend.utils.md5_handler import save_md5, check_md5_hex
from backend.utils.logger_handler import logger

router = APIRouter(prefix='/documents', tags=['documents'])
UPLOAD_PATH = Path("backend/data/upload")
UPLOAD_PATH.mkdir(parents=True, exist_ok=True)

@router.post('/upload')
async def upload_document(file:UploadFile = File(...)):

    allow_types = tuple(chroma_config['allow_types'])
    if not file.filename.endswith(allow_types):
        raise HTTPException(status_code=400, detail=f"file type not allowed. Allowed types:{allow_types}")

    file_path = UPLOAD_PATH / file.filename
    content = await file.read()
    with open(file_path, 'wb') as f:
        f.write(content)

    docs = get_file_docs(str(file_path))
    md5 = get_file_md5_hex(str(file_path))

    if check_md5_hex(md5):
        logger.info(f"File {file.filename} already exists, skipping.")
        return {
            "status": 400,
            "message": "file already exists, skip indexing",
            "filename": file.filename,
            "md5": md5
        }

    vs = get_vector_store()
    vs.add_documents(docs)

    save_md5(md5)

    QueryCache.invalidate_by_pattern("qa:*")

    logger.info(f"File {file.filename} uploaded and indexed, segments: {len(docs)}")

    return {
        "status": 200,
        "message": "uploaded success",
        "filename": file.filename,
        "md5": md5,
        "segments": len(docs),
        "total_chars": sum(len(doc.page_content) for doc in docs)
    }

