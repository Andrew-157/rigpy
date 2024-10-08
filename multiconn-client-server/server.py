#!/usr/bin/python3

import selectors
import socket
import sys
import types

# NOTE recv() is like reading from a file and send() is like writing to a file
 
sel = selectors.DefaultSelector()

def accept_wrapper(sock: socket.socket) -> None:
    """ Function for accepting and registering client connections in selector """
    conn, addr = sock.accept()
    print(f"Accepted connection from: {addr}")
    conn.setblocking(False)
    data = types.SimpleNamespace(addr=addr, inb=b"", outb=b"")
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    sel.register(conn, events, data=data)


def service_connection(key: selectors.SelectorKey, mask: selectors.EVENT_READ | selectors.EVENT_WRITE):
    """ Function for serving and closing client connections """
    sock: socket.socket = key.fileobj
    data: types.SimpleNamespace = key.data
    if mask & selectors.EVENT_READ:
        recv_data = sock.recv(1024)
        if recv_data:
            data.outb += recv_data
        else:
            print(f"Closing connection to {data.addr}")
            sel.unregister(sock)
            sock.close()
    if mask & selectors.EVENT_WRITE:
        if data.outb:
            print(f"Echoing {data.outb!r} to {data.addr}")
            sent = sock.send(data.outb) # Should be ready to write
            data.outb = data.outb[sent:]


if len(sys.argv) != 3:
    print(f"Usage: {sys.argv[0]} <host> <port>")
    sys.exit(1)

host, port = sys.argv[1], int(sys.argv[2])
lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
lsock.bind((host, port))
lsock.listen()
print(f"Listening on {(host, port)}")
lsock.setblocking(False)
sel.register(lsock, selectors.EVENT_READ, data=None)

try:
    while True:
        events: list[tuple[selectors.SelectorKey, selectors.EVENT_READ | selectors.EVENT_WRITE]] = sel.select(timeout=None) # 6. Select file descriptors that are ready for I/O operations
        for key, mask in events:
            if key.data is None:
                accept_wrapper(key.fileobj)
            else:
                service_connection(key, mask)
except KeyboardInterrupt:
    print("Caught keyboard interrupt, exiting...")
finally:
    sel.close()