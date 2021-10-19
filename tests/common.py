import os
from collections import namedtuple
from pathlib import Path

Testing = namedtuple("Testing", ("socket_address", "method", "log_path"))


METHODS = ["spawn", "fork"]
MAX_BYTES = 200000
BATCH_SIZE = 2000
TEST_DIR = "data/log"
TEST_FILE = "test_{method}.log"
TEST_TEXT = "logging test"
TEST_ROUND = 2000
WORKER_NUM = 5
SOCKET_ADDR = "/tmp/{method}.socket"

log_dir = str(Path(os.getcwd()).joinpath(TEST_DIR))

testings = []

for method in METHODS:
    log_path = str(
        Path(os.getcwd()).joinpath(TEST_DIR, TEST_FILE.format(method=method))
    )

    socket_address = SOCKET_ADDR.format(method=method)

    testings.append(
        Testing(socket_address=socket_address, method=method, log_path=log_path)
    )
