"""日志配置"""

import logging
import sys


def setup_logger(name: str = "mask_tool", level: int = logging.INFO) -> logging.Logger:
    """
    配置日志器

    Args:
        name: 日志器名称
        level: 日志级别

    Returns:
        配置好的Logger实例
    """
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logger.setLevel(level)

    handler = logging.StreamHandler(sys.stderr)
    handler.setLevel(level)

    formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger
