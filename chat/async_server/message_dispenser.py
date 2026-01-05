from __future__ import annotations
from typing import TYPE_CHECKING
import threading
import message

if TYPE_CHECKING:
    import connection


class MessageHandler:
    connections: dict[tuple[str, int], connection.ConnectionThread]
    rooms: dict[str, connection.ChatRoom]

    def __init__(self, connections: dict[tuple[str, int], connection.Connection], rooms: dict[str, connection.ChatRoom]):
        self.connections = connections
        self.rooms = rooms
        

    async def handle_chat(self, m: message.Message):
        ChatMessage = message.ChatMessage
        AuthMessage = message.AuthMessage
        if isinstance(m, ChatMessage):
            print(f"processing message {m.content}")
            if m.verify(self.rooms):
                # verify a conn is in a room
                await m.room.forward_message(m)
            else:
                print("ignoring a message due to failing to verify a conn in the message's designated room")
        elif isinstance(m, AuthMessage):
            print(f"processing auth message")
            m: message.AuthMessage
            if m.verify(self.rooms):
                m.on_valid_request(self.rooms, self.connections)
            await self.connections[m.from_addr].message_forward_queue.put(m)
    
    def handle_leave_room():
        pass

    def handle_key_exchange():
        pass
