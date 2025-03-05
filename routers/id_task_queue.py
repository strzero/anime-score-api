import asyncio
from fastapi import APIRouter, WebSocket
from models.request_model import IdRequest
from services.task_scheduler import task_queue, task_set, task_scheduler, Task, running_tasks, \
    completed_id_tasks

router = APIRouter()

@router.post("/task/add_id")
async def add_task(request: IdRequest):
    if request.bangumi_id+1 not in task_set:
        task = Task(request)
        await task_queue.put(task)
        task_set.add(request.bangumi_id+1)

@router.websocket("/ws/id/tasks")
async def websocket_tasks(websocket: WebSocket):
    await websocket.accept()
    while True:
        # 筛选出队列中所有任务类型为 IdRequest 的任务
        tasks = [task for task in task_queue._queue if isinstance(task.request, IdRequest)] + \
                [task for task in running_tasks if isinstance(task.request, IdRequest)]

        if tasks:
            task_data = [
                {"title": task.request.title, "status": "pending" if task in task_queue._queue else "running"}
                for task in tasks
            ]
            await websocket.send_json(task_data)

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
