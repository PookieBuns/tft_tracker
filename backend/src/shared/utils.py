import re
from typing import Type

from pydantic import AnyUrl, BaseModel

from shared.settings import Settings


def camel_to_snake(camel: str) -> str:
    """Convert CamelCase to snake_case"""
    snake = re.sub(r"(?<!^)(?=[A-Z])", "_", camel).lower()
    return snake


def create_db_url(settings: Settings, driver: str, UrlCls: Type[AnyUrl]) -> str:
    """Create DB URL from settings"""

    class DummyModel(BaseModel):
        url: UrlCls  # type: ignore

    url = AnyUrl.build(
        scheme=driver,
        user=settings.db_user,
        password=settings.db_password,
        host=settings.db_host,
        port=str(settings.db_port),
    )
    DummyModel(url=url)
    return url
