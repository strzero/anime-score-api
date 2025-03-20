import asyncio
from datetime import datetime
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from tortoise.contrib.fastapi import register_tortoise

from config import settings
from maintain.maintain_db import maintain_db
from routers import info, query, id_task_queue, score_task_queue, bangumi, change_statistics, anime_now
from services.db_renew import renew_data
from services.task_scheduler import task_scheduler
from utils.logger import logger

@asynccontextmanager
async def lifespan(app: FastAPI):
    asyncio.create_task(task_scheduler())
    asyncio.create_task(renew_data())
    asyncio.create_task(maintain_db())
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

app.include_router(query.router)
app.include_router(id_task_queue.router)
app.include_router(score_task_queue.router)
app.include_router(bangumi.router)
app.include_router(change_statistics.router)
app.include_router(anime_now.router)
app.include_router(info.router)

logger.info("\n\n\n------------------------------\n\n\n")
logger.info("API启动:" + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=5100)