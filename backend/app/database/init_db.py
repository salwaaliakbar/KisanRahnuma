"""Create (or recreate) all tables.

    python -m app.database.init_db           # create missing tables
    python -m app.database.init_db --reset   # drop and recreate everything (deletes data!)
"""
import argparse

from app.database.session import Base, engine
import app.models  # noqa: F401  (registers models on Base.metadata)


def init_db(reset: bool = False) -> None:
    if reset:
        Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reset", action="store_true", help="drop all tables first")
    args = parser.parse_args()
    init_db(reset=args.reset)
    print(f"Tables ready on {engine.url.render_as_string(hide_password=True)}")
