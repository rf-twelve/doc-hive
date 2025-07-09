# utils/gui_dashboard.py

from PIL import Image
import json
import os
import sqlite3
import webbrowser
import subprocess
import customtkinter as ctk
import tkinter as tk
import time

from toast_manager import ToastManager
# 🔁 Import Edit Document Popup
from gui_edit_document import EditDocumentPopup

# 🔁 Import Paginator for pagination controls
from paginator import Paginator

# from CTkMessagebox import CTkMessagebox
from tkinter import messagebox

# 🔁 Import DB initializer
from db_init import init_db

# 🔐 Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "db", "document_store.db")
DOCS_DIR = os.path.join(BASE_DIR, "documents")
ADD_DOC_SCRIPT = os.path.join(BASE_DIR, "utils", "gui_add_document.py")
SETTINGS_PATH = os.path.join(BASE_DIR, "settings.json")


def load_settings():
    if os.path.exists(SETTINGS_PATH):
        try:
            with open(SETTINGS_PATH, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            print("⚠️ settings.json is invalid. Resetting to defaults.")
            default = {"theme": "System"}
            save_settings(default)
            return default
    return {"theme": "System"}


def save_settings(settings):
    with open(SETTINGS_PATH, "w") as f:
        json.dump(settings, f, indent=4)

# ✅ Initialize DB on startup
init_db()

ctk.set_appearance_mode("Dark")  # Options: "System" (default), "Light", "Dark")
ctk.set_default_color_theme("blue")

class DocumentDashboard(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("LGU Kalibo - Document Dashboard")
        self.geometry("800x700")
        icon_path = os.path.join(BASE_DIR, "assets", "icon.ico")
        self.iconbitmap(icon_path)


        self.settings = load_settings()
        ctk.set_appearance_mode(self.settings.get("theme", "System"))

        # Create a native menu bar
        menu_bar = tk.Menu(self)
        # File Menu
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="New Document", command=self.open_add_document)
        file_menu.add_command(label="Exit", command=self.quit)
        menu_bar.add_cascade(label="File", menu=file_menu)

        # Edit Menu
        edit_menu = tk.Menu(menu_bar, tearoff=0)
        edit_menu.add_command(label="Refresh", command=self.reset_filters)
        menu_bar.add_cascade(label="Edit", menu=edit_menu)

        # Settings Menu
        settings_menu = tk.Menu(menu_bar, tearoff=0)
        settings_menu.add_command(label="Theme Preferences", command=self.open_settings)
        menu_bar.add_cascade(label="Settings", menu=settings_menu)

        # Help Menu
        help_menu = tk.Menu(menu_bar, tearoff=0)
        help_menu.add_command(label="About", command=self.show_about)
        menu_bar.add_cascade(label="Help", menu=help_menu)

        # Attach the menu to the window
        self.configure(menu=menu_bar)

        # 🔍 Search + Filter Row
        top_frame = ctk.CTkFrame(self,fg_color="transparent")
        top_frame.pack(pady=10, padx=20, fill="x")

        # Configure grid for better layout
        self.current_page = 1
        self.docs_per_page = 10

        self.search_entry = ctk.CTkEntry(top_frame, placeholder_text="Search by title, sender, or recipient...")
        self.search_entry.pack(side="left", padx=(0, 10), fill="x", expand=True)

        self.type_filter = ctk.CTkOptionMenu(top_frame, values=["All", "incoming", "outgoing", "others"])
        self.type_filter.set("All")
        self.type_filter.pack(side="left", padx=(0, 10))

        self.class_filter = ctk.CTkOptionMenu(top_frame, values=["All", "advisory", "circular", "endorsement", "executive order", "memorandum", "office order", "ordinance", "policy", "resolution", "others"])
        self.class_filter.set("All")
        self.class_filter.pack(side="left", padx=(0, 10))

        search_btn = ctk.CTkButton(top_frame, text="🔍 Search", command=self.load_documents)
        search_btn.pack(side="left")

        # 📋 Scrollable Document List
        self.scroll_frame = ctk.CTkScrollableFrame(self, width=750, height=500)
        self.scroll_frame.pack(pady=10, padx=20, fill="both", expand=True)

        # 🔄 Pagination Controls
        self.paginator = Paginator(
            master=self,
            on_page_change=self.load_documents,
            total_count_fn=self.get_total_document_count
        )

        # 👤 Developer Signature
        footer = ctk.CTkLabel(
            self,
            text="Developed by Rosel Francisco",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        footer.pack(side="bottom", pady=2)

        self.load_documents()

    def open_settings(self):
        settings_win = ctk.CTkToplevel(self)
        settings_win.title("Settings")
        settings_win.geometry("300x200")
        settings_win.transient(self)
        settings_win.grab_set()
        settings_win.focus()

        ctk.CTkLabel(settings_win, text="Choose Theme:", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(20, 10))

        theme_var = tk.StringVar(value=ctk.get_appearance_mode())

        def apply_theme():
            selected = theme_var.get()
            ctk.set_appearance_mode(selected)
            self.settings["theme"] = selected
            save_settings(self.settings)
            ToastManager.show_info(self, f"Theme set to {selected}")
            settings_win.destroy()  # ✅ Close the modal to prevent focus issues

        for theme in ["Light", "Dark", "System"]:
            ctk.CTkRadioButton(
                settings_win,
                text=theme,
                variable=theme_var,
                value=theme,
                command=apply_theme
            ).pack(anchor="w", padx=40, pady=5)

    def show_about(self):
        about = ctk.CTkToplevel(self)
        about.title("About LGU Kalibo - DMS")
        about.geometry("300x180")
        about.transient(self)
        about.grab_set()
        about.focus()

        # 📷 Load and show logo
        logo_path = os.path.join(BASE_DIR, "assets", "icon.png")
        if os.path.exists(logo_path):
            image = Image.open(logo_path)
            image = image.resize((30, 30), Image.LANCZOS)
            logo = ctk.CTkImage(light_image=image, dark_image=image, size=(30, 30))
            ctk.CTkLabel(about, image=logo, text="").pack(pady=(15, 5))
        # 📝 Text content
        ctk.CTkLabel(about, text="Document Management System").pack()
        ctk.CTkLabel(about, text="Code & Developed by Rosel Francisco", text_color="#2e8b57").pack(pady=(10, 5))
        ctk.CTkLabel(about, text="© 2025").pack()

    def reset_filters(self):
        self.search_entry.delete(0, 'end')
        self.type_filter.set("All")
        self.load_documents()

    def open_add_document(self):
        subprocess.Popen(["python", ADD_DOC_SCRIPT], shell=True)

    def get_total_document_count(self):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        query = "SELECT COUNT(*) FROM documents"
        params = []

        filters = []
        doc_type = self.type_filter.get()
        doc_class = self.class_filter.get()
        search_term = self.search_entry.get().strip().lower()

        if doc_type != "All":
            filters.append("doc_type = ?")
            params.append(doc_type)
        if doc_class != "All":
            filters.append("doc_class = ?")
            params.append(doc_class)
        if search_term:
            filters.append("(LOWER(title) LIKE ? OR LOWER(sender) LIKE ? OR LOWER(recipient) LIKE ?)")
            params.extend([f"%{search_term}%"] * 3)

        if filters:
            query += " WHERE " + " AND ".join(filters)

        cursor.execute(query, params)
        count = cursor.fetchone()[0]
        conn.close()
        return count

    def load_documents(self):
        search_term = self.search_entry.get().strip().lower()
        selected_type = self.type_filter.get().lower()
        selected_class = self.class_filter.get().lower()

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        query = "SELECT id, title, doc_type, doc_class, date, sender, recipient, description, file_path FROM documents WHERE 1=1"
        params = []

        # Filter by doc_type
        if selected_type != "all":
            query += " AND doc_type = ?"
            params.append(selected_type)

        # Filter by doc_class
        if selected_class != "all":
            query += " AND doc_class = ?"
            params.append(selected_class)

        # Filter by search keyword
        if search_term:
            query += " AND (title LIKE ? OR sender LIKE ? OR recipient LIKE ?)"
            params.extend([f"%{search_term}%"] * 3)

        query += " ORDER BY date DESC"
        cursor.execute(query, params)

        rows = cursor.fetchall()
        conn.close()

        # Clear previous cards
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        # Render cards
        if not rows:
            ctk.CTkLabel(self.scroll_frame, text="No documents found.").pack(pady=20)
        else:
            for doc in rows:
                self.create_card(doc)

        # ✅ Update paginator display
        self.paginator.update()

    def create_card(self, doc):
        doc_id, title, doc_type,doc_class, date, sender, recipient, description, file_path = doc

        # 🎨 Color by type
        color_map = {
            "incoming": "#1f6aa5",  # Blue
            "outgoing": "#2e8b57",  # Green
            "others": "#d2691e"  # Orange
        }
        card_color = color_map.get(doc_type.lower(), "#444444")

        def truncate_title(text, max_chars=50):
            return text if len(text) <= max_chars else text[:max_chars] + "…"

        def truncate(text, max_chars=65):
            return text if len(text) <= max_chars else text[:max_chars] + "…"


        card = ctk.CTkFrame(self.scroll_frame, corner_radius=10, fg_color=card_color)
        card.pack(pady=10, padx=10, fill="x")

        # Configure grid
        card.grid_columnconfigure(0, weight=1)
        card.grid_columnconfigure(1, weight=0)

        # 🧾 Left Column: Metadata
        title_label = ctk.CTkLabel(card, text=f"📌 {truncate_title(title)}", font=ctk.CTkFont(size=18, weight="bold"),
                                   text_color="white")
        title_label.grid(row=0, column=0, sticky="w", padx=10, pady=(10, 0))

        meta = f"📜 {doc_type.upper()}  |  {doc_class.upper()}   📅 {date}   FROM: {sender.upper() or 'N/A'} TO: {recipient.upper() or 'N/A'}"
        meta_label = ctk.CTkLabel(card, text=meta, text_color="white")
        meta_label.grid(row=1, column=0, sticky="w", padx=10)

        # sender_info = f"🪪 {sender or 'N/A'} → {recipient or 'N/A'}"
        # sender_label = ctk.CTkLabel(card, text=sender_info, text_color="white")
        # sender_label.grid(row=2, column=0, sticky="w", padx=10)

        if description:
            desc_label = ctk.CTkLabel(card, text=truncate(description),font=ctk.CTkFont(size=16, weight="bold"), text_color="white")
            desc_label.grid(row=3, column=0, sticky="w", padx=10, pady=(0, 10))

        # 🧰 Right Column: Buttons
        def open_file():
            abs_path = os.path.join(BASE_DIR, file_path)
            if os.path.exists(abs_path):
                webbrowser.open(abs_path)
            else:
                ToastManager.show_warning(self, "The file could not be found.")

        def delete_doc():
            confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this document?")
            if not confirm:
                return

            try:
                with sqlite3.connect(DB_PATH) as conn:
                    cursor = conn.cursor()

                    # ✅ Step 1: Get the file path before deleting
                    cursor.execute("SELECT file_path FROM documents WHERE id = ?", (doc_id,))
                    result = cursor.fetchone()
                    if result:
                        file_path = os.path.join(BASE_DIR, result[0])
                        if os.path.exists(file_path):
                            try:
                                os.remove(file_path)  # ✅ Step 2: Delete the file
                            except Exception as file_err:
                                ToastManager.show_warning(self, f"⚠️ File not deleted: {file_err}")

                    # ✅ Step 3: Delete the record from the database
                    cursor.execute("DELETE FROM documents WHERE id = ?", (doc_id,))
                    conn.commit()

                self.load_documents()
                ToastManager.show_success(self, "🗑️ Document deleted successfully!")

            except sqlite3.OperationalError as db_err:
                ToastManager.show_error(self, f"Database error: {db_err}")

        def edit_doc():
            EditDocumentPopup(self, doc, self.load_documents)

        btn_frame = ctk.CTkFrame(card, fg_color="transparent")
        btn_frame.grid(row=0, column=1, rowspan=4, padx=10, pady=10, sticky="ne")

        ctk.CTkButton(btn_frame, text="🗃 Open", command=open_file, width=80, fg_color="transparent", border_color="white", border_width=2).grid(row=0, column=0, pady=2)
        ctk.CTkButton(btn_frame, text="✍ Edit", command=edit_doc, width=80, fg_color="transparent", border_color="white", border_width=2).grid(row=1, column=0, pady=2)
        ctk.CTkButton(btn_frame, text="♻ Delete", command=delete_doc, width=80, fg_color="transparent", border_color="white", border_width=2, hover_color="#A52A2A").grid(row=2, column=0, pady=2)




if __name__ == "__main__":
    app = DocumentDashboard()
    app.mainloop()