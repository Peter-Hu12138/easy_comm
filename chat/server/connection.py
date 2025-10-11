from __future__ import annotations
from typing import TYPE_CHECKING
import threading, socket, select, queue, ssl
import bcrypt
import message, message_sender

ETX = b'\x03'  # End of Text

class ChatRoom():
    id: str
    manager_queue: queue.Queue[message.Message]
    connections: dict[tuple[str, int], ConnectionThread]
    hashed_password: bytes

    def __init__(self, id: str):
        self.connections = {}
        self.id = id
        
    def forward_message(self, message_to_be_forawrded: message.Message):
        src_addr = message_to_be_forawrded.from_addr
        for k in self.connections:
            if k != src_addr:
                print(f"putting message to {self.connections[k]}'s queue")
                self.connections[k].message_forward_queue.put(message_to_be_forawrded)

    def admit(self, ct: ConnectionThread):
        self.connections[ct.addr] = ct
        ct.rooms[self.id] = self

    def set_password(self, password: bytes):
        self.hashed_password = bcrypt.hashpw(password, bcrypt.gensalt())
        
    def check_password(self, password: bytes):
        return bcrypt.checkpw(password, self.hashed_password)
    
    def initiate_secret_exchange(s):
        pass

def drain_ssl(sock: ssl.SSLSocket, on_data) -> tuple[bool, bool, bool]:
    """
    Drain any app data already available in the SSL buffers.
    Returns: (need_read, need_write, closed)
    - need_read: True if we should wait for readability next
    - need_write: True if we should wait for writability next
    - closed: peer performed close_notify or connection closed
    """
    while True:
        try:
            chunk = sock.recv(65536)
            if not chunk:
                return False, False, True  
            on_data(chunk)
            # If OpenSSL still has decrypted bytes, keep draining without select():
            if sock.pending() == 0:
                return True, False, False
            # otherwise loop again (there's more pending)
        except ssl.SSLWantReadError:
            # No more decrypted data right now
            return True, False, False
        except ssl.SSLWantWriteError:
            # Read needs an underlying write first
            return False, True, False
        except ssl.SSLZeroReturnError:
            return False, False, True


class ConnectionThread(threading.Thread):
    addr: tuple[str, int]
    sock: socket.socket

    TLS_secret: bytes

    message_forward_queue: queue.Queue[message.Message]
    rooms: dict[str, ChatRoom]
    manager_queue: queue.Queue[message.Message]
    sender: message_sender.MessageSender

    current_message_built: message.Message | None
    receive_buffer: bytes

    def __init__(self, sock: socket.socket, addr: tuple[str, int], group = None, target = None, name = None, args = ..., kwargs = None, *, daemon = None):
        super().__init__(group, target, name, args, kwargs, daemon=daemon)
        self.sock = sock
        self.addr = addr
        self.message_forward_queue = queue.Queue()
        self.rooms = {}
        self.current_message_built = None
        self.receive_buffer = b''
        self.sender = message_sender.MessageSender()
        self.TLS_secret = b''

    def process_queue(self):
        if not self.message_forward_queue.empty():
            message = self.message_forward_queue.get()
            message.forward(self.sender)
            
    def process_message(self):
        self.manager_queue.put(self.current_message_built)
        self.current_message_built = None

    def process_input(self, chunk: bytes) -> bool:
        # takes in an input, cat it to the end of self.receive_buffer
        # if there is a complete message found, move it to current message built, and returns true
        # otherwise, returns false
        self.receive_buffer += chunk
        idx = self.receive_buffer.find(ETX)
        print(f"Receiving bytes: {chunk} from {self.addr}")
        # TODO: handle server/ client comm thru encryption and decryption
        if idx != -1 and self.current_message_built is None:
            self.current_message_built = message.Message(self.receive_buffer[:idx + 1], self.addr)
            self.receive_buffer = self.receive_buffer[idx + 1:]
            self.process_message()
            return True
        else: 
            return False

    

    def handle_connection(self):
        sock: ssl.SSLSocket = self.sock
        want_write, want_read = False, True
        while True:
            self.process_queue()
            

            need_r, need_w, closed = drain_ssl(sock, self.process_input)
            if closed:
                break
            # Merge needs with existing wants
            want_read  = need_r or want_read
            want_write = need_w or want_write

            # Build interest lists dynamically
            rlist = [sock]
            wlist = [sock] if want_write or self.sender.write_buffer else []
            readable, writable, _ = select.select(rlist, wlist, [], 0.1)

            if writable and not want_read:
                try:
                    self.sender.send(writable[0])
                    want_write = False
                except ssl.SSLWantReadError:
                    want_read, want_write = True, False
                except ssl.SSLWantWriteError:
                    want_write = True
                except ssl.SSLZeroReturnError:
                    break
                
            if readable and not want_write:
                need_r, need_w, closed = drain_ssl(sock, self.process_input)
                if closed:
                    break
                want_read  = need_r
                want_write = need_w
        try:
            sock.close()
        except:
            pass
        print(f"a conn from {self.addr} is closing....")

    def run(self):
        self.handle_connection()
