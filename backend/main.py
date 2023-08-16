import asyncio

import typer
import uvicorn

from etl_service.core.worker import get_and_sync_games, get_and_sync_players
from etl_service.main import main, web_app

app = typer.Typer()


@app.command()
def games(batch_size: int = 10, run_forever: bool = False, debug: bool = False):
    asyncio.run(
        main(
            get_and_sync_games,
            batch_size=batch_size,
            run_forever=run_forever,
            debug=debug,
        )
    )


@app.command()
def players(batch_size: int = 10, run_forever: bool = False, debug: bool = False):
    asyncio.run(
        main(
            get_and_sync_players,
            batch_size=batch_size,
            run_forever=run_forever,
            debug=debug,
        )
    )


@app.command()
def runserver():
    uvicorn.run(web_app)


if __name__ == "__main__":
    app()
