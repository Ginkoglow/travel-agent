from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
import uuid

from agent.agent_core import TravelAgent
from db.mysql_conn import init_db, save_query, save_plan, get_history, get_plan_by_query_id
from tools.export import export_plan_to_pdf

load_dotenv()
app = FastAPI(title="Travel-Agent 智能旅行助手")
agent = TravelAgent()
init_db()

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
        
        qid = save_query(session_id, data.query, city, days, pref)
        save_plan(qid, plan)
        
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
                "city": i.city,
                "days": i.days,
                "query": i.query,
                "created_at": i.created_at
            } for i in get_history()
        ]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/travel/detail/{query_id}")
async def detail(query_id: int):
    plan = get_plan_by_query_id(query_id)
    if not plan:
        raise HTTPException(status_code=404, detail="未找到该计划")
    return {"plan": plan}

@app.post("/api/travel/export/pdf")
async def export_pdf(data: ExportInput):
    path = export_plan_to_pdf(data.plan)
    return {"file": path, "msg": "PDF 导出成功"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)