# frontend/gui.py
"""Library application GUI — Tkinter-based client for the Library API."""
import tkinter as tk
from tkinter import ttk, messagebox
import requests
import re

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
        """Load items from backend with better error handling."""
        cat = self.cat_var.get().strip()
        params = {}
        if cat:
            params["category"] = cat
        try:
            r = requests.get(f"{BASE}/media", params=params, timeout=10)
            r.raise_for_status()
            self.items = r.json()
        except requests.exceptions.ConnectionError:
            messagebox.showerror("Connection Error", "Cannot connect to backend server.\nMake sure the backend is running on http://127.0.0.1:5000")
            self.items = []
        except requests.exceptions.Timeout:
            messagebox.showerror("Timeout", "Backend server is not responding.")
            self.items = []
        except Exception as e:
            messagebox.showerror("Error", f"Could not load items:\n{str(e)}")
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
        # Hide internal `id` field from the details view for a cleaner UI.
        lines = []
        for k, v in item.items():
            if k == "id":
                continue
            lines.append(f"{k}: {v}")
        txt = "\n".join(lines)
        self.details_text.delete("1.0", tk.END)
        self.details_text.insert(tk.END, txt)

    def search(self):
        """Search for items by exact name."""
        name = self.search_var.get().strip()
        if not name:
            messagebox.showinfo("Search", "Enter a name to search (exact match).")
            return
        try:
            r = requests.get(f"{BASE}/media/search", params={"name": name}, timeout=10)
            r.raise_for_status()
            self.items = r.json()
            self.refresh_listbox()
            if not self.items:
                messagebox.showinfo("Search Result", f"No items found matching '{name}'.")
        except requests.exceptions.ConnectionError:
            messagebox.showerror("Connection Error", "Cannot connect to backend server.")
        except Exception as e:
            messagebox.showerror("Search Error", f"Search failed:\n{str(e)}")

    def create_item(self):
        """Open a modal dialog to create a new item with validation."""
        dlg = tk.Toplevel(self)
        dlg.title("Create Item")
        dlg.transient(self)
        dlg.grab_set()
        dlg.resizable(False, False)

        name_var = tk.StringVar()
        pub_var = tk.StringVar()
        author_var = tk.StringVar()
        category_var = tk.StringVar(value="Book")  # Default selection

        frm = ttk.Frame(dlg, padding=12)
        frm.grid(row=0, column=0, sticky="nsew")

        ttk.Label(frm, text="Name:").grid(row=0, column=0, sticky="w")
        ttk.Entry(frm, textvariable=name_var, width=40).grid(row=0, column=1, pady=4)

        ttk.Label(frm, text="Publication date (YYYY-MM-DD):").grid(row=1, column=0, sticky="w")
        ttk.Entry(frm, textvariable=pub_var, width=40).grid(row=1, column=1, pady=4)

        ttk.Label(frm, text="Author:").grid(row=2, column=0, sticky="w")
        ttk.Entry(frm, textvariable=author_var, width=40).grid(row=2, column=1, pady=4)

        ttk.Label(frm, text="Category:").grid(row=3, column=0, sticky="w")
        cat_combo = ttk.Combobox(frm, textvariable=category_var, values=["Book", "Film", "Magazine"], width=38, state="readonly")
        cat_combo.grid(row=3, column=1, pady=4)

        btn_frame = ttk.Frame(frm)
        btn_frame.grid(row=4, column=0, columnspan=2, pady=(12,0))

        def on_ok():
            name = name_var.get().strip()
            pub = pub_var.get().strip()
            author = author_var.get().strip()
            category = category_var.get().strip()
            
            # Validation
            if not name:
                messagebox.showwarning("Validation Error", "Name is required.", parent=dlg)
                return
            if not pub:
                messagebox.showwarning("Validation Error", "Publication date is required.", parent=dlg)
                return
            if not author:
                messagebox.showwarning("Validation Error", "Author is required.", parent=dlg)
                return
            if not category:
                messagebox.showwarning("Validation Error", "Category is required.", parent=dlg)
                return
            
            # Validate date format
            if not re.match(r'^\d{4}-\d{2}-\d{2}$', pub):
                messagebox.showwarning("Validation Error", "Date must be in YYYY-MM-DD format.", parent=dlg)
                return
            
            dlg.result = {
                "name": name,
                "publication_date": pub,
                "author": author,
                "category": category
            }
            dlg.destroy()

        def on_cancel():
            dlg.result = None
            dlg.destroy()

        ttk.Button(btn_frame, text="OK", command=on_ok).pack(side="left", padx=6)
        ttk.Button(btn_frame, text="Cancel", command=on_cancel).pack(side="left")

        # Center the dialog over the main window
        self.update_idletasks()
        dlg.update_idletasks()
        x = self.winfo_rootx() + (self.winfo_width() // 2) - (dlg.winfo_reqwidth() // 2)
        y = self.winfo_rooty() + (self.winfo_height() // 2) - (dlg.winfo_reqheight() // 2)
        dlg.geometry(f"+{x}+{y}")

        dlg.result = None
        self.wait_window(dlg)

        if not getattr(dlg, 'result', None):
            return

        payload = dlg.result

        try:
            r = requests.post(f"{BASE}/media", json=payload, timeout=10)
            r.raise_for_status()
            messagebox.showinfo("Success", f"Item '{payload['name']}' created successfully!")
            self.load_list()
        except requests.exceptions.ConnectionError:
            messagebox.showerror("Error", "Cannot connect to backend server.")
        except Exception as e:
            # Try to parse error from server
            try:
                error_detail = r.json().get('error', str(e))
            except:
                error_detail = str(e)
            messagebox.showerror("Creation Failed", f"{error_detail}")

    def delete_selected(self):
        """Delete the selected item with confirmation."""
        sel = self.listbox.curselection()
        if not sel:
            messagebox.showwarning("No Selection", "Please select an item to delete.")
            return
        idx = sel[0]
        item = self.items[idx]
        item_id = item.get("id")
        item_name = item.get("name", "Unknown")

        # Confirmation dialog
        if not messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete '{item_name}'?"):
            return

        try:
            r = requests.delete(f"{BASE}/media/{item_id}", timeout=10)
            if r.status_code == 200:
                messagebox.showinfo("Success", f"Item '{item_name}' deleted successfully.")
                self.load_list()
            else:
                try:
                    error_detail = r.json().get('error', f"Status {r.status_code}")
                except:
                    error_detail = f"Status {r.status_code}"
                messagebox.showerror("Delete Failed", error_detail)
        except requests.exceptions.ConnectionError:
            messagebox.showerror("Error", "Cannot connect to backend server.")
        except Exception as e:
            messagebox.showerror("Delete Error", f"Failed to delete item:\n{str(e)}")

if __name__ == "__main__":
    import traceback, sys, os
    try:
        app = App()
        app.mainloop()
    except Exception:
        # Write traceback to a log file for diagnostics so double-click launches
        log_path = os.path.join(os.path.dirname(__file__), 'gui_error.log')
        with open(log_path, 'w', encoding='utf-8') as f:
            traceback.print_exc(file=f)
        # Also print to stderr
        traceback.print_exc()
        # Show a messagebox if tkinter is available
        try:
            messagebox.showerror('Startup Error', f'An error occurred. See {log_path}')
        except Exception:
            pass
        sys.exit(1)
