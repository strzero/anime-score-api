import asyncio
from maintain.download_bangumi_data import download_bangumi_data
from maintain.update_bangumi_data import update_bangumi_data
from utils.client import client
from utils.logger import logger
from models.db_model import Info
from tortoise.exceptions import DBConnectionError


async def get_local_version_time():
    """ 获取本地存储的数据库更新时间 """
    try:
        # 获取第一个匹配的字段 'value'
        result = await Info.filter(variable='time').values_list('value', flat=True).first()
        return result if result else None
    except DBConnectionError:
        logger.warning("数据库连接丢失，尝试重新连接...")
        return None


async def update_local_version_time(new_time):
    """ 更新本地存储的数据库更新时间 """
    try:
        await Info.filter(variable='time').update(value=new_time)
    except DBConnectionError:
        logger.error("更新数据库版本时间失败，可能是连接丢失")


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

            # 获取本地数据库版本时间
            local_version_time = await get_local_version_time()

            if web_version_time != local_version_time:
                logger.info("Bangumi数据库有新版本，开始更新...")
                if download_bangumi_data():
                    if update_bangumi_data():
                        logger.info("Bangumi数据库更新成功！")
                        await update_local_version_time(web_version_time)
                    else:
                        logger.error("Bangumi数据库更新失败！")
                else:
                    logger.error("Bangumi数据库下载失败！")

        except Exception as e:
            logger.error(f"更新Bangumi数据库版本时出错: {e}")

        await asyncio.sleep(43200)  # 每12小时检查一次
