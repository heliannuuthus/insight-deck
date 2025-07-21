from datetime import datetime, timedelta
from fastapi import APIRouter, Query
from logging import getLogger
import asyncio

logger = getLogger(__name__)

from insightdeck.arxiv.agent import compute_article_score
from insightdeck.arxiv.client import Client, Category, Search, SortCriterion, SortOrder

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
    query += f" AND submittedDate:[{last_monday.strftime('%Y%m%d%2000')} TO {last_sunday.strftime('%Y%m%d%19:59')}]"

    results = []
    # 并发收集全部文章（拉取本身是串行的，只能先这样）
    async for result in Client(page_size=max_results).results(
        Search(query=query,
               max_results=max_results,
               sort_by=SortCriterion.SubmittedDate,
               sort_order=SortOrder.Descending)):
        results.append(result)

    # 并发处理文章打分
    async def score_article(article):
        return compute_article_score(article)

    scored = await asyncio.gather(*(score_article(r) for r in results))
    scored.sort(key=lambda x: x["average_score"], reverse=True)
    logger.info(f"scored: {scored}")
    return scored[:10]
