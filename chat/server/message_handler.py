from __future__ import annotations

from . import message
from . import connection


class MessageHandler:
    """Business logic for each message type. Single-threaded under asyncio, so the
    old conn_threads locks are gone."""

    def __init__(self, rooms: dict[str, connection.ChatRoom]):
        self.rooms = rooms

    def handle_create(self, m: message.CreateMessage):
        if m.room_name in self.rooms:
            m.sender.send(message.Response.fail(m, f"room {m.room_name} already exists"))
            return
        room = connection.ChatRoom(m.room_name, m.password)
        self.rooms[m.room_name] = room
        room.admit(m.sender)
        m.sender.send(message.Response.ok(m))
        print(f"{m.sender.addr} created room {m.room_name}")

    def handle_join(self, m: message.JoinMessage):
        room = self.rooms.get(m.room_name)
        if room is None:
            m.sender.send(message.Response.fail(m, "no such room, create it first"))
        elif not room.check_password(m.password):
            m.sender.send(message.Response.fail(m, "wrong password"))
        else:
            room.admit(m.sender)
            m.sender.send(message.Response.ok(m))
            print(f"{m.sender.addr} joined room {m.room_name}")

    def handle_chat(self, m: message.ChatMessage):
        room = m.sender.rooms.get(m.room_name)
        if room is None:
            # unauthenticated chat messages are ignored, per protocol.md
            print(f"dropping chat from {m.sender.addr} for room {m.room_name}: not a member")
            return
        room.broadcast(m, exclude=m.sender)

    def handle_key_exchange(self):
        # type bytes 1-5, not implemented yet
        pass
