from __future__ import annotations
from typing import TYPE_CHECKING
import threading
import message
import message_dispenser


if TYPE_CHECKING:
    import connection

class MessageDispatcher:
    connections: dict[tuple[str, int], connection.Connection]
    handler: message_dispenser.MessageHandler

    def __init__(self,
                 connections: dict[tuple[str, int], connection.ConnectionThread]):
        self.connections = connections
        self.handler = message_dispenser.MessageHandler(connections)
        

    async def dispatch(self, m: message.Message) -> message.Message:
        """Decode the raw message and dispatch to it to the right place. """
        match m.type_byte:
            case 0:
                m = message.Message00_Login(m.to_bytes(), m.from_addr)
            case 6:
                m = message.Message04_Chat(m.to_bytes(), m.from_addr, )
            case _:
                print(f"unexpected manager request {m}")

        await m.dispatch(self.handler)