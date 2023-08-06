from datetime import datetime

from pydantic import BaseModel
from sqlalchemy import BigInteger, Column, ForeignKey
from sqlalchemy.orm import declared_attr
from sqlmodel import Field, Index
from sqlmodel import SQLModel as _SQLModel

from src.utils import camel_to_snake


class SQLModel(_SQLModel):
    @declared_attr  # type: ignore
    def __tablename__(cls) -> str:
        return camel_to_snake(cls.__name__)


class GameBase(SQLModel):
    id: int = Field(sa_column=Column(BigInteger, primary_key=True))
    region: str
    origin_player_name: str
    game_mode: str
    game_length: int
    game_start_time: datetime


class Game(GameBase, table=True):
    created_at: datetime = Field(default=datetime.utcnow)
    modified_at: datetime = Field(default=datetime.utcnow)


class PlayerBase(SQLModel):
    region: str
    player_name: str = Field(index=True, unique=True)
    player_tier: str | None = None
    player_division: int | None = None


class Player(PlayerBase, table=True):
    id: int = Field(default=None, primary_key=True)
    created_at: datetime = Field(default=datetime.utcnow)
    modified_at: datetime = Field(default=datetime.utcnow)


class GamePlayer(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    game_id: int = Field(sa_column=Column(BigInteger, ForeignKey("game.id")))
    player_id: int = Field(foreign_key="player.id")
    placement: int
    created_at: datetime = Field(default=datetime.utcnow)
    modified_at: datetime = Field(default=datetime.utcnow)

    __table_args__ = (
        Index("game_player_game_id_player_id", "game_id", "player_id", unique=True),
    )


class AugmentBase(SQLModel):
    id: int = Field(primary_key=True)
    augment_name: str = Field(index=True, unique=True)


class Augment(AugmentBase, table=True):
    created_at: datetime = Field(default=datetime.utcnow)
    modified_at: datetime = Field(default=datetime.utcnow)


class GamePlayerAugment(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    game_player_id: int = Field(foreign_key="game_player.id")
    augment_num: int
    augment_id: int = Field(foreign_key="augment.id")
    created_at: datetime = Field(default=datetime.utcnow)
    modified_at: datetime = Field(default=datetime.utcnow)

    __table_args__ = (
        Index(
            "game_player_augment_game_player_id_augment_num",
            "game_player_id",
            "augment_num",
            unique=True,
        ),
    )


class UnitBase(SQLModel):
    unit_name: str = Field(index=True, unique=True)


class Unit(UnitBase, table=True):
    id: int = Field(default=None, primary_key=True)
    created_at: datetime = Field(default=datetime.utcnow)
    modified_at: datetime = Field(default=datetime.utcnow)


class GamePlayerUnit(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    game_player_id: int = Field(foreign_key="game_player.id")
    unit_num: int
    unit_id: int = Field(foreign_key="unit.id")
    created_at: datetime = Field(default=datetime.utcnow)
    modified_at: datetime = Field(default=datetime.utcnow)

    __table_args__ = (
        Index(
            "game_player_unit_game_player_id_unit_num",
            "game_player_id",
            "unit_num",
            unique=True,
        ),
    )


class ItemBase(SQLModel):
    item_name: str = Field(index=True, unique=True)


class Item(ItemBase, table=True):
    id: int = Field(default=None, primary_key=True)
    created_at: datetime = Field(default=datetime.utcnow)
    modified_at: datetime = Field(default=datetime.utcnow)


class GamePlayerUnitItem(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    game_player_unit_id: int = Field(foreign_key="game_player_unit.id")
    item_num: int
    item_id: int = Field(foreign_key="item.id")
    created_at: datetime = Field(default=datetime.utcnow)
    modified_at: datetime = Field(default=datetime.utcnow)

    __table_args__ = (
        Index(
            "game_player_unit_item_game_player_unit_id_item_num",
            "game_player_unit_id",
            "item_num",
            unique=True,
        ),
    )


class UnitModel(BaseModel):
    unit_name: str
    items: list[ItemBase]


class GamePlayerModel(BaseModel):
    summoner_name: str
    placement: int
    augments: list[AugmentBase]
    units: list[UnitModel]


class GameModel(BaseModel):
    game: Game
    players: list[GamePlayerModel]
