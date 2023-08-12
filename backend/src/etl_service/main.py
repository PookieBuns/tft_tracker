import asyncio
from typing import Callable

import typer
from loguru import logger
from sqlalchemy.ext.asyncio import create_async_engine

from etl_service.core.loader import load_augment_cache, load_item_cache, load_unit_cache
from etl_service.core.worker import sync_games, sync_players
from shared.settings import settings

DB_URL = (
    "postgresql+asyncpg://"
    f"{settings.db_user}:{settings.db_password}@"
    f"{settings.db_host}:{settings.db_port}/"
    f"{settings.db_name}"
)


async def main(
    sync_function: Callable, batch_size: int = 10, run_forever: bool = False
):
    engine = create_async_engine(DB_URL)
    async with engine.begin() as conn:
        await load_augment_cache(conn)
        await load_unit_cache(conn)
        await load_item_cache(conn)
    if not run_forever:
        await sync_function(engine, batch_size=batch_size)
        return
    while True:
        try:
            await sync_function(engine, batch_size=batch_size)
        except Exception as e:
            logger.exception(e)


app = typer.Typer()


@app.command()
def games(batch_size: int = 10, run_forever: bool = False):
    asyncio.run(main(sync_games, batch_size=batch_size, run_forever=run_forever))


@app.command()
def players(batch_size: int = 10, run_forever: bool = False):
    asyncio.run(main(sync_players, batch_size=batch_size, run_forever=run_forever))


if __name__ == "__main__":
    app()
