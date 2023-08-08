import asyncio
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


async def main(sync_function, batch_size=10):
    engine = create_async_engine(DB_URL)
    async with engine.begin() as conn:
        await load_augment_cache(conn)
        await load_unit_cache(conn)
        await load_item_cache(conn)
    await sync_function(engine, batch_size=batch_size)


app = typer.Typer()


@app.command()
def games(batch_size: int = 10):
    asyncio.run(main(sync_games, batch_size=batch_size))


@app.command()
def players(batch_size: int = 10):
    asyncio.run(main(sync_players, batch_size=batch_size))


if __name__ == "__main__":
    # print(SQLModel.metadata.tables)
    app()
