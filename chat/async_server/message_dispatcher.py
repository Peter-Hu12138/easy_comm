from __future__ import annotations
from typing import TYPE_CHECKING
import threading
import message
import message_dispenser


if TYPE_CHECKING:
    import connection

class MessageDispatcher:
    handler: message_dispenser.MessageHandler

    def __init__(self, handler: message_dispenser.MessageHandler):
        self.handler = handler
        

    async def dispatch(self, m: message.Message, ) -> message.Message:
        """Decode the raw message and dispatch to it to the right place. """
        match m.type_byte:
            case 0:
                m = message.Message00_CreateChatRoom(m.to_bytes(), m.from_addr)
            case 1:
                m = message.Message01_JoinChatRoom(m.to_bytes(), m.from_addr, )
            case 2:
                m = message.Message02_LeaveChatRoom(m.to_bytes(), m.from_addr, )
            case 3:
                m = message.Message03_Chat(m.to_bytes(), m.from_addr, )
            case _:
                print(f"unexpected manager request {m}")

        await m.dispatch(self.handler)