#!/usr/bin/python3

import selectors
import socket
import sys
import types

sel = selectors.DefaultSelector()

def accept_wrapper(sock: socket.socket) -> None:
    """ Function for accepting and registering client connections in selector """
    # here sock will be our listening socket
    conn, addr = sock.accept() # 7A-1. Accept connections. conn now represents one of the client sockets
    print(f"Accepted connection from: {addr}")
    conn.setblocking(False) # 7A-2. Set client socket to be non-blocking
    data = types.SimpleNamespace(addr=addr, inb=b"", outb=b"") # 7A-3. Create "data" object to be stored beside new client socket
    events = selectors.EVENT_READ | selectors.EVENT_WRITE # 7A-4. Set events to be stored beside new client socket
    sel.register(conn, events, data=data) # 7A-5. Register client socket with selector
    # sel.register returns selectors.SelectorKey(fileobj, events, data)


def service_connection(key: selectors.SelectorKey, mask: selectors.EVENT_READ | selectors.EVENT_WRITE):
    """ Function for serving and closing client connections """
    sock: socket.socket = key.fileobj #7B-1. Get socket object from SelectorKey object
    # this socket is the socket we registered in accept_wrapper method
    data: types.SimpleNamespace = key.data #7B-2. Get data from SelectorKey object
    if mask & selectors.EVENT_READ: #7B-3A.
        # 7B-3A-1. If the client socket is ready to be read from - recv data from it
        recv_data = sock.recv(1024) # Should be ready to read
        if recv_data:
            # 7B-3A-2A. Is there is still data sent by the client - add it to the data that the server will send back to the client
            data.outb += recv_data
        else:
            # 7B-3A-2B. If all the data was received from the client - unregister the client socket from selector
            # and close this socket
            print(f"Closing connection to {data.addr}")
            sel.unregister(sock)
            sock.close()
    if mask & selectors.EVENT_WRITE: #7B-3B. If the client socket is ready to be written to - send data to it
        if data.outb:
            print(f"Echoing {data.outb!r} to {data.addr}")
            sent = sock.send(data.outb) # Should be ready to write
            data.outb = data.outb[sent:]


if len(sys.argv) != 3:
    print(f"Usage: {sys.argv[0]} <host> <port>")
    sys.exit(1)

host, port = sys.argv[1], int(sys.argv[2])
lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # 1. Create listening socket
lsock.bind((host, port)) # 2. Bind it to host:port
lsock.listen() # 3. Set it into listening mode
print(f"Listening on {(host, port)}")
lsock.setblocking(False) # 4. Make it non-blocking
sel.register(lsock, selectors.EVENT_READ, data=None) # 5. Register listening socket with selector
# EVENT_READ means that the file object(socket in this case) is ready to be read from or that it is ready to 
# accept connections - it is the listening socket

try:
    while True:
        events: tuple[selectors.SelectorKey, selectors._EventMask] = sel.select(timeout=None) # 6. Select file descriptors that are ready for I/O operations
        # sel.select is blocking with timeout=None, set it to 
        # some value for it to be non-blocking
        for key, mask in events:
            # key stores fileobj(socket), events, data
            # Our listening socket has data set to None and also on the first iteration
            # it is the only registered socket, so we call accept_wrapper
            if key.data is None:
                accept_wrapper(key.fileobj) # 7A. Accept connection if the socket is listening
                # TODO: Add debugs to see how many time this function will be called
            else:
                service_connection(key, mask) # 7B. Serve connection if it is the client socket
except KeyboardInterrupt:
    print("Caught keyboard interrupt, exiting...")
finally:
    sel.close() # we do not close lsock manually, but maybe sel.close does it ???