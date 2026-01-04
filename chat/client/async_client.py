import asyncio
import tkinter as tk
import aioconsole, struct
import ssl

ETX = b'\x03'  # End of Text

context = ssl.create_default_context()

# async def tcp_rec(reader: asyncio.StreamReader):
#     while True:
#         data = await reader.read(8964)
#         print(f'Received: {data.decode()!r}')

# async def tcp_send(writer: asyncio.StreamWriter):
#     while True:
#         line = await aioconsole.ainput("Send to chat:")
#         writer.write(int.to_bytes(6) + "hi,".encode() + line.encode() + ETX)
#         await writer.drain()  # Ensure data is sent

async def tcp_client():
    tasks = set()
    reader, writer = await asyncio.open_connection('127.0.0.1', 8000, ssl=context)
    asyncio.create_task(tcp_send(writer))
    await asyncio.create_task(tcp_rec(reader))

async def tcp_send(writer):
        while True:
            line = await aioconsole.ainput("Send to chat:")
            message = line
            msg = int.to_bytes(3) + "hi,".encode() + message.encode()
            print(f"sending {msg}")
            writer.write(struct.pack("i", len(msg)) + msg) # Send prefix + msg
            print("before draining")
            await writer.drain()  # Ensure data is sent
            print("after draining")

        

async def tcp_rec(reader: asyncio.StreamReader):
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
                    print(data.decode())
                    state = "idle"
                    yet_reading_size = 4
                    receive_buffer = b''
        print("quitting rec")

async def main():
    await tcp_client()

if __name__ == '__main__':
    asyncio.run(main())


# root = tk.Tk()

# label = tk.Label(root)
# label.pack()

# tk.Button(root, text="Start", command=counter).pack()

# async_mainloop(root)