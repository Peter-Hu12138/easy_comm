from __future__ import annotations
import struct
import tkinter as tk
from tkinter.scrolledtext import ScrolledText
from tkinter import ttk
from Constants import *
import asyncio, ssl
from typing import TYPE_CHECKING

from async_tkinter_loop import async_handler, async_mainloop

if TYPE_CHECKING:
    import top_level


context = ssl.create_default_context()
loop = asyncio.new_event_loop()


class ChatWindow(tk.Frame):
    text_area: ScrolledText
    input_field: tk.Entry
    messages: str
    room_id: int
    is_failed: bool

    def __init__(self, room_id: str, master, UI_manager: top_level.CardApp):
        super().__init__(master=master)  # initialize the window object
        self.room_name = room_id
        self.UI_manager = UI_manager

        self.text_area = ScrolledText(self, wrap=tk.WORD, state=tk.DISABLED)
        self.text_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        self.text_area.config(state=tk.NORMAL)

        self.input_field = tk.Entry(self)
        self.input_field.pack(padx=10, pady=10, fill=tk.X)
        self.input_field.bind("<Return>", self.send_message)

        self.is_failed = False

        self.display_message(
            "Welcome to use EASY COMM, developed by Jingtian Hu at the University of Toronto. For help, enter \"/help\"")

    def service_connection(self, message):
        if message:
            self.display_message(f"Received {message.decode()}")

    def display_message(self, message: str):
        self.text_area.config(state=tk.NORMAL)
        self.text_area.insert(tk.END, message + "\n")
        self.text_area.yview(tk.END)
        self.text_area.config(state=tk.DISABLED)


    def send_message(self, event=None):
        if self.input_field.get():
            if self.input_field.get().startswith("/"):
                cmd(self.input_field.get()[1:], self.key, self, self.display_message)
            else:
                self.display_message("Sent: " + self.input_field.get())
                self.UI_manager.send_message(message_type=6, room_name=self.room_name, msg_content=self.input_field.get())
            self.input_field.delete(0, tk.END)

    def on_closing(self):
        self.manager.close_chat_window(self)

