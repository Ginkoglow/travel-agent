import requests
from datetime import datetime
from settings.config import settings

def get_city_weather(city: str, days: int = 3) -> str:
    """
    使用高德地图 API 获取城市未来几天的天气信息（不含当天）。
    """
    if not settings.AMAP_API_KEY:
        return "❌ 未配置高德地图API密钥"

    try:
        # 1. 地理编码：城市名 -> adcode
        geo_url = "https://restapi.amap.com/v3/geocode/geo"
        geo_params = {
            "address": city,
            "key": settings.AMAP_API_KEY
        }
        geo_resp = requests.get(geo_url, params=geo_params, timeout=10)
        geo_resp.raise_for_status()
        geo_data = geo_resp.json()

        if geo_data.get("status") != "1" or not geo_data.get("geocodes"):
            return f"❌ 未找到城市：{city}"

        adcode = geo_data["geocodes"][0]["adcode"]

        # 2. 查询天气（extensions=all 返回预报）
        weather_url = "https://restapi.amap.com/v3/weather/weatherInfo"
        weather_params = {
            "city": adcode,
            "key": settings.AMAP_API_KEY,
            "extensions": "all"
        }
        weather_resp = requests.get(weather_url, params=weather_params, timeout=10)
        weather_resp.raise_for_status()
        weather_data = weather_resp.json()

        if weather_data.get("status") != "1":
            return f"❌ 天气获取失败：{weather_data.get('info')}"

        forecasts = weather_data.get("forecasts", [])
        if not forecasts:
            return "❌ 未获取到天气数据"

        casts = forecasts[0].get("casts", [])
        if not casts:
            return "❌ 无天气预报数据"

        # 3. 获取今天的日期（格式 YYYY-MM-DD）
        today_str = datetime.now().strftime("%Y-%m-%d")

        # 4. 过滤掉当天，只保留未来日期
        future_casts = [day for day in casts if day["date"] > today_str]

        # 5. 取前 days 条
        future_casts = future_casts[:days]

        if not future_casts:
            return "❌ 没有未来天气预报数据"

        lines = [f"🌤️ {city} 未来{len(future_casts)}天天气："]
        for day in future_casts:
            day_weather = day['dayweather']
            night_weather = day['nightweather']
            if day_weather == night_weather:
                weather_desc = day_weather
            else:
                weather_desc = f"{day_weather}转{night_weather}"
            lines.append(
                f"{day['date']}: {weather_desc}，"
                f"气温 {day['nighttemp']}~{day['daytemp']}℃"
            )
        return "\n".join(lines)

    except requests.exceptions.Timeout:
        return "❌ 请求天气服务超时"
    except requests.exceptions.RequestException as e:
        return f"❌ 网络请求异常：{e}"
    except Exception as e:
        return f"❌ 未知错误：{e}"