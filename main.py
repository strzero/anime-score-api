from datetime import datetime
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from tortoise.contrib.fastapi import register_tortoise

from config import settings
from routers import get_data, id_task_queue, score_task_queue, bangumi, change_statistics
from utils.logger import logger

@asynccontextmanager
async def lifespan(app: FastAPI):
    await id_task_queue.id_task_queue_start()
    await score_task_queue.score_task_queue_start()
    yield

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_tortoise(
    app,
    config=settings.DATABASE_CONFIG,
    # add_exception_handlers=True,
)

app.include_router(get_data.router)
app.include_router(id_task_queue.router)
app.include_router(score_task_queue.router)
app.include_router(bangumi.router)
app.include_router(change_statistics.router)

logger.info("\n\n\n------------------------------\n\n\n")
logger.info("API启动:" + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)