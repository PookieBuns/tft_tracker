import asyncio

import typer

from etl_service.core.worker import sync_games, sync_players
from etl_service.main import main

app = typer.Typer()


@app.command()
def games(batch_size: int = 10, run_forever: bool = False, debug: bool = False):
    asyncio.run(
        main(sync_games, batch_size=batch_size, run_forever=run_forever, debug=debug)
    )


@app.command()
def players(batch_size: int = 10, run_forever: bool = False, debug: bool = False):
    asyncio.run(
        main(sync_players, batch_size=batch_size, run_forever=run_forever, debug=debug)
    )


if __name__ == "__main__":
    app()
