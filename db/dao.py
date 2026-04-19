from sqlalchemy.orm import Session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from datetime import datetime

Base = declarative_base()

class UserQuery(Base):
    __tablename__ = "user_queries"
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), index=True)
    query_text = Column(Text, nullable=False)
    location = Column(String(100))
    travel_date = Column(String(50))
    days = Column(Integer)
    preferences = Column(String(255))
    created_at = Column(DateTime, default=datetime.now)

class TravelRecommendation(Base):
    __tablename__ = "travel_recommendations"
    id = Column(Integer, primary_key=True, index=True)
    query_id = Column(Integer, ForeignKey("user_queries.id"))
    weather_info = Column(Text)
    poi_info = Column(Text)
    recommendation = Column(Text)
    created_at = Column(DateTime, default=datetime.now)

# ------------------- 数据操作 -------------------
def create_user_query(db: Session, query_text: str, location: str, travel_date: str, days: int, preferences: str, session_id: str = None):
    db_query = UserQuery(
        session_id=session_id,
        query_text=query_text,
        location=location,
        travel_date=travel_date,
        days=days,
        preferences=preferences
    )
    db.add(db_query)
    db.commit()
    db.refresh(db_query)
    return db_query

def create_recommendation(db: Session, query_id: int, weather_info: str, poi_info: str, recommendation: str):
    db_reco = TravelRecommendation(
        query_id=query_id,
        weather_info=weather_info,
        poi_info=poi_info,
        recommendation=recommendation
    )
    db.add(db_reco)
    db.commit()
    db.refresh(db_reco)
    return db_reco

def get_history_list(db: Session, skip: int = 0, limit: int = 10):
    return db.query(UserQuery).order_by(UserQuery.created_at.desc()).offset(skip).limit(limit).all()

def get_recommendation_detail(db: Session, query_id: int):
    return db.query(TravelRecommendation).filter(TravelRecommendation.query_id == query_id).first()