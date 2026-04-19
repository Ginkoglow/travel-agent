#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Travel Agent 终端交互机器人
在终端上实现完整的旅行规划功能，支持多轮对话。
"""

import sys
import traceback
from agent.agent_core import TravelAgent
from db.dao import create_user_query, create_recommendation
from db.mysql_conn import SessionLocal

class TerminalBot:
    def __init__(self):
        self.agent = TravelAgent()
        self.db = SessionLocal()

    def _save_to_db(self, user_query: str, parsed_data: dict, weather: str, poi: str, plan: str):
        try:
            query_record = create_user_query(
                db=self.db,
                query_text=user_query,
                location=parsed_data.get("location", ""),
                travel_date=parsed_data.get("travel_date", ""),
                days=parsed_data.get("days", 3),
                preferences=parsed_data.get("preferences", "")
            )
            create_recommendation(
                db=self.db,
                query_id=query_record.id,
                weather_info=weather,
                poi_info=poi,
                recommendation=plan
            )
        except Exception as e:
            print(f"⚠️ 数据库保存失败: {e}")

    def run(self):
        print("=" * 60)
        print("✈️  欢迎使用 Travel Agent 终端助手！")
        print("=" * 60)
        print("输入你的旅行需求 (例如: '我想去北京玩3天，喜欢历史古迹')\n输入 'quit' 或 'exit' 退出程序")
        print("=" * 60)

        while True:
            try:
                user_input = input("\n👤 你: ").strip()
                if user_input.lower() in ["quit", "exit"]:
                    print("👋 再见！")
                    break
                if not user_input:
                    continue

                print("🤔 Agent 正在规划中...")
                parsed_data = self.agent.parse_info(user_input)
                print(f"📋 解析结果: {parsed_data}")
                weather_info, poi_info, plan = self.agent.generate_travel_plan(parsed_data)
                
                print(f"\n🌍 旅行规划:\n{plan}")
                print(f"\n📌 天气参考:\n{weather_info}")
                print(f"\n📍 推荐地点:\n{poi_info}")

                self._save_to_db(user_input, parsed_data, weather_info, poi_info, plan)

            except KeyboardInterrupt:
                print("\n\n👋 程序被中断，退出。")
                break
            except Exception as e:
                print(f"❌ 发生错误: {e}")
                traceback.print_exc()
        self.db.close()

if __name__ == "__main__":
    bot = TerminalBot()
    bot.run()