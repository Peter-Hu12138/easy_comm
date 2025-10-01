from __future__ import annotations
from typing import TYPE_CHECKING
import threading

if TYPE_CHECKING:
    import message
    import connection


class MessageHandler:
    conn_threads_lock: threading.Lock
    conn_threads: dict[tuple[str, int], connection.ConnectionThread]

    def __init__(self, conn_threads_lock: threading.Lock, conn_threads: dict[tuple[str, int], connection.ConnectionThread]):
        self.conn_threads_lock = conn_threads_lock
        self.conn_threads = conn_threads
        

    def handle_chat(self, m: message.Message04_Chat):
        print(f"processing message {m.content}")
        self.conn_threads_lock.acquire()
        m.parse_room(self.conn_threads[m.from_addr].rooms)
        self.conn_threads_lock.release()
        m.room.forward_message(m)
    
    def handle_auth():
        pass

    def handle_key_exchange():
        pass