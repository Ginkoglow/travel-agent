import json
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate

from settings import settings
from tools.weather import get_city_weather
from tools.poi import get_poi_info
from agent.prompts import PARSE_PROMPT, TRAVEL_PLAN_PROMPT

llm = ChatOpenAI(
    api_key=settings.LLM_API_KEY,
    model=settings.LLM_MODEL,
    temperature=0.7
)

class TravelAgent:
    def __init__(self):
        self.llm = llm

    def parse_info(self, user_query: str) -> dict:
        prompt = PromptTemplate(template=PARSE_PROMPT, input_variables=["user_query"])
        chain = prompt | self.llm
        result = chain.invoke({"user_query": user_query})
        try:
            return json.loads(result.content)
        except:
            return {"location": "", "travel_date": "", "days": 0, "preferences": ""}

    def generate_travel_plan(self, parsed_data: dict) -> tuple:
        """返回 (weather_info, poi_info, plan_text)"""
        location = parsed_data.get("location", "")
        days = parsed_data.get("days", 3)
        travel_date = parsed_data.get("travel_date", "")
        preferences = parsed_data.get("preferences", "")

        weather_info = get_city_weather(location)
        poi_info = get_poi_info(location)

        prompt = PromptTemplate(
            template=TRAVEL_PLAN_PROMPT,
            input_variables=["location", "days", "travel_date", "preferences", "weather", "poi_info"]
        )
        chain = prompt | self.llm
        plan_result = chain.invoke({
            "location": location,
            "days": days,
            "travel_date": travel_date,
            "preferences": preferences,
            "weather": weather_info,
            "poi_info": poi_info
        })
        return weather_info, poi_info, plan_result.content

    def chat(self, user_query: str) -> str:
        """兼容旧调用，仅返回计划文本"""
        parsed = self.parse_info(user_query)
        _, _, plan = self.generate_travel_plan(parsed)
        return plan