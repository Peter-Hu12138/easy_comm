# problems:
# 1. I/O model?
# 2. are socket.read write blocking?
# 3. selector mechanism?
# 4. threading model? pros and cons?
# 5. why this shit's conn socket has the same port as the listenning one.
import sys
import socket
import selectors
import types

rooms: dict[int, int] = {}
STX = b'\x02'  # Start of Text
ETX = b'\x03'  # End of Text

def disconnect(sock, data):
    print(f"closing connection to {data.addr}")
    # rooms.pop(data.id) # TODO: handle room_id release
    # print(f"released id {data.id}")
    sel.unregister(sock)
    sock.close()

def intial_accept(sock: socket.socket):
    conn, addr = sock.accept() # any sock passed is ready to read (accept in this for a listening socket), so the line is guranteed non blocking
    print(f"accepted connection from {addr}")
    conn.setblocking(False)
    data = types.SimpleNamespace(addr=addr, inb=b"", outb=b"", confirmed=False, succ=False, id=-1) # hold data included with a simple name space object
    events = selectors.EVENT_READ | selectors.EVENT_WRITE # '|' stands for bitwise or, this is creating a mask for both read and write
    sel.register(conn, events, data=data)

def confirm_accept(key: selectors.SelectorKey, mask):
    global rooms
    sock: socket.socket = key.fileobj
    data = key.data
    if mask & selectors.EVENT_READ:
        recv_data: bytes = sock.recv(2048)
        if recv_data:
            data.inb += recv_data
            if recv_data.endswith(ETX):
                id = int(data.inb.split(b",")[1])
                password = int(data.inb.split(b",")[2])
                print(f"confirmation message compelete, {data.inb}")
                if data.inb.startswith(b"create"):
                    if id in rooms:
                        data.outb += STX + b"failed, id exists, please enter another id" # fail, id already exists
                    else:
                        data.outb += STX + b"successful, room created"
                        data.succ = True
                        data.id = id
                        rooms[id] = password # creates room
                elif data.inb.startswith(b"join"):
                    if id in rooms:
                        if rooms[id] == password:
                            data.outb += STX + b"successful, joining"
                            data.succ = True
                            data.id = id
                        else:
                            data.outb += STX + b"failed, wrong password"
                    else:
                        data.outb += STX + b"failed, no room exists, must create such room first"
                else:
                    pass
        else:
            disconnect(sock, data)
    if mask & selectors.EVENT_WRITE:
        if data.outb:
            # if data.outb.startswith(b"successful"):
            #     data.confirmed = True
            #     sent = sock.send(data.outb)
            #     data.outb = data.outb[sent:]
            # if data.outb.startswith(b"successful"):
            # print(f"echoing {data.outb!r} to {data.addr}")
            sent = sock.send(data.outb)
            data.outb = data.outb[sent:]
            if not data.outb:
                if data.succ:
                    data.confirmed = True
                else:
                    disconnect(sock, data)

def service_connection(key: selectors.SelectorKey, mask):
    """
    Used to service a confirmed (validated into a room) connection
    """
    sock = key.fileobj
    data = key.data

    if mask & selectors.EVENT_READ:
        recv_data = sock.recv(1024)
        if recv_data:
            # data.outb += recv_data
            curr_conns = dict(sel.get_map())
            for fd in curr_conns:
                sk = curr_conns[fd]
                if sk.data is not None and fd != key.fileobj.fileno() and sk.data.id == data.id:
                    # make sure it is not the listenning socket and it is not the socket we receive data from
                    sk.data.outb += recv_data
        else:
            disconnect(sock, data)
    if mask & selectors.EVENT_WRITE:
        if data.outb:
            print(f"echoing {data.outb!r} to {data.addr}")
            sent = sock.send(data.outb)
            data.outb = data.outb[sent:]


sel = selectors.DefaultSelector()

host, port = '127.0.0.1', int(sys.argv[1])
lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
lsock.bind((host, port))
lsock.listen()
print(f"listening on {(host, port)}")
lsock.setblocking(False)
sel.register(lsock, selectors.EVENT_READ, data=None)

try:
    while True:
        events = sel.select(timeout=None)
        for key, mask in events:
            if key.data is None:
                intial_accept(key.fileobj)
            else:
                if not key.data.confirmed:
                    confirm_accept(key, mask)
                else:
                    service_connection(key, mask)
except KeyboardInterrupt:
    print("keyboard interrupt, exiting")
finally:
    sel.close()
