import glob
import logging
import multiprocessing as mp
import os
import time

import pytest

from socket_logging import Server, ServerHandler
from tests.common import (
    BATCH_SIZE,
    MAX_BYTES,
    TEST_ROUND,
    TEST_TEXT,
    WORKER_NUM,
    log_dir,
    testings,
)
from tests.test_client import worker


def clean_up_dir(dir_path):
    all_log_files = glob.glob(dir_path)

    for log_file in all_log_files:
        os.remove(log_file)


@pytest.mark.parametrize("testing", testings)
def test_mp_logging(testing):
    os.makedirs(log_dir, exist_ok=True)
    server_handler = ServerHandler(testing.log_path, maxBytes=MAX_BYTES)
    server_handler.setLevel(logging.INFO)
    server = Server(
        server_handler, socket_address=testing.socket_address, batch_size=BATCH_SIZE
    )
    server.start()
    procs = [
        mp.get_context(testing.method).Process(
            target=worker,
            args=(
                testing.socket_address,
                TEST_TEXT,
            ),
        )
        for _ in range(WORKER_NUM)
    ]

    for proc in procs:
        proc.start()

    for proc in procs:
        proc.join()
        proc.terminate()

    time.sleep(10)  # wait for all logging finished
    server.stop()

    total_log_lines = 0
    for log_file in glob.glob(f"{testing.log_path}*"):
        assert os.path.getsize(log_file) <= MAX_BYTES + BATCH_SIZE
        with open(log_file, "r") as fp:
            total_log_lines += len(fp.readlines())
    assert total_log_lines >= TEST_ROUND * WORKER_NUM
    clean_up_dir(f"{testing.log_path}*")
