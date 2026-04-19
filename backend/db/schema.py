from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, JSON, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from pgvector.sqlalchemy import Vector

from backend.utils.config_handler import postgresql_config

Base = declarative_base()

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True)
    filename = Column(String(255),nullable=False)
    file_type = Column(String(50))
    file_size = Column(Integer)
    chunk_count = Column(Integer)
    unload_time = Column(DateTime, default=datetime.now())
    status = Column(String(20))
    extra_metadata = Column(JSON)

class QueryLog(Base):
    __tablename__ = "query_logs"

    id = Column(Integer, primary_key=True)
    session_id = Column(String(100))
    question = Column(Text, nullable=False)
    answer = Column(Text)
    source = Column(JSON)
    latency_ms = Column(Integer)
    cache_hit = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.now())

class UserFeedback(Base):
    __tablename__ = "user_feedback"

    id = Column(Integer, primary_key=True)
    query_log_id = Column(Integer)
    rating = Column(Integer)
    comment = Column(Text)
    created_at = Column(DateTime, default=datetime.now())

class DocumentVector(Base):
    __tablename__ = 'document_vectors'


    id = Column(Integer, primary_key=True)
    # document_id = Column(Integer, ForeignKey("documents.id"))
    content = Column(String, nullable=False)
    doc_metadata = Column(JSON)
    embedding = Column(Vector(postgresql_config['dimension']))
