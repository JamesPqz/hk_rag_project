from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from backend.utils.config_handler import postgresql_config as cfg
from backend.db.schema import Base

engine = create_engine(f"postgresql://{cfg['pg_user']}:{cfg['pg_password']}@{cfg['pg_host']}"
                       f":{cfg['pg_port']}/{cfg['pg_database']}")

SessionLocal = sessionmaker(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():

    with engine.connect() as conn:
        # 激活 pgvector 插件
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
        conn.commit()
    Base.metadata.create_all(bind=engine)