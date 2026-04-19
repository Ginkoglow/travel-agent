#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Travel Agent 终端交互机器人
支持多轮对话、流式输出、PDF导出、数据库保存。
"""

import sys
import traceback
from agent.agent_core import TravelAgent
from db.dao import create_user_query, create_recommendation
from db.mysql_conn import SessionLocal
from langchain_core.callbacks import BaseCallbackHandler
from tools.export import export_plan_to_pdf


class StreamHandler(BaseCallbackHandler):
    """流式输出回调处理器"""
    def __init__(self):
        self.text = ""

    def on_llm_new_token(self, token: str, **kwargs) -> None:
        sys.stdout.write(token)
        sys.stdout.flush()
        self.text += token


class TerminalBot:
    def __init__(self):
        self.agent = TravelAgent()
        self.db = SessionLocal()
        self.last_plan = None           # 最近一次旅行计划（用于导出PDF）
        self.history = []               # 对话历史，格式：[{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]

    def _save_plan_to_db(self, user_query: str, parsed: dict, weather: str, poi: str, plan: str):
        """仅保存旅行计划相关记录到数据库"""
        try:
            q = create_user_query(
                db=self.db,
                query_text=user_query,
                location=parsed.get("location", ""),
                travel_date=parsed.get("travel_date", ""),
                days=parsed.get("days", 3),
                preferences=parsed.get("preferences", "")
            )
            create_recommendation(
                db=self.db,
                query_id=q.id,
                weather_info=weather,
                poi_info=poi,
                recommendation=plan
            )
        except Exception as e:
            print(f"\n⚠️ 数据库保存失败: {e}")

    def run(self):
        print("=" * 60)
        print("✈️  欢迎使用 Travel Agent 终端助手！")
        print("=" * 60)
        print("您可以：查询天气、推荐景点美食、制定旅行计划，也可以随便聊天～")
        print("输入 'quit' 退出，输入 'export pdf' 导出上一次的旅行计划")
        print("=" * 60)

        while True:
            try:
                user_input = input("\n👤 你: ").strip()
                if user_input.lower() in ["quit", "exit"]:
                    print("👋 再见！")
                    break
                if user_input.lower() == "export pdf":
                    if self.last_plan:
                        path = export_plan_to_pdf(self.last_plan["plan"])
                        print(f"✅ PDF已导出至：{path}")
                    else:
                        print("❌ 暂无旅行计划可导出")
                    continue
                if not user_input:
                    continue

                # 将用户消息加入历史
                self.history.append({"role": "user", "content": user_input})

                # 流式输出回调
                stream_handler = StreamHandler()
                print("🤖 Agent: ", end="", flush=True)

                # 调用核心方法，传入完整历史
                result = self.agent.chat_with_tools(self.history, stream_handler)

                # 处理返回值
                if isinstance(result, tuple):
                    # 旅行计划返回元组 (plan_text, weather, poi)
                    plan_text, weather, poi = result
                    print()  # 流式输出已完成，补一个换行

                    # 解析旅行信息（带历史上下文）
                    parsed = self.agent.parse_info_with_history(self.history)

                    print(f"\n📅 出行日期：{parsed.get('travel_date', '未指定')}")
                    print(f"\n📌 天气参考:\n{weather}")
                    print(f"\n📍 推荐地点:\n{poi}")

                    # 保存到数据库
                    self._save_plan_to_db(user_input, parsed, weather, poi, plan_text)

                    # 将助手回复（计划文本）加入历史
                    self.history.append({"role": "assistant", "content": plan_text})

                    # 记录最近计划供导出
                    self.last_plan = {"plan": plan_text, "weather": weather, "poi": poi}

                    # 提示导出
                    print("\n💡 提示：输入 'export pdf' 可将本次旅行计划导出为 PDF 文件。")
                else:
                    # 普通文本回复
                    print()  # 流式输出已完成，换行
                    self.history.append({"role": "assistant", "content": result})

            except KeyboardInterrupt:
                print("\n\n👋 程序被中断，退出。")
                break
            except Exception as e:
                print(f"\n❌ 发生错误: {e}")
                traceback.print_exc()

        self.db.close()


if __name__ == "__main__":
    bot = TerminalBot()
    bot.run()