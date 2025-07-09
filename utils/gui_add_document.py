import random

import customtkinter as ctk
from tkinter import filedialog, messagebox
import os
import shutil
import sqlite3
import time

from datetime import datetime
from db_init import init_db
from tkcalendar import DateEntry

from toast_manager import ToastManager

# 🔐 Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "db", "document_store.db")
DOCS_DIR = os.path.join(BASE_DIR, "documents")

# ✅ Initialize DB
init_db()

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class DocumentUploader(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Document Form")
        self.geometry("450x600")
        icon_path = os.path.join(BASE_DIR, "assets", "icon.ico")
        self.iconbitmap(icon_path)
        self.grid_columnconfigure(1, weight=1)

        # Row 0: Title
        ctk.CTkLabel(self, text="Title:").grid(row=0, column=0, padx=10, pady=10, sticky="e")
        self.title_entry = ctk.CTkEntry(self)
        self.title_entry.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        # Row 1: Type
        ctk.CTkLabel(self, text="Type:").grid(row=1, column=0, padx=10, pady=10, sticky="e")
        self.type_option = ctk.CTkOptionMenu(self, values=["incoming", "outgoing", "others"])
        self.type_option.set("incoming")
        self.type_option.grid(row=1, column=1, padx=10, pady=10, sticky="w")

        # Row 1.5: class
        ctk.CTkLabel(self, text="Class:").grid(row=2, column=0, padx=10, pady=10, sticky="e")
        self.class_option = ctk.CTkOptionMenu(self, values=["advisory", "circular", "endorsement", "executive order", "memorandum", "office order", "ordinance", "policy", "resolution", "others"])
        self.class_option.set("advisory")
        self.class_option.grid(row=2, column=1, padx=10, pady=10, sticky="w")


        # 📅 Date Entry
        ctk.CTkLabel(self, text="Date:").grid(row=4, column=0, sticky="e", pady=10, padx=10)
        self.date_entry = ctk.CTkEntry(self)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))  # Default to today
        self.date_entry.grid(row=4, column=1, pady=10, padx=10, sticky="ew")

        # ⏰ Time Entry
        ctk.CTkLabel(self, text="Time:").grid(row=5, column=0, sticky="e", pady=10, padx=10)
        self.time_entry = ctk.CTkEntry(self)
        self.time_entry.insert(0, datetime.now().strftime("%H:%M:%S"))  # Default to now
        self.time_entry.grid(row=5, column=1, pady=10, padx=10, sticky="ew")

        # Row 3: Sender
        ctk.CTkLabel(self, text="Sender:").grid(row=6, column=0, padx=10, pady=10, sticky="e")
        self.sender_entry = ctk.CTkEntry(self)
        self.sender_entry.grid(row=6, column=1, padx=10, pady=10, sticky="ew")

        # Row 4: Recipient
        ctk.CTkLabel(self, text="Recipient:").grid(row=7, column=0, padx=10, pady=10, sticky="e")
        self.recipient_entry = ctk.CTkEntry(self)
        self.recipient_entry.grid(row=7, column=1, padx=10, pady=10, sticky="ew")

        # Row 5: Description
        ctk.CTkLabel(self, text="Description:").grid(row=8, column=0, padx=10, pady=10, sticky="e")
        self.desc_entry = ctk.CTkTextbox(self, height=100)  # ~4 rows
        self.desc_entry.grid(row=8, column=1, padx=10, pady=10, sticky="ew")

        # Row 6: File Picker
        ctk.CTkLabel(self, text="Select File:").grid(row=9, column=0, padx=10, pady=10, sticky="e")
        self.file_button = ctk.CTkButton(self, text="📁 Browse", command=self.select_file)
        self.file_button.grid(row=9, column=1, padx=10, pady=10, sticky="w")

        # Row 7: Submit Button
        self.submit_button = ctk.CTkButton(self, text="➕ Save Document", command=self.add_document)
        self.submit_button.grid(row=10, column=0, columnspan=2, pady=20)

        self.file_path = None

    def select_file(self):
        filetypes = [("PDF files", "*.pdf"), ("Image files", "*.jpg *.png"), ("All files", "*.*")]
        self.file_path = filedialog.askopenfilename(title="Select Document", filetypes=filetypes)
        if self.file_path:
            self.file_button.configure(text=os.path.basename(self.file_path))

    def add_document(self):
        title = self.title_entry.get().strip()
        doc_type = self.type_option.get().strip()
        doc_class = self.class_option.get().strip()
        date_str = self.date_entry.get().strip()
        time_str = self.time_entry.get().strip()
        sender = self.sender_entry.get().strip() or None
        recipient = self.recipient_entry.get().strip() or None
        description = self.desc_entry.get("1.0", "end").strip() or None

        if not title or not date_str or not self.file_path:
            messagebox.showerror("Missing Info", "Please fill in all required fields.")
            return

        try:
            # Parse and reformat into filename-friendly string
            dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M:%S")
            timestamp_str = dt.strftime("%Y_%m_%d_%H%M%S")  # e.g., "2025_07_08_144530"
        except ValueError:
            ToastManager.show_error(self, "Invalid date or time format.")
            return

        folder_map = {"incoming": "incoming", "outgoing": "outgoing", "others": "others"}
        folder = folder_map.get(doc_type)

        if not folder:
            ToastManager.show_warning(self, f"Unrecognized document type: {doc_type}")
            return
        dest_dir = os.path.join(DOCS_DIR, folder)
        os.makedirs(dest_dir, exist_ok=True)

        # Generate a short random number to ensure uniqueness
        rand_suffix = str(random.randint(100, 999))  # e.g., "742"

        # Get original file extension
        original_ext = os.path.splitext(self.file_path)[1]  # e.g., ".pdf"

        # Build new filename
        new_filename = f"{timestamp_str}_{rand_suffix}{original_ext}"
        dest_path = os.path.join(dest_dir, new_filename)

        try:
            shutil.copy2(self.file_path, dest_path)
        except Exception as e:
            messagebox.showerror("File Error", f"Could not move file: {e}")
            return

        relative_path = os.path.relpath(dest_path, BASE_DIR)

        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO documents (title, doc_type,doc_class, date, sender, recipient, description, file_path)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (title, doc_type, doc_class, dt, sender, recipient, description, relative_path))
            conn.commit()
            conn.close()
            ToastManager.show_success(self, "Document updated successfully!")
            self.reset_form()
        except sqlite3.Error as e:
            ToastManager.show_error(self, f"Database error: {str(e)}")

    def reset_form(self):
        self.title_entry.delete(0, 'end')
        # self.date_entry.delete(0, 'end')
        # self.time_entry.delete(0, 'end')
        self.sender_entry.delete(0, 'end')
        self.recipient_entry.delete(0, 'end')
        self.desc_entry.delete(1.0, 'end')
        self.file_button.configure(text="📁 Browse")
        self.file_path = None

if __name__ == "__main__":
    app = DocumentUploader()
    app.mainloop()
