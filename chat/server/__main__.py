import sys

from . import manager

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage: python -m chat.server port_to_listen_to")
        sys.exit(1)
    manager.main("0.0.0.0", int(sys.argv[1]))
