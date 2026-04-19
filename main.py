from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from dotenv import load_dotenv
import uuid
from sqlalchemy.orm import Session

from agent.agent_core import TravelAgent
from db.mysql_conn import engine, get_db
from db.dao import Base, create_user_query, create_recommendation, get_history_list, get_recommendation_detail
from tools.export import export_plan_to_pdf

load_dotenv()
app = FastAPI(title="Travel-Agent 智能旅行助手")
agent = TravelAgent()
Base.metadata.create_all(bind=engine)

class ChatInput(BaseModel):
    query: str
    session_id: str = None

class ExportInput(BaseModel):
    plan: str

@app.post("/api/travel/chat")
async def chat(data: ChatInput, db: Session = Depends(get_db)):
    try:
        session_id = data.session_id or str(uuid.uuid4())
        result = agent.chat_with_tools(data.query)
        # 判断是否为旅行计划（返回元组）
        if isinstance(result, tuple):
            plan_text, weather, poi = result
            parsed = agent.parse_info(data.query)
            qid = create_user_query(
                db, data.query,
                parsed.get("location", ""),
                parsed.get("travel_date", ""),
                parsed.get("days", 3),
                parsed.get("preferences", "")
            )
            create_recommendation(db, qid, weather, poi, plan_text)
            return {
                "session_id": session_id,
                "query_id": qid,
                "plan": plan_text,
                "weather": weather,
                "poi_info": poi
            }
        else:
            # 普通回复，不存入数据库（或可存对话历史，按需扩展）
            return {
                "session_id": session_id,
                "reply": result
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/travel/history")
async def history(db: Session = Depends(get_db)):
    try:
        return {"history": [
            {
                "id": i.id,
                "query": i.query_text,
                "location": i.location,
                "travel_date": i.travel_date,
                "days": i.days,
                "created_at": i.created_at
            } for i in get_history_list(db)
        ]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/travel/detail/{query_id}")
async def detail(query_id: int, db: Session = Depends(get_db)):
    rec = get_recommendation_detail(db, query_id)
    if not rec:
        raise HTTPException(status_code=404, detail="未找到该计划")
    return {
        "plan": rec.recommendation,
        "weather": rec.weather_info,
        "poi_info": rec.poi_info
    }

@app.post("/api/travel/export/pdf")
async def export_pdf(data: ExportInput):
    path = export_plan_to_pdf(data.plan)
    return {"file": path, "msg": "PDF 导出成功"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)