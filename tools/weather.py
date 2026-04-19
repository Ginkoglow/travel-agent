import requests
from settings.config import settings

# def get_location_id(city_name: str):
#     url = "https://geoapi.qweather.com/v2/city/lookup"
#     params = {
#         "location": city_name,
#         "range": "cn",
#         "number": 1,
#         "key": settings.HEWEATHER_API_KEY
#     }
#     try:
#         resp = requests.get(url, params=params, timeout=10)
#         resp.raise_for_status()
#         data = resp.json()
#         if data.get("code") == "200" and data.get("location"):
#             return data["location"][0]["id"]
#         else:
#             print(f"GeoAPI返回错误，code: {data.get('code')}, 消息: {data.get('message')}")
#             return None
#     except Exception as e:
#         print("获取城市ID失败:", e)
#         return None

def get_city_weather(city: str, days: int = 3):
    # 免费版Key直接用城市名调用天气接口，绕过GeoAPI
    url = "https://devapi.qweather.com/v7/weather/3d"
    params = {
        "location": city,  # 直接填中文城市名，如"成都"
        "key": settings.HEWEATHER_API_KEY
    }

    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        if data.get("code") != "200":
            return f"天气获取失败，错误码：{data.get('code')}"

        weather_list = data["daily"][:days]
        lines = [f"未来{days}天天气："]
        for day in weather_list:
            lines.append(f"{day['fxDate']} {day['textDay']} {day['tempMin']}~{day['tempMax']}℃")
        return "\n".join(lines)
    except Exception as e:
        print("获取天气信息失败:", e)
        return "天气服务异常"