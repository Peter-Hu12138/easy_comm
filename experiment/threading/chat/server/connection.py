from __future__ import annotations
import threading, socket, select, queue
import bcrypt

ETX = b'\x03'  # End of Text

class ChatRoom():
    connections: list[ConnectionThread]
    hashed_password: bytes

    def __init__(self):
        self.connections = []
        
    def admit(self, ct: ConnectionThread):
        self.connections.append(ct)
        ct.rooms.append(self)

    def set_password(self, password: bytes):
        self.hashed_password = bcrypt.hashpw(password, bcrypt.gensalt())
        
    def check_password(self, password: bytes):
        return bcrypt.checkpw(password, self.hashed_password)
    
    def initiate_secret_exchange(s):
        pass

class ConnectionThread(threading.Thread):
    addr: tuple[str, int]
    sock: socket.socket

    message_forward_queue: queue.Queue[bytes]
    rooms: list[ChatRoom]
    
    manager_queue: queue.Queue[bytes]

    current_message_built: bytes
    receive_buffer: bytes
    write_buffer: bytes

    def __init__(self, sock: socket.socket, addr: tuple[str, int], group = None, target = None, name = None, args = ..., kwargs = None, *, daemon = None):
        super().__init__(group, target, name, args, kwargs, daemon=daemon)
        self.sock = sock
        self.addr = addr
        self.message_forward_queue = queue.Queue()
        self.rooms = []
        self.current_message_built = b''
        self.receive_buffer = b''
        self.write_buffer = b''

    def process_queue(self):
        if not self.message_forward_queue.empty() and self.write_buffer == b'':
            message = self.message_forward_queue.get()
            print(f"relaying message {message} to {self.addr}")

            type_byte = message[0]
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
                    self.write_buffer = message


    def process_message(self):
        type_byte = self.current_message_built[0]
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
                room = self.rooms[0]
                for conn in room.connections:
                    if conn is not self:
                        print(f"putting message tp {conn.addr}'s queue")
                        conn.message_forward_queue.put(self.current_message_built)
        self.current_message_built = b''

    def process_input(self, chunk: bytes) -> bool:
        # takes in an input, cat it to the end of self.receive_buffer
        # if there is a complete message found, move it to current message built, and returns true
        # otherwise, returns false
        self.receive_buffer += chunk
        idx = self.receive_buffer.find(ETX)
        print(f"Receiving bytes: {chunk} from {self.addr}")

        if idx != -1 and self.current_message_built == b'':
            self.current_message_built = self.receive_buffer[:idx + 1]
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
