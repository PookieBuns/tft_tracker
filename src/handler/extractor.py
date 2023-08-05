from aiohttp import ClientSession

PROFILE_URL = "https://lolchess.gg/profile/na/{profile_name}"


async def get_profile_data(session: ClientSession, username: str) -> str:
    async with session.get(PROFILE_URL.format(profile_name=username)) as response:
        return await response.text()


async def update_profile_data(session: ClientSession, update_url: str):
    while True:
        res = await session.get(update_url)
        res_json = await res.json()
        print(res_json)
        if res_json.get("done"):
            break
        res = await session.get(update_url)
        res_json = await res.json()
