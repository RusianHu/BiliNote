# 注册监听器
from app.utils.logger import get_logger
from events.handlers import cleanup_temp_files
from events.signals import transcription_finished, note_generation_finished

logger = get_logger(__name__)

def register_handler():
    try:
        # 不再在转写完成后清理文件
        # transcription_finished.connect(cleanup_temp_files)
        
        # 在笔记生成完成后清理文件
        note_generation_finished.connect(cleanup_temp_files)
        logger.info("注册监听器成功")
    except Exception as e:
        logger.error(f"注册监听器失败:{e}")