"""从 .env 加载应用配置，所有可调参数集中管理，不硬编码。"""

from functools import lru_cache

from pydantic_settings import BaseSettings


class AppSettings(BaseSettings):
    """应用全局配置，自动从 .env 读取同名变量。"""

    app_title: str = "智能旅行助手 API"
    app_version: str = "0.1.0"
    app_description: str = "智能旅行规划助手后端服务，提供行程规划与编辑能力"

    default_currency: str = "CNY"
    default_plan_version: int = 1

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


@lru_cache
def get_settings() -> AppSettings:
    return AppSettings()
