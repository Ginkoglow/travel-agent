import importlib
import traceback

# ===================== 1. 动态导入工具模块（适配travel-agent含短横线的目录名） =====================
# 导出工具（替换成你export.py里的真实函数/类名）
export_module = importlib.import_module("travel-agent.tools.export")
export_data = export_module.export_data  # 若实际是类：export_data = export_module.ExportExcel().run

# POI工具（替换成你poi.py里的真实函数/类名）
poi_module = importlib.import_module("travel-agent.tools.poi")
get_poi_info = poi_module.get_poi_info  # 若实际是类：get_poi_info = poi_module.POISearch().query

# 天气工具（替换成你weather.py里的真实函数/类名）
weather_module = importlib.import_module("travel-agent.tools.weather")
get_weather = weather_module.get_weather  # 若实际是类：get_weather = weather_module.WeatherFetcher().fetch

# ===================== 2. 工具映射表（对齐业务术语） =====================
TOOL_MAPPER = {
    "数据导出": export_data,    # 替换成你实际的指令关键词（比如“导出旅行数据”）
    "景点查询": get_poi_info,   # 替换成你实际的指令关键词（比如“POI搜索”）
    "查天气": get_weather       # 替换成你实际的指令关键词（比如“天气查询”）
}

# ===================== 3. 工具调用处理（对齐参数/异常） =====================
def handle_tool_call(user_input):
    """处理用户指令，调用对应工具"""
    # 遍历工具关键词，匹配指令
    for keyword, tool_func in TOOL_MAPPER.items():
        if keyword in user_input:
            # 提取参数（适配多参数/无参数场景）
            args_str = user_input.replace(keyword, "").strip()
            args = args_str.split() if args_str else []

            # 校验参数（按你的工具实际参数调整）
            if keyword == "景点查询" and len(args) < 2:
                return "⚠️ 景点查询参数错误！示例：景点查询 北京 故宫"
            if keyword == "数据导出" and len(args) > 1:
                return "⚠️ 数据导出参数错误！示例：数据导出 202405 或 数据导出"
            if keyword == "查天气" and len(args) < 1:
                return "⚠️ 查天气参数错误！示例：查天气 上海"

            # 调用工具并捕获异常（对齐工具实际异常类型）
            try:
                # 适配参数传递：无参/单参/多参
                if not args:
                    result = tool_func()
                elif len(args) == 1:
                    result = tool_func(args[0])
                else:
                    result = tool_func(*args)

                # 格式化返回结果（对齐工具返回值类型）
                if isinstance(result, dict):
                    formatted_result = "\n".join([f"  {k}：{v}" for k, v in result.items()])
                elif isinstance(result, list):
                    formatted_result = "\n".join([f"  - {item}" for item in result])
                else:
                    formatted_result = str(result)

                return f"✅ {keyword}成功！结果：\n{formatted_result}"

            # 精准捕获工具自定义异常（替换成你实际的异常类）
            except poi_module.POISearchError as e:
                return f"❌ 景点查询失败：{str(e)}（请检查景点名称是否合法）"
            except weather_module.WeatherFetchError as e:
                return f"❌ 查天气失败：{str(e)}（请检查城市名称）"
            except export_module.ExportError as e:
                return f"❌ 数据导出失败：{str(e)}（请检查导出日期）"
            # 通用异常捕获（网络/格式等）
            except ImportError as e:
                return f"❌ 工具加载失败：{str(e)}（请检查tools目录文件是否存在）"
            except Exception as e:
                return f"❌ 执行失败：{str(e)}\n{traceback.format_exc()[:200]}（异常详情）"

    # 无匹配工具
    return f"❌ 未识别的指令！支持的指令：{', '.join(TOOL_MAPPER.keys())}"

# ===================== 4. 终端交互主逻辑（对齐业务场景） =====================
def main():
    print("="*50)
    print("✅ 旅行代理终端机器人已启动（基于travel-agent/tools工具集）")
    print(f"💡 支持指令：{', '.join(TOOL_MAPPER.keys())}")
    print("💡 示例：景点查询 北京 故宫 | 查天气 上海 | 数据导出 202405")
    print("💡 输入 'exit'/'退出' 关闭机器人")
    print("="*50)

    while True:
        user_input = input("\n请输入指令：").strip()
        # 退出逻辑
        if user_input.lower() in ["exit", "退出"]:
            print("👋 机器人已关闭，再见！")
            break
        # 空输入处理
        if not user_input:
            print("⚠️ 请输入有效指令！")
            continue
        # 处理工具调用
        response = handle_tool_call(user_input)
        print(response)

if __name__ == "__main__":
    main()