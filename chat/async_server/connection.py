from __future__ import annotations
from typing import TYPE_CHECKING
import asyncio, socket, select, ssl
import bcrypt
import message, message_sender

ETX = b'\x03'  # End of Text

class ChatRoom():
    id: str
    manager_queue: asyncio.Queue[message.Message]
    connections: dict[tuple[str, int], Connection]
    hashed_password: bytes

    def __init__(self, id: str):
        self.connections = {}
        self.id = id
        
    async def forward_message(self, message_to_be_forawrded: message.Message):
        src_addr = message_to_be_forawrded.from_addr
        for k in self.connections:
            if k != src_addr:
                print(f"putting message to {self.connections[k]}'s queue")
                await self.connections[k].message_forward_queue.put(message_to_be_forawrded)

    def admit(self, conn: Connection):
        self.connections[conn.addr] = conn
        conn.rooms[self.id] = self

    def set_password(self, password: bytes):
        self.hashed_password = bcrypt.hashpw(password, bcrypt.gensalt())
        
    def check_password(self, password: bytes):
        return bcrypt.checkpw(password, self.hashed_password)
    
    def initiate_secret_exchange(s):
        pass



class Connection:
    addr: tuple[str, int]
    reader: asyncio.StreamReader
    writer: asyncio.StreamWriter

    TLS_secret: bytes

    message_forward_queue: asyncio.Queue[message.Message]
    rooms: dict[str, ChatRoom]
    manager_queue: asyncio.Queue[message.Message]
    sender: message_sender.MessageSender

    current_message_built: message.Message | None
    receive_buffer: bytes

    def __init__(self, addr: tuple[str, int], manager_queue: asyncio.Queue[message.Message], reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        self.reader = reader
        self.writer = writer
        self.addr = addr
        self.manager_queue = manager_queue
        self.message_forward_queue = asyncio.Queue()
        self.rooms = {}
        self.current_message_built = None
        self.receive_buffer = b''
        self.sender = message_sender.MessageSender()
        self.TLS_secret = b''
        

    async def process_message(self):
        await self.manager_queue.put(self.current_message_built)
        self.current_message_built = None

    async def process_input(self, chunk: bytes):
        # takes in an input, cat it to the end of self.receive_buffer
        # if there is a complete message found, move it to current message built, and returns true
        # otherwise, returns false
        self.receive_buffer += chunk
        print(f"Receiving bytes: {chunk} from {self.addr}")

        idx = self.receive_buffer.find(ETX)
        while idx != -1:
            self.current_message_built = message.Message(self.receive_buffer[:idx + 1], self.addr)
            self.receive_buffer = self.receive_buffer[idx + 1:]
            await self.process_message()
            idx = self.receive_buffer.find(ETX)
        # TODO: handle server/ client comm thru encryption and decryption

    async def main(self):
        queue_worker = asyncio.create_task(self.process_queue())
        try:
            while True:
                data = await self.reader.read(1000)
                if data:
                    await self.process_input(data)
                else:
                    break
        except ConnectionError as e:
            print(f"Connection error: {e}")
        finally:
            # TODO: signal manager that this connection is close
            if not queue_worker.done():
                queue_worker.cancel()
            if self.writer and not self.writer.is_closing():
                await self.writer.drain()
                self.writer.close()
                await self.writer.wait_closed()
        
    async def process_queue(self):
        try:
            while True:
                message = await self.message_forward_queue.get()
                print("new message retrived from queue")
                message.forward(self.sender)
                print("awaiting to be sent")
                await self.sender.send(writer=self.writer)
        except asyncio.CancelledError:
            print("queue worker cancelling")
        except Exception as e:
            print("queue worker err'ed", e)
        finally:
            pass
    
