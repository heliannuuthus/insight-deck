from typing import Dict, List

from langchain.vectorstores.utils import cosine_similarity
from langchain_google_genai import GoogleGenerativeAIEmbeddings

from internal.setting import get_arxiv_settings

__embedding_model = GoogleGenerativeAIEmbeddings(model=get_arxiv_settings().model_name)


def get_interest_keywords() -> Dict[str, List[str]]:
    return get_arxiv_settings().interests


# 可配置的兴趣维度（你可以放到配置文件）
INTEREST = {
    "方法": ["diffusion", "transformer", "RL", "LLM", "tokenizer"],
    "应用": ["robotics", "code generation", "reasoning"],
    "领域": ["AI", "machine learning", "planning", "autonomous"],
}


def get_embedding(text: str) -> List[float]:
    return __embedding_model.embed_query(text)


def compute_article_score(article: Dict, interest: Dict[str, List[str]]) -> Dict:
    """对单篇文章打分，返回分数和匹配信息"""
    text = article["title"] + ". " + article["summary"]
    summary_emb = get_embedding(text)
    total_score = 0.0
    sub_scores = {}

    # 对每个维度分别计算相似度
    for dim, keywords in interest.items():
        interest_emb = get_embedding(", ".join(keywords))
        score = cosine_similarity(summary_emb, interest_emb)
        sub_scores[dim] = score

    # 加权求和（可自定义）
    total_score = (
        0.5 * sub_scores["方法"] + 0.3 * sub_scores["应用"] + 0.2 * sub_scores["领域"]
    )

    return {
        "title": article["title"],
        "summary": article["summary"],
        "score": total_score,
        "sub_scores": sub_scores,
    }


def filter_articles(articles: List[Dict], top_k: int = 10) -> List[Dict]:
    """主函数：对全部文章打分并筛选"""
    results = []
    for article in articles:
        result = compute_article_score(article, INTEREST)
        results.append(result)

    return sorted(results, key=lambda x: x["score"], reverse=True)[:top_k]
