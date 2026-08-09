from __future__ import annotations
from typing import TYPE_CHECKING

from . import message
from . import message_handler

if TYPE_CHECKING:
    from . import connection

MESSAGE_TYPES: dict[int, type[message.Message]] = {
    message.TYPE_JOIN: message.JoinMessage,
    message.TYPE_CHAT: message.ChatMessage,
    message.TYPE_CREATE: message.CreateMessage,
}


class MessageDispatcher:
    """Decodes a raw frame into a typed Message and double-dispatches it to the handler."""

    def __init__(self, handler: message_handler.MessageHandler):
        self.handler = handler

    def dispatch(self, raw: bytes, sender: connection.Connection):
        if not raw:
            raise message.ProtocolError("empty frame")
        message_class = MESSAGE_TYPES.get(raw[0])
        if message_class is None:
            raise message.ProtocolError(f"unknown or unsupported type byte {raw[0]}")
        message_class(raw[1:], sender).dispatch(self.handler)
