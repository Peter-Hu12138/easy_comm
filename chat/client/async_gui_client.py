from __future__ import annotations
import socket
import sys
import struct
import tkinter as tk
from tkinter.scrolledtext import ScrolledText
from help_manual import cmd
from tkinter import ttk
import asyncio, ssl
from async_tkinter_loop import async_handler, async_mainloop

context = ssl.create_default_context()
loop = asyncio.new_event_loop()


class ChatWindow(tk.Toplevel):
    manager: Manager
    text_area: ScrolledText
    input_field: tk.Entry
    messages: str
    room_id: int
    is_failed: bool

    def __init__(self, manager: Manager, room_id: str, master=None):
        super().__init__(master=master)  # initialize the window object
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.manager = manager

        self.title(f"Chat Client -- welcome for using -- room id: {room_id}")
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
            # recv_data: bytes = sock.recv(1024)  # Should be ready to read
            # if recv_data:
            #     if recv_data.startswith(STX):
            #         self.display_message(f"Received from server: {recv_data.decode()}")
            #         if b"fail" in recv_data:
            #             self.input_field.config(state=tk.DISABLED)
            #     else:
            #         self.display_message(f"Received {recv_data.decode()}")
            #         data.recv_total += len(recv_data)
            # else:
            #     if not self.is_failed:
            #         self.display_message(f"Server closed the connection, please close this window and try again")
            #         self.is_failed = True

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
                # self.messages = f"{self.key.data.name} said: {self.input_field.get()}"
                # self.key.data.outb += self.messages.encode()
                # self.messages = ""
                loop.create_task(self.manager.tcp_send(self.input_field.get().encode()))

            self.input_field.delete(0, tk.END)

    def on_closing(self):
        self.manager.close_chat_window(self)



class Manager():
    chat_windows: dict[str, ChatWindow]
    root: tk.Tk
    name: str
    server_addr: tuple[str, int]

    def __init__(self, host, port, name):
        self.server_addr = (host, int(port))
        self.name = name
        self.chat_windows = {}
        self.root = tk.Tk()

        self.root.title(f"Easy_comm - Welcome back, {name}!")
        self.root.geometry("400x300")  # width x height

        # Create input fields
        self.room_label = ttk.Label(self.root, text="Room ID:")
        self.room_label.pack()
        self.room_entry = ttk.Entry(self.root)
        self.room_entry.pack()

        self.pass_label = ttk.Label(self.root, text="Password:")
        self.pass_label.pack()
        self.pass_entry = ttk.Entry(self.root)
        self.pass_entry.pack()

        # Create buttons
        self.join_button = ttk.Button(self.root, text="join", command=lambda: self.add_new_conn("join"))
        self.join_button.pack(pady=5)

        self.create_button = ttk.Button(self.root, text="create", command=lambda: self.add_new_conn("create"))
        self.create_button.pack(pady=5)
        # self.room_entry.insert(0, "1")
        # self.add_new_conn("join")

    def start(self):
        loop.create_task(self.tcp_client())
        async_mainloop(self.root, loop)

    def add_new_conn(self, operation: str):
        """
        creates a chatwindow with a newly created socket, then try to validate with the server with a formatted message.
        """
        chat_window = ChatWindow(manager=self, room_id="hi")

        # if operation == "join":
        #     key.data.outb += f"join,{room_id},{password},".encode() + ETX
        # if operation == "create":
        #     key.data.outb += f"create,{room_id},{password},".encode() + ETX

        self.chat_windows["hi"] = chat_window


    def close_chat_window(self, chat_window: ChatWindow):
        print("before closing:")
        print(self.chat_windows)
        self.chat_windows.remove(chat_window)
        chat_window.key.fileobj.close()
        chat_window.destroy()
        print("after closing:")
        print(self.chat_windows)

    def quit(self):
        self.root.quit()
        # for fd in curr_conns:
        #     key = curr_conns[fd]
        #     key.fileobj.close()

    async def tcp_send(self, message: bytes):
        print(f"sending {message.decode()}")
        msg = int.to_bytes(3) + "hi,".encode() + message
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
            print(f"receiving {data}")
            receive_buffer += data
            if len(receive_buffer) == yet_reading_size:
                if state == "idle":
                    state = "reading_body"
                    yet_reading_size = struct.unpack("i", receive_buffer)[0]
                    receive_buffer = b''
                elif state == "reading_body":
                    self.chat_windows["hi"].display_message(data.decode())
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
