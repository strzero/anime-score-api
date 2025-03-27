import asyncio
import os
from datetime import datetime
from maintain.download_bangumi_data import download_bangumi_data
from maintain.update_bangumi_data import update_bangumi_data
from utils.client import client
from utils.logger import logger
from models.db_model import Info
from tortoise.exceptions import DBConnectionError

data_dir = os.path.join("maintain", "data")
version_file = os.path.join(data_dir, "db_version.txt")

async def get_local_version_time():
    """ 获取本地存储的数据库更新时间 """
    try:
        result = await Info.filter(variable='time').first()
        return result.value if result else None
    except DBConnectionError:
        logger.warning("数据库连接丢失，尝试重新连接...")
        return None

def get_file_version_time():
    """ 获取本地存储的数据库版本文件时间 """
    if os.path.exists(version_file):
        return datetime.fromtimestamp(os.path.getmtime(version_file)).isoformat()
    return None

async def update_local_version_time(new_time):
    """ 更新本地存储的数据库更新时间 """
    try:
        await Info.update_or_create(defaults={'value': new_time}, variable='time')
    except DBConnectionError:
        logger.error("更新数据库版本时间失败，可能是连接丢失")

def update_file_version_time(new_time):
    """ 更新本地数据库版本文件 """
    os.makedirs(data_dir, exist_ok=True)
    with open(version_file, "w") as f:
        f.write(new_time)

async def maintain_db():
    while True:
        try:
            # 获取远程数据库最新版本时间
            response = await client.get(
                'https://raw.githubusercontent.com/bangumi/Archive/refs/heads/master/aux/latest.json')
            web_version_time = response.json().get('created_at')

            if not web_version_time:
                logger.error("获取远程数据库版本时间失败")
                await asyncio.sleep(43200)
                continue

            # 先更新数据库时间，避免长时间连接丢失问题
            await update_local_version_time(web_version_time)

            # 获取本地数据库版本时间和文件时间
            local_version_time = await get_local_version_time()
            file_version_time = get_file_version_time()

            if web_version_time != local_version_time or web_version_time != file_version_time:
                logger.info("Bangumi数据库有新版本，开始更新...")
                if download_bangumi_data():
                    if update_bangumi_data():
                        logger.info("Bangumi数据库更新成功！")
                        # await update_local_version_time(web_version_time)
                        update_file_version_time(web_version_time)
                    else:
                        logger.error("Bangumi数据库更新失败！")
                else:
                    logger.error("Bangumi数据库下载失败！")

        except Exception as e:
            logger.error(f"更新Bangumi数据库版本时出错: {e}")

        await asyncio.sleep(43200)  # 每12小时检查一次
