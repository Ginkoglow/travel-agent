import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # LLM 配置
    LLM_BASE_URL: str = os.getenv("LLM_BASE_URL")
    LLM_API_KEY: str = os.getenv("LLM_API_KEY")
    LLM_MODEL: str = os.getenv("LLM_MODEL")

    # 数据库配置
    DB_HOST: str = os.getenv("DB_HOST")
    DB_PORT: int = int(os.getenv("DB_PORT", 3306))
    DB_USER: str = os.getenv("DB_USER")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD")
    DB_NAME: str = os.getenv("DB_NAME")

    # 高德地图 API（同时用于 POI 和天气）
    AMAP_API_KEY: str = os.getenv("AMAP_API_KEY")

settings = Settings()