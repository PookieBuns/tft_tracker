from sqlmodel import SQLModel, Field
from datetime import datetime


class GameBase(SQLModel):
    id: int = Field(primary_key=True)
    game_mode: str
    game_length: int
    game_start_time: datetime


class Game(GameBase, table=True):
    created_at: datetime = Field(default=datetime.utcnow)
    modified_at: datetime = Field(default=datetime.utcnow)


class PlayerBase(SQLModel):
    player_name: str
    player_region: str
    player_tier: str
    player_division: int


class Player(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    player_name: str
    created_at: datetime = Field(default=datetime.utcnow)
    modified_at: datetime = Field(default=datetime.utcnow)


class GamePlayer(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    game_id: int = Field(foreign_key="game.id")
    player_id: int = Field(foreign_key="player.id")
    placement: int
    created_at: datetime = Field(default=datetime.utcnow)
    modified_at: datetime = Field(default=datetime.utcnow)


class Augment(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    augment_name: str
    created_at: datetime = Field(default=datetime.utcnow)
    modified_at: datetime = Field(default=datetime.utcnow)


class GamePlayerAugment(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    game_player_id: int = Field(foreign_key="game_player.id")
    augment_id: int = Field(foreign_key="augment.id")
    created_at: datetime = Field(default=datetime.utcnow)
    modified_at: datetime = Field(default=datetime.utcnow)


class Unit(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    unit_name: str
    created_at: datetime = Field(default=datetime.utcnow)
    modified_at: datetime = Field(default=datetime.utcnow)


class GamePlayerUnit(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    game_player_id: int = Field(foreign_key="game_player.id")
    unit_id: int = Field(foreign_key="unit.id")
    created_at: datetime = Field(default=datetime.utcnow)
    modified_at: datetime = Field(default=datetime.utcnow)


class Item(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    item_name: str
    created_at: datetime = Field(default=datetime.utcnow)
    modified_at: datetime = Field(default=datetime.utcnow)


class GamePlayerUnitItem(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    game_player_unit_id: int = Field(foreign_key="game_player_unit.id")
    item_id: int = Field(foreign_key="item.id")
    created_at: datetime = Field(default=datetime.utcnow)
    modified_at: datetime = Field(default=datetime.utcnow)
