import asyncio
import tkinter as tk
import aioconsole
import ssl

ETX = b'\x03'  # End of Text

context = ssl.create_default_context()

async def tcp_rec(reader: asyncio.StreamReader):
    while True:
        data = await reader.read(8964)
        print(f'Received: {data.decode()!r}')

async def tcp_send(writer: asyncio.StreamWriter):
    while True:
        line = await aioconsole.ainput("Send to chat:")
        writer.write(int.to_bytes(6) + "hi,".encode() + line.encode() + ETX)
        await writer.drain()  # Ensure data is sent

async def tcp_client():
    tasks = set()
    reader, writer = await asyncio.open_connection('127.0.0.1', 8000, ssl=context)
    tasks.add(asyncio.create_task(tcp_rec(reader)))
    tasks.add(asyncio.create_task(tcp_send(writer)))
    while len(tasks) > 0:
        await asyncio.wait(tasks)

async def main():
    await tcp_client()

if __name__ == '__main__':
    asyncio.run(main())


# root = tk.Tk()

# label = tk.Label(root)
# label.pack()

# tk.Button(root, text="Start", command=counter).pack()

# async_mainloop(root)