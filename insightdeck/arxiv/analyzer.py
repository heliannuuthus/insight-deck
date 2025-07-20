from insightdeck.arxiv.client import Search, SortCriterion


def fetch_arxiv_articles(categories, max_results=100):
    query = " OR ".join([f"cat:{c}" for c in categories])
    return Search(
        query=query, max_results=max_results, sort_by=SortCriterion.SubmittedDate
    )
