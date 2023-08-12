import re

import arrow
from bs4 import BeautifulSoup, Tag

from shared.models import (
    AugmentBase,
    GameBase,
    GamePlayerModel,
    ItemBase,
    PlayerBase,
    UnitModel,
)

TIER_ABBREVIATION_MAP = {
    "U": "Unranked",
    "I": "Iron",
    "B": "Bronze",
    "S": "Silver",
    "G": "Gold",
    "P": "Platinum",
    "D": "Diamond",
    "M": "Master",
    "GM": "Grandmaster",
    "C": "Challenger",
}


def time_to_seconds(time_str: str) -> int:
    minutes, seconds = map(int, time_str.split(":"))
    total_seconds = minutes * 60 + seconds
    return total_seconds


def get_update_url(profile_data: str, player: str) -> str:
    pattern = (
        r"https://lolchess.gg/api/v1/profile/sync/by-puuid/([A-Z]+)/([A-Za-z0-9_-]+)"
    )
    # Search the HTML for the pattern
    match = re.search(pattern, profile_data)
    assert match, f"Could not find update URL for {player=}"
    return match.group(0)


def parse_match_to_game(match, player: PlayerBase) -> GameBase:
    data_game_id = match["data-game-id"]
    summary = match.find("div", {"class": "summary"})
    game_mode = summary.find("div", {"class": "game-mode"}).get_text(strip=True)
    length = summary.find("div", {"class": "length"}).get_text(strip=True)
    age = summary.find("div", {"class": "age"})
    tooltip = age.find("span", {"data-toggle": "tooltip"})
    game_start_time = tooltip["title"]
    game_start_time = arrow.get(
        game_start_time, "MM-DD-YYYY HH:mm:ss"
    ).datetime.replace(tzinfo=None)
    return GameBase(
        id=data_game_id,
        region=player.region,
        origin_player_name=player.player_name,
        game_mode=game_mode,
        game_length=time_to_seconds(length),
        game_start_time=game_start_time,
    )


def parse_player_info_to_games(
    soup: BeautifulSoup, player: PlayerBase
) -> list[GameBase]:
    games = []
    match_history = soup.find("div", {"class": "profile__match-history-v2__items"})
    assert isinstance(match_history, Tag), f"Could not find match history for {player=}"
    for match in match_history.find_all(
        "div", {"class": "profile__match-history-v2__item"}
    ):
        games.append(parse_match_to_game(match, player))
    return games


def parse_player_info_to_player(soup: BeautifulSoup) -> PlayerBase:
    player_name = soup.find("div", {"class": "player-name"})
    assert isinstance(player_name, Tag), f"Could not find player name for {soup=}"
    player_region = player_name.find("span", {"class": "player-region"})
    assert isinstance(player_region, Tag), f"Could not find player region for {soup=}"
    player_region_str = player_region.get_text(strip=True)
    player_name_str = (
        player_name.get_text(strip=True).replace(player_region_str, "").strip().lower()
    )
    profile_tier_summary = soup.find("div", {"class": "profile__tier__summary"})
    assert isinstance(
        profile_tier_summary, Tag
    ), f"Could not find tier summary for {soup=}"
    profile_tier = profile_tier_summary.find(
        "span", {"class": "profile__tier__summary__tier"}
    )
    assert isinstance(profile_tier, Tag), f"Could not find tier for {soup=}"
    profile_tier_str = profile_tier.get_text(strip=True)
    tier_info = profile_tier_str.split(" ")
    if len(tier_info) == 1:
        tier = tier_info[0]
        division = "1"
    else:
        tier, division = tier_info
    division_int = int(division)
    player = PlayerBase(
        region=player_region_str,
        player_name=player_name_str,
        player_tier=tier,
        player_division=division_int,
    )
    return player


def get_placement(row: Tag) -> int:
    placement = row.find("td", {"class": "placement"})
    assert isinstance(placement, Tag), f"Could not find placement for {row=}"
    placement_int = int(placement.get_text(strip=True))
    return placement_int


def get_player(row: Tag) -> PlayerBase:
    summoner_pattern = r"https://lolchess.gg/profile/([a-z]+)/(.+)"
    summoner = row.find("td", {"class": "summoner"})
    assert isinstance(summoner, Tag), f"Could not find summoner for {row=}"
    summoner_profile = summoner.find("a")
    assert isinstance(
        summoner_profile, Tag
    ), f"Could not find summoner profile for {summoner=}"
    summoner_profile_url = summoner_profile["href"]
    assert isinstance(summoner_profile_url, str), "summoner_profile_url is not a str"
    summoner_match = re.search(summoner_pattern, summoner_profile_url)
    assert summoner_match, f"Could not find summoner name {summoner_profile_url=}"
    region = summoner_match.group(1)
    summoner_name = summoner_match.group(2)
    tier_abbreviation = summoner.find("span", {"class": "tier-badge"})
    assert isinstance(
        tier_abbreviation, Tag
    ), f"Could not find tier abbreviation for {summoner=}"
    tier_abbreviation_str = tier_abbreviation.get_text(strip=True)
    match = re.match(r"([A-Z]+)(\d*)", tier_abbreviation_str)
    assert match, f"Could not find tier and division {tier_abbreviation=}"
    tier_char, division_char = match.groups()
    tier = TIER_ABBREVIATION_MAP[tier_char]
    division = int(division_char) if division_char else 1
    player = PlayerBase(
        region=region,
        player_name=summoner_name,
        player_tier=tier,
        player_division=division,
    )
    return player


def get_augments(row: Tag) -> list[AugmentBase]:
    augment_pattern = r"https://lolchess.gg/tooltip/item/([a-z0-9]+)/([0-9]+)"
    augments = row.find("td", {"class": "augments"})
    assert isinstance(augments, Tag), f"Could not find augments for {row=}"
    augment_list = []
    for augment in augments.find_all("div", {"class": "augment"}):
        img = augment.find("img")
        augment_name = img["alt"]
        augment_url = img["data-tooltip-url"]
        augment_match = re.search(augment_pattern, augment_url)
        assert augment_match, "Could not find update URL"
        augment_id = augment_match.group(2)
        augment_mdl = AugmentBase(
            id=augment_id,
            augment_name=augment_name,
        )
        assert augment_mdl.id != 9999, "Invalid augment"
        augment_list.append(augment_mdl)
    if len(augment_list) == 2:
        augment_list.insert(0, AugmentBase(id=9999, augment_name="Legend Augment"))
    return augment_list


def get_units(row: Tag) -> list[UnitModel]:
    units = row.find("td", {"class": "champions"})
    assert isinstance(units, Tag), f"Could not find units for {row=}"
    champions_list = units.find_all("div", {"class": "champions__image"})
    champions_items = units.find_all("ul", {"class": "champions__items"})
    assert len(champions_list) == len(champions_items)
    unit_list = []
    for champion, items in zip(champions_list, champions_items):
        champion_img = champion.find("img")
        champion_name = champion_img["alt"]
        item_list = []
        for item in items.find_all("img"):
            item_name = item["title"]
            item = ItemBase(
                item_name=item_name,
            )
            item_list.append(item)
        unit = UnitModel(
            unit_name=champion_name,
            items=item_list,
        )
        unit_list.append(unit)
    return unit_list


def parse_game_data_to_game_players(soup: BeautifulSoup) -> list[GamePlayerModel]:
    tbody = soup.find("tbody")
    assert isinstance(tbody, Tag), f"Could not find tbody for {soup=}"
    rows = tbody.find_all("tr")
    game_players = [
        GamePlayerModel(
            player=get_player(row),
            placement=get_placement(row),
            augments=get_augments(row),
            units=get_units(row),
        )
        for row in rows
    ]
    return game_players


def transform_profile_data(profile_data: str) -> tuple[PlayerBase, list[GameBase]]:
    soup = BeautifulSoup(profile_data, "html.parser")
    player = parse_player_info_to_player(soup)
    games = parse_player_info_to_games(soup, player)
    return player, games


def transform_game_data(game_data: str) -> list[GamePlayerModel]:
    soup = BeautifulSoup(game_data, "html.parser")
    game_players = parse_game_data_to_game_players(soup)
    return game_players
