from aiohttp import ClientSession

PROFILE_URL = "https://lolchess.gg/profile/{region}/{profile_name}"
MATCH_URL = (
    "https://lolchess.gg/profile/{region}/{profile_name}/{set_name}/matches/all/{page}"
)
MATCH_DETAIL_URL = "https://lolchess.gg/profile/{region}/{profile_name}/matchDetail/{set_name}/{game_id}"
SET_NAME = "s9"


async def get_profile_data(session: ClientSession, region: str, username: str) -> str:
    async with session.get(
        PROFILE_URL.format(region=region, profile_name=username)
    ) as response:
        return await response.text()


async def update_profile_data(session: ClientSession, update_url: str):
    for _ in range(10):
        res = await session.get(update_url)
        res_json = await res.json()
        if res_json.get("done"):
            break


async def get_match_data(
    session: ClientSession, region: str, username: str, page: int
) -> str:
    async with session.get(
        MATCH_URL.format(
            region=region, profile_name=username, set_name=SET_NAME, page=page
        )
    ) as response:
        return await response.text()


async def get_match_detail_data(
    session: ClientSession, region: str, username: str, game_id: int
) -> str:
    async with session.get(
        MATCH_DETAIL_URL.format(
            region=region, profile_name=username, set_name=SET_NAME, game_id=game_id
        )
    ) as response:
        resp_json = await response.json()
        return resp_json["html"]
