from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from utils.config_handler import postgresql_config as cfg
from src.db.schema import Base

engine = create_engine(f"postgresql://{cfg['PG_USER']}:{cfg['PG_PASSWORD']}@{cfg['PG_HOST']}"
                       f":{cfg['PG_PORT']}/{cfg['PG_DATABASE']}")

SessionLocal = sessionmaker(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    Base.metadata.create_all(bind=engine)