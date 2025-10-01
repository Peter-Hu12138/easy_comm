import socket, select
ETX = b'\x03'  # End of Text

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(("localhost", 8000))
to_send = int.to_bytes(4) + "hi,".encode() + (input("Input what will be echoed back:")).encode("utf-8") + ETX
read_buffer = b''
while True:
    readable, writable, _ = select.select([client_socket], [client_socket], [])
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
        to_send = int.to_bytes(4) + "hi,".encode() + input("Input what will be echoed back:").encode("utf-8") + ETX
