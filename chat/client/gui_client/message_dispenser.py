from __future__ import annotations
from typing import TYPE_CHECKING
import threading
import message


if TYPE_CHECKING:
    import top_level

class MessageHandler:
    UI_manager: top_level.CardApp

    def __init__(self, UI_manager):
        self.UI_manager = UI_manager
        

    async def handle_chat(self, m: message.Message):
        if isinstance(m, message.ChatMessage):
            print(f"processing message {m.content}")
            await m.on_valid_request(self.UI_manager)
        elif isinstance(m, message.AuthMessage):
            print(f"processing auth message")
            m: message.AuthMessage
            if m.verify():
                m.on_valid_request(self.UI_manager)
            else:
                # TODO: inform user with a pop up
                pass
