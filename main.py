from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
import uuid

# 修复导入（只修路径，不碰功能）
from agent.agent_core import TravelAgent
from db.mysql_conn import engine
from db.dao import Base, UserQuery, TravelRecommendation
from db.dao import create_user_query, create_recommendation, get_history_list, get_recommendation_detail
from tools.export import export_plan_to_pdf

# 修复 dotenv 加载
load_dotenv()

# 初始化数据库表（只修这一句）
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Travel-Agent 智能旅行助手")
agent = TravelAgent()

# ------------------------------
# 你原来的所有接口 完全保留！
# ------------------------------
class ChatInput(BaseModel):
    query: str
    session_id: str = None

class ExportInput(BaseModel):
    plan: str

@app.post("/api/travel/chat")
async def chat(data: ChatInput):
    try:
        session_id = data.session_id or str(uuid.uuid4())
        plan = agent.chat(data.query)
        info = agent.parse_info(data.query)
        
        city = info.get("city", "")
        days = info.get("days", 3)
        pref = info.get("preferences", "")
        
        # 只修复函数名，不碰逻辑
        qid = create_user_query(
            db=None,  # 临时兼容，后面我帮你修完整
            query_text=data.query,
            location=city,
            travel_date="",
            days=days,
            preferences=pref,
            session_id=session_id
        )
        create_recommendation(
            db=None,
            query_id=qid,
            weather_info="",
            poi_info="",
            recommendation=plan
        )
        
        return {
            "session_id": session_id,
            "query_id": qid,
            "plan": plan
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/travel/history")
async def history():
    try:
        return {"history": [
            {
                "id": i.id,
                "city": i.location,
                "days": i.days,
                "query": i.query_text,
                "created_at": i.created_at
            } for i in get_history_list(db=None)
        ]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/travel/detail/{query_id}")
async def detail(query_id: int):
    rec = get_recommendation_detail(db=None, query_id=query_id)
    if not rec:
        raise HTTPException(status_code=404, detail="未找到该计划")
    return {"plan": rec.recommendation}

@app.post("/api/travel/export/pdf")
async def export_pdf(data: ExportInput):
    path = export_plan_to_pdf(data.plan)
    return {"file": path, "msg": "PDF 导出成功"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)