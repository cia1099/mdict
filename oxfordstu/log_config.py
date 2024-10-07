import logging
import logging.config


# 自定义过滤器，只允许特定日志级别
class MaxLevelFilter(logging.Filter):
    def __init__(self, max_level):
        self.max_level = max_level
        super().__init__()

    def filter(self, record):
        # 只允许小于等于 max_level 的日志通过
        return record.levelno <= self.max_level


class JsonFormatter(logging.Formatter):
    def format(self, record):
        import json, re

        dict_record = {
            "asctime": self.formatTime(record, self.datefmt),  # 格式化时间
            "levelname": record.levelname,  # 日志级别
            "message": record.getMessage(),  # 日志消息
            "name": record.name,  # 日志记录器名称
            "pathname": record.pathname,  # 完整文件路径
            "filename": record.filename,
            "msecs": int(record.msecs),
            "lineno": record.lineno,  # 行号
            "funcName": record.funcName,  # 函数名
            "thread": record.thread,  # 线程ID
            "process": record.process,  # 进程ID
            "created": int(record.created),
        }
        matches = re.findall(r"%\((.*?)\)", self._fmt)
        obj = {}
        for k in matches:
            if not k in dict_record.keys():
                continue
            obj[k] = dict_record[k]

        return f"{json.dumps(obj)},"


LOGGER_SETTINGS = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "debug_formatter": {
            "class": "logging.Formatter",
            "datefmt": "\x1b[32m%H:%M:%S\x1b[0m",
            "format": "[\x1b[32m%(levelname)s\x1b[0m]: %(message)s %(asctime)s\x1b[31m@\x1b[0m%(filename)s:\x1b[35m%(lineno)d\x1b[0m",
        },
        "console_formatter": {
            "class": "logging.Formatter",
            "datefmt": "\x1b[32m%H:%M:%S\x1b[0m",
            "format": "[\x1b[34m%(levelname)s\x1b[0m]: %(message)s %(asctime)s\x1b[31m@\x1b[0m%(filename)s:\x1b[35m%(lineno)d\x1b[0m",
        },
        "file_formatter": {
            "()": JsonFormatter,
            "datefmt": "%Y/%m/%d-%H:%M:%S",
            "format": "%(message)s %(filename)s:%(lineno)d %(levelname)s",
        },
    },
    "filters": {
        "only_debug": {
            "()": MaxLevelFilter,
            "max_level": logging.DEBUG,
        },
    },
    "handlers": {
        "debug_console": {
            "class": "logging.StreamHandler",  # "rich.logging.RichHandler",  # could use logging.StreamHandler instead
            "level": "DEBUG",
            "formatter": "debug_formatter",
            "filters": ["only_debug"],
        },
        "console": {
            "class": "logging.StreamHandler",  # could use logging.StreamHandler instead
            "level": "INFO",
            "formatter": "console_formatter",
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "DEBUG",
            "formatter": "file_formatter",
            "filename": "dict_oxfordstu.log",
            "maxBytes": 1024,  # 1 kB
            # "backupCount": 0,
            "encoding": "utf8",
        },
    },
    "loggers": {
        "oxfordstu": {
            "level": "DEBUG",
            "handlers": ["debug_console", "console", "file"],
            "propagate": False,  # 防止日志冒泡到根记录器
        },
    },
}
logging.config.dictConfig(LOGGER_SETTINGS)
log = logging.getLogger("oxfordstu")

if __name__ == "__main__":
    log.addHandler(logging.NullHandler())
    # 示例日志
    log.debug("This is a debug message")
    log.info("This is an info message")
    log.warning("This is a warning message")
    log.error("This is an error message")
    log.critical("This is a critical message")
