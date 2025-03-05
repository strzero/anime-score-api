import asyncio

from fastapi import WebSocket, APIRouter
from models.request_model import ScoreRequest
from services.task_scheduler import task_queue, task_set, task_scheduler, Task, running_tasks, \
    completed_score_tasks

from config import settings
from models.request_model import ScoreRequest
from services.get_web_data import get_four_score

router = APIRouter()

@router.post("/task/add_score")
async def add_task(request: ScoreRequest):
    if request.bangumi_id+2 not in task_set:
        task = Task(request)
        await task_queue.put(task)
        task_set.add(request.bangumi_id+2)


@router.websocket("/ws/score/tasks")
async def websocket_tasks(websocket: WebSocket):
    await websocket.accept()
    while True:
        # 筛选出队列中所有任务类型为 ScoreRequest 的任务
        tasks = [task for task in task_queue._queue if isinstance(task.request, ScoreRequest)] + \
                [task for task in running_tasks if isinstance(task.request, ScoreRequest)]

        if tasks:
            task_data = [
                {"title": task.request.title, "status": "pending" if task in task_queue._queue else "running"}
                for task in tasks
            ]
            await websocket.send_json(task_data)

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

@router.post("/task/clean_score")
async def clean_id():
    while not task_queue.empty():
        await task_queue.get()
    return "已清空"