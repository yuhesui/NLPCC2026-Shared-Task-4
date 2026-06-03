import os
import sys

from loguru import logger

from config import LOGGING


def setup_logger():
    """
    Configures a global logger for the application.
    """
    # Remove any default handlers
    logger.remove()

    # Configure console logging
    logger.add(
        sys.stdout,
        level=LOGGING["LEVEL"],
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        colorize=True,
    )

    # Configure file logging for the server
    log_dir = LOGGING["LOG_DIR"]
    os.makedirs(log_dir, exist_ok=True)
    enqueue_logs = os.environ.get("NLPCC_LOGURU_ENQUEUE", "0").lower() in {"1", "true", "yes"}
    server_log_path = log_dir / LOGGING["SERVER_LOG_FILE"]
    logger.add(
        server_log_path,
        level=LOGGING["LEVEL"],
        # rotation=LOGGING["ROTATION"],  # 不要rotation啊我干
        # retention=LOGGING["RETENTION"],
        enqueue=enqueue_logs,
        backtrace=True,
        diagnose=True,
        format="{time} {level} {message}",
        filter=lambda record: "server_platform" in record["extra"],
    )

    # Configure file logging for the agent
    agent_log_path = LOGGING["LOG_DIR"] / LOGGING["AGENT_LOG_FILE"]
    logger.add(
        agent_log_path,
        level=LOGGING["LEVEL"],
        # rotation=LOGGING["ROTATION"],
        # retention=LOGGING["RETENTION"],
        enqueue=enqueue_logs,
        backtrace=True,
        diagnose=True,
        format="{time} {level} {message}",
        filter=lambda record: "agent_platform" in record["extra"],
    )

    return logger


# Create a globally accessible logger instance
log = setup_logger()

# Create context-specific loggers
server_logger = log.patch(lambda record: record["extra"].update(server_platform=True))
agent_logger = log.patch(lambda record: record["extra"].update(agent_platform=True))
