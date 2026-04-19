import requests
from settings.config import settings

def get_poi_info(city: str) -> str:
    """获取景点、美食、酒店信息，支持城市名或区名"""
    if not settings.AMAP_API_KEY or not city:
        return "暂无推荐数据，请尝试使用更具体的城市名"

    types = ["景点", "美食", "酒店"]
    result = []
    found_any = False

    for t in types:
        url = "https://restapi.amap.com/v3/place/text"
        params = {
            "keywords": t,
            "city": city,
            "key": settings.AMAP_API_KEY,
            "offset": 5,
            "output": "json"
        }
        try:
            res = requests.get(url, params=params, timeout=10)
            data = res.json()
            if data.get("status") == "1" and data.get("pois"):
                pois = data["pois"]
                names = [p["name"] for p in pois[:5]]
                result.append(f"【{t}】：{'、'.join(names)}")
                found_any = True
            else:
                result.append(f"【{t}】：未找到相关信息")
        except Exception as e:
            result.append(f"【{t}】：查询失败")

    if not found_any:
        return f"抱歉，未能获取到 {city} 的详细推荐信息，建议您使用更具体的城市名或地标名再次查询。"

    return "\n".join(result)