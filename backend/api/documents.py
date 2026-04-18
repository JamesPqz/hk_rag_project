from pathlib import Path

from fastapi import APIRouter, UploadFile, File
from langgraph_sdk.auth.exceptions import HTTPException

from backend.utils.config_handler import chroma_config
from backend.utils.file_handler import get_file_docs, get_file_md5_hex

router = APIRouter(prefix='/documents', tags=['documents'])
UPLOAD_PATH = Path("data/upload")
UPLOAD_PATH.mkdir(parents=True, exist_ok=True)

@router.post('/upload')
async def upload_document(file:UploadFile = File(...)):

    allow_types = tuple(chroma_config['allow_type'])
    if not file.filename.endswith(allow_types):
        raise HTTPException(status_code=400, detail=f"file type not allowed. Allowed types:{allow_types}")

    file_path = UPLOAD_PATH / file.filename
    with open(file_path, 'wb', encoding='utf-8') as f:
        content = await f.read()
        f.write(content)

    docs = get_file_docs(str(file_path))
    md5 = get_file_md5_hex(str(file_path))

    return {
        "status": 200,
        "message": "uploaded",
        "filename": file.filename,
        "md5": md5,
        "segments": len(docs),
        "total_chars": sum(len(doc.page_content) for doc in docs)
    }

