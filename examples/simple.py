import argparse
import logging
import multiprocessing as mp
import os
import time

from socket_logging import Server, ServerHandler, register_handler

MAX_BYTES = 100000
BATCH_SIZE = 2000
LOG_FILE = "data/log/socket.log"
TEST_ROUND = 500
WORKER_NUM = 5


def worker(text):
    client_logger = logging.getLogger("client_logger")
    register_handler(client_logger, logging_level=logging.INFO)
    client_logger.setLevel(logging.INFO)
    pid = os.getpid()
    for i in range(TEST_ROUND):
        client_logger.info(f"{i} {text} from {pid}")
        time.sleep(0.01)


def sample_running(text):
    procs = [
        mp.get_context("spawn").Process(target=worker, args=(text,))
        for _ in range(WORKER_NUM)
    ]

    for proc in procs:
        proc.start()

    for proc in procs:
        proc.join()
        proc.terminate()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--text", default="client test")
    args = parser.parse_args()

    server_handler = ServerHandler(LOG_FILE, maxBytes=MAX_BYTES)
    server_handler.setLevel(logging.INFO)
    server = Server(server_handler, batch_size=BATCH_SIZE)
    server.start()

    sample_running(args.text)
    server.stop()
