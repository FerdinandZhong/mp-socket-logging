import logging
import os
import time

from socket_logging import register_handler
from tests.common import TEST_ROUND


def worker(socket_addr, text):
    test_logger = logging.getLogger("test_logger")
    register_handler(test_logger, logging_level=logging.INFO, socket_addr=socket_addr)
    test_logger.setLevel(logging.INFO)
    pid = os.getpid()
    for i in range(TEST_ROUND):
        test_logger.info(f"{i} {text} from {pid}")
        time.sleep(0.01)
