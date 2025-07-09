# utils/toast_manager.py

import customtkinter as ctk

class ToastManager:
    @staticmethod
    def show(master, message, duration=3000, color="#2e8b57"):
        toast = ctk.CTkLabel(
            master,
            text=message,
            fg_color=color,
            text_color="white",
            corner_radius=6,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        toast.place(relx=0.5, rely=0.90, anchor="s")
        toast.lift()
        master.after(duration, toast.destroy)

    @staticmethod
    def show_success(master, message, duration=3000):
        ToastManager.show(master, f"✅ {message}", duration, color="#2e8b57")  # Green

    @staticmethod
    def show_warning(master, message, duration=3000):
        ToastManager.show(master, f"⚠️ {message}", duration, color="#d2691e")  # Orange

    @staticmethod
    def show_error(master, message, duration=3000):
        ToastManager.show(master, f"❌ {message}", duration, color="#8B0000")  # Red

    @staticmethod
    def show_info(master, message, duration=3000):
        ToastManager.show(master, f"ℹ️{message}", duration, color="#1e90ff")  # Dodger Blue
