from dataclasses import dataclass
from functools import lru_cache
from typing import List, Tuple

from dynaconf import Dynaconf

__settings = Dynaconf(
    settings_files=["config.toml"],
)


def get_global_settings() -> Dynaconf:
    return __settings


@dataclass
class ArxivSettings:
    model_name: str
    max_results: int
    interests: List[Tuple[str, float]]


@lru_cache(maxsize=1)
def get_arxiv_settings() -> ArxivSettings:
    raw = __settings.arxiv

    interest_groups = raw.interests
    interests: List[Tuple[str, float]] = []

    for group_name in interest_groups.keys():
        group = getattr(interest_groups, group_name)
        interests.extend(
            (key.replace("_", " "), float(value)) for key, value in group.items()
        )

    return ArxivSettings(
        model_name=raw.model_name, max_results=raw.max_results, interests=interests
    )
