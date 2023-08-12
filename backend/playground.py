import asyncio
import sys
from pathlib import Path

from pydantic import PostgresDsn

sys.path.append(str(Path(__file__).parents[2]))

from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from shared.models import Player
from shared.settings import settings
from shared.utils import create_db_url


async def main():
    db_url = create_db_url(
        settings=settings, driver="postgresql+asyncpg", UrlCls=PostgresDsn
    )
    engine = create_async_engine(db_url, echo=True)
    async with AsyncSession(engine) as session:
        stmt = select(Player).limit(10)
        results = await session.exec(stmt)
        a = await session.get(Player)
        print(a)
        for result in results:
            print(result)


if __name__ == "__main__":
    asyncio.run(main())
