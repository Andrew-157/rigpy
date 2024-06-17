import socket
import select

if __name__ == "__main__":

    listener_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listener_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    address_port = ('127.0.0.1', 7722)
    listener_socket.bind(address_port)

    listener_socket.listen(1)
    print("Server is listening at 127.0.0.1:7722")


    while True:
        read_ready_sockets, _, _ = select.select(
            [listener_socket], [], [], 0
        )

        if read_ready_sockets:

            for ready_socket in read_ready_sockets:

                client_socket, client_address = ready_socket.accept()
                client_msg = client_socket.recv(4096)
                print(f"Client said: {client_msg.decode('utf-8')}")

                client_socket.sendall(b"Welcome to the server!\n")

                try:
                    client_socket.close()
                except OSError:
                    pass