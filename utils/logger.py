import logging
from logging.handlers import RotatingFileHandler
from config import settings

log_handler = RotatingFileHandler(
    filename=settings.log_file_path,
    maxBytes=10 * 1024 * 1024,  # 当日志文件超过 10MB 时清空并重新写入
    backupCount=3,
    encoding="utf-8"
)

log_handler.setLevel(logging.INFO)
log_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

logger = logging.getLogger(__name__)
logger.addHandler(log_handler)
logger.setLevel(logging.INFO)