from __future__ import annotations
from typing import TYPE_CHECKING
import json

if TYPE_CHECKING:
    import connection
    import message_sender
    import message_dispenser


class Message:
    type_byte: int
    content: bytes | None
    from_addr: tuple[str,int]
    to_addr: tuple[str, int] | None
    valid: bool


    def __init__(self, raw_message: bytes, from_addr: tuple[str,int]):
        self.type_byte = raw_message[0]
        self.from_addr = from_addr
        self.content = raw_message[1:]
        self.to_addr = None

    def __str__(self):
        return f"type: {self.type_byte} to:{self.to.addr} content:{self.content}"

    def to_bytes(self) -> bytes:
        return int.to_bytes(self.type_byte) + self.content

    async def dispatch(self, handler: message_dispenser.MessageHandler):
        await handler.handle_chat(self)
    
    def forward(self, handler: message_sender.MessageSender):
        handler.forward_chat(self)
    
    def verify(self, connection_rooms: dict[str, connection.ChatRoom]):
        raise NotImplementedError
    
    def output(self) -> str:
        pass

    
class ChatMessage(Message):
    pass

class AuthMessage(Message):
    status: str
    def on_valid_request(self, connection_rooms: dict[str, connection.ChatRoom], connections: dict[tuple[str, int], connection.ConnectionThread]):
        raise NotImplementedError
    


class Message04_Chat(ChatMessage):
    room_name: str | None
    message_content: str | None
    from_name: str | None
    room: connection.ChatRoom
    def __init__(self, raw_message: bytes, from_addr: str):
        super().__init__(raw_message, from_addr)
        self.json_dictionary = json.loads(self.content.decode())
        self.room_name = self.json_dictionary["room_name"]
        self.message_content = self.json_dictionary["content"]
        self.from_name = self.json_dictionary["from_name"]
        self.valid = self.parse_room_name()

    async def dispatch(self, handler: message_dispenser.MessageHandler):
        await handler.handle_chat(self)

    def parse_room_name(self) -> bool:
        # pasrs room name and returns true iff parsed successfully
        idx = self.room_name.find(',')
        if idx == -1:
            # invalid request
            return True
        self.room_name = (self.content[:idx]).decode("utf-8")
        return False
    
    def parse_room(self, connection_rooms: dict[str, connection.ChatRoom]) -> bool:
        if self.room_name not in connection_rooms:
            return False
        self.room = connection_rooms[self.room_name]
        return True
    
    def verify(self, connection_rooms):
        if not self.valid:
            return False

        if self.parse_room(connection_rooms):
            if self.from_addr in connection_rooms[self.room_name].connections:
                return True
        return False
    
    def forward(self, handler: message_sender.MessageSender):
        handler.forward_chat(self)

    def output(self):
        result = {"from_name": self.from_addr, "content": self.message_content, "room_name": self.room_name}
        return int.to_bytes(3) + json.dumps(result).encode()
        


class Message00_CreateChatRoom(AuthMessage):
    room_name: str | None
    password: str| None
    json_dictionary: dict[str:str]

    valid: bool

    def __init__(self, raw_message, from_addr):
        super().__init__(raw_message, from_addr)
        self.json_dictionary = json.loads(self.content.decode())
        self.room_name = self.json_dictionary["room_name"]
        self.password = self.json_dictionary["password"]
        self.valid = self.verify_room_name()
            
    def verify_room_name(self):
        if ',' in self.room_name:
            return False
        else:
            return True
        
    def verify(self, connection_rooms):
        if not self.verify_room_name():
            self.status = "incorret_room_name"
            return False

        if self.room_name in connection_rooms:
            self.status = "room_taken"
            return False
        
        self.status = "succ"
        return True
    
    def on_valid_request(self, connection_rooms: dict[str, connection.ChatRoom], connections: dict[tuple[str, int], connection.ConnectionThread]):
        import connection
        connection_rooms[self.room_name] = connection.ChatRoom(self.room_name, self.password)
        connection_rooms[self.room_name].admit(connections[self.from_addr])

    def output(self):
        result = {"status": self.status, "room_name": self.room_name}
        return int.to_bytes(0) + json.dumps(result).encode()

class Message01_JoinChatRoom(AuthMessage):
    room_name: str | None
    password: str| None
    json_dictionary: dict[str:str]

    valid: bool

    def __init__(self, raw_message, from_addr):
        super().__init__(raw_message, from_addr)
        self.json_dictionary = json.loads(self.content.decode())
        self.room_name = self.json_dictionary["room_name"]
        self.password = self.json_dictionary["password"]
        self.valid = self.verify_room_name()

    def verify_room_name(self):
        if ',' in self.room_name:
            return False
        else:
            return True
        
    def verify(self, connection_rooms):
        if not self.verify_room_name():
            self.status = "incorret_room_name"
            return False

        if self.room_name not in connection_rooms:
            self.status = "room_DNE"
            return False
        
        if not connection_rooms[self.room_name].verify_password(self.password):
            self.status = "incorrect_password"
            return False
        
        self.status = "succ"
        return True
    
    def output(self):
        result = {"status": self.status, "room_name": self.room_name}
        return int.to_bytes(1) + json.dumps(result).encode()
    
    def on_valid_request(self, connection_rooms: dict[str, connection.ChatRoom], connections: dict[tuple[str, int], connection.ConnectionThread]):
        connection_rooms[self.room_name].admit(connections[self.from_addr])
