from typing import List, Tuple, Optional
from langchain_core.documents import Document
from sqlalchemy import text, inspect, select

from .base_store import BaseVectorStore
from ..db.schema import DocumentVector
from ..db.session import SessionLocal, engine
from ..models.factory import embedding_model
from ..utils.config_handler import postgresql_config
from ..utils.logger_handler import logger

import json


class PgVectorStore(BaseVectorStore):

    def __init__(self):
        super().__init__(postgresql_config)

        self.dimension = postgresql_config['dimension']
        self.table = DocumentVector
        self._create_table()
        self.load()

    def _create_table(self):
        with engine.connect() as conn:
            conn.execute(text('CREATE EXTENSION IF NOT EXISTS vector'))
            conn.commit()

        inspector = inspect(engine)
        if not inspector.has_table(self.table.__tablename__):
            self.table.__table__.create(engine)
            logger.info(f"table {self.table.__tablename__} created.")
        else:
            logger.info(f"table {self.table.__tablename__} already existed")

    def load(self):
        logger.info("PgVectorStore ready")
        return self

    def delete(self, ids: list[str]):
        int_ids = [int(id) for id in ids]
        with SessionLocal() as session:
            session.query(self.table).filter(self.table.id.in_(int_ids)).delete()
            session.commit()
            logger.info(f"Deleted {len(ids)} documents")

    def add_documents(self, docs: List[Document]):
        with SessionLocal() as session:
            try:
                for doc in docs:
                    query_embedding = embedding_model.embed_query(doc.page_content)
                    doc_vector = DocumentVector(
                        content=doc.page_content,
                        doc_metadata=doc.metadata,
                        embedding=query_embedding
                    )
                    session.add(doc_vector)
                session.commit()
                logger.info(f"add doc vector to pgvector success.length:{len(docs)}")
            except Exception as e:
                session.rollback()
                logger.error(f"add doc vector to pgvector fail.{str(e)}")
                raise

    def _search_impl(self, query: str, k: int, with_score: bool) -> List[Tuple[Document, float]]:
        query_embedding = embedding_model.embed_query(query)

        # ✅ 核心修复：把列表转成 vector 字符串，安全拼接
        vec_str = json.dumps(query_embedding)
        vector_literal = f"'{vec_str}'::vector"

        with SessionLocal() as session:
            sql = text(f"""
                SELECT content, doc_metadata, 1 - (embedding <=> {vector_literal}) as similarity
                FROM document_vectors
                ORDER BY embedding <=> {vector_literal}
                LIMIT :k
            """)

            results = session.execute(sql, {"k": k}).fetchall()
            return [(Document(page_content=row[0], metadata=row[1]), row[2] if with_score else 1.0) for row in results]

    def hybrid_search(self, query: str, k: Optional[int] = None, alpha: float = 0.5) -> List[Tuple[Document, float]]:
        k = k or self.top_k
        embedding = embedding_model.embed_query(query)

        try:
            with SessionLocal() as session:
                with open(postgresql_config['sql_path'], 'r') as f:
                    template = f.read()
                    sql = text(template.format(table_name=self.table.__tablename__))
                    results = session.execute(sql, {
                        "embedding": embedding,
                        "query": query,
                        "k": k,
                        "alpha": alpha
                    }).fetchall()
                    logger.info(f"hybrid search by pgvector success.length:{len(results)}")
                    return [(Document(page_content=row[0], metadata=row[1]), row[2]) for row in results]
        except Exception as e:
            logger.error(f"hybrid search fail.{str(e)}")
            raise