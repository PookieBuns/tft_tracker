from operator import pos

from sqlalchemy import insert, select
from sqlalchemy.dialects import postgresql
from sqlalchemy.ext.asyncio import AsyncConnection

from src.models import (
    Game,
    GameBase,
    GameModel,
    GamePlayer,
    GamePlayerAugment,
    GamePlayerUnit,
    GamePlayerUnitItem,
    Player,
    PlayerBase,
    Augment,
    AugmentBase,
    Unit,
    UnitBase,
    Item,
    ItemBase,
)


async def load_player(conn: AsyncConnection, player: PlayerBase):
    insert_stmt = postgresql.insert(Player).values(**player.dict())
    upsert_stmt = insert_stmt.on_conflict_do_update(
        index_elements=["player_name"],
        set_={
            k: getattr(insert_stmt.excluded, k)
            for k in player.dict()
            if getattr(player, k) is not None
        },
    )
    res = await conn.execute(upsert_stmt)
    return res.inserted_primary_key.id


async def load_game(conn: AsyncConnection, game: GameBase):
    insert_stmt = postgresql.insert(Game).values(**game.dict())
    upsert_stmt = insert_stmt.on_conflict_do_update(
        index_elements=["id"],
        set_={k: getattr(insert_stmt.excluded, k) for k in game.dict() if k != "id"},
    )
    res = await conn.execute(upsert_stmt)
    return res.inserted_primary_key.id


async def load_game_player(
    conn: AsyncConnection, game_id: int, player_id: int, placement: int
):
    insert_stmt = postgresql.insert(GamePlayer).values(
        game_id=game_id, player_id=player_id, placement=placement
    )
    upsert_stmt = insert_stmt.on_conflict_do_update(
        index_elements=["game_id", "player_id"],
        set_=dict(placement=placement),
    )
    res = await conn.execute(upsert_stmt)
    return res.inserted_primary_key.id


async def load_augment(conn: AsyncConnection, augment: AugmentBase):
    insert_stmt = postgresql.insert(Augment).values(**augment.dict())
    upsert_stmt = insert_stmt.on_conflict_do_update(
        index_elements=["id"],
        set_={k: getattr(insert_stmt.excluded, k) for k in augment.dict() if k != "id"},
    )
    res = await conn.execute(upsert_stmt)
    return res.inserted_primary_key.id


async def load_game_player_augment(
    conn: AsyncConnection, game_player_id: int, augment_id: int, augment_num: int
):
    insert_stmt = postgresql.insert(GamePlayerAugment).values(
        game_player_id=game_player_id, augment_id=augment_id, augment_num=augment_num
    )
    upsert_stmt = insert_stmt.on_conflict_do_update(
        index_elements=["game_player_id", "augment_num"],
        set_=dict(augment_id=augment_id),
    )
    res = await conn.execute(upsert_stmt)
    return res.inserted_primary_key.id


async def load_unit(conn: AsyncConnection, unit: UnitBase):
    insert_stmt = postgresql.insert(Unit).values(**unit.dict())
    upsert_stmt = insert_stmt.on_conflict_do_update(
        index_elements=["unit_name"],
        set_={k: getattr(insert_stmt.excluded, k) for k in unit.dict()},
    )
    res = await conn.execute(upsert_stmt)
    return res.inserted_primary_key.id


async def load_game_player_unit(
    conn: AsyncConnection, game_player_id: int, unit_id: int, unit_num: int
):
    insert_stmt = postgresql.insert(GamePlayerUnit).values(
        game_player_id=game_player_id, unit_id=unit_id, unit_num=unit_num
    )
    upsert_stmt = insert_stmt.on_conflict_do_update(
        index_elements=["game_player_id", "unit_num"], set_=dict(unit_id=unit_id)
    )
    res = await conn.execute(upsert_stmt)
    return res.inserted_primary_key.id


async def load_item(conn: AsyncConnection, item: ItemBase):
    insert_stmt = postgresql.insert(Item).values(**item.dict())
    upsert_stmt = insert_stmt.on_conflict_do_update(
        index_elements=["item_name"],
        set_={k: getattr(insert_stmt.excluded, k) for k in item.dict()},
    )
    res = await conn.execute(upsert_stmt)
    return res.inserted_primary_key.id


async def load_game_player_unit_item(
    conn: AsyncConnection, game_player_unit_id: int, item_id: int, item_num: int
):
    insert_stmt = postgresql.insert(GamePlayerUnitItem).values(
        game_player_unit_id=game_player_unit_id, item_id=item_id, item_num=item_num
    )
    upsert_stmt = insert_stmt.on_conflict_do_update(
        index_elements=["game_player_unit_id", "item_num"], set_=dict(item_id=item_id)
    )
    res = await conn.execute(upsert_stmt)
    return res.inserted_primary_key.id


async def load_game_detail(conn: AsyncConnection, game: GameModel):
    for player_mdl in game.players:
        player = PlayerBase(
            region=game.game.region,
            player_name=player_mdl.summoner_name,
        )
        player_id = await load_player(conn, player)
        game_player_id = await load_game_player(
            conn,
            game_id=game.game.id,
            player_id=player_id,
            placement=player_mdl.placement,
        )
        augments = player_mdl.augments
        for augment_num, augment in enumerate(augments):
            augment_id = await load_augment(conn, augment)
            await load_game_player_augment(
                conn,
                game_player_id=game_player_id,
                augment_id=augment_id,
                augment_num=augment_num,
            )

        units = player_mdl.units
        for unit_num, unit_mdl in enumerate(units):
            unit = UnitBase(
                unit_name=unit_mdl.unit_name,
            )
            unit_id = await load_unit(conn, unit)
            game_player_unit_id = await load_game_player_unit(
                conn, game_player_id=game_player_id, unit_id=unit_id, unit_num=unit_num
            )
            for item_num, item in enumerate(unit_mdl.items):
                item_id = await load_item(conn, item)
                await load_game_player_unit_item(
                    conn,
                    game_player_unit_id=game_player_unit_id,
                    item_id=item_id,
                    item_num=item_num,
                )
