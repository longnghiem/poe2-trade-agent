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
# EE2's saved copy of the official trade site's stat list, in the site's own order.
OFFICIAL_STATS_URL = "https://raw.githubusercontent.com/Kvan7/Exiled-Exchange-2/master/renderer/specs/data/stats.json"


def download(url: str) -> str:
    logger.info("Downloading %s", url)
    response = httpx.get(url, timeout=60)
    response.raise_for_status()
    return response.text


def parse_stats_lines(lines: list[str]) -> list[Mod]:
    mods: dict[str, Mod] = {}
    for line in lines:
        entry = json.loads(line)
        # A mod with a choice ("Allocates #") can't be searched without choosing;
        # the official list has one id per choice.
        if entry["trade"].get("option"):
            continue
        # A few stats can't be searched on the trade site; their "ids" is null.
        ids_by_source = entry["trade"]["ids"] or {}
        for source, trade_ids in ids_by_source.items():
            for trade_id in trade_ids:
                mods[trade_id] = Mod(id=trade_id, text=entry["ref"], source=source)
    return list(mods.values())


def parse_official_stats(official_stats: str) -> dict[str, str]:
    """Map each trade id to its official text, in the official order."""
    groups = json.loads(official_stats)["result"]
    return {
        entry["id"]: entry["text"] for group in groups for entry in group["entries"]
    }


def merge_official_stats(mods: list[Mod], official: dict[str, str]) -> list[Mod]:
    """Set each mod's position, add "(Local)" and the like, and add the missing mods."""
    merged = {mod.id: mod for mod in mods}
    for position, (trade_id, text) in enumerate(official.items()):
        mod = merged.get(trade_id)
        if mod is None:
            # Mostly choices, e.g. "Allocates Doomsayer" (enchant.stat_2954116742|57190).
            mod = Mod(id=trade_id, text=text, source=trade_id.split(".")[0])
            merged[trade_id] = mod
        elif text.lower().startswith(f"{mod.text} (".lower()):
            mod.text = text
        mod.position = position
    return list(merged.values())


def import_mods() -> None:
    """Download the stat lists and replace all rows of the mod table, in one transaction."""
    mods = parse_stats_lines(download(STATS_URL).splitlines())
    official = parse_official_stats(download(OFFICIAL_STATS_URL))
    mods = merge_official_stats(mods, official)
    without_position = sum(mod.position is None for mod in mods)
    with Session(engine) as session:
        session.exec(delete(Mod))
        session.add_all(mods)
        session.commit()
    logger.info("Imported %d mods (%d without position)", len(mods), without_position)


def main() -> None:
    setup_logging()
    try:
        import_mods()
    except Exception:
        logger.exception("The import failed; the mod table is unchanged")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
