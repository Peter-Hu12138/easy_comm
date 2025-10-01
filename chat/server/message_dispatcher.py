from __future__ import annotations
from typing import TYPE_CHECKING
import threading, queue
import message
import message_dispenser


if TYPE_CHECKING:
    import connection

class MessageDispatcher:
    conn_threads_lock: threading.Lock
    conn_threads: dict[tuple[str, int], connection.ConnectionThread]
    handler: message_dispenser.MessageHandler

    def __init__(self, conn_threads_lock: threading.Lock, 
                 conn_threads: dict[tuple[str, int], connection.ConnectionThread]):
        self.conn_threads = conn_threads
        self.conn_threads_lock = conn_threads_lock
        self.handler = message_dispenser.MessageHandler(conn_threads_lock, conn_threads)
        

    def dispatch(self, m: message.Message) -> message.Message:
        """Decode the raw message and dispatch to it to the right place. """
        match m.type_byte:
            case 4:
                m = message.Message04_Chat(m.to_bytes(), m.from_addr, )
            case _:
                print(f"unexpected manager request {m}")

        m.dispatch(self.handler)

    def process_incoming_from_socket(self):
        type_byte = self.type_byte
        match type_byte:
            # login request
            case 0:
                pass
            # DH public key from host
            case 1:
                pass
            # DH public key from attendents
            case 2:
                pass
            # shared AES secrets over DH exchanged key
            case 3:
                pass
            # normal message over AES
            case 4:
                pass

    def process_incoming_from_queue(self):
        print(f"Relaying message {self} to {self.to.addr}")
        match self.type_byte:
            # login request
            case 0:
                pass
            # DH public key from host
            case 1:
                pass
            # DH public key from attendents
            case 2:
                pass
            # shared AES secrets over DH exchanged key
            case 3:
                pass
            # normal message over AES
            case 4:
                self.to.write_buffer = self.content
