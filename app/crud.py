import logging
from random import randint

from tinydb import TinyDB

from app.config import Settings
from tinydb import database

settings = Settings()
db = TinyDB("data/data.json", sort_keys=True, indent=4, separators=(",", ": "))

def get_random_item(db: database) -> dict:
    """Get a random item from the database."""

    id_selection = randint(1, len(db.all()))
    doc = None

    while not doc:
        logging.warning(f"fetching artist at {id_selection=}")
        id_selection = randint(1, len(db.all()))
        doc = db.get(doc_id=id_selection)
        logging.warning(f"{doc=}")

    return db.get(doc_id=id_selection)
