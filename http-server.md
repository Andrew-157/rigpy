# Primitive HTTP Server in Python using TCP sockets

!["TCP Diagram"](./images/tcp-diagram.png "a title")

## Basic Python Client/Server Using sockets

Server

```python
import socket

HOST = '127.0.0.1'
PORT = 5000

with socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    conn, addr = s.accept()
    with conn:
        print(f"Got connection from {addr}")
        while True:
            data = conn.recv(1024)
            if not data:
                break
            conn.sendall(data)
```

Client

```python
import socket

HOST, PORT = '127.0.0.1', 5000

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    s.sendall(b"Hello World")
    data = s.recv(1024)

print("Received response from server: {}".format(data.decode()))
```

- `socket.AF_INET` - IPv4 IP Address Family
- `socket.SOCK_STREAM` - TCP protocol

What Server Does:

create socket -> bind -> listen -> accept -> recv -> send -> close

What Client Does:

create socket -> connect -> send -> recv -> close

>**NOTE:** `s.accept()` is blocking, so the program just hangs on this line until a client connects.

Running both scripts:

Server Shell:

```bash
Got connection from ('127.0.0.1', 60516)
```

`60516` in the output above is the TCP port number of the client.

Client Shell:

```bash
Received response from server: Hello World
```

## Handling multiple connections

There is a big limitation. When the client uses `s.recv()`, it's possible that it will return only one byte, `b'H'` from `b'Hello, world'`:

```python
...
data = s.recv(1024)
...
```

The `bufsize` argument of 1024 used above is the maximum amount of data to be received at once. It doesn’t mean that .recv() will return 1024 bytes.

The `.send()` method also behaves this way. It returns the number of bytes sent, which may be less than the size of the data passed in. You’re responsible for checking this and calling .send() as many times as needed to send all of the data.

In the example above, this was avoided by using .sendall():

> "Unlike send(), this method continues to send data from bytes until either all data has been sent or an error occurs. None is returned on success."

The above implementations of client and server have 2 limitations:

- They do not handle multiple connections concurrently
- `.send()` and `.recv()` need to be called until all the data is sent or received

For handling multiple connections, concurrency can be used. It can be handled using Asyncio, Multithreading, Multiprocessing.

The below examples will not use the concurrency, though. `selectors` and `.select()` will be used for that.

The `.select()` method allows to check for I/O completion on more than one socket. So `.select()` can be called to see which sockets have I/O ready for reading and/or writing.

## Multi-Connection Client and Server
