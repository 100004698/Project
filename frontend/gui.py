# frontend/gui.py
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import requests

BASE = "http://127.0.0.1:5000"

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Library App")
        self.geometry("800x400")

        # Top controls
        top = ttk.Frame(self)
        top.pack(fill="x", padx=8, pady=6)

        ttk.Label(top, text="Category:").pack(side="left")
        self.cat_var = tk.StringVar()
        cat_combo = ttk.Combobox(top, textvariable=self.cat_var, values=["", "Book", "Film", "Magazine"], width=12)
        cat_combo.pack(side="left", padx=6)
        ttk.Button(top, text="Filter", command=self.load_list).pack(side="left")

        ttk.Label(top, text="Search (exact name):").pack(side="left", padx=(12,0))
        self.search_var = tk.StringVar()
        ttk.Entry(top, textvariable=self.search_var, width=20).pack(side="left", padx=6)
        ttk.Button(top, text="Search", command=self.search).pack(side="left")

        ttk.Button(top, text="Create", command=self.create_item).pack(side="right")
        ttk.Button(top, text="Delete", command=self.delete_selected).pack(side="right", padx=6)

        # Main panes
        main = ttk.Frame(self)
        main.pack(fill="both", expand=True, padx=8, pady=6)

        # Left: list
        left = ttk.Frame(main)
        left.pack(side="left", fill="both", expand=True)
        self.listbox = tk.Listbox(left)
        self.listbox.pack(fill="both", expand=True)
        self.listbox.bind("<<ListboxSelect>>", self.show_details)

        # Right: details
        right = ttk.Frame(main, width=300)
        right.pack(side="right", fill="y")
        ttk.Label(right, text="Details:", font=("TkDefaultFont", 12, "bold")).pack(anchor="nw")
        self.details_text = tk.Text(right, width=40, height=20)
        self.details_text.pack(fill="y", expand=True)

        self.items = []  # holds current items loaded from backend
        self.load_list()

    def load_list(self):
        cat = self.cat_var.get().strip()
        params = {}
        if cat:
            params["category"] = cat
        try:
            r = requests.get(f"{BASE}/media", params=params, timeout=3)
            r.raise_for_status()
            self.items = r.json()
        except Exception as e:
            messagebox.showerror("Error", f"Could not load items:\n{e}")
            self.items = []
        self.refresh_listbox()

    def refresh_listbox(self):
        self.listbox.delete(0, tk.END)
        for it in self.items:
            display = f"{it.get('name')} ({it.get('category')})"
            self.listbox.insert(tk.END, display)
        self.details_text.delete("1.0", tk.END)

    def show_details(self, event=None):
        sel = self.listbox.curselection()
        if not sel:
            return
        idx = sel[0]
        item = self.items[idx]
        txt = "\n".join([f"{k}: {v}" for k, v in item.items()])
        self.details_text.delete("1.0", tk.END)
        self.details_text.insert(tk.END, txt)

    def search(self):
        name = self.search_var.get().strip()
        if not name:
            messagebox.showinfo("Info", "Enter a name to search (exact match).")
            return
        try:
            r = requests.get(f"{BASE}/media/search", params={"name": name}, timeout=3)
            r.raise_for_status()
            self.items = r.json()
            self.refresh_listbox()
            if not self.items:
                messagebox.showinfo("Search", "No exact match found.")
        except Exception as e:
            messagebox.showerror("Error", f"Search failed:\n{e}")

    def create_item(self):
        name = simpledialog.askstring("Create", "Name:")
        if not name: return
        pub = simpledialog.askstring("Create", "Publication date (YYYY-MM-DD):")
        if not pub: return
        author = simpledialog.askstring("Create", "Author:")
        if not author: return
        category = simpledialog.askstring("Create", "Category (Book/Film/Magazine):")
        if not category: return
        
        payload = {
            "name": name,
            "publication_date": pub,
            "author": author,
            "category": category
        }

        try:
            r = requests.post(f"{BASE}/media", json=payload, timeout=3)
            r.raise_for_status()
            messagebox.showinfo("Created", "Item created successfully.")
            self.load_list()
        except Exception as e:
            messagebox.showerror("Error", f"Create failed:\n{e}")

    def delete_selected(self):
        sel = self.listbox.curselection()
        if not sel:
            messagebox.showinfo("Info", "Select an item to delete.")
            return
        idx = sel[0]
        item = self.items[idx]
        item_id = item.get("id")

        if not messagebox.askyesno("Confirm", f"Delete '{item.get('name')}'?"):
            return

        try:
            r = requests.delete(f"{BASE}/media/{item_id}", timeout=3)
            if r.status_code == 200:
                messagebox.showinfo("Deleted", "Item deleted.")
                self.load_list()
            else:
                messagebox.showerror("Error", f"Delete failed: {r.status_code}")
        except Exception as e:
            messagebox.showerror("Error", f"Delete failed:\n{e}")

if __name__ == "__main__":
    app = App()
    app.mainloop()
