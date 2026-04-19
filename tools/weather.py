import requests
from settings.config import settings

def get_city_weather(city: str, days: int = 3) -> str:
    """获取城市天气信息"""
    if not settings.HEWEATHER_API_KEY:
        return "❌ 未配置和风天气API密钥"
    if not settings.HEWEATHER_API_HOST:
        return "❌ 未配置和风天气专属API Host"

    try:
        # 1. 城市搜索
        geo_url = f"https://{settings.HEWEATHER_API_HOST}/v2/city/lookup"
        geo_params = {"location": city, "key": settings.HEWEATHER_API_KEY}
        geo_resp = requests.get(geo_url, params=geo_params, timeout=10)
        geo_resp.raise_for_status()
        geo_data = geo_resp.json()

        if geo_data.get("code") != "200":
            return f"❌ 城市查询失败，错误码：{geo_data.get('code')}"

        locations = geo_data.get("location", [])
        if not locations:
            return f"❌ 未找到城市：{city}"
        location_id = locations[0]["id"]

        # 2. 获取天气
        weather_url = f"https://{settings.HEWEATHER_API_HOST}/v7/weather/{days}d"
        weather_params = {"location": location_id, "key": settings.HEWEATHER_API_KEY}
        weather_resp = requests.get(weather_url, params=weather_params, timeout=10)
        weather_resp.raise_for_status()
        weather_data = weather_resp.json()

        if weather_data.get("code") != "200":
            return f"❌ 天气获取失败，错误码：{weather_data.get('code')}"

        daily = weather_data.get("daily", [])
        if not daily:
            return "❌ 未获取到天气数据"

        lines = [f"🌤️ {city} 未来{days}天天气："]
        for day in daily:
            lines.append(
                f"{day['fxDate']}: {day['textDay']}, "
                f"气温 {day['tempMin']}~{day['tempMax']}℃"
            )
        return "\n".join(lines)

    except requests.exceptions.Timeout:
        return "❌ 请求天气服务超时"
    except requests.exceptions.RequestException as e:
        return f"❌ 网络请求异常：{e}"
    except Exception as e:
        return f"❌ 未知错误：{e}"