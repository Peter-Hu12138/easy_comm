from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from . import connection
    from . import message_handler

ETX = b'\x03'  # End of Text, terminates every frame on the wire

# type bytes, see chat/protocol.md
TYPE_JOIN = 0        # room login request: room_name,password
TYPE_CHAT = 6        # normal message: room_name,text
TYPE_CREATE = 7      # room build request: room_name,password
# 1-5 are reserved for the DH/AES key exchange, 8 for room listing


class ProtocolError(Exception):
    pass


class Message:
    """One protocol frame: a type byte followed by the payload, ETX-terminated on the wire."""
    type_byte: int = -1
    content: bytes
    sender: connection.Connection | None

    def __init__(self, content: bytes, sender: connection.Connection | None = None):
        self.content = content
        self.sender = sender

    def __str__(self):
        return f"type: {self.type_byte} content: {self.content!r}"

    def encode(self) -> bytes:
        return bytes([self.type_byte]) + self.content + ETX

    def dispatch(self, handler: message_handler.MessageHandler):
        raise NotImplementedError


class JoinMessage(Message):
    """Type 0 — authenticate into an existing room. Payload: room_name,password"""
    type_byte = TYPE_JOIN
    room_name: str
    password: bytes

    def __init__(self, content: bytes, sender: connection.Connection | None = None):
        super().__init__(content, sender)
        idx = content.find(b',')
        if idx == -1:
            raise ProtocolError("join request must be room_name,password")
        self.room_name = content[:idx].decode("utf-8")
        self.password = content[idx + 1:]

    def dispatch(self, handler: message_handler.MessageHandler):
        handler.handle_join(self)


class CreateMessage(JoinMessage):
    """Type 7 — build a new room. Same payload as a join request."""
    type_byte = TYPE_CREATE

    def dispatch(self, handler: message_handler.MessageHandler):
        handler.handle_create(self)


class ChatMessage(Message):
    """Type 6 — a chat line to relay. Payload: room_name,text"""
    type_byte = TYPE_CHAT
    room_name: str
    text: bytes

    def __init__(self, content: bytes, sender: connection.Connection | None = None):
        super().__init__(content, sender)
        idx = content.find(b',')
        if idx == -1:
            raise ProtocolError("chat message must be room_name,text")
        self.room_name = content[:idx].decode("utf-8")
        self.text = content[idx + 1:]

    def dispatch(self, handler: message_handler.MessageHandler):
        handler.handle_chat(self)


class Response(Message):
    """Server reply to a join/create request, sent back with the request's type byte.
    Payload: ok,room_name or fail,reason"""

    def __init__(self, type_byte: int, content: bytes):
        super().__init__(content)
        self.type_byte = type_byte

    @classmethod
    def ok(cls, request: JoinMessage) -> Response:
        return cls(request.type_byte, b"ok," + request.room_name.encode("utf-8"))

    @classmethod
    def fail(cls, request: JoinMessage, reason: str) -> Response:
        return cls(request.type_byte, b"fail," + reason.encode("utf-8"))
