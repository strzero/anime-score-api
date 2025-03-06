origins = [
    "http://localhost:3000"
]

log_file_path = "logs.log"

real_headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
}

timeout = 10

DATABASE_CONFIG = {
    "connections": {
        "default": "mysql://root:so6666@localhost:3306/anime-score"
    },
    "apps": {
        "models": {
            "models": ["models.db_model"],
            "default_connection": "default",
        }
    }
}

logger_exc_info = True

task_queue_interval = 5