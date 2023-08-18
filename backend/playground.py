import asyncio

from aiohttp import ClientSession

from etl_service.core.extractor import get_match_data, get_profile_data
from etl_service.core.transformer import (
    transform_match_list_data,
    transform_profile_data,
)


async def main():
    user_name = "pookiebuns"
    region = "NA"
    async with ClientSession() as session:
        profile_data = await get_profile_data(session, region, user_name)
    transformed_data = transform_profile_data(profile_data, user_name)
    print(transformed_data)
    async with ClientSession() as session:
        for page in range(1, 10):
            game_data = await get_match_data(session, region, user_name, page)
            transofrmed_game_data = transform_match_list_data(
                game_data, transformed_data
            )
            print(transofrmed_game_data)


if __name__ == "__main__":
    asyncio.run(main())
