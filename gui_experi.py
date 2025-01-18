from tkinter import ttk
import tkinter as tk

def new_chat_window(sk, ):


root = tk.Tk()

# Set window size
root.geometry("400x300")  # width x height

# Create input fields
room_label = ttk.Label(root, text="Room ID:")
room_label.pack()
room_entry = ttk.Entry(root)
room_entry.pack()

pass_label = ttk.Label(root, text="Password:")
pass_label.pack()
pass_entry = ttk.Entry(root)
pass_entry.pack()

# Create buttons
join_button = ttk.Button(root, text="Join")
join_button.pack(pady=5)

create_button = ttk.Button(root, text="Create")
create_button.pack(pady=5)

# tabControl = ttk.Notebook(root)
# tab1 = ttk.Frame(tabControl)
# tab2 = ttk.Frame(tabControl)
# tabControl.add(tab1, text='Tab 1')
# tabControl.add(tab2, text='Tab 2222')
# tabControl.pack(expand=1, fill="both")

root.mainloop()