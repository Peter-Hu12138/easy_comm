from __future__ import annotations
from typing import TYPE_CHECKING
import threading, socket, select, queue
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

class ConnectionThread(threading.Thread):
    addr: tuple[str, int]
    sock: socket.socket

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

        if idx != -1 and self.current_message_built is None:
            self.current_message_built = message.Message(self.receive_buffer[:idx + 1], self.addr)
            self.receive_buffer = self.receive_buffer[idx + 1:]
            self.process_message()
            return True
        else: 
            return False

    def handle_connection(self):
        sock = self.sock

        while True:
            self.process_queue()
            readable, writable, _ = select.select([sock], [sock], [])
            if readable:
                rsock: socket.socket = readable[0]
                chunk = rsock.recv(8192)
                if len(chunk) == 0:
                    break
                self.process_input(chunk)

            if writable:
                self.sender.send(writable[0])
        sock.close()
        print(f"a conn from {self.addr} is closing....")

    def run(self):
        self.handle_connection()
