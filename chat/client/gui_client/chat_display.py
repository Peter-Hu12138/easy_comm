import tkinter as tk
from tkinter import font as tkfont

class ClickableInfoFrame(tk.Frame):
    """
    A custom Tkinter Frame acting as a clickable card with three distinct areas:
    - Top Left: A boxed short string.
    - Top Right: A number inside a red circular badge.
    - Bottom Left: A long message (truncated if necessary).
    """

    def __init__(self, parent, tl_text, bl_message, tr_number, command=None, **kwargs):
        """
        Args:
            parent: The parent widget.
            tl_text (str): Text for top-left box.
            bl_message (str): Long message for bottom-left.
            tr_number (int/str): Number for the top-right red circle.
            command (function, optional): Callback function when frame is clicked.
            **kwargs: Standard Frame arguments (e.g., bg, relief, borderwidth).
        """
        # Set default styling if not provided in kwargs
        kwargs.setdefault('relief', tk.RAISED)
        kwargs.setdefault('borderwidth', 2)
        kwargs.setdefault('bg', '#f0f0f0') # Light gray background for the card
        
        super().__init__(parent, **kwargs)
        
        self.command = command
        self._bg_color = kwargs['bg'] # remember bg color for hover effects later if desired

        # --- Layout Configuration ---
        # We use a 2x2 grid.
        # Column 0 gets weight 1 (expands horizontally).
        # Column 1 gets weight 0 (stays fixed size for the circle).
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)
        
        # --- 1. Top Left: Boxed String ---
        # We use a Label with a border (highlightbackground/thickness) to look like a box
        self.tl_label = tk.Label(
            self,
            text=tl_text,
            bg="white",
            fg="#333333",
            padx=5, pady=2,
            highlightbackground="#aaaaaa",
            highlightcolor="#aaaaaa",
            highlightthickness=1,
            font=("Arial", 9, "bold")
        )
        # Sticky "w" keeps it to the left
        self.tl_label.grid(row=0, column=0, sticky="w", padx=5, pady=(5, 2))


        self.unread_messages_num = tk.IntVar()
        self.unread_messages_num.set(tr_number)
        # --- 2. Top Right: Number in Red Circle ---
        # We use a small Canvas to draw the circle and text
        canvas_size = 30
        self.tr_canvas = tk.Canvas(self, width=canvas_size, height=canvas_size, 
                                   bg=self._bg_color, highlightthickness=0)
        self.tr_canvas.grid(row=0, column=1, sticky="ne", padx=5, pady=5)

        # Draw red circle filled
        padding = 2
        self.tr_canvas.create_oval(padding, padding, 
                                   canvas_size-padding, canvas_size-padding,
                                   fill="#dd0000", outline="#dd0000")
        # Draw white text centered
        self.tr_canvas.create_text(canvas_size/2, canvas_size/2,
                                   text=str(tr_number), fill="white",
                                   font=("Arial", 10, "bold"))

        self.last_message_var = tk.StringVar()
        # --- 3. Bottom Left: Truncated Message ---
        truncated_msg = self._truncate_text(bl_message, char_limit=50)
        
        self.bl_label = tk.Label(
            self,
            textvariable=self.last_message_var,
            bg=self._bg_color,
            fg="#555555",
            anchor="w", justify="left", # Align text left
            font=("Arial", 9)
        )
        # Spanning 2 columns so long text doesn't get cramped by the circle above it
        self.bl_label.grid(row=1, column=0, columnspan=2, sticky="ew", padx=5, pady=(2, 5))

        # --- Make it clickable ---
        if self.command:
            self._bind_click_events()
            self._setup_hover_effect()

    def clear_unread_message(self):
        pass
    
    def set_last_message(self, message: str):
        self.last_message_var.set(message)

    def _truncate_text(self, text, char_limit):
        """Helper to cut off long text and add ellipsis."""
        if len(text) > char_limit:
            return text[:char_limit-3] + "..."
        return text

    def _bind_click_events(self):
        """
        Binds button-1 click to the main frame AND all its children.
        Crucial step: if you don't bind children, clicking the labels won't trigger the event.
        """
        callback = lambda event: self.command()
        
        # Bind self
        self.bind("<Button-1>", callback)
        
        # Bind all direct children widgets defined in init
        # (Canvas, Labels)
        for child in self.winfo_children():
            child.bind("<Button-1>", callback)
            
            # Note regarding the Canvas: Clicking the *shapes* inside canvas 
            # doesn't automatically bubble up to the canvas widget itself reliably 
            # across platforms. We bind specifically to the canvas tag "all".
            if isinstance(child, tk.Canvas):
                 child.tag_bind("all", "<Button-1>", callback)

    def _setup_hover_effect(self):
        """Optional: Adds a slight visual cue when hovering."""
        # Find a slightly darker shade for hover
        hover_bg = "#e0e0e0"

        def on_enter(e):
            self.config(bg=hover_bg)
            self.bl_label.config(bg=hover_bg)
            self.tr_canvas.config(bg=hover_bg)

        def on_leave(e):
            self.config(bg=self._bg_color)
            self.bl_label.config(bg=self._bg_color)
            self.tr_canvas.config(bg=self._bg_color)

        # Apply bindings recursively
        self.bind("<Enter>", on_enter)
        self.bind("<Leave>", on_leave)
        for child in self.winfo_children():
            child.bind("<Enter>", on_enter)
            child.bind("<Leave>", on_leave)

# =========================================
# DEMO USAGE
# =========================================
if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("400x500")
    root.title("Custom Clickable Frame Demo")
    root.config(bg="white")

    header = tk.Label(root, text="Notifications List", bg="white", font=("Arial", 14))
    header.pack(pady=10)

    # Callback function for the demo
    def on_card_clicked(card_id):
        print(f"Card ID {card_id} was clicked!")

    # --- Example 1: Standard ---
    card1 = ClickableInfoFrame(
        root,
        tl_text="SERVER-01",
        bl_message="CPU usage is critical at 95%. Immediate action required by operations team.",
        tr_number=3,
        command=lambda: on_card_clicked("SERVER-01")
    )
    card1.pack(fill="x", padx=20, pady=5)

    # --- Example 2: Short message, large number ---
    card2 = ClickableInfoFrame(
        root,
        tl_text="EMAIL",
        bl_message="New emails synced.",
        tr_number=99,
        command=lambda: on_card_clicked("EMAIL_SYNC")
    )
    card2.pack(fill="x", padx=20, pady=5)

    # --- Example 3: Very long message showing truncation ---
    long_msg = "This is a very long system log entry that goes on for far too long and will definitely need to be cut off by the widget otherwise it will break the layout entirely."
    card3 = ClickableInfoFrame(
        root,
        tl_text="LOGS",
        bl_message=long_msg,
        tr_number=1,
        command=lambda: on_card_clicked("LOGS_VIEW")
    )
    card3.pack(fill="x", padx=20, pady=5)

    root.mainloop()