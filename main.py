import logging
from dotenv import load_dotenv

load_dotenv()
from fastapi import FastAPI
from insightdeck import arxiv_router

from internal import setup_logging, get_global_config

setup_logging(get_global_config().logging.config_path)
logger = logging.getLogger(__name__)

app = FastAPI()

app.include_router(arxiv_router)


def start():
    import uvicorn
    logger.info("Starting server")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)


if __name__ == "__main__":
    start()
