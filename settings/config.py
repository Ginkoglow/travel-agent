from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

load_dotenv()

class Settings(BaseSettings):
    # MySQL配置
    DB_USER: str = os.getenv("DB_USER")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD")
    DB_HOST: str = os.getenv("DB_HOST")
    DB_PORT: int = int(os.getenv("DB_PORT"))
    DB_NAME: str = os.getenv("DB_NAME")

    # 第三方API
    AMAP_API_KEY: str = os.getenv("AMAP_API_KEY")
    HEWEATHER_API_KEY: str = os.getenv("HEWEATHER_API_KEY")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY")

    # AI模型配置
    AI_MODEL: str = "gpt-3.5-turbo"

# 单例配置
settings = Settings()