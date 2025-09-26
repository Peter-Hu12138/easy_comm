import socket, threading
import select
from ConnectionThread import ConnectionThread

ETX = b'\x03'  # End of Text

def start(port: int):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("localhost", 8000))
    server_socket.listen(5)
    try:
        while True:
            sock, addr = server_socket.accept()
            sock.setblocking(False)
            ct = ConnectionThread(sock=sock, daemon=True,)
            ct.start()
    except KeyboardInterrupt:
        print("ctrl-c detected, existing...")
    finally:
        server_socket.close()
