import requests
from settings.config import settings

def get_poi_info(city: str) -> str:
    """获取景点、美食、酒店信息"""
    if not settings.AMAP_API_KEY or not city:
        return "❌ 未获取到当地景点/美食/酒店信息"
    
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
            if data.get("status") == "1" and data.get("pois"):
                pois = data["pois"]
                names = [p["name"] for p in pois[:5]]  # 每个类别取前5个
                result.append(f"【{t}】：{'、'.join(names)}")
            else:
                result.append(f"【{t}】：未找到相关信息")
        except Exception as e:
            print(f"获取POI信息失败 ({t}): {e}")
            result.append(f"【{t}】：查询失败")
    
    return "\n".join(result) if result else "❌ POI信息查询失败"