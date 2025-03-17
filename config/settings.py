import os

# origins = [
#     "http://192.168.0.1:3000"
# ]

origins = ["*"]

log_file_path = "logs.log"

real_headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
}

timeout = 10

os.environ.get('SCORE_DB')

database_url = os.environ.get('AS_DB_URL', 'mysql://root:123456@localhost:3306/anime-score')

DATABASE_CONFIG = {
    "connections": {
        "default": database_url
    },
    "apps": {
        "models": {
            "models": ["models.db_model"],
            "default_connection": "default",
        }
    }
}

logger_exc_info = True

task_queue_interval = 3