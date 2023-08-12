import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parents[2]))

from sqlmodel import SQLModel, create_engine

from shared import models  # noqa
from shared.settings import settings

if __name__ == "__main__":
    db_url = (
        "postgresql+psycopg2://"
        f"{settings.db_user}:{settings.db_password}@"
        f"{settings.db_host}:{settings.db_port}/"
        f"{settings.db_name}"
    )
    engine = create_engine(db_url, echo=True)
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)
