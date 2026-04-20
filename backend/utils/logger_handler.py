import logging
from logging.handlers import RotatingFileHandler
from backend.utils.path_tool import get_abs_path
import os
from datetime import  datetime

LOG_ROOT = get_abs_path('logs')

os.makedirs(LOG_ROOT, exist_ok=True)

DEFAULT_LOG_FORMAT = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
)

def get_logger(
        name = 'rag',
        console_lv = logging.INFO,
        file_lv = logging.DEBUG,
        log_file = None
) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    if logger.handlers:
        return logger

    console_handler = logging.StreamHandler()
    console_handler.setLevel(console_lv)
    console_handler.setFormatter(DEFAULT_LOG_FORMAT)

    logger.addHandler(console_handler)

    if not log_file:
        log_file = os.path.join(LOG_ROOT, f'{name}_{datetime.now().strftime('%Y%m%d')}.log')
    # file_handler = logging.FileHandler(log_file, encoding='utf-8')
    # 轮转
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(file_lv)
    file_handler.setFormatter(DEFAULT_LOG_FORMAT)

    logger.addHandler(file_handler)

    return logger

logger = get_logger()

if __name__ == '__main__':
    logger.info('info')
    logger.error('error')
    logger.warning('warning')
    logger.debug('debug')

