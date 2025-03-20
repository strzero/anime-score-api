import asyncio
from maintain.download_bangumi_data import download_bangumi_data
from models.db_model import Info
from maintain.update_bangumi_data import update_bangumi_data
from utils.client import client
from utils.logger import logger

async def maintain_db():
    while(True):
        try:
            response = await client.get('https://raw.githubusercontent.com/bangumi/Archive/refs/heads/master/aux/latest.json')
            web_version_time = response.json()['created_at']
            local = await Info.filter(variable='time').first()
            local_version_time = local.value
            if(web_version_time != local_version_time):
                logger.info("Bangumi数据库有新版本，开始更新...")
                download_status = download_bangumi_data()
                if download_status:
                    update_status = update_bangumi_data()
                    if update_status:
                        logger.info("Bangumi数据库更新成功！")
                        local.value = web_version_time
                        await local.save()
                    else:
                        logger.error("Bangumi数据库更新失败！")
                else:
                    logger.error("Bangumi数据库下载失败！")
        except Exception as e:
            logger.error(f"更新Bangumi数据库版本时出错: {e}")

        await asyncio.sleep(43200)