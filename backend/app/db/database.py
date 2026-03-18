from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.exc import SQLAlchemyError

from app.config import config
import logging

logger = logging.getLogger('sqlalchemy.engine')
logger.setLevel(logging.INFO)

engine = create_engine(config.DB_URL, pool_pre_ping=True, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_engine():
    return engine

