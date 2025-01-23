import shlex
import selectors
import tkinter

def cmd(line: str, sk: selectors.SelectorKey, window: tkinter.Toplevel, display_message: callable) -> None:
    """
    Commands:
    ---------
    /help
        Prints the help manual for commands

    /changename <newname>
        Changes the user's display name in the chat.
        - newname: New display name to be used (required)
        Example: /changename JohnDoe

    See 'help' command for full list of available commands.

    Returns: None
    """
    args = shlex.split(line)
    if args[0] == "help":
        display_message(cmd.__doc__)
    elif args[0] == "changename":
        sk.data.name = args[1]
        window.title(f"Chat Client -- welcome for using, {sk.data.name} -- room id {window.room_id}")
