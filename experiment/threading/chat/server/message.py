from __future__ import annotations

class Message:
    type_byte: bytes
    content: bytes | None
    type: str

    def from_bytes(raw_message: bytes) -> Message:
        message = Message()
        message.type_byte = raw_message[0]
        message.content = raw_message[1:]
        return message