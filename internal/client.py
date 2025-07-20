from httpx import AsyncClient

_client = None


def get_client() -> AsyncClient:
    global _client
    if _client is None:
        _client = AsyncClient()
    return _client
