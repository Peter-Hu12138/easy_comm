import tkinter as tk
from tkinter import ttk

root = tk.Tk()
notebook = ttk.Notebook(root)

# Create two frames for the two cards
frame1 = ttk.Frame(notebook)
frame2 = ttk.Frame(notebook)

# Add the frames to the notebook
notebook.add(frame1, text='Card 1')
notebook.add(frame2, text='Card 2')

notebook.pack()

# To show the second card, call notebook.select() with the identifier for frame2
# The identifier is the frame object itself
notebook.select(frame2)

root.mainloop()
