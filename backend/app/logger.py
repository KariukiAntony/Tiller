import logging
import os
from dotenv import load_dotenv, find_dotenv
from termcolor import colored

load_dotenv(find_dotenv())

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

"""
Define custom loggers
"""
file_logger = logging.FileHandler(os.environ.get("logger_file", "logs.log"))
console_logger = logging.StreamHandler()

"""
Set the levels of the loggers
"""
file_logger.setLevel(logging.DEBUG)
console_logger.setLevel(logging.DEBUG)

""" set the formatter"""
formatter = logging.Formatter(
    "%(asctime)s %(levelname)s %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
)

""" set the format of the above loggers """
file_logger.setFormatter(formatter)
console_logger.setFormatter(formatter)

""" add the custom loggers to the logger """
logger.addHandler(file_logger)
logger.addHandler(console_logger)
