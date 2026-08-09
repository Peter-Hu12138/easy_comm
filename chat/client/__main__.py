import sys

from . import gui

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("usage: python -m chat.client server_ip port_to_connect_to name_in_chat_room")
        sys.exit(1)
    gui.main(sys.argv[1], int(sys.argv[2]), sys.argv[3])
