from backend.utils.logger_handler import logger
from pathlib import Path
from typing import List

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

import backend.utils.config_handler as cfg
from backend.utils import file_handler

class DocumentLoader:
    def __init__(self):
        self.text_spliter = RecursiveCharacterTextSplitter(
            chunk_size= cfg.chroma_config['chunk_size'],
            chunk_overlap= cfg.chroma_config['chunk_overlap'],
            separators=cfg.chroma_config['separators'],
            length_function=len
        )

    def split(self, documents:List[Document]) -> List[Document]:
        print("真实文本长度：", len(documents[0].page_content))  # <-- 加这行
        print("chunk_size：", self.text_spliter._chunk_size)
        return self.text_spliter.split_documents(documents)

    def process(self, path:str):
        path_obj = Path(path)

        if not path_obj.exists():
            raise FileNotFoundError(f"file not found.{path}")

        docs = file_handler.get_file_docs(str(path_obj))

        chunks = self.split(docs)
        logger.info(f"load {path_obj.name} : {len(docs)} pages -> {len(chunks)} pieces")
        return chunks

doc_loader = DocumentLoader()

if __name__ == '__main__':
    loader = DocumentLoader()

    chunks = loader.process('../../data/raw/test_doc.txt')
    for idx, c in enumerate(chunks,1):
        print(f"第{idx}块内容预览: {c.page_content}")
