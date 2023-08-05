import arrow
import re
from bs4 import BeautifulSoup

from src.models import GameBase, PlayerBase


def time_to_seconds(time_str: str) -> int:
    minutes, seconds = map(int, time_str.split(":"))
    total_seconds = minutes * 60 + seconds
    return total_seconds


def get_update_url(profile_data: str) -> str:
    pattern = r"https://lolchess.gg/api/v1/profile/sync/by-puuid/NA/[A-Za-z0-9_-]+"
    # Search the HTML for the pattern
    match = re.search(pattern, profile_data)
    assert match, "Could not find update URL"
    return match.group(0)


def parse_match_to_game(match) -> GameBase:
    data_game_id = match["data-game-id"]
    summary = match.find("div", {"class": "summary"})
    game_mode = summary.find("div", {"class": "game-mode"}).get_text(strip=True)
    length = summary.find("div", {"class": "length"}).get_text(strip=True)
    age = summary.find("div", {"class": "age"})
    tooltip = age.find("span", {"data-toggle": "tooltip"})
    game_start_time = tooltip["title"]
    game_start_time = arrow.get(game_start_time, "MM-DD-YYYY HH:mm:ss").datetime
    return GameBase(
        id=data_game_id,
        game_mode=game_mode,
        game_length=time_to_seconds(length),
        game_start_time=game_start_time,
    )


def parse_match_history_to_games(match_history) -> list[GameBase]:
    games = []
    for match in match_history.find_all(
        "div", {"class": "profile__match-history-v2__item"}
    ):
        games.append(parse_match_to_game(match))
    return games


def parse_player_info_to_player(soup: BeautifulSoup) -> PlayerBase:
    player_name = soup.find("div", {"class": "player-name"})
    player_region_str = player_name.find("span", {"class": "player-region"}).get_text(
        strip=True
    )
    player_name_str = (
        player_name.get_text(strip=True).replace(player_region_str, "").strip()
    )
    profile_tier_summary = soup.find("div", {"class": "profile__tier__summary"})
    profile_tier = profile_tier_summary.find(
        "span", {"class": "profile__tier__summary__tier"}
    ).get_text(strip=True)
    tier_info = profile_tier.split(" ")
    if len(tier_info) == 1:
        tier = tier_info[0]
        division = 1
    else:
        tier, division = tier_info
    player = PlayerBase(
        player_name=player_name_str,
        player_region=player_region_str,
        player_tier=tier,
        player_division=division,
    )
    return player


def transform_profile_data(profile_data: str) -> tuple[PlayerBase, list[GameBase]]:
    soup = BeautifulSoup(profile_data, "html.parser")
    # get profile__match_history_v2
    match_history = soup.find("div", {"class": "profile__match-history-v2__items"})
    games = parse_match_history_to_games(match_history)
    player = parse_player_info_to_player(soup)
    return player, games
