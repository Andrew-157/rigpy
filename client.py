import socket

HOST, PORT = '127.0.0.1', 8080

with socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM) as sock:
    sock.connect((HOST, PORT))
    sock.sendall(b"Hello world!")
    data = sock.recv(1024)

print(f"Received data {data!r}")