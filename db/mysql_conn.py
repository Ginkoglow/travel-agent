from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from settings.config import settings
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
    from db.dao import UserQuery, TravelRecommendation
    Base.metadata.create_all(bind=engine)


def save_query(session_id: str, query: str, city: str, days: int, preferences: str) -> int:
    from db.dao import UserQuery
    db = SessionLocal()
    try:
        db_query = UserQuery(
            query_text=query,
            location=city,
            travel_date="",
            days=days,
            preferences=preferences
        )
        db.add(db_query)
        db.commit()
        db.refresh(db_query)
        return db_query.id
    finally:
        db.close()


def save_plan(query_id: int, plan: str) -> None:
    from db.dao import TravelRecommendation
    db = SessionLocal()
    try:
        reco = TravelRecommendation(
            query_id=query_id,
            weather_info="",
            poi_info="",
            recommendation=plan
        )
        db.add(reco)
        db.commit()
    finally:
        db.close()


def get_history():
    from db.dao import UserQuery
    db = SessionLocal()
    try:
        return db.query(UserQuery).order_by(UserQuery.created_at.desc()).limit(20).all()
    finally:
        db.close()


def get_plan_by_query_id(query_id: int) -> str:
    from db.dao import TravelRecommendation
    db = SessionLocal()
    try:
        reco = db.query(TravelRecommendation).filter(TravelRecommendation.query_id == query_id).first()
        return reco.recommendation if reco else None
    finally:
        db.close()