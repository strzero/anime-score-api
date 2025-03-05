import asyncio
from xmlrpc.client import Boolean

from fastapi import FastAPI, WebSocket, APIRouter
from asyncio import Queue

from models.request_model import IdRequest
from services.get_web_data import get_four_id

router = APIRouter()

class Task:
    def __init__(self, request: IdRequest):
        self.request = request
        self.completed = False
        self.result = None

    async def run(self):
        self.result = await get_four_id(self.request)
        self.completed = True
        return self

# 任务管理
task_queue = asyncio.Queue()  # 存放待执行任务
completed_tasks = asyncio.Queue()  # 存放已完成任务
running_tasks = []
task_id_counter = 0  # 任务 ID 计数器

# 任务调度器（每秒启动一个任务）
async def task_scheduler():
    while True:
        task = await task_queue.get()  # 取出最早的任务
        running_tasks.append(task)
        asyncio.create_task(execute_task(task))  # 并发执行任务
        await asyncio.sleep(5)  # 每秒调度一次

@router.post("/task/add_id")
async def add_task(request: IdRequest):
    task = Task(request)
    await task_queue.put(task)

# 任务执行逻辑
async def execute_task(task: Task):
    result = await task.run()
    running_tasks.remove(task)
    await completed_tasks.put(result)  # 任务完成后放入完成队列

# WebSocket 1：仅在任务队列非空时发送
@router.websocket("/ws/id/tasks")
async def websocket_tasks(websocket: WebSocket):
    await websocket.accept()
    have_data = False
    while True:
        tasks = list(task_queue._queue) + running_tasks
        if tasks:
            have_data = True

        if have_data:
            task_data = [
                {"title": task.request.title, "status": "pending" if task in task_queue._queue else "running"}
                for task in tasks
            ]
            await websocket.send_json(task_data)

        if not tasks:
            have_data = False

        await asyncio.sleep(1)

# WebSocket 2：推送已完成任务
@router.websocket("/ws/id/task_completed")
async def websocket_task_completed(websocket: WebSocket):
    await websocket.accept()
    while True:
        task = await completed_tasks.get()  # 获取完成的任务
        await websocket.send_json({"task_title": task.request.title, "result": task.result})

# 启动调度器
@router.on_event("startup")
async def start_scheduler():
    asyncio.create_task(task_scheduler())