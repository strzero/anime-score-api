import asyncio
import uuid
from uuid import UUID

from fastapi import APIRouter, WebSocket
from models.request_model import IdRequest
from services.task_scheduler import task_queue, task_scheduler, Task, running_tasks, \
    completed_id_tasks, bgmid_to_uuid_getid
from utils.logger import logger

router = APIRouter()

@router.post("/task/add_id")
async def add_id_task(request: IdRequest, task_id: UUID = uuid.uuid4()):
    bangumi_id = request.bangumi_id
    if not bangumi_id in bgmid_to_uuid_getid:
        task = Task(request, task_id)
        bgmid_to_uuid_getid[bangumi_id] = [task_id, 1]
        await task_queue.put(task)
    else:
        bgmid_to_uuid_getid[bangumi_id][1] += 1
    return task_id

@router.websocket("/ws/id/tasks")
async def websocket_tasks(websocket: WebSocket):
    await websocket.accept()
    last_sent_tasks = None  # 记录上一次发送的数据
    while True:
        tasks = [task for task in task_queue._queue if isinstance(task.request, IdRequest)] + \
                [task for task in running_tasks if isinstance(task.request, IdRequest)]

        task_data = [
            {"title": task.request.title, "status": "pending" if task in task_queue._queue else "running"}
            for task in tasks
        ]

        if task_data != last_sent_tasks:  # 只有任务状态变化时才发送数据
            await websocket.send_json(task_data)
            last_sent_tasks = task_data

        await asyncio.sleep(1)


@router.websocket("/ws/id/task_completed")
async def websocket_task_completed(websocket: WebSocket):
    await websocket.accept()
    while True:
        task = await completed_id_tasks.get()  # 从专用队列中获取完成的 IdRequest 任务
        await websocket.send_json({"task_title": task.request.title, "result": task.result})

# 启动调度器
async def id_task_queue_start():
    asyncio.create_task(task_scheduler())

@router.post("/task/clean_id")
async def clean_id():
    while not task_queue.empty():
        await task_queue.get()
    return "已清空"
