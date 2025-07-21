import asyncio
from datetime import datetime, timedelta
from logging import getLogger
from typing import Tuple

from fastapi import APIRouter, Query

from insightdeck.arxiv.agent import Result, Score, compute_article_score
from insightdeck.arxiv.client import (
    Category,
    Client,
    Search,
    SortCriterion,
    SortOrder,
)

logger = getLogger(__name__)
router = APIRouter()


@router.get("/arxiv/articles")
async def get_arxiv_articles(
        categories: list[Category] = Query(),
        max_results: int = Query(default=800),
):
    logger.info(
        f"Getting articles for categories: {categories}, max_results: {max_results}"
    )
    query = " OR ".join([f"cat:{c.value}" for c in categories])

    today = datetime.now()
    this_monday = today - timedelta(days=today.weekday())
    last_monday = this_monday - timedelta(days=7)
    last_sunday = last_monday + timedelta(days=6)
    query += f" AND submittedDate:[{last_monday.strftime('%Y%m%d2000')} TO {last_sunday.strftime('%Y%m%d1959')}]"
    scored = await asyncio.gather(
        *[
            asyncio.to_thread(compute_article_score, r)
            async for r in Client(page_size=max_results).results(
                Search(
                    query=query,
                    max_results=max_results,
                    sort_by=SortCriterion.SubmittedDate,
                    sort_order=SortOrder.Descending,
                ))
        ],
        return_exceptions=True,
    )

    def process_result(result: Tuple[Result, Score] | Exception,) -> float:
        if isinstance(result, Exception):
            logger.error(f"error processing article: {result[0].title}")
            return 0
        logger.info(f"processed article: {result[0].title}")
        return result[1].average_score

    scored.sort(key=process_result, reverse=True)
    logger.info(f"scored: {scored}")
    return scored[:10]
