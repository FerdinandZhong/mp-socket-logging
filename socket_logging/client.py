import logging
import signal
import socket
import struct

from .utils import register_logger

LENGTH_BYTE_FORMAT = "!I"


class Client(logging.Handler):
    def __init__(self, socket_addr) -> None:
        super().__init__()
        self.socket = socket.socket(socket.AF_UNIX)
        self.socket.settimeout(1)
        self.logger = logging.getLogger(__name__)
        register_logger(self.logger)
        try:
            self.socket.connect(socket_addr)
            self.logger.info(f"socket connect to /tmp/serving.socket")
        except BrokenPipeError as err:
            self.logger.warning(f"socket is broken: {err}")
        except FileNotFoundError as err:
            self.logger.warning(f"socket file not found: {err}")

    def emit(self, record):
        record = self.format(record)
        try:
            self._send(record.encode())
        except OSError as err:
            self.logger.warning(f"socket send error: {err}")

    def _send(self, byte_data):
        length = struct.pack(LENGTH_BYTE_FORMAT, len(byte_data))
        self.socket.sendall(length + byte_data)

    def _init_termination(self):
        """init signal handler and termination event"""
        signal.signal(signal.SIGTERM, self._terminate)
        signal.signal(signal.SIGINT, self._terminate)

    def _terminate(self, signum, frame):
        """graceful shutdown everything"""
        self.logger.info(f"[{signum}] terminate children processes: {frame}")

        self.socket.close()


def register_handler(
    target_logger, logging_level, formatter=None, socket_addr="/tmp/socket"
):
    if not formatter:
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - [%(levelname)s]: %(message)s"
        )
    client = Client(socket_addr)
    client.setFormatter(formatter)
    client.setLevel(logging_level)
    target_logger.addHandler(client)
