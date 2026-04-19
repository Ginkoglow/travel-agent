from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel

# [!] 修正导入路径
from db.mysql_conn import get_db
from db.dao import create_user_query, create_recommendation, get_history_list, get_recommendation_detail
from agent.agent_core import TravelAgent

router = APIRouter(prefix="/api", tags=["旅行助手"])

# 创建 TravelAgent 实例
travel_agent = TravelAgent()

class TravelPlanRequest(BaseModel):
    user_query: str

class TravelPlanResponse(BaseModel):
    code: int
    msg: str
    data: dict

@router.post("/travel/plan", response_model=TravelPlanResponse)
def travel_plan(request: TravelPlanRequest, db: Session = Depends(get_db)):
    user_query = request.user_query
    
    # 1. 解析用户输入
    parsed_data = travel_agent.parse_info(user_query)
    location = parsed_data["location"]
    travel_date = parsed_data["travel_date"]
    days = parsed_data["days"]
    preferences = parsed_data["preferences"]
    
    # 2. 生成旅行计划
    weather_info, poi_info, recommendation = travel_agent.generate_travel_plan(parsed_data)
    
    # 3. 存储到数据库
    user_query_db = create_user_query(db, user_query, location, travel_date, days, preferences)
    create_recommendation(db, user_query_db.id, weather_info, poi_info, recommendation)
    
    return TravelPlanResponse(
        code=200,
        msg="生成成功",
        data={
            "query_id": user_query_db.id,
            "parsed_info": parsed_data,
            "weather": weather_info,
            "poi_info": poi_info,
            "travel_plan": recommendation
        }
    )

@router.get("/history/list")
def history_list(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    data = get_history_list(db, skip, limit)
    return {"code": 200, "msg": "查询成功", "data": data}

@router.get("/history/detail/{query_id}")
def history_detail(query_id: int, db: Session = Depends(get_db)):
    data = get_recommendation_detail(db, query_id)
    return {"code": 200, "msg": "查询成功", "data": data}