from sqlalchemy.orm import Session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, ForeignKey
from datetime import datetime

Base = declarative_base()

# 1. 用户查询表（和你的SQL完全对应）
class UserQuery(Base):
    __tablename__ = "user_queries"
    id = Column(Integer, primary_key=True, autoincrement=True)
    query_text = Column(Text, nullable=False)
    location = Column(String(100))
    travel_date = Column(String(50))
    days = Column(Integer)
    preferences = Column(String(255))
    created_at = Column(TIMESTAMP, default=datetime.now)

# 2. 推荐结果表（和你的SQL完全对应）
class TravelRecommendation(Base):
    __tablename__ = "travel_recommendations"
    id = Column(Integer, primary_key=True, autoincrement=True)
    query_id = Column(Integer, ForeignKey("user_queries.id"))
    weather_info = Column(Text)
    poi_info = Column(Text)
    recommendation = Column(Text)
    created_at = Column(TIMESTAMP, default=datetime.now)

# ------------------- 数据操作方法 -------------------
# 新增用户查询
def create_user_query(db: Session, query_text: str, location: str, travel_date: str, days: int, preferences: str):
    db_query = UserQuery(
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

# 新增推荐结果
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

# 查询所有历史记录
def get_history_list(db: Session, skip: int = 0, limit: int = 10):
    return db.query(UserQuery).order_by(UserQuery.created_at.desc()).offset(skip).limit(limit).all()

# 查询单条推荐详情
def get_recommendation_detail(db: Session, query_id: int):
    return db.query(TravelRecommendation).filter(TravelRecommendation.query_id == query_id).first()