import asyncio
import numpy as np
from functools import lru_cache
from typing import Dict, List, Tuple

from logging import getLogger
from langchain_community.vectorstores.utils import cosine_similarity
from langchain_google_genai import GoogleGenerativeAIEmbeddings

from insightdeck.arxiv.client import Result
from internal.config import get_arxiv_config

logger = getLogger(__name__)

__embedding_model = GoogleGenerativeAIEmbeddings(
    model=get_arxiv_config().model_name)


def compute_article_score(article: Result) -> Dict:
    """
    对单篇文章打分，返回总分和各维度的分数

    Args:
        article: 文章信息
            title: 文章标题
            summary: 文章摘要

    Returns:
        Dict: 平均分和各维度的分数
    """
    text = article.title + ". " + article.summary
    summary_emb = np.array(__get_embedding(text)).reshape(1, -1)
    scores: Dict[str, float] = {}

    for dim, dim_embedding in __get_weighted_interest_embedding().items():
        # TODO 目前仅计算与单个维度的相似度，后续可以考虑计算与多个维度的相似度
        logger.info(f"article: {article.title}, dim: {dim}")
        scores[dim] = cosine_similarity(summary_emb, dim_embedding)

    average_score = sum(scores.values()) / len(scores)
    return {"average_score": average_score, "scores": scores}


@lru_cache(maxsize=20)
def __get_weighted_interest_embedding() -> Dict[str, List[float]]:
    """
    计算单个维度的关键词的权重总和
    """
    dim_scores: Dict[str, List[float]] = {}
    interests = __get_interests()
    for dim, keywords in interests.items():
        dim_scores[dim] = __compute_weighted_interest_embedding_for_dim(
            keywords)
    return dim_scores


def __compute_weighted_interest_embedding_for_dim(
        keywords: List[Tuple[str, float]]) -> List[float]:
    """
    计算单个维度的关键词的权重总和
    """
    weighted_vec: np.ndarray | None = None

    for k, score in keywords:
        emb = np.array(__get_embedding(k)) * score
        weighted_vec = np.sum(emb, axis=0) if weighted_vec is None else np.add(
            weighted_vec, emb)

    return weighted_vec.reshape(1, -1).tolist()


def __get_embedding(text: str) -> List[float]:
    return __embedding_model.embed_query(text)


def __get_interests() -> Dict[str, List[Tuple[str, float]]]:
    return get_arxiv_config().interests
