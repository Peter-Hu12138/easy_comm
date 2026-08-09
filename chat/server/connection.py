from __future__ import annotations
import asyncio
import bcrypt

from . import message


class ChatRoom:
    name: str
    hashed_password: bytes
    members: dict[tuple[str, int], Connection]

    def __init__(self, name: str, password: bytes):
        self.name = name
        self.hashed_password = bcrypt.hashpw(password, bcrypt.gensalt())
        self.members = {}

    def check_password(self, password: bytes) -> bool:
        return bcrypt.checkpw(password, self.hashed_password)

    def admit(self, conn: Connection):
        self.members[conn.addr] = conn
        conn.rooms[self.name] = self

    def evict(self, conn: Connection):
        self.members.pop(conn.addr, None)
        conn.rooms.pop(self.name, None)

    def broadcast(self, m: message.Message, exclude: Connection | None = None):
        for member in self.members.values():
            if member is not exclude:
                member.send(m)


class Connection:
    """One client socket. Replaces the old ConnectionThread: the read loop is a
    coroutine, and outgoing messages go through a queue drained by a writer task
    so any part of the server can send() without awaiting."""
    addr: tuple[str, int]
    rooms: dict[str, ChatRoom]

    def __init__(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter,
                 inbox: asyncio.Queue[tuple[bytes, Connection]]):
        self.reader = reader
        self.writer = writer
        self.addr = writer.get_extra_info("peername")
        self.inbox = inbox
        self.rooms = {}
        self.outgoing: asyncio.Queue[message.Message] = asyncio.Queue()

    def send(self, m: message.Message):
        self.outgoing.put_nowait(m)

    async def _write_loop(self):
        while True:
            m = await self.outgoing.get()
            self.writer.write(m.encode())
            await self.writer.drain()

    async def run(self):
        writer_task = asyncio.create_task(self._write_loop())
        try:
            while True:
                try:
                    frame = await self.reader.readuntil(message.ETX)
                except (asyncio.IncompleteReadError, ConnectionResetError):
                    break
                except asyncio.LimitOverrunError:
                    print(f"frame from {self.addr} exceeds size limit, disconnecting")
                    break
                await self.inbox.put((frame[:-1], self))
        finally:
            writer_task.cancel()
            self.writer.close()
        print(f"connection from {self.addr} closed")
