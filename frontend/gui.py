# frontend/gui.py
"""Library application GUI — Tkinter-based client for the Library API."""
import tkinter as tk
from tkinter import ttk, messagebox
import requests
import re

BASE = "http://127.0.0.1:5000"

# Color scheme
COLORS = {
    "primary": "#2C3E50",      # Dark blue-gray
    "secondary": "#3498DB",    # Bright blue
    "accent": "#E74C3C",       # Red/coral
    "success": "#27AE60",      # Green
    "bg": "#ECF0F1",           # Light gray
    "fg": "#2C3E50",           # Dark text
    "white": "#FFFFFF",
    "dark": "#34495E",
}

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Library App")
        self.geometry("1000x600")
        self.configure(bg=COLORS["bg"])
        
        # Configure styles
        self.setup_styles()

        # Header
        self.create_header()

        # Top controls
        self.create_top_controls()

        # Main panes
        self.create_main_content()

        self.items = []  # holds current items loaded from backend
        self.load_list()

    def setup_styles(self):
        """Configure ttk styles for the application."""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure button style
        style.configure('TButton',
                       font=('Segoe UI', 10),
                       padding=8)
        style.map('TButton',
                 background=[('active', COLORS["secondary"])])
        
        # Configure label style
        style.configure('TLabel',
                       background=COLORS["bg"],
                       foreground=COLORS["fg"],
                       font=('Segoe UI', 10))
        
        # Configure frame style
        style.configure('TFrame',
                       background=COLORS["bg"])
        
        # Configure combobox
        style.configure('TCombobox',
                       font=('Segoe UI', 10))
        
        # Header label style
        style.configure('Header.TLabel',
                       background=COLORS["primary"],
                       foreground=COLORS["white"],
                       font=('Segoe UI', 16, 'bold'),
                       padding=15)
        
        # Section title style
        style.configure('Title.TLabel',
                       background=COLORS["bg"],
                       foreground=COLORS["primary"],
                       font=('Segoe UI', 12, 'bold'))

    def create_header(self):
        """Create a header section."""
        header = tk.Frame(self, bg=COLORS["primary"], height=70)
        header.pack(fill="x", padx=0, pady=0)
        header.pack_propagate(False)
        
        title = tk.Label(header, text="📚 Library Manager", 
                        bg=COLORS["primary"], 
                        fg=COLORS["white"],
                        font=('Segoe UI', 18, 'bold'),
                        pady=10)
        title.pack(side="left", padx=20)
        
        subtitle = tk.Label(header, text="Organize your media collection",
                           bg=COLORS["primary"],
                           fg="#BDC3C7",
                           font=('Segoe UI', 10))
        subtitle.pack(side="left", padx=20)

    def create_top_controls(self):
        """Create the top control panel."""
        top = ttk.Frame(self)
        top.pack(fill="x", padx=15, pady=15)

        # Left section - Filter
        left_frame = ttk.Frame(top)
        left_frame.pack(side="left", fill="x", expand=True)
        
        ttk.Label(left_frame, text="Filter by Category:", style='Title.TLabel').pack(side="left", padx=(0, 8))
        self.cat_var = tk.StringVar()
        cat_combo = ttk.Combobox(left_frame, textvariable=self.cat_var, 
                                 values=["", "Book", "Film", "Magazine"], 
                                 width=12, state="readonly")
        cat_combo.pack(side="left", padx=4)
        
        filter_btn = ttk.Button(left_frame, text="🔍 Filter", command=self.load_list)
        filter_btn.pack(side="left", padx=4)

        # Middle section - Search
        middle_frame = ttk.Frame(top)
        middle_frame.pack(side="left", fill="x", expand=True, padx=(20, 0))
        
        ttk.Label(middle_frame, text="Search:", style='Title.TLabel').pack(side="left", padx=(0, 8))
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(middle_frame, textvariable=self.search_var, width=25)
        search_entry.pack(side="left", padx=4)
        
        search_btn = ttk.Button(middle_frame, text="🔎 Find", command=self.search)
        search_btn.pack(side="left", padx=4)

        # Right section - Actions
        right_frame = ttk.Frame(top)
        right_frame.pack(side="right")
        
        create_btn = ttk.Button(right_frame, text="✨ Create", command=self.create_item)
        create_btn.pack(side="left", padx=4)
        
        delete_btn = ttk.Button(right_frame, text="🗑️ Delete", command=self.delete_selected)
        delete_btn.pack(side="left", padx=4)

    def create_main_content(self):
        """Create the main content area with list and details."""
        main = ttk.Frame(self)
        main.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        # Left: list
        left = ttk.Frame(main)
        left.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        list_title = ttk.Label(left, text="📖 Items", style='Title.TLabel')
        list_title.pack(anchor="nw", pady=(0, 8))
        
        self.listbox = tk.Listbox(left, 
                                 bg=COLORS["white"],
                                 fg=COLORS["fg"],
                                 font=('Segoe UI', 10),
                                 highlightcolor=COLORS["secondary"],
                                 selectmode=tk.SINGLE,
                                 relief="solid",
                                 borderwidth=1,
                                 activestyle="none")
        self.listbox.pack(fill="both", expand=True)
        self.listbox.bind("<<ListboxSelect>>", self.show_details)
        
        # Scrollbar for listbox
        scrollbar = ttk.Scrollbar(left, orient="vertical", command=self.listbox.yview)
        scrollbar.pack(side="right", fill="y")
        self.listbox.config(yscrollcommand=scrollbar.set)

        # Right: details
        right = ttk.Frame(main, width=320)
        right.pack(side="right", fill="y", padx=(10, 0))
        right.pack_propagate(False)
        
        details_title = ttk.Label(right, text="ℹ️ Details", style='Title.TLabel')
        details_title.pack(anchor="nw", pady=(0, 8))
        
        # Details frame with border effect
        details_frame = tk.Frame(right, bg=COLORS["white"], relief="solid", borderwidth=1)
        details_frame.pack(fill="y", expand=True)
        
        self.details_text = tk.Text(details_frame,
                                   width=45,
                                   height=25,
                                   bg=COLORS["white"],
                                   fg=COLORS["fg"],
                                   font=('Segoe UI', 10),
                                   relief="flat",
                                   padx=10,
                                   pady=10,
                                   wrap="word",
                                   state="normal")
        self.details_text.pack(fill="y", expand=True)

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
            else:
                messagebox.showinfo("Search Result", f"Found {len(self.items)} item(s) matching '{name}'.")
        except requests.exceptions.ConnectionError:
            messagebox.showerror("Connection Error", "Cannot connect to backend server.")
        except Exception as e:
            messagebox.showerror("Search Error", f"Search failed:\n{str(e)}")

    def create_item(self):
        """Open a modal dialog to create a new item with validation."""
        dlg = tk.Toplevel(self)
        dlg.title("Create New Item")
        dlg.transient(self)
        dlg.grab_set()
        dlg.resizable(False, False)
        dlg.configure(bg=COLORS["bg"])
        
        # Configure dialog style
        dlg_style = ttk.Style()
        dlg_style.configure('Dialog.TLabel',
                          background=COLORS["bg"],
                          foreground=COLORS["fg"],
                          font=('Segoe UI', 10))
        dlg_style.configure('Dialog.TFrame',
                          background=COLORS["bg"])

        name_var = tk.StringVar()
        pub_var = tk.StringVar()
        author_var = tk.StringVar()
        category_var = tk.StringVar(value="Book")

        frm = ttk.Frame(dlg, padding=20)
        frm.grid(row=0, column=0, sticky="nsew")

        # Title
        title_lbl = tk.Label(frm, text="✨ Create New Item",
                            bg=COLORS["bg"],
                            fg=COLORS["primary"],
                            font=('Segoe UI', 14, 'bold'))
        title_lbl.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 20))

        # Name
        ttk.Label(frm, text="Name:", style='Dialog.TLabel').grid(row=1, column=0, sticky="w", pady=8)
        name_entry = ttk.Entry(frm, textvariable=name_var, width=40, font=('Segoe UI', 10))
        name_entry.grid(row=1, column=1, pady=8, padx=(10, 0))
        name_entry.focus()

        # Publication date
        ttk.Label(frm, text="Publication Date:", style='Dialog.TLabel').grid(row=2, column=0, sticky="w", pady=8)
        date_hint = tk.Label(frm, text="(YYYY-MM-DD format)",
                            bg=COLORS["bg"],
                            fg="#7F8C8D",
                            font=('Segoe UI', 8))
        date_hint.grid(row=2, column=1, sticky="w", padx=(10, 0))
        pub_entry = ttk.Entry(frm, textvariable=pub_var, width=40, font=('Segoe UI', 10))
        pub_entry.grid(row=3, column=1, pady=(0, 8), padx=(10, 0))

        # Author
        ttk.Label(frm, text="Author:", style='Dialog.TLabel').grid(row=4, column=0, sticky="w", pady=8)
        author_entry = ttk.Entry(frm, textvariable=author_var, width=40, font=('Segoe UI', 10))
        author_entry.grid(row=4, column=1, pady=8, padx=(10, 0))

        # Category
        ttk.Label(frm, text="Category:", style='Dialog.TLabel').grid(row=5, column=0, sticky="w", pady=8)
        cat_combo = ttk.Combobox(frm, textvariable=category_var, 
                                values=["Book", "Film", "Magazine"], 
                                width=38, state="readonly", font=('Segoe UI', 10))
        cat_combo.grid(row=5, column=1, pady=8, padx=(10, 0))

        btn_frame = ttk.Frame(frm)
        btn_frame.grid(row=6, column=0, columnspan=2, pady=(20, 0))

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

        ok_btn = ttk.Button(btn_frame, text="✅ Create", command=on_ok)
        ok_btn.pack(side="left", padx=6)
        
        cancel_btn = ttk.Button(btn_frame, text="❌ Cancel", command=on_cancel)
        cancel_btn.pack(side="left", padx=6)

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
            messagebox.showinfo("Success", f"✅ Item '{payload['name']}' created successfully!")
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
        if not messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete '{item_name}'?\nThis action cannot be undone."):
            return

        try:
            r = requests.delete(f"{BASE}/media/{item_id}", timeout=10)
            if r.status_code == 200:
                messagebox.showinfo("Success", f"✅ Item '{item_name}' deleted successfully.")
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
