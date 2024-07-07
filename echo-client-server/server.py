import socket

HOST, PORT = '127.0.0.1', 8080

with socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM) as sock:
    # AF_INET - IPv4 IP addresses
    # SOCK_STREAM - TCP
    sock.bind((HOST, PORT))
    sock.listen()
    conn, addr = sock.accept() #  blocks execution and waits for an incoming connection
    with conn:
        print(f"Connected by {addr}")
        while True:
            data = conn.recv(1024)
            if not data:
                break
            conn.sendall(data)