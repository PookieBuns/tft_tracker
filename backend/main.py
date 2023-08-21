import asyncio

import typer
import uvicorn

from etl_service.core.worker import get_and_sync_games, get_and_sync_players
from etl_service.main import main
from etl_service.main import web_app as etl_web_app
from main_service.main import app as main_web_app

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


APP_NAME_TO_WEB_APP = {"etl": etl_web_app, "main": main_web_app}


@app.command()
def runserver(app_name: str):
    uvicorn.run(APP_NAME_TO_WEB_APP[app_name])


if __name__ == "__main__":
    app()
