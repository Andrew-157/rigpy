#!/usr/bin/python

import socket
import selectors
import sys
import types

class Server:
    def __init__(self, host: str, port: int, selector_timeout: int | None = None) -> None:
        self.__host = host
        self.__port = port
        self.__sel = selectors.DefaultSelector()
        self.__server_events = selectors.EVENT_READ
        self.__client_events = selectors.EVENT_READ | selectors.EVENT_WRITE
        self.__sock: socket.socket | None = None
        self.__server_socket_type: str = "server"
        self.__client_socket_type: str = "client"
        self.__init_socket()
        self.__selector_timeout = selector_timeout
    
    def addr(self) -> tuple[str, int]:
        return (self.__host, self.__port)

    def __init_socket(self):
        """ Initialize Listening TCP IPv4 Socket """
        sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
        self.__sock = sock
        sock.bind(self.addr())
        sock.listen()
        print(f"Server Listens on {self.addr()}")
        sock.setblocking(False)
        data = types.SimpleNamespace(type=self.__server_socket_type)
        self.__sel.register(sock, events=self.__server_events, data=data)

    def __repr__(self) -> str:
        return f"Address:{self.addr()}|Type:{self.__server_socket_type}"


    def __str__(self) -> str:
        return self.__repr__()
    

    def __accept_connections(self) -> None:
        conn, addr = self.__sock.accept()
        print(f"Accepted connection from client on: {addr}")
        conn.setblocking(False)
        data = types.SimpleNamespace(type=self.__client_socket_type, addr=addr)
        self.__sel.register(conn, events=self.__client_events, data=data)

    def __serve_connections(self, key: selectors.SelectorKey, mask: selectors.EVENT_READ | selectors.EVENT_WRITE) -> None:
        sock: socket.socket = key.fileobj
        data = key.data
        if mask & selectors.EVENT_READ:
            data_from_client = sock.recv(4096)
            print(f"Received Data from client on addr: {data.addr}")
            print(data_from_client.decode())
        elif mask & selectors.EVENT_WRITE:
            minimal_http_response = b"HTTP/1.1 200 OK"
            print("Sending minimal HTTP Response")
            sock.sendall(minimal_http_response)
            sock.close()
            self.__sel.unregister(sock)

    def run(self) -> None:
        try:
            while True:
                for key, mask in self.__sel.select(timeout=self.__selector_timeout):
                    if key.data.type == self.__server_socket_type:
                        self.__accept_connections()
                    else:
                        self.__serve_connections(key, mask)
        except KeyboardInterrupt:
            print("Caught Ctrl-C, exiting...")
        finally:
            self.__sel.close()
            sys.exit(0)


if __name__ == "__main__":
    server = Server("127.0.0.1", 9000, 1)
    server.run()