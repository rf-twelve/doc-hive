# utils/custom_toast.py

import customtkinter as ctk

def show_toast(master, message, duration=3000, color="#2e8b57"):
    toast = ctk.CTkLabel(
        master,
        text=message,
        fg_color=color,
        text_color="white",
        corner_radius=6,
        font=ctk.CTkFont(size=14, weight="bold")
    )
    toast.place(relx=0.5, rely=0.95, anchor="s")
    toast.lift()
    master.after(duration, toast.destroy)
