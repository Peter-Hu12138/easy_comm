from __future__ import annotations
import asyncio
import traceback

from . import connection
from . import message
from . import message_dispatcher
from . import message_handler


class Manager:
    rooms: dict[str, connection.ChatRoom]
    connections: dict[tuple[str, int], connection.Connection]
    inbox: asyncio.Queue[tuple[bytes, connection.Connection]]

    def __init__(self):
        self.rooms = {}
        self.connections = {}
        self.inbox = asyncio.Queue()
        self.dispatcher = message_dispatcher.MessageDispatcher(
            message_handler.MessageHandler(self.rooms))

    async def _handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        conn = connection.Connection(reader, writer, self.inbox)
        self.connections[conn.addr] = conn
        print(f"accepted connection from {conn.addr}")
        try:
            await conn.run()
        finally:
            self.connections.pop(conn.addr, None)
            for room in list(conn.rooms.values()):
                room.evict(conn)

    async def _dispatch_loop(self):
        while True:
            raw, sender = await self.inbox.get()
            try:
                self.dispatcher.dispatch(raw, sender)
            except message.ProtocolError as e:
                print(f"bad frame from {sender.addr}: {e}")
            except Exception:
                traceback.print_exc()
                print("error, continuing")

    async def serve(self, host: str, port: int):
        server = await asyncio.start_server(self._handle_client, host, port)
        dispatch_task = asyncio.create_task(self._dispatch_loop())
        print(f"listening on {(host, port)}")
        try:
            async with server:
                await server.serve_forever()
        finally:
            dispatch_task.cancel()


def main(host: str, port: int):
    try:
        asyncio.run(Manager().serve(host, port))
    except KeyboardInterrupt:
        print("ctrl-c detected, exiting...")
