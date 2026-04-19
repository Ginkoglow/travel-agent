import json
from datetime import datetime  # 需要导入
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from settings.config import settings
from tools.weather import get_city_weather
from tools.poi import get_poi_info
from agent.prompts import (
    PARSE_PROMPT,
    TRAVEL_PLAN_PROMPT,
    WEATHER_ENHANCE_PROMPT,
    POI_ENHANCE_PROMPT,
)

# 初始化 LLM（开启流式输出）
llm = ChatOpenAI(
    api_key=settings.LLM_API_KEY,
    base_url=settings.LLM_BASE_URL,
    model=settings.LLM_MODEL,
    temperature=0.7,
    streaming=True,
)


class TravelAgent:
    def __init__(self):
        self.llm = llm

    def _is_simple_chat(self, user_query: str) -> bool:
        simple_keywords = [
            "你好", "嗨", "hello", "hi", "早上好", "晚上好", "下午好", "再见", "拜拜",
            "谢谢", "你是谁", "你能做什么", "帮助", "help", "笑话", "故事", "讲个",
            "what can you do", "who are you", "good morning", "good evening",
        ]
        query_lower = user_query.lower()
        for kw in simple_keywords:
            if kw in query_lower:
                return True
        travel_words = ["天气", "景点", "美食", "酒店", "旅行", "攻略", "玩", "游", "行程", "推荐", "规划"]
        if len(user_query) < 15 and not any(w in user_query for w in travel_words):
            return True
        return False

    def _extract_city(self, user_query: str) -> str:
        prompt = PromptTemplate(
            template="从以下句子中提取城市名，只返回城市名，如果没有则返回空字符串：\n{user_query}",
            input_variables=["user_query"]
        )
        chain = prompt | self.llm
        result = chain.invoke({"user_query": user_query})
        return result.content.strip()

    def _get_intent(self, user_query: str) -> str:
        intent_prompt = PromptTemplate(
            template="""判断用户输入是否需要实时天气数据或地点推荐数据。
- 如果用户询问某个城市的天气（包括温度、下雨、穿衣建议等），返回 "weather"
- 如果用户询问某个城市的景点、美食、酒店推荐，返回 "poi"
- 如果用户明确要求制定旅行计划、行程安排，返回 "plan"
- 其他情况返回 "chat"

请只返回一个单词：weather, poi, plan, chat。

用户输入：{user_query}""",
            input_variables=["user_query"]
        )
        chain = intent_prompt | self.llm
        result = chain.invoke({"user_query": user_query})
        return result.content.strip().lower()

    def _convert_to_langchain_messages(self, messages: list) -> list:
        lc_msgs = []
        for msg in messages:
            role = msg["role"]
            content = msg["content"]
            if role == "user":
                lc_msgs.append(HumanMessage(content=content))
            elif role == "assistant":
                lc_msgs.append(AIMessage(content=content))
            elif role == "system":
                lc_msgs.append(SystemMessage(content=content))
        return lc_msgs

    def parse_info(self, user_query: str) -> dict:
        prompt = PromptTemplate(template=PARSE_PROMPT, input_variables=["user_query"])
        chain = prompt | self.llm
        result = chain.invoke({"user_query": user_query})
        try:
            data = json.loads(result.content)
            data["days"] = int(data.get("days", 0)) if data.get("days") else 0
            return data
        except:
            return {"location": "", "travel_date": "", "days": 0, "preferences": ""}

    def parse_info_with_history(self, messages: list) -> dict:
        """结合历史消息和当前日期提取旅行信息，并将相对日期转换为具体日期"""
        history_text = ""
        for msg in messages:
            history_text += f"{msg['role']}: {msg['content']}\n"
    
        # 获取当前系统日期，格式：2026年4月19日 星期日
        now = datetime.now()
        current_date_str = now.strftime("%Y年%m月%d日 %A")
    
        prompt = PromptTemplate(
            template="""你是一个旅行需求解析助手。请结合以下对话历史和**当前日期**，从用户的最新请求中提取结构化信息。
    如果历史中提到过目的地城市，但最新消息未明确，请使用历史中的城市。
    **重要**：对于旅行日期，如果用户使用相对描述（如“下周末”、“下周”、“五一”、“三天后”），请根据当前日期计算出具体的开始日期，并以 YYYY-MM-DD 格式返回（例如 2026-04-25）。如果用户未提及，则返回空字符串。

    当前日期：{current_date}

    需要提取的字段：
    1. location: 目的地城市（字符串，必须从历史或最新消息中推断）
    2. travel_date: 出行开始日期（字符串，格式 YYYY-MM-DD，若用户提到相对日期请推算，无则为空）
    3. days: 游玩天数（数字，必须严格按照描述提取，例如“两天”=2，未提及则返回0）
    4. preferences: 旅行偏好（自然风光/美食/人文/亲子/小众，多个用逗号分隔，无则为空）

    对话历史：
    {history}

    请严格按照JSON格式返回，不要多余内容。
    返回格式：{{"location":"","travel_date":"","days":0,"preferences":""}}
    """,
            input_variables=["current_date", "history"]
        )
        chain = prompt | self.llm
        result = chain.invoke({"current_date": current_date_str, "history": history_text})
        try:
            data = json.loads(result.content)
            data["days"] = int(data.get("days", 0)) if data.get("days") else 0
            return data
        except:
            return {"location": "", "travel_date": "", "days": 0, "preferences": ""}

    def chat_with_tools(self, messages: list, stream_handler: BaseCallbackHandler = None):
        if not messages:
            return "请输入内容。"

        last_user_msg = ""
        for msg in reversed(messages):
            if msg["role"] == "user":
                last_user_msg = msg["content"]
                break

        # 1. 简单闲聊快速通道
        if self._is_simple_chat(last_user_msg):
            lc_messages = self._convert_to_langchain_messages(messages)
            config = {"callbacks": [stream_handler]} if stream_handler else {}
            result = self.llm.invoke(lc_messages, config=config)
            return result.content

        # 2. 判断意图
        intent = self._get_intent(last_user_msg)
        config = {"callbacks": [stream_handler]} if stream_handler else {}

        # 3. 根据意图处理
        if intent == "weather":
            city = self._extract_city(last_user_msg)
            if city:
                weather_data = get_city_weather(city)
                enhanced_messages = messages.copy()
                enhanced_messages.append({
                    "role": "system",
                    "content": f"实时天气数据：{weather_data}"
                })
                lc_messages = self._convert_to_langchain_messages(enhanced_messages)
                result = self.llm.invoke(lc_messages, config=config)
                return result.content
            else:
                lc_messages = self._convert_to_langchain_messages(messages)
                return self.llm.invoke(lc_messages, config=config).content

        elif intent == "poi":
            city = self._extract_city(last_user_msg)
            if city:
                poi_data = get_poi_info(city)
                enhanced_messages = messages.copy()
                enhanced_messages.append({
                    "role": "system",
                    "content": f"实时推荐数据：{poi_data}"
                })
                lc_messages = self._convert_to_langchain_messages(enhanced_messages)
                result = self.llm.invoke(lc_messages, config=config)
                return result.content
            else:
                lc_messages = self._convert_to_langchain_messages(messages)
                return self.llm.invoke(lc_messages, config=config).content

        elif intent == "plan":
            # 使用历史消息解析，获取城市信息
            parsed = self.parse_info_with_history(messages)
            location = parsed.get("location", "")
            days = parsed.get("days", 0)
            if days <= 0:
                days = 1
            travel_date = parsed.get("travel_date", "")
            preferences = parsed.get("preferences", "")

            if not location:
                return "请告诉我您想去哪个城市旅行？"

            weather_data = get_city_weather(location)
            poi_data = get_poi_info(location)

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
                "weather": weather_data,
                "poi_info": poi_data
            }, config=config)

            return plan_result.content, weather_data, poi_data

        else:
            lc_messages = self._convert_to_langchain_messages(messages)
            result = self.llm.invoke(lc_messages, config=config)
            return result.content

    def chat(self, user_query: str) -> str:
        result = self.chat_with_tools([{"role": "user", "content": user_query}])
        if isinstance(result, tuple):
            return result[0]
        return result