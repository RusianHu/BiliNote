from celery import Celery
from dotenv import load_dotenv
import os

# 加载 .env 文件中的环境变量
load_dotenv()

# 从环境变量中读取配置（可适配不同环境）
BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
BACKEND_URL = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")

# 初始化 Celery 实例
celery_app = Celery(
    "bilinote",
    broker=BROKER_URL,
    backend=BACKEND_URL,
)

# 基础配置
celery_app.conf.update(
    task_track_started=True,     # 任务启动时即可记录状态
    task_time_limit=600,         # 每个任务最大运行时间（秒）
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="Asia/Shanghai",    # 设置时区
    enable_utc=False,
)
