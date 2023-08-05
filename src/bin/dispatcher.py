import pandas as pd
from sqlalchemy import CursorResult, select, text
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from src.settings import settings
from src.utils import convert_to_df


async def query_dispatch_data(engine: AsyncEngine) -> pd.DataFrame:
    async with engine.begin() as session:
        stmt = select(
            text("select * from summoner_tasks where next_sync_time < unix_timestamp()")
        )
        res = await session.execute(stmt)
        return convert_to_df(rows)


def format_data(df: pd.DataFrame):
    pass


async def dispatch():
    engine = create_async_engine()
    dispatch_df = await query_dispatch_data(engine)
    tasks = format_data(dispatch_df)
    await dispatch_tasks(tasks)


async def main():
    await dispatch()
