import os
import hashlib
from backend.utils.logger_handler import logger
from langchain_core.documents import Document
from langchain_community.document_loaders import PyPDFLoader, TextLoader, CSVLoader, UnstructuredMarkdownLoader

from backend.utils.path_tool import get_abs_path

def get_file_md5_hex(file_path:str):
    if not os.path.exists(file_path):
        logger.error(f'[md5] path {file_path} not exist')
        return None

    if not os.path.isfile(file_path):
        logger.error(f'[md5] path {file_path} is not a file')
        return None

    md5_obj = hashlib.md5()
    chunk_size = 4096
    try:
        with open(file_path, 'rb') as f:
            while chunk := f.read(chunk_size):
                md5_obj.update(chunk)
            md5_hex = md5_obj.hexdigest()
            return md5_hex
    except Exception as e:
        logger.error(f'md5 update fail{str(e)}')
        return None

def list_dir_with_allowed_type(path:str , allowed_types: tuple[str]):
    files = []

    if not os.path.isdir(path):
        logger.error(f'[list_dir_with_allowed_type] {path} is not dir')
        # print(f'[list_dir_with_allowed_type] {path} is not dir')
        return tuple(files)

    for f in os.listdir(path):
        if f.endswith(allowed_types):
            files.append(os.path.join(path, f))

    return tuple(files)

def load_pdf(file_path:str, password:str = None) -> list[Document]:
    return PyPDFLoader(file_path, password).load()

def load_txt(file_path:str) -> list[Document]:
    return TextLoader(file_path, encoding='utf-8').load()

def load_csv(file_path:str) -> list[Document]:
    return CSVLoader(file_path, encoding='utf-8').load()

def load_md(file_path:str) -> list[Document]:
    return UnstructuredMarkdownLoader(file_path).load()

def get_file_docs(path:str):
    if path.endswith('.txt'):
        return load_txt(path)
    if path.endswith('.pdf'):
        return load_pdf(path)
    if path.endswith('.csv') or path.endswith('.tsv'):
        return load_csv(path)
    if path.endswith('.md') or path.endswith('.markdown'):
        return load_md(path)
    return []

if __name__ == '__main__':
    from backend.utils.config_handler import chroma_config as cfg
    docs = list_dir_with_allowed_type(
        get_abs_path(cfg['data_path']),
        tuple(cfg['allow_types'])
    )
    for doc in docs:
        md5_hex = get_file_md5_hex(doc)
        print(md5_hex)