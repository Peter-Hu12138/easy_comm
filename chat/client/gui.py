from __future__ import annotations
import asyncio
import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText

from . import net

TK_PUMP_INTERVAL = 0.02


class ChatWindow(tk.Toplevel):
    def __init__(self, app: App, room_name: str, operation: str, password: str, master=None):
        super().__init__(master=master)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.app = app
        self.title(f"Chat Client -- welcome for using, {app.name} -- room: {room_name}")

        self.text_area = ScrolledText(self, wrap=tk.WORD, state=tk.DISABLED)
        self.text_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        self.input_field = tk.Entry(self)
        self.input_field.pack(padx=10, pady=10, fill=tk.X)
        self.input_field.bind("<Return>", self.send_message)

        self.display_message(
            "Welcome to use EASY COMM, developed by Jingtian Hu at the University of Toronto.")

        self.conn = net.RoomConnection(
            app.host, app.port, room_name,
            on_response=self.on_response,
            on_chat=lambda text: self.display_message(f"Received: {text}"),
            on_disconnect=self.on_disconnect)
        self.conn_task = asyncio.get_running_loop().create_task(
            self.conn.run(operation, password))

    def on_response(self, ok: bool, detail: str):
        if ok:
            self.display_message(f"Joined room: {detail}")
        else:
            self.display_message(f"Request failed: {detail}")
            self.input_field.config(state=tk.DISABLED)

    def on_disconnect(self):
        if self.winfo_exists():
            self.display_message("Server closed the connection, please close this window and try again")
            self.input_field.config(state=tk.DISABLED)

    def display_message(self, text: str):
        self.text_area.config(state=tk.NORMAL)
        self.text_area.insert(tk.END, text + "\n")
        self.text_area.yview(tk.END)
        self.text_area.config(state=tk.DISABLED)

    def send_message(self, event=None):
        text = self.input_field.get()
        if text and self.conn.joined:
            self.conn.send_chat(f"{self.app.name} said: {text}")
            self.display_message(f"Sent: {text}")
            self.input_field.delete(0, tk.END)

    def on_closing(self):
        self.app.close_chat_window(self)


class App:
    """The lobby window. Owns the Tk root and keeps it alive from inside the
    asyncio loop instead of tk.mainloop(), so socket coroutines and the GUI
    share one thread."""

    def __init__(self, host: str, port: int, name: str):
        self.host = host
        self.port = port
        self.name = name
        self.chat_windows: set[ChatWindow] = set()
        self.running = True

        self.root = tk.Tk()
        self.root.title(f"Easy_comm - Welcome back, {name}!")
        self.root.geometry("400x300")
        self.root.protocol("WM_DELETE_WINDOW", self.quit)

        ttk.Label(self.root, text="Room name:").pack()
        self.room_entry = ttk.Entry(self.root)
        self.room_entry.pack()

        ttk.Label(self.root, text="Password:").pack()
        self.pass_entry = ttk.Entry(self.root, show="*")
        self.pass_entry.pack()

        ttk.Button(self.root, text="join",
                   command=lambda: self.open_room("join")).pack(pady=5)
        ttk.Button(self.root, text="create",
                   command=lambda: self.open_room("create")).pack(pady=5)

    def open_room(self, operation: str):
        room_name = self.room_entry.get()
        password = self.pass_entry.get()
        if not room_name:
            return
        self.room_entry.delete(0, tk.END)
        self.pass_entry.delete(0, tk.END)
        print(f"starting connection to {(self.host, self.port)}, room {room_name}")
        self.chat_windows.add(ChatWindow(self, room_name, operation, password))

    def close_chat_window(self, chat_window: ChatWindow):
        self.chat_windows.discard(chat_window)
        chat_window.conn.close()
        chat_window.conn_task.cancel()
        chat_window.destroy()

    def quit(self):
        self.running = False

    async def run(self):
        # tk is pumped from the asyncio loop: no mainloop(), no second thread
        while self.running:
            self.root.update()
            await asyncio.sleep(TK_PUMP_INTERVAL)
        for chat_window in list(self.chat_windows):
            self.close_chat_window(chat_window)
        self.root.destroy()


def main(host: str, port: int, name: str):
    app = App(host, port, name)
    try:
        asyncio.run(app.run())
    except KeyboardInterrupt:
        print("ctrl+c detected, exiting")
