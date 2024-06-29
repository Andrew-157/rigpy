import socket
import time

HOST, PORT = '127.0.0.1', 9999


try:
    with socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM) as sock:
        sock.bind((HOST, PORT))
        sock.listen()
        while True:
            conn, addr = sock.accept()
            data = conn.recv(1024)
            print("Data received from the client")
            print(data)
            conn.sendall(
    bytes(f"""HTTP/1.1 200 OK\r\nContent-type: text/html\r\n
    \r\n
    <!doctype html>
    <html>
        <head/>
        <body>
            <h1>Welcome to the server!</h1>
        </body>
    </html>
    \r\n\r\n
    """, "utf-8"))
            conn.close()

except KeyboardInterrupt:
    print("Exiting...")
    exit(0)


