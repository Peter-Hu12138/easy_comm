import tkinter as tk
from tkinter import ttk
from tkinter.constants import *

from chat_display import ClickableInfoFrame
from scroll_frame import ScrollFrame

class VerticalScrolledFrame(ttk.Frame):
    """A pure Tkinter scrollable frame that actually works!
    * Use the 'interior' attribute to place widgets inside the scrollable frame.
    * Construct and pack/place/grid normally.
    * This frame only allows vertical scrolling.
    """
    def __init__(self, parent, *args, **kw):
        ttk.Frame.__init__(self, parent, *args, **kw)

        # Create a canvas object and a vertical scrollbar for scrolling it.
        vscrollbar = ttk.Scrollbar(self, orient=VERTICAL)
        vscrollbar.pack(fill=Y, side=RIGHT, expand=FALSE)
        canvas = tk.Canvas(self, bd=0, highlightthickness=0,
                           yscrollcommand=vscrollbar.set)
        canvas.pack(side=LEFT, fill=BOTH, expand=TRUE)
        vscrollbar.config(command=canvas.yview)

        # Reset the view
        canvas.xview_moveto(0)
        canvas.yview_moveto(0)

        # Create a frame inside the canvas which will be scrolled with it.
        self.interior = interior = ttk.Frame(canvas)
        interior_id = canvas.create_window(0, 0, window=interior,
                                           anchor=NW)

        # Track changes to the canvas and frame width and sync them,
        # also updating the scrollbar.
        def _configure_interior(event):
            # Update the scrollbars to match the size of the inner frame.
            size = (interior.winfo_reqwidth(), interior.winfo_reqheight())
            canvas.config(scrollregion="0 0 %s %s" % size)
            if interior.winfo_reqwidth() != canvas.winfo_width():
                # Update the canvas's width to fit the inner frame.
                canvas.config(width=interior.winfo_reqwidth())
        interior.bind('<Configure>', _configure_interior)

        def _configure_canvas(event):
            if interior.winfo_reqwidth() != canvas.winfo_width():
                # Update the inner frame's width to fill the canvas.
                canvas.itemconfigure(interior_id, width=canvas.winfo_width())
        canvas.bind('<Configure>', _configure_canvas)

class CardApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Easy Communication Everywhere")
        self.geometry("1200x800")

        self.navbar = tk.Frame(self)
        self.navbar.pack(side = 'left',fill='y')

        self.admin_button = ttk.Button(self.navbar, text="Join / Create a Room")
        self.admin_button.pack(side= 'bottom', fill='x')

        def on_card_clicked(card_id):
            print(f"Card ID {card_id} was clicked!")

        # self.chat_room_scrollable = VerticalScrolledFrame(self.navbar)
        # self.chat_room_scrollable.pack(side='top', fill='both')
        # for i in range(10):


        

        # 1. The Container (Acts as the JPanel with CardLayout)
        self.container = tk.Frame(self)
        self.container.pack(fill="both", expand=True)


        # Configure grid to allow the container to expand
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        # Dictionary to keep track of frames (like giving strings to CardLayout)

        
        self.frames = {}
        
        self.scrollFrame = ScrollFrame(self.navbar) # add a new scrollable frame.
        
        # Now add some controls to the scrollframe. 
        # NOTE: the child controls are added to the view port (scrollFrame.viewPort, NOT scrollframe itself)
        for row in range(10):
            self.room_info = ClickableInfoFrame(self.scrollFrame.viewPort, "secret chat", "sd: hi", 20, command=lambda: on_card_clicked("SERVER-01"))
            self.room_info.pack(fill='x')
            # a = row
            # tk.Label(self.scrollFrame.viewPort, text="%s" % row, width=3, borderwidth="1", 
            #          relief="solid").grid(row=row, column=0)
            # t="this is the second column for row %s" %row
            # tk.Button(self.scrollFrame.viewPort, text=t, command=lambda x=a: self.printMsg("Hello " + str(x))).grid(row=row, column=1)

        # when packing the scrollframe, we pack scrollFrame itself (NOT the viewPort)
        self.scrollFrame.pack(side="top", fill="both", expand=True)
    
    def printMsg(self, msg):
        print(msg)

    def show_frame(self, page_name):
        '''Equivalent to cardLayout.show(parent, "name")'''
        frame = self.frames[page_name]
        frame.tkraise() # Brings this frame to the top of the stack

if __name__ == "__main__":
    app = CardApp()
    app.mainloop()