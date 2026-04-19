import json
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
        """
        通过本地关键词判断是否为无需工具的简单闲聊。
        避免对「你好」「谢谢」等简单问题再调用一次 LLM 做意图分类，大幅提升响应速度。
        """
        simple_keywords = [
            "你好", "嗨", "hello", "hi", "早上好", "晚上好", "下午好", "再见", "拜拜",
            "谢谢", "你是谁", "你能做什么", "帮助", "help", "笑话", "故事", "讲个",
            "what can you do", "who are you", "good morning", "good evening",
        ]
        query_lower = user_query.lower()
        for kw in simple_keywords:
            if kw in query_lower:
                return True

        # 如果输入长度很短，且不含任何旅行相关词，也视为简单闲聊
        travel_words = ["天气", "景点", "美食", "酒店", "旅行", "攻略", "玩", "游", "行程", "推荐", "规划"]
        if len(user_query) < 15 and not any(w in user_query for w in travel_words):
            return True

        return False

    def _extract_city(self, user_query: str) -> str:
        """让 LLM 从用户输入中提取城市名，用于后续工具调用"""
        prompt = PromptTemplate(
            template="从以下句子中提取城市名，只返回城市名，如果没有则返回空字符串：\n{user_query}",
            input_variables=["user_query"]
        )
        chain = prompt | self.llm
        result = chain.invoke({"user_query": user_query})
        return result.content.strip()

    def _get_intent(self, user_query: str) -> str:
        """判断用户意图（weather/poi/plan/chat）"""
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
        """将 dict 列表转换为 LangChain 消息对象列表"""
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
        """解析旅行需求，返回结构化信息（仅在生成旅行计划时使用）"""
        prompt = PromptTemplate(template=PARSE_PROMPT, input_variables=["user_query"])
        chain = prompt | self.llm
        result = chain.invoke({"user_query": user_query})
        try:
            return json.loads(result.content)
        except:
            return {"location": "", "travel_date": "", "days": 3, "preferences": ""}

    def chat_with_tools(self, messages: list, stream_handler: BaseCallbackHandler = None):
        """
        智能对话入口，支持完整对话历史。
        - 对于简单问候，直接交给 LLM 自由回答，无额外延迟。
        - 对于天气/POI 查询，调用工具获取实时数据，再由 LLM 自然回复。
        - 对于明确旅行计划需求，生成结构化攻略并返回 (plan, weather, poi) 元组。
        - 其他问题由 LLM 直接回答。

        messages 格式：[{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]
        返回：如果是旅行计划则返回元组 (plan_text, weather, poi)，否则返回字符串。
        """
        if not messages:
            return "请输入内容。"

        # 最新一条用户消息
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

        # 2. 判断意图（基于最后一条用户消息）
        intent = self._get_intent(last_user_msg)
        config = {"callbacks": [stream_handler]} if stream_handler else {}

        # 3. 根据意图处理
        if intent == "weather":
            city = self._extract_city(last_user_msg)
            if city:
                weather_data = get_city_weather(city)
                # 将天气数据作为系统消息插入历史末尾
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
            # 生成旅行计划（独立任务，但可利用历史中的用户偏好）
            parsed = self.parse_info(last_user_msg)
            location = parsed.get("location", "")
            days = parsed.get("days", 3)
            travel_date = parsed.get("travel_date", "")
            preferences = parsed.get("preferences", "")

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

            # 返回元组，方便外部获取天气、POI 用于存储和展示
            return plan_result.content, weather_data, poi_data

        else:
            # 普通聊天（含情感交流、推理计算等），使用完整历史
            lc_messages = self._convert_to_langchain_messages(messages)
            result = self.llm.invoke(lc_messages, config=config)
            return result.content

    def chat(self, user_query: str) -> str:
        """兼容旧调用的纯文本返回方法（无流式输出，无历史记忆）"""
        result = self.chat_with_tools([{"role": "user", "content": user_query}])
        if isinstance(result, tuple):
            return result[0]  # 仅返回计划文本
        return result