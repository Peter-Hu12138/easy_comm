import tkinter as tk
from tkinter import ttk
from tkinter.constants import *

from chat_display import ClickableInfoFrame
from scroll_frame import ScrollFrame
from chat_room_content import ChatWindow
from managemant import Manager
from Constants import *

import asyncio, ssl, struct, json
from async_tkinter_loop import async_handler, async_mainloop
import message
import message_dispatcher, message_dispenser

context = ssl.create_default_context()
loop = asyncio.new_event_loop()

class CardApp(tk.Tk):
    frames: dict[str: None | int | str:ttk.Frame]
    room_infos: dict[str: ClickableInfoFrame]

    conn_manager: object
    dispatcher: message_dispatcher.MessageDispatcher
    handler: message_dispenser.MessageHandler

    def __init__(self):
        super().__init__()

        self.conn_manager = ConnectionManager(loop, self)
        
        self.title("Easy Communication Everywhere")
        self.geometry("1200x1000")

        self.navbar = tk.Frame(self)
        self.navbar.pack(side = 'left',fill='y')

        self.admin_button = ttk.Button(self.navbar, text="Join / Create a Room", command=lambda:self.show_frame(None))
        self.admin_button.pack(side= 'bottom', fill='x')

        self.container = tk.Frame(self)
        self.container.pack(fill="both", expand=True)

        # Configure grid to allow the container to expand
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        # Dictionary to keep track of frames (like giving strings to CardLayout)
        self.frames = {}
        self.room_infos = {}
        self.frames[None] = Manager(self.container, self.send_message)
        self.frames[None].grid(row=0, column=0, sticky="nsew")
        
        self.scrollFrame = ScrollFrame(self.navbar) # add a new scrollable frame.

        # when packing the scrollframe, we pack scrollFrame itself (NOT the viewPort)
        self.scrollFrame.pack(side="top", fill="both", expand=True)

        self.handler = message_dispenser.MessageHandler(self)
        self.dispatcher = message_dispatcher.MessageDispatcher(self.handler)
    
    def printMsg(self, msg):
        print(msg)

    def show_frame(self, page_name):
        '''Equivalent to cardLayout.show(parent, "name")'''
        frame = self.frames[page_name]
        print(f"showing page number {page_name}")
        frame.tkraise() # Brings this frame to the top of the stack

    def process_incoming_message(self, msg: bytes):
        print(f"cardapp receiving {msg}")
        m = message.Message(msg)
        loop.create_task(self.dispatcher.dispatch(m))

    def update_message(self, chat_room_name: str, message:str, from_name: str):
        self.frames[chat_room_name].display_message(message, from_name)
    
    def send_message(self, message_type: int, room_name: str=None, msg_content: str=None, password: str= None, from_name: str = None):
        match message_type:
            case 0:
                msg = message.Message00_CreateChatRoom.from_string(room_name, password)
            case 1:
                msg = message.Message01_JoinChatRoom.from_string(room_name, password)
            case 2:
                msg = message.Message02_LeaveChatRoom.from_string(room_name)
            case 3:
                msg = message.Message03_Chat.from_string(room_name, msg_content)

        loop.create_task(self.conn_manager.tcp_send(msg.output()))

    def add_room(self, room_name):
        self.frames[room_name] = ChatWindow(room_name, self.container, self)
        self.frames[room_name].grid(row=0, column=0, sticky="nsew")
        
        # Now add some controls to the scrollframe. 
        # NOTE: the child controls are added to the view port (scrollFrame.viewPort, NOT scrollframe itself)
        self.room_infos[room_name] = ClickableInfoFrame(self.scrollFrame.viewPort, room_name, "sd: hi", 20, command=lambda name=room_name: self.show_frame(name))
        self.room_infos[room_name].pack(fill='x')

    def delete_room(self, room_name):
        self.frames[room_name].destroy()
        del self.frames[room_name]

        self.room_infos[room_name].destroy()
        del self.room_infos[room_name]






class ConnectionManager:
    writer: asyncio.StreamWriter
    top_level: CardApp

    def __init__(self, loop, top_level):
        self.loop = loop
        self.top_level = top_level

        loop.create_task(self.tcp_client())

    def start(self):
        self.loop.create_task(self.tcp_client())

    def send(self, msg: bytes, chat_room_name: str):
        self.loop.create_task(self.tcp_send(msg, chat_room_name))

    async def tcp_send(self, msg: bytes):
        print(f"sending {msg.decode()} to {self.writer.get_extra_info('socket', default=None)}")
        self.writer.write(struct.pack("i", len(msg)) + msg) # Send prefix + msg
        await self.writer.drain()  # Ensure data is sent

    async def tcp_rec(self, reader: asyncio.StreamReader):
        state = "idle"
        yet_reading_size = 4
        receive_buffer = b''
        while True:
            data = await reader.read(yet_reading_size - len(receive_buffer))
            if not data:
                break
            print(f"tcp receiving {data}")
            receive_buffer += data
            if len(receive_buffer) == yet_reading_size:
                if state == "idle":
                    state = "reading_body"
                    yet_reading_size = struct.unpack("i", receive_buffer)[0]
                    receive_buffer = b''
                elif state == "reading_body":
                    self.top_level.process_incoming_message(data)
                    state = "idle"
                    yet_reading_size = 4
                    receive_buffer = b''


    async def tcp_client(self):
        tasks = set()
        reader, writer = await asyncio.open_connection('127.0.0.1', 8000, ssl=context)
        self.writer = writer
        tasks.add(asyncio.create_task(self.tcp_rec(reader)))
        # while len(tasks) > 0:
        #     await asyncio.wait(tasks)

if __name__ == "__main__":
    app = CardApp()
    async_mainloop(app, loop)