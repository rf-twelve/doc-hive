# utils/base_popup.py

import customtkinter as ctk

class BasePopup(ctk.CTkToplevel):
    def __init__(self, master, title="Popup", size="500x500"):
        super().__init__(master)
        self.title(title)
        self.geometry(size)
        self.attributes("-alpha", 0.0)
        self.fade_in()

    def fade_in(self):
        alpha = self.attributes("-alpha")
        if alpha < 1.0:
            alpha += 0.1
            self.attributes("-alpha", alpha)
            self.after(20, self.fade_in)

    def show_toast(self, message, color="#2e8b57"):
        toast = ctk.CTkLabel(self, text=message, fg_color=color, text_color="white", corner_radius=6)
        toast.place(relx=0.5, rely=0.8, anchor="s")
        toast.lift()
        self.after(5000, toast.destroy)

    def disable_widgets(self, widgets):
        for widget in widgets:
            widget.configure(state="disabled")

    def enable_widgets(self, widgets):
        for widget in widgets:
            widget.configure(state="normal")
