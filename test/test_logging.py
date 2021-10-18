import argparse
import logging
import multiprocessing as mp
import time

from socket_logging import register_handler
from socket_logging import Server, ServerHandler


def worker(text):
    test_logger = logging.getLogger("test_logger")
    register_handler(test_logger, logging_level=logging.INFO)
    test_logger.setLevel(logging.INFO)
    for i in range(500):
        test_logger.info(f"{i} {text}")
        time.sleep(0.01)
        if i % 100 == 0:
            time.sleep(1)


def mp_testing(text):
    procs = [mp.Process(target=worker, args=(text,)) for _ in range(5)]

    for proc in procs:
        proc.start()

    for proc in procs:
        proc.join()
        proc.terminate()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--text", default="client test")
    args = parser.parse_args()

    server_handler = ServerHandler("data/log/socket/test.log", maxBytes=100000)
    server_handler.setLevel(logging.INFO)
    server = Server(server_handler)
    server.start()

    mp_testing(args.text)
    server.stop()
