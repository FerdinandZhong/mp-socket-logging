# Small Toolkit for Python Multiprocessing Logging

This is a small toolkit for solving unsafe python mutliprocess logging (file logging and rotation)

## Install

**Only for Python 3.5+**

```sh
pip install mp-socket-logging
```

## Features
- The package uses unix socket for communication between processes.
- I/O operations will all be done by server in main process.
- Client Class itself is a logging.Handler which will be added to user's logger inside child process. Client handler will do the formatting and sending the logs to server side through socket.
- Inside child process, user can do logging as normal with the logger.

## Quick Start

- start a server before in the main process

```python
server_handler = ServerHandler(LOG_FILE, maxBytes=MAX_BYTES)
server_handler.setLevel(logging.INFO)
server = Server(server_handler, batch_size=BATCH_SIZE)
server.start()
```

- register the client to your logger inside multiprocessing worker for sending logs to server through socket
- you can define your own formatter to add to the handler (otherwise a default formatter will be used)

```python
client_logger = logging.getLogger("client_logger")
formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(filename)s- [%(levelname)s]: %(message)s"
)
register_handler(client_logger, logging_level=logging.INFO, formatter=formatter)
client_logger.setLevel(logging.INFO)
```