import socket, threading, queue
import select
from connection import ConnectionThread, ChatRoom

conn_threads_lock = threading.Lock()
conn_threads: dict[tuple[str, int], ConnectionThread] = {}

def accepting_thread(server_socket: socket.socket):
    global conn_threads
    global conn_threads_lock
    while True:
        sock, addr = server_socket.accept()
        sock.setblocking(False)
        ct = ConnectionThread(sock=sock, daemon=True, addr=addr)
        ct.start()
        conn_threads_lock.acquire()
        conn_threads[addr] = ct

def start(port: int):
    manager_queue = queue.Queue()
    rooms: dict[str, ChatRoom] = {}
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("localhost", 8000))
    server_socket.listen(5)
    threading.Thread(target=accepting_thread, kwargs={"server_socket": server_socket})
    try:
        while True:
            rooms[0]
    
             
    except KeyboardInterrupt:
        print("ctrl-c detected, existing...")
    finally:
        server_socket.close()

if __name__ == "__main__":
    start(1)