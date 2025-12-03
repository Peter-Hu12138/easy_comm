from __future__ import annotations
from typing import TYPE_CHECKING
import threading

if TYPE_CHECKING:
    import message
    import connection


class MessageHandler:
    connections: dict[tuple[str, int], connection.ConnectionThread]

    def __init__(self, connections: dict[tuple[str, int], connection.ConnectionThread]):
        self.connections = connections
        

    async def handle_chat(self, m: message.Message04_Chat):
        print(f"processing message {m.content}")
        m.parse_room(self.connections[m.from_addr].rooms)
        await m.room.forward_message(m)
    
    def handle_auth():
        pass

    def handle_key_exchange():
        pass
