from __future__ import annotations
from typing import TYPE_CHECKING
import socket

if TYPE_CHECKING:
    import message
    import connection

class MessageSender:
    write_buffer: bytes
    rooms: dict[str, connection.ChatRoom]

    def __init__(self):
        self.write_buffer = b''

    def forward_chat(self, m: message.Message04_Chat):
        self.write_buffer += m.to_bytes()
    
    def send(self, wsock: socket):
        """Pre: wsock is writable"""
        if not self.write_buffer: return
        sent = wsock.send(self.write_buffer)
        print(f"sending {self.write_buffer[:sent]}")
        self.write_buffer = self.write_buffer[sent:]
