import asyncio
from datetime import datetime, timedelta

from aiohttp import ClientSession
from loguru import logger
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlmodel import col

from etl_service.core.extractor import (
    get_game_data,
    get_profile_data,
    update_profile_data,
)
from etl_service.core.loader import load_game, load_game_detail, load_player
from etl_service.core.scheduler import (
    get_need_dispatch_games,
    get_need_dispatch_players,
)
from etl_service.core.transformer import (
    get_update_url,
    transform_game_data,
    transform_profile_data,
)
from shared.models import Game, GameBase, GameModel, Player, PlayerBase


async def sync_games(engine: AsyncEngine, games: list[Game]):
    async with ClientSession() as session:
        coros = [
            get_game_data(session, game.region, game.origin_player_name, game.id)
            for game in games
        ]
        game_datas = await asyncio.gather(*coros)
    logger.info("Done Extract Data")
    game_mdls: list[GameModel] = []
    for game, game_data in zip(games, game_datas):
        game_players = transform_game_data(game_data)
        game_mdl = GameModel(game=game, players=game_players)
        game_mdls.append(game_mdl)
    logger.info("Done Transform Data")
    for game_mdl in game_mdls:
        logger.info(f"Load game {game_mdl.game.id}")
        async with engine.begin() as conn:
            await load_game_detail(conn, game_mdl)
    logger.info("Done Load Data")
    logger.success("Done sync games")


async def get_and_sync_games(engine: AsyncEngine, batch_size=10):
    logger.info("Start sync games")
    games = await get_need_dispatch_games(batch_size)
    logger.info(f"Get {len(games)} games")
    await sync_games(engine, games)


async def get_latest_profile_data(player: Player, session) -> str | None:
    try:
        profile_data = await get_profile_data(
            session, player.region, player.player_name
        )
        update_url = get_update_url(profile_data, player.player_name)
        await update_profile_data(session, update_url)
        profile_data = await get_profile_data(
            session, player.region, player.player_name
        )
        return profile_data
    except Exception as e:
        logger.error(f"Error when get profile data: {e}")
        return None


async def sync_players(engine: AsyncEngine, players: list[Player]):
    async with ClientSession() as session:
        coros = [get_latest_profile_data(player, session) for player in players]
        profile_datas = await asyncio.gather(*coros)
    logger.info("Done Extract Data")
    player_games: list[tuple[PlayerBase, list[GameBase]]] = []
    for db_player, profile_data in zip(players, profile_datas):
        if not profile_data:
            continue
        player, games = transform_profile_data(profile_data, db_player.player_name)
        player_games.append((player, games))
    logger.info("Done Transform Data")
    async with engine.begin() as conn:
        player_ids = []
        for player, games in player_games:
            logger.info(f"Load player {player.player_name}")
            player_id = await load_player(conn, player)
            player_ids.append(player_id)
            for game in games:
                logger.info(f"Load game {game.id}")
                await load_game(conn, game)
        await conn.execute(
            update(Player)
            .where(col(Player.id).in_(player_ids))
            .values(
                last_sync_time=datetime.utcnow(),
                next_sync_time=datetime.utcnow() + timedelta(days=1),
            )
        )
    logger.info("Done Load Data")
    logger.success("Done sync players")
    return player_games


async def get_and_sync_players(engine: AsyncEngine, batch_size=10):
    logger.info("Start sync players")
    players = await get_need_dispatch_players(batch_size)
    logger.info(f"Get {len(players)} players")
    await sync_players(engine, players)
