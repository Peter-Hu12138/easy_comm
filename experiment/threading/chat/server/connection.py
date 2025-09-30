from __future__ import annotations
import threading, socket, select, queue

import bcrypt

ETX = b'\x03'  # End of Text

class Message:
    type_byte: int
    content: bytes | None
    type: str
    from_ct: ConnectionThread
    to: ConnectionThread

    room_name: str | None
    room_password: str | None

    def __init__(self, raw_message: bytes, from_ct: ConnectionThread, to_ct: ConnectionThread | None = None):
        self.type_byte = raw_message[0]
        self.from_ct = from_ct
        self.content = raw_message[1:]
        self.to = to_ct
        self.room_name = None
        self.room_password = None

    def __str__(self):
        return f"type: {self.type_byte} to:{self.to.addr} content:{self.content}"

    def to_bytes(self) -> bytes:
        return int.to_bytes(self.type_byte) + self.content
        
    def parse_room_name(self) -> bool:
        # pasrs room name and returns true iff parsed successfully
        idx = self.content.find(b',')
        if idx == -1:
            # invalid request
            return False
        self.room_name = (self.content[:idx]).decode("utf-8")
        self.room_password = self.content[idx+1:]

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
                print(f"processing message {self.content}")
                self.parse_room_name()
                room = self.from_ct.rooms[self.room_name]
                room.forward_message(self.from_ct, self)

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


class ChatRoom():
    id: str
    manager_queue: queue.Queue[Message]
    connections: dict[tuple[str, int], ConnectionThread]
    hashed_password: bytes

    def __init__(self, id: str):
        self.connections = {}
        self.id = id
        
    def forward_message(self, from_ct: ConnectionThread, message: Message):
        src_addr = from_ct.addr
        for k in self.connections:
            if k != src_addr:
                new_message = Message(message.to_bytes(), 
                                  from_ct=message.from_ct, 
                                  to_ct=self.connections[k])
                print(f"putting message to {self.connections[k]}'s queue")
                self.connections[k].message_forward_queue.put(new_message)

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

    message_forward_queue: queue.Queue[Message]
    rooms: dict[str, ChatRoom]
    manager_queue: queue.Queue[Message]

    current_message_built: Message | None
    receive_buffer: bytes
    write_buffer: bytes

    def __init__(self, sock: socket.socket, addr: tuple[str, int], group = None, target = None, name = None, args = ..., kwargs = None, *, daemon = None):
        super().__init__(group, target, name, args, kwargs, daemon=daemon)
        self.sock = sock
        self.addr = addr
        self.message_forward_queue = queue.Queue()
        self.rooms = {}
        self.current_message_built = None
        self.receive_buffer = b''
        self.write_buffer = b''

    def process_queue(self):
        if not self.message_forward_queue.empty() and self.write_buffer == b'':
            message = self.message_forward_queue.get()
            message.process_incoming_from_queue()
            

    def process_message(self):
        self.current_message_built.process_incoming_from_socket()
        self.current_message_built = None

    def process_input(self, chunk: bytes) -> bool:
        # takes in an input, cat it to the end of self.receive_buffer
        # if there is a complete message found, move it to current message built, and returns true
        # otherwise, returns false
        self.receive_buffer += chunk
        idx = self.receive_buffer.find(ETX)
        print(f"Receiving bytes: {chunk} from {self.addr}")

        if idx != -1 and self.current_message_built is None:
            self.current_message_built = Message(self.receive_buffer[:idx + 1], self)
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
                if not self.write_buffer: continue
                wsock: socket.socket = writable[0]
                sent = wsock.send(self.write_buffer)
                print(f"sending {self.write_buffer[:sent]}")
                self.write_buffer = self.write_buffer[sent:]
        sock.close()
        print(f"a conn from {self.addr} is closing....")

    def run(self):
        self.handle_connection()
