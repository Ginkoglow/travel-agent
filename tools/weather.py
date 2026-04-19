import requests
from settings import settings

def get_city_weather(city: str, days: int = 3) -> str:
    """
    获取城市天气信息。
    
    Args:
        city (str): 城市名。
        days (int): 获取未来多少天的天气，默认3天。
    
    Returns:
        str: 格式化后的天气信息字符串，如果获取失败则返回错误信息。
    """
    if not settings.HEWEATHER_API_KEY:
        return "❌ 未配置和风天气API密钥"

    url = "https://devapi.qweather.com/v7/weather/3d"
    params = {
        "location": city,
        "key": settings.HEWEATHER_API_KEY
    }
    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        
        if data.get("code") != "200":
            return f"❌ 天气获取失败，错误码：{data.get('code')}"
        
        weather_list = data.get("daily", [])[:days]
        if not weather_list:
            return "❌ 未获取到天气数据"
            
        lines = [f"🌤️ 未来{days}天天气："]
        for day in weather_list:
            lines.append(
                f"{day['fxDate']}: {day['textDay']}, "
                f"气温 {day['tempMin']}~{day['tempMax']}℃"
            )
        return "\n".join(lines)
        
    except requests.exceptions.Timeout:
        return "❌ 请求天气服务超时，请稍后重试"
    except requests.exceptions.RequestException as e:
        print(f"获取天气信息失败: {e}")
        return "❌ 天气服务暂时不可用"
    except Exception as e:
        print(f"获取天气信息时发生未知错误: {e}")
        return "❌ 天气服务异常"