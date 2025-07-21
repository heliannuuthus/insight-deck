from dataclasses import dataclass
from functools import lru_cache
from typing import Dict, List, Tuple

from dynaconf import Dynaconf

__config = Dynaconf(settings_files=["config.toml"],)


def get_global_config() -> Dynaconf:
    return __config


@dataclass
class ArxivConfig:
    model_name: str
    max_results: int
    interests: Dict[str, List[Tuple[str, float]]]


@lru_cache(maxsize=1)
def get_arxiv_config() -> ArxivConfig:
    raw = __config.arxiv

    interest_groups = raw.interests
    interests: Dict[str, List[Tuple[str, float]]] = {}

    for group_name in interest_groups.keys():
        group = getattr(interest_groups, group_name)
        interests[group_name] = [(key.replace("_", " "), float(value))
                                 for key, value in group.items()]

    return ArxivConfig(model_name=raw.model_name,
                       max_results=raw.max_results,
                       interests=interests)
