from __future__ import annotations
from typing import TYPE_CHECKING
import json

if TYPE_CHECKING:
    import top_level
    import message_dispenser


class Message:
    type_byte: int
    content: bytes | None
    from_addr: tuple[str,int]
    to_addr: tuple[str, int] | None
    json_dictionary: dict[str:str]
    
    valid: bool


    def __init__(self, raw_message: bytes=None, dict_message: dict=None):
        if raw_message: # decode
            self.type_byte = raw_message[0]
            self.content = raw_message[1:]
            self.to_addr = None
            self.json_dictionary = json.loads(self.content)
        else: # encode
            self.json_dictionary = dict_message

    def __str__(self):
        return f"type: {self.type_byte} to:{self.to_addr} content:{self.content}"

    def to_bytes(self) -> bytes:
        return int.to_bytes(self.type_byte) + self.content

    async def dispatch(self, handler: message_dispenser.MessageHandler):
        await handler.handle_chat(self)
    
    def output(self) -> str:
        raise NotImplementedError

    def from_string(**kw) -> Message:
        # package a message from dictionary to byte representation of that type
        raise NotImplementedError


    
class ChatMessage(Message):
    pass

class AuthMessage(Message):
    status: str

    def verify():
        raise NotImplementedError

    async def on_valid_request(self, UI_manager: top_level.CardApp):
        raise NotImplementedError
    


class Message03_Chat(ChatMessage):
    from_name: str | None
    room_name: str | None
    content: str | None
    def __init__(self, raw_message: bytes=None, dict_message: dict=None):
        super().__init__(raw_message, dict_message)
        self.from_name = self.json_dictionary["from_name"]
        self.room_name = self.json_dictionary["room_name"]
        self.content = self.json_dictionary["content"]

    async def dispatch(self, handler: message_dispenser.MessageHandler):
        await handler.handle_chat(self)
    
    async def on_valid_request(self, UI_manager: top_level.CardApp):
        UI_manager.update_message(self.room_name, self.content, self.from_name)

    def output(self):
        return int.to_bytes(3) + json.dumps(self.json_dictionary).encode()
    
    def from_string(room_name: str, content: str, from_name: str="Anonymous"):
        return Message03_Chat(None, {"room_name": room_name,
                                     "content": content,
                                     "from_name": from_name})
        


class Message00_CreateChatRoom(AuthMessage):
    status: str | None
    room_name: str | None
    valid: bool

    def __init__(self, raw_message: bytes=None, dict_message: dict=None):
        super().__init__(raw_message, dict_message)
        if raw_message:
            self.status = self.json_dictionary["status"]
        self.room_name = self.json_dictionary["room_name"]

    def verify(self):
        if self.status == "succ":
            return True
        return False
        
    
    async def on_valid_request(self, UI_manager: top_level.CardApp):
        UI_manager.add_room(self.room_name)

    def output(self):
        return int.to_bytes(0) + json.dumps(self.json_dictionary).encode()
    
    def from_string(room_name: str, password: str):
        return Message00_CreateChatRoom(None, {"room_name": room_name,
                                     "password": password})
 

class Message01_JoinChatRoom(AuthMessage):
    room_name: str | None
    password: str| None
    json_dictionary: dict[str:str]

    valid: bool

    def __init__(self, raw_message = None,dict_message: dict=None):
        super().__init__(raw_message, dict_message)
        self.room_name = self.json_dictionary["room_name"]
        if raw_message:
            self.status = self.json_dictionary["status"]


    def verify_room_name(self):
        return True
        
    def verify(self):
        if self.status == "succ":
            return True
        return False
    
    async def on_valid_request(self, UI_manager: top_level.CardApp):
        UI_manager.add_room(self.room_name)
    
    def output(self):
        return int.to_bytes(1) + json.dumps(self.json_dictionary).encode()
    
    def from_string(room_name: str, password: str):
        return Message01_JoinChatRoom(None, {"room_name": room_name,
                                     "password": password})

class Message02_LeaveChatRoom(AuthMessage):
    room_name: str | None
    json_dictionary: dict[str:str]

    valid: bool

    def __init__(self, raw_message = None,dict_message: dict=None):
        super().__init__(raw_message, dict_message)
        self.room_name = self.json_dictionary["room_name"]
        if raw_message:
            self.status = self.json_dictionary["status"]

    def verify_room_name(self):
        return True
        
    def verify(self):
        if self.status == "succ":
            return True
        return False
    
    async def on_valid_request(self, UI_manager: top_level.CardApp):
        UI_manager.delete_room(self.room_name)
    
    def output(self):
        return int.to_bytes(2) + json.dumps(self.json_dictionary).encode()
    
    def from_string(room_name: str):
        return Message02_LeaveChatRoom(None, {"room_name": room_name})
