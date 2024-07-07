import selectors
import socket
import types


sel = selectors.DefaultSelector()

HOST, PORT = '127.0.0.1', 8080

lsock = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
lsock.bind((HOST, PORT))
lsock.listen()
print(f"Listening on {HOST, PORT}")
lsock.setblocking(False)

sel.register(fileobj=lsock, 
             events=selectors.EVENT_READ,
             data=None)


def accept_wrapper(sock: socket.socket) -> None:
    conn, addr = sock.accept()
    print(f"Accepted connection from {addr}")
    conn.setblocking(False)
    data = types.SimpleNamespace(addr=addr, inb=b"", outb=b"")
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    sel.register(fileobj=conn, 
                 events=events, 
                 data=data)

def service_connection(key: selectors.SelectorKey, 
                       mask: selectors.EVENT_READ | selectors.EVENT_WRITE) -> None:
    sock = key.fileobj
    data = key.data
    if mask & selectors.EVENT_READ:
        # Reading what data client socket has been sending
        recv_data = sock.recv(1024) # Should be ready to read
        if recv_data:
            data.outb += recv_data
        else:
            print(f"Closing connection to {data.addr}")
            sel.unregister(sock)
            sock.close()
    if mask & selectors.EVENT_WRITE:
        # Sending the data sent by the client socket back to the client
        if data.outb:
            print(f"Echoing {data.outb!r} to {data.addr}")
            sent = sock.send(data.outb) # Should be ready to write
            data.outb = data.outb[sent:]

try:
    while True:
        # Now this is blocking: https://docs.python.org/3/library/selectors.html#selectors.BaseSelector.select 
        events = sel.select(timeout=None)
        for key, mask in events: # a mask or bitmask is data that is used for bitwise operations
            if not key.data:
                # if key.data is None, then you know it’s from the 
                # listening socket and you need to accept the connection
                accept_wrapper(key.fileobj)
            else:
                # If key.data is not None, then you know it’s a client socket 
                # that’s already been accepted, and you need to service it
                service_connection(key, mask)
except KeyboardInterrupt:
    print("Caught Ctrl-C, exiting...") # No point in this really, but I'll leave it here
finally:
    sel.close()