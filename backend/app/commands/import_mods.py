"""Downloads Exiled Exchange 2's English stat list and replaces the mod table with it.

Run it after game patches: uv run python -m app.commands.import_mods
Data: Exiled Exchange 2 (MIT, © 2020 Alexander Drozdov).
"""

import json
import logging

import httpx
from sqlmodel import Session, delete

from app.core.db import engine
from app.core.logging_config import setup_logging
from app.models import Mod

logger = logging.getLogger(__name__)

STATS_URL = "https://raw.githubusercontent.com/Kvan7/Exiled-Exchange-2/master/renderer/public/data/en/stats.ndjson"


def parse_stats_lines(lines: list[str]) -> list[Mod]:
    mods: dict[str, Mod] = {}
    for line in lines:
        entry = json.loads(line)
        # A few stats can't be searched on the trade site; their "ids" is null.
        ids_by_source = entry["trade"]["ids"] or {}
        for source, trade_ids in ids_by_source.items():
            for trade_id in trade_ids:
                mods[trade_id] = Mod(id=trade_id, text=entry["ref"], source=source)
    return list(mods.values())


def import_mods() -> None:
    """Download the stat list and replace all rows of the mod table, in one transaction."""
    logger.info("Downloading the stat list from %s", STATS_URL)
    response = httpx.get(STATS_URL, timeout=60)
    response.raise_for_status()
    mods = parse_stats_lines(response.text.splitlines())
    with Session(engine) as session:
        session.exec(delete(Mod))
        session.add_all(mods)
        session.commit()
    logger.info("Imported %d mods", len(mods))


def main() -> None:
    setup_logging()
    try:
        import_mods()
    except Exception:
        logger.exception("The import failed; the mod table is unchanged")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
