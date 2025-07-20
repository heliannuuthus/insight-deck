from dotenv import load_dotenv
from fastapi import FastAPI

from internal.logging import setup_logging

load_dotenv()

setup_logging()

app = FastAPI()


def run():
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    run()
