"""
Utilities for logging.
"""

import logging
import sys


class ColoredFormatter(logging.Formatter):
    COLORS = {
        "INFO": "\033[92m",  # Green
        "WARNING": "\033[93m",  # Yellow
        "ERROR": "\033[91m",  # Red
        "DEBUG": "\033[94m",  # Blue
        "CRITICAL": "\033[95m",  # Magenta
    }
    GREY = "\033[90m"
    RESET = "\033[0m"

    def format(self, record):
        level_color = self.COLORS.get(record.levelname, "")
        formatted = (
            f"{level_color}[{record.levelname}]{self.RESET} {self.GREY}{record.name}:{self.RESET} {record.getMessage()}"
        )
        return formatted


FORMATTER = ColoredFormatter()
LEVEL = logging.INFO


class ConsoleHandler(logging.StreamHandler):
    """
    A handler that logs to console in the sensible way.
    StreamHandler can log to *one of* sys.stdout or sys.stderr.
    It is more sensible to log to sys.stdout by default with only error
    (logging.ERROR and above) messages going to sys.stderr. This is how
    ConsoleHandler behaves.
    """

    def __init__(self, level, formatter=FORMATTER):
        logging.StreamHandler.__init__(self)
        self.stream = None  # reset it; we are not going to use it anyway
        self.setLevel(level)
        self.setFormatter(formatter)

    def emit(self, record):
        if record.levelno >= logging.ERROR:
            self.__emit(record, sys.stderr)
        else:
            self.__emit(record, sys.stdout)

    def __emit(self, record, strm):
        self.stream = strm
        logging.StreamHandler.emit(self, record)

    def flush(self):
        # Workaround a bug in logging module
        # See:
        #   http://bugs.python.org/issue6333
        if self.stream and hasattr(self.stream, "flush") and not self.stream.closed:
            logging.StreamHandler.flush(self)


# Configure root logger to use our custom formatter
root_logger = logging.getLogger()
root_logger.setLevel(LEVEL)
root_logger.handlers.clear()
root_logger.addHandler(ConsoleHandler(LEVEL, FORMATTER))


def get_logger(name, level=LEVEL, handlers=[ConsoleHandler(LEVEL, FORMATTER)]):
    return logging.getLogger(name)


def set_level(level):
    logging.getLogger().setLevel(level)
