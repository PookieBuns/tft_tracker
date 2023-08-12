from typing import Optional

from sqlalchemy import insert, select, update
from sqlalchemy.dialects import postgresql
from sqlalchemy.ext.asyncio import AsyncConnection

from shared.models import (
    Augment,
    AugmentBase,
    Game,
    GameBase,
    GameModel,
    GamePlayer,
    GamePlayerAugment,
    GamePlayerUnit,
    GamePlayerUnitItem,
    Item,
    ItemBase,
    Player,
    PlayerBase,
    Unit,
    UnitBase,
)

augment_cache = {}
unit_cache = {}
item_cache = {}


async def load_augment_cache(conn: AsyncConnection) -> None:
    stmt = select(Augment.augment_name, Augment.id)
    res = await conn.execute(stmt)
    for augment_name, augment_id in res:
        augment_cache[augment_name] = augment_id


async def load_unit_cache(conn: AsyncConnection) -> None:
    stmt = select(Unit.unit_name, Unit.id)
    res = await conn.execute(stmt)
    for unit_name, unit_id in res:
        unit_cache[unit_name] = unit_id


async def load_item_cache(conn: AsyncConnection) -> None:
    stmt = select(Item.item_name, Item.id)
    res = await conn.execute(stmt)
    for item_name, item_id in res:
        item_cache[item_name] = item_id


async def load_player(
    conn: AsyncConnection, player: PlayerBase, ignore_update: Optional[set] = None
):
    if ignore_update is None:
        ignore_update = set()
    insert_stmt = postgresql.insert(Player).values(**player.dict())
    upsert_stmt = insert_stmt.on_conflict_do_update(
        index_elements=["player_name"],
        set_={
            k: getattr(insert_stmt.excluded, k)
            for k in player.dict()
            if getattr(player, k) is not None and k not in ignore_update
        },
    )
    res = await conn.execute(upsert_stmt)
    assert hasattr(res, "inserted_primary_key"), "inserted_primary_key doesn't exist"
    return res.inserted_primary_key.id


async def load_game(conn: AsyncConnection, game: GameBase):
    insert_stmt = postgresql.insert(Game).values(**game.dict())
    upsert_stmt = insert_stmt.on_conflict_do_update(
        index_elements=["id"],
        set_={k: getattr(insert_stmt.excluded, k) for k in game.dict() if k != "id"},
    )
    res = await conn.execute(upsert_stmt)
    assert hasattr(res, "inserted_primary_key"), "inserted_primary_key doesn't exist"
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
    assert hasattr(res, "inserted_primary_key"), "inserted_primary_key doesn't exist"
    return res.inserted_primary_key.id


async def load_augment(conn: AsyncConnection, augment: AugmentBase):
    if augment.augment_name in augment_cache:
        return augment_cache[augment.augment_name]
    insert_stmt = insert(Augment).values(**augment.dict())
    res = await conn.execute(insert_stmt)
    assert hasattr(res, "inserted_primary_key"), "inserted_primary_key doesn't exist"
    augment_id = res.inserted_primary_key.id
    augment_cache[augment.augment_name] = augment_id
    return augment_id


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
    assert hasattr(res, "inserted_primary_key"), "inserted_primary_key doesn't exist"
    return res.inserted_primary_key.id


async def load_unit(conn: AsyncConnection, unit: UnitBase):
    if unit.unit_name in unit_cache:
        return unit_cache[unit.unit_name]
    insert_stmt = insert(Unit).values(**unit.dict())
    res = await conn.execute(insert_stmt)
    assert hasattr(res, "inserted_primary_key"), "inserted_primary_key doesn't exist"
    unit_id = res.inserted_primary_key.id
    unit_cache[unit.unit_name] = unit_id
    return unit_id


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
    assert hasattr(res, "inserted_primary_key"), "inserted_primary_key doesn't exist"
    return res.inserted_primary_key.id


async def load_item(conn: AsyncConnection, item: ItemBase):
    if item.item_name in item_cache:
        return item_cache[item.item_name]
    insert_stmt = insert(Item).values(**item.dict())
    res = await conn.execute(insert_stmt)
    assert hasattr(res, "inserted_primary_key"), "inserted_primary_key doesn't exist"
    item_id = res.inserted_primary_key.id
    item_cache[item.item_name] = item_id
    return item_id


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
    assert hasattr(res, "inserted_primary_key"), "inserted_primary_key doesn't exist"
    return res.inserted_primary_key.id


async def load_game_detail(conn: AsyncConnection, game: GameModel):
    for player_mdl in game.players:
        player = player_mdl.player
        player.region = game.game.region
        player_id = await load_player(
            conn, player, ignore_update={"player_tier", "player_division"}
        )
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
    await conn.execute(
        update(Game).where(Game.id == game.game.id).values(status="processed")
    )
