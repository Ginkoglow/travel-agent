import requests
from settings.config import settings

def get_location_id(city_name: str):
    url = "https://geoapi.qweather.com/v2/city/lookup"
    params = {
        "location": city_name,
        "range": "cn",
        "number": 1,
        "key": settings.HEWEATHER_API_KEY
    }
    try:
        resp = requests.get(url, params=params, timeout=10)
        data = resp.json()
        if data.get("code") == "200" and data.get("location"):
            return data["location"][0]["id"]
    except Exception as e:
        print("获取城市ID失败:", e)
    return None

def get_city_weather(city: str):
    city_id = get_location_id(city)
    if not city_id:
        return "无法获取城市信息"

    url = "https://devapi.qweather.com/v7/weather/3d"
    params = {
        "location": city_id,
        "key": settings.HEWEATHER_API_KEY
    }

    try:
        resp = requests.get(url, params=params, timeout=10)
        data = resp.json()
        if data.get("code") != "200":
            return "天气获取失败"

        lines = ["未来三天天气："]
        for day in data["daily"]:
            lines.append(f"{day['fxDate']} {day['textDay']} {day['tempMin']}~{day['tempMax']}℃")
        return "\n".join(lines)
    except:
        return "天气服务异常"