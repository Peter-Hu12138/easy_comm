import socket, threading, queue
import connection, message, message_dispatcher
import select
import traceback

class Manager:
    conn_threads_lock: threading.Lock
    conn_threads: dict[tuple[str, int], connection.ConnectionThread]
    rooms: dict[str, connection.ChatRoom]

    manager_queue: queue.Queue[message.Message]

    dispacher: message_dispatcher.MessageDispatcher

    def __init__(self):
        self.conn_threads_lock = threading.Lock()
        self.manager_queue: queue.Queue[message.Message] = queue.Queue()
        self.conn_threads: dict[tuple[str, int], connection.ConnectionThread] = {}
        self.rooms: dict[str, connection.ChatRoom] = {}
        self.dispacher = message_dispatcher.MessageDispatcher(self.conn_threads_lock, self.conn_threads)

    def accepting_thread(self, server_socket: socket.socket):
        room = connection.ChatRoom("hi")
        while True:
            sock, addr = server_socket.accept()
            sock.setblocking(False)
            ct = connection.ConnectionThread(sock=sock, daemon=True, addr=addr)
            ct.manager_queue = self.manager_queue
            ct.start()
            self.conn_threads_lock.acquire()
            self.conn_threads[addr] = ct
            self.conn_threads_lock.release()
            room.admit(ct)

    def process_manager_request(self, req: message.Message):
        self.dispacher.dispatch(req)

    def start(self, port: int):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind(("localhost", 8000))
        server_socket.listen(5)
        threading.Thread(target=self.accepting_thread, kwargs={"server_socket": server_socket}).start()
        try:
            while True:
                try:
                    if not self.manager_queue.empty():
                        request = self.manager_queue.get()
                        self.process_manager_request(request)
                except KeyboardInterrupt:
                    raise KeyboardInterrupt
                except Exception as e:
                    traceback.print_exc()
                    print(f"error, continuing")

        except KeyboardInterrupt:
            print("ctrl-c detected, existing...")
        # except Exception as e:
        #     print(f"unexpected error {e}")
        finally:
            server_socket.close()
        print("main thread exiting")

if __name__ == "__main__":
    manager = Manager()
    manager.start(1)