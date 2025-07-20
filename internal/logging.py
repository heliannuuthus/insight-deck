import logging
from logging import getLogger

logger = getLogger(__name__)


def setup_logging(level: int = logging.INFO) -> None:
    logging.basicConfig(
        level=level,
        format="v1 %(asctime)s 【%(levelname)s】%(filename)s %(funcName)s：%(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
