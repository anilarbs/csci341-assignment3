import os
from pathlib import Path

from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url

ROOT = Path(__file__).resolve().parent
url = make_url(os.environ["DATABASE_URL"])
if url.drivername in {"postgres", "postgresql"}:
    url = url.set(drivername="postgresql+psycopg")
engine = create_engine(url, pool_pre_ping=True)


def statements(filename):
    # The project's three controlled SQL scripts contain simple statements only.
    return [s.strip() for s in (ROOT / "sql" / filename).read_text().split(";") if s.strip()]


def initialize(connection):
    for filename in ("schema.sql", "seed.sql", "view.sql"):
        for statement in statements(filename):
            connection.execute(text(statement))


if __name__ == "__main__":
    with engine.begin() as connection:
        initialize(connection)
    print("Created and populated the database.")
