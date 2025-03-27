import asyncio
import os
from datetime import datetime, timezone
from maintain.download_bangumi_data import download_bangumi_data
from maintain.update_bangumi_data import update_bangumi_data
from utils.client import client
from utils.logger import logger
from models.db_model import Info
from tortoise.exceptions import DBConnectionError

data_dir = os.path.join("maintain", "data")
version_file = os.path.join(data_dir, "db_version.txt")

async def get_local_version_date():
    """ 获取本地存储的数据库更新时间（仅日期） """
    try:
        result = await Info.filter(variable='time').first()
        return result.value[:10] if result else None  # 仅取 YYYY-MM-DD
    except DBConnectionError:
        logger.warning("数据库连接丢失，尝试重新连接...")
        return None

def get_file_version_date():
    """ 获取本地存储的数据库版本文件时间（仅日期） """
    if os.path.exists(version_file):
        timestamp = os.path.getmtime(version_file)
        return datetime.fromtimestamp(timestamp, tz=timezone.utc).strftime('%Y-%m-%d')  # 仅取 YYYY-MM-DD
    return None

async def update_local_version_date(new_date):
    """ 更新本地存储的数据库更新时间（仅日期），仅在需要时更新 """
    try:
        current_local_date = await get_local_version_date()
        if current_local_date != new_date:
            await Info.update_or_create(defaults={'value': new_date}, variable='time')
    except DBConnectionError:
        logger.error("更新数据库版本时间失败，可能是连接丢失")

def update_file_version_date(new_date):
    """ 更新本地数据库版本文件 """
    os.makedirs(data_dir, exist_ok=True)
    with open(version_file, "w") as f:
        f.write(new_date)

async def maintain_db():
    while True:
        try:
            # 获取远程数据库最新版本时间
            response = await client.get(
                'https://raw.githubusercontent.com/bangumi/Archive/refs/heads/master/aux/latest.json')
            web_version_date = response.json().get('created_at', '')[:10]  # 仅取 YYYY-MM-DD

            if not web_version_date:
                logger.error("获取远程数据库版本时间失败")
                await asyncio.sleep(43200)
                continue

            # 获取本地数据库版本时间和文件时间
            local_version_date = await get_local_version_date()

            # 如果 web 和 local 一致，直接更新文件版本时间
            if web_version_date == local_version_date:
                update_file_version_date(web_version_date)
            file_version_date = get_file_version_date()
            
            # 如果 web 与 local 或 file 不一致，则执行更新
            if web_version_date != local_version_date or web_version_date != file_version_date:
                logger.info("Bangumi数据库有新版本，开始更新...")
                if download_bangumi_data():
                    if update_bangumi_data():
                        logger.info("Bangumi数据库更新成功！")
                        update_file_version_date(web_version_date)
                    else:
                        logger.error("Bangumi数据库更新失败！")
                else:
                    logger.error("Bangumi数据库下载失败！")

        except Exception as e:
            logger.error(f"更新Bangumi数据库版本时出错: {e}")

        await asyncio.sleep(43200)  # 每12小时检查一次
