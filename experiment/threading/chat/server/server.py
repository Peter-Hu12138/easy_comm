import socket, threading, queue
import select
from connection import ConnectionThread, ChatRoom, Message

class Manager:
    conn_threads_lock: threading.Lock
    manager_queue: queue.Queue[Message]
    conn_threads: dict[tuple[str, int], ConnectionThread]

    def __init__(self):
        self.conn_threads_lock = threading.Lock()
        self.manager_queue: queue.Queue[Message] = queue.Queue()
        self.conn_threads: dict[tuple[str, int], ConnectionThread] = {}

    def accepting_thread(self, server_socket: socket.socket):
        room = ChatRoom("hi")
        while True:
            sock, addr = server_socket.accept()
            sock.setblocking(False)
            ct = ConnectionThread(sock=sock, daemon=True, addr=addr)
            ct.manager_queue = self.manager_queue
            ct.start()
            self.conn_threads_lock.acquire()
            self.conn_threads[addr] = ct
            self.conn_threads_lock.release()
            room.admit(ct)

    def process_manager_request(self, req: Message):
        match req.type_byte:
            case 0: # room login request
                pass
            case 7: # room build request
                pass
            case 8: # room list request
                pass

            case _: # error handling
                print(f"unexpected manager request {req}")

    def start(self, port: int):
        rooms: dict[str, ChatRoom] = {}
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind(("localhost", 8000))
        server_socket.listen(5)
        threading.Thread(target=self.accepting_thread, kwargs={"server_socket": server_socket}).start()
        try:
            while True:
                if not self.manager_queue.empty():
                    request = self.manager_queue.get()
                    self.process_manager_request(request)        
        except KeyboardInterrupt:
            print("ctrl-c detected, existing...")
        finally:
            server_socket.close()

if __name__ == "__main__":
    manager = Manager()
    manager.start(1)