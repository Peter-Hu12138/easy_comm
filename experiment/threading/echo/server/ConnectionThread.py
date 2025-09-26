import threading, socket, select

class ConnectionThread(threading.Thread):
    sock: socket.socket
    def __init__(self, sock: socket.socket, group = None, target = None, name = None, args = ..., kwargs = None, *, daemon = None):
        super().__init__(group, target, name, args, kwargs, daemon=daemon)
        self.sock = sock

    def handle_connection(self):
        sock = self.sock
        read_buffer: bytes = b''
        ready_to_send = b''
        write_buffer: bytes = b''
        def process_incoming_chunk(chunk: bytes):
            pass

        while True:
            readable, writable, _ = select.select([sock], [sock], [])
            if readable:
                rsock: socket.socket = readable[0]
                chunk = rsock.recv(8192)
                if len(chunk) == 0:
                    break
                idx = chunk.find(ETX)
                print(f"receiving {chunk}")

                if idx != -1:
                    chunk = chunk[:idx] + b"\n" + chunk[idx + 1:]
                read_buffer += chunk

            if writable:
                if not read_buffer: continue
                wsock: socket.socket = writable[0]
                sent = wsock.send(read_buffer)
                print(f"sending {read_buffer[:sent]}")
                read_buffer = read_buffer[sent:]
        sock.close()
        print("a conn closing....")

    def run(self):
        self.handle_connection()
