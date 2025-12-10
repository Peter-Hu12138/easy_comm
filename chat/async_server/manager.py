import socket, asyncio
import connection, message, message_dispatcher, message_dispenser
import select, ssl
import traceback

class Manager:
    connections: dict[tuple[str, int], connection.Connection]
    connection_main_coros: list[connection.Connection.main]
    conn_secrets: dict[tuple[str, int], str]
    rooms: dict[str, connection.ChatRoom]

    manager_queue: asyncio.Queue[message.Message]

    dispacher: message_dispatcher.MessageDispatcher

    def __init__(self):
        self.manager_queue: asyncio.Queue[message.Message] = asyncio.Queue()
        self.connections: dict[tuple[str, int], connection.Connection] = {}
        self.connection_main_coros = []
        self.rooms: dict[str, connection.ChatRoom] = {}
        self.handler = message_dispenser.MessageHandler(self.connections, self.rooms)
        self.dispacher = message_dispatcher.MessageDispatcher(self.handler)
        self.conn_secrets = {}

    def create_connection(self, reader, writer):
        try:
            addr = writer.get_extra_info('peername')
            conn = connection.Connection(addr, self.manager_queue, reader, writer)
            self.connections[addr] = conn
            self.connection_main_coros.append(asyncio.create_task(conn.main()))
        finally:
            pass

    async def process_manager_request(self, req: message.Message):
        await self.dispacher.dispatch(req)

    async def server_on(self, server):
        async with server:
            await server.serve_forever()

    async def close_conn(self, connection: tuple[str, int]):
        del self.connections[connection]

    async def main(self, port: int):
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain('/home/jthu/Documents/easy_comm/experiment/ssl/server.crt', '/home/jthu/Documents/easy_comm/experiment/ssl/server.key')
        
        server = await asyncio.start_server(self.create_connection, '127.0.0.1', 8000, ssl=context)

        addrs = ', '.join(str(sock.getsockname()) for sock in server.sockets)
        print(f'Serving on {addrs}')

        asyncio.create_task(self.server_on(server))

        try:
            while True:
                request = await self.manager_queue.get()
                print("get new request in manger queue")
                await self.process_manager_request(request)
        except KeyboardInterrupt:
            print("ctrl-c detected, existing...")
        # except Exception as e:
        #     print(f"unexpected error {e}")
        
        server.close()
        await server.wait_closed()
        # TODO: cancel connections gently
        print("main thread exiting")

if __name__ == "__main__":
    manager = Manager()
    asyncio.run(manager.main(8000))
