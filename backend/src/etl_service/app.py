from urllib.parse import quote_plus

from fastapi import FastAPI
from pydantic import PostgresDsn
from sqlalchemy.ext.asyncio import create_async_engine

from etl_service.core.loader import load_augment_cache, load_item_cache, load_unit_cache
from etl_service.core.worker import sync_games, sync_players
from shared.models import Player, PlayerRequest
from shared.settings import settings
from shared.utils import create_db_url

DB_URL = create_db_url(settings, "postgresql+asyncpg", PostgresDsn)


app = FastAPI()


@app.on_event("startup")
async def startup_event():
    engine = create_async_engine(DB_URL)
    async with engine.begin() as conn:
        await load_item_cache(conn)
        await load_unit_cache(conn)
        await load_augment_cache(conn)


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/etl/run")
async def run_etl(player: PlayerRequest):
    assert player.region == "NA", "Only support NA region"
    player.player_name = player.player_name.lower()
    player.player_name = quote_plus(player.player_name)
    engine = create_async_engine(DB_URL)
    game_players = await sync_players(engine, [Player(**player.dict())])
    for _, games in game_players:
        await sync_games(engine, games)
    return {"status": "ok"}
