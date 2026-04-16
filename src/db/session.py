from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.config.setting import setting
from src.db.schema import Base

engine = create_engine(f"postgresql://{setting.PG_USER}:{setting.PG_PASSWORD}@{setting.PG_HOST}"
                       f":{setting.PG_PORT}/{setting.PG_DATABASE}")

SessionLocal = sessionmaker(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    Base.metadata.create_all(bind=engine)