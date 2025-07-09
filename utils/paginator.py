# utils/paginator.py

import customtkinter as ctk

class Paginator:
    def __init__(self, master, on_page_change, total_count_fn, page_sizes=[10, 25, 50]):
        self.master = master
        self.on_page_change = on_page_change
        self.total_count_fn = total_count_fn
        self.page_sizes = page_sizes

        self.current_page = 1
        self.page_size = page_sizes[0]

        self.total_items = 0
        self.total_pages = 1

        self._build_ui()

    def _build_ui(self):
        self.frame = ctk.CTkFrame(self.master, fg_color="transparent")
        self.frame.pack(pady=(0, 10))

        self.prev_btn = ctk.CTkButton(self.frame, text="⬅️ Previous", command=self.prev_page)
        self.prev_btn.grid(row=0, column=0, padx=5)

        self.page_label = ctk.CTkLabel(self.frame, text="Page 1")
        self.page_label.grid(row=0, column=1, padx=5)

        self.next_btn = ctk.CTkButton(self.frame, text="Next ➡️", command=self.next_page)
        self.next_btn.grid(row=0, column=2, padx=5)

        self.size_menu = ctk.CTkOptionMenu(
            self.frame,
            values=[str(size) for size in self.page_sizes],
            command=self.change_page_size
        )
        self.size_menu.set(str(self.page_size))
        self.size_menu.grid(row=0, column=3, padx=10)

        self.count_label = ctk.CTkLabel(self.frame, text="")
        self.count_label.grid(row=0, column=4, padx=5)

    def update(self):
        self.total_items = self.total_count_fn()
        self.total_pages = max(1, (self.total_items + self.page_size - 1) // self.page_size)

        self.page_label.configure(text=f"Page {self.current_page} of {self.total_pages}")
        self.count_label.configure(text=f"{self.total_items} documents")

        self.prev_btn.configure(state="normal" if self.current_page > 1 else "disabled")
        self.next_btn.configure(state="normal" if self.current_page < self.total_pages else "disabled")

    def next_page(self):
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.on_page_change()

    def prev_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            self.on_page_change()

    def change_page_size(self, value):
        self.page_size = int(value)
        self.current_page = 1
        self.on_page_change()

    def get_offset_limit(self):
        offset = (self.current_page - 1) * self.page_size
        return offset, self.page_size
