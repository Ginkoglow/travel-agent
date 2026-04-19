import sys
import traceback
import os

# 把travel-agent根目录加入Python路径（确保能导入你的所有模块）
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# ========== 严格导入你截图里的核心模块 ==========
try:
    # 导入你的核心Agent逻辑（agent/agent_core.py）
    from agent.agent_core import TravelAgent  # 替换成你agent_core.py里的实际类名
    # 导入你的配置（settings/config.py）
    from settings.config import settings      # 你的配置实例（按你实际变量名改）
    # 导入你的工具函数（tools/下的所有文件）
    from tools.weather import get_weather     # 你的天气工具
    from tools.poi import get_poi_info         # 你的POI工具
    from tools.export import export_plan_to_pdf # 你的导出工具
except ImportError as e:
    print(f"❌ 导入失败（路径完全按你截图）：{e}")
    print("💡 请确认：agent/agent_core.py、settings/config.py、tools/下文件存在")
    sys.exit(1)

def init_agent():
    """初始化你的核心Agent（复用你agent_core.py的逻辑）"""
    try:
        # 按你agent_core.py的实际初始化方式来（比如传配置）
        agent = TravelAgent(config=settings)
        print("✅ 核心Agent初始化成功（复用agent/agent_core.py）")
        print("💡 支持指令：天气查询/POI查询/导出计划（输入'exit/退出'关闭）")
        print("-" * 80)
        return agent
    except Exception as e:
        print(f"❌ Agent初始化失败：{str(e)}")
        traceback.print_exc()  # 终端打印完整报错（不隐藏）
        sys.exit(1)

def handle_user_input(agent, user_input):
    """处理用户输入：调用你agent_core的核心方法 + tools下的工具"""
    try:
        # 调用你agent_core.py里的核心交互方法（比如chat/query）
        # 替换成你agent_core.py里实际的方法名（比如agent.chat(user_input)）
        response = agent.chat(user_input)
        return f"🤖 回复：\n{response}"
    except Exception as e:
        # 原生报错直接输出（包含你agent/tools里的报错）
        error_detail = traceback.format_exc()
        return f"❌ 处理失败：\n错误原因：{str(e)}\n详细栈：\n{error_detail}"

def terminal_chat_loop():
    """纯终端交互循环（无网页/接口，报错直接打终端）"""
    # 初始化你的核心Agent
    agent = init_agent()
    
    while True:
        # 终端获取输入
        user_input = input("\n👉 你: ").strip()
        
        # 退出逻辑
        if user_input.lower() in ["exit", "退出", "q", "quit"]:
            print("👋 终端机器人已退出！")
            break
        
        # 空输入处理
        if not user_input:
            print("⚠️  输入不能为空，请重新输入！")
            continue
        
        # 处理输入并返回结果（全程在终端）
        result = handle_user_input(agent, user_input)
        print(result)

if __name__ == "__main__":
    # 启动终端机器人（仅运行这一个文件即可）
    terminal_chat_loop()