#!/usr/bin/python3

import selectors
import socket
import sys
import types

sel = selectors.DefaultSelector()
messages: list[bytes] = [b"Message 1 from client.", b"Message 2 from client."]

def start_connections(host: str, port: int, num_conns: int) -> None:
    server_addr = (host, port)
    for i in range(num_conns):
        connid = i + 1
        print(f"Starting connection {connid} to {server_addr}")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setblocking(False)
        sock.connect_ex(server_addr) 
        events = selectors.EVENT_READ | selectors.EVENT_WRITE
        data = types.SimpleNamespace(
            connid=connid,
            msg_total=sum(len(m) for m in messages),
            recv_total=0,
            messages=messages.copy(),
            outb=b""
        )
        sel.register(sock, events, data=data)

def service_connection(key: selectors.SelectorKey, mask: selectors.EVENT_READ | selectors.EVENT_WRITE) -> None:
    sock: socket.socket = key.fileobj
    data = key.data
    if mask & selectors.EVENT_READ:
        recv_data = sock.recv(1024)
        if recv_data:
            print(f"Received {recv_data!r} from connection {data.connid}")
            data.recv_total += len(recv_data)
        if not recv_data or data.recv_total == data.msg_total:
            print(f"Closing connection {data.connid}")
            sel.unregister(sock)
            sock.close()
    if mask & selectors.EVENT_WRITE:
        if not data.outb and data.messages:
            data.outb = data.messages.pop(0)
        if data.outb:
            print(f"Sending {data.outb!r} to connection {data.connid}")
            sent = sock.send(data.outb)
            data.outb = data.outb[sent:]


if len(sys.argv) != 4:
    print(f"Usage: {sys.argv[0]} <host> <port> <num_connections>")
    sys.exit(1)


host, port, num_conns = sys.argv[1:4]
start_connections(host, int(port), int(num_conns)) # 1. Create num_conns client sockets and register them with selector

try:
    while True:
        events: list[tuple[selectors.SelectorKey, selectors.EVENT_READ | selectors.EVENT_WRITE]] = sel.select(timeout=1)
        # 2. Wait for fileobjects to be ready for I/O
        if events:
            for key, mask in events:
                service_connection(key, mask) # 3. Serve client sockets
        # Check for a socket being monitored to continue.
        if not sel.get_map():
            break
except KeyboardInterrupt:
    print("Caught KeyboardInterrupt, exiting")
finally:
    sel.close()