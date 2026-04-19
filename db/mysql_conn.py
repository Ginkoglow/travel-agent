from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from settings.config import settings          # ✅ 修正导入
from db.dao import Base

DB_URL = f"mysql+pymysql://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}?charset=utf8mb4"

engine = create_engine(DB_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """手动建表（可选）"""
    from db.dao import UserQuery, TravelRecommendation
    Base.metadata.create_all(bind=engine)