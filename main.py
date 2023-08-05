import aiohttp
import asyncio

from src.handler.extractor import get_profile_data, update_profile_data
from src.handler.transformer import transform_profile_data, get_update_url


async def main():
    username = "nitemist"
    async with aiohttp.ClientSession() as session:
        profile_data = await get_profile_data(session, username=username)
        update_url = get_update_url(profile_data)
        await update_profile_data(session, update_url)

    player, games = transform_profile_data(profile_data)
    print(update_url)
    print(player)
    print(games)


if __name__ == "__main__":
    while True:
        asyncio.run(main())
