import selectors
import socket
import sys
import types
import tkinter as tk
from tkinter.scrolledtext import ScrolledText
from help_manual import cmd

class ChatWindow(tk.Toplevel):
    def __init__(self, title, master = None, cnf = ..., *, background = ..., bd = 0, bg = ..., border = 0, borderwidth = 0, class_ = "Toplevel", colormap = "", container = False, cursor = "", height = 0, highlightbackground = ..., highlightcolor = ..., highlightthickness = 0, menu = ..., name = ..., padx = 0, pady = 0, relief = "flat", screen = "", takefocus = 0, use = ..., visual = "", width = 0):
        super().__init__(master, cnf, background=background, bd=bd, bg=bg, border=border, borderwidth=borderwidth, class_=class_, colormap=colormap, container=container, cursor=cursor, height=height, highlightbackground=highlightbackground, highlightcolor=highlightcolor, highlightthickness=highlightthickness, menu=menu, name=name, padx=padx, pady=pady, relief=relief, screen=screen, takefocus=takefocus, use=use, visual=visual, width=width)
        self.title = title

sel = selectors.DefaultSelector()
messages = b""

def service_connection(key, mask):
    sock = key.fileobj
    data = key.data
    if mask & selectors.EVENT_READ:
        recv_data = sock.recv(1024)  # Should be ready to read
        if recv_data:
            display_message(f"Received {recv_data.decode()}")
            data.recv_total += len(recv_data)
    if mask & selectors.EVENT_WRITE:
        if data.outb:
            sent = sock.send(data.outb)  # Should be ready to write
            data.outb = data.outb[sent:]

def display_message(message: str):
    global text_area
    text_area.config(state=tk.NORMAL)
    text_area.insert(tk.END, message + "\n")
    text_area.yview(tk.END)
    text_area.config(state=tk.DISABLED)

def send_message(event=None):
    global messages
    if input_field.get():
        if input_field.get().startswith("/"):
            cmd(input_field.get()[1:], sk, root, display_message)
        else:
            display_message("Sent: " + input_field.get())
            messages = f"{sk.data.name} said: {input_field.get()}"
            messages = messages.encode()
            sk.data.outb += messages
            messages = b""
        input_field.delete(0, tk.END)



    

host, port, name = '74.48.98.218', sys.argv[1], sys.argv[2]
print(host, port, name)

server_addr = (host, int(port))
print(f"Starting connection to {server_addr}")
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setblocking(False)
sock.connect_ex(server_addr)
events = selectors.EVENT_READ | selectors.EVENT_WRITE
data = types.SimpleNamespace(
    recv_total=0,
    outb=b"",
    name=name
)
sk = sel.register(sock, events, data=data)

root = tk.Tk()
root.title(f"Chat Client -- welcome for using, {sk.data.name}")



text_area = ScrolledText(root, wrap=tk.WORD, state=tk.DISABLED)
text_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

input_field = tk.Entry(root)
input_field.pack(padx=10, pady=10, fill=tk.X)
input_field.bind("<Return>", send_message)

display_message("Welcome to use LETS CHAT, developed by Jingtian Hu at the University of Toronto. For help, enter \"/help\"")

def check_socket():
    events = sel.select(timeout=None)
    if events:
        for key, mask in events:
            service_connection(key, mask)
    root.after(20, check_socket)


try:
    root.after(20, check_socket)
    root.mainloop()
except KeyboardInterrupt:
    print("ctrl+c detected exiting")
finally:
    sock.close()
    sel.close()
    root.quit()


