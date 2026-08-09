from __future__ import annotations
import asyncio
from typing import Callable

from ..server import message


class RoomConnection:
    """The asyncio side of one chat window: a socket authenticated into one room.

    GUI-agnostic on purpose — the owner passes plain callbacks (called from the
    event loop thread) so this can also be driven headless for testing.
    """

    def __init__(self, host: str, port: int, room_name: str,
                 on_response: Callable[[bool, str], None],
                 on_chat: Callable[[str], None],
                 on_disconnect: Callable[[], None]):
        self.host = host
        self.port = port
        self.room_name = room_name
        self.on_response = on_response
        self.on_chat = on_chat
        self.on_disconnect = on_disconnect
        self.writer: asyncio.StreamWriter | None = None
        self.joined = False

    async def run(self, operation: str, password: str):
        """Connect, send the join/create request, then relay incoming frames to
        the callbacks until the server hangs up or close() is called."""
        try:
            reader, self.writer = await asyncio.open_connection(self.host, self.port)
        except OSError as e:
            self.on_response(False, f"could not connect: {e}")
            self.on_disconnect()
            return

        type_byte = message.TYPE_CREATE if operation == "create" else message.TYPE_JOIN
        self._send_frame(type_byte, f"{self.room_name},{password}".encode("utf-8"))

        try:
            while True:
                try:
                    frame = await reader.readuntil(message.ETX)
                except (asyncio.IncompleteReadError, ConnectionResetError):
                    break
                self._handle_frame(frame[:-1])
        except asyncio.CancelledError:
            pass
        finally:
            self.writer.close()
            self.on_disconnect()

    def _handle_frame(self, raw: bytes):
        if not raw:
            return
        type_byte, content = raw[0], raw[1:]
        if type_byte in (message.TYPE_JOIN, message.TYPE_CREATE):
            status, _, detail = content.partition(b',')
            self.joined = status == b"ok"
            self.on_response(self.joined, detail.decode("utf-8", "replace"))
        elif type_byte == message.TYPE_CHAT:
            _, _, text = content.partition(b',')
            self.on_chat(text.decode("utf-8", "replace"))
        else:
            print(f"ignoring frame with unsupported type byte {type_byte}")

    def _send_frame(self, type_byte: int, content: bytes):
        self.writer.write(bytes([type_byte]) + content + message.ETX)

    def send_chat(self, text: str):
        if self.writer is not None and not self.writer.is_closing():
            self._send_frame(message.TYPE_CHAT, f"{self.room_name},{text}".encode("utf-8"))

    def close(self):
        if self.writer is not None:
            self.writer.close()
