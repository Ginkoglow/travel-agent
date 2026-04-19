import requests
from settings.config import settings

def get_poi_info(city: str) -> str:
    """获取景点、美食、酒店信息"""
    if not settings.AMAP_API_KEY or not city:
        return "未获取到当地景点/美食/酒店信息"

    types = ["景点", "美食", "酒店"]
    result = []

    for t in types:
        url = "https://restapi.amap.com/v3/place/text"
        params = {
            "keywords": t,
            "city": city,
            "key": settings.AMAP_API_KEY,
            "offset": 3,
            "output": "json"
        }
        try:
            res = requests.get(url, params=params, timeout=10)
            data = res.json()
            if data["status"] == "1":
                pois = data["pois"]
                names = [p["name"] for p in pois]
                result.append(f"【{t}】：{'、'.join(names)}")
        except:
            continue

    return "\n".join(result) if result else "POI信息查询失败"