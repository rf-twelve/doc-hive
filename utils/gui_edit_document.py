# utils/gui_edit_document.py

import customtkinter as ctk
import os
import sqlite3
from tkcalendar import DateEntry
from base_popup import BasePopup
from toast_manager import ToastManager
from PIL import Image, ImageTk
import tkinter as tk

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

# Adjust path if needed
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "db", "document_store.db")
DOCS_DIR = os.path.join(BASE_DIR, "documents")

class EditDocumentPopup(BasePopup):
    def __init__(self, master, doc_data, refresh_callback):
        super().__init__(master)
        self.transient(master)
        self.grab_set()
        self.focus()
        self.title("Document Form")
        self.geometry("450x500")
        # Load PNG icon
        icon_path = os.path.join(BASE_DIR, "assets", "icon.png")
        icon_image = Image.open(icon_path)
        icon_photo = ImageTk.PhotoImage(icon_image)
        self.wm_iconphoto(True, icon_photo)
        self.doc_id, title, doc_type, doc_class, date, sender, recipient, description, file_path = doc_data
        self.original_type = doc_type
        self.original_path = file_path
        self.refresh_callback = refresh_callback

        self.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(self, text="Title:").grid(row=0, column=0, padx=10, pady=10, sticky="e")
        self.title_entry = ctk.CTkEntry(self)
        self.title_entry.insert(0, title)
        self.title_entry.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        ctk.CTkLabel(self, text="Type:").grid(row=1, column=0, padx=10, pady=10, sticky="e")
        self.type_option = ctk.CTkOptionMenu(self, values=["incoming", "outgoing", "others"])
        self.type_option.set(doc_type)
        self.type_option.grid(row=1, column=1, padx=10, pady=10, sticky="w")

        ctk.CTkLabel(self, text="Class:").grid(row=2, column=0, padx=10, pady=10, sticky="e")
        self.class_option = ctk.CTkOptionMenu(self, values=["advisory", "circular", "endorsement", "executive order", "memorandum", "office order", "ordinance", "policy", "resolution", "others"])
        self.class_option.set(doc_class)
        self.class_option.grid(row=2, column=1, padx=10, pady=10, sticky="w")

        # 📅 Date Entry
        ctk.CTkLabel(self, text="Date:").grid(row=3, column=0, sticky="e", pady=10, padx=10)
        self.date_entry = ctk.CTkEntry(self)
        self.date_entry.insert(0, date or "")
        self.date_entry.grid(row=3, column=1, pady=10, padx=10, sticky="ew")

        ctk.CTkLabel(self, text="Sender:").grid(row=4, column=0, padx=10, pady=10, sticky="e")
        self.sender_entry = ctk.CTkEntry(self)
        self.sender_entry.insert(0, sender or "")
        self.sender_entry.grid(row=4, column=1, padx=10, pady=10, sticky="ew")

        ctk.CTkLabel(self, text="Recipient:").grid(row=5, column=0, padx=10, pady=10, sticky="e")
        self.recipient_entry = ctk.CTkEntry(self)
        self.recipient_entry.insert(0, recipient or "")
        self.recipient_entry.grid(row=5, column=1, padx=10, pady=10, sticky="ew")

        ctk.CTkLabel(self, text="Description:").grid(row=6, column=0, padx=10, pady=10, sticky="ne")
        self.desc_entry = ctk.CTkTextbox(self, height=100)
        self.desc_entry.insert("1.0", description or "")
        self.desc_entry.grid(row=6, column=1, padx=10, pady=10, sticky="ew")

        self.save_btn = ctk.CTkButton(self, text="💾 Save Changes", command=self.save_changes)
        self.save_btn.grid(row=7, column=0, columnspan=2, pady=20)

        self.saving = False
    def save_changes(self):
        updated_data = {
            "title": self.title_entry.get().strip(),
            "doc_type": self.type_option.get(),
            "doc_class": self.class_option.get(),
            "date": self.date_entry.get().strip() or None,
            "sender": self.sender_entry.get().strip() or None,
            "recipient": self.recipient_entry.get().strip() or None,
            "description": self.desc_entry.get("1.0", "end").strip() or None
        }
        old_type = self.type_option.get()
        new_type = updated_data["doc_type"]
        type_changed = self.original_type != updated_data["doc_type"]

        if self.saving:
            return
        self.saving = True
        self.disable_widgets([
            self.title_entry, self.type_option, self.date_entry,
            self.sender_entry, self.recipient_entry, self.desc_entry, self.save_btn
        ])
        self.save_btn.configure(text="Saving...")

        # Validate inputs
        if type_changed:
            old_abs_path = os.path.join(BASE_DIR, self.original_path)
            filename = os.path.basename(old_abs_path)
            new_folder = os.path.join(DOCS_DIR, updated_data["doc_type"])
            os.makedirs(new_folder, exist_ok=True)
            new_abs_path = os.path.join(new_folder, filename)

            try:
                os.rename(old_abs_path, new_abs_path)
                # Update the relative path for DB
                updated_data["file_path"] = os.path.relpath(new_abs_path, BASE_DIR)
            except Exception as move_err:
                ToastManager.show_error(self, f"Failed to move file: {move_err}")
                self.saving = False
                self.enable_widgets([...])
                self.save_btn.configure(state="normal", text="💾 Save Changes")
                return
        else:
            updated_data["file_path"] = self.original_path

        # Collect data and update DB
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE documents
                SET title = ?, doc_type = ?, doc_class = ?, date = ?, sender = ?, recipient = ?, description = ?, file_path = ?
                WHERE id = ?
            ''', (
                updated_data["title"],
                updated_data["doc_type"],
                updated_data["doc_class"],
                updated_data["date"],
                updated_data["sender"],
                updated_data["recipient"],
                updated_data["description"],
                updated_data["file_path"],
                self.doc_id
            ))
            conn.commit()
            conn.close()
            ToastManager.show_success(self, "Document updated successfully!")
            self.refresh_callback()
            self.after(1000, self.destroy)
        except sqlite3.Error as e:
            self.saving = False
            self.enable_widgets([
                self.title_entry, self.type_option, self.date_picker,
                self.sender_entry, self.recipient_entry, self.desc_entry, self.save_btn
            ])
            self.save_btn.configure(state="normal", text="💾 Save Changes")
            ToastManager.show_error(self, f"Database error: {str(e)}")

