from fastapi import WebSocket, WebSocketDisconnect, APIRouter
import asyncio
router = APIRouter()

clients = []
@router.websocket("/ws/task_status")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    clients.append(websocket)

    try:
        while True:
            await asyncio.sleep(1)  # 每秒钟推送一次更新信息

            # 获取所有任务
            tasks = asyncio.all_tasks()

            # 筛选出name以"get"开头的任务
            filtered_tasks = [
                task for task in tasks if task.get_name().startswith("get")
            ]

            # 获取任务数量
            filtered_task_count = len(filtered_tasks)

            # 任务信息
            task_status = [{"name": task.get_name(), "done": task.done()} for task in filtered_tasks]

            # 向 WebSocket 客户端推送筛选后的任务状态以及数量
            await websocket.send_json({
                "task_status": task_status,
                "get_task_count": filtered_task_count
            })

    except WebSocketDisconnect:
        clients.remove(websocket)