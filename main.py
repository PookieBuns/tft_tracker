import asyncio
from typing import Callable
from loguru import logger
import typer
from src.settings import settings
from src.handler.worker import sync_players, sync_games
from sqlalchemy.ext.asyncio import create_async_engine
from src.handler.loader import load_augment_cache, load_unit_cache, load_item_cache

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
