from __future__ import annotations
import socket
import sys
import struct
from Constants import *
import tkinter as tk
from tkinter.scrolledtext import ScrolledText
from tkinter import ttk
import asyncio, ssl
from async_tkinter_loop import async_handler, async_mainloop



class Manager(ttk.Frame):
    root: tk.Tk
    name: str
    server_addr: tuple[str, int]

    def __init__(self, master, send: callable):
        super().__init__(master)
        # self.server_addr = (host, int(port))
        self.chat_windows = {}

        # Create input fields
        self.room_label = ttk.Label(self, text="Room ID:")
        self.room_label.pack()
        self.room_entry = ttk.Entry(self)
        self.room_entry.pack()

        self.pass_label = ttk.Label(self, text="Password:")
        self.pass_label.pack()
        self.pass_entry = ttk.Entry(self)
        self.pass_entry.pack()

        # Create buttons
        self.join_button = ttk.Button(self, text="join", command=lambda: send(message_type=1, room_name=self.room_entry.get(), password=self.pass_entry.get()))
        self.join_button.pack(pady=5)

        self.create_button = ttk.Button(self, text="create", command=lambda: send(message_type=0, room_name=self.room_entry.get(), password=self.pass_entry.get()))
        self.create_button.pack(pady=5)
        # self.room_entry.insert(0, "1")
        # self.add_new_conn("join")



if __name__ == "__main__":
    host, port, name = "localhost", 8000, "peter"
    print(host, port, name)

    server_addr = (host, int(port))

    manager = Manager(host=host, port=port, name=name)

    try:
        manager.start()
    except KeyboardInterrupt:
        print("ctrl+c detected exiting")
    finally:
        manager.quit()
