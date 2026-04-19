import requests
key = "6e6f9e6a7394474519ed914c6e18c8c7"
url = f"https://restapi.amap.com/v3/place/text?keywords=景点&city=北京&key={key}"
print(requests.get(url).json())