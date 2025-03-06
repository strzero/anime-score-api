import asyncio
from config import settings
from models.request_model import ScoreRequest, IdRequest
from services.get_web_data import get_four_score, get_four_id
from services.task_action import id_task_action, score_task_action
from utils.logger import logger

# 任务管理
task_queue = asyncio.Queue()  # 存放待执行任务
completed_score_tasks = asyncio.Queue()
completed_id_tasks = asyncio.Queue()
running_tasks = []
bgmid_to_uuid_getid = {}
bgmid_to_uuid_getscore = {}
task_results = {}

class Task:
    def __init__(self, request, uuid):
        self.uuid = uuid
        self.request = request
        self.completed = False
        self.result = None

    async def run(self):
        if isinstance(self.request, ScoreRequest):
            self.result = await score_task_action(self.request)
            bgmid_to_uuid_getscore.pop(self.request.bangumi_id, '')
        elif isinstance(self.request, IdRequest):
            self.result = await id_task_action(self.request)
            bgmid_to_uuid_getid.pop(self.request.bangumi_id, '')
        self.completed = True
        task_results[self.uuid] = self.result
        logger.info(task_results)
        return self

# 任务调度器（每秒启动一个任务）
async def task_scheduler():
    while True:
        if not task_queue.empty():  # 如果队列不为空
            task = await task_queue.get()  # 取出最早的任务

            running_tasks.append(task)
            asyncio.create_task(execute_task(task))  # 并发执行任务
            await asyncio.sleep(settings.task_queue_interval)  # 每秒调度一次
        else:
            await asyncio.sleep(0.1)  # 队列为空时，稍等片刻再继续检查

# 任务执行逻辑
async def execute_task(task: Task):
    result = await task.run()
    running_tasks.remove(task)
    if isinstance(task.request, ScoreRequest):  # 如果是 ScoreRequest 类型的任务
        await completed_score_tasks.put(result)  # 放入对应的队列
    elif isinstance(task.request, IdRequest):  # 如果是 IdRequest 类型的任务
        await completed_id_tasks.put(result)  # 放入对应的队列

