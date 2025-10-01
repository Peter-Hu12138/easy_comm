from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import connection
    import message_sender
    import message_dispenser


class Message:
    type_byte: int
    content: bytes | None
    from_addr: tuple[str,int]
    to_addr: tuple[str, int] | None


    def __init__(self, raw_message: bytes, from_addr: tuple[str,int]):
        self.type_byte = raw_message[0]
        self.from_addr = from_addr
        self.content = raw_message[1:]
        self.to_addr = None

    def __str__(self):
        return f"type: {self.type_byte} to:{self.to.addr} content:{self.content}"

    def to_bytes(self) -> bytes:
        return int.to_bytes(self.type_byte) + self.content

    def dispatch(self, handler: message_dispenser.MessageHandler):
        raise NotImplementedError
    
    def forward(self, handler: message_sender.MessageSender):
        raise NotImplementedError


class Message04_Chat(Message):
    room_name: str | None
    room: connection.ChatRoom
    def __init__(self, raw_message: bytes, from_addr: str):
        super().__init__(raw_message, from_addr)
        if not self.parse_room_name():
            raise RuntimeError("Not a valid chat request")

    def dispatch(self, handler: message_dispenser.MessageHandler):
        handler.handle_chat(self)

    def parse_room_name(self) -> bool:
        # pasrs room name and returns true iff parsed successfully
        idx = self.content.find(b',')
        if idx == -1:
            # invalid request
            return False
        self.room_name = (self.content[:idx]).decode("utf-8")
        return True
    
    def parse_room(self, connection_rooms: dict[str, connection.ChatRoom]) -> bool:
        self.room = connection_rooms[self.room_name]
        return True
    
    def forward(self, handler: message_sender.MessageSender):
        handler.forward_chat(self)