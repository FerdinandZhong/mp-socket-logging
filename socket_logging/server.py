import logging
import os
import selectors
import signal
import socket
import struct
import time
from logging.handlers import RotatingFileHandler
from threading import Event, Thread

from .utils import register_logger

LENGTH_BYTE_LENGTH = 4
LENGTH_BYTE_FORMAT = "!I"
LINE_BREAK = b"\n"


def recv_all(conn, length):
    buffer = bytearray(length)
    mv = memoryview(buffer)
    size = 0
    while size < length:
        packet = conn.recv_into(mv)
        mv = mv[packet:]
        size += packet
    return buffer


class ServerHandler(RotatingFileHandler):
    def __init__(self, filename, maxBytes, suffix="%Y-%m-%d.%H%M%S"):
        """Preferred handler for server to do file logging and rotation

        The class is inherited from logging.handlers.RotatingFileHandler
        but with a redefined rotating function including:

            - Renaming Old log files a suffix (default timestamp suffix with format "%Y-%m-%d.%H%M%S")
            - Don't remove files exceed the limit of backupcount

        Due to the server's batching methodology, the rotated file size is less than "maxbytes + batch_size"

        Args:
            filename (str): filename of log file
            maxBytes (int): max byte before rotation
            suffix (str, optional): suffix of rotated files. Defaults to "%Y-%m-%d.%H%M%S".
        """
        self.suffix = suffix  # timestamp marked for rotation file
        super().__init__(filename=filename, maxBytes=maxBytes)

    def doRollover(self):
        """
        Function for doing rollover
        """
        if self.stream:
            self.stream.close()
            self.stream = None
        currentTime = int(time.time())
        timeTuple = time.localtime(currentTime)
        dfn = self.rotation_filename(
            self.baseFilename + "." + time.strftime(self.suffix, timeTuple)
        )
        if os.path.exists(dfn):
            os.remove(dfn)

        self.rotate(self.baseFilename, dfn)
        self.stream = self._open()

    def shouldRollover(self):
        """
        Determine if rollover should occur.

        Basically, see if the supplied record would cause the file to exceed
        the size limit we have.
        """
        if self.maxBytes > 0:  # are we rolling over?
            self.stream.seek(0, 2)  # due to non-posix-compliant Windows feature
            if self.stream.tell() >= self.maxBytes:
                return True

        return False

    def emit(self, record):
        try:
            if self.shouldRollover():
                self.doRollover()
            if isinstance(record, str):
                self.stream.write(record + self.terminator)
                self.flush()
            else:
                logging.FileHandler.emit(self, record)
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception:
            self.handleError(record)


class Server:
    def __init__(
        self,
        defined_handler: logging.Handler,
        server_address="/tmp/socket",
        batch_size=20000,
    ) -> None:
        """Server for receiving logs from client and do writting logs in batch to files.

        Args:
            defined_handler (RotatingFileHandler): [handler for writing logs, preferred "ServerHandler"]
            server_address (str, optional): [server socket address]. Defaults to "/tmp/socket".
            batch_size (int, optional): [batch size for writting logs to file in batch]. Defaults to 20000.
        """
        try:
            os.remove(server_address)
        except OSError:
            pass
        self.logger = logging.getLogger(__name__)
        register_logger(self.logger)

        self.socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.socket.bind(server_address)
        self.socket.listen()
        self.logger.info(f"listening on {server_address}")
        self.socket.setblocking(False)

        self.sel = selectors.DefaultSelector()
        self.sel.register(self.socket, selectors.EVENT_READ, data=self.accept)

        self.handler = defined_handler
        self.thread = Thread(target=self.run)
        self.batch_size = batch_size
        self.bytes = bytearray()
        self.total_length = 0

    def accept(self, sock):
        conn, addr = sock.accept()  # Should be ready to read
        self.logger.info(f"accepted connection from {addr}")
        conn.setblocking(False)
        events = selectors.EVENT_READ
        self.sel.register(conn, events, data=self.read_data)
        if self.termination.is_set():
            self.sel.unregister(sock)

    def read_data(self, conn):
        length_bytes = conn.recv(LENGTH_BYTE_LENGTH)
        if length_bytes:
            length = struct.unpack(LENGTH_BYTE_FORMAT, length_bytes)[0]
            self.total_length += length
            payload = recv_all(conn, length)
            self.bytes += payload
            if self.total_length >= self.batch_size:
                self.handler.emit(self.bytes.decode())
                self.bytes = bytearray()
                self.total_length = 0
            else:
                self.bytes += LINE_BREAK
        if self.termination.is_set():
            self.logger.info(f"current total length {self.total_length}")
            self.handler.emit(self.bytes.decode())
            self.bytes = bytearray()
            self.sel.unregister(conn)
            conn.close()

    def _init_termination(self):
        """init signal handler and termination event"""
        self.termination = Event()
        signal.signal(signal.SIGTERM, self._terminate)
        signal.signal(signal.SIGINT, self._terminate)

    def _terminate(self, signum, frame):
        """graceful shutdown everything"""
        self.logger.info(f"[{signum}] terminate server: {frame}")

        self.termination.set()

    def run(self):
        assert self.handler, "no handler set up"
        self.logger.info("server is running")
        while True:
            events = self.sel.select(timeout=None)
            for key, _ in events:
                callback = key.data
                callback(key.fileobj)
            if self.termination.is_set():
                self.logger.info("termination is set")
                break
        self.socket.close()
        self.sel.close()

    def start(self):
        self._init_termination()
        self.thread.start()

    def stop(self):
        self._terminate(signal.SIGTERM, "stop server")
