import asyncio
import uuid
from uuid import UUID

from fastapi import WebSocket, APIRouter
from models.request_model import ScoreRequest
from services.task_scheduler import task_queue, task_scheduler, Task, running_tasks, \
    completed_score_tasks, bgmid_to_uuid_getscore

from config import settings
from models.request_model import ScoreRequest
from services.webdata_get import get_four_score

router = APIRouter()

# @router.post("/task/add_score")
async def add_score_task(request: ScoreRequest, task_id: UUID):
    bangumi_id = request.bangumi_id
    if not bangumi_id in bgmid_to_uuid_getscore:
        task = Task(request, task_id)
        bgmid_to_uuid_getscore[bangumi_id] = [task_id, 1]
        await task_queue.put(task)
    else:
        bgmid_to_uuid_getscore[bangumi_id][1] += 1
    return bgmid_to_uuid_getscore[bangumi_id][0]


@router.websocket("/ws/score/tasks")
async def websocket_tasks(websocket: WebSocket):
    await websocket.accept()
    last_sent_tasks = None  # 记录上一次发送的数据
    while True:
        tasks = [task for task in task_queue._queue if isinstance(task.request, ScoreRequest)] + \
                [task for task in running_tasks if isinstance(task.request, ScoreRequest)]

        task_data = [
            {"title": task.request.title, "status": "pending" if task in task_queue._queue else "running"}
            for task in tasks
        ]

        if task_data != last_sent_tasks:  # 只有任务状态变化时才发送数据
            await websocket.send_json(task_data)
            last_sent_tasks = task_data

        await asyncio.sleep(1)


@router.websocket("/ws/score/task_completed")
async def websocket_task_completed(websocket: WebSocket):
    await websocket.accept()
    while True:
        task = await completed_score_tasks.get()  # 从专用队列中获取完成的 ScoreRequest 任务
        await websocket.send_json({"task_title": task.request.title, "result": task.result})

# 启动调度器
async def score_task_queue_start():
    asyncio.create_task(task_scheduler())

# @router.post("/task/clean_score")
async def clean_id():
    while not task_queue.empty():
        await task_queue.get()
    return "已清空"