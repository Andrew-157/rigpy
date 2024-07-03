import socket
import time

HOST, PORT = '127.0.0.1', 9999

# TODO: Add selector or any other way to make sock.accept() nonblocking

try:
    with socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM) as sock:
        sock.bind((HOST, PORT))
        sock.listen()
        while True:
            conn, addr = sock.accept()
            data = conn.recv(1024)
            print("Data received from the client")
            with open("./templates/index.html", "r") as file:
                html = file.read()
            to_send = "HTTP/1.1 200\r\nOK\r\n\r\n" + html
            conn.sendall(
    bytes(to_send, "utf-8"))
            conn.close()

except KeyboardInterrupt:
    print("Exiting...")
    exit(0)


