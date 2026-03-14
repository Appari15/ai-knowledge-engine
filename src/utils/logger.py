import sys
import os
from loguru import logger

os.makedirs("logs", exist_ok=True)
logger.remove()
logger.add(
    sys.stdout,
    format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
    level="INFO",
    colorize=True,
)
logger.add("logs/app_{time:YYYY-MM-DD}.log", rotation="1 day", retention="7 days", level="DEBUG")
app_logger = logger
