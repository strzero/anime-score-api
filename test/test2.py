from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
import asyncio
import random

app = FastAPI()

task_queue = asyncio.Queue()
completed_tasks = []

# 模拟异步任务
async def async_task(task_id):
    # 模拟任务执行时间
    await asyncio.sleep(random.uniform(1, 5))
    return f"Task {task_id} completed"

# 任务启动器
async def task_starter():
    while True:
        task_id = await task_queue.get()
        asyncio.create_task(run_task(task_id))
        await asyncio.sleep(1)  # 每秒启动一个任务

# 任务执行和完成处理
async def run_task(task_id):
    result = await async_task(task_id)
    completed_tasks.append(result)

# WebSocket 连接管理
async def send_task_queue(websocket: WebSocket):
    try:
        while True:
            queue_content = list(task_queue._queue)
            await websocket.send_text(f"Current queue: {queue_content}")
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        print("WebSocket disconnected")

async def send_completed_tasks(websocket: WebSocket):
    try:
        while True:
            if completed_tasks:
                task = completed_tasks.pop(0)
                await websocket.send_text(task)
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        print("WebSocket disconnected")

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(task_starter())

@app.get("/")
async def get():
    return HTMLResponse("""
    <html>
        <body>
            <h1>WebSocket Test</h1>
            <p>Open the console to see the output.</p>
            <script>
                const taskQueueSocket = new WebSocket("ws://localhost:8000/ws/task_queue");
                const completedTasksSocket = new WebSocket("ws://localhost:8000/ws/completed_tasks");

                taskQueueSocket.onmessage = function(event) {
                    console.log("Task Queue: ", event.data);
                };

                completedTasksSocket.onmessage = function(event) {
                    console.log("Completed Task: ", event.data);
                };
            </script>
        </body>
    </html>
    """)

@app.websocket("/ws/task_queue")
async def websocket_endpoint_task_queue(websocket: WebSocket):
    await websocket.accept()
    await send_task_queue(websocket)

@app.websocket("/ws/completed_tasks")
async def websocket_endpoint_completed_tasks(websocket: WebSocket):
    await websocket.accept()
    await send_completed_tasks(websocket)

@app.post("/add_task")
async def add_task(task_id: int):
    await task_queue.put(task_id)
    return {"message": f"Task {task_id} added to the queue"}
