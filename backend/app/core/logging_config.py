import logging


def setup_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    # httpx logs every request at info level; keep only its warnings and errors.
    logging.getLogger("httpx").setLevel(logging.WARNING)
