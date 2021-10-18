import argparse
import logging
import multiprocessing as mp
import time
import os
import glob
from pathlib import Path

from socket_logging import register_handler
from socket_logging import Server, ServerHandler
import shutil
import pytest

MAX_BYTES = 200000
BATCH_SIZE = 2000
TEST_DIR = "data/log"
TEST_FILE = "test.log"
TEST_TEXT = "logging test"
TEST_ROUND = 2000
WORKER_NUM = 5


log_path = str(Path(os.getcwd()).joinpath(TEST_DIR, TEST_FILE))
log_dir = str(Path(os.getcwd()).joinpath(TEST_DIR))
if os.path.exists(log_dir):
    shutil.rmtree(log_dir)
os.makedirs(log_dir)

server_handler = ServerHandler(log_path, maxBytes=MAX_BYTES)
server_handler.setLevel(logging.INFO)
server = Server(server_handler, batch_size=BATCH_SIZE)
server.start()

def clean_up_dir(dir_path):
    all_log_files = glob.glob(dir_path)

    for log_file in all_log_files:
        os.remove(log_file)


def worker(text):
    test_logger = logging.getLogger("test_logger")
    register_handler(test_logger, logging_level=logging.INFO)
    test_logger.setLevel(logging.INFO)
    pid = os.getpid()
    for i in range(TEST_ROUND):
        test_logger.info(f"{i} {text} from {pid}")
        time.sleep(0.01)


@pytest.mark.parametrize("method", ["spawn", "fork"])
def test_mp_logging(method):
    procs = [mp.get_context(method).Process(target=worker, args=(TEST_TEXT,)) for _ in range(WORKER_NUM)]

    for proc in procs:
        proc.start()

    for proc in procs:
        proc.join()
        proc.terminate()

    time.sleep(10) # wait for all logging finished
    server.stop()

    total_log_lines = 0
    for log_file in glob.glob(f"{log_dir}/*"):
        assert os.path.getsize(log_file) <= MAX_BYTES + BATCH_SIZE
        with open(log_file, "r") as fp:
            total_log_lines += len(fp.readlines())
    assert total_log_lines >= TEST_ROUND * WORKER_NUM
    clean_up_dir(f"{log_dir}/*")
