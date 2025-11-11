import socket, select, ssl
ETX = b'\x03'  # End of Text


client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(("localhost", 8000))
hostname = '127.0.0.1'
context = ssl.create_default_context()
read_buffer = b''
to_send = b''
sock = context.wrap_socket(client_socket, server_hostname=hostname)

while True:
    readable, writable, _ = select.select([sock], [sock] if to_send else [], [], 0.1)
    if writable:
        wsock: socket.socket = writable[0]
        sent = wsock.send(to_send)
        to_send = to_send[sent:]

    if readable:
        rsock: socket.socket = readable[0]
        read_buffer += rsock.recv(2048)

    else:
        print(read_buffer.decode("utf-8"), end="")
        read_buffer = b""
        to_send = int.to_bytes(6) + "hi,".encode() + input("Input what will be echoed back:").encode("utf-8") + ETX