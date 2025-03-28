from __future__ import annotations
import selectors
import socket
import sys
import types
import tkinter as tk
from tkinter.scrolledtext import ScrolledText
from help_manual import cmd
from tkinter import ttk

STX = b'\x02'  # Start of Text
ETX = b'\x03'  # End of Text


class ChatWindow(tk.Toplevel):
    manager: Manager
    text_area: ScrolledText
    input_field: tk.Entry
    key: selectors.SelectorKey
    messages: str
    room_id: int
    is_failed: bool

    def __init__(self, manager: Manager, room_id: int = -1, sk: selectors.SelectorKey = None, master=None):
        super().__init__(master=master)  # initialize the window object
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.manager = manager

        self.key = sk
        self.room_id = room_id

        self.title(f"Chat Client -- welcome for using, {sk.data.name} -- room id: {self.room_id}")
        self.text_area = ScrolledText(self, wrap=tk.WORD, state=tk.DISABLED)
        self.text_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        self.text_area.config(state=tk.NORMAL)

        self.input_field = tk.Entry(self)
        self.input_field.pack(padx=10, pady=10, fill=tk.X)
        self.input_field.bind("<Return>", self.send_message)

        self.is_failed = False

        self.display_message(
            "Welcome to use EASY COMM, developed by Jingtian Hu at the University of Toronto. For help, enter \"/help\"")

    def service_connection(self, key, mask):
        sock: socket.socket = key.fileobj
        data = key.data
        if mask & selectors.EVENT_READ:
            recv_data: bytes = sock.recv(1024)  # Should be ready to read
            if recv_data:
                if recv_data.startswith(STX):
                    self.display_message(f"Received from server: {recv_data.decode()}")
                    if b"fail" in recv_data:
                        self.input_field.config(state=tk.DISABLED)
                else:
                    self.display_message(f"Received {recv_data.decode()}")
                    data.recv_total += len(recv_data)
            else:
                if not self.is_failed:
                    self.display_message(f"Server closed the connection, please close this window and try again")
                    self.is_failed = True

        if mask & selectors.EVENT_WRITE:
            if data.outb:
                sent = sock.send(data.outb)  # Should be ready to write
                data.outb = data.outb[sent:]

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
                self.messages = f"{self.key.data.name} said: {self.input_field.get()}"
                self.key.data.outb += self.messages.encode()
                self.messages = ""
            self.input_field.delete(0, tk.END)

    def on_closing(self):
        self.manager.close_chat_window(self)



class Manager():
    sel: selectors.DefaultSelector
    chat_windows: set[ChatWindow]
    root: tk.Tk
    name: str
    server_addr: tuple[str, int]

    def __init__(self, host, port, name):
        self.server_addr = (host, int(port))
        self.name = name
        self.sel = selectors.DefaultSelector()
        self.chat_windows = set()
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
        self.root.after(20, self.check_socket)
        self.root.mainloop()

    def add_new_conn(self, operation: str):
        """
        creates a chatwindow with a newly created socket, then try to validate with the server with a formatted message.
        """
        room_id = int(self.room_entry.get())
        self.room_entry.delete(0, tk.END)
        password = int(self.pass_entry.get())
        self.pass_entry.delete(0, tk.END)
        print(f"Starting connection to {server_addr} room number {room_id}")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setblocking(False)
        sock.connect_ex(server_addr)
        events = selectors.EVENT_READ | selectors.EVENT_WRITE
        data = types.SimpleNamespace(
            recv_total=0,
            outb=b"",
            name=self.name,
            window=-1,
        )
        key = self.sel.register(sock, events, data=data)
        chat_window = ChatWindow(manager=self, room_id=room_id, sk=key)
        data.window = chat_window

        if operation == "join":
            key.data.outb += f"join,{room_id},{password},".encode() + ETX
        if operation == "create":
            key.data.outb += f"create,{room_id},{password},".encode() + ETX

        self.chat_windows.add(chat_window)

    def close_chat_window(self, chat_window: ChatWindow):
        print("before closing:")
        print(self.chat_windows)
        print(dict(self.sel.get_map()))
        self.chat_windows.remove(chat_window)
        self.sel.unregister(chat_window.key.fileobj)
        chat_window.key.fileobj.close()
        chat_window.destroy()
        print("after closing:")
        print(self.chat_windows)
        print(dict(self.sel.get_map()))

    def quit(self):
        self.root.quit()
        curr_conns = dict(self.sel.get_map())
        for fd in curr_conns:
            key = curr_conns[fd]
            key.fileobj.close()
        self.sel.close()

    def check_socket(self):
        # print("check+socket working properly")
        if len(self.chat_windows) > 0:
            events = self.sel.select(timeout=0)
            if events:
                for key, mask in events:
                    key.data.window.service_connection(key, mask)
        self.root.after(20, self.check_socket)

if __name__ == "__main__":
    host, port, name = sys.argv[1], sys.argv[2], sys.argv[3]
    print(host, port, name)

    server_addr = (host, int(port))

    manager = Manager(host=host, port=port, name=name)

    try:
        manager.start()
    except KeyboardInterrupt:
        print("ctrl+c detected exiting")
    finally:
        manager.quit()
